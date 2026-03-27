---
last-updated: 2026-03-26
status: CURRENT
active-milestone: 1
---

# ROADMAP.md -- DeepStack TradingView (OpenClaw)

> Execution roadmap derived from the project's VISION and BUILDING docs.
> Operational companion: `MILESTONE_TASKLISTS.md`
> Canonical execution board: `TICKETS.md`
> Current milestone deep-dive: `MILESTONE_1_CHECKLIST.md`

---

## Execution Layer

| Doc | Role | Audience |
|---|---|---|
| `ROADMAP.md` | Strategy, sequencing, gates | Humans and agents |
| `MILESTONE_TASKLISTS.md` | Tactical task lists per milestone | Humans and agents |
| `TICKETS.md` | Agent-executable work units with dependencies | Agents (primary), humans |
| `MILESTONE_N_CHECKLIST.md` | Deep-dive for the current milestone with file-level targets | Agents |

**Naming convention:** The current milestone always has a dedicated checklist named `MILESTONE_N_CHECKLIST.md` (e.g., `MILESTONE_1_CHECKLIST.md`). When a milestone closes, its checklist is archived and replaced with the next milestone's checklist. Only one active checklist exists at a time.

**Reconciliation:** Each milestone's final ticket updates all docs to reflect shipped state. Frontmatter timestamps are updated. The `active-milestone` field increments.

---

## Current Read

DeepStack TradingView (OpenClaw) is an **automated indicator discovery engine**. It scrapes TradingView community indicators, converts PineScript to Python backtests via Claude Haiku, runs them against real market data, and surfaces winners by composite score. All 3 VISION pillars are REALIZED. 40% distance from vision.

What is true right now:
- 3,921 Python backtest scripts generated from scraped PineScript sources.
- 1,964 PineScript source files scraped across 10 TradingView categories.
- Claude Haiku converts PineScript to Python backtests (`framework/pine_converter.py`).
- Supabase tables rank results by composite score (30% Sharpe + 25% ROI + 25% Win Rate + 20% Profit Factor).
- FastAPI server at port 8100 for on-demand backtesting (`api/server.py`).
- Trigger auto-recalculates scores on insert.
- `ds_tv_backtests` table has 4,764 rows; 16 pass stock_momentum filter (Sharpe>=1, WR>=60%, trades>=5).

What is not true yet:
- Full pipeline has NOT been run against all 3,921 scripts (many converted but not backtested).
- Results NOT filtered for quality (Sharpe >= 1, WR >= 60%, trades >= 5).
- Top performers NOT fed into DeepStack's IBKR strategy pool.
- `scripts/daily_run.sh` cron NOT deployed for continuous discovery.
- No monitoring or alerting on pipeline failures.
- No dashboard for browsing results (Supabase tables only).

## Planning Principles

- **Run the pipeline before building features.** The framework is built. The bottleneck is execution, not architecture. Run backtests, filter results, prove the pipeline works end-to-end.
- **Quality over quantity.** 3,921 scripts mean nothing if none survive the quality filter. The output is a shortlist of strategies that pass Sharpe >= 1, WR >= 60%, trades >= 5.
- **Automate before optimizing.** Get `daily_run.sh` running on cron before tuning scoring weights or adding new categories.
- **Feed the main engine.** This project exists to supply DeepStack's IBKR strategy pool with backtested, ranked indicators. If strategies never reach live trading, the pipeline is a toy.

## Universal Definition of Done

Before calling any milestone done, confirm all three:
- **Built:** the pipeline stage exists in code and runs without errors.
- **Verified:** the output data is correct, filtered, and stored in Supabase.
- **Operational:** the stage runs unattended (cron, monitoring) and feeds downstream systems.

If one of those is missing, the work is still in progress.

---

## Now

### Milestone 1 -- Full Pipeline Run
**Window:** immediate
**Goal:** Run backtests against all 3,921 scripts across SPY/QQQ/BTC. Filter results for quality. Set up cron for daily runs. This is the gate between "framework built" and "alpha discovery operational."

#### Deliverables
- Complete backtest run across all converted scripts and target tickers
- Quality filter applied (Sharpe >= 1, WR >= 60%, trades >= 5)
- `daily_run.sh` deployed on cron for continuous discovery
- Pipeline failure monitoring (at minimum: exit code logging, Supabase error rows)

#### Workstreams
- **Batch execution**
  Run `scripts/run_pipeline.py` against all 3,921 scripts for SPY, QQQ, BTC. Track progress, handle failures gracefully, resume from where it left off.
- **Quality filtering**
  Apply composite score thresholds. Surface only strategies that meet minimum quality bars. Store filtered results in a dedicated view or table.
- **Automation**
  Deploy `scripts/daily_run.sh` on cron. Verify it runs unattended, handles errors, and logs results.
- **Monitoring**
  Detect pipeline failures. At minimum: log exit codes, count failed backtests, alert on zero new results.

#### Exit Criteria
- All 3,921 scripts have been backtested against SPY, QQQ, and BTC (or failures logged).
- Quality-filtered results are queryable in Supabase.
- `daily_run.sh` is running on cron and has completed at least one unattended cycle.
- Pipeline failures are logged and discoverable.

---

## Next

### Milestone 2 -- IBKR Integration
**Window:** after full pipeline run is operational
**Goal:** Feed top performers into DeepStack's live trading strategy pool. Monitor strategy performance. Feedback loop for degrading strategies.

#### Deliverables
- Top strategies exported from `ds_tv_backtests` into IBKR-compatible format
- Strategy onboarding into DeepStack's paper trading pipeline
- Performance monitoring for TV-sourced strategies vs native strategies
- Degradation detection: flag strategies whose live performance diverges from backtest

#### Exit Criteria
- At least 3 TV-sourced strategies are running in DeepStack paper trading.
- Performance tracking distinguishes TV-sourced from native strategies.
- Degradation alerts flag strategies that drop below backtest expectations.

---

## Not Now

Intentionally deferred to protect pipeline focus:
- Dashboard UI for browsing results (Supabase is sufficient)
- Additional ticker coverage beyond SPY/QQQ/BTC
- Alternative AI models for PineScript conversion
- Strategy parameter optimization / walk-forward analysis
- Public API for external consumers

---

## Priority Stack

The canonical priority order and ticket dependencies live in `TICKETS.md`. At a glance:

1. Batch backtest execution across all scripts (M1)
2. Quality filtering and ranked results (M1)
3. Cron deployment for daily_run.sh (M1)
4. Pipeline monitoring and error handling (M1)
5. Verification sweep (M1)
6. IBKR strategy export (M2)
7. Paper trading onboarding (M2)
8. Degradation detection (M2)
