# SKILL: BIDS Standard Dataset Kernel

> **Applicable mode**: The dataset follows the BIDS standard, contains `participants.tsv` and `*_events.tsv`,  
> and EEGUnity can read EEG files normally (EDF / BDF / SET, etc.).  
> The kernel's main task is to extract participant metadata and event structure from BIDS sidecar files.  
> **Reference example**: `kernels/bids.py` (generic BIDS kernel, can be reused directly)  
> **Specification document**: `kernels/KERNEL_RULEBOOK.md`

---

## Your Role

You are an EEGUnity kernel engineer. Goal: generate a Stage1 kernel for the given BIDS dataset that complies with `KERNEL_RULEBOOK.md`.  
**First confirm whether the generic BIDS kernel already meets requirements; only create a new kernel when dataset-specific processing is needed.**

---

## Phase 0: Does a New Kernel Need to Be Created?

First try using the generic BIDS kernel (`kernels/bids.py`):

```python
# neurodoc/kernels/bids.py already implements:
# - Extract age / sex from participants.tsv
# - Extract event summary from *_events.tsv or raw.annotations
# - Write to eegunity_description (does not include amplifier/cap/handedness)
```

A new dataset-specific kernel is only needed in the following cases:
1. Channel names are non-standard and need renaming
2. Events need remapping (events.tsv label format is unusual)
3. Additional sidecar files need to be read (e.g., `.mat`, `.json`)
4. amplifier / cap / handedness have known values that need to be hardcoded
5. Multi-paradigm files exist that require paradigm prefixes

If the generic kernel is sufficient, simply specify `bids.py` in analysis.md — no new file is needed.

---

## Phase 1: Dataset Exploration (Auto-extraction)

### 1.1 Confirm BIDS Structure

```bash
# Check top-level structure
ls <dataset_path>/
# Expected: participants.tsv, dataset_description.json, sub-*/ directories

# Check subject directory structure
ls <dataset_path>/sub-01/
# Expected: eeg/ directory (or ses-XX/eeg/)
```

### 1.2 Read participants.tsv

```python
import pandas as pd
df = pd.read_csv("<dataset_path>/participants.tsv", sep="\t")
print(df.head(10))
print("columns:", df.columns.tolist())
print("row count:", len(df))
```

Record: format of the `participant_id` column, `age` column (whether it exists, format), `sex`/`gender` column (value format).

### 1.3 Read a Sample EEG File

```bash
find <dataset_path> -name "*.edf" -o -name "*.bdf" -o -name "*.set" | head -3
```

```python
import mne
raw = mne.io.read_raw("<sample_eeg_file>", preload=False, verbose=False)
print("ch_names:", raw.ch_names)
print("ch_types:", raw.get_channel_types())
print("sfreq:", raw.info['sfreq'])
```

Record: whether non-standard channel names exist.

### 1.4 Read events.tsv

```bash
find <dataset_path> -name "*_events.tsv" | head -5
```

```python
events_df = pd.read_csv("<sample_events_tsv>", sep="\t")
print(events_df.head(10))
print("columns:", events_df.columns.tolist())
# Standard columns: onset, duration, trial_type, value, stim_type
```

Record: event label column name, all unique label values and their meanings.

### 1.5 Check dataset_description.json

```python
import json
with open("<dataset_path>/dataset_description.json") as f:
    desc = json.load(f)
print(json.dumps(desc, indent=2))
# Look for: Name, Authors, ReferencesAndLinks, EEGReference, etc.
```

Record: dataset name, reference paper DOI, device information (if available).

### 1.6 Confirm Whether Generic bids.py Is Usable

| Check Item | Result |
|------------|--------|
| participants.tsv exists and has age / sex columns | ✓ / ✗ |
| Channel names conform to standard_1020 | ✓ / ✗ |
| events.tsv labels are already human-readable strings | ✓ / ✗ |
| amplifier / cap have known hardcoded values | ✓ / ✗ |
| No multi-paradigm ambiguity | ✓ / ✗ |

If all ✓, use the generic `bids.py` — this SKILL workflow ends here.  
If any ✗, proceed to Phase 2 to create a dedicated kernel.

---

## Phase 2: Dedicated Kernel Generation

Only use this template when the generic `bids.py` is insufficient.  
You can inherit from `bids.py`'s `BIDSKernel` and only override the parts that need extension.

```python
"""<DatasetName> stage1 kernel for EEGUnity.

Extends the generic BIDS kernel with dataset-specific channel mapping
and/or hardcoded device metadata.

Source: <dataset DOI or OpenNeuro link>
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

import mne

# Inherit generic BIDS kernel (already handles participants.tsv / events.tsv)
from kernels.bids import BIDSKernel


# Source: <dataset documentation>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
# Only add this dictionary when channel names are non-standard
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # "<original_name>": "<standard 10-20 name>",
}

# Known device metadata (if explicitly documented in the dataset)
# Source: <dataset documentation / paper>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
_AMPLIFIER = "<amplifier_str>"   # write "unknown" if not known
_CAP = "<cap_str>"               # write "unknown" if not known
_HANDEDNESS = "<handedness_str>" # write "unknown" if not known


@dataclass
class <DatasetName>Kernel(BIDSKernel):
    """Stage1 kernel for the <dataset_name> BIDS dataset."""

    KERNEL_ID: str = "<dataset-id>-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ── Step 1: Rename channels (only when non-standard names exist) ────────────────────
        if _CHANNEL_RENAME_MAP:
            rename_map = {
                ch: _CHANNEL_RENAME_MAP[ch]
                for ch in raw.ch_names
                if ch in _CHANNEL_RENAME_MAP
            }
            if rename_map:
                raw.rename_channels(rename_map)

        # ── Step 2: Set montage ──────────────────────────────────────────────
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.info.set_montage(montage, on_missing="ignore")

        # ── Step 3: Get age / sex from participants.tsv (via parent class) ──
        age, sex = self.get_age_sex(file_path)

        # ── Step 4: Write eegunity_description ──────────────────────────────
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age":        age,
                "sex":        sex,
                "amplifier":  _AMPLIFIER,
                "cap":        _CAP,
                "handedness": _HANDEDNESS,
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
| Article 6 | Channel | channel rename is called **before** `set_montage()` |
| Article 6 | Channel | `set_montage` uses `on_missing="ignore"` |
| Article 7 | Source | `_CHANNEL_RENAME_MAP` has source annotation (if present) |
| Article 8 | Description | `raw.info["description"]` writes valid JSON containing `original_description` + `eegunity_description` |
| Article 9 | Description | `eegunity_description` contains all 5 fields: `age`, `sex`, `amplifier`, `cap`, `handedness` |
| Article 10 | age | `age` is a string; `"unknown"` when not known, not `"0"` |
| Article 11 | sex | `sex` is lowercase `"male"`/`"female"`/`"unknown"` |
| Article 13 | raw meta | If annotations were modified, confirm they remain raw meta (no semantic derivation) |
| Article 17 | Annotation | `_CHANNEL_RENAME_MAP`, `_AMPLIFIER`/`_CAP` have source annotations |
| Article 3 | LLM integrity | All LLM-inferred information is marked "needs human review" |

---

## Appendix: Limitations of the Generic bids.py

The generic `bids.py` does not fill in the `amplifier`, `cap`, or `handedness` fields (writes `"unknown"`),  
and does not perform channel renaming. If the dataset has this known information, a dedicated kernel must be created with hardcoded values.
