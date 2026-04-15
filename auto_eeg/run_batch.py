#!/usr/bin/env python3
"""
auto_eeg batch runner — non-web CLI for running the full pipeline on multiple datasets.

Usage:
    python run_batch.py --dataset openneuro_ds001784 openneuro_ds002578 openneuro_ds003061
    python run_batch.py --dataset openneuro_ds001784,openneuro_ds002578   # comma-sep also works
    python run_batch.py --dataset openneuro_ds001784 --workers 4 --fresh

Options:
    --dataset   One or more dataset names (space- or comma-separated)
    --workers   Max parallel workers (default: 8)
    --fresh     Ignore existing progress and restart from scratch
    --config    Path to machine_config JSON (auto-detected if omitted)
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────
AUTO_EEG_DIR = Path(__file__).parent
BIDS_ROOT = AUTO_EEG_DIR.parent
LOGS_DIR = AUTO_EEG_DIR / "logs"
MACHINE_CFG_DIR = AUTO_EEG_DIR / "machine_config"

sys.path.insert(0, str(AUTO_EEG_DIR))

from pipeline.runner import Pipeline, load_progress


# ── Config loading ──────────────────────────────────────────────────────────

def _find_config(explicit: str | None) -> dict:
    if explicit:
        return json.loads(Path(explicit).read_text(encoding="utf-8"))
    candidates = sorted(MACHINE_CFG_DIR.glob("*.json"))
    if not candidates:
        sys.exit("ERROR: No machine_config JSON found. Run the auto_eeg web UI once to save settings.")
    if len(candidates) > 1:
        print(f"[batch] Multiple configs found, using: {candidates[-1].name}")
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


# ── Per-dataset worker ──────────────────────────────────────────────────────

def _run_one(dataset_name: str, cfg: dict, fresh: bool, stop_event: threading.Event) -> dict:
    """
    Run the pipeline for one dataset. Writes logs to logs/<dataset>.log.
    Returns a result summary dict.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{dataset_name}.log"

    log_queue: queue.Queue[str | None] = queue.Queue()
    pause_event = threading.Event()

    start_ts = datetime.now()

    def _write_logs():
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"[batch] Run started: {start_ts.isoformat()}\n")
            f.write(f"{'='*70}\n")
            while True:
                msg = log_queue.get()
                if msg is None:
                    break
                line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
                f.write(line)
                f.flush()

    log_thread = threading.Thread(target=_write_logs, daemon=True)
    log_thread.start()

    # Watch for global stop signal
    def _monitor_stop():
        while not stop_event.wait(timeout=1.0):
            pass
        pause_event.set()

    monitor_thread = threading.Thread(target=_monitor_stop, daemon=True)
    monitor_thread.start()

    pipeline = Pipeline(dataset_name, cfg, log_queue, pause_event, fresh_start=fresh)
    pipeline.run()

    log_queue.put(None)  # signal writer to finish
    log_thread.join(timeout=5)

    elapsed = (datetime.now() - start_ts).total_seconds()
    prog = load_progress(dataset_name)

    return {
        "dataset": dataset_name,
        "status": prog.get("status", prog.get("phase", "unknown")),
        "phase": prog.get("phase", "?"),
        "budget_used": prog.get("budget_used", 0),
        "kernel_ok": prog.get("kernel_ok", None),
        "elapsed_s": round(elapsed),
        "log": str(log_path),
    }


# ── Summary table ───────────────────────────────────────────────────────────

def _print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 80)
    print(f"{'DATASET':<35} {'STATUS':<12} {'PHASE':<14} {'BUDGET':>8} {'KERNEL':>8} {'TIME':>8}")
    print("-" * 80)
    for r in results:
        kernel_str = {True: "OK", False: "FAIL", None: "-"}.get(r["kernel_ok"], "?")
        elapsed_str = f"{r['elapsed_s'] // 60}m{r['elapsed_s'] % 60:02d}s"
        print(
            f"{r['dataset']:<35} "
            f"{r['status']:<12} "
            f"{r['phase']:<14} "
            f"{r['budget_used']:>8} "
            f"{kernel_str:>8} "
            f"{elapsed_str:>8}"
        )
    print("=" * 80)
    n_done = sum(1 for r in results if r["phase"] == "done")
    n_fail = sum(1 for r in results if r["status"] == "error")
    print(f"  Done: {n_done}/{len(results)}  |  Errors: {n_fail}  |  Logs: {LOGS_DIR}/")
    print()


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="auto_eeg batch runner")
    parser.add_argument(
        "--dataset", "-d", nargs="+", required=True,
        help="Dataset name(s). Space- or comma-separated.",
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=4,
        help="Max parallel workers (default: 4)",
    )
    parser.add_argument(
        "--fresh", action="store_true",
        help="Ignore existing progress and restart from scratch",
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to machine_config JSON (auto-detected if omitted)",
    )
    args = parser.parse_args()

    # Normalize dataset list (handle comma-separated input)
    datasets = []
    for item in args.dataset:
        datasets.extend(d.strip() for d in item.split(",") if d.strip())
    datasets = list(dict.fromkeys(datasets))  # deduplicate, preserve order

    cfg = _find_config(args.config)
    workers = min(args.workers, len(datasets))

    # Cap total processes: batch_workers × eegunity_num_workers ≤ 32
    # Override num_workers in config so each pipeline respects the cap.
    eegunity_workers = max(1, min(4, 32 // workers))
    cfg = dict(cfg)  # don't mutate the original
    cfg["num_workers"] = eegunity_workers

    print(f"[batch] Datasets ({len(datasets)}): {', '.join(datasets[:5])}{'...' if len(datasets) > 5 else ''}")
    print(f"[batch] Workers: {workers} (batch) × {eegunity_workers} (eegunity) = {workers * eegunity_workers} max processes")
    print(f"[batch] Fresh: {args.fresh} | Logs: {LOGS_DIR}/")
    print(f"[batch] LLM: {cfg.get('model')} @ {cfg.get('url')}")
    print(f"[batch] Starting...")

    # Global stop event — set on Ctrl+C so all pipelines pause cleanly
    stop_event = threading.Event()
    results_lock = threading.Lock()
    completed_results: list[dict] = []

    def _sigint_handler(sig, frame):
        print("\n[batch] Interrupt received — sending pause to all running pipelines...")
        stop_event.set()

    signal.signal(signal.SIGINT, _sigint_handler)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_run_one, ds, cfg, args.fresh, stop_event): ds
            for ds in datasets
        }

        active = len(futures)
        for future in as_completed(futures):
            ds = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "dataset": ds,
                    "status": "error",
                    "phase": "?",
                    "budget_used": 0,
                    "kernel_ok": None,
                    "elapsed_s": 0,
                    "log": str(LOGS_DIR / f"{ds}.log"),
                }
                # Write the exception to the log
                log_path = LOGS_DIR / f"{ds}.log"
                LOGS_DIR.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as f:
                    import traceback
                    f.write(f"[FATAL] Unhandled exception: {exc}\n")
                    f.write(traceback.format_exc())

            with results_lock:
                completed_results.append(result)
                active -= 1
                status_icon = "✓" if result["phase"] == "done" else "✗" if result["status"] == "error" else "~"
                print(
                    f"[batch] [{status_icon}] {ds} — "
                    f"phase={result['phase']} budget={result['budget_used']} "
                    f"time={result['elapsed_s'] // 60}m{result['elapsed_s'] % 60:02d}s "
                    f"({active} remaining)"
                )

    # Sort results in original dataset order
    order = {ds: i for i, ds in enumerate(datasets)}
    completed_results.sort(key=lambda r: order.get(r["dataset"], 9999))

    _print_summary(completed_results)


if __name__ == "__main__":
    main()
