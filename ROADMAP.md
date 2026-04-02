---
last-updated: 2026-04-02
status: CURRENT
active-milestone: 2
---

# ROADMAP.md -- DeepStack TradingView

> Execution roadmap derived from the triad: `VISION.md`, `SPEC.md`, `BUILDING.md`.
> Operational companion: `MILESTONE_TASKLISTS.md`
> Canonical execution board: `TICKETS.md`
> Current milestone deep-dive: `MILESTONE_2_CHECKLIST.md`

---

## Execution Layer

The triad (`VISION.md`, `SPEC.md`, `BUILDING.md`) defines what the product is.
The execution layer defines what to do about it, at four zoom levels:

| Doc | Role | Audience |
|---|---|---|
| `ROADMAP.md` | Strategy, sequencing, gates | Humans and agents |
| `MILESTONE_TASKLISTS.md` | Tactical task lists per milestone | Humans and agents |
| `TICKETS.md` | Agent-executable work units with dependencies | Agents (primary), humans |
| `MILESTONE_N_CHECKLIST.md` | Deep-dive for the current milestone with file-level targets | Agents |

**Reconciliation:** Each milestone's final ticket updates all triad and execution docs to reflect shipped state. Frontmatter timestamps are updated. The `active-milestone` field increments.

---

## Current Read

DeepStack TV completed **Milestone 1 (Pipeline Foundation)** in March 2026. **Milestone 2 (Validation Engine)** was built April 2 and needs completion (full-corpus rolling scorer run). The TradingView MCP bridge is operational. Consistency scoring replaced the original composite formula in Supabase.

What is true right now:
- 3,921 Python backtest scripts generated from 1,964 PineScript sources across 10 categories
- Pipeline runs daily at 2 AM (scrape, convert, backtest, rank)
- TradingView MCP bridge operational (tv_bridge.py, 10 functions, proven against live data)
- Rolling window scorer built (scripts/rolling_scorer.py, 6-month non-overlapping windows)
- Supabase rankings updated with consistency scores for top 15 scripts
- Data quality validated: yfinance and TradingView prices match to the penny
- 3 consistently profitable strategies identified across SPY/QQQ/BTC

What is not true yet:
- Rolling scorer has only run on top 15 scripts (2,485 total need scoring)
- No strategy has graduated to DAE V2 or live trading
- Pine injection into TV strategy tester not working (isStrategy=false bug)
- Bridge limited to 300 bars (CLI buffer overflow)
- No automated consistency check in the daily pipeline

## Planning Principles

- **Validate before trading.** No strategy enters DAE V2 without passing rolling window validation across all three assets.
- **Consistency over peak performance.** A strategy profitable in 4/4 windows beats one with 200% ROI in one window.
- **Thin bridge first, highway later.** Prove value with subprocess calls before building direct CDP client.
- **Data is not the problem.** yfinance and TV match. Focus on scoring methodology, not data sources.

## Health Dimensions

Six dimensions define DeepStack TV's health. Use `/drift` to compute the current gap.

| Dimension | What It Measures | Current Direction |
|-----------|-----------------|-------------------|
| **Pipeline** | Is the scrape/convert/backtest loop running daily? | --> CONVERGING (daily cron active, 3,921 scripts processed) |
| **Accuracy** | Do rankings reflect real-world performance? | --> CONVERGING (consistency scoring live, old composite replaced) |
| **Coverage** | How many scripts have rolling validation? | <-- DIVERGING (15/2,485 scored, 0.6%) |
| **Bridge** | Is the TV MCP bridge reliable and useful? | --> CONVERGING (proven, 5 functions tested live) |
| **Graduation** | Are validated strategies feeding into live trading? | --- FLAT (no strategy graduated yet) |
| **Automation** | Does the system run without human intervention? | --- FLAT (rolling scorer requires manual trigger) |

### Strategy Gates

| Gate | Trigger | Criteria |
|------|---------|----------|
| 1: Foundation -> Validation | M1 complete | Pipeline running, Supabase syncing, 3,900+ scripts processed. |
| 2: Validation -> Coverage | M2 complete | Rolling scorer proven on top 15, consistency scoring in Supabase. |
| 3: Coverage -> Graduation | M3 complete | Full corpus scored. Top 10 consistent strategies identified. |
| 4: Graduation -> Automation | M4 complete | At least 1 strategy running in DAE V2 with live capital. |
| 5: Automation -> Self-Healing | M5 complete | Daily pipeline auto-scores new scripts. Alerts on consistency drift. |

### Decision Rules

- **Agents act autonomously:** Run scoring jobs, update rankings, sync to Supabase.
- **Eddie decides at gates:** Which strategies graduate to live capital, risk parameters, position sizing.
- **Escalation:** Coverage flat 1+ week = run overnight batch. Graduation blocked 2+ weeks = re-evaluate strategy criteria.

## Universal Definition of Done

Before calling any milestone done, confirm all three:
- **Built:** the code exists and runs without errors.
- **Verified:** results are validated against known ground truth.
- **Adopted:** output is being used for actual decision-making (ranking, trading, or research).

---

## Done

### Milestone 1 -- Pipeline Foundation (Mar 2026) -- COMPLETE
**Goal:** Build the scrape/convert/backtest/rank pipeline. Process thousands of TradingView indicators.

#### What Shipped
- Batch scraper across 10 TradingView categories
- Claude Haiku PineScript-to-Python converter
- Multi-ticker backtest engine (SPY, QQQ, BTC)
- Supabase sync with composite scoring trigger
- FastAPI server for on-demand backtesting
- Daily pipeline cron (2 AM)
- 3,921 scripts processed, 7,539 backtest results

---

## Now

### Milestone 2 -- Validation Engine (Apr 2026) -- IN PROGRESS
**Window:** 1 week
**Goal:** Prove which rankings are trustworthy. Replace naive composite with consistency scoring. Build the TV bridge.

#### What Shipped (Apr 2)
- TradingView MCP cloned, installed, registered at user scope
- tv_bridge.py (thin Python wrapper, 10 functions)
- validate_rankings.py (re-runs top scripts on TV data)
- rolling_scorer.py (6-month rolling windows across all 3 tickers)
- Supabase updated: consistency scores for top 15, ranks recomputed

#### Remaining
- Run rolling scorer on full 2,485 scripts (overnight batch)
- Integrate consistency score into daily pipeline
- Fix 300-bar bridge limit
- Document the 3 consistent strategies with trade-by-trade analysis

#### Exit Criteria
- Rolling scorer has run on all scripts with 3+ ticker results
- Top 50 scripts ranked by consistency in Supabase
- Daily pipeline auto-computes rolling score for newly processed scripts
- Results documented in BUILDING.md

---

## Next

### Milestone 3 -- Full Corpus Scoring
**Goal:** Every script with backtest data gets a consistency score. Surface the real top 10.

### Milestone 4 -- Strategy Graduation
**Goal:** Feed the most consistent strategy into DAE V2 for paper trading. Validate with real market conditions.

### Milestone 5 -- Automated Consistency Pipeline
**Goal:** New scripts auto-score on ingestion. Consistency drift alerts via Telegram. Self-healing rankings.

---

## Not Now

- Direct CDP Python client (subprocess overhead acceptable at current scale)
- Pine injection into TV strategy tester (GUI issue, workaround not critical)
- Cross-timeframe validation (daily only for now)
- Options/futures backtesting (equities + crypto first)
- Public API for external consumers

---

## Priority Stack

The canonical priority order and ticket dependencies live in `TICKETS.md`.
