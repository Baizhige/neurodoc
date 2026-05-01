# SKILL: GDF/BDF/EDF Annotation Remap Kernel

> **Applicable mode**: Data files are in GDF / BDF / EDF format, event labels are stored in MNE Annotations,  
> possibly as numeric codes (e.g., `"769"`) or messy strings that need to be uniformly mapped to human-readable descriptions.  
> **Reference examples**: `kernels/bcic_iv_2a.py`, `kernels/bcic_iv_2b.py`  
> **Specification document**: `kernels/KERNEL_RULEBOOK.md`

---

## Your Role

You are an EEGUnity kernel engineer. Goal: generate a Stage1 kernel for the given dataset that complies with `KERNEL_RULEBOOK.md`.  
**Before writing any code, complete all exploration steps in Phase 1.**

---

## Phase 1: Dataset Exploration (Auto-extraction)

### 1.1 List File Structure

```bash
# Replace <dataset_path> with the actual path
find <dataset_path> -name "*.gdf" -o -name "*.bdf" -o -name "*.edf" | head -20
```

Record: file extension, file naming pattern (e.g., `A01T.gdf`, `sub-01_task-MI_eeg.bdf`).

### 1.2 Read a Representative Sample File

```python
import mne
# Choose the corresponding read function based on extension:
# GDF: mne.io.read_raw_gdf
# BDF: mne.io.read_raw_bdf
# EDF: mne.io.read_raw_edf
raw = mne.io.read_raw_gdf("<sample_file>", preload=False, verbose=False)
print("ch_names:", raw.ch_names)
print("ch_types:", raw.get_channel_types())
print("sfreq:", raw.info['sfreq'])
print("n_channels:", len(raw.ch_names))
```

Record: all channel names and types. Identify EEG channels, EOG channels, STI/misc channels.

### 1.3 Extract Raw Annotation Labels

```python
events, event_id = mne.events_from_annotations(raw, verbose=False)
print("event_id:", event_id)
# event_id is a dict of {'description_string': numeric_code}
# If descriptions are pure numeric strings (e.g., '769'), the GDF stores numeric codes — consult dataset documentation to translate them
```

Record: all `event_id` entries. If they are pure numbers, consult the dataset documentation for their meanings.

### 1.4 Check Whether Channel Names Are Standard

Compare `raw.ch_names` against MNE standard names (`standard_1020`):

```python
montage = mne.channels.make_standard_montage("standard_1020")
standard_names = set(montage.ch_names)
non_standard = [ch for ch in raw.ch_names if ch not in standard_names]
print("Non-standard channel names:", non_standard)
```

If there are non-standard names (e.g., `EEG:C3`, `EEG-0`, `EEG-Fz`), consult the dataset documentation to confirm the corresponding standard 10-20 names.

### 1.5 Check for .mat Sidecar Files

```bash
find <dataset_path> -name "*.mat" | head -10
```

If same-name `.mat` files exist (e.g., `A01E.mat` corresponding to `A01E.gdf`), see `SKILL_mat_sidecar.md`.

### 1.6 Extract Participant Information

Try in order of priority:

1. **Participant list file** (BIDS format):
   ```bash
   find <dataset_path> -name "participants.tsv" | head -3
   ```
2. **Dataset README / description document**:
   ```bash
   find <dataset_path> -name "README*" -o -name "*.pdf" -o -name "*.txt" | head -5
   cat <readme_path>
   ```
3. **Official dataset paper** (DOI / URL, if provided by user).
4. If none of the above are accessible, write `"unknown"` for all fields.

Record: each subject ID → age (str), sex (`"male"` / `"female"` / `"unknown"`),  
amplifier model, electrode cap model, handedness.

---

## Phase 2: Kernel Generation

Based on the extraction results from Phase 1, fill in the code template below.  
**Warning: LLM-inferred information must be annotated in comments as "inferred by LLM, needs human review".**

```python
"""<DatasetName> stage1 kernel for EEGUnity.

<A short description: dataset name, paradigm, channel count, event structure>

Source: <paper DOI or dataset URL>
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

import mne
import numpy as np


# Source: <paper citation / dataset documentation URL>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Format: subject_id -> {age: str, sex: str}
    # age must be a string ("22" or "22-30"), sex must be "male"/"female"/"unknown"
    "<SUB_ID>": {"age": "<age_str>", "sex": "<sex_str>"},
    # ... fill in all subjects based on Phase 1.6 results
}

# Source: <dataset documentation or paper describing channel name origins>
# Annotator: <claude-model-id>, <YYYY-MM-DD> — inferred by LLM, needs human review
# Only add this dictionary when non-standard channel names exist; delete this section if names are already standard
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # "<original_name>": "<standard 10-20 name>",
    # e.g.: "EEG:C3": "C3", "EEG-0": "FC3"
}


def _remap_annotations(
    original_events: np.ndarray,
    original_event_id: Dict[str, int],
    new_event_id: Dict[str, int],
    numeric_map: Dict[str, str] = None,
) -> np.ndarray:
    """Map original annotation codes to canonical event IDs.

    numeric_map: if GDF stores numeric strings (e.g., '769'), provide a translation
    table from numeric strings to canonical descriptions. Pass None if GDF already
    uses description strings directly.
    """
    remapped = original_events.copy()
    old_to_new: Dict[int, int] = {}

    for orig_desc, orig_id in original_event_id.items():
        canonical = (numeric_map or {}).get(orig_desc, orig_desc)
        new_id = new_event_id.get(canonical)
        if new_id is not None:
            old_to_new[orig_id] = new_id

    for old_id, new_id in old_to_new.items():
        remapped[remapped[:, 2] == old_id, 2] = new_id

    return remapped


@dataclass
class <DatasetName>Kernel:
    """Stage1 kernel for the <dataset_name> dataset."""

    KERNEL_ID: str = "<dataset-id>-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ── Subject ID extraction ────────────────────────────────────────────
        # Adjust extraction logic based on file naming pattern from Phase 1.1
        subject_id = os.path.basename(file_path)[:3]  # Example: take first 3 chars of filename
        if subject_id not in _SUBJECT_DICT:
            raise ValueError(f"Unrecognized subject id: {subject_id!r}")

        # ── Step 1: Write eegunity_description ──────────────────────────────
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age":        _SUBJECT_DICT[subject_id]["age"],
                "sex":        _SUBJECT_DICT[subject_id]["sex"],
                "amplifier":  "<amplifier_str>",   # fill from Phase 1.6; write "unknown" if not known
                "cap":        "<cap_str>",          # fill from Phase 1.6; write "unknown" if not known
                "handedness": "<handedness_str>",   # "right"/"left"/"unknown"
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ── Step 2: Rename channels (only when non-standard names exist) ────────────────────
        if _CHANNEL_RENAME_MAP:
            rename_map = {
                ch: _CHANNEL_RENAME_MAP[ch]
                for ch in raw.ch_names
                if ch in _CHANNEL_RENAME_MAP
            }
            if rename_map:
                raw.rename_channels(rename_map)

        # ── Step 3: Set channel types (EOG / STI) ──────────────────────────
        # Update types based on EOG channels identified in Phase 1.2
        # Skip this step if all channel types are already correct
        # Example (modify channel name matching logic as needed):
        # _EOG_KEYS = {"EOG:CH01", "EOG:CH02"}  # replace with actual names
        # ch_type_updates = {ch: "eog" for ch in raw.ch_names if ch.upper() in _EOG_KEYS}
        # if ch_type_updates:
        #     raw.set_channel_types(ch_type_updates)

        # ── Step 4: Set standard montage ────────────────────────────────────
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.info.set_montage(montage, on_missing="ignore")

        # ── Step 5: Remap events ─────────────────────────────────────────────
        # Fill in canonical event_id and numeric_map based on Phase 1.3
        event_id = {
            # "<description_string>": <integer ID>,
            # e.g.: "Cue onset left (class 1)": 7,
        }

        # If GDF annotations are pure numeric strings (e.g., '769'), fill in this translation table
        # If annotations are already description strings, set to None
        numeric_map = {
            # "<numeric_string>": "<canonical description>",
            # e.g.: "769": "Cue onset left (class 1)",
        } or None  # delete this line and assign None directly if not needed

        original_events, original_event_id = mne.events_from_annotations(raw, verbose=False)
        new_events = _remap_annotations(
            original_events, original_event_id, event_id, numeric_map
        )

        # ── Step 6: Convert back to annotations ─────────────────────────────
        id_to_desc = {v: k for k, v in event_id.items()}
        annotations = mne.annotations_from_events(
            events=new_events,
            sfreq=raw.info["sfreq"],
            event_desc=id_to_desc,
        )
        raw.set_annotations(annotations)
        return raw


KERNEL = <DatasetName>Kernel()
```

---

## Phase 3: Validation Checklist (Against KERNEL_RULEBOOK.md)

Check each item after generating the code:

| Number | Rule | Check Item |
|--------|------|------------|
| Article 5 | Interface | Module ends with `KERNEL = <ClassName>()` |
| Article 5 | Interface | `apply(self, udataset, raw, row) -> mne.io.BaseRaw` signature is correct |
| Article 6 | Channel | channel rename is called **before** `set_montage()` |
| Article 6 | Channel | `set_montage` uses `on_missing="ignore"` |
| Article 7 | Source | `_CHANNEL_RENAME_MAP` has source annotation (paper/document + annotator + date) |
| Article 8 | Description | `raw.info["description"]` writes valid JSON containing `original_description` + `eegunity_description` |
| Article 9 | Description | `eegunity_description` contains all 5 fields: `age`, `sex`, `amplifier`, `cap`, `handedness` |
| Article 10 | age | `age` is a string type (`"22"` not integer `22`) |
| Article 10 | age | `age` is `"unknown"` when not known, must not be `"0"` or empty string |
| Article 11 | Description source | `_SUBJECT_DICT` has source annotation; if filled by LLM, mark "needs human review" |
| Article 11 | sex | `sex` is lowercase `"male"`/`"female"`/`"unknown"` (no uppercase first letter) |
| Article 12 | Label | annotation descriptions are human-readable strings, not bare numbers |
| Article 13 | raw meta | All annotations are raw meta (directly corresponding to original event codes) |
| Article 17 | Annotation | All non-raw data sources have: source + annotator + date comments |
| Article 3 | LLM integrity | LLM does not annotate as a human; all LLM-filled information is marked "needs human review" |
