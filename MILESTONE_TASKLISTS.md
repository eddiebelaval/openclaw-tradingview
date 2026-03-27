---
last-updated: 2026-03-26
status: CURRENT
active-milestone: 1
---

# MILESTONE_TASKLISTS.md -- DeepStack TradingView (OpenClaw)

> Execution task lists for all roadmap milestones.
> Strategy and sequencing: `ROADMAP.md`
> Canonical execution board: `TICKETS.md`
> Current milestone deep-dive: `MILESTONE_1_CHECKLIST.md`

---

## How To Use This Doc

- `ROADMAP.md` explains sequence, intent, and gates.
- This doc turns each milestone into a practical task list with verification criteria.
- `TICKETS.md` is the canonical execution board. Agents work from tickets, not this file.
- The current milestone always has a dedicated checklist (e.g., `MILESTONE_1_CHECKLIST.md`) with file-level detail.

If a task is vague, it is not ready. Break it down further before starting.

---

## Milestone 1 -- Full Pipeline Run

Deep-dive: `MILESTONE_1_CHECKLIST.md`

### Todo
- [ ] Audit current state: how many of 3,921 scripts have been backtested vs only converted
- [ ] Run `scripts/run_pipeline.py` against all unconverted/unbacetested scripts for SPY, QQQ, BTC
- [ ] Handle pipeline failures gracefully (log, skip, continue)
- [ ] Apply quality filter: Sharpe >= 1, WR >= 60%, trades >= 5
- [ ] Store filtered results in a queryable Supabase view or table
- [ ] Run `scripts/update_rankings.py` to recalculate composite scores
- [ ] Deploy `scripts/daily_run.sh` on cron (launchd or crontab)
- [ ] Verify cron completes at least one unattended cycle
- [ ] Add pipeline failure logging (exit codes, error counts, zero-result alerts)
- [ ] Reconcile docs after the work lands

### Verification
- [ ] All 3,921 scripts attempted (success or logged failure)
- [ ] Quality-filtered results exist in Supabase and are queryable
- [ ] Composite scores are current (recalculated after full run)
- [ ] `daily_run.sh` has run unattended at least once
- [ ] Pipeline errors are logged and discoverable
- [ ] Python scripts run without unhandled exceptions

### Done When
- [ ] Pipeline is operational: scrape, convert, backtest, rank, filter -- end to end
- [ ] Quality-filtered shortlist of strategies exists
- [ ] Daily automation is running
- [ ] Pipeline failures are visible without manual inspection

---

## Milestone 2 -- IBKR Integration

### Todo
- [ ] Define export format for TV-sourced strategies compatible with DeepStack IBKR pipeline
- [ ] Build export script: top N strategies from `ds_tv_backtests` to IBKR strategy format
- [ ] Onboard TV-sourced strategies into DeepStack paper trading
- [ ] Tag TV-sourced strategies for separate performance tracking
- [ ] Build degradation detection: compare live performance vs backtest expectations
- [ ] Set up alerts for strategies that fall below backtest thresholds

### Verification
- [ ] At least 3 TV-sourced strategies running in DeepStack paper trading
- [ ] Performance tracking distinguishes TV-sourced from native strategies
- [ ] Degradation alert fires when a strategy underperforms backtest by defined threshold

### Done When
- [ ] TV-sourced strategies are live in paper trading
- [ ] Performance feedback loop is operational
- [ ] Degrading strategies are automatically flagged

---

## Execution Order

See `TICKETS.md` for the canonical priority order and dependency graph. Milestones are sequential: Milestone 1's gate must close before Milestone 2 opens.
