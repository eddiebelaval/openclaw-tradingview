---
last-updated: 2026-04-02
milestone: 2
status: IN_PROGRESS
---

# MILESTONE_2_CHECKLIST.md -- Validation Engine

> Deep-dive for the current milestone.
> Strategy: `ROADMAP.md`
> All milestones: `MILESTONE_TASKLISTS.md`
> Ticket board: `TICKETS.md`

---

## Goal

Prove which rankings are trustworthy. Replace naive composite scoring with consistency-based ranking. Build the TradingView bridge as the validation instrument.

## Completed Work (Apr 2, 2026)

### TV MCP Bridge
- [x] `~/Development/tradingview-mcp/` cloned and installed
- [x] MCP registered at user scope (`tradingview: node src/server.js`)
- [x] TradingView Desktop launches with CDP on port 9222
- [x] `framework/tv_bridge.py` -- 10 functions, tested live
  - `is_connected()` -- CDP health check
  - `get_quote(symbol?)` -- real-time OHLCV snapshot
  - `get_ohlcv(count, as_dataframe)` -- DataFrame matching data_fetcher.py format
  - `get_study_values()` -- all visible indicator values as floats
  - `set_symbol(symbol)` / `set_timeframe(tf)` -- chart control
  - `get_chart_state()` -- symbol, timeframe, studies
  - `inject_pine(source)` -- Pine code injection (compiles, but isStrategy bug)
  - `get_strategy_results()` -- reads strategy tester (blocked by isStrategy bug)
  - `get_pine_lines/labels(filter?)` -- Pine graphics data
  - `screenshot(region)` -- chart capture

### Validation Discovery
- [x] DMI signal test: 40% agreement (length=14 vs 17)
- [x] Top 10 validation: 30% trust rate (7/10 diverged)
- [x] Root cause: bar count (502 vs 300), NOT data quality
  - Close price delta: $0.0004 avg across 300 overlapping bars
  - Volume delta: 0.0% avg (rounding only)
- [x] Full vs trimmed yfinance confirms: trimmed results = TV bridge results exactly

### Rolling Scorer
- [x] `scripts/rolling_scorer.py` -- 6-month non-overlapping windows
- [x] SPY results: swing-highlow #1 (CS=0.636), smart-money #2, liquidities-pivot #3
- [x] QQQ results: swing-highlow #1 (CS=0.819), liquidities-pivot #2, smart-money #3
- [x] BTC results: swing-highlow #1 (CS=0.771), smart-money #2, liquidities-pivot #3
- [x] Cross-asset consistency scores computed and uploaded to Supabase

### The Consistent Three
| Script | CS | SPY Avg | QQQ Avg | BTC Avg | Profitable Windows |
|--------|----:|--------:|--------:|--------:|---:|
| swing-highlow-wick-zones | 0.755 | 13.4% | 19.6% | 42.6% | 82% |
| liquidities-pivot-levels | 0.748 | 8.9% | 8.0% | 41.7% | 73% |
| smart-money-auto-order-blocks | 0.733 | 14.1% | 12.8% | 59.4% | 82% |

## Remaining Work

### M2-T7: Full Corpus Rolling Scorer -- DONE
**File:** `scripts/rolling_scorer.py`
**Implemented (2026-04-02):**
- [x] `--all` flag walks all 2,513 .py files in `backtests/` (filesystem, not CSV-derived)
- [x] tqdm progress bar with live ETA, ok/skip/error counters
- [x] `.rolling_state.json` state file, saves every 50 scripts, per-ticker tracking
- [x] `--no-resume` flag to force re-score everything
- [x] Per-ticker output: `results/rolling_rankings_SPY.csv` (appends as it goes, no data loss)
- [x] Error handling: skip and continue, print summary at end
- [x] Top 20 summary printed after batch
- [x] Smoke tested: 5 scripts scored, state save/load verified

### M2-T8: Pipeline Integration
**File:** `scripts/run_pipeline.py`
**Changes needed:**
- After backtest step, call rolling scorer for the just-processed script
- Sync consistency score to Supabase alongside regular backtest results
- Update `framework/supabase_sync.py` to include consistency fields

### M2-T9: Bridge Buffer Fix
**File:** `framework/tv_bridge.py`
**Changes needed:**
- `get_ohlcv(count=500)` currently fails at ~300 bars (JSON buffer overflow in CLI stdout)
- Solution: request in chunks (2x 250 bars with time offset) or pipe CLI to tempfile and read
- Verify: 500 bars returned without error

### M2-T10: Strategy Reports
**Directory:** `results/strategy_reports/`
**Deliverables:**
- `swing-highlow-wick-zones.md` -- full analysis
- `liquidities-pivot-levels.md` -- full analysis
- `smart-money-auto-order-blocks.md` -- full analysis
- Each report: per-window trade log, entry/exit dates, P&L, max drawdown, risk profile

## Exit Criteria

- [ ] All 2,485 scripts scored (M2-T7)
- [ ] Top 50 in Supabase ranked by consistency
- [ ] Daily pipeline auto-scores new scripts (M2-T8)
- [ ] Top 3 strategies documented with trade-level analysis (M2-T10)
- [ ] BUILDING.md updated with full corpus results
- [ ] Triad and execution docs reconciled
