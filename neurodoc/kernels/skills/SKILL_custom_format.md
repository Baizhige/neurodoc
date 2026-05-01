# SKILL: Custom / Proprietary Format Kernel (HANDLES_UNAVAILABLE)

> **Applicable mode**: EEGUnity cannot directly parse the data files (non-standard format, proprietary binary,  
> multi-file combination, etc.), requiring the kernel to implement `HANDLES_UNAVAILABLE=True` and provide  
> a `load()` method to manually construct an MNE `RawArray`.  
> **Reference document**: EEGUnity kernel tutorial — "HANDLES_UNAVAILABLE Interface"  
> **Specification document**: `kernels/KERNEL_RULEBOOK.md`

---

## Your Role

You are an EEGUnity kernel engineer. Goal: generate a Stage1 kernel for the given dataset that complies with `KERNEL_RULEBOOK.md`.  
This SKILL applies to **file formats that EEGUnity reports errors and cannot parse** — the kernel must read the data internally.  
**Before writing any code, complete all exploration steps in Phase 1.**

---

## Phase 1: Dataset Exploration (Auto-extraction)

### 1.1 Confirm File Format

```bash
# List all data file extensions
find <dataset_path> -type f | grep -v "__pycache__" | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

Record: file extensions, file naming pattern.

### 1.2 Attempt Standard MNE Parsing (Confirm It Truly Cannot Be Parsed)

```python
import mne
# Try the corresponding read function based on extension:
# .eeg/.vhdr: mne.io.read_raw_brainvision
# .cnt: mne.io.read_raw_cnt
# .set: mne.io.read_raw_eeglab
# .fif: mne.io.read_raw_fif
# other: mne.io.read_raw (let MNE auto-detect)
try:
    raw = mne.io.read_raw("<sample_file>", preload=False)
    print("MNE can parse this! Switch to SKILL_gdf_annotation_remap.md or another SKILL.")
except Exception as e:
    print("MNE cannot parse:", e)
    print("→ HANDLES_UNAVAILABLE kernel needed")
```

### 1.3 Inspect File Structure

For common proprietary formats:

```python
# If .mat format:
import scipy.io as sio
mat = sio.loadmat("<sample_file>", simplify_cells=True)
print("keys:", [k for k in mat.keys() if not k.startswith('__')])

# If HDF5 / .h5 format:
import h5py
with h5py.File("<sample_file>", "r") as f:
    print("keys:", list(f.keys()))
    # Recursively display structure
    f.visititems(lambda name, obj: print(name, type(obj)))

# If numpy / .npy / .npz format:
import numpy as np
data = np.load("<sample_file>", allow_pickle=True)
print("shape:", data.shape if hasattr(data, 'shape') else data.files)

# If pure binary format, consult official documentation or README for parsing method.
```

Record: data field paths, EEG matrix shape (n_channels × n_samples or n_samples × n_channels), sample rate field name, channel name field name, marker/event field name.

### 1.4 Extract Channel Information

```python
# Get channel names
ch_names = mat["<path>"]["chnames"]   # replace based on 1.3 results
print("Channel names:", ch_names)
print("Count:", len(ch_names))

# Get sample rate
sfreq = float(mat["<path>"]["sampFreq"])   # replace based on 1.3 results
print("Sample rate:", sfreq, "Hz")
```

Identify which channels are EEG, EOG, or other types.

### 1.5 Extract Events / Markers

See `SKILL_mat_sidecar.md` Phase 1.3: locate the marker field and determine whether it is a continuous marker or event index.

### 1.6 Extract Participant Information

Try in order of priority:

1. `participants.tsv` (BIDS)
2. README / documentation
3. Official paper (DOI / URL)
4. If none are accessible, write `"unknown"` for all fields

---

## Phase 2: Kernel Generation

A `HANDLES_UNAVAILABLE` kernel must implement two methods: `load()` and `apply()`.  
EEGUnity automatically calls `load()` in place of the standard read workflow when it detects the file cannot be parsed.

```python
"""<DatasetName> stage1 kernel for EEGUnity (HANDLES_UNAVAILABLE).

<Short description: dataset name, paradigm, file format, channel count, event structure>

This kernel reads <format> files directly because EEGUnity cannot parse
them with standard MNE routines.

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
import scipy.io as sio   # replace based on actual format


# Source: <paper citation / dataset documentation URL>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # "<sub_key>": {"age": "<age_str>", "sex": "<sex_str>"},
}

# Source: <dataset documentation describing the meaning of each marker value>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
_EVENT_MAP: Dict[int, str] = {
    # marker_int_value: "annotation_description",
}


def _load_raw_from_file(file_path: str) -> mne.io.BaseRaw:
    """Parse the proprietary file and return an MNE RawArray.

    Adjust the data access paths based on Phase 1.3 findings.
    """
    # Read file (select based on Phase 1.3 results)
    mat = sio.loadmat(file_path, simplify_cells=True)
    data_struct = mat["<top_key>"]

    # EEG data matrix
    eeg_data = np.array(data_struct["<data_key>"], dtype=float)
    # Ensure shape is (n_channels, n_samples)
    if eeg_data.shape[0] > eeg_data.shape[1]:
        eeg_data = eeg_data.T

    sfreq = float(data_struct["<sfreq_key>"])

    # Channel information
    # Fill in actual channel names based on Phase 1.4
    ch_names: List[str] = list(data_struct["<chnames_key>"])
    # Set channel types (based on Phase 1.4 identification results)
    ch_types = []
    for ch in ch_names:
        if ch.upper().startswith("EOG"):
            ch_types.append("eog")
        elif ch.upper() in ("STI 014", "STIM"):
            ch_types.append("stim")
        else:
            ch_types.append("eeg")

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info, verbose=False)

    # Standard montage (if channel names conform to standard_1020)
    montage = mne.channels.make_standard_montage("standard_1020")
    raw.info.set_montage(montage, on_missing="ignore")

    # Build annotations from marker field (refer to helper functions in SKILL_mat_sidecar.md)
    marker = data_struct["<marker_key>"].flatten()
    onsets, durations, descs = [], [], []
    current_code: Optional[int] = None
    current_start: int = 0
    for i, code_raw in enumerate(marker):
        code = int(code_raw)
        label = _EVENT_MAP.get(code)
        if label is not None:
            if current_code is None:
                current_code = code
                current_start = i
            elif code != current_code:
                onsets.append(current_start / sfreq)
                durations.append((i - current_start) / sfreq)
                descs.append(_EVENT_MAP[current_code])
                current_code = code
                current_start = i
        else:
            if current_code is not None:
                onsets.append(current_start / sfreq)
                durations.append((i - current_start) / sfreq)
                descs.append(_EVENT_MAP[current_code])
                current_code = None
    if current_code is not None:
        onsets.append(current_start / sfreq)
        durations.append((len(marker) - current_start) / sfreq)
        descs.append(_EVENT_MAP[current_code])
    raw.set_annotations(mne.Annotations(onsets, durations, descs))

    return raw


@dataclass
class <DatasetName>Kernel:
    """Stage1 kernel for the <dataset_name> dataset (HANDLES_UNAVAILABLE)."""

    KERNEL_ID: str = "<dataset-id>-stage1"
    HANDLES_UNAVAILABLE: bool = True

    def load(self, file_path: str) -> mne.io.BaseRaw:
        """Called by EEGUnity when the file cannot be parsed by standard MNE."""
        return _load_raw_from_file(file_path)

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ── Subject ID extraction ────────────────────────────────────────────
        subject_match = re.search(r"<pattern>", os.path.basename(file_path), re.IGNORECASE)
        if subject_match is None:
            raise ValueError(f"Cannot infer subject id from: {file_path!r}")
        subject_key = subject_match.group(1).upper()
        if subject_key not in _SUBJECT_DICT:
            raise ValueError(f"Unknown subject id: {subject_key!r}")

        # ── Write eegunity_description ───────────────────────────────────────
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
| Article 5 | Interface | `HANDLES_UNAVAILABLE = True` exists as a class attribute |
| Article 5 | Interface | `load(self, file_path: str) -> mne.io.BaseRaw` method exists |
| Article 5 | Interface | `apply(self, udataset, raw, row) -> mne.io.BaseRaw` signature is correct |
| Article 6 | Channel | `ch_types` correctly distinguishes eeg / eog / stim, corresponding to actual channels |
| Article 6 | Channel | `set_montage` uses `on_missing="ignore"` |
| Article 8 | Description | `raw.info["description"]` writes valid JSON containing `original_description` + `eegunity_description` |
| Article 9 | Description | `eegunity_description` contains all 5 fields: `age`, `sex`, `amplifier`, `cap`, `handedness` |
| Article 10 | age | `age` is a string type (`"22"` not integer `22`) |
| Article 11 | sex | `sex` is lowercase `"male"`/`"female"`/`"unknown"` |
| Article 12 | Label | Description strings in `_EVENT_MAP` are human-readable, not bare numbers |
| Article 13 | raw meta | All annotations correspond to original marker values, no semantic derivation introduced |
| Article 16 | External file | `load()` has clear error messages for missing fields/keys |
| Article 17 | Annotation | `_SUBJECT_DICT` and `_EVENT_MAP` both have source annotations |
| Article 3 | LLM integrity | All LLM-inferred information is marked "needs human review" |
