"""task_h5_builder.py — Build a task-ready v2 HDF5 for one (dataset, task) pair.

This is the core of the export utility. It bridges the NeuroDoc analysis
documents (``dataset_document/<dataset>/analysis.md``) and EEGUnity's epoch
exporters, then caches the result EEG2-style under ``<cache_dir>``.

Flow for one job:
    1. Resolve raw path (config raw_path / dataset_roots) and kernel.
    2. Parse the target Task block from analysis.md (Epoch Method, Epoch
       Parameters, Label Route, Target Definition) — finest scope wins for
       processing params, resolved by the caller.
    3. Compute config_key (epoch method + epoch params + pipeline + channel
       space signature) and check the on-disk cache.
    4. On miss: build a kernel-applied UnifiedDataset and call the matching
       ``epoch_by_*_hdf5`` (pipeline = user pipeline -> common-channel align),
       or the NeuroDoc misc route for ``/misc_meta`` targets.
    5. Read the HDF5 back for a lightweight validation summary.

The output HDF5 is the EEGUnity v2 layout consumed by ``neurodoc.dataset_api``:
    /data (N, n_ch, n_times), /epoch_meta/{event_code,source_group},
    /source_meta/<group>/attrs, root attrs {version, ch_names, label_map}.

Channel handling
----------------
* ``common_channels`` is None -> no alignment; the kernel must already yield a
  uniform channel count (EEGUnity raises otherwise). That failure is surfaced.
* ``common_channels`` is a list -> each recording is aligned to exactly that
  set in the pipeline (missing channels interpolated, extras dropped), giving a
  uniform flat HDF5. A task whose recordings have no overlap with the requested
  set is skipped with a detailed log instead of crashing the batch.
"""
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
import sys
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# NeuroDoc package paths (this file lives in neurodoc/utils/).
NEURODOC_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = NEURODOC_DIR.parent                      # EEGBenchmarkSKILL/
DATASET_DOCUMENT_DIR = ROOT_DIR / "dataset_document"
KERNELS_DIR = NEURODOC_DIR / "kernels"
DEFAULT_EEGUNITY_PATH = str(ROOT_DIR / "Script")    # parent of the `eegunity` package

# Epoch method -> required epoch-param keys (after merging doc defaults + overrides).
REQUIRED_EPOCH_PARAMS: Dict[str, set] = {
    "epoch_by_event_hdf5":        {"tmin", "tmax"},
    "epoch_by_segmentation_hdf5": {"segment_length", "overlap"},
    "epoch_by_long_event_hdf5":   {"tmin", "tmax", "overlap"},
}
_METHOD_PREFIX = {
    "epoch_by_event_hdf5": "evt",
    "epoch_by_segmentation_hdf5": "seg",
    "epoch_by_long_event_hdf5": "long",
}


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class JobResult:
    dataset: str
    task: int
    status: str                       # 'success' | 'cached' | 'skipped' | 'failed'
    reason: str = ""
    hdf5_path: Optional[str] = None
    config_key: Optional[str] = None
    n_epochs: Optional[int] = None
    summary: Dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status in ("success", "cached")


class TaskSkip(Exception):
    """Raised to skip a task with a human-readable reason (not a hard failure)."""


# ---------------------------------------------------------------------------
# analysis.md parsing  (mirrors the small helpers in neurodoc/detect.py)
# ---------------------------------------------------------------------------

def _split_task_blocks(tasks_text: str) -> List[str]:
    parts = re.split(
        r"(?=^###\s+(?:Classical|Potential)\s+Task\s+\d+)",
        tasks_text, flags=re.MULTILINE,
    )
    return [p for p in parts if re.match(r"###\s+(Classical|Potential)\s+Task", p)]


def _tasks_section(analysis_text: str) -> str:
    m = re.search(r"^##\s+Tasks\s*$", analysis_text, flags=re.MULTILINE)
    if not m:
        return ""
    rest = analysis_text[m.end():]
    end = re.search(r"^##\s+\S", rest, flags=re.MULTILINE)
    return rest[: end.start()] if end else rest


def _task_field(block: str, field_name: str) -> str:
    m = re.search(rf"-\s*\*\*{re.escape(field_name)}\*\*\s*:\s*([^\n]*)", block)
    if not m:
        return ""
    return m.group(1).strip().strip("`").strip()


def _task_title(block: str) -> str:
    m = re.match(r"###\s+([^\n]+)", block)
    return m.group(1).strip() if m else "(unnamed)"


def _target_def_table(block: str) -> Tuple[List[str], List[List[str]]]:
    lines = block.splitlines()
    in_td = seen_header = False
    header: List[str] = []
    body: List[List[str]] = []
    for line in lines:
        s = line.strip()
        if s.startswith("- **Target Definition**"):
            in_td = True
            continue
        if in_td:
            if s.startswith("- **") and not s.startswith("|"):
                break
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if all(re.fullmatch(r":?-+:?", c or "") for c in cells if c):
                    continue
                if not seen_header:
                    header, seen_header = cells, True
                else:
                    body.append(cells)
    return header, body


def _normalize_header(cells: List[str]) -> List[str]:
    out = []
    for c in cells:
        c = c.lower().strip()
        c = re.sub(r"\s*\([^)]*\)", "", c).strip()
        out.append(c)
    return out


_NUM_RE = r"[-+]?\d+(?:\.\d+)?"


def parse_epoch_params_text(text: str) -> Dict[str, float]:
    """Extract the first tmin/tmax/overlap/segment_length from free Epoch Parameters text.

    Tolerates units ('s'), asterisks, and multi-phase descriptions (takes the
    first occurrence of each key). Returns floats. Missing keys are simply
    absent; the caller validates against the epoch method's requirements.
    """
    out: Dict[str, float] = {}
    for key in ("segment_length", "tmin", "tmax", "overlap"):
        m = re.search(rf"\b{key}\s*=\s*({_NUM_RE})", text)
        if m:
            out[key] = float(m.group(1))
    # Fallback: some docs write bare "length = N" for the segment window.
    if "segment_length" not in out:
        m = re.search(rf"\blength\s*=\s*({_NUM_RE})", text)
        if m:
            out["segment_length"] = float(m.group(1))
    return out


def parse_target_events_text(text: str) -> List[str]:
    """Extract target_events=[...] from free Epoch Parameters text."""
    m = re.search(r"\btarget_events\s*=\s*\[([^\]]*)\]", text)
    if not m:
        return []
    events: List[str] = []
    for raw in m.group(1).split(","):
        val = raw.strip().strip("`").strip("'\"").strip()
        if val:
            events.append(val)
    return events


@dataclass
class TaskSpec:
    index: int
    title: str
    epoch_method: str
    label_route: Optional[str]
    task_type: Optional[str]
    label_field: Optional[str]
    target_rows: List[Dict]
    doc_epoch_params: Dict[str, float]
    target_events: List[str]


def load_task_spec(dataset: str, task_index: int) -> TaskSpec:
    """Parse the `task_index`-th (1-based, document order) Task block."""
    doc = DATASET_DOCUMENT_DIR / dataset / "analysis.md"
    if not doc.exists():
        raise TaskSkip(f"analysis.md not found: {doc}")
    text = doc.read_text(encoding="utf-8")
    blocks = _split_task_blocks(_tasks_section(text))
    if not blocks:
        raise TaskSkip(f"no Task blocks found in {doc}")
    if task_index < 1 or task_index > len(blocks):
        raise TaskSkip(
            f"task index {task_index} out of range (document has {len(blocks)} task(s))"
        )
    block = blocks[task_index - 1]

    epoch_method = _task_field(block, "Epoch Method")
    if epoch_method not in REQUIRED_EPOCH_PARAMS:
        raise TaskSkip(
            f"unsupported or missing Epoch Method {epoch_method!r} "
            f"(expected one of {sorted(REQUIRED_EPOCH_PARAMS)})"
        )

    route = (_task_field(block, "Label Route") or "").lower() or None
    ttype = (_task_field(block, "Task Type") or "").lower() or None

    header, body = _target_def_table(block)
    norm = _normalize_header(header) if header else []
    rows: List[Dict] = []
    label_field: Optional[str] = None
    for raw_cells in body:
        cells = [c.strip().strip("`").strip() for c in raw_cells]
        if not any(cells):
            continue
        row: Dict = {}
        for key, val in zip(norm, cells):
            if key == "event id":
                row["event_id"] = val
            elif key == "info field":
                row["info_field"] = val
                label_field = label_field or val
            elif key in ("misc channel name", "misc channel"):
                row["misc_channel"] = val
                label_field = label_field or val
            elif key == "y":
                try:
                    row["y"] = int(val)
                except (ValueError, TypeError):
                    row["y"] = val
            elif key == "value":
                row["value"] = val
            elif key == "meaning":
                row["meaning"] = val
        rows.append(row)

    epoch_params_text = _task_field(block, "Epoch Parameters")
    target_events = [r["event_id"] for r in rows if r.get("event_id")]
    if not target_events:
        target_events = parse_target_events_text(epoch_params_text)
    doc_params = parse_epoch_params_text(epoch_params_text)

    return TaskSpec(
        index=task_index,
        title=_task_title(block),
        epoch_method=epoch_method,
        label_route=route,
        task_type=ttype,
        label_field=label_field,
        target_rows=rows,
        doc_epoch_params=doc_params,
        target_events=target_events,
    )


def factory_task_dict(spec: TaskSpec) -> Dict:
    """Shape the spec into the dict consumed by dataset_api.build_dataset_from_task."""
    return {
        "label_route": spec.label_route,
        "task_type": spec.task_type,
        "label_field": spec.label_field,
        "target_rows": spec.target_rows,
    }


# ---------------------------------------------------------------------------
# Pipeline loading  (make_pipeline factory OR plain pipeline; mirrors EEG2)
# ---------------------------------------------------------------------------

def load_pipeline(
    pipeline_path: Optional[str],
    pipeline_params: Optional[Dict] = None,
) -> Tuple[Optional[Callable], str]:
    """Load a preprocessing pipeline .py file. Returns (callable_or_None, key)."""
    if not pipeline_path:
        if pipeline_params:
            raise ValueError("pipeline_param given but pipeline not specified.")
        return None, "nopipe"

    p = Path(pipeline_path)
    if not p.is_absolute():
        for base in (Path.cwd(), ROOT_DIR, NEURODOC_DIR):
            cand = base / pipeline_path
            if cand.is_file():
                p = cand
                break
    if not p.is_file():
        raise FileNotFoundError(f"Pipeline file not found: {pipeline_path}")

    stem = p.stem
    spec = importlib.util.spec_from_file_location("_user_pipeline", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    has_factory = callable(getattr(mod, "make_pipeline", None))
    has_plain = callable(getattr(mod, "pipeline", None))
    params = pipeline_params or {}

    if params:
        if not has_factory:
            raise AttributeError(
                f"pipeline_param given but '{p}' has no make_pipeline() factory."
            )
        valid = set(inspect.signature(mod.make_pipeline).parameters)
        unknown = set(params) - valid
        if unknown:
            raise ValueError(
                f"unknown pipeline_param key(s) {sorted(unknown)} for make_pipeline() "
                f"in '{p}'. Valid: {sorted(valid)}"
            )
        fn = mod.make_pipeline(**params)
        key = f"{stem}_" + "_".join(f"{k}{v}" for k, v in sorted(params.items()))
    else:
        if has_plain:
            fn = mod.pipeline
        elif has_factory:
            sig = inspect.signature(mod.make_pipeline)
            missing = [n for n, q in sig.parameters.items()
                       if q.default is inspect.Parameter.empty]
            if missing:
                raise ValueError(
                    f"make_pipeline() in '{p}' needs param(s) {missing} but none given."
                )
            fn = mod.make_pipeline()
        else:
            raise AttributeError(
                f"pipeline file '{p}' must export make_pipeline() or pipeline()."
            )
        key = stem

    if not callable(fn):
        raise TypeError(f"pipeline from '{p}' is not callable.")
    return fn, key


# ---------------------------------------------------------------------------
# Channel-space helpers
# ---------------------------------------------------------------------------

def _channel_signature(common_channels: Optional[List[str]]) -> str:
    if not common_channels:
        return "nochan"
    joined = ",".join(common_channels)
    h = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:8]
    return f"ch{len(common_channels)}-{h}"


def _eeg_channels_of_row(channel_string: str) -> List[str]:
    """EEG channel names from one locator 'Channel Names' cell (typed via eegunity)."""
    from eegunity.modules.parser.eeg_parser import channel_name_parser
    formatted = channel_name_parser(str(channel_string))
    out, seen = [], set()
    for entry in formatted.split(","):
        entry = entry.strip()
        if ":" not in entry:
            continue
        prefix, name = entry.split(":", 1)
        if prefix.strip().lower() != "eeg":
            continue
        name = name.strip()
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            out.append(name)
    return out


_CH_TYPE_PREFIXES = {"eeg", "eog", "emg", "ecg", "meg", "misc", "stim",
                     "ref", "seeg", "ecog", "dbs", "bio", "resp", "temp"}


def _normalize_ch_name(name: str) -> str:
    """Strip a leading channel-type token so raw names match locator-parsed ones.

    EEGUnity's locator stores ``type:channel`` and the exporter compares on the
    bare ``channel``; raw MNE objects often keep the type as a word prefix
    (e.g. ``"EEG F4-M1"``). Drop a leading ``EEG ``/``EOG ``/... token so the two
    forms line up. Names without such a prefix are returned unchanged.
    """
    name = str(name).strip()
    parts = name.split(" ", 1)
    if len(parts) == 2 and parts[0].casefold() in _CH_TYPE_PREFIXES:
        return parts[1].strip()
    return name


def _all_channels_of_row(channel_string: str) -> List[str]:
    """All channel names from one locator 'Channel Names' cell (any type), ordered.

    Unlike `_eeg_channels_of_row` this keeps every channel (EEG/MISC/EOG/...),
    using the name after the ``type:`` prefix when present. Used by the
    ``auto`` common-channel intersection so it works for clinical / sleep
    montages whose channels EEGUnity does not type as ``eeg``.
    """
    from eegunity.modules.parser.eeg_parser import channel_name_parser
    formatted = channel_name_parser(str(channel_string))
    out, seen = [], set()
    for entry in formatted.split(","):
        entry = entry.strip()
        if not entry:
            continue
        name = entry.split(":", 1)[1].strip() if ":" in entry else entry
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            out.append(name)
    return out


def _common_channels_intersection(locator_df, log: Callable) -> List[str]:
    """Channel names present in EVERY available recording, ordered by the first.

    This is the ``common_channels: auto`` channel space — each dataset exports
    exactly the channels its recordings share, with no interpolation. Returns
    an empty list when the recordings share no channel (caller skips the task).
    """
    available = locator_df[locator_df["Completeness Check"].astype(str) != "Unavailable"]
    common_keys = None
    order: List[str] = []
    seen_order = set()
    for _, row in available.iterrows():
        chans = _all_channels_of_row(row.get("Channel Names", ""))
        keys = {c.casefold() for c in chans}
        common_keys = keys if common_keys is None else (common_keys & keys)
        for c in chans:
            if c.casefold() not in seen_order:
                seen_order.add(c.casefold())
                order.append(c)
    if not common_keys:
        return []
    return [c for c in order if c.casefold() in common_keys]


def _dominant_channels(locator_df, min_fraction: float, log: Callable
                       ) -> Tuple[List[str], int, int]:
    """Channels shared by a MAJORITY of recordings (>= min_fraction), ordered.

    Strict all-file intersection is brittle: one outlier recording (a dummy
    channel like '0'/'1', a typo, or a different recording cohort) empties it.
    Instead keep channels present in at least ``min_fraction`` of available
    recordings, ordered by the recording that best matches that set. The caller
    then drops the minority recordings that lack a selected channel so the flat
    HDF5 stays uniform. Returns (channels, kept_file_count_estimate, n_available).
    """
    available = locator_df[locator_df["Completeness Check"].astype(str) != "Unavailable"]
    n = len(available)
    if n == 0:
        return [], 0, 0
    per_file = [_all_channels_of_row(r.get("Channel Names", "")) for _, r in available.iterrows()]
    freq: Counter = Counter()
    for ch in per_file:
        for k in {c.casefold() for c in ch}:
            freq[k] += 1
    threshold = max(1, int(round(min_fraction * n)))
    keep_keys = {k for k, v in freq.items() if v >= threshold}
    if not keep_keys:
        return [], 0, n
    # Order by the recording with the most overlap with keep_keys.
    best = max(per_file, key=lambda ch: len({c.casefold() for c in ch} & keep_keys))
    selected, seen = [], set()
    for c in best:
        k = c.casefold()
        if k in keep_keys and k not in seen:
            seen.add(k)
            selected.append(c)
    n_kept = sum(1 for ch in per_file
                 if keep_keys <= {c.casefold() for c in ch} or
                 {c.casefold() for c in ch} >= seen)
    return selected, n_kept, n


def _preflight_common_channels(locator_df, common_channels: List[str],
                               min_matched: int, log: Callable) -> None:
    """Raise TaskSkip if no available recording overlaps the common channel space."""
    import pandas as pd  # noqa: F401  (locator_df is a DataFrame)

    want = {c.casefold() for c in common_channels}
    available = locator_df[locator_df["Completeness Check"].astype(str) != "Unavailable"]
    best = 0
    union: set = set()
    for _, row in available.iterrows():
        chans = _eeg_channels_of_row(row.get("Channel Names", ""))
        union.update(chans)
        matched = len({c.casefold() for c in chans} & want)
        best = max(best, matched)
    if best < min_matched:
        log(f"    dataset EEG channels (union): {sorted(union)}")
        log(f"    requested common_channels:    {common_channels}")
        log(f"    intersection is empty (best match {best} < min {min_matched}).")
        raise TaskSkip(
            f"no recording overlaps the requested common channel space "
            f"(best match {best} < min_matched {min_matched})"
        )


def _make_combined_pipeline(user_pipeline: Optional[Callable],
                            common_channels: Optional[List[str]],
                            min_matched: int,
                            pick_only: bool = False,
                            preserve_label_channels: bool = False) -> Optional[Callable]:
    """Compose user pipeline with channel handling.

    pick_only=True  -> just select `common_channels` in order (no interpolation);
                       used by ``auto`` (the channels are the across-file
                       intersection, guaranteed present). Montage-agnostic.
    pick_only=False -> align to `common_channels` (interpolate missing) then pick;
                       used for an explicit standard-montage channel list.
    """
    if user_pipeline is None and not common_channels:
        return None

    def _label_channel_names(raw) -> List[str]:
        from eegunity.utils.label_channel import misc_channel_indices, stim_channel_indices
        idx = sorted(set(misc_channel_indices(raw)) | set(stim_channel_indices(raw)))
        return [raw.ch_names[i] for i in idx]

    def _pipe(raw):
        if user_pipeline is not None:
            raw = user_pipeline(raw)
        if common_channels:
            if pick_only:
                # Map target names (locator-parsed, type prefix stripped, e.g.
                # "F4-M1") back to raw ch_names which often keep the type word
                # ("EEG F4-M1"). Match on the normalised name.
                raw_map = {}
                for c in raw.ch_names:
                    raw_map.setdefault(_normalize_ch_name(c).casefold(), c)
                sel = [raw_map[c.casefold()] for c in common_channels
                       if c.casefold() in raw_map]
                if preserve_label_channels:
                    sel.extend(ch for ch in _label_channel_names(raw) if ch not in sel)
                raw.pick_channels(sel, ordered=True)
            else:
                from eegunity.utils import channel_align_raw
                raw = channel_align_raw(raw, list(common_channels),
                                        min_matched_channel=min_matched)
                keep = list(common_channels)
                if preserve_label_channels:
                    keep.extend(ch for ch in _label_channel_names(raw) if ch not in keep)
                raw.pick_channels(keep, ordered=True)
        return raw

    return _pipe


def _make_target_event_priority_pipeline(
    pipeline: Optional[Callable],
    target_events: List[str],
) -> Optional[Callable]:
    """Prefer requested target annotations when multiple events share an onset."""
    if not target_events:
        return pipeline

    target_set = {str(e) for e in target_events}

    def _pipe(raw):
        if pipeline is not None:
            raw = pipeline(raw)
        annotations = getattr(raw, "annotations", None)
        if annotations is None or len(annotations) == 0:
            return raw

        sfreq = float(raw.info.get("sfreq") or 1.0)
        buckets: Dict[int, List[int]] = {}
        for idx, onset in enumerate(annotations.onset):
            buckets.setdefault(int(round(float(onset) * sfreq)), []).append(idx)

        keep: List[int] = []
        changed = False
        for indices in buckets.values():
            target_indices = [
                idx for idx in indices
                if str(annotations.description[idx]) in target_set
            ]
            if target_indices:
                keep.append(target_indices[0])
                changed = changed or len(indices) != 1 or indices[0] != target_indices[0]
            else:
                keep.extend(indices)

        if not changed:
            return raw

        keep = sorted(keep)
        raw.set_annotations(type(annotations)(
            onset=[float(annotations.onset[idx]) for idx in keep],
            duration=[float(annotations.duration[idx]) for idx in keep],
            description=[str(annotations.description[idx]) for idx in keep],
            orig_time=annotations.orig_time,
        ))
        return raw

    return _pipe


def _canonical_misc_name(ch_name: str) -> str:
    ch_name = str(ch_name)
    return ch_name[len("misc:"):] if ch_name.startswith("misc:") else ch_name


def _misc_reducer_for(name: str) -> str:
    """Choose a conservative per-epoch reducer for known misc labels."""
    if _canonical_misc_name(name).casefold() in {"apnea_label"}:
        return "max"
    return "mean"


def _reduce_misc_epochs(values, reducer: str):
    import numpy as np

    arr = np.asarray(values, dtype=np.float64)
    finite = np.isfinite(arr)
    out = np.full(arr.shape[0], np.nan, dtype=np.float32)
    has_value = finite.any(axis=1)
    if not has_value.any():
        return out

    if reducer == "max":
        masked = np.where(finite, arr, -np.inf)
        out[has_value] = masked.max(axis=1)[has_value].astype(np.float32)
    else:
        sums = np.where(finite, arr, 0.0).sum(axis=1)
        counts = finite.sum(axis=1)
        out[has_value] = (sums[has_value] / counts[has_value]).astype(np.float32)
    return out


def _extract_source_attrs(raw, row) -> dict:
    """Extract scalar source metadata for HDF5 /source_meta attrs."""
    attrs = {"file_path": str(row.get("File Path", "unknown"))}
    try:
        desc = json.loads(raw.info.get("description", "{}"))
        eu = desc.get("eegunity_description", {})
        attrs["age"] = eu.get("age", "unknown")
        attrs["gender"] = eu.get("sex", "unknown")
        attrs["amplifier"] = eu.get("amplifier", "unknown")
        attrs["cap"] = eu.get("cap", "unknown")
        attrs["handedness"] = eu.get("handedness", "unknown")
        for key, value in eu.items():
            if key not in attrs and value is not None:
                attrs[key] = value
    except Exception:
        for key in ("age", "gender", "amplifier", "cap", "handedness"):
            attrs[key] = "unknown"
    return attrs


def _split_epoch_data_and_misc(epochs_obj, required_misc: List[str]):
    """Return input epoch data, input names, misc_values, and input-only Info."""
    import mne

    all_data = epochs_obj.get_data()
    required = {_canonical_misc_name(name).casefold() for name in required_misc if name}
    input_idx: List[int] = []
    misc_values: Dict[str, object] = {}

    for idx, name in enumerate(epochs_obj.ch_names):
        canonical = _canonical_misc_name(name)
        try:
            ch_type = mne.channel_type(epochs_obj.info, idx)
        except Exception:
            ch_type = ""
        is_misc = (
            ch_type == "misc"
            or str(name).startswith("misc:")
            or canonical.casefold() in required
        )
        if is_misc:
            misc_values[canonical] = _reduce_misc_epochs(
                all_data[:, idx, :], _misc_reducer_for(canonical))
            continue
        if ch_type == "stim":
            continue
        input_idx.append(idx)

    if not input_idx:
        raise ValueError("no input channels remain after removing misc/stim label channels.")

    input_data = all_data[:, input_idx, :]
    input_names = [epochs_obj.ch_names[i] for i in input_idx]
    input_info = mne.pick_info(epochs_obj.info, input_idx, copy=True)
    return input_data, input_names, misc_values, input_info


def _write_misc_epoch_block(dataset_writer, raw, row, group_name: str,
                            event_name: str, epochs_obj, required_misc: List[str]) -> int:
    import pickle

    epoch_data, ch_names, misc_values, input_info = _split_epoch_data_and_misc(
        epochs_obj, required_misc)
    if epoch_data.ndim != 3 or epoch_data.shape[0] == 0:
        return 0

    dataset_writer.add_epochs(
        group_name=group_name,
        event_name=event_name,
        epoch_data=epoch_data,
        info_bytes=pickle.dumps(input_info),
        source_attrs=_extract_source_attrs(raw, row),
        sfreq=raw.info["sfreq"],
        ch_names=ch_names,
        misc_values=misc_values,
    )
    return int(epoch_data.shape[0])


def _load_raw_for_misc_export(ud, row):
    """Load raw data, falling back to kernels that handle parser-unavailable rows."""
    try:
        return ud.eeg_batch._get_data_row(row)
    except Exception as first_exc:
        from eegunity.modules.parser.eeg_parser import apply_dataset_kernel_unavailable

        raw = apply_dataset_kernel_unavailable(ud, row)
        if raw is None:
            raise first_exc
        return raw


def _misc_epoch_params(epoch_params: Dict) -> Dict:
    params = dict(epoch_params)
    params.setdefault("picks", "all")
    params.setdefault("event_repeated", "drop")
    return params


def _export_misc_event_file(dataset_writer, raw, row, spec: TaskSpec,
                            epoch_params: Dict, required_misc: List[str]) -> int:
    import mne
    from eegunity.modules.parser.eeg_parser import extract_events

    events, event_id = extract_events(raw)
    if events is None or len(events) == 0:
        return 0
    epochs = mne.Epochs(raw, events, event_id, **_misc_epoch_params(epoch_params))
    epochs.drop_bad()

    file_name = os.path.splitext(os.path.basename(row["File Path"]))[0]
    written = 0
    for event in event_id:
        if spec.target_events and event not in spec.target_events:
            continue
        written += _write_misc_epoch_block(
            dataset_writer, raw, row, file_name, event, epochs[event], required_misc)
    return written


def _export_misc_segmentation_file(dataset_writer, raw, row, epoch_params: Dict,
                                   segment_params: Dict, required_misc: List[str]) -> int:
    import mne
    import numpy as np

    sfreq = float(raw.info["sfreq"])
    segment_length = float(segment_params["segment_length"])
    overlap = float(segment_params["overlap"])
    if segment_length <= 0:
        raise ValueError("segment_length must be positive.")
    if not 0.0 <= overlap < 1.0:
        raise ValueError("overlap must be between 0.0 and less than 1.0.")

    window_size = int(segment_length * sfreq)
    step_size = int(window_size * (1 - overlap))
    if window_size <= 0 or step_size <= 0:
        raise ValueError(
            f"invalid segmentation window/step: window={window_size}, step={step_size}."
        )
    if raw.n_times < window_size:
        return 0

    onset_samples = np.arange(0, raw.n_times - window_size + 1, step_size)
    events = np.zeros((len(onset_samples), 3), dtype=int)
    events[:, 0] = onset_samples
    events[:, 2] = 1
    event_id = {"Segment": 1}
    epochs = mne.Epochs(
        raw, events, event_id, tmin=0, tmax=segment_length,
        **_misc_epoch_params(epoch_params))
    epochs.drop_bad()

    file_name = os.path.splitext(os.path.basename(row["File Path"]))[0]
    return _write_misc_epoch_block(
        dataset_writer, raw, row, file_name, "Segment", epochs, required_misc)


def _export_misc_long_event_file(dataset_writer, raw, row, spec: TaskSpec,
                                 epoch_params: Dict, overlap: float,
                                 required_misc: List[str]) -> int:
    import mne
    import numpy as np

    if not 0.0 <= overlap < 1.0:
        raise ValueError("overlap must be between 0.0 and less than 1.0.")
    annotations = raw.annotations
    if annotations is None or len(annotations) == 0:
        return 0

    t_min = float(epoch_params.get("tmin", 0.0))
    t_max = float(epoch_params.get("tmax", 1.0))
    epoch_length = t_max - t_min
    if epoch_length <= 0:
        raise ValueError("tmax must be greater than tmin for long-event epoching.")
    step = epoch_length * (1 - overlap)
    if step <= 0:
        raise ValueError("long-event step size must be positive.")

    target_set = {str(e) for e in spec.target_events}
    temp_annotations = []
    eps = max(1e-9, 1.0 / max(float(raw.info.get("sfreq") or 1.0), 1.0))
    for onset, duration, description in zip(
            annotations.onset, annotations.duration, annotations.description):
        description = str(description)
        if target_set and description not in target_set:
            continue
        duration = float(duration)
        if duration + eps < epoch_length:
            continue
        n_segments = int(np.floor((max(0.0, duration - epoch_length) + eps) / step)) + 1
        for i in range(n_segments):
            temp_annotations.append((float(onset) + i * step, epoch_length, description))

    if not temp_annotations:
        return 0

    raw.set_annotations(mne.Annotations(
        onset=[a[0] for a in temp_annotations],
        duration=[a[1] for a in temp_annotations],
        description=[a[2] for a in temp_annotations],
    ))
    events, event_id = mne.events_from_annotations(raw)
    epochs = mne.Epochs(raw, events, event_id, **_misc_epoch_params(epoch_params))
    epochs.drop_bad()

    file_name = os.path.splitext(os.path.basename(row["File Path"]))[0]
    written = 0
    for event in event_id:
        if target_set and event not in target_set:
            continue
        written += _write_misc_epoch_block(
            dataset_writer, raw, row, file_name, event, epochs[event], required_misc)
    return written


def _build_misc_route_hdf5(*, ud, spec: TaskSpec, epoch_params: Dict,
                           task_dir: Path, config_key: str,
                           pipeline: Optional[Callable], log: Callable) -> int:
    """Build a v2.1 HDF5 for Label Route=misc without changing EEGUnity's public API."""
    from eegunity.utils.h5 import h5EpochDatasetV2

    dataset_writer = h5EpochDatasetV2(Path(task_dir), name=config_key)
    live = ud.get_shared_attr()["locator"]
    available = live[live["Completeness Check"].astype(str) != "Unavailable"]
    required_misc = [spec.label_field] + [
        row.get("misc_channel") for row in spec.target_rows if row.get("misc_channel")
    ]

    total_written = 0
    failed = 0
    for _, row in available.iterrows():
        try:
            raw = _load_raw_for_misc_export(ud, row)
            if pipeline is not None:
                raw = pipeline(raw)

            if spec.epoch_method == "epoch_by_event_hdf5":
                written = _export_misc_event_file(
                    dataset_writer, raw, row, spec, epoch_params, required_misc)
            elif spec.epoch_method == "epoch_by_segmentation_hdf5":
                written = _export_misc_segmentation_file(
                    dataset_writer, raw, row,
                    {"baseline": None},
                    {"segment_length": epoch_params["segment_length"],
                     "overlap": epoch_params["overlap"]},
                    required_misc)
            else:
                long_epoch_params = {
                    "tmin": epoch_params["tmin"],
                    "tmax": epoch_params["tmax"],
                    "baseline": None if epoch_params["tmin"] >= 0 else (None, 0),
                    "event_repeated": "drop",
                }
                written = _export_misc_long_event_file(
                    dataset_writer, raw, row, spec, long_epoch_params,
                    float(epoch_params["overlap"]), required_misc)
            total_written += written
        except Exception as exc:  # noqa: BLE001 - keep batch export tolerant
            failed += 1
            log(f"    misc row skipped: {row.get('File Path', 'unknown')} :: {exc}")

    dataset_writer.save()
    if failed:
        log(f"    misc export skipped {failed} recording(s) with row-level errors")
    return total_written


# ---------------------------------------------------------------------------
# config key + paths
# ---------------------------------------------------------------------------

def compute_config_key(epoch_method: str, epoch_params: Dict,
                       pipeline_key: str, channel_sig: str,
                       max_files: Optional[int] = None) -> str:
    prefix = _METHOD_PREFIX[epoch_method]
    pstr = "_".join(f"{k}{epoch_params[k]}" for k in sorted(epoch_params))
    sample = f"n{max_files}" if max_files else "all"
    raw = f"{prefix}|{pstr}|{pipeline_key}|{channel_sig}|{sample}"
    h = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", f"{prefix}_{pipeline_key}_{channel_sig}_{sample}")
    return f"{safe}_{h}"


# ---------------------------------------------------------------------------
# file lock (POSIX, NFS/GPFS-safe)
# ---------------------------------------------------------------------------

@contextmanager
def _exclusive_lock(lock_path: str, log: Callable):
    import fcntl
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lf:
        waited = False
        try:
            fcntl.lockf(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            waited = True
            log(f"    waiting for concurrent build lock: {lock_path}")
            fcntl.lockf(lf, fcntl.LOCK_EX)
        try:
            if waited:
                log("    lock acquired, re-checking cache.")
            yield
        finally:
            fcntl.lockf(lf, fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# locator cache + UnifiedDataset
# ---------------------------------------------------------------------------

def _resolve_raw_path(dataset: str, raw_path: Optional[str],
                      dataset_roots: List[str]) -> str:
    if raw_path:
        if not os.path.isdir(raw_path):
            raise TaskSkip(f"configured raw_path is not a directory: {raw_path}")
        return raw_path
    # Mirror scan_engine.find_dataset_path (incl. openneuro_ prefix fallback).
    names = [dataset]
    if dataset.startswith("openneuro_"):
        names.append(dataset[len("openneuro_"):])
    for root in dataset_roots or []:
        for name in names:
            cand = Path(root) / name
            if cand.is_dir():
                return str(cand)
    raise TaskSkip(
        f"raw data directory not found for '{dataset}'. Set dataset_roots "
        f"(global) or raw_path (dataset scope) in the config."
    )


def _resolve_kernel(dataset: str) -> Optional[str]:
    candidates = [
        KERNELS_DIR / f"{dataset}.py",
        KERNELS_DIR / "openneuro_specific" / f"{dataset}.py",
        KERNELS_DIR / "openneuro.py" if dataset.startswith("openneuro") else None,
        KERNELS_DIR / "bids.py",
    ]
    for c in candidates:
        if c and c.exists():
            return str(c)
    return None


def _ensure_locator(dataset: str, raw_path: str, kernel_spec: Optional[str],
                    cache_dir: str, num_workers: int, log: Callable) -> str:
    """Build (once) and cache the base locator CSV for a dataset."""
    ds_dir = Path(cache_dir) / dataset
    ds_dir.mkdir(parents=True, exist_ok=True)
    locator_path = ds_dir / "locator.csv"
    if locator_path.exists():
        log(f"    locator cache hit: {locator_path}")
        return str(locator_path)

    log(f"    scanning raw data to build locator: {raw_path}")
    from eegunity import UnifiedDataset
    kwargs = dict(dataset_path=raw_path, domain_tag=dataset,
                  verbose="WARNING", num_workers=num_workers)
    if kernel_spec:
        kwargs["kernel_spec"] = kernel_spec
    ud = UnifiedDataset(**kwargs)
    ud.get_shared_attr()["locator"].to_csv(str(locator_path), index=False)
    log(f"    locator saved ({len(ud.get_shared_attr()['locator'])} files): {locator_path}")
    return str(locator_path)


def _load_kernel_object(kernel_spec: Optional[str]):
    if not kernel_spec:
        return None
    p = Path(kernel_spec)
    if not p.is_file():
        return None
    module_name = f"_neurodoc_export_kernel_{hashlib.sha1(str(p).encode('utf-8')).hexdigest()[:10]}"
    spec = importlib.util.spec_from_file_location(module_name, str(p))
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, "KERNEL", None)


def _apply_kernel_export_filter(locator_df, kernel_spec: Optional[str], log: Callable):
    """Let kernels exclude rows before export sampling/channel grouping.

    The base EEGUnity locator is intentionally format-level metadata. Some
    datasets contain parseable non-benchmark recordings beside the target EEG/PSG
    files (for example ECG-only companion files). Kernels can expose
    ``export_include_row(row) -> bool`` to mark those rows unavailable before the
    exporter picks a channel group.
    """
    kernel = _load_kernel_object(kernel_spec)
    include_row = getattr(kernel, "export_include_row", None) if kernel is not None else None
    if not callable(include_row):
        return locator_df

    if "Error" not in locator_df.columns:
        locator_df["Error"] = ""

    avail = locator_df["Completeness Check"].astype(str) != "Unavailable"
    keep = locator_df.apply(lambda row: bool(include_row(row)), axis=1)
    drop_idx = locator_df.index[avail & ~keep]
    if len(drop_idx):
        locator_df.loc[drop_idx, "Completeness Check"] = "Unavailable"
        locator_df.loc[drop_idx, "Error"] = "Excluded by kernel export_include_row"
        log(f"    kernel export filter: dropped {len(drop_idx)} recording(s)")
    return locator_df


# ---------------------------------------------------------------------------
# HDF5 validation summary  (h5py only — no torch dependency)
# ---------------------------------------------------------------------------

def _summarize_hdf5(hdf5_path: str, spec: TaskSpec) -> Dict:
    import h5py
    import numpy as np
    summary: Dict = {}
    with h5py.File(hdf5_path, "r") as f:
        data = f.get("data")
        if data is not None:
            summary["n_epochs"] = int(data.shape[0])
            summary["shape"] = tuple(int(x) for x in data.shape)
        summary["version"] = f.attrs.get("version")
        if "source_meta" in f:
            summary["n_source_groups"] = len(f["source_meta"])
        if spec.label_route == "event" and "epoch_meta/event_code" in f:
            codes = f["epoch_meta/event_code"][:]
            label_map = json.loads(f.attrs.get("label_map", "{}"))  # code->name
            name_counts = Counter(label_map.get(str(int(c)), str(int(c))) for c in codes)
            summary["event_counts"] = dict(name_counts)
            if spec.task_type == "classification":
                name_to_y = {r.get("event_id"): r.get("y") for r in spec.target_rows}
                y_counts: Counter = Counter()
                for name, n in name_counts.items():
                    y = name_to_y.get(name)
                    if y is not None:
                        y_counts[y] += n
                summary["y_distribution"] = dict(sorted(y_counts.items(),
                                                         key=lambda kv: str(kv[0])))
        if spec.label_route == "misc":
            if "misc_meta" in f:
                names = sorted(str(k) for k in f["misc_meta"].keys())
                summary["misc_channels"] = names
                counts: Dict[str, int] = {}
                for name in names:
                    values = np.asarray(f[f"misc_meta/{name}"][:], dtype=np.float64)
                    finite = np.isfinite(values)
                    counts[name] = int(finite.sum())
                    if name == spec.label_field:
                        label_stats = {"name": name, "count": int(finite.sum())}
                        if finite.any():
                            vals = values[finite]
                            label_stats.update({
                                "min": float(vals.min()),
                                "max": float(vals.max()),
                                "mean": float(vals.mean()),
                            })
                        summary["misc_label"] = label_stats
                summary["misc_counts"] = counts
    return summary


def _task_summary_failure(spec: TaskSpec, summary: Dict) -> Optional[str]:
    if spec.label_route != "misc":
        return None
    label = spec.label_field
    if not label:
        return "misc route has no label_field parsed from Target Definition."
    stats = summary.get("misc_label")
    if not stats:
        available = summary.get("misc_channels") or []
        return f"misc channel '{label}' not found under /misc_meta (available={available})."
    if int(stats.get("count") or 0) <= 0:
        return f"misc channel '{label}' has no finite labels in /misc_meta."
    return None


# ---------------------------------------------------------------------------
# Main entry: build one task
# ---------------------------------------------------------------------------

def build_task_hdf5(
    *,
    dataset: str,
    task: int,
    cache_dir: str,
    params: Dict,
    eegunity_path: Optional[str] = None,
    dataset_roots: Optional[List[str]] = None,
    raw_path: Optional[str] = None,
    num_workers: int = 8,
    rebuild: bool = False,
    max_files: Optional[int] = None,
    log: Callable = print,
) -> JobResult:
    """Build (or reuse) the v2 HDF5 for one (dataset, task). Never raises for
    expected problems — returns a JobResult with status skipped/failed instead.

    ``params`` is the already scope-resolved processing dict with keys:
        pipeline, pipeline_param, common_channels, min_matched_channels, epoch_param
    """
    # Put EEGUnity on sys.path (debug: local Script/; release: env -> leave empty).
    eu_path = eegunity_path or DEFAULT_EEGUNITY_PATH
    if eu_path and eu_path not in sys.path:
        sys.path.insert(0, eu_path)

    try:
        spec = load_task_spec(dataset, task)
        log(f"  task {task}: {spec.title}")
        log(f"    epoch_method={spec.epoch_method} route={spec.label_route} "
            f"type={spec.task_type}")

        # Resolve epoch params: doc defaults, overridden wholesale by scope epoch_param.
        epoch_params = dict(spec.doc_epoch_params)
        epoch_params.update(params.get("epoch_param") or {})
        epoch_params = {k: float(v) for k, v in epoch_params.items()}
        missing = REQUIRED_EPOCH_PARAMS[spec.epoch_method] - set(epoch_params)
        if missing:
            raise TaskSkip(
                f"epoch params {sorted(missing)} missing for {spec.epoch_method}. "
                f"Parsed from doc: {spec.doc_epoch_params}. "
                f"Set them via epoch_param in the config."
            )

        # common_channels: None | "auto" | explicit list.
        #   "auto"  -> per-dataset across-file channel intersection (pick, no
        #              interpolation); resolved after the locator is loaded.
        #   list    -> align to that standard montage (interpolate missing) + pick.
        common_channels = params.get("common_channels") or None
        channel_auto = isinstance(common_channels, str) and common_channels.lower() == "auto"
        if channel_auto:
            common_channels = None  # resolved below once the locator is known
        elif common_channels is not None and not isinstance(common_channels, list):
            raise TaskSkip("common_channels must be a list, \"auto\", or null.")
        min_matched = int(params.get("min_matched_channels") or 1)

        pipeline_fn, pipeline_key = load_pipeline(
            params.get("pipeline"), params.get("pipeline_param"))
        channel_sig = "chauto" if channel_auto else _channel_signature(common_channels)
        max_files = int(max_files) if max_files else None
        config_key = compute_config_key(spec.epoch_method, epoch_params,
                                        pipeline_key, channel_sig, max_files)

        task_dir = Path(cache_dir) / dataset / f"task{task}"
        task_dir.mkdir(parents=True, exist_ok=True)
        hdf5_path = task_dir / f"{config_key}.hdf5"

        # Fast path: cache hit.
        if hdf5_path.exists() and not rebuild:
            log(f"    cache hit: {hdf5_path}")
            summary = _summarize_hdf5(str(hdf5_path), spec)
            failure = _task_summary_failure(spec, summary)
            if failure:
                return JobResult(dataset, task, "failed", reason=failure,
                                 hdf5_path=str(hdf5_path), config_key=config_key,
                                 n_epochs=summary.get("n_epochs"), summary=summary)
            return JobResult(dataset, task, "cached", hdf5_path=str(hdf5_path),
                             config_key=config_key,
                             n_epochs=summary.get("n_epochs"), summary=summary)

        with _exclusive_lock(str(hdf5_path) + ".lock", log):
            if hdf5_path.exists() and not rebuild:
                log(f"    cache hit after lock: {hdf5_path}")
                summary = _summarize_hdf5(str(hdf5_path), spec)
                failure = _task_summary_failure(spec, summary)
                if failure:
                    return JobResult(dataset, task, "failed", reason=failure,
                                     hdf5_path=str(hdf5_path), config_key=config_key,
                                     n_epochs=summary.get("n_epochs"), summary=summary)
                return JobResult(dataset, task, "cached", hdf5_path=str(hdf5_path),
                                 config_key=config_key,
                                 n_epochs=summary.get("n_epochs"), summary=summary)

            # Resolve raw path + kernel, build/load base locator.
            resolved_raw = _resolve_raw_path(dataset, raw_path, dataset_roots or [])
            kernel_spec = _resolve_kernel(dataset)
            log(f"    kernel: {kernel_spec or '(default EEGUnity parser)'}")
            base_locator = _ensure_locator(dataset, resolved_raw, kernel_spec,
                                           cache_dir, num_workers, log)

            import pandas as pd
            locator_df = pd.read_csv(base_locator)
            locator_df = _apply_kernel_export_filter(locator_df, kernel_spec, log)

            kernel_obj = _load_kernel_object(kernel_spec)
            if bool(getattr(kernel_obj, "HANDLES_UNAVAILABLE", False)):
                include_row = getattr(kernel_obj, "export_include_row", None)
                if callable(include_row):
                    can_load = locator_df.apply(lambda row: bool(include_row(row)), axis=1)
                else:
                    can_load = locator_df["File Path"].astype(str).str.len() > 0
                unavailable = locator_df["Completeness Check"].astype(str) == "Unavailable"
                promote_idx = locator_df.index[unavailable & can_load]
                if len(promote_idx):
                    locator_df.loc[promote_idx, "Completeness Check"] = "Completed"
                    log(f"    kernel handles unavailable rows: allowing "
                        f"{len(promote_idx)} recording(s) for export load()")

            # Optional sampling: keep the first N available recordings (testing /
            # quick smoke runs). Folded into config_key so it caches separately.
            # If the scan marked every recording Unavailable there is nothing to
            # epoch. Report it with the extension breakdown so the cause (parse
            # failures, environment issues, etc.) is visible.
            avail = locator_df[locator_df["Completeness Check"].astype(str) != "Unavailable"]
            if avail.shape[0] == 0:
                all_exts = Counter(os.path.splitext(str(p))[1].lower()
                                   for p in locator_df.get("File Path", []))
                raise TaskSkip(
                    f"no available recordings: all {len(locator_df)} file(s) failed the "
                    f"scan/completeness check (extensions = {dict(all_exts)}). "
                    f"Check the kernel and the EEGUnity/MNE environment for this format."
                )

            if max_files:
                avail_mask = locator_df["Completeness Check"].astype(str) != "Unavailable"
                keep_idx = locator_df[avail_mask].head(max_files).index
                locator_df = locator_df.loc[keep_idx].reset_index(drop=True)
                log(f"    sampling first {len(locator_df)} available file(s) (max_files={max_files})")

            # Resolve "auto" channel space = intersection of channels present in
            # every available recording (each dataset exports the channels it
            # actually shares). pick-only -> works for any montage.
            pick_only = False
            # Explicit common-channel list (standard montage): align+interpolate.
            # (channel_auto is handled AFTER the UnifiedDataset is built, on its
            # live post-kernel channel counts — the cached locator's
            # 'Number of Channels' is recomputed on load and may differ.)
            if common_channels:
                _preflight_common_channels(locator_df, common_channels,
                                           min_matched, log)
                avail = locator_df["Completeness Check"].astype(str) != "Unavailable"
                locator_df.loc[avail, "Number of Channels"] = len(common_channels)

            task_locator = task_dir / "locator.csv"
            locator_df.to_csv(str(task_locator), index=False)

            from eegunity import UnifiedDataset
            ud_kwargs = dict(locator_path=str(task_locator),
                             verbose="WARNING", num_workers=num_workers)
            if kernel_spec:
                ud_kwargs["kernel_spec"] = kernel_spec
            ud = UnifiedDataset(**ud_kwargs)

            if bool(getattr(kernel_obj, "HANDLES_UNAVAILABLE", False)):
                live = ud.get_shared_attr()["locator"]
                include_row = getattr(kernel_obj, "export_include_row", None)
                if callable(include_row):
                    can_load = live.apply(lambda row: bool(include_row(row)), axis=1)
                else:
                    can_load = live["File Path"].astype(str).str.len() > 0
                unavailable = live["Completeness Check"].astype(str) == "Unavailable"
                promote_idx = live.index[unavailable & can_load]
                if len(promote_idx):
                    live.loc[promote_idx, "Completeness Check"] = "Completed"
                    ud.get_shared_attr()["locator"] = live
                    log(f"    live locator: kernel re-enabled "
                        f"{len(promote_idx)} recording(s) for export load()")

            if channel_auto:
                # Dominant-montage grouping on the LIVE (post-kernel) locator —
                # EEGUnity's auto_domain/group_by_domain done inline: keep only the
                # recordings whose channel COUNT equals the most common one, so the
                # kept group is homogeneous and exports as a uniform flat HDF5.
                live = ud.get_shared_attr()["locator"]
                am = live["Completeness Check"].astype(str) != "Unavailable"
                counts = live.loc[am, "Number of Channels"].astype(float).astype(int)
                n_av = int(am.sum())
                if n_av == 0:
                    raise TaskSkip("no available recordings for auto channel grouping.")
                dominant = int(counts.mode().iloc[0])
                cnt_dist = dict(Counter(counts.tolist()))
                drop_idx = counts[counts != dominant].index
                live.loc[drop_idx, "Completeness Check"] = "Unavailable"
                ud.get_shared_attr()["locator"] = live
                n_kept = n_av - len(drop_idx)
                log(f"    auto dominant montage = {dominant} channels; "
                    f"kept {n_kept}/{n_av} recordings (live count distribution {cnt_dist})")
                if n_kept == 0:
                    raise TaskSkip("auto dominant montage matched no recording.")

            combined_pipeline = _make_combined_pipeline(
                pipeline_fn, common_channels, min_matched, pick_only=pick_only,
                preserve_label_channels=(spec.label_route == "misc"))
            if spec.target_events:
                combined_pipeline = _make_target_event_priority_pipeline(
                    combined_pipeline, spec.target_events)

            # --rebuild: the EEGUnity writer refuses to overwrite, so clear any
            # stale output first.
            if rebuild and hdf5_path.exists():
                hdf5_path.unlink()

            tmin = epoch_params.get("tmin")
            baseline = None if (tmin is None or tmin >= 0) else (None, 0)

            log(f"    building HDF5 (config_key={config_key}) ...")
            if spec.label_route == "misc":
                n_misc = _build_misc_route_hdf5(
                    ud=ud,
                    spec=spec,
                    epoch_params=epoch_params,
                    task_dir=task_dir,
                    config_key=config_key,
                    pipeline=combined_pipeline,
                    log=log,
                )
                log(f"    misc epochs written: {n_misc}")
            elif spec.epoch_method == "epoch_by_event_hdf5":
                ud.eeg_batch.epoch_by_event_hdf5(
                    output_path=str(task_dir),
                    file_name_prefix=config_key,
                    miss_bad_data=True,
                    include_events=spec.target_events or None,
                    format_version="v2",
                    epoch_params={"tmin": epoch_params["tmin"],
                                  "tmax": epoch_params["tmax"],
                                  "baseline": baseline,
                                  "event_repeated": "drop"},
                    pipeline=combined_pipeline,
                )
            elif spec.epoch_method == "epoch_by_segmentation_hdf5":
                ud.eeg_batch.epoch_by_segmentation_hdf5(
                    output_path=str(task_dir),
                    file_name_prefix=config_key,
                    miss_bad_data=True,
                    format_version="v2",
                    segment_params={"segment_length": epoch_params["segment_length"],
                                    "overlap": epoch_params["overlap"]},
                    epoch_params={"baseline": None},
                    pipeline=combined_pipeline,
                )
            else:  # epoch_by_long_event_hdf5
                long_event_epoch_params = {
                    "tmin": epoch_params["tmin"],
                    "tmax": epoch_params["tmax"],
                    "baseline": baseline,
                    "event_repeated": "drop",
                }
                # EEGUnity 0.8.x only segments annotations whose duration is
                # strictly greater than (tmax - tmin). Many sleep-stage labels
                # are exactly 30 s long, so shrink the export-time window by an
                # epsilon while preserving the document's 30 s task definition.
                if long_event_epoch_params["tmax"] > long_event_epoch_params["tmin"]:
                    long_event_epoch_params["tmax"] -= 1e-6
                ud.eeg_batch.epoch_by_long_event_hdf5(
                    output_path=str(task_dir),
                    overlap=epoch_params["overlap"],
                    file_name_prefix=config_key,
                    miss_bad_data=True,
                    include_events=spec.target_events or None,
                    format_version="v2",
                    epoch_params=long_event_epoch_params,
                    pipeline=combined_pipeline,
                )

            if not hdf5_path.exists():
                # EEGUnity's v2 writer only creates the file on the first epoch.
                # No file => zero epochs were produced for this task.
                detail = (
                    f"target_events={spec.target_events}" if spec.target_events
                    else "segmentation produced no epochs"
                )
                msg = (
                    f"no epochs produced ({detail}) across "
                    f"{'sampled ' if max_files else ''}recordings. Likely cause: the "
                    f"kernel emits no matching event annotations (events may live in "
                    f"unread BIDS events.tsv sidecars), or all recordings failed to "
                    f"load. Inspect raw.annotations for this dataset's kernel."
                )
                log(f"    NO-EPOCHS: {msg}")
                return JobResult(dataset, task, "failed", reason=msg,
                                 config_key=config_key)

            summary = _summarize_hdf5(str(hdf5_path), spec)
            failure = _task_summary_failure(spec, summary)
            if failure:
                log(f"    FAILED: {failure}")
                return JobResult(dataset, task, "failed", reason=failure,
                                 hdf5_path=str(hdf5_path),
                                 config_key=config_key,
                                 n_epochs=summary.get("n_epochs"), summary=summary)
            log(f"    built: {hdf5_path}")
            log(f"    summary: {summary}")
            return JobResult(dataset, task, "success", hdf5_path=str(hdf5_path),
                             config_key=config_key,
                             n_epochs=summary.get("n_epochs"), summary=summary)

    except TaskSkip as e:
        log(f"    SKIPPED: {e}")
        return JobResult(dataset, task, "skipped", reason=str(e))
    except Exception as e:  # noqa: BLE001 - batch must be fault tolerant
        import traceback
        log(f"    FAILED: {e}")
        log(traceback.format_exc())
        return JobResult(dataset, task, "failed", reason=str(e))
