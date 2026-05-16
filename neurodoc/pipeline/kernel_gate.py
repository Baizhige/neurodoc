"""K1–K6 static kernel-invariant gate.

Runs after the LLM emits a kernel, BEFORE the subprocess test in
kernel_builder.py. Each violation is an error string; the gate returns
the (possibly empty) list of violations.

The point is to fail fast on do-no-harm offences — pollution of channel
names, invented event IDs, ungroundable misc derivations, or sidecar
paths that LocatorReport never proved exist.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _strip_strings_and_comments(code: str) -> str:
    """Best-effort: blank out comments and string literals so regex matchers
    don't false-positive on docstrings. Not a real parser; good enough."""
    # comments
    code = re.sub(r"#.*", "", code)
    # triple-quoted strings
    code = re.sub(r'"""[\s\S]*?"""', '""', code)
    code = re.sub(r"'''[\s\S]*?'''", "''", code)
    # single-quoted strings (greedy enough for our use)
    code = re.sub(r'"([^"\\]|\\.)*"', '""', code)
    code = re.sub(r"'([^'\\]|\\.)*'", "''", code)
    return code


def _extract_string_literals(code: str) -> List[str]:
    out: List[str] = []
    out += re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', code)
    out += re.findall(r"'([^'\\]*(?:\\.[^'\\]*)*)'", code)
    return out


# -----------------------------------------------------------------------------
# Per-rule checks
# -----------------------------------------------------------------------------

def _check_k1_preserve_channels(
    code: str,
    rename_map: Dict[str, str],
    required_native_misc: List[str],
) -> List[str]:
    """K1 — preserve channel names that downstream tasks depend on.

    The motivating SHHS incident: kernel rewrote `EOG(L) → EOG-L` and `Heart Rate → HR`,
    silently breaking the static check that compared declared `required_native_misc`
    against post-rename names.

    K1 fires when the kernel calls `rename_channels(...)` AND there are misc channels
    declared in kernel_requirements that could plausibly be renamed (i.e. anything
    non-EEG that downstream tasks ground on). When required_native_misc is empty,
    rename is treated as cosmetic (case normalisation, numeric→10-20 mapping) and
    accepted: those datasets aren't depending on misc channel name preservation.
    """
    stripped = _strip_strings_and_comments(code)
    if "rename_channels" not in stripped:
        return []
    if rename_map:
        return []
    if not required_native_misc:
        # No declared misc dependencies — rename is allowed (typical for motor-imagery
        # datasets where the kernel normalises numeric / case-variant channel names).
        return []
    return [
        "K1: kernel calls rename_channels() while required_native_misc is non-empty "
        f"(declared misc: {required_native_misc}). Rename could break misc declarations; "
        "either remove the rename or add an entry to rename_evidence/rename_map."
    ]


def _check_k2_preserve_events(code: str, event_prefix_groups: List[str]) -> List[str]:
    stripped = _strip_strings_and_comments(code)
    violations: List[str] = []
    if "rename_events" in stripped:
        if not event_prefix_groups:
            violations.append("K2: kernel calls mne.rename_events but event_prefix_groups is empty.")
    if re.search(r"event_id_map\s*=", stripped):
        violations.append("K2: kernel passes event_id_map=... — only pass-through allowed.")
    return violations


def _check_k3_native_misc(code: str, required_native_misc: List[str], probe_misc: Set[str]) -> List[str]:
    bad = [m for m in required_native_misc if m not in probe_misc]
    if bad:
        return [f"K3: required_native_misc not seen by probe: {bad} (probe set: {sorted(probe_misc)})"]
    return []


def _check_k4_derived_misc(derived: List[Dict[str, Any]], sidecar_columns: Set[str]) -> List[str]:
    violations: List[str] = []
    for d in derived or []:
        if not isinstance(d, dict):
            continue
        src = (d.get("source_field") or "").strip()
        ok = src in sidecar_columns
        if not ok:
            for k in sidecar_columns:
                if k.endswith(f":{src}"):
                    ok = True
                    break
        if not ok:
            violations.append(f"K4: derived misc '{d.get('name')}' source_field '{src}' is not in sidecar columns.")
    return violations


def _check_k5_annotation_paths(code: str, annotation_paths: List[str]) -> List[str]:
    """Look for hard-coded sidecar reads in the kernel and verify each appears in
    `annotation_paths` either by exact rel-path suffix match or by pairing-rule
    fragment (e.g. an `annotations-events-nsrr` segment)."""
    if not annotation_paths:
        return []
    fragments: Set[str] = set()
    for p in annotation_paths:
        for seg in p.replace("\\", "/").split("/"):
            if seg and seg not in (".", ".."):
                fragments.add(seg)

    violations: List[str] = []
    for lit in _extract_string_literals(code):
        # Heuristic: a string with one of these suffixes that does NOT share at
        # least one path fragment with a known annotation path is suspicious.
        suspicious_suffix = lit.endswith((".xml", ".tsv", ".json", ".csv", ".evt"))
        if not suspicious_suffix:
            continue
        if "annotations" not in lit.lower() and "events" not in lit.lower() and "nsrr" not in lit.lower():
            continue
        # Allow if any path fragment is shared.
        lit_segs = set(s for s in lit.replace("\\", "/").split("/") if s)
        if lit_segs & fragments:
            continue
        violations.append(f"K5: kernel hard-codes annotation path '{lit}' that does not match LocatorReport.annotation_files.")
    return violations[:5]   # cap for log readability


# -----------------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------------

def check_kernel_invariants(
    kernel_code: str,
    kernel_requirements: Optional[Dict[str, Any]],
    probe_report: Optional[Dict[str, Any]],
    locator_report: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Return a list of human-readable violation strings (empty == clean)."""
    if not kernel_code:
        return []
    kr = kernel_requirements or {}
    pr = probe_report or {}
    loc = locator_report or {}

    rename_map = kr.get("rename_map") or {}
    prefix_groups = kr.get("event_prefix_groups") or []
    required_native_misc = list(kr.get("required_native_misc") or [])
    derived = list(kr.get("derived_misc_channels") or [])
    annotation_paths = list(kr.get("annotation_paths") or [])

    probe_misc: Set[str] = set(pr.get("misc_channel_names") or [])

    # Pull sidecar column tokens (events.tsv:col, participants.tsv:col)
    sidecar_columns: Set[str] = set()
    sc = (loc.get("sidecars") or {})
    for tag, label in (("events_tsv", "events.tsv"), ("participants_tsv", "participants.tsv")):
        for entry in sc.get(tag, []) or []:
            for col in entry.get("columns") or []:
                if isinstance(col, str) and col:
                    sidecar_columns.add(f"{label}:{col}")

    violations: List[str] = []
    violations += _check_k1_preserve_channels(kernel_code, rename_map, required_native_misc)
    violations += _check_k2_preserve_events(kernel_code, prefix_groups)
    violations += _check_k3_native_misc(kernel_code, required_native_misc, probe_misc)
    violations += _check_k4_derived_misc(derived, sidecar_columns)
    violations += _check_k5_annotation_paths(kernel_code, annotation_paths)
    return violations
