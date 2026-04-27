"""Dataset-specific kernel for openneuro ds003570.

EEG auditory oddball task with musical chord progressions.
Extracts chord-level events from events.tsv and maps stimulus conditions
(standard, exemplar_deviant, function_deviant) to annotations for epoching.

Source: https://openneuro.org/datasets/ds003570
Source: DOI 10.1016/j.neuroimage.2021.118458

Paradigm:
- Participants listened to sequences of three-chord musical progressions
- Oddball paradigm with standard (85%), exemplar_deviant (7.5%), function_deviant (7.5%)
- Events: STATUS system marker + stimulus events in events.tsv

Stimulus event naming convention:
- e.g., "five6_S" → standard chord (suffix _S)
- e.g., "four6_deviantE" → exemplar deviant (same functional class, suffix _deviantE)
- e.g., "fourRoot_deviantF" → function deviant (different functional class, suffix _deviantF)
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Condition suffix mapping from stimulus event names
# Source: DOI 10.1016/j.neuroimage.2021.118458, Table 1
# Annotator: LLM, 2026-04-08, requires human verification
_CONDITION_MAP: Dict[str, str] = {
    "_S": "standard",
    "_deviantE": "exemplar_deviant",
    "_deviantF": "function_deviant",
}

# Standard 10-20 system channel names for 64-channel EEG
# Source: standard_1020 montage, BrainVision / BIDS convention
# Annotator: LLM, 2026-04-08, requires human verification
_STANDARD_10_20_CHANNELS: List[str] = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "Cz",
    "C4", "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "Oz", "O2",
    "F1", "F2", "C1", "C2", "P1", "P2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F5", "F6", "FC5", "FC3", "FC1", "FC2", "FC4", "FC6",
    "FT7", "FT8", "C5", "C6", "TP7", "TP8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P5", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
    "M1", "M2", "CB1", "CB2",
]


def _find_bids_dir(eeg_file_path: str) -> Optional[str]:
    """Find BIDS root directory from EEG file path.
    
    Walks up the directory tree to find dataset_description.json.
    """
    current = os.path.dirname(eeg_file_path)
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "dataset_description.json")):
            return current
        current = os.path.dirname(current)
    return None


def _find_events_tsv(eeg_file_path: str) -> Optional[str]:
    """Find events.tsv file sibling to the given EEG file.
    
    BIDS convention: events.tsv sits next to the data file with same basename.
    """
    base = os.path.splitext(eeg_file_path)[0]
    # Try exact basename match first
    exact = base + "_events.tsv"
    if os.path.exists(exact):
        return exact
    
    # Try without the _eeg suffix if present
    if base.endswith("_eeg"):
        alt = base[:-4] + "_events.tsv"
        if os.path.exists(alt):
            return alt
    
    # Walk up to find any events.tsv in the same directory
    eeg_dir = os.path.dirname(eeg_file_path)
    if not eeg_dir:
        return None
    try:
        for fname in os.listdir(eeg_dir):
            if fname.endswith("_events.tsv"):
                return os.path.join(eeg_dir, fname)
    except FileNotFoundError:
        return None
    
    return None


def _find_participants_tsv(bids_dir: str) -> Optional[str]:
    """Find participants.tsv in BIDS root."""
    if bids_dir is None:
        return None
    path = os.path.join(bids_dir, "participants.tsv")
    if os.path.exists(path):
        return path
    return None


def _extract_subject_id(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path.
    
    Matches patterns like sub-01, sub-1, etc.
    """
    # Try to find sub-XX pattern in path
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return match.group(0)  # Return full "sub-XX"
    return None


def _read_participants_row(participants_tsv: str, subject_id: str) -> Dict[str, str]:
    """Read a single subject's row from participants.tsv.
    
    Returns dict with all columns as strings. Missing values become "unknown".
    """
    df = pd.read_csv(participants_tsv, sep="\t")
    
    # Normalize subject_id format
    sub_clean = subject_id.lstrip("sub-")
    
    # Try matching with and without "sub-" prefix
    for sub_col in ["participant_id", "subject_id"]:
        if sub_col in df.columns:
            # Try exact match first
            mask = df[sub_col] == subject_id
            if not mask.any():
                mask = df[sub_col] == ("sub-" + sub_clean)
            if not mask.any():
                mask = df[sub_col] == sub_clean
            if mask.any():
                row = df[mask].iloc[0]
                result = {}
                for col in df.columns:
                    val = row[col]
                    if pd.isna(val):
                        result[col] = "unknown"
                    else:
                        result[col] = str(val)
                return result
    
    return {}


def _map_sex(value: str) -> str:
    """Normalize sex/gender value to lowercase standard."""
    if pd.isna(value) or value == "" or value.lower() in ["n/a", "na", "unknown", ""]:
        return "unknown"
    v = str(value).lower().strip()
    if v in ["f", "female", "w", "woman"]:
        return "female"
    if v in ["m", "male", "man"]:
        return "male"
    return "unknown"


def _map_handedness(value: str) -> str:
    """Normalize handedness value."""
    if pd.isna(value) or value == "" or value.lower() in ["n/a", "na", "unknown", ""]:
        return "unknown"
    v = str(value).lower().strip()
    if v in ["r", "right", "right-handed", "right handed"]:
        return "right"
    if v in ["l", "left", "left-handed", "left handed"]:
        return "left"
    if v in ["a", "ambidextrous", "both", "ambi"]:
        return "ambidextrous"
    return "unknown"


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events.tsv DataFrame to MNE Annotations.
    
    Uses 'onset', 'duration', and 'value' columns as the primary source for
    event descriptions, since 'trial_type' is uniform "STATUS" in this dataset.
    The 'value' column contains the actual distinguishable event labels.
    """
    if events_df is None or len(events_df) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Determine description column: use 'value' since it carries distinguishable labels
    # 'trial_type' is all "STATUS" in this dataset, so 'value' is the meaningful column
    if "value" in events_df.columns:
        descriptions = []
        for _, row in events_df.iterrows():
            val = row.get("value", "")
            if pd.notna(val) and str(val).strip() != "":
                descriptions.append(str(val).strip())
            else:
                # Fallback to trial_type if value is empty
                tt = row.get("trial_type", "")
                if pd.notna(tt) and str(tt).strip() != "":
                    descriptions.append(str(tt).strip())
                else:
                    descriptions.append("unknown")
    elif "trial_type" in events_df.columns:
        descriptions = []
        for _, row in events_df.iterrows():
            tt = row.get("trial_type", "")
            if pd.notna(tt) and str(tt).strip() != "":
                descriptions.append(str(tt).strip())
            else:
                descriptions.append("unknown")
    else:
        descriptions = ["unknown"] * len(events_df)
    
    onsets = []
    durations = []
    for _, row in events_df.iterrows():
        onset = float(row["onset"]) if pd.notna(row.get("onset")) else 0.0
        dur = float(row["duration"]) if pd.notna(row.get("duration")) else 0.0
        onsets.append(onset)
        durations.append(dur)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS003570Kernel:
    """Dataset-specific kernel for OpenNeuro ds003570."""

    KERNEL_ID = "openneuro_ds003570"
    DATASET_NAME = "OpenNeuro ds003570"
    CITATION = "DOI 10.1016/j.neuroimage.2021.118458"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        eeg_file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        bids_dir = _find_bids_dir(eeg_file_path)
        subject_id = _extract_subject_id(eeg_file_path)
        
        # Read participants.tsv for subject info
        participants_tsv = _find_participants_tsv(bids_dir) if bids_dir else None
        participants_info = {}
        if participants_tsv and subject_id:
            participants_info = _read_participants_row(participants_tsv, subject_id)
        
        # Build eegunity_description with required fields
        age = participants_info.get("age", "unknown")
        sex = _map_sex(participants_info.get("sex", "unknown"))
        handedness = _map_handedness(participants_info.get("handedness", participants_info.get("hand", "unknown")))
        
        # Determine amplifier and cap from dataset context
        # ds003570 uses BrainVision amplifier and standard 10-20 cap
        amplifier = "BrainVision"
        cap = "standard_1020"
        
        # Get original description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        # Read and apply events from events.tsv
        # The raw .set files may have empty event fields, so we must use events.tsv
        events_tsv = _find_events_tsv(eeg_file_path)
        events_df = _read_events_tsv(events_tsv) if events_tsv else None
        
        # Always set annotations from events.tsv if available
        # This ensures events are present even if raw file has no native triggers
        if events_df is not None and len(events_df) > 0:
            annotations = _events_to_annotations(events_df)
            raw.set_annotations(annotations)
        elif raw.annotations is None or len(raw.annotations) == 0:
            # If no events.tsv and no native annotations, set empty annotations
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
                "dataset_name": self.DATASET_NAME,
                "citation": self.CITATION,
                "subject_id": subject_id if subject_id else "unknown",
            }
        })
        
        # Ensure channel types are set correctly
        # Set EEG channels
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) > 0:
            # Check if channel types need to be set
            for ch_name in raw.ch_names:
                if ch_name in _STANDARD_10_20_CHANNELS or ch_name.startswith(("Fp", "F", "T", "C", "P", "O", "AF", "FC", "FT", "CP", "TP", "PO", "M", "CB")):
                    if raw.info["chs"][raw.ch_names.index(ch_name)]["kind"] != mne.io.constants.FIFF.FIFFV_EEG_CH:
                        raw.set_channel_types({ch_name: "eeg"})
        
        # Set montage if not already set
        try:
            current_montage = raw.get_montage()
            if current_montage is None:
                raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        return raw


KERNEL = OpenNeuroDS003570Kernel()