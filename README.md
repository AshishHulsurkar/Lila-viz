# LILA BLACK — Player Journey Visualizer

A web-based tool for LILA Games' Level Design team to explore player behavior on LILA BLACK maps.

**Live tool:** https://lila-viz-k76rxdbe6vyglbrz6fiyzm.streamlit.app/

---

## What It Does

- Visualizes player paths on all 3 maps (AmbroseValley, GrandRift, Lockdown)
- Shows kill, death, loot, and storm events as distinct markers
- Distinguishes human players from bots visually
- Heatmaps for traffic, kills, and deaths
- Filter by map, date, and match
- Timeline playback to watch a match unfold
- Highlights rare PvP matches with ⚔️ badge

---

## How to Run Locally

### Requirements
- Python 3.10+

### Setup

```bash
git clone https://github.com/AshishHulsurkar/Lila-viz.git
cd lila-viz
pip install -r requirements.txt
```

### Add Data

1. Place raw parquet folders (`February_10` through `February_14`) in `data/raw/`
2. Place minimap images in `minimaps/`
3. Run the preprocessor:

```bash
python preprocessor.py
```

This generates processed JSON files in `data/processed/` — takes approximately 10–15 minutes.

### Run the App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
lila-viz/
├── app.py              # Streamlit app
├── preprocessor.py     # Data pipeline (parquet → JSON)
├── requirements.txt    # Dependencies
├── minimaps/           # Map images
├── data/
│   ├── raw/            # Raw parquet files (not in repo)
│   └── processed/      # Preprocessed JSON files
├── ARCHITECTURE.md     # Tech decisions and data flow
└── INSIGHTS.md         # 3 insights from the data
```

---

## Docs

- [Architecture](./ARCHITECTURE.md) — tech stack, data flow, coordinate mapping, tradeoffs
- [Insights](./INSIGHTS.md) — 3 findings from the data with level design and monetization implications
