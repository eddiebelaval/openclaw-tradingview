"""Rolling window backtest scorer. Ranks strategies by consistency, not peak performance.

Splits 2-year yfinance data into rolling 6-month windows, runs each strategy
on every window, and scores by how consistently it performs across all windows.

A strategy that scores well in 4/4 windows is more trustworthy than one that
spiked in one period and flatlined in others.

Usage:
    python scripts/rolling_scorer.py [--top N] [--ticker SPY] [--window-months 6]
    python scripts/rolling_scorer.py --all --ticker SPY       # Score all 2,500+ scripts
    python scripts/rolling_scorer.py --all --ticker SPY --no-resume  # Force re-score everything
"""

import argparse
import csv
import json
import sys
import time
import traceback
from pathlib import Path

import pandas as pd
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework.backtest_engine import load_strategy_from_file, run_backtest
from framework.data_fetcher import fetch_ohlcv

RESULTS_CSV = Path(__file__).parent.parent / "results" / "backtest_results.csv"
BACKTESTS_DIR = Path(__file__).parent.parent / "backtests"
STATE_FILE = Path(__file__).parent.parent / "results" / ".rolling_state.json"


def get_top_scripts(n: int = 25) -> pd.DataFrame:
    """Get top N scripts by original composite score."""
    df = pd.read_csv(RESULTS_CSV)
    clean = df[df["error"].isna()].copy()
    avg = clean.groupby("script_name").agg(
        avg_sharpe=("sharpe_ratio", "mean"),
        avg_roi=("roi_pct", "mean"),
        avg_win_rate=("win_rate_pct", "mean"),
        avg_profit_factor=("profit_factor", "mean"),
        num_tickers=("ticker", "count"),
        category=("category", "first"),
    ).reset_index()
    avg = avg[avg["num_tickers"] == 3]
    avg["composite"] = (
        avg["avg_sharpe"] * 0.3
        + avg["avg_roi"] / 100 * 0.25
        + avg["avg_win_rate"] / 100 * 0.25
        + avg["avg_profit_factor"] / 10 * 0.2
    )
    return avg.nlargest(n, "composite")


def get_all_scripts() -> list[dict]:
    """Walk the backtests/ directory and return all available scripts.

    Returns list of dicts with 'script_name', 'category', 'path'.
    """
    scripts = []
    for category_dir in sorted(BACKTESTS_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        category = category_dir.name
        for py_file in sorted(category_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            scripts.append({
                "script_name": py_file.stem,
                "category": category,
                "path": str(py_file),
            })
    return scripts


def load_state() -> dict:
    """Load resume state from disk."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"completed": {}, "ticker": None, "started_at": None}


def save_state(state: dict):
    """Persist resume state to disk."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def append_result_csv(result: dict, output_path: Path, write_header: bool = False):
    """Append a single result to the rolling rankings CSV."""
    flat = {k: v for k, v in result.items() if k != "windows"}
    for j, w in enumerate(result.get("windows", [])):
        if "error" not in w:
            flat[f"w{j}_roi"] = w.get("roi", 0)
            flat[f"w{j}_trades"] = w.get("trades", 0)

    mode = "w" if write_header else "a"
    with open(output_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=flat.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(flat)


def find_backtest_file(script_name: str, category: str) -> Path | None:
    """Find the Python backtest file for a script."""
    path = BACKTESTS_DIR / category / f"{script_name}.py"
    if path.exists():
        return path
    for p in BACKTESTS_DIR.rglob(f"{script_name}.py"):
        return p
    return None


def split_rolling_windows(data: pd.DataFrame, window_months: int = 6) -> list[tuple[str, pd.DataFrame]]:
    """Split data into rolling windows.

    Returns list of (label, DataFrame) tuples.
    """
    windows = []
    total_days = len(data)
    window_days = window_months * 21  # ~21 trading days per month

    if total_days < window_days:
        return [("full", data)]

    # Non-overlapping windows from the end
    i = total_days
    window_num = 0
    while i - window_days >= 0:
        chunk = data.iloc[i - window_days:i]
        start = chunk.index[0].strftime("%Y-%m")
        end = chunk.index[-1].strftime("%Y-%m")
        label = f"W{window_num} ({start} to {end})"
        windows.append((label, chunk))
        i -= window_days
        window_num += 1

    windows.reverse()
    return windows


def score_script_rolling(
    script_name: str,
    category: str,
    data: pd.DataFrame,
    window_months: int = 6,
) -> dict:
    """Run a script across rolling windows and compute consistency score."""
    result = {
        "script": script_name,
        "category": category,
        "status": "unknown",
    }

    bt_file = find_backtest_file(script_name, category)
    if not bt_file:
        result["status"] = "SKIP"
        result["reason"] = "file not found"
        return result

    try:
        strategy_class = load_strategy_from_file(bt_file)
    except Exception as e:
        result["status"] = "ERROR"
        result["reason"] = f"load: {str(e)[:60]}"
        return result

    windows = split_rolling_windows(data, window_months)
    result["num_windows"] = len(windows)

    window_results = []
    for label, chunk in windows:
        try:
            stats = run_backtest(strategy_class, chunk)
            if "error" in stats:
                window_results.append({"window": label, "error": stats["error"][:60]})
                continue

            roi = stats.get("Return [%]", 0) or 0
            sharpe = stats.get("Sharpe Ratio", 0) or 0
            trades = int(stats.get("# Trades", 0) or 0)
            win_rate = stats.get("Win Rate [%]", 0) or 0
            pf = stats.get("Profit Factor", 0) or 0
            max_dd = stats.get("Max. Drawdown [%]", 0) or 0

            window_results.append({
                "window": label,
                "roi": roi,
                "sharpe": sharpe,
                "trades": trades,
                "win_rate": win_rate,
                "profit_factor": pf,
                "max_dd": max_dd,
            })
        except Exception as e:
            window_results.append({"window": label, "error": str(e)[:60]})

    result["windows"] = window_results

    # Compute consistency metrics
    valid = [w for w in window_results if "error" not in w and w["trades"] > 0]
    result["active_windows"] = len(valid)

    if not valid:
        result["status"] = "NO_TRADES"
        result["consistency_score"] = 0
        return result

    rois = [w["roi"] for w in valid]
    sharpes = [w["sharpe"] for w in valid]
    win_rates = [w["win_rate"] for w in valid]

    # Profitable windows ratio
    profitable_windows = sum(1 for r in rois if r > 0)
    result["profitable_ratio"] = profitable_windows / len(windows)

    # ROI stats
    result["avg_roi"] = np.mean(rois)
    result["roi_std"] = np.std(rois) if len(rois) > 1 else 0
    result["min_roi"] = min(rois)
    result["max_roi"] = max(rois)

    # Sharpe stats
    result["avg_sharpe"] = np.mean(sharpes)
    result["sharpe_std"] = np.std(sharpes) if len(sharpes) > 1 else 0

    # Win rate stats
    result["avg_win_rate"] = np.mean(win_rates)

    # Consistency score:
    # High = profitable in all windows, low variance, decent avg return
    # Formula: profitable_ratio * 0.35 + sharpe_consistency * 0.25 + avg_roi_norm * 0.25 + active_ratio * 0.15
    active_ratio = len(valid) / len(windows)
    sharpe_consistency = max(0, 1 - result["sharpe_std"]) if result["avg_sharpe"] > 0 else 0
    roi_norm = min(result["avg_roi"] / 50, 1) if result["avg_roi"] > 0 else 0

    result["consistency_score"] = (
        result["profitable_ratio"] * 0.35
        + sharpe_consistency * 0.25
        + roi_norm * 0.25
        + active_ratio * 0.15
    )

    result["status"] = "OK"
    return result


def run_top_mode(args):
    """Original mode: score top N scripts by composite ranking."""
    data = _fetch_data(args)
    windows = split_rolling_windows(data, args.window_months)
    _print_windows(windows, args.window_months)

    top = get_top_scripts(args.top)
    print(f"\nScoring top {len(top)} scripts...\n")

    all_results = []
    for i, row in enumerate(top.itertuples(), 1):
        r = score_script_rolling(row.script_name, row.category, data, args.window_months)
        r["orig_composite"] = round(row.composite, 3)
        all_results.append(r)

        if r["status"] in ("SKIP", "ERROR", "NO_TRADES"):
            print(f"  {i:>2}. {row.script_name[:45]:<45} {r['status']}: {r.get('reason', 'no trades')}")
        else:
            w_rois = " | ".join(
                f"{w['roi']:>6.1f}%" if "error" not in w and w["trades"] > 0 else "  n/a "
                for w in r["windows"]
            )
            print(
                f"  {i:>2}. {row.script_name[:45]:<45} "
                f"CS={r['consistency_score']:.3f}  "
                f"P={r['profitable_ratio']:.0%}  "
                f"ROI=[{w_rois}]"
            )

    _print_rankings(all_results, top)
    _save_results(all_results)


def run_all_mode(args):
    """Score all scripts in the backtests/ directory with resume support."""
    scripts = get_all_scripts()
    print(f"Found {len(scripts)} backtest scripts across {len(set(s['category'] for s in scripts))} categories")

    # Resume state
    state = load_state() if args.resume else {"completed": {}, "ticker": None, "started_at": None}

    # If ticker changed from a previous run, warn but allow resume of scored scripts
    if state["ticker"] and state["ticker"] != args.ticker:
        print(f"WARNING: Previous run used ticker {state['ticker']}, this run uses {args.ticker}")
        print(f"  Completed scripts from previous ticker are preserved. Only unscored scripts will use {args.ticker}.")

    already_done = set(state["completed"].get(args.ticker, []))
    remaining = [s for s in scripts if s["script_name"] not in already_done]

    if already_done:
        print(f"Resuming: {len(already_done)} already scored, {len(remaining)} remaining")

    if not remaining:
        print("All scripts already scored. Use --no-resume to re-run.")
        return

    state["ticker"] = args.ticker
    if not state["started_at"]:
        state["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    data = _fetch_data(args)
    windows = split_rolling_windows(data, args.window_months)
    _print_windows(windows, args.window_months)

    output = Path(__file__).parent.parent / "results" / f"rolling_rankings_{args.ticker}.csv"
    write_header = not output.exists() or not args.resume

    all_results = []
    ok_count = 0
    skip_count = 0
    error_count = 0
    t0 = time.time()

    bar = tqdm(remaining, desc=f"Scoring ({args.ticker})", unit="script", ncols=100)
    for s in bar:
        r = score_script_rolling(s["script_name"], s["category"], data, args.window_months)
        r["orig_composite"] = 0  # no composite ranking in --all mode
        all_results.append(r)

        # Track status
        if r["status"] == "OK":
            ok_count += 1
            append_result_csv(r, output, write_header=write_header)
            write_header = False
        elif r["status"] == "SKIP":
            skip_count += 1
        else:
            error_count += 1

        # Update state for resume
        if args.ticker not in state["completed"]:
            state["completed"][args.ticker] = []
        state["completed"][args.ticker].append(s["script_name"])

        # Save state every 50 scripts
        if len(all_results) % 50 == 0:
            save_state(state)

        # Update progress bar
        elapsed = time.time() - t0
        rate = len(all_results) / elapsed if elapsed > 0 else 0
        eta_min = (len(remaining) - len(all_results)) / rate / 60 if rate > 0 else 0
        bar.set_postfix(ok=ok_count, skip=skip_count, err=error_count, eta=f"{eta_min:.0f}m")

    # Final state save
    state["last_completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save_state(state)

    elapsed = time.time() - t0
    print(f"\nCompleted {len(all_results)} scripts in {elapsed/60:.1f} minutes")
    print(f"  OK: {ok_count} | Skipped: {skip_count} | Errors: {error_count}")
    print(f"  Results: {output}")
    print(f"  State: {STATE_FILE}")

    if ok_count > 0:
        # Print top 20 from this run
        scored = [r for r in all_results if r["status"] == "OK"]
        scored.sort(key=lambda x: x["consistency_score"], reverse=True)
        print(f"\nTop 20 by consistency (this batch):")
        print(f"{'Rank':<5} {'CS':>6} {'Profit%':>8} {'Avg ROI':>9} {'Category':<20} {'Script':<45}")
        print("-" * 110)
        for i, r in enumerate(scored[:20], 1):
            print(
                f"{i:<5} {r['consistency_score']:>6.3f} {r['profitable_ratio']:>7.0%} "
                f"{r['avg_roi']:>8.1f}% {r['category']:<20} {r['script'][:45]}"
            )


def _fetch_data(args):
    """Fetch OHLCV data for the given ticker."""
    print(f"Fetching {args.ticker} data...")
    data = fetch_ohlcv(args.ticker, period="2y", interval="1d", use_cache=False)
    print(f"Got {len(data)} bars: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    return data


def _print_windows(windows, window_months):
    """Print rolling window breakdown."""
    print(f"Rolling windows ({window_months}mo): {len(windows)}")
    for label, chunk in windows:
        print(f"  {label}: {len(chunk)} bars")


def _print_rankings(all_results, top):
    """Print the final ranking table."""
    scored = [r for r in all_results if r["status"] == "OK"]
    scored.sort(key=lambda x: x["consistency_score"], reverse=True)

    print(f"\n{'='*120}")
    print(f"ROLLING WINDOW RANKINGS (sorted by consistency, not peak performance)")
    print(f"{'='*120}")
    print(f"{'Rank':<5} {'CS':>6} {'Profit%':>8} {'Avg ROI':>9} {'ROI Std':>8} {'Min ROI':>8} {'Max ROI':>8} {'Orig':>7} {'Script':<45}")
    print("-" * 120)

    for i, r in enumerate(scored, 1):
        moved = ""
        orig_rank = next((j for j, row in enumerate(top.itertuples(), 1) if row.script_name == r["script"]), "?")
        if isinstance(orig_rank, int) and orig_rank != i:
            delta = orig_rank - i
            moved = f" (+{delta})" if delta > 0 else f" ({delta})"

        print(
            f"{i:<5} {r['consistency_score']:>6.3f} {r['profitable_ratio']:>7.0%} "
            f"{r['avg_roi']:>8.1f}% {r['roi_std']:>7.1f}% "
            f"{r['min_roi']:>7.1f}% {r['max_roi']:>7.1f}% "
            f"{r['orig_composite']:>7.3f} {r['script'][:43]:<43}{moved}"
        )


def _save_results(all_results):
    """Save results to rolling_rankings.csv."""
    scored = [r for r in all_results if r["status"] == "OK"]
    scored.sort(key=lambda x: x["consistency_score"], reverse=True)

    output = Path(__file__).parent.parent / "results" / "rolling_rankings.csv"
    flat_results = []
    for r in scored:
        flat = {k: v for k, v in r.items() if k != "windows"}
        for j, w in enumerate(r.get("windows", [])):
            if "error" not in w:
                flat[f"w{j}_roi"] = w.get("roi", 0)
                flat[f"w{j}_trades"] = w.get("trades", 0)
        flat_results.append(flat)

    if flat_results:
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=flat_results[0].keys())
            writer.writeheader()
            writer.writerows(flat_results)
        print(f"\nSaved to: {output}")

    failed = [r for r in all_results if r["status"] != "OK"]
    if failed:
        print(f"\nSkipped/failed: {len(failed)}")
        for r in failed:
            print(f"  - {r['script']}: {r['status']} ({r.get('reason', '')})")


def main():
    parser = argparse.ArgumentParser(description="Rolling window backtest scorer")
    parser.add_argument("--top", type=int, default=25, help="Number of top scripts to evaluate")
    parser.add_argument("--all", action="store_true", help="Score ALL scripts in backtests/, not just top N")
    parser.add_argument("--ticker", default="SPY", choices=["SPY", "BTC", "QQQ"])
    parser.add_argument("--window-months", type=int, default=6, help="Window size in months")
    parser.add_argument("--no-resume", dest="resume", action="store_false", default=True,
                        help="Ignore previous state and re-score everything")
    args = parser.parse_args()

    if getattr(args, "all"):
        run_all_mode(args)
    else:
        run_top_mode(args)


if __name__ == "__main__":
    main()
