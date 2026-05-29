---
last-evolved: 2026-04-02
confidence: HIGH
distance: 30%
pillars: "4 (3R, 1P, 0U)"
---

# VISION

## Soul

OpenClaw TradingView is an automated indicator discovery engine. It scrapes every public TradingView indicator, converts PineScript to Python backtests via Claude, runs them against real market data, and surfaces the strategies that actually work. The thesis: most community indicators are noise, but the signal buried in 4,000+ scripts is worth finding systematically.

## Why This Exists

TradingView has the largest open-source library of trading indicators on the planet. Thousands of community-built scripts covering every conceivable approach: momentum, volatility, trend, volume, oscillators. The problem is discovery. There is no way to know which indicators actually produce alpha without manually backtesting each one. Nobody does that at scale. The result: useful strategies sit buried under thousands of underperforming ones.

DeepStack's main trading bot (Kalshi + IBKR) needs an edge pipeline. Instead of hand-picking indicators based on popularity or upvotes, OpenClaw tests everything. PineScript goes in, backtest statistics come out. Sharpe ratio, win rate, profit factor, ROI across SPY, QQQ, BTC. The survivors feed directly into DeepStack's strategy pool.

This is brute-force alpha discovery with AI-powered conversion, not manual curation.

## Pillars

### 1. Scrape Everything (REALIZED)

Automated scraping across 10 TradingView categories. URL manifests track every indicator. The scraper pulls PineScript source for each. Currently covering ~3,900+ indicators.

### 2. Convert and Backtest at Scale (REALIZED)

Claude Haiku converts PineScript to runnable Python backtests using backtesting.py. The pipeline orchestrator processes every script against multiple tickers (SPY, QQQ, BTC). Results log to CSV and sync to Supabase with composite scoring.

### 3. Surface Winners to DeepStack (REALIZED)

Supabase tables (`ds_tv_indicators`, `ds_tv_backtests`) rank indicators by composite score (30% Sharpe + 25% ROI + 25% Win Rate + 20% Profit Factor). A trigger auto-recalculates on every new backtest insert. The FastAPI server exposes the pipeline as an HTTP endpoint for on-demand backtesting.

### 4. Validate Winners Against Live Data (PROGRESSING)

The original composite score (Sharpe/ROI/WinRate/PF blend) suffers from window bias: strategies that spiked in one 6-month period inflate the score even if they underperform in every other period. Phase 4 introduces a TradingView MCP bridge that reads live chart data and a rolling window scorer that ranks by consistency across multiple time periods and assets. Only strategies profitable across all windows graduate to DeepStack.

Key finding (Apr 2): data between yfinance and TradingView is identical (close delta <$0.05). The divergence was 100% bar count (502 vs 300 bars). Rankings are now recomputed with consistency scoring.

## North Star

A self-refreshing indicator research pipeline that continuously discovers, tests, validates against live data, and graduates consistently profitable strategies into the live DeepStack trading system.
