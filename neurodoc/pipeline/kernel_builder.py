"""Phase 5: Iterative kernel generation + subprocess testing loop."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple  # noqa: F401

from .budget import BudgetExhausted
from .ref_analyzer import _parse_json
try:
    from ..paths import KERNELS_DIR
except ImportError:
    from paths import KERNELS_DIR


_KERNEL_SYSTEM = """\
You are an EEG kernel engineer. Write a complete Python kernel file for EEGUnity.

Output your response as a Python code block ONLY — no explanation, no JSON:
```python
<full kernel source code here>
```

MANDATORY requirements — violating any will cause rejection:
1. Last line of file: KERNEL = <ClassName>()
   The instantiated class must expose `KERNEL_ID = "<dataset_name>"` as a string
   class or instance attribute; the sandbox reads `kernel.KERNEL_ID`.
2. Method signature MUST be EXACTLY: def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
   — DO NOT split across lines, DO NOT add type annotations to parameters, DO NOT rename udataset/raw/row
3. raw.info["description"] = json.dumps({
       "original_description": <original>,
       "eegunity_description": {"age": str, "sex": str, "amplifier": str, "cap": str, "handedness": str,
                                 <any extra required info fields, verbatim from participants.tsv>}
   })
4. age is always a STRING (e.g. "22", not 22)
5. sex is always lowercase: "male" / "female" / "unknown"
6. Inferred values: add comment  # inferred by LLM, needs human review
7. Channel rename BEFORE set_montage()
   Whenever you call `raw.set_montage(...)`, pass `on_missing="ignore"` unless
   the dataset sidecar proves every channel has a montage position. MAT/custom
   files often contain extended/space-padded names that otherwise fail full_scan.
   If you call `raw.rename_channels(...)`, ensure the resulting names are unique.
   EDF headers sometimes already contain duplicate names; pass `allow_duplicates=True`
   or append a stable suffix yourself when stripping prefixes/whitespace.
8. When `required_info_fields` is non-empty in kernel_requirements, the kernel MUST read
   the listed columns from participants.tsv for the current subject and include them as
   STRING values inside eegunity_description (see above). The downstream epoch writer
   attaches every non-canonical key as a source-level HDF5 attr so InfoDataset can reach it.
   If a column is genuinely missing for a subject, use "unknown" (do NOT fabricate).
   Do NOT put canonical fields (`age`, `sex`, `amplifier`, `cap`, `handedness`) into
   `required_info_fields`; those five keys must always be explicitly present in
   eegunity_description with defaults even when no participants.tsv exists.
9. When `required_native_misc` or `derived_misc_channels` is non-empty, the kernel MUST
   ensure those channel names exist on the returned raw as misc-type channels.
   - Native misc: already a physical channel on the raw; just make sure its ch_type is
     'misc' (use raw.set_channel_types({name: 'misc'}) if the loader mislabelled it).
   - Derived misc: the kernel creates the channel. The derivation mechanism is YOUR CHOICE
     — constant broadcast (one value per file), trial-locked step function from events.tsv,
     RawArray concatenated via raw.add_channels(), or any other MNE-compatible path. The
     ONLY invariants are (a) the exact `name` in raw.ch_names, (b) ch_types[name] == 'misc',
     (c) raw.get_data(picks=[name]) returns shape (1, len(raw.times)) with finite values.
   - If you use raw.add_channels(...) on a raw object read from EDF/GDF/BDF/SET/FIF,
     call raw.load_data() first. For interval labels from sidecars, prefer
     raw.set_annotations(...) instead of misc channels.
   - For derived misc sourced from `events.tsv:<column>`, read the sibling events.tsv for
     the current file and populate the channel samples so that at each annotation onset
     the channel reflects that row's value. Between trials use 0 / NaN / carry-forward —
     your call, as long as the per-trial targets are recoverable at epoch-extraction time.
10. When events.tsv sidecars exist AND the raw file format may not carry its own triggers
   (EEGLAB .set without populated `event`; EDF without annotations; BrainVision .eeg
   without its marker file; plain .fif without events baked in), the kernel MUST derive
   `mne.Annotations` from the sibling events.tsv so `mne.events_from_annotations(raw)`
   yields ≥ the number of non-empty rows in events.tsv. Do NOT remap or rename event
   IDs (HC-5) — pass the literal `value` / `trial_type` column through. The exact
   reading approach (pandas + mne.Annotations, mne.annotations_from_events, etc.) is
   your call; only the outcome matters.
10b. When local EDF/GDF sidecars expose interval annotations (CSV with
    `start_time/stop_time/label`, TSE/LBL token rows, or summary files with
    `Seizure N Start/End Time`), convert those intervals into raw.annotations using
    literal sidecar labels. Deduplicate repeated channel-level rows by
    `(start, stop, label)`. Do NOT create a misc channel for these interval event
    labels unless kernel_requirements explicitly asks for a misc route.
11. HC-5 applies to ALL formats, not only BIDS. For .mat/GDF/EDF/CSV sidecars, preserve
    the literal marker code/annotation/sidecar label as the annotation description. Do
    NOT replace `1`, `769`, `T1`, `gnsz`, etc. with semantic labels such as left/right,
    motor imagery class names, seizure names, or prettier descriptions. Semantic meaning
    belongs in analysis.md, not in kernel event IDs. Prefix enrichment is allowed only
    when the original ID remains visible (e.g. `protocolA::1`).
12. If MNE/EEGUnity cannot natively load the data file format (common for .mat/custom
    arrays), implement a custom `load(...)` method that returns an MNE Raw object and
    set `HANDLES_UNAVAILABLE = True`. Make `load(...)` accept either a file path string
    or a row/Series containing `File Path`.
    Row objects usually use the exact key `File Path` (capital F/P). Use a helper that
    tries `row.get("File Path")` first and converts Path objects to str before calling
    string methods such as `.replace()` or `.split()`.
13. For custom loaders, put parsing/annotation construction in a shared helper and call
    that helper from BOTH `load(...)` and `apply(...)`. Real EEGUnity scans may call
    `apply(...)` on a partially loaded raw object without invoking `load(...)`; if the
    incoming raw lacks annotations/misc channels that your helper can reconstruct from
    `row["File Path"]`, `apply(...)` must rebuild or add them. A kernel whose sample
    files are all skipped by the sandbox test is invalid.
14. In mixed-format releases, prioritize the standard raw recordings selected for the
    sandbox test. Do not synthesize annotations from MAT/CSV label sidecars unless the
    final kernel_requirements explicitly asks for that sidecar-derived label field.
"""

_KERNEL_FIX_SYSTEM = """\
You are an EEG kernel engineer fixing a broken Python kernel for EEGUnity.
Fix ONLY what is broken. Output your fix as a Python code block ONLY:
```python
<full corrected kernel source code here>
```

MANDATORY — any violation will fail validation again:
- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  — exact signature, one line, no type hints on params
- The kernel class must define `KERNEL_ID = "<dataset_name>"` as a string class
  or instance attribute; the test harness reads `kernel.KERNEL_ID`.
- Inside apply(), one literal statement:
    raw.info["description"] = json.dumps({
        "original_description": <original>,
        "eegunity_description": { ... populated ... },
    })
  Do NOT use `raw.info["description"] = {}` / `.update(...)` / dict assignment —
  MNE stores description as a STRING, not a dict.
- When the error lists `required_info_fields`, read each one from participants.tsv
  for the current subject and put it (as str) into eegunity_description.
- Always initialize eegunity_description with explicit default keys:
  `age`, `sex`, `amplifier`, `cap`, `handedness`. Then add extra participants.tsv
  columns if required. Never rely on looping over `required_info_fields` to create
  those five canonical keys.
- When the error lists `derived_misc_channels`, create each one as an MNE misc-type
  channel on the returned raw. Derivation mechanism is YOUR choice — constant broadcast
  is fine for participants.tsv sources; events.tsv-sourced columns often warrant a
  trial-locked step function. Only invariants: exact `name` in raw.ch_names, ch_type
  'misc', and finite data of shape (1, len(raw.times)). If you use raw.add_channels(...),
  call raw.load_data() first unless you created the RawArray yourself.
- If the failure was annotations/event-count related, fix the event-reading path:
  decide whether the raw file carries its own triggers, whether events.tsv must be
  parsed, whether an EDF clinical CSV/TSE/LBL/summary sidecar must be parsed, or whether
  a STIM channel is available. HC-5 forbids remapping event IDs — pass the literal
  local labels through to raw.annotations.
- If a custom `load(...)` produced annotations but full_scan still saw zero events,
  move the same annotation-building logic into `apply(...)` as well. EEGUnity may pass
  `apply(...)` a raw object that has channels but no annotations; use `row["File Path"]`
  to rebuild/add the literal raw event IDs.
- If using `set_montage(...)`, add `on_missing="ignore"` and strip/normalize channel
  name whitespace before montage assignment.
- If using `raw.rename_channels(...)`, avoid duplicate-name failures: either pass
  `allow_duplicates=True` or make the target names unique before renaming.
- If the traceback mentions `row['file_path']`, `Path.replace`, or `PosixPath.split`,
  fix path handling: prefer `row.get("File Path")`, convert to `str`, then use string
  operations.
- HC-5 applies to every source: .mat marker codes, GDF annotation strings, EDF labels,
  and CSV sidecar labels must stay literal. Put semantic interpretation in the document
  Meaning field, not in raw.annotations.
- In mixed-format releases, do not keep adding MAT/CSV label-sidecar loaders when the
  sandbox sample files are standard raw recordings and kernel_requirements contains no
  sidecar-derived misc/super label."""

_KERNEL_EVENT_DIAGNOSE_SYSTEM = """\
You are an EEG kernel engineer. The previous kernel loaded sample files without error
and populated eegunity_description, BUT the resulting raw objects or full_scan exposed
FAR FEWER annotations/events than the local raw markers or sibling events.tsv files
indicate. Your task: diagnose WHY and emit a corrected kernel so
`mne.events_from_annotations(raw)` yields the literal local event IDs.

Common root causes — pick the one that fits the evidence:
  1. Raw file format carries no triggers (EEGLAB .set with empty `event` field, EDF
     without annotations, BrainVision .eeg without its marker file). Events MUST come
     from events.tsv — use `mne.Annotations` or `mne.annotations_from_events` keyed on
     the `onset`/`duration`/`trial_type` (or `value`) columns.
  1b. EDF clinical corpora often store intervals in a sibling CSV/TSE/LBL file or a
      per-subject summary text file instead of the EDF header. Parse those local
      intervals, dedupe repeated channel-level rows by `(start, stop, label)`, and
      create raw.annotations with the literal sidecar label.
  2. Kernel read events.tsv with the wrong column — e.g. took `trial_type` when the
     meaningful trigger is in `value`, or vice versa. Look at the events.tsv snippet
     you are given and pick the column that actually carries distinguishable labels.
  3. HC-5 violation — kernel remapped/renamed event IDs (e.g. `event_id_map={{...}}`
     or `mne.rename_events(...)`). Remove the remap; pass literal tsv labels through.
  4. `mne.find_events()` was called on a file with no STIM channel → silently returned
     empty. Switch to annotation-based events.
  5. Onset unit mismatch — events.tsv `onset` is in seconds, but the kernel passed
     samples to `mne.Annotations(onset=..., sfreq=...)` or forgot to scale.
  6. The kernel loaded events but assigned them to `raw.info` instead of
     `raw.set_annotations(...)` → they never reach `raw.annotations`.
  7. Custom `load(...)` builds annotations, but `apply(...)` only writes metadata.
     Real full_scan may call `apply(...)` on a bare raw object; share the parser helper
     between `load(...)` and `apply(...)`, or have `apply(...)` rebuild from row/File Path.

You are given:
  - the prior kernel's full source (truncated if large),
  - per-file annotation counts it produced vs expected events.tsv row counts when present,
  - the matching events.tsv snippet (header + first rows) for each sample file when present,
  - the non-canonical numeric columns of events.tsv (from the grounded catalog) when present,
  - the events.json column definitions if present,
  - otherwise the current kernel and sample files for custom-format diagnosis.

HARD RULES:
  - Do NOT fabricate event labels. Use the literal strings in the relevant tsv column.
  - HC-5: do NOT remap or rename event IDs from any source. Semantic labels belong in
    analysis.md Meaning fields, never as replacement annotation descriptions.
  - Preserve the full kernel signature, eegunity_description (dynamic json.dumps), and
    the `KERNEL = <ClassName>()` module-level assignment.
  - All other requirements from the initial `_KERNEL_SYSTEM` still apply.

Output ONLY a Python code block — no explanation, no JSON:
```python
<full corrected kernel source code here>
```"""


def _compute_expected_events(sample_files: List[str], ds_dir: Path) -> Dict[str, int]:
    """For each sample EEG file, count rows in its sibling `*_events.tsv` (if any).

    Returns {abs_path: expected_event_count}. Read-only, no schema imposed.
    """
    out: Dict[str, int] = {}
    for fpath in sample_files:
        p = Path(fpath)
        stem = p.stem
        # Try exact-stem sibling first, then BIDS-style sibling under the same dir.
        candidates = [
            p.with_name(stem + "_events.tsv"),
            p.parent / (stem.rsplit("_", 1)[0] + "_events.tsv") if "_" in stem else None,
        ]
        for c in candidates:
            if c is None or not c.exists():
                continue
            try:
                lines = c.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            if len(lines) < 2:
                continue
            # Count non-empty data rows (skip the header).
            n = sum(1 for ln in lines[1:] if ln.strip())
            out[str(p)] = n
            break
    return out


def _verify_kernel_events(stdout: str, expected_map: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
    """Parse `[EVENTS] <fpath> annotations=N` lines; compare to expected tsv counts.

    Returns (ok, report). ok=False when a sample file with expected>=5 produced
    got < 0.5 * expected — a reliable signal the kernel dropped events.tsv on the floor.
    """
    got_map: Dict[str, int] = {}
    for m in re.finditer(r"^\[EVENTS\]\s+(\S+)\s+annotations=(\d+)", stdout, re.MULTILINE):
        got_map[m.group(1)] = int(m.group(2))
    per_file: List[Dict[str, Any]] = []
    any_mismatch = False
    for fpath, expected in expected_map.items():
        got = got_map.get(fpath, 0)
        mismatch = (expected >= 5 and got < 0.5 * expected)
        any_mismatch = any_mismatch or mismatch
        per_file.append({"file": fpath, "expected": expected, "got": got, "mismatch": mismatch})
    summary = (
        f"files_with_events_tsv={len(expected_map)} "
        f"mismatches={sum(1 for x in per_file if x['mismatch'])} "
        f"min_got={min((x['got'] for x in per_file), default=0)}"
    )
    return (not any_mismatch), {"per_file": per_file, "summary": summary, "got_map": got_map}


def _format_event_mismatch(
    mismatch: Dict[str, Any],
    ds_dir: Path,
    sample_files: List[str],
    events_numeric_columns: Optional[Dict[str, List[str]]] = None,
) -> str:
    """Assemble a compact evidence block for _KERNEL_EVENT_DIAGNOSE_SYSTEM retries."""
    lines = [f"[event mismatch summary] {mismatch['summary']}", ""]
    for entry in mismatch["per_file"][:5]:
        fpath = entry["file"]
        p = Path(fpath)
        lines.append(f"[file] {p.name}")
        lines.append(f"  expected_events_in_tsv={entry['expected']}, kernel_produced_annotations={entry['got']}")
        # Attach events.tsv head
        stem = p.stem
        tsv_candidates = [
            p.with_name(stem + "_events.tsv"),
            p.parent / (stem.rsplit("_", 1)[0] + "_events.tsv") if "_" in stem else None,
        ]
        for c in tsv_candidates:
            if c is None or not c.exists():
                continue
            try:
                head = c.read_text(encoding="utf-8").splitlines()[:12]
            except Exception:
                head = []
            if head:
                lines.append(f"  [events.tsv head: {c.name}]")
                for ln in head:
                    lines.append(f"    {ln}")
                # events.json peer
                ej = c.with_suffix(".json")
                if ej.exists():
                    try:
                        j = ej.read_text(encoding="utf-8")
                        if len(j) < 1500:
                            lines.append(f"  [events.json: {ej.name}]")
                            lines.append(f"    {j.replace(chr(10), chr(10) + '    ')}")
                    except Exception:
                        pass
            break
        lines.append("")
    if events_numeric_columns:
        lines.append("[events.tsv numeric columns discovered across the dataset]")
        for fname, cols in list(events_numeric_columns.items())[:10]:
            lines.append(f"  {fname}: {cols}")
        lines.append("")
    return "\n".join(lines)


_RULEBOOK_VALIDATION_CHECKS = [
    (r"KERNEL\s*=\s*\w+\(", "KERNEL = ... object missing at module level"),
    (r"\bKERNEL_ID\s*=", "KERNEL_ID attribute missing from kernel class/instance"),
    (r"def apply\b", "apply() method missing entirely"),
    (r"udataset", "udataset parameter missing from apply()"),
    (r"eegunity_description", "eegunity_description key missing"),
    (r'"age"', '"age" field missing from eegunity_description'),
    (r'"sex"', '"sex" field missing from eegunity_description'),
    (r'"amplifier"', '"amplifier" field missing from eegunity_description'),
    (r'"cap"', '"cap" field missing from eegunity_description'),
    (r'"handedness"', '"handedness" field missing from eegunity_description'),
]


def _extract_apply_body(code: str) -> str:
    """Return the text of def apply(...) body, or '' if not parsable.

    Handles optional return-type annotations like `-> mne.io.BaseRaw:`.
    """
    m = re.search(r"def apply\s*\([^)]*\)[^:\n]*:\s*\n", code)
    if not m:
        return ""
    start = m.end()
    lines = code[start:].splitlines(keepends=True)
    if not lines:
        return ""
    # Determine body indent from first non-blank line
    body_indent = None
    for line in lines:
        stripped = line.lstrip()
        if stripped and not stripped.startswith("#"):
            body_indent = len(line) - len(stripped)
            break
    if body_indent is None or body_indent == 0:
        return ""
    body: List[str] = []
    for line in lines:
        if not line.strip():
            body.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if indent < body_indent:
            break
        body.append(line)
    return "".join(body)


def _static_validate(code: str,
                    kernel_requirements: Optional[Dict[str, Any]] = None) -> List[str]:
    """Quick static checks before running subprocess.

    Hardened v3.1: when kernel_requirements declares required_info_fields or
    derived_misc_channels, the kernel source MUST reference each name. Also
    requires the eegunity_description dict to be populated at apply() time
    (dynamic json.dumps into raw.info['description']) rather than as a
    class-level static — previous rules only checked for the field names as
    string literals, which a static dict could satisfy trivially.
    """
    errors: List[str] = []
    for pattern, msg in _RULEBOOK_VALIDATION_CHECKS:
        if not re.search(pattern, code):
            errors.append(f"STATIC CHECK FAILED: {msg}")

    errors.extend(_event_remap_check(code))

    if "set_montage" in code and "on_missing" not in code:
        errors.append(
            "STATIC CHECK FAILED: set_montage(...) is used without "
            '`on_missing="ignore"`. Add on_missing="ignore" and normalize channel '
            "name whitespace before montage assignment so full_scan does not reject "
            "records with partial montage coverage."
        )

    if "rename_channels" in code and "allow_duplicates" not in code:
        errors.append(
            "STATIC CHECK FAILED: rename_channels(...) is used without "
            "allow_duplicates=True or an explicit duplicate-safe strategy. EDF files "
            "often contain duplicate channel names; make target names unique before "
            "renaming or pass allow_duplicates=True."
        )

    if re.search(r"raw\.add_channels\s*\(", code) and not re.search(r"\.load_data\s*\(", code):
        errors.append(
            "STATIC CHECK FAILED: raw.add_channels(...) is used without raw.load_data(). "
            "EDF/GDF/BDF/SET/FIF Raw objects are usually not preloaded; call "
            "raw.load_data() first, or use raw.set_annotations(...) for interval labels "
            "instead of creating a misc channel."
        )

    if re.search(r"row\s*\[\s*['\"]file_path['\"]\s*\]", code):
        errors.append(
            "STATIC CHECK FAILED: use row.get(\"File Path\") rather than row['file_path']. "
            "EEGUnity row keys are title-cased in the sandbox/full_scan path; convert the "
            "result to str before string operations."
        )

    # Rule #3 (tightened): apply() body must assign raw.info["description"] via
    # json.dumps(...) so the per-subject eegunity_description is actually
    # written per file. A class-level dict alone never reaches raw.info.
    apply_body = _extract_apply_body(code)
    if apply_body:
        has_dynamic_write = re.search(
            r"raw\.info\[\s*['\"]description['\"]\s*\]\s*=\s*json\.dumps\s*\(",
            apply_body,
        )
        if not has_dynamic_write:
            errors.append(
                "STATIC CHECK FAILED: apply() body must contain the EXACT line "
                "`raw.info[\"description\"] = json.dumps({...})` (rulebook #3). "
                "MNE stores description as a STRING, not a dict — do NOT use "
                "`raw.info[\"description\"] = {}` / `.update(...)` / dict assignment. "
                "Build a dict with keys `original_description` and "
                "`eegunity_description`, then json.dumps it in ONE statement."
            )
        canonical_fields = ["age", "sex", "amplifier", "cap", "handedness"]
        canonical_source = apply_body
        if re.search(r"['\"]eegunity_description['\"]\s*:\s*[A-Za-z_]\w+", apply_body):
            # Common good pattern: a helper builds the canonical dict and apply()
            # writes it dynamically. Validate those helper defaults too.
            canonical_source += "\n" + code
        missing_canonical = []
        for field in canonical_fields:
            literal_key = re.search(rf"['\"]{re.escape(field)}['\"]\s*:", canonical_source)
            explicit_set = re.search(
                rf"eegunity_description\s*\[\s*['\"]{re.escape(field)}['\"]\s*\]",
                canonical_source,
            )
            if not literal_key and not explicit_set:
                missing_canonical.append(field)
        if missing_canonical:
            errors.append(
                "STATIC CHECK FAILED: apply() must explicitly populate canonical "
                "eegunity_description fields with defaults when local metadata is "
                f"missing: {missing_canonical}. Do not rely on looping over "
                "required_info_fields, because absent participants.tsv files would "
                "leave the required keys missing."
            )
    else:
        errors.append(
            "STATIC CHECK FAILED: cannot locate apply() body for dynamic-write check."
        )

    if kernel_requirements:
        info_fields = kernel_requirements.get("required_info_fields") or []
        missing_info = [
            f for f in info_fields
            if not re.search(rf"\b{re.escape(f)}\b", code)
        ]
        if missing_info:
            errors.append(
                "STATIC CHECK FAILED: required_info_fields not referenced in kernel "
                f"(must be read from participants.tsv and put into eegunity_description): "
                f"{missing_info}"
            )

        derived = kernel_requirements.get("derived_misc_channels") or []
        missing_misc = []
        for d in derived:
            name = d.get("name") if isinstance(d, dict) else None
            if name and not re.search(rf"\b{re.escape(name)}\b", code):
                missing_misc.append(name)
        if missing_misc:
            errors.append(
                "STATIC CHECK FAILED: derived_misc_channels not created in kernel "
                f"(must appear as misc-type channels on raw): {missing_misc}"
            )

        native_misc = kernel_requirements.get("required_native_misc") or []
        missing_native = [
            n for n in native_misc
            if not re.search(rf"\b{re.escape(n)}\b", code)
        ]
        if missing_native:
            errors.append(
                "STATIC CHECK FAILED: required_native_misc not referenced in kernel: "
                f"{missing_native}"
            )

    return errors


# Patterns that indicate the kernel writes/deletes files — not acceptable.
_DANGEROUS_PATTERNS: List[Tuple[str, str]] = [
    (r"\bos\.remove\b",        "os.remove — file deletion"),
    (r"\bos\.unlink\b",        "os.unlink — file deletion"),
    (r"\bos\.rmdir\b",         "os.rmdir — directory deletion"),
    (r"\bshutil\.rmtree\b",    "shutil.rmtree — recursive deletion"),
    (r"\bshutil\.move\b",      "shutil.move — file move/rename"),
    (r"\bsubprocess\b",        "subprocess — shell execution"),
    (r"\bos\.system\b",        "os.system — shell execution"),
    (r"\bos\.popen\b",         "os.popen — shell execution"),
    (r"\beval\s*\(",           "eval() — dynamic code execution"),
    (r"\bexec\s*\(",           "exec() — dynamic code execution"),
    # write-mode open: open(path, 'w') / open(path, 'wb') / open(path, 'a')
    (r"""open\s*\([^)]*['"][wa]b?['"]""", "open() in write/append mode — file write"),
]


def _security_check(code: str) -> List[str]:
    """Return list of security violations found in the generated kernel code."""
    violations = []
    for pattern, desc in _DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            violations.append(f"SECURITY: {desc}")
    return violations


_EVENT_REMAP_PATTERNS: List[Tuple[str, str]] = [
    (r"\bmne\.rename_events\s*\(", "mne.rename_events replaces event IDs"),
    (r"\b(?:event_id_map|rename_events|replace_events)\s*=", "event remap variable"),
    (r"\b(?:new_event_id|numeric_event_map)\s*=", "new/canonical event-id mapping"),
    (r"\bdef\s+_?(?:remap|rename|update)_?events?\b", "event remap helper"),
    (r"\bdef\s+_?remap_annotations\b", "annotation remap helper"),
    (r"\b768\s*\+\s*int\s*\(", "class label offset into acquisition event ID"),
    (r"\bclasslabel\b[\s\S]{0,600}\b768\s*\+", "classlabel converted to 769/770/771/772-style IDs"),
]


def _event_remap_check(code: str) -> List[str]:
    """Detect obvious HC-5 event-remapping patterns in generated kernels."""
    violations: List[str] = []
    for pattern, desc in _EVENT_REMAP_PATTERNS:
        if re.search(pattern, code):
            violations.append(
                "HC-5 CHECK FAILED: generated kernel appears to remap/rename event IDs "
                f"({desc}). Preserve literal raw marker IDs in raw.annotations; put "
                "semantic interpretation in analysis.md Meaning fields instead."
            )
    return violations


def _extract_code_block(raw: str) -> str:
    """Extract Python source from a markdown ```python ... ``` code block."""
    # Strip <think> blocks (some models include chain-of-thought)
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    # Match ```python ... ``` or ``` ... ```
    m = re.search(r"```python\s*\n([\s\S]*?)\n```", raw, re.IGNORECASE)
    if not m:
        m = re.search(r"```\s*\n([\s\S]*?)\n```", raw)
    if m:
        return m.group(1).strip()
    # Fallback: if the model just returned raw Python without fences, try detecting it
    if "def apply" in raw and "KERNEL" in raw:
        return raw.strip()
    return ""


def _build_test_script(
    kernel_path: Path,
    sample_files: List[str],
    eegunity_path: str,
    python_env: str,
) -> str:
    """Generate a Python test script that imports and applies the kernel."""
    files_repr = json.dumps(sample_files)
    eegunity_import = (
        f'import sys; sys.path.insert(0, {json.dumps(eegunity_path)})\n'
        if eegunity_path else ""
    )
    return f"""\
{eegunity_import}import sys
import importlib.util
import traceback

kernel_path = {json.dumps(str(kernel_path))}
spec = importlib.util.spec_from_file_location("_test_kernel", kernel_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["_test_kernel"] = mod  # required for @dataclass and similar decorators
spec.loader.exec_module(mod)

kernel = mod.KERNEL
print(f"[TEST] Kernel loaded: {{kernel.KERNEL_ID}}")

sample_files = {files_repr}

import mne
mne.set_log_level("WARNING")

errors = []
_EXT_READERS = {{
    ".edf": lambda f: mne.io.read_raw_edf(f, preload=False, verbose=False),
    ".bdf": lambda f: mne.io.read_raw_bdf(f, preload=False, verbose=False),
    ".gdf": lambda f: mne.io.read_raw_gdf(f, preload=False, verbose=False),
    ".set": lambda f: mne.io.read_raw_eeglab(f, preload=False, verbose=False),
    ".fif": lambda f: mne.io.read_raw_fif(f, preload=False, allow_maxshield=True, verbose=False),
    ".eeg": lambda f: mne.io.read_raw_brainvision(f, preload=False, verbose=False),
}}

def _load_with_kernel(load_fn, fpath, row):
    if load_fn is None:
        return None
    last_err = None
    for arg in (fpath, row):
        try:
            raw_obj = load_fn(arg)
            if raw_obj is not None:
                return raw_obj
        except TypeError as exc:
            last_err = exc
            continue
        except Exception as exc:
            last_err = exc
            break
    if last_err is not None:
        raise last_err
    return None

tested_count = 0
custom_load_count = 0
runtime_apply_recovery_checked = False
for fpath in sample_files:
    print(f"[TEST] Testing: {{fpath}}")
    try:
        import pandas as pd
        row = pd.Series({{"File Path": fpath}})
        ext = fpath[fpath.rfind("."):].lower()
        reader = _EXT_READERS.get(ext)
        raw = None
        used_custom_load = False
        if reader is not None:
            try:
                raw = reader(fpath)
            except Exception as load_err:
                print(f"  [WARN] Standard reader could not load {{fpath}}: {{load_err}}")

        if raw is None:
            load_fn = getattr(kernel, "load", None)
            if load_fn is None:
                if reader is None:
                    errors.append(
                        f"{{fpath}}: unsupported extension {{ext}} and kernel has no custom load() method. "
                        "For .mat/custom formats, implement load(...) returning an MNE Raw object."
                    )
                else:
                    print(f"  [SKIP] Cannot load {{fpath}} and no custom load() is available")
                continue
            try:
                raw = _load_with_kernel(load_fn, fpath, row)
                custom_load_count += 1
                used_custom_load = True
                print("  [OK] custom load() produced raw object")
            except Exception as load_err:
                errors.append(f"{{fpath}}: custom load() failed: {{load_err}}")
                continue
            if raw is None:
                errors.append(f"{{fpath}}: custom load() returned None")
                continue

        tested_count += 1
        result = kernel.apply(None, raw, row)
        import json as _json
        desc = result.info.get("description", "")
        try:
            parsed = _json.loads(desc)
        except Exception:
            parsed = {{}}
        eegu = parsed.get("eegunity_description", {{}})
        required = {{"age", "sex", "amplifier", "cap", "handedness"}}
        missing = required - set(eegu.keys())
        if missing:
            errors.append(f"{{fpath}}: eegunity_description missing fields: {{missing}}")
        else:
            print(f"  [OK] age={{eegu['age']!r}} sex={{eegu['sex']!r}} channels={{len(result.ch_names)}}")

        # Report event count so the outer verifier can diff against events.tsv.
        try:
            n_ann = len(result.annotations) if getattr(result, "annotations", None) is not None else 0
        except Exception:
            n_ann = 0
        # Also report misc channel names for the outer misc verifier (Change #3).
        try:
            misc_names = [ch for ch, ct in zip(result.ch_names, result.get_channel_types()) if ct == "misc"]
        except Exception:
            misc_names = []
        print(f"[EVENTS] {{fpath}} annotations={{n_ann}}")
        print(f"[MISC] {{fpath}} channels={{_json.dumps(misc_names)}}")

        # EEGUnity full_scan may call apply() on a raw object loaded by its own parser
        # without first calling custom load(). If load() found annotations, apply()
        # must be able to restore them from row/File Path when the incoming raw is bare.
        if used_custom_load and n_ann > 0 and not runtime_apply_recovery_checked:
            runtime_apply_recovery_checked = True
            try:
                probe = result.copy()
                probe.set_annotations(mne.Annotations([], [], []))
                recovered = kernel.apply(None, probe, row)
                recovered_n = len(recovered.annotations) if getattr(recovered, "annotations", None) is not None else 0
                if recovered_n <= 0:
                    errors.append(
                        f"{{fpath}}: custom load() created annotations, but apply() did not "
                        "recreate them when given a raw object with empty annotations. "
                        "Move the same row/File Path annotation-building logic into apply(); "
                        "otherwise full_scan may report Events Not Found."
                    )
                else:
                    print(f"  [OK] apply() restored annotations without relying on load(): {{recovered_n}}")
            except Exception as recovery_err:
                errors.append(f"{{fpath}}: apply() annotation-recovery probe failed: {{recovery_err}}")
    except Exception as e:
        errors.append(f"{{fpath}}: {{traceback.format_exc()}}")

# If every sample file was skipped, we never called kernel.apply() and the errors
# list may be empty regardless of validity. This is invalid: .mat/custom formats
# must implement and exercise a custom load() path.
if tested_count == 0 and sample_files:
    errors.append(
        f"All {{len(sample_files)}} sample file(s) were skipped; kernel.apply() was never "
        "tested on real data. For unsupported formats such as .mat, implement custom "
        "load(...) and ensure the sandbox can exercise it."
    )
elif custom_load_count:
    print(f"[NOTE] custom load() exercised on {{custom_load_count}} file(s).")

if errors:
    print("\\n[FAIL] Errors:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"\\n[PASS] All {{len(sample_files)}} test file(s) passed.")
    sys.exit(0)
"""


def _pick_sample_files(ds_dir: Path, n: int = 5, format_evidence: str = "") -> List[str]:
    """Pick a diverse set of sample files from the dataset directory."""
    EEG_EXTS = {".edf", ".bdf", ".gdf", ".set", ".fif", ".mat", ".eeg"}
    STANDARD_RAW_EXTS = {".edf", ".bdf", ".gdf", ".set", ".fif", ".eeg"}
    # Suffixes that indicate non-raw FIF files
    _FIF_SKIP_SUFFIXES = ("-proj.fif", "-fwd.fif", "-cov.fif", "-ave.fif",
                          "-inv.fif", "-trans.fif", "-src.fif", "-bem.fif")
    all_files: List[Tuple[int, str]] = []
    for root, _, files in os.walk(str(ds_dir)):
        for f in files:
            fl = f.lower()
            if Path(fl).suffix not in EEG_EXTS:
                continue
            # Skip known non-raw fif files
            if fl.endswith(".fif") and any(fl.endswith(s) for s in _FIF_SKIP_SUFFIXES):
                continue
            fp = Path(root) / f
            all_files.append((fp.stat().st_size, str(fp)))
        if len(all_files) > 200:
            break

    if not all_files:
        return []

    standard_raw = [
        item for item in all_files
        if Path(item[1]).suffix.lower() in STANDARD_RAW_EXTS
    ]
    if standard_raw:
        # In mixed-format releases, MAT files are often labels, preprocessed
        # mirrors, or helper arrays for the standard raw recordings. Sampling
        # them here pressures the LLM to support an unrelated input format and
        # can hide whether the actual GDF/EDF/BDF/SET reader path is correct.
        #
        # Pure-MAT/custom datasets still have no STANDARD_RAW_EXTS, so the
        # custom loader path remains mandatory and cannot all-skip pass.
        all_files = standard_raw

    preferred = _sample_files_from_format_evidence(ds_dir, format_evidence, EEG_EXTS)
    if preferred:
        known = {f for _, f in all_files}
        selected: List[str] = []
        for p in preferred:
            if p in selected:
                continue
            if p in known or Path(p).exists():
                selected.append(p)
            if len(selected) >= n:
                return selected
        if selected:
            remaining = [item for item in all_files if item[1] not in set(selected)]
            remaining.sort(key=lambda x: x[0])
            if remaining:
                step = max(1, len(remaining) // max(1, n - len(selected)))
                for i in range(0, len(remaining), step):
                    selected.append(remaining[i][1])
                    if len(selected) >= n:
                        break
            return selected[:n]

    all_files.sort(key=lambda x: x[0])
    if len(all_files) <= n:
        return [f for _, f in all_files]
    # Pick stratified by size (small, mid, large)
    step = len(all_files) // n
    return [all_files[i * step][1] for i in range(n)]


def _sample_files_from_format_evidence(
    ds_dir: Path,
    format_evidence: str,
    eeg_exts: set[str],
) -> List[str]:
    """Prefer sample recordings named in interval evidence."""
    out: List[str] = []
    for line in (format_evidence or "").splitlines():
        if "interval_example:" not in line:
            continue
        payload = line.split("interval_example:", 1)[1].strip()
        candidates: List[Path] = []
        if " -> " in payload:
            left, right = payload.split(" -> ", 1)
            summary_path = ds_dir / left.strip()
            edf_name = right.split(":", 1)[0].strip()
            if edf_name:
                candidates.append(summary_path.parent / edf_name)
        else:
            rel = payload.split(":", 1)[0].strip()
            sidecar = ds_dir / rel
            if sidecar.suffix.lower() in {".csv", ".tse", ".lbl"}:
                candidates.append(sidecar.with_suffix(".edf"))
            elif sidecar.name.lower().endswith(".csv_bi"):
                candidates.append(sidecar.with_name(sidecar.name[:-7] + ".edf"))
            elif sidecar.name.lower().endswith(".tse_bi") or sidecar.name.lower().endswith(".lbl_bi"):
                candidates.append(sidecar.with_name(sidecar.name[:-7] + ".edf"))
            else:
                candidates.append(sidecar)

        for candidate in candidates:
            if candidate.suffix.lower() not in eeg_exts:
                continue
            if candidate.exists():
                out.append(str(candidate))
                break
    return out


def _format_kernel_requirements(kr: Optional[Dict[str, Any]]) -> str:
    """Render the v2 task_synthesizer kernel_requirements dict into the kernel prompt."""
    if not kr:
        return ""
    events = kr.get("required_event_ids") or []
    native_misc = kr.get("required_native_misc") or []
    info_fields = kr.get("required_info_fields") or []
    derived = kr.get("derived_misc_channels") or []
    if not (events or native_misc or info_fields or derived):
        return ""
    lines = [
        "=== Kernel Requirements (from v2 task synthesizer — MUST be honored) ===",
        "The kernel MUST produce output that exposes the following fields so that the",
        "downstream scan + Tasks section can train on them. Anti-hallucination rules:",
        "  * Do NOT fabricate a field that has no ground-truth source. If you cannot",
        "    derive a required field from the actual data files, omit it — reconcile will",
        "    drop the corresponding task rather than accept a hallucinated value.",
        "  * source_field for derived misc MUST be an actual grounded source: either a",
        "    participants.tsv column or an events.tsv:<column> listed in the catalog.",
        "",
    ]
    if events:
        lines.append(f"Required event IDs (must appear in scan): {events}")
        lines.append(
            "  HC-5 reminder: these must be literal raw marker IDs. If a required value "
            "looks semantic and the local file only contains numeric/string codes, keep "
            "the literal local code in annotations; semantic meaning belongs in analysis.md."
        )
    if native_misc:
        lines.append(f"Required native misc channels (already in raw data): {native_misc}")
    if info_fields:
        lines.append(f"Required info fields (participants.tsv columns): {info_fields}")
    if derived:
        lines.append("Required derived misc channels (kernel MUST create these):")
        for d in derived:
            lines.append(
                f"  - name = {d.get('name','?')!r}; "
                f"source_field = {d.get('source_field','?')!r}; "
                f"derivation = {d.get('derivation','?')}; "
                f"evidence = {d.get('groundable_evidence','?')}"
            )
    return "\n".join(lines)


def _format_error_history(error_history: List[Dict[str, Any]]) -> str:
    """Format prior failure history for injection into retry prompts.

    Shows the full error text for the 2 most recent failures and a one-line
    summary for older ones — same pattern used by Claude Code / Aider to keep
    LLM context relevant without exploding prompt size.
    """
    if not error_history:
        return ""
    lines = ["=== Prior attempt failures (do NOT repeat these approaches) ==="]
    recent_cutoff = max(0, len(error_history) - 2)
    for i, entry in enumerate(error_history):
        v, strategy = entry["version"], entry["strategy"]
        text = entry["full"] if i >= recent_cutoff else f"{entry['summary']} [full error truncated]"
        lines.append(f"\n[Attempt v{v}, strategy={strategy}]")
        lines.append(text)
    return "\n".join(lines)


def _check_all_zero_annotations(stdout: str, sample_files: List[str]) -> bool:
    """Return True when every tested file produced annotations=0.

    Returns False if no [EVENTS] lines were emitted (all files skipped / test
    crashed) — we need at least one confirmed test to trust the result.
    """
    got_map: Dict[str, int] = {}
    for m in re.finditer(r"^\[EVENTS\]\s+(\S+)\s+annotations=(\d+)", stdout, re.MULTILINE):
        got_map[m.group(1)] = int(m.group(2))
    if not got_map:
        return False
    return all(v == 0 for v in got_map.values())


def _format_zero_event_evidence(
    ds_dir: Path,
    sample_files: List[str],
    stdout: str,
    context: Dict[str, Any],
) -> str:
    """Build evidence block for the all-zero-annotation case (no events.tsv available).

    Gives the LLM enough context to decide: are events genuinely absent
    (resting state / continuous recording), or did the kernel miss them?
    """
    lines = [
        "[zero-annotation evidence] All tested sample files produced 0 annotations.",
        "No BIDS *_events.tsv sidecars were found, so expected-count verification",
        "was skipped.  Determine whether events truly do not exist (resting-state,",
        "marker-less recording) or whether the kernel failed to surface them.",
        "",
    ]

    # File format evidence
    ext_counts: Dict[str, int] = {}
    for f in sample_files:
        ext = Path(f).suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    lines.append(f"Sample file extensions: {ext_counts}")
    lines.append(f"Sample files ({len(sample_files)}): {[Path(f).name for f in sample_files[:5]]}")

    # Search for any events-like files anywhere in the dataset
    events_files: List[Path] = []
    if ds_dir.exists():
        for pat in ("*events*.tsv", "*events*.csv", "*events*.txt", "*markers*", "*trigger*"):
            events_files.extend(list(ds_dir.rglob(pat))[:3])
    if events_files:
        lines.append("\nEvent-related files found in dataset (may contain event info):")
        for ef in events_files[:6]:
            rel = ef.relative_to(ds_dir) if ds_dir in ef.parents else ef
            lines.append(f"  {rel}")
            try:
                head = ef.read_text(encoding="utf-8", errors="replace").splitlines()[:6]
                for ln in head:
                    lines.append(f"    {ln}")
            except Exception:
                pass
    else:
        lines.append("\nNo events/markers/trigger files found — dataset may be event-free.")

    # MISC channels from the test run (to show what the kernel DID produce)
    misc_hits = re.findall(r"^\[MISC\].*", stdout, re.MULTILINE)
    if misc_hits:
        lines.append("\nMISC channels produced by kernel:")
        for ln in misc_hits[:5]:
            lines.append(f"  {ln}")

    # Dataset tree for structural context
    tree = context.get("ds_tree", "")[:1500]
    if tree:
        lines.append(f"\nDataset directory tree (truncated):\n{tree}")

    # Paradigm hint from analysis.md
    analysis = context.get("analysis_md", "")
    pm = re.search(r"## Paradigm\s*(.*?)(?=^##|\Z)", analysis, re.DOTALL | re.MULTILINE)
    if pm:
        lines.append(f"\nParadigm (from analysis.md):\n{pm.group(1).strip()[:400]}")

    return "\n".join(lines)


def build_kernel(
    dataset_name: str,
    context: Dict[str, Any],
    tasks_section: str,
    call_llm,
    budget,
    log,
    sandbox_dir: Path,
    python_env: str,
    eegunity_path: str,
    dataset_path: str,
    kernel_requirements: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Path, bool]:
    """
    Iterative kernel generation loop.

    Returns:
        (kernel_code, kernel_path, success)
    """
    ds_dir = Path(dataset_path) if dataset_path else Path(context["ds_dir"])
    format_evidence = context.get("format_evidence", "")
    sample_files = _pick_sample_files(ds_dir, format_evidence=format_evidence)
    log(f"[KernelBuilder] Sample files for testing: {len(sample_files)}")
    if not sample_files:
        log("[KernelBuilder] WARNING: No EEG files found for testing. Will generate kernel without testing.")

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # Build the initial generation prompt
    casebook_summary = context.get("kernel_casebook", "")

    reqs_block = _format_kernel_requirements(kernel_requirements)
    sample_block = "\n".join(f"- {Path(p).name} ({p})" for p in sample_files[:8])

    base_user = (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md ===\n{context['analysis_md'][:4000]}\n\n"
        f"=== Dataset directory tree ===\n{context['ds_tree'][:2000]}\n\n"
        f"=== Tasks to support ===\n{tasks_section[:3000]}\n\n"
        + (f"{reqs_block}\n\n" if reqs_block else "")
        + (f"=== Sandbox sample files that MUST pass ===\n{sample_block}\n\n" if sample_block else "")
        + (f"=== Raw format evidence ===\n{format_evidence[:5000]}\n\n" if format_evidence else "")
        + f"=== KERNEL_RULEBOOK ===\n{context['rulebook'][:6000]}\n\n"
        f"=== Generic anonymized kernel casebook ===\n{casebook_summary[:6000]}\n\n"
        f"=== Existing kernel (if any; parsing reference only, do not copy event remapping) ===\n{context.get('existing_kernel', '')[:3000]}\n\n"
        f"Now write the complete kernel for {dataset_name}."
    )

    MAX_VERSIONS = 9               # total iteration budget
    MAX_EVENT_DIAGNOSE_RETRIES = 10  # generous — outer MAX_VERSIONS is the real cap
    _REGENERATE_FROM_V = 7         # v7-9 switch to full re-generation with failure history

    kernel_code = ""
    last_error = ""
    version = 0
    success = False
    event_diagnose_mode = False   # subprocess passed but events.tsv mismatch detected
    is_zero_event = False         # subprocess passed but ALL sample files have 0 annotations
    force_regenerate = False      # structural static error → skip generic fix, go straight to regen
    event_diagnose_retries = 0
    error_history: List[Dict[str, Any]] = []   # rolling failure log for prompt injection
    expected_events_map = _compute_expected_events(sample_files, ds_dir) if sample_files else {}
    events_numeric_columns = (context.get("bids_sidecars") or {}).get("events_numeric_columns") or {}

    # Compact context digest carried into fix / event-diagnose prompts so the LLM
    # always knows what dataset and data format it is working with.
    context_digest = (
        f"=== Dataset context ===\n"
        f"Dataset: {dataset_name}\n"
        f"Directory tree:\n{context['ds_tree'][:1200]}\n"
        + (f"\nSandbox sample files:\n{sample_block[:800]}\n" if sample_block else "")
        + (f"\nRaw format evidence:\n{format_evidence[:1000]}\n" if format_evidence else "")
        + (f"\nGeneric casebook:\n{casebook_summary[:1200]}\n" if casebook_summary else "")
        + (f"\nKernel requirements:\n{reqs_block[:600]}\n" if reqs_block else "")
        + f"\nTasks excerpt:\n{tasks_section[:500]}\n"
    )

    while version < MAX_VERSIONS:
        version += 1

        # ── Determine strategy for this iteration ──────────────────────────
        if version == 1:
            mode = "initial"
        elif force_regenerate or version >= _REGENERATE_FROM_V:
            mode = "regenerate"
            force_regenerate = False
        elif event_diagnose_mode or is_zero_event:
            mode = "event_diagnose"
            event_diagnose_mode = False
            is_zero_event = False
        else:
            mode = "fix"

        log(f"[KernelBuilder] v{version}/{MAX_VERSIONS} mode={mode}...")
        history_block = _format_error_history(error_history)

        # ── Build prompt ───────────────────────────────────────────────────
        try:
            if mode == "initial":
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_SYSTEM},
                    {"role": "user", "content": base_user},
                ])

            elif mode == "event_diagnose":
                if event_diagnose_retries < MAX_EVENT_DIAGNOSE_RETRIES:
                    event_diagnose_retries += 1
                diag_user = (
                    f"Dataset: {dataset_name}\n\n"
                    f"=== Event-extraction failure evidence ===\n{last_error[:6000]}\n\n"
                    f"=== Current kernel ===\n```python\n{kernel_code[:10000]}\n```\n\n"
                    + (f"{history_block}\n\n" if history_block else "")
                    + f"{context_digest}\n\n"
                    "Emit a corrected kernel so that `raw.annotations` is populated.\n"
                    "If events genuinely do not exist in this dataset (resting state /\n"
                    "marker-less recording), return the kernel unchanged and add a comment\n"
                    "`# no events expected` — do NOT fabricate events."
                )
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_EVENT_DIAGNOSE_SYSTEM},
                    {"role": "user", "content": diag_user},
                ])

            elif mode == "regenerate":
                regen_user = (
                    f"{base_user}\n\n"
                    f"{'='*60}\n"
                    f"IMPORTANT — {len(error_history)} previous attempt(s) all failed.\n"
                    f"{history_block}\n\n"
                    "Write a completely new kernel. Do NOT repeat the approaches above."
                )
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_SYSTEM},
                    {"role": "user", "content": regen_user},
                ])

            else:  # fix
                fix_user = (
                    f"Fix this EEGUnity kernel for dataset '{dataset_name}'.\n\n"
                    f"=== Error ===\n{last_error[:3000]}\n\n"
                    f"=== Current kernel ===\n{kernel_code[:8000]}\n\n"
                    + (f"{history_block}\n\n" if history_block else "")
                    + f"{context_digest}\n\n"
                    "Requirements:\n"
                    "- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  (exact, one line)\n"
                    "- eegunity_description dict with: age(str), sex, amplifier, cap, handedness\n"
                    "- KERNEL = <ClassName>()  at end of file\n"
                )
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_FIX_SYSTEM},
                    {"role": "user", "content": fix_user},
                ])

        except BudgetExhausted:
            log(f"[KernelBuilder] Budget exhausted at v{version}. Using last available kernel.")
            break
        except Exception as exc:
            log(f"[KernelBuilder] v{version}: LLM call failed: {exc}. Using last available kernel.")
            break

        new_code = _extract_code_block(raw_response)
        if not new_code:
            last_error = "LLM returned no ```python code block."
            error_history.append({"version": version, "strategy": mode,
                                   "summary": last_error, "full": last_error})
            log(f"[KernelBuilder] v{version}: LLM returned no Python code block, retrying...")
            continue

        kernel_code = new_code

        # ── Security check ─────────────────────────────────────────────────
        sec_violations = _security_check(kernel_code)
        if sec_violations:
            last_error = "\n".join(sec_violations)
            fail_path = sandbox_dir / f"kernel_v{version}_SECURITY.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: SECURITY BLOCK ({fail_path.name}):\n{last_error}")
            error_history.append({"version": version, "strategy": mode,
                                   "summary": last_error[:120], "full": last_error})
            continue

        # ── Static validation ──────────────────────────────────────────────
        static_errors = _static_validate(kernel_code, kernel_requirements)
        if static_errors:
            last_error = "\n".join(static_errors)
            fail_path = sandbox_dir / f"kernel_v{version}_FAILED.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: Static validation failed ({fail_path.name}):\n{last_error}")
            log(f"[KernelBuilder] v{version}: Code preview: {kernel_code[:300]!r}")
            error_history.append({"version": version, "strategy": mode,
                                   "summary": last_error[:120], "full": last_error})
            # Structural errors (missing apply() or KERNEL=) waste fix attempts —
            # jump straight to re-generation on the next iteration.
            _structural_kws = ("apply() method missing", "KERNEL = ... object missing",
                               "cannot locate apply() body")
            if any(kw in last_error for kw in _structural_kws):
                force_regenerate = True
                log(f"[KernelBuilder] v{version}: Structural error → forcing regeneration next.")
            continue

        # ── Write to sandbox ───────────────────────────────────────────────
        kernel_path = sandbox_dir / f"kernel_v{version}.py"
        kernel_path.write_text(kernel_code, encoding="utf-8")
        log(f"[KernelBuilder] v{version}: Written to {kernel_path}")

        if not sample_files:
            log(f"[KernelBuilder] v{version}: No sample files — skipping subprocess test.")
            success = True
            break

        # ── Run test script ────────────────────────────────────────────────
        test_script = _build_test_script(kernel_path, sample_files, eegunity_path, python_env)
        test_path = sandbox_dir / f"test_v{version}.py"
        test_path.write_text(test_script, encoding="utf-8")

        log(f"[KernelBuilder] v{version}: Running test script...")
        try:
            result = subprocess.run(
                [python_env, str(test_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(sandbox_dir),
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            log(f"[KernelBuilder] v{version}: exit={result.returncode}")
            combined = (stdout + "\n" + stderr).strip()
            if combined:
                for line in combined.splitlines()[-30:]:
                    log(f"  {line}")

            if result.returncode == 0:
                # ── Verify annotation counts ───────────────────────────────
                if expected_events_map and event_diagnose_retries < MAX_EVENT_DIAGNOSE_RETRIES:
                    ok_events, mismatch = _verify_kernel_events(stdout, expected_events_map)
                    if not ok_events:
                        event_diagnose_retries += 1
                        event_diagnose_mode = True
                        last_error = _format_event_mismatch(
                            mismatch, ds_dir, sample_files, events_numeric_columns,
                        )
                        fail_path = sandbox_dir / f"kernel_v{version}_EVENTS_EMPTY.py"
                        fail_path.write_text(kernel_code, encoding="utf-8")
                        error_history.append({
                            "version": version, "strategy": mode,
                            "summary": f"events.tsv mismatch: {mismatch['summary']}",
                            "full": last_error[:2000],
                        })
                        log(
                            f"[KernelBuilder] v{version}: events mismatch "
                            f"({mismatch['summary']}); queuing event-diagnose retry "
                            f"{event_diagnose_retries}/{MAX_EVENT_DIAGNOSE_RETRIES}"
                        )
                        continue
                    elif expected_events_map:
                        log(f"[KernelBuilder] v{version}: event counts consistent with events.tsv")

                elif (not expected_events_map
                      and sample_files
                      and event_diagnose_retries < MAX_EVENT_DIAGNOSE_RETRIES
                      and _check_all_zero_annotations(stdout, sample_files)):
                    # Non-BIDS zero-annotation safety net: all files show 0 annotations
                    # even though no events.tsv exists to compare against.  Let the LLM
                    # decide whether events are genuinely absent or were missed.
                    event_diagnose_retries += 1
                    is_zero_event = True
                    last_error = _format_zero_event_evidence(
                        ds_dir, sample_files, stdout, context,
                    )
                    fail_path = sandbox_dir / f"kernel_v{version}_ZERO_EVENTS.py"
                    fail_path.write_text(kernel_code, encoding="utf-8")
                    error_history.append({
                        "version": version, "strategy": mode,
                        "summary": "all sample files produced 0 annotations (no events.tsv)",
                        "full": last_error[:2000],
                    })
                    log(
                        f"[KernelBuilder] v{version}: All annotations=0, no events.tsv; "
                        f"queuing zero-event diagnose "
                        f"{event_diagnose_retries}/{MAX_EVENT_DIAGNOSE_RETRIES}"
                    )
                    continue

                log(f"[KernelBuilder] v{version}: PASS")
                success = True
                break
            else:
                last_error = f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
                first_line = (stderr or stdout).splitlines()[0][:120] if (stderr or stdout) else "subprocess failed"
                error_history.append({"version": version, "strategy": mode,
                                       "summary": first_line, "full": last_error})
                log(f"[KernelBuilder] v{version}: FAIL — will retry")
        except subprocess.TimeoutExpired:
            last_error = "Test script timed out (120s)."
            error_history.append({"version": version, "strategy": mode,
                                   "summary": last_error, "full": last_error})
            log(f"[KernelBuilder] v{version}: TIMEOUT")
        except Exception as e:
            last_error = str(e)
            error_history.append({"version": version, "strategy": mode,
                                   "summary": str(e)[:120], "full": str(e)})
            log(f"[KernelBuilder] v{version}: subprocess error: {e}")

    # Write the final kernel to sandbox regardless
    final_path = sandbox_dir / "kernel_final.py"
    final_path.write_text(kernel_code or "# empty — generation failed", encoding="utf-8")
    return kernel_code, final_path, success


def patch_kernel_for_events(
    current_kernel_code: str,
    dataset_name: str,
    ds_dir: Path,
    sample_files: List[str],
    events_numeric_columns: Optional[Dict[str, List[str]]],
    required_event_ids: Optional[List[str]],
    call_llm,
    budget,
    log,
) -> Optional[str]:
    """Post-scan safety net: scan returned empty event_counts despite required_event_ids.

    Calls the LLM with the event-diagnose system prompt and events.tsv evidence,
    returns patched kernel source (or None if the LLM gave up / failed).
    """
    log(f"[Runner] Post-scan event recovery: scan missing events {required_event_ids or '(any)'}")
    # Build evidence — expected counts from tsv + empty got counts (all zero per scan)
    expected_map = _compute_expected_events(sample_files, ds_dir) if sample_files else {}
    per_file = [
        {"file": f, "expected": n, "got": 0, "mismatch": True}
        for f, n in expected_map.items()
    ]
    mismatch = {
        "summary": (
            f"post_scan_event_counts_empty; expected>=5 rows in {sum(1 for p in per_file if p['expected']>=5)} sample file(s)"
        ),
        "per_file": per_file,
    }
    evidence_block = _format_event_mismatch(
        mismatch, ds_dir, sample_files, events_numeric_columns,
    )
    required_hint = ""
    if required_event_ids:
        required_hint = (
            "\nThe downstream tasks currently reference these event IDs. Treat them as a hint,\n"
            "not permission to rename raw markers: if they are semantic names, keep literal\n"
            f"raw IDs in annotations and put semantic meaning in document fields:\n{required_event_ids}\n"
        )
    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"The full scan produced an empty event_counts dict after installing the kernel.\n"
        f"Patch the kernel so raw.annotations is populated from literal local markers or\n"
        f"sidecars during apply(), not only during load().{required_hint}\n"
        f"=== Evidence ===\n{evidence_block}\n\n"
        f"=== Current kernel ===\n```python\n{current_kernel_code[:12000]}\n```"
    )
    try:
        budget.charge("kernel_loop")
        raw = call_llm([
            {"role": "system", "content": _KERNEL_EVENT_DIAGNOSE_SYSTEM},
            {"role": "user", "content": user_msg},
        ])
    except Exception as exc:
        log(f"[Runner] Post-scan event recovery LLM call failed: {exc}")
        return None
    code = _extract_code_block(raw)
    if not code:
        log("[Runner] Post-scan event recovery returned no Python code block.")
        return None
    return code


def install_kernel(kernel_code: str, dataset_name: str, log) -> Path:
    """Copy the approved kernel to neurodoc/kernels/<dataset_name>.py."""
    dest = KERNELS_DIR / f"{dataset_name}.py"
    dest.write_text(kernel_code, encoding="utf-8")
    log(f"[KernelBuilder] Kernel installed: {dest}")
    return dest
