---
last-synced-to-vision: 2026-03-25
status: ACTIVE
---

# SPEC

## Architecture

```
scripts/
  scrape_tradingview.py    # Scrapes indicator URLs from TradingView categories
  batch_scraper.py         # Batch downloads PineScript source from URLs
  run_pipeline.py          # Orchestrator: pine -> python -> backtest -> log
  update_rankings.py       # Recalculates composite scores in Supabase
  daily_run.sh             # Cron wrapper for full pipeline execution
  urls_*.json              # URL manifests per category (10 categories)

framework/
  pine_converter.py        # PineScript -> Python via Claude Haiku API
  backtest_engine.py       # Runs backtesting.py against OHLCV data
  data_fetcher.py          # Fetches market data for SPY, QQQ, BTC
  csv_logger.py            # Logs results to backtest_results.csv
  stats_formatter.py       # Formats stats output
  supabase_sync.py         # Syncs results to Supabase tables
  notifications.py         # Pipeline status notifications
  single_scraper.py        # Single-indicator scraper for API use

api/
  server.py                # FastAPI server (POST /backtest)

pinescript/                # Raw .pine source files (organized by category)
backtests/                 # Generated .py backtest files (organized by category)
results/                   # CSV output + pipeline state tracking
```

## Data Flow

```
TradingView categories
  -> scrape_tradingview.py (collect URLs -> urls_*.json)
  -> batch_scraper.py (download .pine files)
  -> run_pipeline.py:
       pine_converter.py (Claude Haiku: .pine -> .py)
       data_fetcher.py (OHLCV for SPY/QQQ/BTC)
       backtest_engine.py (run strategy, collect stats)
       csv_logger.py (append to backtest_results.csv)
       supabase_sync.py (upsert to ds_tv_indicators + ds_tv_backtests)
  -> update_rankings.py (composite score ranking)
```

## Database Schema (Supabase)

**ds_tv_indicators** -- One row per TradingView script (aggregated stats)
- script_name (UNIQUE), category, source_url, pine_hash
- composite_score, avg_sharpe, avg_roi, avg_win_rate, avg_profit_factor
- num_tickers_tested, best_ticker, worst_ticker, rank

**ds_tv_backtests** -- One row per (script, ticker) pair
- script_name, ticker (UNIQUE together)
- roi_pct, max_drawdown_pct, sharpe_ratio, sortino_ratio
- win_rate_pct, profit_factor, num_trades, expectancy_pct

**Composite Score Formula:**
`Sharpe * 0.3 + (ROI/100) * 0.25 + (WinRate/100) * 0.25 + (ProfitFactor/10) * 0.2`

Auto-recalculated by Postgres trigger on every backtest insert/update.

## API

**FastAPI** on port 8100:
- `POST /backtest` -- accepts `{"url": "https://tradingview.com/script/..."}`, returns JSON backtest results
- CORS enabled for dashboard integration

## Categories (10)

editors_picks, popular, top, trending, oscillators, trend_analysis, volume, moving_averages, volatility, momentum

## Dependencies

- Python 3.12, backtesting.py, pandas_ta, anthropic SDK
- Claude Haiku for PineScript conversion
- Supabase (project: scfdoayhmcruieppwawg, Oregon)
- yfinance / data fetcher for OHLCV

## Environment Variables

- `ANTHROPIC_API_KEY` -- Claude Haiku for PineScript conversion
- `SUPABASE_URL` / `SUPABASE_KEY` -- results sync
