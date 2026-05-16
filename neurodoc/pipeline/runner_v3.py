"""v3 5-phase pipeline orchestrator.

Phases:
  1. Locate    — pipeline.locator.build_locator_report()
  2. Probe     — pipeline.scan_bridge.run_probe() (sampled scan)
  3. Refs      — pipeline.ref_analyzer.analyze_references()
  4. Synth v3  — pipeline.task_synthesizer_v3.synthesize_tasks_v3()
  5. Build+Doc — kernel build → full scan → analysis.md

Workspace mode:
  When `workspace_dir` is provided, all artefacts (locator.json, probe.json,
  kernel.py, analysis.md) land in `<workspace_dir>/<dataset>/`. The kernel is
  installed there *only* — production paths under neurodoc/kernels/ and
  dataset_document/ are not touched.
"""
from __future__ import annotations

import json
import queue
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .budget import Budget, BudgetExhausted
from .context_builder import build_context
from .doc_writer import generate_analysis_md, merge_and_write
from .kernel_builder import build_kernel
from .locator import build_locator_report
from .ref_analyzer import analyze_references
from .scan_bridge import run_probe, run_scan
from .task_synthesizer_v3 import synthesize_tasks_v3

try:
    from ..llm_adapter import extract_text_from_response, post_llm_json, resolve_llm_config
except (ImportError, ValueError):
    from llm_adapter import extract_text_from_response, post_llm_json, resolve_llm_config

try:
    from ..paths import KERNELS_DIR, NEURODOC_DIR, SANDBOX_DIR
except ImportError:
    from paths import KERNELS_DIR, NEURODOC_DIR, SANDBOX_DIR


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _make_log(log_queue: Optional[queue.Queue], stdout_fallback: bool = True) -> Callable[[str], None]:
    if log_queue is not None:
        def _log(msg: str) -> None:
            log_queue.put(msg)
        return _log
    if stdout_fallback:
        def _log(msg: str) -> None:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg}", flush=True)
        return _log
    return lambda msg: None


def _make_call_llm(llm_config: Dict[str, Any], log: Callable, pause_event: Optional[threading.Event]):
    """Construct a closure that sends a chat to the configured LLM with retry."""
    import time

    def _call(messages: List[Dict], timeout: int = 240) -> str:
        if pause_event is not None and pause_event.is_set():
            raise RuntimeError("Paused by user.")
        if not llm_config.get("active_url"):
            raise ValueError("LLM URL not configured.")
        last_exc = None
        for attempt in range(3):
            if attempt > 0:
                delay = 2 ** attempt
                log(f"[LLM] retry {attempt}/2 after {delay}s (prev: {last_exc})")
                time.sleep(delay)
            try:
                data = post_llm_json(llm_config, messages, timeout=timeout)
                return extract_text_from_response(data, llm_config["provider"])
            except Exception as e:
                last_exc = e
                status = getattr(getattr(e, "response", None), "status_code", None)
                if status is not None and status < 500:
                    raise
        raise last_exc

    return _call


def _resolve_dataset_root(dataset_name: str, dataset_roots: List[str]) -> str:
    raw_name = dataset_name
    for prefix in ("openneuro_", "bcic_", "kaggle_", "physionet_", "mendeley_", "figshare_", "sleepdata_"):
        if dataset_name.startswith(prefix):
            raw_name = dataset_name[len(prefix):]
            break
    for root in dataset_roots:
        for cand in (Path(root) / raw_name, Path(root) / dataset_name):
            if cand.is_dir():
                return str(cand)
    return ""


def _drop_df(d: Dict[str, Any]) -> Dict[str, Any]:
    """Strip pandas DataFrame from a result dict (not JSON-serialisable)."""
    return {k: v for k, v in d.items() if k != "df"}


# -----------------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------------

def run_v3(
    dataset_name: str,
    config: Dict[str, Any],
    log_queue: Optional[queue.Queue] = None,
    pause_event: Optional[threading.Event] = None,
    workspace_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run the v3 5-phase pipeline. Returns a status dict.

    config keys consumed:
      - python_env, eegunity_path, dataset_roots, num_workers, budget
      - llm settings (forwarded to resolve_llm_config)
    """
    log = _make_log(log_queue)
    budget = Budget(total=config.get("budget", 500))
    llm_config = resolve_llm_config(config)
    call_llm = _make_call_llm(llm_config, log, pause_event)

    eegunity_path = config.get("eegunity_path", "")
    dataset_roots = config.get("dataset_roots", [])
    num_workers = int(config.get("num_workers", 2))

    workspace_dir = Path(workspace_dir) if workspace_dir else None
    if workspace_dir is not None:
        ws = workspace_dir / dataset_name
        ws.mkdir(parents=True, exist_ok=True)

    status: Dict[str, Any] = {"dataset": dataset_name, "started_at": datetime.now(timezone.utc).isoformat()}

    try:
        # ── Phase 1: Locate ────────────────────────────────────────────────
        ds_root = _resolve_dataset_root(dataset_name, dataset_roots)
        if not ds_root:
            raise FileNotFoundError(f"No dataset root found for {dataset_name} in {dataset_roots}")
        log(f"[v3.Locate] dataset_root={ds_root}")
        locator_obj = build_locator_report(
            dataset_name, ds_root,
            workspace=workspace_dir, use_cache=True,
        )
        locator = locator_obj.to_dict()
        log(
            f"[v3.Locate] format={locator['format']} | raws={locator_obj.total_raw_files()} | "
            f"groups={[(g['key'], g['n_files']) for g in locator['groups']]} | "
            f"annot={len(locator['annotation_files'])}"
        )

        # ── Phase 2: Probe (sampled scan) ─────────────────────────────────
        log("[v3.Probe] sampling per-group...")
        probe_result = run_probe(
            dataset_name=dataset_name,
            locator=_LocatorAdapter(locator_obj),
            dataset_roots=dataset_roots,
            eegunity_path=eegunity_path,
            num_workers=num_workers,
            log=log,
            per_group=int(config.get("probe_per_group", 5)),
        )
        probe_serialisable = _drop_df(probe_result)
        if workspace_dir is not None:
            (workspace_dir / dataset_name / "probe.json").write_text(
                json.dumps(probe_serialisable, indent=2, default=str), encoding="utf-8"
            )
        log(
            f"[v3.Probe] sampled_n={probe_result.get('sampled_n')} | "
            f"events={len(probe_result.get('event_counts') or {})} | "
            f"misc_native={probe_result.get('misc_channel_names') or []}"
        )

        # ── Phase 3: Refs ──────────────────────────────────────────────────
        # Reuse build_context for refs/skill/rulebook/example_kernels
        try:
            context = build_context(dataset_name, log, data_dir=ds_root)
        except FileNotFoundError as e:
            # The dataset_document/<name>/ directory is required for refs.
            # If missing in workspace mode, fall back to a synthetic minimal context.
            log(f"[v3.Refs] build_context failed: {e}. Falling back to minimal context.")
            context = {
                "dataset_name": dataset_name,
                "ds_dir": ds_root,
                "analysis_md": "",
                "ds_tree": locator["tree_summary"],
                "ref_files": [],
                "existing_kernel": "",
                "existing_kernel_path": "",
                "rulebook": "",
                "skill_texts": {},
                "example_kernels": {},
                "app_rulebook": "",
                "category": "",
                "category_skill": "",
                "data_dir": ds_root,
                "format_type": locator["format"],
                "bids_sidecars": locator.get("sidecars") or {},
                "eeg_header_summary": "",
            }

        log(f"[v3.Refs] {len(context['ref_files'])} reference(s) on disk")
        ref_extractions: List[Dict[str, Any]] = []
        if context["ref_files"]:
            try:
                ref_extractions = analyze_references(
                    dataset_name,
                    context["ref_files"],
                    context["analysis_md"],
                    call_llm,
                    budget,
                    log,
                )
            except BudgetExhausted:
                log("[v3.Refs] Budget exhausted; proceeding with empty ref extractions.")

        # ── Phase 4: Synth v3 ──────────────────────────────────────────────
        log("[v3.Synth] catalog-grounded task synthesis...")
        tasks_section, kernel_requirements = synthesize_tasks_v3(
            dataset_name=dataset_name,
            analysis_md=context["analysis_md"],
            ref_extractions=ref_extractions,
            locator_report=locator,
            probe_report=probe_serialisable,
            category_skill=context.get("category_skill", ""),
            call_llm=call_llm,
            budget=budget,
            log=log,
            bids_sidecars=context.get("bids_sidecars"),
            format_type=context.get("format_type", "unknown"),
            eeg_header_summary=context.get("eeg_header_summary", ""),
            event_annotations=None,    # v3 grounds on probe.event_counts directly
        )
        if workspace_dir is not None:
            (workspace_dir / dataset_name / "kernel_requirements.json").write_text(
                json.dumps(kernel_requirements, indent=2, default=str), encoding="utf-8"
            )

        # ── Phase 5: Build + Doc ───────────────────────────────────────────
        sandbox_dir = SANDBOX_DIR / f"v3_{dataset_name}"
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        log(f"[v3.Build] sandbox={sandbox_dir}")
        kernel_code, final_kernel_path, kernel_ok = build_kernel(
            dataset_name=dataset_name,
            context=context,
            tasks_section=tasks_section,
            call_llm=call_llm,
            budget=budget,
            log=log,
            sandbox_dir=sandbox_dir,
            python_env=config.get("python_env", "python3"),
            eegunity_path=eegunity_path,
            dataset_path=ds_root,
            kernel_requirements=kernel_requirements,
            probe_report=probe_serialisable,
            locator_report=locator,
            max_versions=int(config.get("max_versions", 2)),
        )
        log(f"[v3.Build] kernel_ok={kernel_ok}")

        # Install — workspace mode writes to workspace; production install only when no workspace.
        if workspace_dir is not None:
            installed_path = workspace_dir / dataset_name / "kernel.py"
            installed_path.write_text(kernel_code or "# empty — generation failed", encoding="utf-8")
        else:
            installed_path = KERNELS_DIR / f"{dataset_name}.py"
            installed_path.write_text(kernel_code or "# empty", encoding="utf-8")
        log(f"[v3.Install] kernel installed: {installed_path}")

        # Final scan with the installed kernel
        try:
            scan_result = run_scan(
                dataset_name=dataset_name,
                kernel_path=str(installed_path),
                dataset_roots=dataset_roots,
                eegunity_path=eegunity_path,
                num_workers=num_workers,
                log=log,
            )
        except Exception as e:
            log(f"[v3.Scan] full scan failed: {e}; using probe as scan_result fallback.")
            scan_result = probe_result.copy()
            scan_result["scan_type"] = "probe-fallback"

        # Write doc
        analysis_status = "wait_manual_review" if kernel_ok else "wait_kernel_update"
        analysis_md_new = generate_analysis_md(
            dataset_name=dataset_name,
            context=context,
            scan_result=scan_result,
            tasks_section=tasks_section,
            kernel_path=str(installed_path),
            call_llm=call_llm,
            budget=budget,
            log=log,
            bids_sidecars=context.get("bids_sidecars"),
            event_annotations=None,
            status=analysis_status,
        )
        if workspace_dir is not None:
            (workspace_dir / dataset_name / "analysis.md").write_text(analysis_md_new, encoding="utf-8")
        else:
            merge_and_write(dataset_name, analysis_md_new, scan_result, log,
                            bids_sidecars=context.get("bids_sidecars"))

        status.update({
            "ok": True,
            "kernel_ok": kernel_ok,
            "kernel_path": str(installed_path),
            "tasks_n": tasks_section.count("### "),
            "events_n": len(scan_result.get("event_counts") or {}),
            "misc_n": len(probe_result.get("misc_channel_names") or []),
            "budget_used": budget.used,
            "ended_at": datetime.now(timezone.utc).isoformat(),
        })
        log(f"[v3] DONE {dataset_name} | kernel_ok={kernel_ok} | events={status['events_n']}")
        return status

    except Exception as exc:
        log(f"[v3] ERROR {dataset_name}: {exc}")
        log(traceback.format_exc())
        status.update({
            "ok": False,
            "error": str(exc),
            "ended_at": datetime.now(timezone.utc).isoformat(),
        })
        return status


# -----------------------------------------------------------------------------
# Locator → scan_engine adapter
# -----------------------------------------------------------------------------

class _LocatorAdapter:
    """Adapt our LocatorReport to the duck-type expected by scan_engine.run_full_scan
    (specifically: `.raw_files: dict[ext -> list[entry-with-rel_path-and-group_key]]`
    and `.groups`)."""

    def __init__(self, report):
        self._report = report

    @property
    def raw_files(self):
        return self._report.raw_files

    @property
    def groups(self):
        return self._report.groups

    @property
    def root(self):
        return self._report.root

    @property
    def annotation_files(self):
        return self._report.annotation_files
