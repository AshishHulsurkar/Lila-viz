# INSIGHTS.md
## Three Things I Learned About LILA BLACK Using This Tool

---

## Insight 1: PvP is Almost Nonexistent — and That's a Monetization Problem

### What I Saw
Across 797 matches and 5 days of production data, only 2 matches contained human vs human kill events. In both cases, the same player both killed and was killed — meaning there was effectively **1 true PvP encounter** across the entire dataset.

### The Evidence
- Scanned all processed match files for Kill/Killed events involving UUID-based (human) user IDs
- PvP matches found: `042774ea` (AmbroseValley) and `711c9a67` (GrandRift)
- 795 out of 797 matches were entirely PvE — players fighting bots only

### Level Design Action
The map should not be optimized for PvP sightlines, sniper lanes, or flanking routes — players never use them. Instead, design should focus on bot encounter zones, bot spawn density, and bot patrol paths. If PvP is a desired mechanic, the current map structure and player population is not creating conditions for it to occur. Forced convergence zones — contested loot rooms, narrow chokepoints, hot drop locations — are needed to generate human-vs-human encounters.

### Monetization Implication
In extraction shooters, cosmetics derive their value from being *seen* in combat. Skins, weapon wraps, kill effects — their entire emotional value is social. A player who only encounters bots has no audience for their cosmetics, and will quickly feel that any purchase was pointless. **Without PvP moments, the cosmetics economy has no emotional foundation.** Fixing map design to force human encounters isn't just a gameplay decision — it's a prerequisite for cosmetic monetization to work.

---

## Insight 2: Loot Drives All Player Movement — and Marks the Highest-Value Monetization Moment

### What I Saw
Loot events vastly outnumber all combat events combined. Across 50 sampled matches, there were **767 Loot events vs 198 total combat events**. Traffic heatmaps on all three maps show dense clustering around specific structures that align precisely with high loot density — confirming players move toward loot, not toward combat.

### The Evidence
- Loot event count: 767 across 50 sampled matches
- Combat event count: 198 across the same sample
- AmbroseValley traffic heatmap shows northern cluster accounts for ~52% of all player movement, overlapping directly with highest loot density zones

### Level Design Action
Loot placement is the single most powerful lever for controlling player flow. Redistributing loot into underused areas of the map is the most direct way to activate dead zones and increase map utilization. Where loot goes, players follow.

### Monetization Implication
The moment immediately after a loot pickup is the game's peak engagement moment — the player just received something, dopamine is elevated, attention is high. This is precisely when a battle pass prompt, a limited-time offer, or a "rare item found — upgrade it" nudge would convert at highest rate. Right now that moment is invisible to the monetization team. **This tool makes it visible.** Loot zones are not just design decisions — they are the highest-converting real estate in the game for in-session monetization triggers.

---

## Insight 3: 60%+ of Every Map Is Never Visited — That's Wasted Monetization Surface

### What I Saw
Traffic heatmaps across all three maps show activity concentrated in a small fraction of the total map area. Large portions — particularly southern and eastern edges on AmbroseValley — are almost completely dark across all 5 days of data.

### The Evidence
- AmbroseValley: activity concentrated in northern quarter; southeastern region shows near-zero traffic across all matches
- GrandRift and Lockdown show similar patterns — consistent dead zones across multiple days
- Estimated 60%+ of map area accounts for less than 10% of total player traffic

### Level Design Action
Dead zones need investigation before redesign — are they inaccessible? Unappealing? Outside the storm path? The storm's movement likely creates a consistent safe corridor that players follow, rendering the rest of the map irrelevant. Rotating storm direction or seeding dead zones with high-value loot would increase map utilization and reduce the predictability of player paths.

### Monetization Implication
Every area of the map that players visit is potential monetization surface — named POIs create identity, identity creates player attachment, and attachment drives spending on themed cosmetics, location-specific challenges, and battle pass objectives tied to specific zones. **60% of the current map generates zero player attachment and zero monetization surface.** Activating dead zones through level design isn't just about map efficiency — each activated zone is a new canvas for a revenue-generating event, cosmetic theme, or limited-time experience.

---

## Meta: What This Tool Actually Is

The visualization reveals a game where players are spatially concentrated, session lengths are compressed by early deaths, and most of the map goes unseen. That's not just a design problem — it describes a player who never gets deep enough into the experience to *want* to spend money.

**Retention is the precondition for monetization.** This tool shows exactly where retention is breaking — which zones, which moments, which match phases. That makes it a decision-making engine for both game design and revenue strategy, not just a visualization system.
