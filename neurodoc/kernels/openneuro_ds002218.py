"""OpenNeuro ds002218 stage1 kernel for EEGUnity.

Auditory and Visual Rhythm Omission EEG dataset.
32 channels, 256 Hz, BioSemi amplifier.
BIDS-compliant dataset with EDF files and events.tsv sidecars.

Paradigm: rhythmic tones and flashes with occasional omissions.
Event mapping confirmed from task-Experiment_events.json:
  - 1: BioSemi STATUS hardware marker (high count, interleaved)
  - 2: Auditory rhythm non-omission trial (regular tone)
  - 3: BioSemi STATUS hardware marker (high count, interleaved)
  - 4: Auditory rhythm omission trial (expected tone missing)
  - 5: Visual rhythm non-omission trial (regular flash)
  - 6: Visual rhythm omission trial (expected flash missing)

Source: https://openneuro.org/datasets/ds002218
Reference: DOI 10.1111/ejn.15314, 10.1101/2020.11.29.402701
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Event mapping confirmed from task-Experiment_events.json and paper evidence
# Annotator: LLM, 2026-04-08, inferred from dataset documentation and published papers
# LLM 推断，需人类复核
_EVENT_MAP: Dict[int, str] = {
    1: "STATUS_marker",
    2: "auditory_non-omission",
    3: "STATUS_marker",
    4: "auditory_omission",
    5: "visual_non-omission",
    6: "visual_omission",
}

# BioSemi standard 32-channel layout for ActiCAP
# Standard 10-20 system with 32 electrode positions
# Source: BioSemi 32-channel standard montage documentation
# Annotator: LLM, 2026-04-08, inferred from BioSemi standard specifications
# LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-Fp1": "Fp1",
    "EEG-Fp2": "Fp2",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-Fz": "Fz",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-T7": "T7",
    "EEG-C3": "C3",
    "EEG-Cz": "Cz",
    "EEG-C4": "C4",
    "EEG-T8": "T8",
    "EEG-P7": "P7",
    "EEG-P3": "P3",
    "EEG-Pz": "Pz",
    "EEG-P4": "P4",
    "EEG-P8": "P8",
    "EEG-O1": "O1",
    "EEG-Oz": "Oz",
    "EEG-O2": "O2",
    "EEG-FC1": "FC1",
    "EEG-FC2": "FC2",
    "EEG-FC5": "FC5",
    "EEG-FC6": "FC6",
    "EEG-CP1": "CP1",
    "EEG-CP2": "CP2",
    "EEG-CP5": "CP5",
    "EEG-CP6": "CP6",
    "EEG-FT9": "FT9",
    "EEG-FT10": "FT10",
    "EEG-TP9": "TP9",
    "EEG-TP10": "TP10",
}

# Kernel requirements configuration
kernel_requirements = {
    "required_info_fields": ["age", "sex", "handedness"],
    "required_native_misc": [],
    "derived_misc_channels": [],
}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a BIDS EEG file."""
    # BIDS naming: sub-XX_task-YYY_run-ZZ_eeg.edf -> sub-XX_task-YYY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.bdf", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run level
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    if "_run-" in file_name:
        parts = file_name.split("_run-")
        run_part = parts[1].split("_eeg")[0]
        # Try all run-matching events in same directory
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv") and parts[0] in f:
                return os.path.join(dir_path, f)
    
    # Search in same directory for any matching events.tsv
    sub_id = None
    if "sub-" in file_name:
        sub_id = file_name.split("sub-")[1].split("_")[0]
        sub_id = "sub-" + sub_id
    
    if sub_id and dir_path:
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv") and sub_id in f:
                return os.path.join(dir_path, f)
    
    return None


def _load_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Load events.tsv file."""
    if not events_path or not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t", encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(events_path, sep="\t", encoding="latin-1")
        except Exception:
            return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from dataset root."""
    current_dir = os.path.dirname(file_path)
    # Walk up to find dataset root (contains participants.tsv)
    for _ in range(5):  # Limit search depth
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _load_participants_tsv(participants_path: str) -> Optional[pd.DataFrame]:
    """Load participants.tsv file."""
    if not participants_path or not os.path.exists(participants_path):
        return None
    try:
        return pd.read_csv(participants_path, sep="\t", encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(participants_path, sep="\t", encoding="latin-1")
        except Exception:
            return None


def _get_subject_info(participants_df: Optional[pd.DataFrame], file_path: str) -> Dict[str, str]:
    """Extract subject info from participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    if participants_df is None or participants_df.empty:
        return info
    
    # Extract subject ID from file path
    sub_id = None
    file_name = os.path.basename(file_path)
    if "sub-" in file_name:
        sub_id = file_name.split("sub-")[1].split("_")[0]
        sub_id = "sub-" + sub_id
    
    if sub_id is None:
        return info
    
    # Find matching row
    pid_col = None
    for col in participants_df.columns:
        if col.lower() in ["participant_id", "participant id", "subject_id", "subject id"]:
            pid_col = col
            break
    
    if pid_col is None:
        # Try first column
        pid_col = participants_df.columns[0]
    
    # Match subject
    match = participants_df[participants_df[pid_col].astype(str) == sub_id]
    if match.empty:
        # Try without "sub-" prefix
        match = participants_df[participants_df[pid_col].astype(str) == sub_id.replace("sub-", "")]
    
    if match.empty:
        return info
    
    row = match.iloc[0]
    
    # Extract age
    for col in participants_df.columns:
        if col.lower() in ["age", "age_years", "age(years)"]:
            val = row.get(col)
            if pd.notna(val):
                info["age"] = str(int(float(val))) if str(val).replace('.', '').isdigit() else str(val)
            break
    
    # Extract sex
    for col in participants_df.columns:
        if col.lower() in ["sex", "gender", "sex_mf"]:
            val = row.get(col)
            if pd.notna(val):
                val_str = str(val).lower().strip()
                if val_str in ["f", "female", "w", "woman"]:
                    info["sex"] = "female"
                elif val_str in ["m", "male", "man"]:
                    info["sex"] = "male"
                else:
                    info["sex"] = "unknown"
            break
    
    # Extract handedness
    for col in participants_df.columns:
        if col.lower() in ["handedness", "hand", "dominant_hand"]:
            val = row.get(col)
            if pd.notna(val):
                val_str = str(val).lower().strip()
                if val_str in ["r", "right"]:
                    info["handedness"] = "right"
                elif val_str in ["l", "left"]:
                    info["handedness"] = "left"
                else:
                    info["handedness"] = "unknown"
            break
    
    return info


def _build_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.Annotations:
    """Build MNE annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return None
    
    # Required columns in BIDS events.tsv
    onset_col = None
    for col in events_df.columns:
        if col.lower() in ["onset", "onsets"]:
            onset_col = col
            break
    
    duration_col = None
    for col in events_df.columns:
        if col.lower() in ["duration", "durations"]:
            duration_col = col
            break
    
    trial_type_col = None
    for col in events_df.columns:
        if col.lower() in ["trial_type", "trial type", "event_type", "event type", "stim_type"]:
            trial_type_col = col
            break
    
    if onset_col is None:
        return None
    
    onsets = events_df[onset_col].values
    durations = events_df[duration_col].values if duration_col else np.zeros(len(onsets))
    descriptions = events_df[trial_type_col].values.astype(str) if trial_type_col else np.array(["unknown"] * len(onsets))
    
    # Filter to valid onsets within data range
    valid_mask = (onsets >= 0) & (onsets < raw.times[-1])
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    if len(onsets) == 0:
        return None
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS002218Kernel:
    KERNEL_ID = "openneuro_ds002218"
    KERNEL_NAME = "OpenNeuro ds002218 - Auditory/Visual Rhythm Omission"
    DATASET_DESCRIPTION = "Auditory and Visual Rhythm Omission EEG dataset (BioSemi 32ch, 256Hz)"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from udataset row
        file_path = str(row.get("file_path", row.get("filepath", "")))
        
        # Load participants.tsv for subject info
        participants_path = _find_participants_tsv(file_path)
        participants_df = _load_participants_tsv(participants_path)
        subject_info = _get_subject_info(participants_df, file_path)
        
        # Load and apply events from events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _load_events_tsv(events_path)
            if events_df is not None and not events_df.empty:
                annot = _build_annotations_from_events_tsv(raw, events_df)
                if annot is not None:
                    raw.set_annotations(annot)
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Build eegunity_description with required fields from participants.tsv
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "BioSemi ActiveTwo",
            "cap": "BioSemi 32-channel ActiCAP",
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS002218Kernel()