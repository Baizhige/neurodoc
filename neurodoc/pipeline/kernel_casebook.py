"""Generic kernel-writing casebook for prompt injection.

The snippets here are intentionally anonymized. They teach parsing patterns
learned from reviewed kernels without naming datasets or copying human-reviewed
event-label remaps into generation prompts.
"""
from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


CASEBOOK_RULES = """\
=== GENERIC KERNEL CASEBOOK: GLOBAL RULES ===
- Preserve raw event IDs exactly. Do not rename `1` to `left`, `769` to `left hand`,
  or `T1` to a run-specific movement label. Semantic interpretation belongs in
  analysis.md Event Structure Meaning, not in raw.annotations descriptions.
- Allowed normalization is only representation cleanup that preserves identity:
  string coercion, strip surrounding whitespace, collapse accidental duplicate spaces,
  or prefix enrichment such as `taskA::1` when multiple file paradigms reuse the same
  raw ID and the original ID remains visible.
- If a label comes from papers or prior human review rather than the current dataset
  files, keep the raw ID and write the semantic note as inferred/needs review.
- Prefer short, explicit helpers: find companion sidecar, parse marker rows, build
  mne.Annotations, write eegunity_description, return raw.
"""


MAT_CASE = """\
=== CASEBOOK: MATLAB .mat or Custom Array Files ===
Exploration pattern:
1. Use `scipy.io.loadmat(file_path, simplify_cells=True)` and print/filter top-level
   keys. Expand nested structs until you find signal data, sampling rate, channel names,
   and marker/class fields.
2. Decide marker shape:
   - continuous marker: one code per sample, often mostly 0; merge contiguous non-zero
     regions into annotations.
   - event index: rows/columns hold onset sample/time plus code; convert each row to
     an annotation.
   - classlabel sidecar: per-trial labels align with generic cue events; preserve the
     raw cue ID and expose class labels via derived misc/super metadata only when the
     task requires it and the source is local.
3. If EEGUnity/MNE cannot load the file directly, put the file parser in one helper
   used by BOTH `load(...)` and `apply(...)`. `load(...)` should return an MNE RawArray;
   `apply(...)` must also rebuild/add annotations from the row/file path when the raw
   object it receives has no usable annotations. EEGUnity scans often call `apply(...)`
   on a partially loaded raw instead of calling `load(...)` first.
4. Set `HANDLES_UNAVAILABLE = True` when a custom loader is required. Make `load(...)`
   tolerant of either a file path string or a row/Series with `File Path`, because
   sandbox tests and EEGUnity adapters may call it differently.
Raw-ID rule:
- Annotation description should be the literal marker code, e.g. `"1"`, `"2"`,
  `"91"`, or a prefix-preserving value such as `"protocolA::1"`.
- Do not emit `"left hand MI"` or `"right"` as annotation descriptions unless those
  exact strings are present as raw marker values in the file/sidecar.
"""


GDF_EDF_CASE = """\
=== CASEBOOK: GDF/BDF/EDF Header Annotations ===
Exploration pattern:
1. Load with the matching MNE reader and inspect `raw.annotations.description` plus
   `mne.events_from_annotations(raw)`.
2. Many files already expose numeric annotation strings such as `769`, `770`, `T0`,
   or `T1`. These are valid event IDs. Preserve them.
3. Use channel rename only for channel identity, with explicit local evidence.
4. Set montage after channel rename and use `on_missing="ignore"`.
Raw-ID rule:
- Do not build `event_id_map`, `new_event_id`, `_NUMERIC_EVENT_MAP`, or call
  `mne.rename_events(...)` to replace event IDs with semantic labels.
- If two acquisition systems format the same raw code slightly differently, normalize
  only formatting, not meaning.
"""


EDF_CSV_CASE = """\
=== CASEBOOK: EDF with Companion CSV/TXT Annotation Files ===
Exploration pattern:
1. Search for sidecars beside the EDF first: same basename with `.csv`, `_events.csv`,
   `_annotations.csv`, or files in nearby annotation folders.
2. Parse comment-prefixed headers safely, then use DictReader/pandas on the actual
   table rows.
3. For interval annotations, use start/onset and stop/end/duration columns. Deduplicate
   repeated channel-level rows by `(start, stop, label)` before creating annotations.
4. If only a summary file exists, parse exact local lines for the current file and
   create intervals from those times.
Raw-ID rule:
- Annotation description is the literal local sidecar label, e.g. `bckg`, `gnsz`,
  `artifact`, `seiz`, or the raw code column value. Do not expand to prettier class
  names in the kernel.
"""


CLINICAL_INTERVAL_CASE = """\
=== CASEBOOK: Clinical EDF Interval Sidecars ===
- Some EDF corpora store all labels outside the EDF header. Common local formats:
  comma tables with `channel,start_time,stop_time,label,confidence`, token tables like
  `start stop label confidence`, and per-subject summaries with `File Name:` plus
  `Seizure N Start/End Time:` lines.
- For event/interval classification, create `raw.annotations` from those local rows.
  Use onset=start, duration=stop-start, and the literal local label. If a summary has
  no separate label column but the local field name is `Seizure`, `seizure` is a
  grounded event type from that file, not an external semantic remap.
- Channel-level rows often repeat the same interval once per montage channel; dedupe by
  `(start, stop, label)` before adding annotations.
- Do not solve interval labels by adding a synthetic misc channel unless the task
  explicitly needs a continuous/regression label. EDF files are commonly not preloaded,
  so `raw.add_channels(...)` without `raw.load_data()` fails; annotations are the
  correct path for interval event labels.
"""


BIDS_CASE = """\
=== CASEBOOK: BIDS events.tsv Sidecars ===
Exploration pattern:
1. Prefer the file-level `*_events.tsv`; otherwise use root/task-level sidecars only
   when their task label matches the EEG file.
2. Use `onset` in seconds when present; otherwise convert `sample / sfreq`.
3. Choose the label column by local evidence: usually `trial_type`, sometimes `value`,
   `stim_type`, `condition`, or `event_type`.
4. If raw annotations are empty or too sparse, populate `raw.annotations` from the
   sidecar so event counts match non-empty rows.
Raw-ID rule:
- Pass the literal selected column value through as annotation description.
- Never infer motor-imagery classes only because codes are 1-4 or 769-772.
"""


MI_TASK_CASE = """\
=== CASEBOOK: Motor-Imagery / Cued-Task Task Granularity ===
- A single grounded multi-class paradigm should normally become one task, not every
  possible pairwise subset.
- Add binary subsets only when a reference or local task file explicitly defines that
  subset or when the raw event set itself is only binary.
- Trial phase markers (rest, fixation, ready, cue onset, feedback) are not class names.
  They may support phase-detection tasks, but do not relabel them as MI classes.
- Evaluation labels from a local classlabel sidecar are not raw event IDs. Preserve the
  generic event ID and expose the classlabel through a grounded derived field only when
  the downstream task needs it.
"""


MIXED_FORMAT_CASE = """\
=== CASEBOOK: Mixed Standard Raw + Helper Sidecars ===
- When standard raw files such as GDF/BDF/EDF/SET/FIF are present, treat those as the
  primary recordings unless the task explicitly requires a custom file family.
- MAT/CSV/TXT files in the same release may be label keys, mirrors, preprocessed arrays,
  or helper sidecars. Do not create synthetic annotations for them just because they
  contain labels.
- If a sidecar stores class labels `1..4` for evaluation/training metadata, those
  labels are not raw event IDs. Do not convert them into acquisition event IDs such as
  `769..772`. Use literal raw annotations from the primary file, or create a derived
  misc/super field only when kernel_requirements explicitly asks for that label field.
"""


def _has_any(path: Path, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if any(True for _ in path.rglob(pattern)):
            return True
    return False


def select_casebook(format_type: str, data_path: Optional[Path], bids_sidecars: Dict[str, Any]) -> str:
    """Return format-relevant generic guidance for the kernel prompt."""
    blocks = [CASEBOOK_RULES]
    fmt = (format_type or "unknown").lower()
    path = data_path if data_path and data_path.is_dir() else None

    has_mat = fmt == "mat" or (path is not None and _has_any(path, ("*.mat",)))
    has_gdf_bdf = fmt in {"gdf", "bdf"} or (path is not None and _has_any(path, ("*.gdf", "*.bdf")))
    has_edf = fmt == "edf" or (path is not None and _has_any(path, ("*.edf", "*.EDF")))
    has_csv = path is not None and _has_any(path, ("*.csv", "*.CSV", "*.txt", "*.TXT"))
    has_interval_sidecar = path is not None and _has_any(
        path,
        ("*.tse", "*.tse_bi", "*.lbl", "*.lbl_bi", "*.edf.seizures", "*summary.txt", "*SUMMARY.txt"),
    )
    has_bids = fmt == "bids" or bool(bids_sidecars.get("events_tsv_samples"))

    if fmt == "mixed" or (has_mat and (has_gdf_bdf or has_edf)):
        blocks.append(MIXED_FORMAT_CASE)
    if has_mat:
        blocks.append(MAT_CASE)
    if has_gdf_bdf or has_edf:
        blocks.append(GDF_EDF_CASE)
    if has_edf and has_csv:
        blocks.append(EDF_CSV_CASE)
    if has_edf and (has_csv or has_interval_sidecar):
        blocks.append(CLINICAL_INTERVAL_CASE)
    if has_bids:
        blocks.append(BIDS_CASE)
    # MI task granularity is broadly useful and short enough to always include.
    blocks.append(MI_TASK_CASE)
    return "\n\n".join(blocks)


def collect_format_evidence(data_path: Path, format_type: str) -> str:
    """Collect small, read-only file-structure evidence for non-BIDS prompts."""
    if not data_path or not data_path.is_dir():
        return ""

    lines: List[str] = ["=== FORMAT EVIDENCE FROM RAW DATA DIRECTORY ==="]
    ext_counts: Dict[str, int] = {}
    for p in data_path.rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower() or "(no-ext)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        if sum(ext_counts.values()) > 2000:
            break
    if ext_counts:
        top = sorted(ext_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
        lines.append("File extension counts: " + ", ".join(f"{ext}={n}" for ext, n in top))

    if ".mat" in ext_counts:
        _append_mat_evidence(lines, data_path)
    _append_annotation_sidecar_evidence(lines, data_path, ext_counts)
    _append_csv_evidence(lines, data_path, ext_counts)
    _append_text_evidence(lines, data_path)

    return "\n".join(lines) if len(lines) > 1 else ""


def _append_mat_evidence(lines: List[str], data_path: Path) -> None:
    mats = sorted(_iter_sidecar_files(data_path, ("*.mat",), limit=40), key=lambda p: p.stat().st_size)[:2]
    if not mats:
        return
    lines.append("\n[MAT file structure samples]")
    try:
        import scipy.io as sio
    except Exception as exc:
        lines.append(f"scipy unavailable for MAT inspection: {exc}")
        return
    large_struct_probe_done = False
    for p in mats:
        lines.append(f"- {p.relative_to(data_path)}")
        try:
            whos = sio.whosmat(str(p))
            if whos:
                lines.append(
                    "  whosmat="
                    + str([(name, tuple(shape), dtype) for name, shape, dtype in whos[:12]])
                )
            if p.stat().st_size > 150 * 1024 * 1024:
                small_marker_vars = [
                    name for name, shape, _dtype in whos
                    if _is_markerish_name(name) and _shape_size(shape) <= 2_000_000
                ][:8]
                if not small_marker_vars:
                    if not large_struct_probe_done and _append_large_mat_struct_probe(lines, p):
                        large_struct_probe_done = True
                    else:
                        lines.append("  large_mat_skipped_full_load=true")
                    continue
                mat = sio.loadmat(str(p), simplify_cells=True, variable_names=small_marker_vars)
            else:
                mat = sio.loadmat(str(p), simplify_cells=True)
            keys = [k for k in mat.keys() if not str(k).startswith("__")]
            lines.append(f"  top_keys={keys[:12]}")
            for key in keys[:5]:
                value = mat.get(key)
                lines.append(f"  {key}: {_describe_value(value)}")
            marker_lines = _collect_marker_value_lines(mat)
            for marker_line in marker_lines[:8]:
                lines.append(f"  marker_values: {marker_line}")
        except Exception as exc:
            lines.append(f"  read_error={type(exc).__name__}: {exc}")


def _append_large_mat_struct_probe(lines: List[str], path: Path) -> bool:
    """Inspect one large MAT struct enough to expose label/onset fields.

    Some datasets keep all labels inside a top-level MATLAB struct alongside very
    large signal arrays. Loading a single smallest file is acceptable evidence
    gathering; doing it repeatedly is not, so callers gate this to once.
    """
    if path.stat().st_size > 850 * 1024 * 1024:
        lines.append("  large_mat_skipped_full_load=true")
        return False
    try:
        import scipy.io as sio
    except Exception:
        return False
    try:
        whos = sio.whosmat(str(path))
        struct_vars = [
            name for name, shape, dtype in whos
            if dtype == "struct" and _shape_size(shape) <= 4
        ]
        if not struct_vars:
            lines.append("  large_mat_skipped_full_load=true")
            return False
        mat = sio.loadmat(str(path), simplify_cells=True, variable_names=struct_vars[:1])
        lines.append(f"  large_struct_probe={struct_vars[0]}")
        for key, value in mat.items():
            if str(key).startswith("__"):
                continue
            lines.append(f"  {key}: {_describe_value(value)}")
        marker_lines = _collect_marker_value_lines(mat)
        for marker_line in marker_lines[:12]:
            lines.append(f"  marker_values: {marker_line}")
        return True
    except Exception as exc:
        lines.append(f"  large_struct_probe_error={type(exc).__name__}: {exc}")
        return False


def _shape_size(shape: Any) -> int:
    total = 1
    try:
        for dim in shape:
            total *= int(dim)
    except Exception:
        return 0
    return total


def _is_markerish_name(name: str) -> bool:
    lower = str(name).lower()
    compact = re.sub(r"[^a-z0-9]+", "", lower)
    tokens = {tok for tok in re.split(r"[^a-z0-9]+", lower) if tok}
    markerish_aliases = _MARKER_VALUE_KEYS | {
        "ann", "annotation", "annotations", "class", "classes", "condition",
        "conditions", "mrk", "stim", "stimulus", "trial", "trials", "y_dec",
        "ydec",
    }
    compact_aliases = {
        "classlabel", "classlabels", "eventid", "events", "trialtype", "ydec",
    }
    return lower in markerish_aliases or compact in compact_aliases or bool(tokens & markerish_aliases)


def _describe_value(value: Any) -> str:
    shape = getattr(value, "shape", None)
    dtype = getattr(value, "dtype", None)
    if isinstance(value, dict):
        parts = [f"dict keys={list(value.keys())[:12]}"]
        for key in list(value.keys())[:8]:
            child = value.get(key)
            child_shape = getattr(child, "shape", None)
            child_dtype = getattr(child, "dtype", None)
            summary = f"{key}:"
            if child_shape is not None:
                summary += f"shape={tuple(child_shape)}, dtype={child_dtype}"
                sample = _sample_values(child)
                if sample:
                    summary += f", sample_values={sample}"
            else:
                summary += type(child).__name__
            parts.append(summary)
        return "; ".join(parts)
    if shape is not None:
        sample = _sample_values(value)
        suffix = f", sample_values={sample}" if sample else ""
        return f"shape={tuple(shape)}, dtype={dtype}{suffix}"
    return type(value).__name__


def _sample_values(value: Any, limit: int = 8) -> List[str]:
    try:
        import numpy as np
    except Exception:
        return []
    try:
        arr = np.asarray(value)
        if arr.dtype == object or arr.size == 0 or arr.ndim > 2:
            return []
        flat = arr.reshape(-1)
        if flat.size > 2000:
            flat = flat[:2000]
        vals = []
        for item in np.unique(flat)[:limit]:
            text = str(item)
            if len(text) > 40:
                text = text[:37] + "..."
            vals.append(text)
        return vals
    except Exception:
        return []


_MARKER_VALUE_KEYS = {
    "y", "label", "labels", "classlabel", "classlabels", "code", "codes",
    "type", "typ", "event", "events", "event_id", "eventid", "marker", "markers",
    "target", "targets", "trial_type",
}
_TIMING_KEYS = {
    "pos", "position", "positions", "sample", "samples", "latency", "latencies",
    "time", "times", "time_interval", "rest_interval", "ival", "onset",
    "onsets", "duration", "durations",
}
_NON_EVENT_VALUE_KEYS = _TIMING_KEYS | {
    "fs", "sfreq", "srate", "rate", "sampling_rate", "samplingrate",
    "samplingfrequency", "sampling_frequency", "frequency", "freq",
}
_COORDINATE_CONTEXT_KEYS = {
    "chanlocs", "channel", "channels", "coords", "coordinate", "coordinates",
    "electrode", "electrodes", "loc", "location", "locations", "mnt",
    "montage", "optode", "optodes", "position", "positions", "probe", "sd",
}


def _collect_marker_value_lines(mat: Dict[str, Any]) -> List[str]:
    """Return explicit marker/value samples separate from large signal summaries."""
    lines: List[str] = []

    def walk(value: Any, prefix: str, parent_is_markerish: bool, depth: int) -> None:
        if depth > 4 or len(lines) >= 12:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                key_lower = key_text.lower()
                markerish = (
                    parent_is_markerish
                    or key_lower in {"mrk", "marker", "markers", "event", "events", "ann", "annotations"}
                    or _is_markerish_name(key_lower)
                )
                walk(child, f"{prefix}.{key_text}" if prefix else key_text, markerish, depth + 1)
            return

        key_lower = prefix.rsplit(".", 1)[-1].lower()
        if key_lower in _NON_EVENT_VALUE_KEYS:
            return
        if key_lower in {"x", "y", "z"} and _path_has_coordinate_context(prefix):
            return
        if key_lower not in _MARKER_VALUE_KEYS and not parent_is_markerish:
            return

        sample = _sample_marker_values(value, limit=16) if parent_is_markerish else _sample_values(value, limit=16)
        if not sample:
            return
        # Avoid huge continuous data summaries masquerading as labels.
        if len(sample) > 12 and all(_looks_numeric(v) for v in sample):
            return
        lines.append(f"{prefix} sample_values={sample}")

    for key, value in mat.items():
        if str(key).startswith("__"):
            continue
        walk(value, str(key), False, 0)
    return lines


def _path_has_coordinate_context(prefix: str) -> bool:
    parts = {tok for tok in re.split(r"[^a-z0-9]+", prefix.lower()) if tok}
    return bool(parts & _COORDINATE_CONTEXT_KEYS)


def _sample_marker_values(value: Any, limit: int = 16) -> List[str]:
    """Sample sparse marker arrays without looking only at the all-zero prefix."""
    try:
        import numpy as np
    except Exception:
        return _sample_values(value, limit=limit)
    try:
        arr = np.asarray(value)
        if arr.dtype == object or arr.size == 0 or arr.ndim > 2:
            return _sample_values(value, limit=limit)
        flat = arr.reshape(-1)
        if flat.size <= 5_000_000:
            vals = np.unique(flat)
        else:
            # For very large sparse vectors, sample across the whole recording so
            # late trigger codes are not hidden by an all-zero prefix.
            idx = np.linspace(0, flat.size - 1, num=min(200_000, flat.size), dtype=int)
            vals = np.unique(flat[idx])
        out: List[str] = []
        for item in vals[:limit]:
            text = str(item)
            if len(text) > 40:
                text = text[:37] + "..."
            out.append(text)
        return out
    except Exception:
        return _sample_values(value, limit=limit)


def _looks_numeric(text: str) -> bool:
    try:
        float(str(text))
        return True
    except Exception:
        return False


def _append_csv_evidence(lines: List[str], data_path: Path, ext_counts: Dict[str, int]) -> None:
    if ".csv" not in ext_counts:
        return
    csvs = list(_iter_sidecar_files(data_path, ("*.csv", "*.CSV"), limit=4))
    if not csvs:
        return
    lines.append("\n[CSV sidecar/header samples]")
    for p in csvs:
        lines.append(f"- {p.relative_to(data_path)}")
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            raw_lines = [ln for ln in text.splitlines() if ln.strip()]
            comments = [ln for ln in raw_lines[:12] if ln.lstrip().startswith("#")]
            table_lines = [ln for ln in raw_lines if not ln.lstrip().startswith("#")][:6]
            if comments:
                lines.append("  comments: " + " | ".join(comments[:3])[:500])
            if table_lines:
                dialect = csv.Sniffer().sniff("\n".join(table_lines[:3])) if len(table_lines) >= 2 else csv.excel
                rows = list(csv.reader(io.StringIO("\n".join(table_lines)), dialect=dialect))
                if rows:
                    lines.append(f"  header={rows[0][:12]}")
                    if len(rows) > 1:
                        lines.append(f"  first_row={rows[1][:12]}")
        except Exception as exc:
                lines.append(f"  read_error={type(exc).__name__}: {exc}")


def _append_annotation_sidecar_evidence(
    lines: List[str],
    data_path: Path,
    ext_counts: Dict[str, int],
) -> None:
    """Summarize local interval sidecars as literal event-label evidence."""
    labels: set[str] = set()
    examples: List[str] = []
    files: List[str] = []

    if ".csv" in ext_counts:
        for p in _iter_sidecar_files(data_path, ("*.csv", "*.CSV"), limit=220):
            new_labels, new_examples = _inspect_interval_csv(p, data_path)
            if new_labels or new_examples:
                labels.update(new_labels)
                examples.extend(new_examples)
                files.append(str(p.relative_to(data_path)))
            if len(examples) >= 8 and len(labels) >= 2:
                break
        if labels or examples:
            _emit_annotation_sidecar_evidence(lines, labels, examples, files)
            return

    if ".txt" in ext_counts:
        for p in _iter_sidecar_files(data_path, ("*summary.txt", "*SUMMARY.txt"), limit=40):
            new_labels, new_examples = _inspect_summary_file(p, data_path)
            if new_labels or new_examples:
                labels.update(new_labels)
                examples.extend(new_examples)
                files.append(str(p.relative_to(data_path)))
            if len(examples) >= 8 and len(labels) >= 1:
                break
        if labels or examples:
            _emit_annotation_sidecar_evidence(lines, labels, examples, files)
            return

    if ".tse" in ext_counts or ".tse_bi" in ext_counts or ".lbl" in ext_counts or ".lbl_bi" in ext_counts:
        for p in _iter_sidecar_files(data_path, ("*.tse", "*.tse_bi", "*.lbl", "*.lbl_bi"), limit=40):
            new_labels, new_examples = _inspect_token_interval_file(p, data_path)
            if new_labels or new_examples:
                labels.update(new_labels)
                examples.extend(new_examples)
                files.append(str(p.relative_to(data_path)))
            if len(examples) >= 8 and len(labels) >= 2:
                break
        if labels or examples:
            _emit_annotation_sidecar_evidence(lines, labels, examples, files)
            return

    if ".seizures" not in ext_counts:
        return
    seizure_files = list(_iter_sidecar_files(data_path, ("*.edf.seizures",), limit=8))
    if seizure_files:
        labels.add("seizure")
        for p in seizure_files[:3]:
            files.append(str(p.relative_to(data_path)))
            examples.append(f"{p.relative_to(data_path)}: companion .edf.seizures file present")

    _emit_annotation_sidecar_evidence(lines, labels, examples, files)


def _emit_annotation_sidecar_evidence(
    lines: List[str],
    labels: set[str],
    examples: List[str],
    files: List[str],
) -> None:
    if not labels and not examples:
        return

    lines.append("\n[External annotation interval sidecars]")
    if labels:
        lines.append(f"external_annotation_labels: {sorted(labels)[:20]}")
    if files:
        lines.append("sample_sidecar_files: " + ", ".join(files[:8]))
    selected: List[str] = []
    seen_labels: set[str] = set()
    for ex in examples:
        label = ex.rsplit("label=", 1)[-1] if "label=" in ex else ""
        if label and label not in seen_labels:
            selected.append(ex)
            seen_labels.add(label)
    for ex in examples:
        if len(selected) >= 10:
            break
        if ex not in selected:
            selected.append(ex)
    for ex in selected[:10]:
        lines.append(f"  interval_example: {ex}")


def _iter_sidecar_files(data_path: Path, patterns: Iterable[str], limit: int) -> Iterable[Path]:
    seen: set[Path] = set()
    count = 0
    for pattern in patterns:
        for p in data_path.rglob(pattern):
            if not p.is_file() or p in seen:
                continue
            seen.add(p)
            yield p
            count += 1
            if count >= limit:
                return


def _inspect_interval_csv(path: Path, data_path: Path) -> tuple[set[str], List[str]]:
    labels: set[str] = set()
    examples_by_label: Dict[str, str] = {}
    try:
        raw_lines = [
            ln for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        if not raw_lines:
            return labels, []
        try:
            dialect = csv.Sniffer().sniff("\n".join(raw_lines[:5]))
        except Exception:
            dialect = csv.excel
        reader = csv.DictReader(io.StringIO("\n".join(raw_lines)), dialect=dialect)
        if not reader.fieldnames:
            return labels, examples
        field_map = {str(f).strip().lower(): f for f in reader.fieldnames if f}
        label_key = _first_present(field_map, ("label", "annotation", "event", "type", "class", "description"))
        start_key = _first_present(field_map, ("start_time", "start", "onset", "onset_sec", "begin"))
        stop_key = _first_present(field_map, ("stop_time", "stop", "end", "end_time", "offset"))
        if not label_key or not start_key:
            return labels, examples
        for i, row in enumerate(reader):
            label = _clean_label(row.get(label_key, ""))
            if not label:
                continue
            labels.add(label)
            if label not in examples_by_label and len(examples_by_label) < 8:
                start = str(row.get(start_key, "")).strip()
                stop = str(row.get(stop_key, "")).strip() if stop_key else ""
                rel = path.relative_to(data_path)
                examples_by_label[label] = f"{rel}: start={start}, stop={stop}, label={label}"
            if i >= 1000 and len(labels) >= 2:
                break
    except Exception:
        return labels, list(examples_by_label.values())
    return labels, list(examples_by_label.values())


def _inspect_token_interval_file(path: Path, data_path: Path) -> tuple[set[str], List[str]]:
    labels: set[str] = set()
    examples: List[str] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "version", "symbols")):
                continue
            parts = stripped.split()
            if len(parts) < 3 or not _looks_numeric(parts[0]) or not _looks_numeric(parts[1]):
                continue
            label = _clean_label(parts[2])
            if not label:
                continue
            labels.add(label)
            if len(examples) < 4:
                examples.append(f"{path.relative_to(data_path)}: start={parts[0]}, stop={parts[1]}, label={label}")
            if len(labels) >= 4 and len(examples) >= 4:
                break
    except Exception:
        return labels, examples
    return labels, examples


def _inspect_summary_file(path: Path, data_path: Path) -> tuple[set[str], List[str]]:
    labels: set[str] = set()
    examples: List[str] = []
    try:
        current_file = ""
        starts: List[tuple[str, str, bool]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m_file = re_match(r"File Name:\s*(\S+)", line)
            if m_file:
                current_file = m_file
                starts = []
                continue
            m_start = re_match(r"Seizure\s+(\d+)\s+Start Time:\s*([0-9.]+)", line)
            if m_start and current_file:
                idx, start = m_start.split(":", 1)
                starts.append((idx, start, False))
                labels.add("seizure")
                continue
            m_end = re_match(r"Seizure\s+(\d+)\s+End Time:\s*([0-9.]+)", line)
            if m_end and current_file:
                idx, stop = m_end.split(":", 1)
                start = ""
                for pos, (start_idx, start_value, used) in enumerate(starts):
                    if not used and start_idx == idx:
                        start = start_value
                        starts[pos] = (start_idx, start_value, True)
                        break
                if not start:
                    for pos, (start_idx, start_value, used) in enumerate(starts):
                        if not used:
                            start = start_value
                            starts[pos] = (start_idx, start_value, True)
                            break
                labels.add("seizure")
                if start and len(examples) < 4:
                    examples.append(
                        f"{path.relative_to(data_path)} -> {current_file}: "
                        f"start={start}, stop={stop}, label=seizure"
                    )
            if len(examples) >= 4:
                break
    except Exception:
        return labels, examples
    return labels, examples


def _first_present(field_map: Dict[str, str], names: Iterable[str]) -> Optional[str]:
    for name in names:
        if name in field_map:
            return field_map[name]
    return None


def _clean_label(value: Any) -> str:
    text = " ".join(str(value).strip().split())
    return text[:80] if text else ""


def re_match(pattern: str, text: str) -> str:
    import re

    match = re.search(pattern, text)
    if not match:
        return ""
    if len(match.groups()) == 1:
        return match.group(1)
    return ":".join(match.groups())


def _append_text_evidence(lines: List[str], data_path: Path) -> None:
    names = ("README", "README.md", "README.txt", "readme.txt", "description.txt", "1Description.txt")
    candidates = [data_path / name for name in names if (data_path / name).exists()]
    if not candidates:
        return
    lines.append("\n[Local text documentation snippets]")
    for p in candidates[:2]:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")[:1000]
        except Exception as exc:
            text = f"[read_error: {exc}]"
        rel = p.relative_to(data_path) if data_path in p.parents or p.parent == data_path else p
        lines.append(f"- {rel}\n{text}")
