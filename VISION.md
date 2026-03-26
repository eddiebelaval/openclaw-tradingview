---
last-evolved: 2026-03-25
confidence: HIGH
distance: 40%
pillars: "3 (3R, 0P, 0U)"
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

## North Star

A self-refreshing indicator research pipeline that continuously discovers, tests, and graduates winning strategies into the live DeepStack trading system.
