# ARCHITECTURE.md
## LILA BLACK — Player Journey Visualizer

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Frontend | Streamlit | Python-native, fast to build, easy deployment — right tool for an internal analytics tool used by designers, not a consumer product |
| Visualization | Plotly | Interactive maps, scatter overlays, heatmaps with zoom/pan — essential for spatial data exploration |
| Data pipeline | Python + PyArrow | Native parquet support, fast reads, no additional infra needed |
| Hosting | Streamlit Community Cloud | Free, GitHub-connected, shareable URL in one click |

---

## How Data Flows

```
Raw Parquet Files (1,243 files across 5 days)
        ↓
preprocessor.py
  - Reads all parquet files across February 10–14
  - Decodes event bytes to human-readable strings
  - Extracts raw milliseconds from timestamp columns
  - Converts world coordinates (x, z) → minimap pixel coordinates
  - Groups events by match_id to reconstruct full matches
  - Builds per-match JSON files with positions + events
  - Builds 32×32 heatmap grids per map (traffic, kills, deaths)
        ↓
data/processed/
  - matches.json          → match index (797 matches)
  - match_{id}.json       → per-match positions + combat events
  - heatmap_{map}.json    → traffic/kill/death grids per map
        ↓
app.py (Streamlit)
  - Loads processed JSONs via st.cache_data (fast repeat loads)
  - Renders minimap as Plotly layout image (resized to 512×512)
  - Overlays player paths as scatter line traces
  - Overlays combat events as distinct scatter marker traces
  - Renders heatmap as scatter markers with Inferno colorscale
  - Filters by map, date, match via sidebar controls
  - Highlights PvP matches with ⚔️ badge
```

---

## Coordinate Mapping

World coordinates (x, z) are mapped to minimap pixels using a linear transform:

```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
pixel_x = u * 1024
pixel_y = (1 - v) * 1024   ← Y axis flipped (image origin top-left)
```

Map configs:

| Map | Scale | Origin (x, z) |
|-----|-------|----------------|
| AmbroseValley | 900 | (-370, -473) |
| GrandRift | 581 | (-290, -290) |
| Lockdown | 1000 | (-500, -500) |

Since the minimap is resized to 512×512 for memory efficiency, all pixel coordinates are multiplied by 0.5 when plotting. This was the trickiest part of the pipeline — getting the coordinate transform wrong by even a small margin causes all events to appear in the wrong location on the map.

---

## Assumptions

| Assumption | Reasoning |
|------------|-----------|
| Timestamps are milliseconds since epoch | Extracted via `.astype("int64")` directly from parquet datetime column — consistent across all files |
| Each parquet file = one player in one match | Files are grouped by match_id to reconstruct full matches |
| Bot detection: numeric user_id = bot, UUID user_id = human | Consistent pattern across all 1,243 files |
| February 14 is a partial day | Treated the same as other days — flagged but not excluded |

---

## Tradeoffs

| Decision | Alternative Considered | Why I Chose This |
|----------|----------------------|-----------------|
| Pre-process to JSON | Query parquet live via DuckDB-WASM | Faster load times, simpler frontend, no browser WASM complexity |
| Streamlit | React + backend API | Faster to build; right fit for internal tool used by designers |
| Resize minimap to 512×512 | Full 1024×1024 | Memory errors on 4GB RAM machines — 512×512 is imperceptible quality loss for this use case |
| 32×32 heatmap grid | Finer resolution grid | Balance between spatial detail and render performance |
| Pre-computed heatmaps | On-demand computation | Eliminates per-session compute cost; heatmaps don't change between sessions |

---

## What I'd Do With More Time

- **Fix timestamp normalization** so the timeline slider shows true match duration rather than raw milliseconds
- **Add a match summary panel** — automatically surface key signals (storm death rate, dead zone %, PvP flag) without requiring the designer to interpret raw heatmaps
- **Player-level filtering** — select a specific player and track their full journey across a match
- **Cross-match analytics** — identify patterns across multiple matches, not just within one
- **DuckDB-WASM** — query parquet directly in the browser, eliminating the preprocessing step entirely
- **Automatic clustering** — identify and name high-traffic zones automatically from the data, rather than relying on designers to interpret heatmaps visually
