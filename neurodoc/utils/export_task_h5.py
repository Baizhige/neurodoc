"""export_task_h5.py — One command, one config file: export task-ready HDF5s.

Usage
-----
    python -m neurodoc.utils.export_task_h5 --config export_jobs.yaml
    python -m neurodoc.utils.export_task_h5 --config export_jobs.yaml --cache_dir /scratch/cache

The config file is the single source of truth for what to export and how to
preprocess it. CLI flags (--cache_dir, --eegunity_path, --log_dir, --num_workers,
--rebuild) override the matching global keys when given.

Config schema (YAML)
--------------------
    cache_dir:     /path/to/cache           # required (here or via --cache_dir)
    eegunity_path: /path/to/Script          # optional; default = local Script/
    log_dir:       /path/to/logs            # optional; tee run output to a file
    dataset_roots: [/path/to/raw]           # optional; used to locate raw data
    num_workers:   8

    default:                                 # broadest scope (fallback for all jobs)
      pipeline: null                         # null = no preprocessing
      pipeline_param: {}
      common_channels: null                  # null = no alignment; or a list
      min_matched_channels: 1
      epoch_param: {}                        # overrides doc tmin/tmax/...

    datasets:                                # per-dataset scope (overrides default)
      bcic_iv_2a:
        raw_path: /path/to/bcic_iv_2a        # optional explicit raw dir
        common_channels: [C3, Cz, C4]
        epoch_param: {tmin: -0.5, tmax: 4.0}

    jobs:                                     # task scope (overrides dataset + default)
      - {dataset: figshare_meng2019, task: 1}
      - {dataset: bcic_iv_2a, task: 2, epoch_param: {tmin: 0, tmax: 2}}

Scope resolution is per parameter, finest-wins, whole-value (option A): for each
of pipeline / pipeline_param / common_channels / min_matched_channels /
epoch_param, the value from the most specific scope that sets it is used as-is
(no deep merge across scopes). epoch_param is then layered over the doc defaults.

Exit code is non-zero if any job is skipped or failed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path
from typing import Dict, List

import yaml

from .task_h5_builder import JobResult, build_task_hdf5

_PROC_KEYS = ("pipeline", "pipeline_param", "common_channels",
              "min_matched_channels", "epoch_param", "max_files")


class _Tee:
    """Write to console and (optionally) a log file simultaneously."""

    def __init__(self, log_path=None):
        self._fh = open(log_path, "w", encoding="utf-8") if log_path else None

    def __call__(self, *args):
        msg = " ".join(str(a) for a in args)
        print(msg)
        if self._fh:
            self._fh.write(msg + "\n")
            self._fh.flush()

    def close(self):
        if self._fh:
            self._fh.close()


def _resolve_params(default: Dict, dataset_cfg: Dict, job: Dict) -> Dict:
    """Finest-wins, whole-value-per-key (option A) across default<dataset<job."""
    resolved: Dict = {}
    for key in _PROC_KEYS:
        if key in job:
            resolved[key] = job[key]
        elif key in dataset_cfg:
            resolved[key] = dataset_cfg[key]
        elif key in default:
            resolved[key] = default[key]
        else:
            resolved[key] = None
    return resolved


def _load_config(path: str) -> Dict:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"config file not found: {path}")
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(cfg, dict):
        raise ValueError("config root must be a mapping.")
    if not cfg.get("jobs"):
        raise ValueError("config has no 'jobs' list.")
    return cfg


def main(argv: List[str] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Export task-ready HDF5 files from analysis.md tasks via EEGUnity.")
    ap.add_argument("--config", required=True, help="Path to the YAML job config.")
    ap.add_argument("--cache_dir", default=None, help="Override global cache_dir.")
    ap.add_argument("--eegunity_path", default=None, help="Override global eegunity_path.")
    ap.add_argument("--log_dir", default=None, help="Override global log_dir.")
    ap.add_argument("--num_workers", type=int, default=None, help="Override global num_workers.")
    ap.add_argument("--max_files", type=int, default=None,
                    help="Sample the first N available files per task (smoke/test runs). "
                         "Overrides config 'max_files' for every job.")
    ap.add_argument("--rebuild", action="store_true", help="Force rebuild of cached HDF5s.")
    args = ap.parse_args(argv)

    cfg = _load_config(args.config)

    cache_dir = args.cache_dir or cfg.get("cache_dir")
    if not cache_dir:
        print("ERROR: cache_dir is required (config 'cache_dir' or --cache_dir).",
              file=sys.stderr)
        return 2
    eegunity_path = args.eegunity_path or cfg.get("eegunity_path") or None
    num_workers = args.num_workers or int(cfg.get("num_workers") or 8)
    dataset_roots = cfg.get("dataset_roots") or []
    default = cfg.get("default") or {}
    datasets_cfg = cfg.get("datasets") or {}
    jobs = cfg["jobs"]

    log_dir = args.log_dir or cfg.get("log_dir")
    log_path = None
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = str(Path(log_dir) / f"export_{stamp}.log")
    log = _Tee(log_path)

    log(f"=== export_task_h5 | {len(jobs)} job(s) | cache_dir={cache_dir} ===")
    if log_path:
        log(f"=== log file: {log_path} ===")

    results: List[JobResult] = []
    try:
        for i, job in enumerate(jobs, 1):
            dataset = job.get("dataset")
            task = job.get("task")
            log(f"\n[{i}/{len(jobs)}] {dataset} task {task}")
            if not dataset or task is None:
                results.append(JobResult(str(dataset), -1, "failed",
                                         reason="job missing 'dataset' or 'task'"))
                log("    FAILED: job missing 'dataset' or 'task'")
                continue
            try:
                task_int = int(task)
            except (ValueError, TypeError):
                results.append(JobResult(dataset, -1, "failed",
                                         reason=f"task must be an integer index, got {task!r}"))
                log(f"    FAILED: task must be an integer index, got {task!r}")
                continue

            ds_cfg = datasets_cfg.get(dataset) or {}
            params = _resolve_params(default, ds_cfg, job)
            max_files = args.max_files if args.max_files is not None else params.get("max_files")
            res = build_task_hdf5(
                dataset=dataset,
                task=task_int,
                cache_dir=cache_dir,
                params=params,
                eegunity_path=eegunity_path,
                dataset_roots=dataset_roots,
                raw_path=ds_cfg.get("raw_path"),
                num_workers=num_workers,
                rebuild=args.rebuild,
                max_files=max_files,
                log=log,
            )
            results.append(res)

        # ---- Summary table ----
        log("\n" + "=" * 64)
        log("SUMMARY")
        log("=" * 64)
        counts = {"success": 0, "cached": 0, "skipped": 0, "failed": 0}
        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
            tag = {"success": "OK ", "cached": "HIT", "skipped": "SKIP", "failed": "FAIL"}[r.status]
            extra = f"n={r.n_epochs}" if r.n_epochs is not None else r.reason
            log(f"  [{tag}] {r.dataset} task {r.task}  {extra}")
        log("-" * 64)
        log(f"  success={counts['success']} cached={counts['cached']} "
            f"skipped={counts['skipped']} failed={counts['failed']}")
    finally:
        log.close()

    return 0 if (counts["skipped"] == 0 and counts["failed"] == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
