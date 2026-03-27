import streamlit as st
import json
import numpy as np
from PIL import Image, ImageFile
import plotly.graph_objects as go
import os
from collections import defaultdict

# Fix truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ── Config ────────────────────────────────────────────────────────────────────
PROCESSED_DIR = "data/processed"
MINIMAP_DIR = "minimaps"

MINIMAP_FILES = {
    "AmbroseValley": "AmbroseValley_Minimap.png",
    "GrandRift": "GrandRift_Minimap.png",
    "Lockdown": "Lockdown_Minimap.jpg",
}

EVENT_COLORS = {
    "Kill":          "#FF0000",
    "Killed":        "#FF8800",
    "BotKill":       "#00FFFF",
    "BotKilled":     "#FFFF00",
    "KilledByStorm": "#9900FF",
    "Loot":          "#00FF00",
}

EVENT_SYMBOLS = {
    "Kill":          "x",
    "Killed":        "circle",
    "BotKill":       "square",
    "BotKilled":     "triangle-up",
    "KilledByStorm": "star",
    "Loot":          "diamond",
}

EVENT_LABELS = {
    "Kill":          "🔴 ✖ Kill — Human killed human",
    "Killed":        "🟠 ⭕ Killed — Human was killed",
    "BotKill":       "🔵 ■ BotKill — Human killed bot",
    "BotKilled":     "🟡 ▲ BotKilled — Killed by bot",
    "KilledByStorm": "🟣 ★ Storm Death",
    "Loot":          "🟢 ♦ Loot — Item picked up",
}

MATCHES_WITH_KILLS = {"042774ea", "711c9a67"}

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_matches():
    with open(f"{PROCESSED_DIR}/matches.json") as f:
        return json.load(f)

@st.cache_data
def load_match_data(match_id):
    safe_id = match_id.replace(".nakama-0", "").replace("-", "_")
    path = f"{PROCESSED_DIR}/match_{safe_id}.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_heatmap(map_id):
    path = f"{PROCESSED_DIR}/heatmap_{map_id}.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_minimap(map_id):
    path = f"{MINIMAP_DIR}/{MINIMAP_FILES[map_id]}"
    img = Image.open(path).convert("RGB").resize((512, 512))
    return img

# ── Page Setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="LILA BLACK — Map Viz", layout="wide")
st.title("🎮 LILA BLACK — Player Journey Visualizer")

matches = load_matches()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

maps = sorted(set(m["map_id"] for m in matches))
selected_map = st.sidebar.selectbox("Map", maps)

dates = sorted(set(m["date"] for m in matches if m["map_id"] == selected_map))
selected_date = st.sidebar.selectbox("Date", ["All"] + dates)

filtered = [
    m for m in matches
    if m["map_id"] == selected_map
    and (selected_date == "All" or m["date"] == selected_date)
]

if not filtered:
    st.warning("No matches found for this filter.")
    st.stop()

match_labels = [
    f"⚔️ {m['match_id'][:8]}... | {m['date']} | 👤{m['human_count']} 🤖{m['bot_count']}"
    if m['match_id'][:8] in MATCHES_WITH_KILLS
    else f"{m['match_id'][:8]}... | {m['date']} | 👤{m['human_count']} 🤖{m['bot_count']}"
    for m in filtered
]

selected_idx = st.sidebar.selectbox(
    "Match",
    range(len(match_labels)),
    format_func=lambda i: match_labels[i]
)

selected_match = filtered[selected_idx]
match_data = load_match_data(selected_match["match_id"])

if match_data is None:
    st.warning("Match data file not found.")
    st.stop()

# ── Event Filters ─────────────────────────────────────────────────────────────
st.sidebar.header("Event Types")
show_humans   = st.sidebar.checkbox("👤 Human paths (blue)", value=True)
show_bots     = st.sidebar.checkbox("🤖 Bot paths (orange)", value=False)
show_kills    = st.sidebar.checkbox("🔴 Kills — human vs human", value=True)
show_deaths   = st.sidebar.checkbox("🟠 Deaths — human killed", value=True)
show_botkills = st.sidebar.checkbox("🔵 Bot kills/deaths", value=False)
show_storm    = st.sidebar.checkbox("🟣 Storm deaths", value=True)
show_loot     = st.sidebar.checkbox("🟢 Loot pickups", value=True)

# ── Legend in Sidebar ─────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("Legend")
st.sidebar.markdown("""
| Color | Shape | Event | Description |
|-------|-------|-------|-------------|
| 🔴 | ✖ X | Kill | Human killed human |
| 🟠 | ⭕ Circle | Killed | Human was killed |
| 🔵 | ■ Square | BotKill | Human killed bot |
| 🟡 | ▲ Triangle | BotKilled | Killed by bot |
| 🟣 | ★ Star | KilledByStorm | Died to storm |
| 🟢 | ♦ Diamond | Loot | Item picked up |
| 🔵 | — Line | Human path | Blue line |
| 🟤 | — Line | Bot path | Orange line |
""")
st.sidebar.markdown("⚔️ = Match has human vs human kills")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🗺️ Match View", "🔥 Heatmaps"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Match View
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    positions = match_data["positions"]
    combat    = match_data["combat"]

    pos_filtered = positions
    com_filtered = combat

    # PvP alert
    has_kills = any(c['event'] == 'Kill' for c in combat)
    if has_kills:
        st.success(f"⚔️ This match contains rare PvP (human vs human) kill events on {selected_map} — look for the large red X on the map!")

    img = load_minimap(selected_map)

    fig = go.Figure()

    fig.add_layout_image(
        source=img,
        x=0, y=512,
        xref="x", yref="y",
        sizex=512, sizey=512,
        sizing="stretch",
        layer="below"
    )

    # Group positions by player
    player_paths = defaultdict(list)
    for p in pos_filtered:
        player_paths[p["user_id"]].append(p)

    # Plot paths
    for uid, path in player_paths.items():
        is_human = path[0]["is_human"]
        if is_human and not show_humans:
            continue
        if not is_human and not show_bots:
            continue
        xs = [p["px"] * 0.5 for p in path]
        ys = [512 - p["py"] * 0.5 for p in path]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(
                width=1.5,
                color="rgba(100,180,255,0.5)" if is_human else "rgba(255,160,50,0.4)"
            ),
            showlegend=False,
            hoverinfo="skip",
        ))

    # Plot combat events
    event_groups = defaultdict(list)
    for c in com_filtered:
        event_groups[c["event"]].append(c)

    for event_type, events in event_groups.items():
        if event_type == "Kill" and not show_kills:
            continue
        if event_type == "Killed" and not show_deaths:
            continue
        if event_type in ("BotKill", "BotKilled") and not show_botkills:
            continue
        if event_type == "KilledByStorm" and not show_storm:
            continue
        if event_type == "Loot" and not show_loot:
            continue

        xs = [e["px"] * 0.5 for e in events]
        ys = [512 - e["py"] * 0.5 for e in events]

        is_kill = event_type == "Kill"

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(
                symbol=EVENT_SYMBOLS.get(event_type, "circle"),
                size=20 if is_kill else 10,
                color=EVENT_COLORS.get(event_type, "#ffffff"),
                opacity=1.0,
                line=dict(width=3 if is_kill else 1.5, color="white")
            ),
            name=EVENT_LABELS.get(event_type, event_type),
            showlegend=False,
            hovertemplate=f"<b>{event_type}</b><br>t=%{{customdata:.1f}}s",
            customdata=[e["t"] for e in events],
        ))

    fig.update_layout(
        xaxis=dict(range=[0, 512], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 512], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        plot_bgcolor="black",
        paper_bgcolor="#0e1117",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Human Players", selected_match["human_count"])
    col2.metric("Bots", selected_match["bot_count"])
    col3.metric("Total Events", selected_match["event_count"])
    col4.metric("Match Duration", "N/A")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Heatmaps
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    heatmap_data = load_heatmap(selected_map)

    if heatmap_data is None:
        st.warning("No heatmap data for this map.")
    else:
        htype = st.radio("Heatmap Type", ["traffic", "kills", "deaths"], horizontal=True)
        grid = np.array(heatmap_data[htype], dtype=float)

        img2 = load_minimap(selected_map)

        fig2 = go.Figure()

        fig2.add_layout_image(
            source=img2,
            x=0, y=512,
            xref="x", yref="y",
            sizex=512, sizey=512,
            sizing="stretch",
            layer="below"
        )

        GRID = 32
        cell = 512 / GRID
        xs, ys, zs = [], [], []
        for row in range(GRID):
            for col in range(GRID):
                val = grid[row][col]
                if val > 0:
                    xs.append(col * cell + cell / 2)
                    ys.append(512 - (row * cell + cell / 2))
                    zs.append(val)

        if xs:
            fig2.add_trace(go.Scatter(
                x=xs, y=ys,
                mode="markers",
                marker=dict(
                    size=16,
                    color=zs,
                    colorscale="Inferno",
                    opacity=0.6,
                    showscale=True,
                    colorbar=dict(
                        title="Count",
                        tickfont=dict(color="white"),
                        title_font=dict(color="white")
                    )
                ),
                hovertemplate="Count: %{marker.color}<extra></extra>",
                showlegend=False,
            ))

        fig2.update_layout(
            xaxis=dict(range=[0, 512], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 512], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            margin=dict(l=0, r=0, t=0, b=0),
            height=700,
            plot_bgcolor="black",
            paper_bgcolor="#0e1117",
        )

        st.plotly_chart(fig2, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Traffic Events", int(np.array(heatmap_data["traffic"]).sum()))
        col2.metric("Total Kills", int(np.array(heatmap_data["kills"]).sum()))
        col3.metric("Total Deaths", int(np.array(heatmap_data["deaths"]).sum()))