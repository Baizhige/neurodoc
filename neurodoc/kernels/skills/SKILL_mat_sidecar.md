# SKILL: .mat Sidecar Marker Kernel

> **Applicable mode**: The main data file is in `.mat` format (or a same-name `.mat` sidecar exists),  
> event labels are stored in a field of the `.mat` file (e.g., `marker`, `classlabel`, `event`),  
> rather than in MNE Annotations. Events must be extracted from the `.mat` field and written back to MNE Annotations.  
> **Reference example**: `kernels/figshare_largemi.py`  
> **Specification document**: `kernels/KERNEL_RULEBOOK.md`

---

## Your Role

You are an EEGUnity kernel engineer. Goal: generate a Stage1 kernel for the given dataset that complies with `KERNEL_RULEBOOK.md`.  
**Before writing any code, complete all exploration steps in Phase 1.**

---

## Phase 1: Dataset Exploration (Auto-extraction)

### 1.1 List .mat File Structure

```bash
find <dataset_path> -name "*.mat" | head -20
```

Record: file naming pattern (e.g., `CLA-SubjectA-160405-3St-LRHand.mat`, `A01E.mat`).

### 1.2 Read a .mat File, Check Top-Level Structure

```python
import scipy.io as sio
mat = sio.loadmat("<sample_mat_file>", simplify_cells=True)
print("Top-level keys:", list(mat.keys()))
# Filter '__header__', '__version__', '__globals__'
data_keys = [k for k in mat.keys() if not k.startswith('__')]
print("Data keys:", data_keys)
```

If the top level has a nested structure (e.g., `mat['o']`), continue expanding:

```python
inner = mat["o"]
print("Inner keys:", list(inner.keys()) if hasattr(inner, 'keys') else type(inner))
```

### 1.3 Locate the marker / label Field

```python
# Common field names: marker, classlabel, event, labels, y
marker = mat["o"]["marker"]   # replace path based on 1.2 results
print("marker shape:", marker.shape)
print("marker dtype:", marker.dtype)
print("unique values:", set(marker.flatten().tolist()[:1000]))
```

Record:
- marker shape (typically `(n_samples,)` or `(1, n_samples)`)
- All unique values and their meanings (consult dataset documentation)
- Whether the marker is a "continuous marker" (one value per sample) or an "event index" (sparse timestamp+value pairs)

**Continuous marker**: values change sample-by-sample throughout the recording; 0 means no event, non-zero values indicate event type.  
**Event index**: only lists the timestamps of event occurrences as `[onset_sample, event_code]`; no entries for other time points.

### 1.4 Read EEG Data Structure

```python
# Common field names: data, eeg, X, signal
eeg = mat["o"]["data"]   # replace based on 1.2 results
print("EEG shape:", eeg.shape)  # expected: (n_channels, n_samples) or (n_samples, n_channels)
sfreq = mat["o"]["sampFreq"]    # or sFreq, Fs, fs, sample_rate
print("Sample rate:", sfreq)
ch_names_raw = mat["o"]["chnames"]   # or channels, channames
print("Channel names:", ch_names_raw)
```

Record: EEG shape, sample rate, channel name list.

### 1.5 Extract Participant Information

Try in order of priority:

1. **Participant list file**:
   ```bash
   find <dataset_path> -name "participants.tsv" | head -3
   ```
2. **README / documentation**:
   ```bash
   find <dataset_path> -name "README*" -o -name "*.txt" | head -5
   cat <readme_path>
   ```
3. **Official dataset paper** (DOI / URL, if provided by user).
4. If none are accessible, write `"unknown"` for all fields.

Record: each subject ID → age (str), sex, amplifier, cap, handedness.

### 1.6 Confirm Marker Type (Continuous vs Event Index)

- If `marker.shape == (n_samples,)` and most values are 0 → **continuous marker** (see template Option A)
- If marker is a sparse event list (each row is `[onset, code]`) → **event index** (see template Option B)

---

## Phase 2: Kernel Generation

Based on the extraction results from Phase 1, select Option A or Option B.

```python
"""<DatasetName> stage1 kernel for EEGUnity.

<Short description: dataset name, paradigm, channel count, event structure>

Source: <paper DOI or dataset URL>
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import scipy.io as sio


# Source: <paper citation / dataset documentation URL>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # "<sub_key>": {"age": "<age_str>", "sex": "<sex_str>"},
}

# Source: <dataset documentation describing the meaning of each marker value>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
# Format: {marker_int_value: "annotation_description"}
_EVENT_MAP: Dict[int, str] = {
    # 1: "left hand MI",
    # 2: "right hand MI",
    # ...
}


# ── Option A: Continuous marker (one marker value per sample) ───────────────────────────────

def _build_annotations_from_continuous_marker(
    marker: np.ndarray,
    sfreq: float,
    event_map: Dict[int, str],
) -> mne.Annotations:
    """Convert a per-sample marker array to MNE Annotations.

    Consecutive samples with the same non-zero code are merged into
    a single annotation with the corresponding duration.
    """
    marker = marker.flatten()
    annotations: List[Tuple[float, float, str]] = []
    current_code: Optional[int] = None
    current_start: int = 0

    for i, raw_code in enumerate(marker):
        code = int(raw_code)
        label = event_map.get(code)

        if label is not None:
            if current_code is None:
                current_code = code
                current_start = i
            elif code != current_code:
                annotations.append((
                    current_start / sfreq,
                    (i - current_start) / sfreq,
                    event_map[current_code],
                ))
                current_code = code
                current_start = i
        else:
            if current_code is not None:
                annotations.append((
                    current_start / sfreq,
                    (i - current_start) / sfreq,
                    event_map[current_code],
                ))
                current_code = None

    if current_code is not None:
        annotations.append((
            current_start / sfreq,
            (len(marker) - current_start) / sfreq,
            event_map[current_code],
        ))

    if annotations:
        onset, duration, desc = zip(*annotations)
        return mne.Annotations(list(onset), list(duration), list(desc))
    return mne.Annotations([], [], [])


# ── Option B: Event index (sparse [onset_sample, code] list) ────────────────────

def _build_annotations_from_event_index(
    events_array: np.ndarray,
    sfreq: float,
    event_map: Dict[int, str],
    default_duration: float = 0.0,
) -> mne.Annotations:
    """Convert a sparse event index array to MNE Annotations.

    events_array: shape (n_events, 2) → columns [onset_sample, event_code]
    default_duration: annotation duration in seconds (0 = instantaneous)
    """
    onsets, durations, descs = [], [], []
    for row in events_array:
        onset_sample, code = int(row[0]), int(row[1])
        label = event_map.get(code)
        if label is not None:
            onsets.append(onset_sample / sfreq)
            durations.append(default_duration)
            descs.append(label)
    return mne.Annotations(onsets, durations, descs)


@dataclass
class <DatasetName>Kernel:
    """Stage1 kernel for the <dataset_name> dataset."""

    KERNEL_ID: str = "<dataset-id>-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ── Subject ID extraction ────────────────────────────────────────────
        # Adjust based on file naming pattern from Phase 1.1
        subject_match = re.search(r"<pattern>", os.path.basename(file_path), re.IGNORECASE)
        if subject_match is None:
            raise ValueError(f"Cannot infer subject id from: {file_path!r}")
        subject_key = subject_match.group(1).upper()
        if subject_key not in _SUBJECT_DICT:
            raise ValueError(f"Unknown subject id: {subject_key!r}")

        # ── Step 1: Load .mat file ───────────────────────────────────────────
        mat = sio.loadmat(file_path, simplify_cells=True)
        # Adjust path based on Phase 1.2–1.4 results
        data_struct = mat["<top_key>"]
        marker = data_struct["<marker_key>"]
        sfreq = float(raw.info["sfreq"])

        # ── Step 2: Build annotations ────────────────────────────────────────
        # Select Option A or Option B, delete the other
        # Option A (continuous marker):
        annotations = _build_annotations_from_continuous_marker(marker, sfreq, _EVENT_MAP)
        # Option B (event index):
        # annotations = _build_annotations_from_event_index(marker, sfreq, _EVENT_MAP)

        raw.set_annotations(annotations)

        # ── Step 3: Write eegunity_description ──────────────────────────────
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age":        _SUBJECT_DICT[subject_key]["age"],
                "sex":        _SUBJECT_DICT[subject_key]["sex"],
                "amplifier":  "<amplifier_str>",
                "cap":        "<cap_str>",
                "handedness": "<handedness_str>",
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        return raw


KERNEL = <DatasetName>Kernel()
```

---

## Phase 3: Validation Checklist (Against KERNEL_RULEBOOK.md)

| Number | Rule | Check Item |
|--------|------|------------|
| Article 5 | Interface | Module ends with `KERNEL = <ClassName>()` |
| Article 5 | Interface | `apply(self, udataset, raw, row) -> mne.io.BaseRaw` signature is correct |
| Article 8 | Description | `raw.info["description"]` writes valid JSON containing `original_description` + `eegunity_description` |
| Article 9 | Description | `eegunity_description` contains all 5 fields: `age`, `sex`, `amplifier`, `cap`, `handedness` |
| Article 10 | age | `age` is a string type (`"22"` not integer `22`) |
| Article 11 | sex | `sex` is lowercase `"male"`/`"female"`/`"unknown"` (no uppercase first letter) |
| Article 11 | Source | `_SUBJECT_DICT` has source annotation; if filled by LLM, must mark "needs human review" |
| Article 12 | Label | Description strings in `_EVENT_MAP` are human-readable, not bare numbers |
| Article 13 | raw meta | All annotations correspond to original marker values, no semantic derivation introduced |
| Article 16 | External file | `.mat` read logic has clear error messages (raises informative error when field not found) |
| Article 17 | Annotation | `_EVENT_MAP` has source annotation (paper/document + annotator + date) |
| Article 3 | LLM integrity | All LLM-inferred information is marked "needs human review" |
