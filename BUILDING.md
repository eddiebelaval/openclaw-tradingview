---
last-updated: 2026-04-02
---

# BUILDING

## Timeline

### Phase 1: Framework (Feb 2026)
- Initial OpenClaw TradingView framework
- PineScript-to-Python converter using Claude Haiku
- Backtest engine with backtesting.py
- CSV result logging

### Phase 2: Batch Pipeline (Mar 2026)
- Batch scraper for TradingView community scripts
- First run: 41 indicators across editors_picks, popular, top, trending
- Multi-ticker backtesting (SPY, QQQ, BTC)
- Pipeline state tracking for resumable runs

### Phase 3: Scale to 3,900+ Indicators (Mar 2026)
- Expanded to 9 categories: editors_picks, momentum, moving_averages, oscillators, trend_analysis, volatility, volume + popular, top, trending
- URL manifest system (urls_*.json per category)
- Supabase sync with composite scoring trigger
- FastAPI server for on-demand backtesting
- Notification system for pipeline status
- **Current inventory:**
  - 3,921 Python backtest scripts
  - 1,964 PineScript source files
  - 10 category URL manifests

## Architecture Decisions

### Why Claude Haiku for Conversion
PineScript is a domain-specific language with no direct Python equivalent. Haiku is fast enough for batch conversion (sub-second per script) and cheap enough to run against thousands of indicators. The conversion prompt is heavily constrained to output a specific class structure (`TvStrategy`) that the backtest engine can dynamically load.

### Why backtesting.py Over Custom Engine
backtesting.py handles order execution, position sizing, and stat calculation out of the box. Writing a custom engine would be premature. The framework wraps it with dynamic strategy loading so each generated .py file is self-contained and testable.

### Why Category-Based Organization
Files are organized by TradingView category (not flat) because: (1) categories map to trading style, useful for filtering results, (2) keeps directory sizes manageable, (3) mirrors the URL manifest structure for pipeline resumability.

### Composite Score Weighting
Sharpe (30%) weighted highest because risk-adjusted returns matter more than raw ROI for real trading. Win rate and profit factor together (45%) capture reliability. ROI (25%) captures magnitude. The trigger-based calculation means scores stay fresh automatically.

### Phase 4: Live Validation + Consistency Scoring (Apr 2026)

**Thesis validated:** Pipeline Haiku conversions are faithful (data matches to the penny between yfinance and TradingView). But rankings suffer from window bias: strategies that spiked in one period inflate the composite score.

**What was built:**
- TradingView MCP bridge (`framework/tv_bridge.py`): reads live chart data via CDP
- Validation script (`scripts/validate_rankings.py`): re-runs top scripts on TV data
- Rolling window scorer (`scripts/rolling_scorer.py`): 6-month non-overlapping windows
- Supabase updated with consistency scores replacing old composite

**Key findings:**
- 30% trust rate on original top 10 (7/10 diverged on different bar windows)
- DMI signal test: 40% agreement between TV native (len=14) and pipeline (len=17)
- Root cause: bar count window bias, NOT data quality or conversion quality
- 3 strategies survived cross-asset rolling validation:
  1. swing-highlow-wick-zones (CS=0.755, 82% profitable windows)
  2. liquidities-pivot-levels (CS=0.748)
  3. smart-money-auto-order-blocks (CS=0.733)

**Architecture decision: thin bridge first, highway later.**
Subprocess calls to Node.js CLI (~200ms/call) prove the value before investing in a direct CDP Python client (~20ms/call).

## What's Next

- [ ] Run rolling scorer on all 2,485 scripts (overnight batch job)
- [ ] Integrate consistency scoring into daily pipeline (auto-compute on new scripts)
- [ ] Fix 300-bar bridge limit (chunk requests or pipe to file)
- [ ] Build direct CDP Python client (eliminate subprocess overhead)
- [ ] Solve Pine injection strategy tester issue (TV Desktop doesn't register isStrategy)
- [ ] Feed consistently profitable strategies into DAE V2 / DeepStack strategy pool
- [ ] Set up daily_run.sh cron for continuous indicator discovery
