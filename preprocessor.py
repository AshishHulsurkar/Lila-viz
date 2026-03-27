import os
import json
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

def world_to_pixel(x, z, map_id):
    cfg = MAP_CONFIG[map_id]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * 1024
    py = (1 - v) * 1024
    return round(px, 1), round(py, 1)

def is_human(user_id):
    return "-" in str(user_id)

def read_parquet(filepath):
    try:
        df = pq.read_table(filepath).to_pandas()
        df["event"] = df["event"].apply(
            lambda x: x.decode("utf-8") if isinstance(x, bytes) else x
        )
        # Extract raw milliseconds directly from the timestamp
        df["ts_ms"] = df["ts"].astype("int64")
        return df
    except Exception as e:
        print(f"  Skipping {filepath}: {e}")
        return None

# ── Load all files ─────────────────────────────────────────────────────────────
print("Loading parquet files...")
all_frames = []

day_folders = sorted(Path(RAW_DIR).glob("February_*"))
if not day_folders:
    print(f"ERROR: No folders found in {RAW_DIR}.")
    exit()

for day_folder in day_folders:
    date_str = day_folder.name.replace("February_", "Feb ")
    files = list(day_folder.iterdir())
    print(f"  {day_folder.name}: {len(files)} files")
    for filepath in files:
        df = read_parquet(filepath)
        if df is None or df.empty:
            continue
        df["date"] = date_str
        df["is_human"] = df["user_id"].apply(is_human)
        all_frames.append(df)

if not all_frames:
    print("ERROR: No data loaded.")
    exit()

print("Combining all data...")
full = pd.concat(all_frames, ignore_index=True)
print(f"  Total rows: {len(full):,}")
print(f"  Sample ts_ms values: {full['ts_ms'].head(5).tolist()}")

# ── Build match index ──────────────────────────────────────────────────────────
print("Building match index...")
matches = []
for (match_id, map_id, date), grp in full.groupby(["match_id", "map_id", "date"]):
    if map_id not in MAP_CONFIG:
        continue
    matches.append({
        "match_id": match_id,
        "map_id": map_id,
        "date": date,
        "human_count": int(grp[grp["is_human"]]["user_id"].nunique()),
        "bot_count":   int(grp[~grp["is_human"]]["user_id"].nunique()),
        "event_count": len(grp),
    })

with open(f"{OUT_DIR}/matches.json", "w") as f:
    json.dump(matches, f)
print(f"  Saved {len(matches)} matches to matches.json")

# ── Build per-match event files ────────────────────────────────────────────────
print("Building per-match event files...")
combat_events = {"Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm", "Loot"}

match_groups = list(full.groupby("match_id"))
for i, (match_id, grp) in enumerate(match_groups):
    map_id = grp["map_id"].iloc[0]
    if map_id not in MAP_CONFIG:
        continue

    grp = grp.copy()
    coords = grp.apply(lambda r: world_to_pixel(r["x"], r["z"], map_id), axis=1)
    grp["px"] = coords.apply(lambda c: c[0])
    grp["py"] = coords.apply(lambda c: c[1])

    # Normalize to seconds from match start
    t_min = grp["ts_ms"].min()
    grp["t"] = ((grp["ts_ms"] - t_min) / 1000).round(1)

    if i < 3:
        print(f"  Match {i}: t range 0 to {grp['t'].max():.1f}s  ({len(grp)} events)")

    positions = grp[grp["event"].isin(["Position", "BotPosition"])][
        ["user_id", "is_human", "px", "py", "t", "event"]
    ].to_dict(orient="records")

    combat = grp[grp["event"].isin(combat_events)][
        ["user_id", "is_human", "px", "py", "t", "event"]
    ].to_dict(orient="records")

    safe_id = match_id.replace(".nakama-0", "").replace("-", "_")
    out = {"match_id": match_id, "map_id": map_id, "positions": positions, "combat": combat}
    with open(f"{OUT_DIR}/match_{safe_id}.json", "w") as f:
        json.dump(out, f)

    if i % 50 == 0:
        print(f"  {i}/{len(match_groups)} matches processed...")

print("  Done with match files.")

# ── Build heatmap data per map ─────────────────────────────────────────────────
print("Building heatmap data...")
GRID = 32

for map_id in MAP_CONFIG:
    map_df = full[full["map_id"] == map_id].copy()
    if map_df.empty:
        continue

    coords = map_df.apply(lambda r: world_to_pixel(r["x"], r["z"], map_id), axis=1)
    map_df["px"] = coords.apply(lambda c: c[0])
    map_df["py"] = coords.apply(lambda c: c[1])

    def make_grid(df):
        grid = [[0]*GRID for _ in range(GRID)]
        for _, row in df.iterrows():
            gx = min(int(row["px"] / (1024/GRID)), GRID-1)
            gy = min(int(row["py"] / (1024/GRID)), GRID-1)
            if 0 <= gx < GRID and 0 <= gy < GRID:
                grid[gy][gx] += 1
        return grid

    traffic = make_grid(map_df[map_df["event"].isin(["Position", "BotPosition"])])
    kills   = make_grid(map_df[map_df["event"].isin(["Kill", "BotKill"])])
    deaths  = make_grid(map_df[map_df["event"].isin(["Killed", "BotKilled", "KilledByStorm"])])

    heatmap = {"traffic": traffic, "kills": kills, "deaths": deaths}
    with open(f"{OUT_DIR}/heatmap_{map_id}.json", "w") as f:
        json.dump(heatmap, f)
    print(f"  Saved heatmap for {map_id}")

print("\n✅ Preprocessing complete! Check your data/processed/ folder.")