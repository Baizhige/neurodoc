"""
neurodoc - generate kernel + analysis.md from scratch.

Usage:
    python generate.py --dataset openneuro_ds001784
    python generate.py --dataset openneuro_ds001784 openneuro_ds002578
    python generate.py --dataset openneuro_ds001784,openneuro_ds002578  # comma-sep
    python generate.py --dataset openneuro_ds001784 --workers 4 --fresh

Options:
    --dataset   Dataset name(s), space- or comma-separated
    --workers   Max parallel workers (default: 4)
    --fresh     Ignore existing progress, restart from scratch
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
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent

sys.path.insert(0, str(AGENT_DIR))

from llm_adapter import resolve_llm_config
from paths import LOGS_DIR, MACHINE_CONFIG_DIR
from pipeline.runner import Pipeline, load_progress


# ── Config ──────────────────────────────────────────────────────────────────

def _find_config(explicit: str | None) -> dict:
    if explicit:
        return json.loads(Path(explicit).read_text(encoding="utf-8"))
    candidates = sorted(MACHINE_CONFIG_DIR.glob("*.json"))
    if not candidates:
        sys.exit("ERROR: No machine_config JSON found in Script/neurodoc_runtime/machine_config/.")
    if len(candidates) > 1:
        print(f"[generate] Multiple configs found, using: {candidates[-1].name}")
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


# ── Per-dataset worker ───────────────────────────────────────────────────────

def _run_one(dataset_name: str, cfg: dict, fresh: bool, stop_event: threading.Event) -> dict:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{dataset_name}.log"

    log_queue: queue.Queue[str | None] = queue.Queue()
    pause_event = threading.Event()
    start_ts = datetime.now()

    def _write_logs():
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n[generate] Run started: {start_ts.isoformat()}\n{'='*70}\n")
            while True:
                msg = log_queue.get()
                if msg is None:
                    break
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
                f.flush()

    log_thread = threading.Thread(target=_write_logs, daemon=True)
    log_thread.start()

    def _monitor_stop():
        while not stop_event.wait(timeout=1.0):
            pass
        pause_event.set()

    threading.Thread(target=_monitor_stop, daemon=True).start()

    pipeline = Pipeline(dataset_name, cfg, log_queue, pause_event, fresh_start=fresh)
    pipeline.run()

    log_queue.put(None)
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


# ── Summary table ────────────────────────────────────────────────────────────

def _print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 80)
    print(f"{'DATASET':<35} {'STATUS':<12} {'PHASE':<14} {'BUDGET':>8} {'KERNEL':>8} {'TIME':>8}")
    print("-" * 80)
    for r in results:
        kernel_str = {True: "OK", False: "FAIL", None: "-"}.get(r["kernel_ok"], "?")
        elapsed_str = f"{r['elapsed_s'] // 60}m{r['elapsed_s'] % 60:02d}s"
        print(
            f"{r['dataset']:<35} {r['status']:<12} {r['phase']:<14} "
            f"{r['budget_used']:>8} {kernel_str:>8} {elapsed_str:>8}"
        )
    print("=" * 80)
    n_done = sum(1 for r in results if r["phase"] == "done")
    n_fail = sum(1 for r in results if r["status"] == "error")
    print(f"  Done: {n_done}/{len(results)}  |  Errors: {n_fail}  |  Logs: {LOGS_DIR}/\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="neurodoc: generate kernel + analysis.md")
    parser.add_argument("--dataset", "-d", nargs="+", required=True,
                        help="Dataset name(s), space- or comma-separated.")
    parser.add_argument("--workers", "-w", type=int, default=4,
                        help="Max parallel workers (default: 4)")
    parser.add_argument("--fresh", action="store_true",
                        help="Ignore existing progress and restart from scratch")
    parser.add_argument("--config", default=None,
                        help="Path to machine_config JSON (auto-detected if omitted)")
    args = parser.parse_args()

    datasets = []
    for item in args.dataset:
        datasets.extend(d.strip() for d in item.split(",") if d.strip())
    datasets = list(dict.fromkeys(datasets))

    cfg = _find_config(args.config)
    workers = min(args.workers, len(datasets))
    eegunity_workers = max(1, min(4, 32 // workers))
    cfg = dict(cfg)
    cfg["num_workers"] = eegunity_workers

    print(f"[generate] Datasets ({len(datasets)}): {', '.join(datasets[:5])}{'...' if len(datasets) > 5 else ''}")
    print(f"[generate] Workers: {workers} batch × {eegunity_workers} eegunity")
    print(f"[generate] Fresh: {args.fresh} | Logs: {LOGS_DIR}/")
    llm_cfg = resolve_llm_config(cfg)
    print(
        f"[generate] LLM: {cfg.get('model')} "
        f"({llm_cfg.get('active_url_key') or 'UNSET'}) @ {llm_cfg.get('active_url')}"
    )

    stop_event = threading.Event()
    results_lock = threading.Lock()
    completed_results: list[dict] = []

    def _sigint_handler(sig, frame):
        print("\n[generate] Interrupt —pausing all pipelines...")
        stop_event.set()

    signal.signal(signal.SIGINT, _sigint_handler)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_run_one, ds, cfg, args.fresh, stop_event): ds for ds in datasets}
        active = len(futures)
        for future in as_completed(futures):
            ds = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                log_path = LOGS_DIR / f"{ds}.log"
                LOGS_DIR.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as f:
                    f.write(f"[FATAL] {exc}\n{traceback.format_exc()}")
                result = {"dataset": ds, "status": "error", "phase": "?",
                          "budget_used": 0, "kernel_ok": None, "elapsed_s": 0, "log": str(log_path)}
            with results_lock:
                completed_results.append(result)
                active -= 1
                icon = "OK" if result["phase"] == "done" else "ERR" if result["status"] == "error" else "~"
                print(f"[generate] [{icon}] {ds} - phase={result['phase']} "
                      f"budget={result['budget_used']} "
                      f"time={result['elapsed_s'] // 60}m{result['elapsed_s'] % 60:02d}s "
                      f"({active} remaining)")

    order = {ds: i for i, ds in enumerate(datasets)}
    completed_results.sort(key=lambda r: order.get(r["dataset"], 9999))
    _print_summary(completed_results)


if __name__ == "__main__":
    main()
