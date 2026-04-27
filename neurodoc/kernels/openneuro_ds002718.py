"""openneuro_ds002718 stage1 kernel for EEGUnity.

Face processing EEG dataset with famous/unfamiliar/scrambled face categories
and symmetry judgment paradigm. BIDS-compliant with EEGLAB .set files.

Source: https://openneuro.org/datasets/ds002718 (DOI: 10.18112/openneuro.ds002718.v1.1.0)
Dataset: 18 subjects, 74 channels, 250 Hz sampling rate.
Events: stimulus presentations (famous/unfamiliar/scrambled × new/early/late)
        and response events (left/right × sym/nonsym).

Derived misc channels: trial_dist_misc, time_dist_misc, event_order_misc
  sourced from events.tsv columns trial_dist, time_dist, event_order.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: dataset README / paper DOI 10.1038/sdata.2015.1
# 74-channel EEG cap with standard electrode positions
# Annotator: Human, 2026-04-08
_STANDARD_74_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "Iz",
    "CB1", "CB2",
]

# Source: 10.1038/sdata.2015.1 - BrainAmp amplifier system
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_AMPLIFIER = "BrainAmp"
_CAP_MATERIAL = "Ag/AgCl"  # LLM 推断，需人类复核


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, Any]]:
    """Load subject information from BIDS participants.tsv.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping from subject_id to {age, sex, handedness, gender}.
    """
    tsv_path = Path(dataset_path) / "participants.tsv"
    if not tsv_path.exists():
        return {}

    df = pd.read_csv(tsv_path, sep="\t")
    subject_dict: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        subj_id = str(row.get("participant_id", "")).strip()
        if not subj_id:
            continue

        info: Dict[str, Any] = {}

        # Handle age column
        age_col = "age" if "age" in df.columns else next(
            (c for c in df.columns if c.lower() == "age"), None
        )
        if age_col and age_col in df.columns:
            age_val = row.get(age_col)
            if pd.notna(age_val):
                info["age"] = str(int(float(age_val)))
            else:
                info["age"] = "unknown"
        else:
            info["age"] = "unknown"

        # Handle sex/gender column - prefer 'sex', fallback to 'gender'
        sex_col = None
        for c in df.columns:
            if c.lower() == "sex":
                sex_col = c
                break
        if sex_col is None:
            for c in df.columns:
                if c.lower() == "gender":
                    sex_col = c
                    break

        if sex_col and sex_col in df.columns:
            sex_val = str(row.get(sex_col, "")).strip().lower()
            if sex_val in ("m", "male"):
                info["sex"] = "male"
            elif sex_val in ("f", "female"):
                info["sex"] = "female"
            else:
                info["sex"] = "unknown"
        else:
            info["sex"] = "unknown"

        # Handle handedness column
        hand_col = None
        for c in df.columns:
            if c.lower() == "handedness":
                hand_col = c
                break

        if hand_col and hand_col in df.columns:
            hand_val = str(row.get(hand_col, "")).strip().lower()
            if hand_val in ("r", "right"):
                info["handedness"] = "right"
            elif hand_val in ("l", "left"):
                info["handedness"] = "left"
            else:
                info["handedness"] = "unknown"
        else:
            info["handedness"] = "unknown"

        # Store gender if present (for required_info_fields)
        gender_col = None
        for c in df.columns:
            if c.lower() == "gender":
                gender_col = c
                break
        if gender_col and gender_col in df.columns:
            gender_val = str(row.get(gender_col, "")).strip()
            info["gender"] = gender_val if pd.notna(row.get(gender_col)) else "unknown"
        else:
            info["gender"] = "unknown"

        subject_dict[subj_id] = info

    return subject_dict


def _find_events_tsv(file_path: str) -> Optional[Path]:
    """Find the sibling events.tsv file for a given EEG file."""
    fp = Path(file_path)
    # BIDS pattern: sub-XXX_task-YYY_eeg.set -> sub-XXX_task-YYY_events.tsv
    # or in eeg/ subdirectory
    
    # Get base name without eeg extension
    base = fp.name.replace("_eeg.set", "").replace("_eeg.eeg", "").replace("_eeg.vhdr", "").replace("_eeg.edf", "")
    parent = fp.parent

    # Same directory
    events_file = parent / f"{base}_events.tsv"
    if events_file.exists():
        return events_file

    # Parent directory (if in eeg/ subfolder)
    events_file = parent.parent / f"{base}_events.tsv"
    if events_file.exists():
        return events_file

    # Try with task-FaceRecognition pattern
    for suffix in ["", "_task-FaceRecognition"]:
        events_file = parent / f"{base}{suffix}_events.tsv"
        if events_file.exists():
            return events_file
        events_file = parent.parent / f"{base}{suffix}_events.tsv"
        if events_file.exists():
            return events_file

    return None


def _read_events_tsv(events_path: Path) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not events_path.exists():
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _create_derived_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame, column: str, channel_name: str) -> None:
    """Create a derived misc channel from events.tsv column values.

    For each event row, creates a step-function segment where the channel
    value equals the column value from event onset to the next event onset
    (or end of file). Between events, value is 0.
    """
    # Ensure raw is preloaded before adding channels
    if not raw.preload:
        raw.load_data()

    if events_df is None or column not in events_df.columns:
        # Create empty channel with zeros
        data = np.zeros((1, len(raw.times)))
        info = mne.create_info([channel_name], raw.info["sfreq"], ["misc"])
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        raw.add_channels([misc_raw], force_update_info=True)
        return

    # Get event onsets in samples
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    channel_data = np.zeros((1, n_samples))

    # Sort by onset
    events_sorted = events_df.sort_values("onset").reset_index(drop=True)

    for i, row in events_sorted.iterrows():
        onset_sec = float(row["onset"])
        onset_sample = int(onset_sec * sfreq)

        # Determine end sample (next event or end of data)
        if i + 1 < len(events_sorted):
            next_onset_sec = float(events_sorted.iloc[i + 1]["onset"])
            end_sample = int(next_onset_sec * sfreq)
        else:
            end_sample = n_samples

        # Clamp to valid range
        onset_sample = max(0, min(onset_sample, n_samples))
        end_sample = max(0, min(end_sample, n_samples))

        if onset_sample < end_sample:
            # Get value - handle numeric or string
            val = row.get(column, 0)
            try:
                val = float(val)
            except (ValueError, TypeError):
                # For non-numeric, use hash or categorical encoding
                val = float(hash(str(val)) % 100000)

            channel_data[0, onset_sample:end_sample] = val

    info = mne.create_info([channel_name], sfreq, ["misc"])
    misc_raw = mne.io.RawArray(channel_data, info, first_samp=raw.first_samp)
    raw.add_channels([misc_raw], force_update_info=True)


class OpenneuroDs002718Kernel:
    KERNEL_ID = "openneuro_ds002718"
    DATASET_NAME = "openneuro_ds002718"
    REQUIRED_INFO_FIELDS = ["age", "sex", "handedness"]
    DERIVED_MISC_CHANNELS = ["trial_dist_misc", "time_dist_misc", "event_order_misc"]
    EVENTS_TSV_COLUMNS = ["trial_dist", "time_dist", "event_order"]

    def __init__(self):
        self._participants_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_path = udataset.dataset_path
        file_path = row["file_path"]

        # Load participants info once
        if self._participants_cache is None:
            self._participants_cache = _load_participants_tsv(dataset_path)

        # Extract subject ID from file path
        fp = Path(file_path)
        subj_id = None
        for part in fp.parts:
            if part.startswith("sub-"):
                subj_id = part
                break

        # Get participant info
        participant_info = self._participants_cache.get(subj_id, {}) if subj_id else {}

        # Build required info fields from participants.tsv
        required_info = {}
        for field in self.REQUIRED_INFO_FIELDS:
            val = participant_info.get(field, "unknown")
            required_info[field] = str(val) if val is not None else "unknown"

        # Build eegunity_description
        eegunity_description = {
            "age": required_info.get("age", "unknown"),
            "sex": required_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP_MATERIAL,
            "handedness": required_info.get("handedness", "unknown"),
        }

        # Preserve original description
        original_description = raw.info.get("description", "")

        # Set description as JSON string (MNE requires string, not dict)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        # Find and read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path) if events_path else None

        # Create derived misc channels from events.tsv columns
        column_map = {
            "trial_dist_misc": "trial_dist",
            "time_dist_misc": "time_dist",
            "event_order_misc": "event_order",
        }

        for channel_name in self.DERIVED_MISC_CHANNELS:
            column = column_map.get(channel_name, channel_name.replace("_misc", ""))
            _create_derived_misc_channel(raw, events_df, column, channel_name)

        return raw


KERNEL = OpenneuroDs002718Kernel()