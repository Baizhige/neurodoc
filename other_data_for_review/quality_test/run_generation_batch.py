#!/usr/bin/env python3
"""Re-run NeuroDoc generation for completed datasets into a new experiment batch.

Output is redirected to Script/neurodoc_test_experiment/batches/<model>_<timestamp>/
via monkey-patching neurodoc.paths at process startup. dataset_document/ is NOT modified.

The model is read from the machine config (same as `neurodoc.generate`). Use --config
to point to a specific config file, or let it auto-detect from MACHINE_CONFIG_DIR.

Usage:
    python Script/neurodoc_test_experiment/run_generation_batch.py
    python Script/neurodoc_test_experiment/run_generation_batch.py --workers 2
    python Script/neurodoc_test_experiment/run_generation_batch.py --fresh
    python Script/neurodoc_test_experiment/run_generation_batch.py --config /path/to/config.json
    python Script/neurodoc_test_experiment/run_generation_batch.py \\
        --datasets openneuro_ds001787 openneuro_ds001849

Notes:
    - Patch must happen before any neurodoc.pipeline.* imports, so path values are
      bound correctly in each sub-module.
    - sys.modules["paths"] is also set so modules using bare `from paths import X`
      pick up the same patched module.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENT_DIR = Path(__file__).resolve().parent
DATASET_DOCUMENT_DIR = ROOT / "dataset_document"

_STATUS_RE = re.compile(r">\s*\*\*Status\*\*:\s*(\w+)", re.MULTILINE)


def find_completed_datasets() -> list[str]:
    datasets: list[str] = []
    for analysis in sorted(DATASET_DOCUMENT_DIR.glob("*/analysis.md")):
        try:
            content = analysis.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        m = _STATUS_RE.search(content)
        if m and m.group(1).strip() == "completed":
            datasets.append(analysis.parent.name)
    return datasets


def _patch_paths(batch_dir: Path) -> None:
    """Redirect neurodoc output paths to the experiment batch directory.

    Must be called BEFORE importing any neurodoc.pipeline.* modules so that
    `from paths import X` bindings in those modules get the patched values.
    KERNELS_DIR is also patched so install_kernel() writes to the batch directory
    instead of overwriting the original neurodoc/kernels/.
    """
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "neurodoc"))

    import neurodoc.paths as _paths

    _paths.DATASET_DOCUMENT_DIR = batch_dir / "generated_docs"
    _paths.PROGRESS_DIR = batch_dir / "cache"
    _paths.LOGS_DIR = batch_dir / "logs"
    _paths.KERNELS_DIR = batch_dir / "kernels"  # prevent overwriting original kernels

    # Register as bare "paths" so modules using `from paths import X` also patch
    sys.modules["paths"] = _paths  # type: ignore[assignment]


def _load_config(explicit: str | None) -> dict:
    """Load machine config without importing any pipeline modules."""
    if explicit:
        return json.loads(Path(explicit).read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT))
    from neurodoc.paths import MACHINE_CONFIG_DIR  # noqa: PLC0415
    candidates = sorted(MACHINE_CONFIG_DIR.glob("*.json"))
    if not candidates:
        sys.exit("ERROR: No machine_config JSON found in Script/neurodoc_runtime/machine_config/.")
    if len(candidates) > 1:
        print(f"[config] Multiple configs found, using: {candidates[-1].name}")
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def _seed_generated_docs(datasets: list[str], generated_docs_dir: Path) -> None:
    """Pre-populate generated_docs/<dataset>/ with reference materials from dataset_document/.

    context_builder uses DATASET_DOCUMENT_DIR both as the read source (PDFs, existing
    analysis.md) and the write target. After patching, it points to generated_docs/.
    Seeding ensures the directory exists and reference files are available.
    analysis.md is intentionally excluded so the pipeline generates it from scratch.
    """
    import shutil  # noqa: PLC0415
    for ds in datasets:
        src = DATASET_DOCUMENT_DIR / ds
        dst = generated_docs_dir / ds
        dst.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            for item in src.iterdir():
                if item.name == "analysis.md":
                    continue  # fresh generation — do not seed the existing doc
                target = dst / item.name
                if item.is_file() and not target.exists():
                    shutil.copy2(item, target)
                elif item.is_dir() and not target.exists():
                    shutil.copytree(item, target)


def _run_pipeline(datasets: list[str], workers: int, fresh: bool, cfg: dict) -> list:
    # Imports happen AFTER _patch_paths() so sub-modules bind the patched paths
    from neurodoc.generate import _print_summary, _run_one  # noqa: PLC0415
    import threading  # noqa: PLC0415
    from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: PLC0415

    stop_event = threading.Event()

    results = []
    with ThreadPoolExecutor(max_workers=min(workers, len(datasets))) as pool:
        futures = {
            pool.submit(_run_one, ds, cfg, fresh, stop_event): ds
            for ds in datasets
        }
        try:
            for fut in as_completed(futures):
                ds = futures[fut]
                try:
                    result = fut.result()
                    results.append(result)
                    print(
                        f"  [{result['phase']:12}] {ds:<40}"
                        f" budget={result['budget_used']:>5}"
                    )
                except Exception as exc:
                    print(f"  [ERROR      ] {ds:<40} {exc}")
                    results.append({"dataset": ds, "phase": "error", "status": "error",
                                    "budget_used": 0, "kernel_ok": None, "elapsed_s": 0})
        except KeyboardInterrupt:
            print("\nInterrupted — stopping workers ...")
            stop_event.set()

    _print_summary(results)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-generate NeuroDoc docs for completed datasets into an experiment batch"
    )
    parser.add_argument("--config", default=None,
                        help="Path to machine_config JSON (auto-detected if omitted)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--fresh", action="store_true", help="Ignore existing progress")
    parser.add_argument("--datasets", nargs="+", help="Subset of datasets (default: all completed)")
    args = parser.parse_args()

    # Load config BEFORE patching paths — pipeline imports must happen after the patch,
    # but _load_config only touches neurodoc.paths (MACHINE_CONFIG_DIR), not pipeline modules.
    cfg = _load_config(args.config)
    model_name = cfg.get("model", "unknown").replace("/", "-").replace(":", "-")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    batch_id = f"{model_name}_{ts}"
    batch_dir = EXPERIMENT_DIR / "batches" / batch_id
    (batch_dir / "generated_docs").mkdir(parents=True, exist_ok=True)
    (batch_dir / "cache").mkdir(parents=True, exist_ok=True)
    (batch_dir / "logs").mkdir(parents=True, exist_ok=True)
    (batch_dir / "kernels").mkdir(parents=True, exist_ok=True)

    datasets = args.datasets or find_completed_datasets()

    print(f"Batch ID  : {batch_id}")
    print(f"Model     : {model_name}")
    print(f"Datasets  : {len(datasets)}")
    print(f"Workers   : {args.workers}")
    print(f"Fresh     : {args.fresh}")
    print(f"Output    : {batch_dir}\n")

    batch_info: dict = {
        "batch_id": batch_id,
        "model": model_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "regeneration",
        "datasets": datasets,
        "total": len(datasets),
        "fresh": args.fresh,
    }
    (batch_dir / "batch_info.json").write_text(
        json.dumps(batch_info, indent=2, ensure_ascii=False)
    )

    # Patch AFTER batch_dir is known, BEFORE pipeline modules are imported
    _patch_paths(batch_dir)

    # Seed generated_docs/<dataset>/ with reference materials (PDFs etc.) from dataset_document/.
    # context_builder reads from DATASET_DOCUMENT_DIR, which is now generated_docs/ after patching.
    print("Seeding reference materials into generated_docs/ ...")
    _seed_generated_docs(datasets, batch_dir / "generated_docs")
    print("Starting generation ...\n")

    results = _run_pipeline(datasets, args.workers, args.fresh, cfg)

    # Update batch_info with final stats
    n_done = sum(1 for r in results if r.get("phase") == "done")
    batch_info["results_summary"] = {
        "done": n_done,
        "total": len(results),
        "errors": sum(1 for r in results if r.get("status") == "error"),
    }
    (batch_dir / "batch_info.json").write_text(
        json.dumps(batch_info, indent=2, ensure_ascii=False)
    )

    print(f"\nBatch complete: {batch_id}")
    print(f"Next step:")
    print(
        f"  python Script/neurodoc_test_experiment/audit/audit_batch.py"
        f" --batch-id {batch_id}"
    )


if __name__ == "__main__":
    main()
