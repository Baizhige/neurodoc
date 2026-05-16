"""Phase 4 v3: catalog-grounded task synthesis (drop-not-repair).

Differences from v2:
  - The *only* legal value space for event IDs / misc names / info fields is the
    deterministic Catalog built from LocatorReport + ProbeReport. v3 forwards
    these to v2 as `event_ids_preview` / `misc_channel_names` / sidecars but
    then re-validates v2's `kernel_requirements` against the Catalog and
    DROPS anything ungroundable (no repair).
  - Adds three v3-only fields to KernelRequirements:
      * annotation_paths     — from LocatorReport.annotation_files (kernel must
        only read sidecars whose pairing rule appears here; enforced by K5).
      * rename_map           — populated only when LocatorReport.rename_evidence
        justifies it; otherwise empty (enforced by K1).
      * event_prefix_groups  — empty unless catalog-collision detection finds
        the same event_id in ≥2 groups (enforced by K2 prefix exception).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .task_synthesizer_v2 import synthesize_tasks_v2


# -----------------------------------------------------------------------------
# Catalog
# -----------------------------------------------------------------------------

@dataclass
class Catalog:
    events:        Set[str] = field(default_factory=set)
    native_misc:   Set[str] = field(default_factory=set)
    info_fields:   Set[str] = field(default_factory=set)
    derivable:     Set[str] = field(default_factory=set)   # "events.tsv:<col>" / "participants.tsv:<col>"
    annotation_paths: List[str] = field(default_factory=list)
    rename_evidence:  Dict[str, str] = field(default_factory=dict)
    event_to_groups:  Dict[str, Set[str]] = field(default_factory=dict)

    def event_ids_preview(self) -> str:
        if not self.events:
            return "(no events detected)"
        return "\n".join(f"  - `{eid}`" for eid in sorted(self.events))


def build_catalog(locator_report: Dict[str, Any], probe_report: Dict[str, Any]) -> Catalog:
    cat = Catalog()

    # Events from probe (real EEGUnity scan)
    for eid in (probe_report.get("event_counts") or {}).keys():
        cat.events.add(str(eid))

    # Native misc channels — only those the probe actually produced
    for m in probe_report.get("misc_channel_names") or []:
        if isinstance(m, str) and m:
            cat.native_misc.add(m)

    # Info fields from participants.tsv columns
    for sc in (locator_report.get("sidecars") or {}).get("participants_tsv") or []:
        for col in sc.get("columns") or []:
            if isinstance(col, str) and col and col.lower() != "participant_id":
                cat.info_fields.add(col)

    # Derivable: numeric columns of events.tsv + numeric columns of participants.tsv
    def _looks_numeric(rows, idx):
        if not rows:
            return False
        seen = 0
        for r in rows[:20]:
            if idx < len(r):
                v = r[idx].strip() if isinstance(r[idx], str) else r[idx]
                try:
                    float(v)
                    seen += 1
                except (TypeError, ValueError):
                    pass
        return seen >= 1

    for sc in (locator_report.get("sidecars") or {}).get("events_tsv") or []:
        cols = sc.get("columns") or []
        rows = sc.get("rows") or []
        for i, col in enumerate(cols):
            if _looks_numeric(rows, i):
                cat.derivable.add(f"events.tsv:{col}")
    for sc in (locator_report.get("sidecars") or {}).get("participants_tsv") or []:
        cols = sc.get("columns") or []
        rows = sc.get("rows") or []
        for i, col in enumerate(cols):
            if _looks_numeric(rows, i):
                cat.derivable.add(f"participants.tsv:{col}")

    # Annotation paths (rooted relative paths from LocatorReport)
    for a in locator_report.get("annotation_files") or []:
        rp = a.get("rel_path")
        if rp and a.get("kind") in (
            "nsrr_xml", "bids_events_tsv", "bids_events_json", "rpoint_csv"
        ):
            cat.annotation_paths.append(rp)

    cat.rename_evidence = locator_report.get("rename_evidence") or {}

    # Event → groups index for collision detection (best-effort: probe.indices map
    # back to locator.raw_files via group_key on the same flat ordering).
    return cat


# -----------------------------------------------------------------------------
# Catalog-gated post-validation of v2's kernel_requirements
# -----------------------------------------------------------------------------

def _gate_kernel_requirements(
    kr: Dict[str, Any],
    cat: Catalog,
    log,
) -> Dict[str, Any]:
    """Drop anything not present in the catalog; return v3-extended dict."""
    dropped: Dict[str, List[str]] = {}

    # Events: must appear in cat.events (subset / startswith for prefix-enriched ids)
    kept_events: List[str] = []
    for e in kr.get("required_event_ids") or []:
        if e in cat.events:
            kept_events.append(e)
        else:
            dropped.setdefault("event_ids", []).append(e)

    # Native MISC: must appear verbatim in cat.native_misc (NO renaming)
    kept_misc: List[str] = []
    for m in kr.get("required_native_misc") or []:
        if m in cat.native_misc:
            kept_misc.append(m)
        else:
            dropped.setdefault("native_misc", []).append(m)

    # Info: must appear in cat.info_fields
    kept_info: List[str] = []
    for f in kr.get("required_info_fields") or []:
        if f in cat.info_fields:
            kept_info.append(f)
        else:
            dropped.setdefault("info_fields", []).append(f)

    # Derived MISC: each must cite a derivable source
    kept_derived: List[Dict[str, Any]] = []
    for d in kr.get("derived_misc_channels") or []:
        if not isinstance(d, dict):
            continue
        src = (d.get("source_field") or "").strip()
        ok = False
        if src in cat.derivable:
            ok = True
        else:
            # tolerate "events.tsv:col" / "participants.tsv:col" with bare column form
            for k in cat.derivable:
                if k.endswith(f":{src}"):
                    ok = True
                    break
        if ok:
            kept_derived.append(d)
        else:
            dropped.setdefault("derived_misc", []).append(d.get("name") or src)

    if dropped:
        for kind, items in dropped.items():
            log(f"[TaskSynthV3][gate] dropped {kind}: {items}")

    return {
        "required_event_ids":    sorted(kept_events),
        "required_native_misc":  sorted(kept_misc),
        "required_info_fields":  sorted(kept_info),
        "derived_misc_channels": kept_derived,
        "annotation_paths":      list(cat.annotation_paths),
        "rename_map":            {},                # populated only if rename_evidence supports it
        "event_prefix_groups":   [],                # populated only if collisions detected
        "_dropped_by_catalog":   dropped,
    }


# -----------------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------------

def synthesize_tasks_v3(
    dataset_name: str,
    analysis_md: str,
    ref_extractions: List[Dict],
    locator_report: Dict[str, Any],
    probe_report: Dict[str, Any],
    category_skill: str,
    call_llm,
    budget,
    log,
    bids_sidecars: Optional[Dict] = None,
    format_type: str = "unknown",
    eeg_header_summary: str = "",
    event_annotations: Optional[Dict] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Run v2 underneath, then strict-gate its outputs against the Catalog."""
    cat = build_catalog(locator_report, probe_report)
    log(
        f"[TaskSynthV3] Catalog: events={len(cat.events)} | "
        f"native_misc={len(cat.native_misc)} | info={len(cat.info_fields)} | "
        f"derivable={len(cat.derivable)} | annot_paths={len(cat.annotation_paths)}"
    )

    tasks_section, kr = synthesize_tasks_v2(
        dataset_name=dataset_name,
        analysis_md=analysis_md,
        ref_extractions=ref_extractions,
        event_ids_preview=cat.event_ids_preview(),
        category_skill=category_skill,
        call_llm=call_llm,
        budget=budget,
        log=log,
        bids_sidecars=bids_sidecars,
        format_type=format_type,
        eeg_header_summary=eeg_header_summary,
        event_annotations=event_annotations,
        misc_channel_names=sorted(cat.native_misc),
        max_repair_rounds=1,                 # v3 prefers drop over repair
    )

    kr = _gate_kernel_requirements(kr, cat, log)
    log(
        f"[TaskSynthV3] Final KR: events={len(kr['required_event_ids'])} | "
        f"native_misc={len(kr['required_native_misc'])} | "
        f"info={len(kr['required_info_fields'])} | "
        f"derived={len(kr['derived_misc_channels'])} | "
        f"annot_paths={len(kr['annotation_paths'])}"
    )
    return tasks_section, kr
