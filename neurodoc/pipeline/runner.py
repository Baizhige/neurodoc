"""Main pipeline orchestrator for NeuroDoc."""
from __future__ import annotations

import json
import queue
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .budget import Budget, BudgetExhausted
from .context_builder import build_context
from .doc_writer import generate_analysis_md, merge_and_write, write_failed_analysis
from .event_annotator import annotate_events
from .kernel_builder import build_kernel, install_kernel, patch_kernel_for_events
try:
    from ..llm_adapter import extract_text_from_response, post_llm_json, resolve_llm_config
except (ImportError, ValueError):
    from llm_adapter import extract_text_from_response, post_llm_json, resolve_llm_config
from .ref_analyzer import analyze_references
from .reconcile import reconcile as reconcile_tasks
from .scan_bridge import get_event_ids_preview, run_scan
from .task_synthesizer import judge_feasibility
from .task_synthesizer_v2 import synthesize_tasks_v2
try:
    from ..paths import EVIDENCE_CACHE_DIR, KERNELS_DIR, NEURODOC_DIR, PROGRESS_DIR, SANDBOX_DIR
except ImportError:
    from paths import EVIDENCE_CACHE_DIR, KERNELS_DIR, NEURODOC_DIR, PROGRESS_DIR, SANDBOX_DIR

# Phase order for resume logic.
# Grouped into three high-level phases (see README.md § Generation Pipeline):
#   Phase 1 (Build Context): context, ref_analysis, pre_scan, event_annotation
#   Phase 2 (Task Synthesis): feasibility, task_synthesis
#   Phase 3 (Kernel Coding): kernel_loop, scan, reconcile, doc_write
PHASES = [
    # ── Phase 1: Build Context ─────────────────────────────────────────────
    "context",           # local evidence: dataset files, BIDS sidecars, EEG header
    "ref_analysis",      # academic sources: extract info from papers/docs
    "pre_scan",          # local evidence: initial scan for event ID preview
    "event_annotation",  # local evidence: LLM annotates semantic meaning of event IDs
    # ── Phase 2: Task Synthesis ────────────────────────────────────────────
    "feasibility",       # entry check: LLM judges dataset feasibility
    "task_synthesis",    # propose task candidates + list kernel requirements
    # ── Phase 3: Kernel Coding ─────────────────────────────────────────────
    "kernel_loop",       # coding loop: generate kernel.py + sandbox validation
    "scan",              # final EEGUnity scan with new kernel
    "reconcile",         # reconcile synthesized tasks against scan results
    "doc_write",         # write final analysis.md
    "done",
]


class PauseSignal(Exception):
    pass


def _progress_path(dataset_name: str) -> Path:
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    return PROGRESS_DIR / f"{dataset_name}.json"


def load_progress(dataset_name: str) -> Dict[str, Any]:
    p = _progress_path(dataset_name)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"phase": "context", "budget_used": 0, "budget_breakdown": {}}


def save_progress(dataset_name: str, data: Dict[str, Any]) -> None:
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    _progress_path(dataset_name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def clear_progress(dataset_name: str) -> None:
    p = _progress_path(dataset_name)
    if p.exists():
        p.unlink()


class Pipeline:
    def __init__(
        self,
        dataset_name: str,
        config: Dict[str, Any],
        log_queue: "queue.Queue[Optional[str]]",
        pause_event: threading.Event,
        fresh_start: bool = False,
    ):
        self.dataset_name = dataset_name
        self.config = config
        self.log_queue = log_queue
        self.pause_event = pause_event

        self.budget = Budget(total=config.get("budget", 500))
        self.progress = {} if fresh_start else load_progress(dataset_name)
        if fresh_start:
            self.progress = {"phase": "context"}
        # Restore budget state
        self.budget.load_dict({
            "total": self.budget.total,
            "used": self.progress.get("budget_used", 0),
            "breakdown": self.progress.get("budget_breakdown", {}),
        })

        self._python_env = config.get("python_env", "python3")
        self._eegunity_path = config.get("eegunity_path", "")
        self._dataset_roots = config.get("dataset_roots", [])
        self._num_workers = int(config.get("num_workers", 2))

        self._llm_config = resolve_llm_config(config)

    # ── logging ────────────────────────────────────────────────────────────

    def log(self, msg: str) -> None:
        self.log_queue.put(msg)

    def _check_pause(self) -> None:
        if self.pause_event.is_set():
            raise PauseSignal("Paused by user.")

    # ── LLM call ───────────────────────────────────────────────────────────

    def call_llm(self, messages: List[Dict], timeout: int = 240) -> str:
        import time
        self._check_pause()
        if not self._llm_config.get("active_url"):
            raise ValueError("LLM URL not configured in neurodoc settings.")

        last_exc = None
        for attempt in range(3):
            if attempt > 0:
                delay = 2 ** attempt  # 2s, 4s
                self.log(f"[LLM] Retry {attempt}/2 after {delay}s (prev: {last_exc})")
                time.sleep(delay)
            try:
                data = post_llm_json(self._llm_config, messages, timeout=timeout)
                return extract_text_from_response(data, self._llm_config["provider"])
            except Exception as e:
                last_exc = e
                # Only retry on server errors (5xx) or connection issues
                status = getattr(getattr(e, "response", None), "status_code", None)
                if status is not None and status < 500:
                    raise  # 4xx — don't retry
        raise last_exc

    # ── progress helpers ───────────────────────────────────────────────────

    def _phase_index(self, phase: str) -> int:
        try:
            return PHASES.index(phase)
        except ValueError:
            return 0

    def _current_phase_index(self) -> int:
        return self._phase_index(self.progress.get("phase", "context"))

    def _save(self, phase: str, **extra) -> None:
        self.progress.update(extra)
        self.progress["phase"] = phase
        self.progress["budget_used"] = self.budget.used
        self.progress["budget_breakdown"] = self.budget.breakdown
        save_progress(self.dataset_name, self.progress)

    # ── main run ───────────────────────────────────────────────────────────

    def run(self) -> None:
        self.log(f"[Pipeline] Starting: {self.dataset_name} | budget: {self.budget.remaining()} remaining")
        cur = self._current_phase_index()

        try:
            # ── Phase 1: Context ────────────────────────────────────────
            # Always rebuild context (fast: just reads local files; not stored in
            # progress JSON because it contains Path objects + large strings).
            self._check_pause()
            data_dir = self._find_data_dir()
            if data_dir:
                self.log(f"[Pipeline] Raw data dir: {data_dir}")
            else:
                self.log("[Pipeline] Raw data dir not found — BIDS sidecar reading skipped")
            context = build_context(self.dataset_name, self.log, data_dir=data_dir)
            if cur <= self._phase_index("context"):
                self._save("ref_analysis", context_summary={
                    "has_kernel": bool(context["existing_kernel"]),
                    "ref_count": len(context["ref_files"]),
                    "category": context["category"],
                    "format_type": context.get("format_type", "unknown"),
                    "has_bids_sidecars": bool(context.get("bids_sidecars")),
                })
            else:
                self.log("[Pipeline] Resuming: context rebuilt from disk")

            self._check_pause()

            # ── Phase 2: Reference Analysis ─────────────────────────────
            if cur <= self._phase_index("ref_analysis"):
                ref_extractions = analyze_references(
                    self.dataset_name,
                    context["ref_files"],
                    context["analysis_md"],
                    self.call_llm,
                    self.budget,
                    self.log,
                )
                self._save("feasibility", ref_extractions=ref_extractions)
            else:
                self.log("[Pipeline] Resuming: skipping ref_analysis")
                ref_extractions = self.progress.get("ref_extractions", [])

            self._check_pause()

            # ── Phase 3: Feasibility ────────────────────────────────────
            if cur <= self._phase_index("feasibility"):
                feasible, reason = judge_feasibility(
                    self.dataset_name,
                    context["analysis_md"],
                    ref_extractions,
                    self.call_llm,
                    self.budget,
                    self.log,
                    bids_sidecars=context.get("bids_sidecars"),
                )
                self._save("pre_scan", feasible=feasible, feasibility_reason=reason)
                if not feasible:
                    self.log(f"[Pipeline] Not feasible: {reason}")
                    write_failed_analysis(
                        self.dataset_name,
                        context["analysis_md"],
                        reason,
                        self.log,
                    )
                    self._save("done", status="failed")
                    self.log_queue.put(None)
                    return
            else:
                self.log("[Pipeline] Resuming: skipping feasibility")
                feasible = self.progress.get("feasible", True)
                reason = self.progress.get("feasibility_reason", "")

            self._check_pause()

            # ── Phase 3.5: Pre-scan (get event IDs for task synthesis) ──
            pre_scan_result = self.progress.get("pre_scan_result")
            if cur <= self._phase_index("pre_scan") or not pre_scan_result:
                self.log("[Pipeline] Running pre-scan to get event IDs...")
                # Use existing kernel if available, else default parser
                existing_kernel_path = context.get("existing_kernel_path", "")
                try:
                    pre_scan_result = run_scan(
                        self.dataset_name,
                        existing_kernel_path,
                        self._dataset_roots,
                        self._eegunity_path,
                        self._num_workers,
                        self.log,
                    )
                    # Don't store full df in progress (too large)
                    pre_scan_for_progress = {k: v for k, v in pre_scan_result.items() if k != "df"}
                    self._save("task_synthesis", pre_scan_result=pre_scan_for_progress)
                except Exception as e:
                    self.log(f"[Pipeline] Pre-scan failed: {e}. Will use analysis.md event list instead.")
                    pre_scan_result = {"event_counts": {}, "misc_channel_names": []}
                    self._save("task_synthesis", pre_scan_result=pre_scan_result)
            else:
                self.log("[Pipeline] Resuming: skipping pre_scan")

            event_ids_preview = get_event_ids_preview(pre_scan_result)
            self._check_pause()

            # ── Phase 3b: Event Annotation (ISOLATED — P3a+P3b) ─────────
            if cur <= self._phase_index("event_annotation"):
                event_annotations = annotate_events(
                    self.dataset_name,
                    event_ids_preview,
                    data_dir,
                    context.get("bids_sidecars", {}),
                    self.call_llm,
                    self.budget,
                    self.log,
                    evidence_cache_dir=str(EVIDENCE_CACHE_DIR),
                )
                self._save("task_synthesis", event_annotations=event_annotations)
            else:
                self.log("[Pipeline] Resuming: skipping event_annotation")
                event_annotations = self.progress.get("event_annotations", {})

            self._check_pause()

            # ── Phase 4: Task Synthesis (v2 — aggregate+fill+gate+repair) ─
            if cur <= self._phase_index("task_synthesis"):
                tasks_section, kernel_requirements = synthesize_tasks_v2(
                    self.dataset_name,
                    context["analysis_md"],
                    ref_extractions,
                    event_ids_preview,
                    context["category_skill"],
                    self.call_llm,
                    self.budget,
                    self.log,
                    bids_sidecars=context.get("bids_sidecars"),
                    format_type=context.get("format_type", "unknown"),
                    eeg_header_summary=context.get("eeg_header_summary", ""),
                    event_annotations=event_annotations,
                    misc_channel_names=(pre_scan_result or {}).get("misc_channel_names", []),
                )
                self._save(
                    "kernel_loop",
                    tasks_section=tasks_section,
                    kernel_requirements=kernel_requirements,
                )
            else:
                self.log("[Pipeline] Resuming: skipping task_synthesis")
                tasks_section = self.progress.get("tasks_section", "## Tasks\n\n(pending)")
                kernel_requirements = self.progress.get("kernel_requirements", {})

            self._check_pause()

            # ── Phase 5: Kernel Build Loop ───────────────────────────────
            sandbox_dir = SANDBOX_DIR / self.dataset_name
            if cur <= self._phase_index("kernel_loop"):
                # Find dataset path
                dataset_path = self._find_dataset_path()
                kernel_code, final_kernel_path, kernel_ok = build_kernel(
                    self.dataset_name,
                    context,
                    tasks_section,
                    self.call_llm,
                    self.budget,
                    self.log,
                    sandbox_dir,
                    self._python_env,
                    self._eegunity_path,
                    dataset_path,
                    kernel_requirements=kernel_requirements,
                )
                self._save("scan",
                           kernel_ok=kernel_ok,
                           kernel_path=str(final_kernel_path),
                           kernel_code_len=len(kernel_code))

                if kernel_ok:
                    # Install kernel
                    installed_path = install_kernel(kernel_code, self.dataset_name, self.log)
                    kernel_path_for_scan = str(installed_path)
                else:
                    self.log("[Pipeline] WARNING: Kernel did not fully pass tests. Installing best attempt.")
                    installed_path = install_kernel(kernel_code, self.dataset_name, self.log)
                    kernel_path_for_scan = str(installed_path)
            else:
                self.log("[Pipeline] Resuming: skipping kernel_loop")
                kernel_ok = self.progress.get("kernel_ok", False)
                kernel_path_for_scan = self.progress.get("installed_kernel_path", "")

            self._check_pause()

            # ── Phase 6: Final Scan ──────────────────────────────────────
            if cur <= self._phase_index("scan"):
                scan_result = run_scan(
                    self.dataset_name,
                    kernel_path_for_scan,
                    self._dataset_roots,
                    self._eegunity_path,
                    self._num_workers,
                    self.log,
                )
                # Post-scan safety net (Change #1c): if event_counts is empty AND tasks
                # require event IDs, make ONE more LLM patch attempt before reconcile.
                scan_result = self._maybe_recover_empty_events(
                    scan_result,
                    kernel_requirements or {},
                    kernel_path_for_scan,
                    context,
                )
                # If recovery installed a new kernel, kernel_path_for_scan may have changed
                kernel_path_for_scan = scan_result.pop("_recovered_kernel_path", kernel_path_for_scan)
                scan_for_progress = {k: v for k, v in scan_result.items() if k != "df"}
                self._save("reconcile", scan_result=scan_for_progress,
                           installed_kernel_path=kernel_path_for_scan)
            else:
                self.log("[Pipeline] Resuming: skipping scan")
                scan_result = self.progress.get("scan_result", {})

            self._check_pause()

            # ── Phase 6.5: Reconcile Tasks ↔ Scan ───────────────────────
            if cur <= self._phase_index("reconcile"):
                def _rescan(new_kernel_path: str) -> Dict[str, Any]:
                    res = run_scan(
                        self.dataset_name,
                        new_kernel_path,
                        self._dataset_roots,
                        self._eegunity_path,
                        self._num_workers,
                        self.log,
                    )
                    return res

                def _install(new_code: str) -> str:
                    p = install_kernel(new_code, self.dataset_name, self.log)
                    return str(p)

                tasks_section, scan_result, kernel_code_post, did_patch = reconcile_tasks(
                    tasks_section,
                    scan_result,
                    kernel_requirements or {},
                    self._load_installed_kernel_code(kernel_path_for_scan),
                    self.dataset_name,
                    context.get("bids_sidecars"),
                    self.call_llm,
                    self.budget,
                    self.log,
                    rescan_func=_rescan,
                    install_func=_install,
                    data_dir=self._find_data_dir(),
                )
                if did_patch:
                    # install_kernel writes to neurodoc/kernels/<dataset>.py
                    kernel_path_for_scan = str(
                        KERNELS_DIR / f"{self.dataset_name}.py"
                    )
                scan_for_progress = {k: v for k, v in scan_result.items() if k != "df"}
                self._save(
                    "doc_write",
                    tasks_section=tasks_section,
                    scan_result=scan_for_progress,
                    reconcile_patched=did_patch,
                    installed_kernel_path=kernel_path_for_scan,
                )
            else:
                self.log("[Pipeline] Resuming: skipping reconcile")

            # Re-generate event_ids_preview from final scan
            event_ids_preview = get_event_ids_preview(scan_result)
            self._check_pause()

            # ── Phase 7: Doc Write ───────────────────────────────────────
            if cur <= self._phase_index("doc_write"):
                status = "wait_manual_review"
                analysis_md_new = generate_analysis_md(
                    self.dataset_name,
                    context,
                    scan_result,
                    tasks_section,
                    kernel_path_for_scan,
                    self.call_llm,
                    self.budget,
                    self.log,
                    bids_sidecars=context.get("bids_sidecars"),
                    event_annotations=event_annotations,
                    status=status,
                )
                merge_and_write(self.dataset_name, analysis_md_new, scan_result, self.log,
                               bids_sidecars=context.get("bids_sidecars"))
                self._save("done", status=status)
                self.log(f"[Pipeline] Complete. Status: {status}. Budget used: {self.budget.used}/{self.budget.total}")

        except PauseSignal:
            self._save(self.progress.get("phase", "context"))
            self.log("[Pipeline] Paused. Progress saved. Click Start to resume.")

        except BudgetExhausted as e:
            self.log(f"[Pipeline] {e}")
            self.log("[Pipeline] Budget exhausted. Saving progress for resume.")
            self._save(self.progress.get("phase", "context"), status="budget_exhausted")
            # Try to write whatever we have
            self._write_partial_output(context, scan_result if 'scan_result' in locals() else {}, tasks_section if 'tasks_section' in locals() else "")

        except Exception as e:
            import traceback
            self.log(f"[Pipeline] ERROR: {e}")
            self.log(traceback.format_exc())
            self._save(self.progress.get("phase", "context"), status="error", last_error=str(e))

        finally:
            self.log_queue.put(None)  # sentinel

    def _find_dataset_path(self) -> str:
        import sys as _sys
        if str(NEURODOC_DIR) not in _sys.path:
            _sys.path.insert(0, str(NEURODOC_DIR))
        import scan_engine
        p = scan_engine.find_dataset_path(self.dataset_name, self._dataset_roots)
        return p or ""

    def _load_installed_kernel_code(self, path_hint: str) -> str:
        """Read the kernel source from the installed path (or the fallback canonical location)."""
        candidates = []
        if path_hint:
            candidates.append(Path(path_hint))
        candidates.append(KERNELS_DIR / f"{self.dataset_name}.py")
        for p in candidates:
            try:
                if p.exists():
                    return p.read_text(encoding="utf-8")
            except Exception:
                continue
        return ""

    def _find_data_dir(self) -> str:
        """Find raw data directory without importing scan_engine."""
        ds = self.dataset_name
        # Strip source prefix for raw lookup (e.g., openneuro_ds005505 -> ds005505)
        raw_name = ds
        for prefix in ("openneuro_", "bcic_", "kaggle_", "physionet_", "mendeley_"):
            if ds.startswith(prefix):
                raw_name = ds[len(prefix):]
                break
        for root in self._dataset_roots:
            for candidate in [Path(root) / raw_name, Path(root) / ds]:
                if candidate.is_dir():
                    return str(candidate)
        return ""

    def _maybe_recover_empty_events(
        self,
        scan_result: Dict[str, Any],
        kernel_requirements: Dict[str, Any],
        kernel_path_for_scan: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Post-scan safety net: one-shot LLM patch + rescan when event_counts is empty.

        Fires only when the downstream tasks actually require event IDs; otherwise a
        legitimately silent dataset is left alone. Returns scan_result, augmented with
        `_recovered_kernel_path` (popped by the caller) if a new kernel was installed.
        """
        ev = scan_result.get("event_counts") or {}
        required_ids = kernel_requirements.get("required_event_ids") or []
        if ev or not required_ids:
            return scan_result
        data_dir = self._find_data_dir()
        if not data_dir:
            return scan_result
        ds_dir = Path(data_dir)
        # Reuse the kernel_builder's sample-picker for consistent coverage.
        try:
            from .kernel_builder import _pick_sample_files
            sample_files = _pick_sample_files(ds_dir)
        except Exception:
            sample_files = []
        if not sample_files:
            return scan_result
        self.log(
            f"[Pipeline] event_counts empty post-scan; required_event_ids={required_ids[:5]}"
            f"{'...' if len(required_ids) > 5 else ''} — attempting one kernel patch."
        )
        current_code = self._load_installed_kernel_code(kernel_path_for_scan)
        if not current_code:
            return scan_result
        events_numeric_columns = (context.get("bids_sidecars") or {}).get("events_numeric_columns") or {}
        try:
            patched = patch_kernel_for_events(
                current_code,
                self.dataset_name,
                ds_dir,
                sample_files,
                events_numeric_columns,
                required_ids,
                self.call_llm,
                self.budget,
                self.log,
            )
        except Exception as exc:
            self.log(f"[Pipeline] event recovery patch failed: {exc}")
            return scan_result
        if not patched:
            return scan_result
        # Install + rescan
        installed = install_kernel(patched, self.dataset_name, self.log)
        new_scan = run_scan(
            self.dataset_name,
            str(installed),
            self._dataset_roots,
            self._eegunity_path,
            self._num_workers,
            self.log,
        )
        new_ev = new_scan.get("event_counts") or {}
        if not new_ev:
            self.log("[Pipeline] event recovery: still empty after rescan; proceeding (reconcile will drop event tasks)")
        else:
            self.log(f"[Pipeline] event recovery: rescan now sees {len(new_ev)} event types")
        new_scan["_recovered_kernel_path"] = str(installed)
        return new_scan

    def _write_partial_output(self, context, scan_result, tasks_section):
        """Best-effort partial output when budget is exhausted."""
        try:
            if scan_result and scan_result.get("event_counts"):
                analysis_md_new = generate_analysis_md(
                    self.dataset_name, context, scan_result, tasks_section,
                    self.progress.get("installed_kernel_path", ""),
                    self.call_llm, self.budget, self.log,
                    bids_sidecars=context.get("bids_sidecars"),
                )
                merge_and_write(self.dataset_name, analysis_md_new, scan_result, self.log,
                               bids_sidecars=context.get("bids_sidecars"))
        except Exception as e:
            self.log(f"[Pipeline] Could not write partial output: {e}")
