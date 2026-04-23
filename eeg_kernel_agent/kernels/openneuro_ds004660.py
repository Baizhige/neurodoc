"""OpenNeuro ds004660 (TNO Military Cognitive Workload) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds004660
DOI: https://doi.org/10.18112/openneuro.ds004660.v1.0.2

A military-relevant cognitive workload study conducted at TNO research institute,
involving hierarchically encoded task conditions with 5-digit numeric trigger codes.

This kernel handles BIDS-standard EDF files with standard_1020 channel layout,
extracts events from sidecar events.tsv when needed, and maps channel names
to standard 10-20 positions.

Tasks supported:
- 6-class cognitive workload classification
- 3-class cognitive workload classification
- Stimulus pair type classification

Source: TNO research institute, Netherlands
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Channel rename map
# Based on: OpenNeuro ds004660 channel naming convention (EEG-01..EEG-38)
# Standard 1020 positions. Annotated by LLM, 2026-04-08
# LLM 推断，需人类复核
# ---------------------------------------------------------------------------
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-01": "Fp1",
    "EEG-02": "Fp2",
    "EEG-03": "F7",
    "EEG-04": "F3",
    "EEG-05": "Fz",
    "EEG-06": "F4",
    "EEG-07": "F8",
    "EEG-08": "T7",
    "EEG-09": "C3",
    "EEG-10": "Cz",
    "EEG-11": "C4",
    "EEG-12": "T8",
    "EEG-13": "P7",
    "EEG-14": "P3",
    "EEG-15": "Pz",
    "EEG-16": "P4",
    "EEG-17": "P8",
    "EEG-18": "O1",
    "EEG-19": "Oz",
    "EEG-20": "O2",
    "EEG-21": "Fpz",
    "EEG-22": "AF3",
    "EEG-23": "AF4",
    "EEG-24": "FC5",
    "EEG-25": "FC1",
    "EEG-26": "FC2",
    "EEG-27": "FC6",
    "EEG-28": "CP5",
    "EEG-29": "CP1",
    "EEG-30": "CP2",
    "EEG-31": "CP6",
    "EEG-32": "PO3",
    "EEG-33": "PO4",
    "EEG-34": "F1",
    "EEG-35": "F2",
    "EEG-36": "C1",
    "EEG-37": "C2",
    "EEG-38": "P1",
}

# EOG channels (if present)
_EOG_RENAME_MAP: Dict[str, str] = {
    "EOG-left": "EOG-left",
    "EOG-right": "EOG-right",
    "EOG-up": "EOG-up",
    "EOG-down": "EOG-down",
}

# System/trigger channel to preserve (if present)
_MISC_CHANNEL_NAMES = {"stim", "trigger", "marker", "status"}


# ---------------------------------------------------------------------------
# Required info fields from participants.tsv
# ---------------------------------------------------------------------------
_REQUIRED_INFO_FIELDS: List[str] = ["age", "sex", "amplifier", "cap", "handedness"]


# ---------------------------------------------------------------------------
# Required native misc channels (ensure ch_type is 'misc')
# ---------------------------------------------------------------------------
_REQUIRED_NATIVE_MISC: List[str] = []


# ---------------------------------------------------------------------------
# Derived misc channels to create
# ---------------------------------------------------------------------------
_DERIVED_MISC_CHANNELS: List[str] = []


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BIDS naming: sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_eeg.<ext>
    # events.tsv: sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_events.tsv
    base = file_path
    # Remove extension
    for ext in [".edf", ".bdf", ".set", ".fif", ".eeg", ".vhdr", ".vmrk"]:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try without run index
    run_pattern = r"_run-\d+"
    base_no_run = re.sub(run_pattern, "", base)
    if base_no_run != base:
        events_tsv = base_no_run + "_events.tsv"
        if os.path.exists(events_tsv):
            return events_tsv
    
    # Try task-level events.tsv in same directory
    dir_path = os.path.dirname(file_path)
    for fname in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
        if fname.endswith("_events.tsv"):
            return os.path.join(dir_path, fname)
    
    return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_tsv):
        return {}
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        # Find subject row
        sub_col = None
        for col in df.columns:
            if col.lower() in ["participant_id", "subject_id", "participant"]:
                sub_col = col
                break
        
        if sub_col is None:
            return {}
        
        # Normalize subject ID format
        if not subject_id.startswith("sub-"):
            search_id = f"sub-{subject_id}"
        else:
            search_id = subject_id
        
        row = df[df[sub_col] == search_id]
        if row.empty:
            # Try without sub- prefix
            row = df[df[sub_col] == subject_id.replace("sub-", "")]
        
        if row.empty:
            return {}
        
        info = {}
        for col in df.columns:
            if col == sub_col:
                continue
            val = row.iloc[0][col]
            if pd.isna(val):
                info[col] = "unknown"
            else:
                info[col] = str(val)
        return info
    except Exception:
        return {}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    # Try to extract sub-<label> from path
    match = re.search(r"sub-([a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    # Fallback: use directory name
    return os.path.basename(os.path.dirname(os.path.dirname(file_path)))


def _normalize_sex(sex_val: Optional[str]) -> str:
    """Normalize sex value to lowercase standard."""
    if sex_val is None:
        return "unknown"
    sex_lower = str(sex_val).lower().strip()
    if sex_lower in ("m", "male", "1"):
        return "male"
    elif sex_lower in ("f", "female", "2"):
        return "female"
    return "unknown"


def _normalize_age(age_val: Any) -> str:
    """Normalize age value to string."""
    if age_val is None or pd.isna(age_val):
        return "unknown"
    try:
        age_float = float(age_val)
        if age_float <= 0 or np.isnan(age_float):
            return "unknown"
        # Check if it's actually an integer
        if age_float == int(age_float):
            return str(int(age_float))
        return str(age_float)
    except (ValueError, TypeError):
        age_str = str(age_val).strip()
        if age_str.lower() in ("n/a", "na", "unknown", "", "none"):
            return "unknown"
        return age_str


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for this raw object."""
    rename_map = {}
    existing = set(raw.ch_names)
    
    # EEG channels
    for old_name, new_name in _CHANNEL_RENAME_MAP.items():
        if old_name in existing and new_name not in existing:
            rename_map[old_name] = new_name
    
    # EOG channels
    for old_name, new_name in _EOG_RENAME_MAP.items():
        if old_name in existing and new_name not in existing:
            rename_map[old_name] = new_name
    
    return rename_map


def _events_tsv_to_annotations(events_tsv_path: str, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
        if df.empty:
            return None
        
        # Required columns
        if "onset" not in df.columns:
            return None
        
        onsets = df["onset"].values.astype(float)
        
        # Duration
        if "duration" in df.columns:
            durations = df["duration"].fillna(0.0).values.astype(float)
        else:
            durations = np.zeros_like(onsets)
        
        # Description / trial_type
        if "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values
        elif "value" in df.columns:
            descriptions = df["value"].astype(str).values
        elif "event_type" in df.columns:
            descriptions = df["event_type"].astype(str).values
        else:
            descriptions = np.array(["event"] * len(onsets))
        
        # Ensure non-negative durations
        durations = np.maximum(durations, 0.0)
        
        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)
    except Exception:
        return None


class OpenNeuroDS004660Kernel:
    """Stage-1 kernel for OpenNeuro ds004660 (TNO Military Cognitive Workload)."""
    
    KERNEL_ID = "openneuro_ds004660"
    DATASET_NAME = "OpenNeuro ds004660 - TNO Military Cognitive Workload"
    DATASET_DOI = "10.18112/openneuro.ds004660.v1.0.2"
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # 1. Channel renaming to standard 10-20
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # 2. Set channel types
        new_ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_RENAME_MAP.values():
                new_ch_types[ch_name] = "eeg"
            elif ch_name in _EOG_RENAME_MAP.values():
                new_ch_types[ch_name] = "eog"
            elif ch_name.lower() in _MISC_CHANNEL_NAMES:
                new_ch_types[ch_name] = "misc"
        
        if new_ch_types:
            raw = raw.set_channel_types(new_ch_types)
        
        # 3. Extract subject info from participants.tsv
        dataset_path = udataset.path if hasattr(udataset, "path") else str(udataset)
        file_path = row["File Path"] if "File Path" in row else ""
        subject_id = _extract_subject_id(file_path)
        participants_info = _read_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in participants_info:
                val = participants_info[field]
                if field == "age":
                    eegunity_description[field] = _normalize_age(val)
                elif field == "sex":
                    eegunity_description[field] = _normalize_sex(val)
                else:
                    eegunity_description[field] = str(val) if val is not None else "unknown"
            else:
                eegunity_description[field] = "unknown"
        
        # 4. Set montage if not already set
        if raw.get_montage() is None:
            try:
                raw = raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
            except Exception:
                pass
        
        # 5. Load events from events.tsv if raw has no annotations
        if len(raw.annotations) == 0:
            events_tsv = _find_events_tsv(file_path)
            if events_tsv:
                annots = _events_tsv_to_annotations(events_tsv, raw.info["sfreq"])
                if annots is not None:
                    raw = raw.set_annotations(annots)
        
        # 6. Set description
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS004660Kernel()