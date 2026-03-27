---
last-updated: 2026-03-26
status: CURRENT
active-milestone: 1
---

# TICKETS.md -- DeepStack TradingView Execution Board

> Canonical ticket board for agent-driven execution.
> Strategy and sequencing: `ROADMAP.md`
> Milestone grouping: `MILESTONE_TASKLISTS.md`
> Current milestone deep-dive: `MILESTONE_1_CHECKLIST.md`

---

## How Agents Should Use This File

This file is the operational source of truth for execution.

### Rules
- Work from the top down.
- Always prefer the **highest-priority unblocked ticket**.
- Only mark a ticket `done` when it is built, verified, and reflected in docs if needed.
- If work uncovers new necessary tasks, add new tickets under the right milestone instead of burying them in notes.
- If a ticket is too large for one session, split it into smaller tickets before starting.
- Future milestone tickets are stubs. Before starting a new milestone, expand its tickets to include Goal, Primary Targets, and Verification details.
- **This is a Python project.** Verification means running scripts and checking Supabase output. There is no build step, no type checker, no test suite (yet).
- **Branch protocol:** Feature branches off `feature/finish-build`. PR back. Never commit to `main` directly.

### Status Values
- `todo` -- ready to pick up
- `in_progress` -- currently being worked
- `blocked` -- cannot proceed yet
- `done` -- completed and verified

### Update Protocol
When an agent starts work:
- change one ticket to `in_progress`
- add short progress notes if helpful

When an agent finishes work:
- change the ticket to `done`
- record verification evidence
- update any affected docs

When an agent gets blocked:
- change the ticket to `blocked`
- add the reason in `Notes`
- create follow-up tickets if needed

---

## Current Priority Order

1. Milestone 1 -- Full Pipeline Run
2. Milestone 2 -- IBKR Integration

---

## Milestone 1 -- Full Pipeline Run

### M1-01 Audit pipeline state
- Status: `todo`
- Priority: `P0`
- Depends on: none
- Goal: determine exactly how many of 3,921 scripts have been backtested vs only converted, and which tickers have coverage
- Primary targets:
  - `scripts/run_pipeline.py` (main orchestrator)
  - `framework/backtest_engine.py` (backtest runner)
  - `framework/supabase_sync.py` (results sync)
  - Supabase `ds_tv_backtests` table (4,764 rows currently)
  - Supabase `ds_tv_scripts` or equivalent tracking table
- Verification:
  - documented count: total scripts, backtested scripts, failed scripts, per-ticker coverage
  - clear list of what remains to be run

### M1-02 Batch backtest execution
- Status: `todo`
- Priority: `P0`
- Depends on: `M1-01`
- Goal: run backtests against all remaining scripts for SPY, QQQ, BTC
- Primary targets:
  - `scripts/run_pipeline.py` (orchestrator)
  - `framework/backtest_engine.py` (execution)
  - `framework/supabase_sync.py` (result storage)
  - `backtests/` directory (generated backtest scripts)
- Verification:
  - all 3,921 scripts attempted across SPY, QQQ, BTC
  - failures are logged with script name, ticker, and error
  - new results appear in `ds_tv_backtests` table
  - no unhandled exceptions crash the pipeline

### M1-03 Recalculate composite scores
- Status: `todo`
- Priority: `P0`
- Depends on: `M1-02`
- Goal: recalculate rankings after full backtest run
- Primary targets:
  - `scripts/update_rankings.py` (score recalculator)
  - Supabase composite score formula (30% Sharpe + 25% ROI + 25% Win Rate + 20% Profit Factor)
- Verification:
  - `python scripts/update_rankings.py` runs without errors
  - composite scores are updated for all rows in `ds_tv_backtests`
  - top 20 results are inspectable in Supabase

### M1-04 Apply quality filter
- Status: `todo`
- Priority: `P0`
- Depends on: `M1-03`
- Goal: filter results to only strategies meeting minimum quality bars
- Primary targets:
  - `scripts/update_rankings.py` or new filter script
  - Supabase: create a view or filtered table for quality results
- Filter criteria:
  - Sharpe ratio >= 1.0
  - Win rate >= 60%
  - Total trades >= 5
- Verification:
  - filtered results are queryable in Supabase (view or table)
  - count of passing strategies is documented
  - no strategies below threshold appear in filtered results

### M1-05 Deploy daily_run.sh on cron
- Status: `todo`
- Priority: `P1`
- Depends on: `M1-02`
- Goal: automate daily pipeline execution for continuous indicator discovery
- Primary targets:
  - `scripts/daily_run.sh` (cron wrapper)
  - launchd plist or crontab entry
- Verification:
  - `scripts/daily_run.sh` runs end-to-end without manual intervention
  - cron/launchd entry is installed and active
  - at least one unattended cycle has completed successfully
  - logs are written to a discoverable location

### M1-06 Add pipeline monitoring
- Status: `todo`
- Priority: `P1`
- Depends on: `M1-05`
- Goal: detect pipeline failures without manual inspection
- Primary targets:
  - `scripts/daily_run.sh` (add logging)
  - `scripts/run_pipeline.py` (add error aggregation)
- Verification:
  - exit codes are logged per run
  - failed backtest count is logged per run
  - zero-result runs are flagged
  - logs are rotated or capped to prevent disk fill

### M1-07 Run Milestone 1 verification sweep
- Status: `todo`
- Priority: `P0`
- Depends on: `M1-03`, `M1-04`, `M1-05`
- Goal: verify the full pipeline end-to-end
- Verification:
  - `python scripts/run_pipeline.py` completes a full cycle
  - `python scripts/update_rankings.py` recalculates without errors
  - quality-filtered results are queryable
  - `scripts/daily_run.sh` has at least one logged unattended run
  - Supabase `ds_tv_backtests` row count reflects full coverage

### M1-08 Reconcile docs after Milestone 1 ships
- Status: `todo`
- Priority: `P1`
- Depends on: `M1-07`
- Goal: keep all docs truthful after the milestone lands
- Primary targets:
  - `ROADMAP.md`, `MILESTONE_TASKLISTS.md`, `TICKETS.md`
  - `MILESTONE_1_CHECKLIST.md` (archive or replace with M2 checklist)
  - `BUILDING.md` (update with pipeline run results)
- Verification:
  - docs reflect shipped state and remaining gaps
  - all frontmatter timestamps updated
  - `active-milestone` incremented to 2 where applicable

---

## Milestone 2 -- IBKR Integration

### M2-01 Define IBKR export format
- Status: `todo`
- Priority: `P0`
- Depends on: `M1-07`

### M2-02 Build strategy export script
- Status: `todo`
- Priority: `P0`
- Depends on: `M2-01`

### M2-03 Onboard TV strategies into paper trading
- Status: `todo`
- Priority: `P0`
- Depends on: `M2-02`

### M2-04 Tag and track TV-sourced strategy performance
- Status: `todo`
- Priority: `P1`
- Depends on: `M2-03`

### M2-05 Build degradation detection
- Status: `todo`
- Priority: `P1`
- Depends on: `M2-04`
