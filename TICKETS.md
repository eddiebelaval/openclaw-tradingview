---
last-updated: 2026-04-02
status: CURRENT
active-milestone: 2
---

# TICKETS.md -- DeepStack TV Execution Board

> Canonical ticket board for agent-driven execution.
> Strategy and sequencing: `ROADMAP.md`
> Milestone grouping: `MILESTONE_TASKLISTS.md`
> Current milestone deep-dive: `MILESTONE_2_CHECKLIST.md`

---

## How Agents Should Use This File

This file is the operational source of truth for execution.

### Rules
- Work from the top down.
- Always prefer the **highest-priority unblocked ticket**.
- Only mark a ticket `done` when it is built, verified, and reflected in docs if needed.
- If work uncovers new necessary tasks, add new tickets under the right milestone instead of burying them in notes.
- If a ticket is too large for one session, split it into smaller tickets before starting.
- Future milestone tickets are stubs. Before starting a new milestone, expand its tickets.

### Status Values
- `todo` -- ready to pick up
- `in_progress` -- currently being worked
- `blocked` -- cannot proceed yet
- `done` -- completed and verified

### Update Protocol
When an agent starts work: change one ticket to `in_progress`, add short progress notes.
When an agent finishes work: change to `done`, record verification evidence, update affected docs.
When an agent gets blocked: change to `blocked`, add reason, create follow-up tickets if needed.

---

## Milestone 1 -- Pipeline Foundation -- COMPLETE

All tickets done. See MILESTONE_TASKLISTS.md for details.

---

## Milestone 2 -- Validation Engine

### M2-T1: Clone and Configure TradingView MCP
**Status:** `done`
**Priority:** P0
**Goal:** TradingView MCP bridge operational, registered at user scope.
**Verification:** `claude mcp list | grep tradingview` shows Connected. `tv status` returns success.
**Notes:** Cloned tradesdontlie/tradingview-mcp. Registered user scope. 78 tools available.

### M2-T2: Build tv_bridge.py
**Status:** `done`
**Priority:** P0
**Depends on:** M2-T1
**Goal:** Python wrapper for TV MCP CLI. DataFrame-compatible with data_fetcher.py.
**Verification:** get_quote, get_ohlcv, get_study_values, set_symbol all tested live against SPY.
**Notes:** 10 functions, ~140 LOC. K/M value parsing fixed for narrow-space character.

### M2-T3: Build validate_rankings.py
**Status:** `done`
**Priority:** P0
**Depends on:** M2-T2
**Goal:** Re-run top scripts on TV data. Quantify divergence.
**Verification:** 30% trust rate discovered. 7/10 top scripts diverged. Root cause: bar count, not data.

### M2-T4: Build rolling_scorer.py
**Status:** `done`
**Priority:** P0
**Depends on:** M2-T3
**Goal:** 6-month rolling window scorer. Rank by consistency, not peak performance.
**Verification:** Ran on top 15 across SPY/QQQ/BTC. 3 consistently profitable strategies identified.

### M2-T5: Update Supabase Rankings
**Status:** `done`
**Priority:** P0
**Depends on:** M2-T4
**Goal:** Replace old composite scores with consistency scores. Recompute ranks.
**Verification:** 12 indicators updated. swing-highlow-wick-zones is new #1 (CS=0.755).

### M2-T6: Update Triad + Execution Docs
**Status:** `done`
**Priority:** P1
**Depends on:** M2-T5
**Goal:** VISION, SPEC, BUILDING reflect Phase 4. Execution layer docs created.
**Verification:** All 7 docs created/updated.

### M2-T7: Add --all Flag to Rolling Scorer
**Status:** `done`
**Priority:** P0
**Depends on:** M2-T4
**Goal:** Score all 2,485 scripts, not just top 15. Add batching, progress, error recovery.
**Primary Targets:**
- `scripts/rolling_scorer.py` -- add `--all` argument, batch processing, progress bar, resume from state file
- `results/.rolling_state.json` -- track processed/pending for resumable runs
**Verification:** `rolling_scorer.py --all --ticker SPY` processes all scripts. State file allows resume on interrupt.
**Notes (2026-04-02):** Implemented. Features: `--all` flag walks 2,513 .py files in backtests/. tqdm progress bar with ETA. State file saves every 50 scripts for resume (`--no-resume` to force re-run). Per-ticker output CSV (`rolling_rankings_SPY.csv`). Top 20 summary printed after batch. Smoke tested on 5 scripts.

### M2-T8: Integrate Consistency into Daily Pipeline
**Status:** `todo`
**Priority:** P1
**Depends on:** M2-T7
**Goal:** run_pipeline.py auto-computes rolling consistency score after backtest.
**Primary Targets:**
- `scripts/run_pipeline.py` -- call rolling scorer after backtest step
- `framework/supabase_sync.py` -- sync consistency score to Supabase
**Verification:** New script processed by pipeline gets consistency score in Supabase within same run.

### M2-T9: Fix 300-Bar Bridge Limit
**Status:** `todo`
**Priority:** P2
**Depends on:** M2-T2
**Goal:** Get 500+ bars from TV bridge without JSON buffer overflow.
**Primary Targets:**
- `framework/tv_bridge.py` -- chunk OHLCV requests (2x 250-bar requests) or pipe CLI output to tempfile
**Verification:** `get_ohlcv(count=500)` returns 500 bars without error.

### M2-T10: Document Top 3 Strategies
**Status:** `todo`
**Priority:** P1
**Depends on:** M2-T5
**Goal:** Per-window trade analysis for swing-highlow, liquidities-pivot, smart-money-auto.
**Primary Targets:**
- `results/strategy_reports/` -- one markdown file per strategy with trade log, window stats, risk profile
**Verification:** Each report includes entry/exit dates, per-trade P&L, max drawdown per window.

---

## Milestone 3 -- Full Corpus Scoring (stubs)

### M3-T1: Run Full Corpus Overnight
**Status:** `todo`
**Priority:** P0
**Goal:** Score all 2,485 scripts across 3 tickers.

### M3-T2: Identify Global Top 10
**Status:** `todo`
**Priority:** P0
**Goal:** Find the 10 most consistent strategies across the full corpus.

### M3-T3: Cross-Reference Community Ratings
**Status:** `todo`
**Priority:** P2
**Goal:** Compare consistency ranking vs TradingView upvotes/downloads.

---

## Milestone 4 -- Strategy Graduation (stubs)

### M4-T1: Convert Top Strategy to DAE V2 Format
**Status:** `todo`
**Goal:** Signal generator compatible with DAE V2's Kalshi market making framework.

### M4-T2: Paper Trade for 2 Weeks
**Status:** `todo`
**Goal:** Validate consistency score predictions with real market conditions.

### M4-T3: Eddie Graduation Decision
**Status:** `todo`
**Goal:** Eddie reviews paper results and approves live capital allocation.
