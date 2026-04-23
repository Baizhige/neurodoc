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

BIDS_ROOT = Path(__file__).parent.parent.parent
AGENT_DIR = Path(__file__).parent.parent
KERNELS_DIR = AGENT_DIR / "kernels"


_KERNEL_SYSTEM = """\
You are an EEG kernel engineer. Write a complete Python kernel file for EEGUnity.

Output your response as a Python code block ONLY — no explanation, no JSON:
```python
<full kernel source code here>
```

MANDATORY requirements — violating any will cause rejection:
1. Last line of file: KERNEL = <ClassName>()
2. Method signature MUST be EXACTLY: def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
   — DO NOT split across lines, DO NOT add type annotations to parameters, DO NOT rename udataset/raw/row
3. raw.info["description"] = json.dumps({
       "original_description": <original>,
       "eegunity_description": {"age": str, "sex": str, "amplifier": str, "cap": str, "handedness": str,
                                 <any extra required info fields, verbatim from participants.tsv>}
   })
4. age is always a STRING (e.g. "22", not 22)
5. sex is always lowercase: "male" / "female" / "unknown"
6. Inferred values: add comment  # LLM 推断，需人类复核
7. Channel rename BEFORE set_montage()
8. When `required_info_fields` is non-empty in kernel_requirements, the kernel MUST read
   the listed columns from participants.tsv for the current subject and include them as
   STRING values inside eegunity_description (see above). The downstream epoch writer
   attaches every non-canonical key as a source-level HDF5 attr so InfoDataset can reach it.
   If a column is genuinely missing for a subject, use "unknown" (do NOT fabricate).
9. When `required_native_misc` or `derived_misc_channels` is non-empty, the kernel MUST
   ensure those channel names exist on the returned raw as misc-type channels.
   - Native misc: already a physical channel on the raw; just make sure its ch_type is
     'misc' (use raw.set_channel_types({name: 'misc'}) if the loader mislabelled it).
   - Derived misc: the kernel creates the channel. The derivation mechanism is YOUR CHOICE
     — constant broadcast (one value per file), trial-locked step function from events.tsv,
     RawArray concatenated via raw.add_channels(), or any other MNE-compatible path. The
     ONLY invariants are (a) the exact `name` in raw.ch_names, (b) ch_types[name] == 'misc',
     (c) raw.get_data(picks=[name]) returns shape (1, len(raw.times)) with finite values.
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
"""

_KERNEL_FIX_SYSTEM = """\
You are an EEG kernel engineer fixing a broken Python kernel for EEGUnity.
Fix ONLY what is broken. Output your fix as a Python code block ONLY:
```python
<full corrected kernel source code here>
```

MANDATORY — any violation will fail validation again:
- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  — exact signature, one line, no type hints on params
- Inside apply(), one literal statement:
    raw.info["description"] = json.dumps({
        "original_description": <original>,
        "eegunity_description": { ... populated ... },
    })
  Do NOT use `raw.info["description"] = {}` / `.update(...)` / dict assignment —
  MNE stores description as a STRING, not a dict.
- When the error lists `required_info_fields`, read each one from participants.tsv
  for the current subject and put it (as str) into eegunity_description.
- When the error lists `derived_misc_channels`, create each one as an MNE misc-type
  channel on the returned raw. Derivation mechanism is YOUR choice — constant broadcast
  is fine for participants.tsv sources; events.tsv-sourced columns often warrant a
  trial-locked step function. Only invariants: exact `name` in raw.ch_names, ch_type
  'misc', and finite data of shape (1, len(raw.times)).
- If the failure was annotations/event-count related, fix the event-reading path:
  decide whether the raw file carries its own triggers, whether events.tsv must be
  parsed, or whether a STIM channel is available. HC-5 forbids remapping event IDs —
  pass the literal tsv labels through to raw.annotations."""

_KERNEL_EVENT_DIAGNOSE_SYSTEM = """\
You are an EEG kernel engineer. The previous kernel loaded sample files without error
and populated eegunity_description, BUT the resulting raw objects exposed FAR FEWER
annotations/events than the sibling BIDS events.tsv files contain. Your task: diagnose
WHY and emit a corrected kernel so `mne.events_from_annotations(raw)` yields at least
as many events as the non-empty rows in the sibling events.tsv.

Common root causes — pick the one that fits the evidence:
  1. Raw file format carries no triggers (EEGLAB .set with empty `event` field, EDF
     without annotations, BrainVision .eeg without its marker file). Events MUST come
     from events.tsv — use `mne.Annotations` or `mne.annotations_from_events` keyed on
     the `onset`/`duration`/`trial_type` (or `value`) columns.
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

You are given:
  - the prior kernel's full source (truncated if large),
  - per-file annotation counts it produced vs expected events.tsv row counts,
  - the matching events.tsv snippet (header + first rows) for each sample file,
  - the non-canonical numeric columns of events.tsv (from the grounded catalog),
  - the events.json column definitions if present.

HARD RULES:
  - Do NOT fabricate event labels. Use the literal strings in the relevant tsv column.
  - HC-5: do NOT remap or rename event IDs.
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

for fpath in sample_files:
    print(f"[TEST] Testing: {{fpath}}")
    try:
        import pandas as pd
        row = pd.Series({{"File Path": fpath}})
        ext = fpath[fpath.rfind("."):].lower()
        reader = _EXT_READERS.get(ext)
        if reader is None:
            print(f"  [SKIP] Unsupported extension: {{ext}}")
            continue
        try:
            raw = reader(fpath)
        except Exception as load_err:
            print(f"  [SKIP] Cannot load {{fpath}}: {{load_err}}")
            continue

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
    except Exception as e:
        errors.append(f"{{fpath}}: {{traceback.format_exc()}}")

if errors:
    print("\\n[FAIL] Errors:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"\\n[PASS] All {{len(sample_files)}} test file(s) passed.")
    sys.exit(0)
"""


def _pick_sample_files(ds_dir: Path, n: int = 5) -> List[str]:
    """Pick a diverse set of sample files from the dataset directory."""
    EEG_EXTS = {".edf", ".bdf", ".gdf", ".set", ".fif", ".mat", ".eeg"}
    # Suffixes that indicate non-raw FIF files
    _FIF_SKIP_SUFFIXES = ("-proj.fif", "-fwd.fif", "-cov.fif", "-ave.fif",
                          "-inv.fif", "-trans.fif", "-src.fif", "-bem.fif")
    all_files = []
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

    all_files.sort(key=lambda x: x[0])
    if len(all_files) <= n:
        return [f for _, f in all_files]
    # Pick stratified by size (small, mid, large)
    step = len(all_files) // n
    return [all_files[i * step][1] for i in range(n)]


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
        "  * source_field for derived misc MUST be an actual participants.tsv column.",
        "",
    ]
    if events:
        lines.append(f"Required event IDs (must appear in scan): {events}")
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
    sample_files = _pick_sample_files(ds_dir)
    log(f"[KernelBuilder] Sample files for testing: {len(sample_files)}")
    if not sample_files:
        log("[KernelBuilder] WARNING: No EEG files found for testing. Will generate kernel without testing.")

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # Build the initial generation prompt
    skill_summary = "\n\n".join(
        f"=== {name} ===\n{content[:3000]}"
        for name, content in context.get("skill_texts", {}).items()
    )
    example_summary = "\n\n".join(
        f"=== Example: {name} ===\n{content}"
        for name, content in context.get("example_kernels", {}).items()
    )

    reqs_block = _format_kernel_requirements(kernel_requirements)

    base_user = (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md ===\n{context['analysis_md'][:4000]}\n\n"
        f"=== Dataset directory tree ===\n{context['ds_tree'][:2000]}\n\n"
        f"=== Tasks to support ===\n{tasks_section[:3000]}\n\n"
        + (f"{reqs_block}\n\n" if reqs_block else "")
        + f"=== KERNEL_RULEBOOK ===\n{context['rulebook'][:6000]}\n\n"
        f"=== SKILL patterns ===\n{skill_summary[:6000]}\n\n"
        f"=== Example kernels ===\n{example_summary[:6000]}\n\n"
        f"=== Existing kernel (if any, for reference) ===\n{context.get('existing_kernel', '')[:3000]}\n\n"
        f"Now write the complete kernel for {dataset_name}."
    )

    MAX_VERSIONS = 7  # bumped from 5 → 7 so event-diagnose retries can fire alongside generic fixes
    MAX_EVENT_DIAGNOSE_RETRIES = 3

    kernel_code = ""
    last_error = ""
    version = 0
    success = False
    event_diagnose_mode = False          # toggled after a successful subprocess but mismatched events
    event_diagnose_retries = 0
    expected_events_map = _compute_expected_events(sample_files, ds_dir) if sample_files else {}
    events_numeric_columns = (context.get("bids_sidecars") or {}).get("events_numeric_columns") or {}

    while version < MAX_VERSIONS:
        version += 1
        log(f"[KernelBuilder] Generating kernel v{version}/{MAX_VERSIONS}...")

        try:
            if version == 1:
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_SYSTEM},
                    {"role": "user", "content": base_user},
                ])
            elif event_diagnose_mode:
                # Dedicated retry for empty/sparse annotations. Surface the evidence.
                diag_user = (
                    f"Dataset: {dataset_name}\n\n"
                    f"=== Event-extraction failure evidence ===\n{last_error[:6000]}\n\n"
                    f"=== Current kernel ===\n```python\n{kernel_code[:10000]}\n```\n\n"
                    f"Emit a corrected kernel so that `raw.annotations` is populated from the "
                    f"relevant source (events.tsv or file-native triggers) — see system prompt."
                )
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_EVENT_DIAGNOSE_SYSTEM},
                    {"role": "user", "content": diag_user},
                ])
                event_diagnose_mode = False  # consume the flag; new kernel will be re-verified
            else:
                # Generic fix retry
                fix_user = (
                    f"Fix this EEGUnity kernel for dataset '{dataset_name}'.\n\n"
                    f"=== Error ===\n{last_error[:3000]}\n\n"
                    f"=== Current kernel (may be shortened) ===\n{kernel_code[:8000]}\n\n"
                    f"Requirements:\n"
                    f"- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  (exact, one line)\n"
                    f"- eegunity_description dict with: age(str), sex, amplifier, cap, handedness\n"
                    f"- KERNEL = <ClassName>()  at end of file\n"
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
            log(f"[KernelBuilder] v{version}: LLM returned no Python code block, retrying...")
            last_error = "LLM returned no ```python code block."
            continue

        kernel_code = new_code

        # Security check — block kernels that write/delete files or run shell commands
        sec_violations = _security_check(kernel_code)
        if sec_violations:
            last_error = "\n".join(sec_violations)
            fail_path = sandbox_dir / f"kernel_v{version}_SECURITY.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: SECURITY BLOCK ({fail_path.name}):\n{last_error}")
            continue

        # Static validation (RULEBOOK compliance)
        static_errors = _static_validate(kernel_code, kernel_requirements)
        if static_errors:
            last_error = "\n".join(static_errors)
            fail_path = sandbox_dir / f"kernel_v{version}_FAILED.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: Static validation failed ({fail_path.name}):\n{last_error}")
            log(f"[KernelBuilder] v{version}: Code preview: {kernel_code[:300]!r}")
            continue

        # Write to sandbox
        kernel_path = sandbox_dir / f"kernel_v{version}.py"
        kernel_path.write_text(kernel_code, encoding="utf-8")
        log(f"[KernelBuilder] v{version}: Written to {kernel_path}")

        if not sample_files:
            log(f"[KernelBuilder] v{version}: No sample files — skipping subprocess test.")
            success = True
            break

        # Generate + run test script
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
                # Subprocess passed — now verify annotation counts vs events.tsv.
                if expected_events_map and event_diagnose_retries < MAX_EVENT_DIAGNOSE_RETRIES:
                    ok_events, mismatch = _verify_kernel_events(stdout, expected_events_map)
                    if not ok_events:
                        event_diagnose_retries += 1
                        event_diagnose_mode = True
                        last_error = _format_event_mismatch(
                            mismatch, ds_dir, sample_files, events_numeric_columns,
                        )
                        # Preserve the kernel for offline inspection
                        fail_path = sandbox_dir / f"kernel_v{version}_EVENTS_EMPTY.py"
                        fail_path.write_text(kernel_code, encoding="utf-8")
                        log(
                            f"[KernelBuilder] v{version}: events mismatch "
                            f"({mismatch['summary']}); queuing event-diagnose retry "
                            f"{event_diagnose_retries}/{MAX_EVENT_DIAGNOSE_RETRIES}"
                        )
                        continue
                    elif expected_events_map:
                        log(f"[KernelBuilder] v{version}: event counts look consistent with events.tsv")
                log(f"[KernelBuilder] v{version}: PASS")
                success = True
                break
            else:
                last_error = f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
                log(f"[KernelBuilder] v{version}: FAIL — will retry")
        except subprocess.TimeoutExpired:
            last_error = "Test script timed out (120s)."
            log(f"[KernelBuilder] v{version}: TIMEOUT")
        except Exception as e:
            last_error = str(e)
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
            f"\nThe downstream tasks require these event IDs to be preserved in raw.annotations:\n"
            f"{required_event_ids}\n"
        )
    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"The full scan produced an empty event_counts dict, even though events.tsv sidecars\n"
        f"contain events. Patch the kernel so raw.annotations is populated.{required_hint}\n"
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
    """Copy the approved kernel to app_kernel/kernels/<dataset_name>.py."""
    dest = KERNELS_DIR / f"{dataset_name}.py"
    dest.write_text(kernel_code, encoding="utf-8")
    log(f"[KernelBuilder] Kernel installed: {dest}")
    return dest
