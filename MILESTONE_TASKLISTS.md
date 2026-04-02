---
last-updated: 2026-04-02
status: CURRENT
active-milestone: 2
---

# MILESTONE_TASKLISTS.md -- DeepStack TradingView

> Execution task lists for all roadmap milestones.
> Strategy and sequencing: `ROADMAP.md`
> Canonical execution board: `TICKETS.md`
> Current milestone deep-dive: `MILESTONE_2_CHECKLIST.md`

---

## How To Use This Doc

- `ROADMAP.md` explains sequence, intent, and gates.
- This doc turns each milestone into a practical task list with verification criteria.
- `TICKETS.md` is the canonical execution board. Agents work from tickets, not this file.
- The current milestone always has a dedicated checklist (e.g., `MILESTONE_2_CHECKLIST.md`) with file-level detail.

If a task is vague, it is not ready. Break it down further before starting.

---

## Milestone 1 -- Pipeline Foundation (Mar 2026) -- COMPLETE

### Done
- [x] Build batch scraper for 10 TradingView categories
- [x] Build PineScript-to-Python converter (Claude Haiku)
- [x] Build backtest engine (backtesting.py wrapper)
- [x] Build data fetcher (yfinance, 3 tickers: SPY, QQQ, BTC)
- [x] Build CSV logger for results
- [x] Build Supabase sync with composite scoring trigger
- [x] Build FastAPI server (POST /backtest on port 8100)
- [x] Set up daily cron (2 AM via launchd)
- [x] Process 3,900+ indicators across all categories
- [x] Write triad docs (VISION.md, SPEC.md, BUILDING.md)

### Verification
- [x] Pipeline runs end-to-end: .pine -> .py -> backtest -> CSV -> Supabase
- [x] 7,539 backtest results in CSV
- [x] Supabase composite scores calculated and ranked
- [x] FastAPI /backtest endpoint accepts URL and returns JSON results
- [x] Daily cron executes without manual intervention

---

## Milestone 2 -- Validation Engine (Apr 2026) -- IN PROGRESS

Deep-dive: `MILESTONE_2_CHECKLIST.md`

### Done (Apr 2)
- [x] Clone tradingview-mcp, install dependencies, register MCP at user scope
- [x] Build tv_bridge.py (thin Python wrapper, 10 functions)
- [x] Verify bridge: is_connected, get_quote, get_ohlcv (DataFrame compatible), get_study_values, set_symbol
- [x] Build validate_rankings.py (re-runs top scripts on TV OHLCV data)
- [x] Discover root cause: data identical, bar count divergence (502 vs 300)
- [x] Build rolling_scorer.py (6-month non-overlapping windows, cross-asset)
- [x] Run rolling scorer on top 15 scripts across SPY, QQQ, BTC
- [x] Update Supabase: consistency scores replace composite, ranks recomputed
- [x] Update triad docs with Phase 4 findings

### Remaining
- [ ] Run rolling scorer on full 2,485 scripts (add --all flag, overnight batch)
- [ ] Integrate consistency score into run_pipeline.py (auto-compute on new scripts)
- [ ] Fix 300-bar bridge limit (chunk OHLCV requests or pipe to file)
- [ ] Document top 3 consistent strategies with per-window trade analysis
- [ ] Update Supabase for full corpus consistency rankings

### Verification
- [ ] `rolling_scorer.py --all --ticker SPY` completes without errors
- [ ] All 2,485 scripts with 3-ticker results have consistency scores in Supabase
- [ ] Top 50 ranked by consistency (not old composite)
- [ ] run_pipeline.py auto-scores newly processed scripts
- [ ] BUILDING.md updated with full corpus results

### Done When
- [ ] Every scored script has a consistency rating in Supabase
- [ ] The daily pipeline produces consistency scores automatically
- [ ] Eddie has a ranked list of the top 10 most consistent strategies

---

## Milestone 3 -- Full Corpus Scoring

### Tasks
- [ ] Add --all flag to rolling_scorer.py with batching and progress tracking
- [ ] Run full scoring job (estimate: 2-4 hours for 2,485 scripts x 3 tickers x 3-5 windows)
- [ ] Identify top 10 most consistent strategies globally
- [ ] For each top 10: generate per-window trade log with entry/exit dates and P&L
- [ ] Cross-reference top 10 against TradingView community ratings
- [ ] Update Supabase rankings for all scored scripts

### Verification
- [ ] 2,485+ scripts scored
- [ ] Top 10 documented with trade-level analysis
- [ ] Zero scripts with high composite but low consistency (old bias eliminated)

---

## Milestone 4 -- Strategy Graduation

### Tasks
- [ ] Select most consistent strategy for paper trading in DAE V2
- [ ] Convert strategy to DAE V2 format (signal generator, not backtesting.py wrapper)
- [ ] Define position sizing and risk parameters based on rolling window stats
- [ ] Run paper trades for 2 weeks with daily P&L tracking
- [ ] Compare paper results against rolling window predictions
- [ ] Decision gate: Eddie approves graduation to live capital

### Verification
- [ ] Paper trading active for 14+ days
- [ ] P&L within 1 standard deviation of rolling window average
- [ ] Risk parameters respected (daily loss cap, max drawdown)
- [ ] Eddie has approved live graduation

---

## Milestone 5 -- Automated Consistency Pipeline

### Tasks
- [ ] Integrate rolling scorer into daily_run.sh (runs after backtest, before ranking update)
- [ ] Add Telegram notification for newly discovered high-consistency scripts
- [ ] Add consistency drift detection (alert when a top-10 script drops below threshold)
- [ ] Build direct CDP Python client (replace subprocess bridge, ~20ms/call)
- [ ] Add cross-timeframe validation (4h, daily, weekly)

### Verification
- [ ] New scripts auto-scored within 24 hours of ingestion
- [ ] Telegram alerts fire for CS > 0.6 discoveries
- [ ] Drift alerts fire when top-10 script drops below CS 0.4
- [ ] CDP client latency < 50ms per call
