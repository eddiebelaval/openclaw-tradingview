---
last-updated: 2026-03-25
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

## What's Next

- [ ] Run full backtest pipeline against all 3,921 scripts
- [ ] Filter results: Sharpe >= 1, WR >= 60%, trades >= 5
- [ ] Feed top performers into DeepStack's IBKR strategy pool
- [ ] Set up daily_run.sh cron for continuous indicator discovery
- [ ] Add new TradingView categories as they emerge
