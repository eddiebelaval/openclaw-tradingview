---
last-updated: 2026-03-26
status: CURRENT
active-milestone: 1
---

# MILESTONE_1_CHECKLIST.md -- Full Pipeline Run

> Deep-dive checklist for the current milestone.
> Strategy: `ROADMAP.md` | Tickets: `TICKETS.md` | Tasklists: `MILESTONE_TASKLISTS.md`
> Goal: get DeepStack TradingView from "framework built" to "alpha discovery operational."

---

## Milestone Goal

Run the full pipeline against all 3,921 converted scripts. Filter for quality. Automate daily execution. The output is a ranked shortlist of backtested indicators ready to feed DeepStack's IBKR strategy pool.

---

## Current Reality

Already true:
- 3,921 Python backtest scripts generated from scraped PineScript
- 1,964 PineScript source files scraped across 10 TradingView categories
- Claude Haiku PineScript-to-Python conversion pipeline works (`framework/pine_converter.py`)
- Supabase `ds_tv_backtests` table has 4,764 rows with composite scoring
- Composite score formula: 30% Sharpe + 25% ROI + 25% Win Rate + 20% Profit Factor
- FastAPI server running at port 8100 (`api/server.py`)
- Trigger auto-recalculates scores on insert
- 16 results already pass stock_momentum filter (Sharpe>=1, WR>=60%, trades>=5)

Not done yet:
- Most of the 3,921 scripts have NOT been backtested (converted but not run)
- No systematic quality filtering applied to results
- `scripts/daily_run.sh` exists but is not deployed on cron
- No monitoring or alerting on pipeline failures
- No visibility into which scripts failed and why

---

## Workstream 1 -- Pipeline Audit

### Outcome
Clear picture of what has been run, what remains, and what is broken.

### Tasks
- [ ] Query `ds_tv_backtests` to count distinct scripts backtested vs total 3,921 available.
- [ ] Identify which tickers (SPY, QQQ, BTC) have coverage and which are missing.
- [ ] Check `backtests/` directory for scripts that exist but have no corresponding Supabase row.
- [ ] Review `scripts/run_pipeline.py` for resume/skip logic (can it pick up where it left off?).
- [ ] Document the gap: X scripts backtested, Y remaining, Z failed.

### Primary Targets
- `scripts/run_pipeline.py`
- `framework/backtest_engine.py`
- `framework/supabase_sync.py`
- Supabase `ds_tv_backtests` table
- `backtests/` directory

### Verification
- [ ] Written count of backtested vs remaining vs failed scripts.
- [ ] Per-ticker coverage documented.
- [ ] Resume capability confirmed or gaps identified.

---

## Workstream 2 -- Batch Execution

### Outcome
All 3,921 scripts backtested against SPY, QQQ, and BTC. Failures logged, not fatal.

### Tasks
- [ ] If `run_pipeline.py` lacks resume logic, add it (skip scripts already in `ds_tv_backtests`).
- [ ] Run pipeline for SPY across all remaining scripts.
- [ ] Run pipeline for QQQ across all remaining scripts.
- [ ] Run pipeline for BTC across all remaining scripts.
- [ ] Log each failure with: script name, ticker, error message, timestamp.
- [ ] After completion, run `python scripts/update_rankings.py` to recalculate composite scores.

### Primary Targets
- `scripts/run_pipeline.py`
- `framework/backtest_engine.py`
- `framework/supabase_sync.py`
- `scripts/update_rankings.py`
- `backtests/` directory (3,921 scripts)

### Dependencies
- Workstream 1 audit must be complete so we know the starting point.

### Verification
- [ ] `ds_tv_backtests` row count reflects full coverage (3,921 x 3 tickers, minus logged failures).
- [ ] Composite scores are recalculated and current.
- [ ] Failure log exists with count and reasons.
- [ ] No unhandled exceptions in pipeline run.

---

## Workstream 3 -- Quality Filtering

### Outcome
A ranked shortlist of strategies that meet minimum quality bars, queryable in Supabase.

### Tasks
- [ ] Define the quality filter as a Supabase view or RPC:
  - Sharpe ratio >= 1.0
  - Win rate >= 60%
  - Total trades >= 5
- [ ] Apply filter to full `ds_tv_backtests` table.
- [ ] Document: how many strategies pass, per ticker, ranked by composite score.
- [ ] Verify the 16 previously identified passing strategies are still present.

### Primary Targets
- `scripts/update_rankings.py`
- Supabase `ds_tv_backtests` table
- New Supabase view (e.g., `ds_tv_quality_strategies`)

### Verification
- [ ] Filtered view/table exists and is queryable.
- [ ] No strategies below threshold appear in filtered results.
- [ ] Top 20 strategies documented with scores.

---

## Workstream 4 -- Automation and Monitoring

### Outcome
Pipeline runs daily without manual intervention. Failures are visible.

### Tasks
- [ ] Review `scripts/daily_run.sh` for completeness (does it run full pipeline + rankings?).
- [ ] Add logging: timestamp, scripts processed, successes, failures, exit code.
- [ ] Deploy on launchd (preferred for macOS) or crontab.
  - Schedule: daily, off-market hours (e.g., 02:00 ET).
- [ ] Verify at least one unattended cycle completes.
- [ ] Add zero-result detection: if a daily run produces zero new backtests, log a warning.
- [ ] Cap or rotate log files to prevent disk fill.

### Primary Targets
- `scripts/daily_run.sh`
- `scripts/run_pipeline.py`
- launchd plist (new file: `com.id8labs.deepstack-tv-daily.plist`)

### Dependencies
- Workstream 2 must be complete so the pipeline is proven to work.

### Verification
- [ ] launchd/cron entry is installed and active (`launchctl list | grep deepstack-tv`).
- [ ] At least one unattended daily run has completed.
- [ ] Logs exist at a known path with timestamps and counts.
- [ ] Zero-result warning fires correctly on an empty run.

---

## Recommended Sequence

1. Pipeline audit (Workstream 1) -- understand the gap
2. Batch execution (Workstream 2) -- fill the gap
3. Quality filtering (Workstream 3) -- surface winners
4. Automation and monitoring (Workstream 4) -- make it self-sustaining

Reasoning:
- Audit first because you cannot run what you do not understand.
- Batch execution is the core work and the largest time investment.
- Quality filtering is fast once data exists.
- Automation comes last because it wraps a pipeline that must already work.

---

## Milestone Exit Checklist

Milestone 1 is done only when all of these are true:
- [ ] All 3,921 scripts have been backtested or their failures are logged.
- [ ] Composite scores are recalculated after the full run.
- [ ] Quality-filtered results are queryable in Supabase.
- [ ] `daily_run.sh` is deployed on cron and has completed at least one unattended cycle.
- [ ] Pipeline failures are logged and discoverable without manual inspection.
- [ ] Docs (`ROADMAP.md`, `TICKETS.md`, `MILESTONE_TASKLISTS.md`) reflect shipped state.
- [ ] All completed tickets in `TICKETS.md` are marked `done` with verification evidence.

If any box above is still open, Milestone 1 is still in progress.
