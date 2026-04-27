"""OpenNeuro ds005114 stage1 kernel for EEGUnity.

DPX (Dot Pattern Expectancy) Cognitive Control Task dataset.
Sub-acute mild traumatic brain injury (mTBI) patients vs healthy controls.
65 channels, 500 Hz, BIDS format.

Source: https://openneuro.org/datasets/ds005114
Reference: DOI 10.1016/j.neuropsychologia.2019.107125
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne


# Admin events to exclude from training
_ADMIN_EVENTS_EXCLUDE = {
    "STATUS",
    "Practice: filler trigger",
}


# Target events for DPX classification (raw meta labels)
_TARGET_EVENTS = {
    "CueAOnset",
    "CueBOnset",
    "Probe_aX_onset",
    "Probe_aY_onset",
    "Probe_bY_onset",
}


# Standard 10-20 channel rename map for common variants
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "FP1",
    "Fp2": "FP2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "FT7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "FT8",
    "P7": "TP7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "TP8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "AFz": "AFz",
    "FCz": "FCz",
    "CPz": "CPz",
    "POz": "POz",
    "PO10": "PO10",
    "PO9": "PO9",
}


def _load_participants_tsv(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load participant metadata from BIDS participants.tsv."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    subject_dict: Dict[str, Dict[str, str]] = {}
    
    if not os.path.exists(participants_path):
        return subject_dict
    
    try:
        import pandas as pd
        df = pd.read_csv(participants_path, sep="\t")
        
        subj_col = None
        for col in df.columns:
            if "participant" in col.lower() and "id" in col.lower():
                subj_col = col
                break
        if subj_col is None and len(df.columns) > 0:
            subj_col = df.columns[0]
        
        if subj_col is None:
            return subject_dict
        
        for _, row in df.iterrows():
            subj_id = str(row.get(subj_col, ""))
            if not subj_id.startswith("sub-"):
                subj_id = f"sub-{subj_id}" if subj_id else ""
            
            age_val = str(row.get("age", "unknown")).strip()
            sex_val = str(row.get("sex", row.get("gender", "unknown"))).strip().lower()
            handed_val = str(row.get("hand", row.get("handedness", "unknown"))).strip().lower()
            
            if sex_val in ["m", "male"]:
                sex_val = "male"
            elif sex_val in ["f", "female"]:
                sex_val = "female"
            else:
                sex_val = "unknown"
            
            if handed_val in ["r", "right"]:
                handed_val = "right"
            elif handed_val in ["l", "left"]:
                handed_val = "left"
            else:
                handed_val = "unknown"
            
            subject_dict[subj_id] = {
                "age": age_val,
                "sex": sex_val,
                "handedness": handed_val,
            }
    except Exception:
        pass
    
    return subject_dict


def _detect_file_format(file_path: str) -> str:
    """Detect EEG file format from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".vhdr":
        return "brainvision"
    elif ext == ".edf":
        return "edf"
    elif ext == ".bdf":
        return "bdf"
    elif ext == ".set":
        return "eeglab"
    elif ext == ".fif":
        return "fif"
    return "auto"


def _apply_channel_renaming(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed."""
    rename_map = {}
    ch_names_lower = {ch.lower() for ch in raw.ch_names}
    
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_RENAME_MAP:
            new_name = _CHANNEL_RENAME_MAP[ch_name]
            if new_name != ch_name:
                if new_name.lower() not in ch_names_lower:
                    rename_map[ch_name] = new_name
        else:
            for src, dst in _CHANNEL_RENAME_MAP.items():
                if ch_name.upper() == src.upper() and ch_name != dst:
                    if dst.lower() not in ch_names_lower:
                        rename_map[ch_name] = dst
                    break
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _apply_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard 10-20 montage if most channels match."""
    try:
        montage_names = [
            "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
            "T7", "C3", "CZ", "C4", "T8", "P7", "P3", 
            "PZ", "P4", "P8", "O1", "OZ", "O2",
            "AF3", "AF4", "AF7", "AF8", "F1", "F2", "F5", "F6",
            "FC1", "FC2", "FC5", "FC6", "FT7", "FT8",
            "C1", "C2", "C5", "C6", "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
            "TP7", "TP8", "P1", "P2", "P5", "P6",
            "PO1", "PO2", "PO3", "PO4", "PO7", "PO8",
            "PO9", "PO10",
        ]
        
        matched = sum(1 for ch in raw.ch_names if ch.upper() in [n.upper() for n in montage_names])
        
        if len(raw.ch_names) >= 32 and matched >= len(raw.ch_names) * 0.7:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass
    except Exception:
        pass
    
    return raw


def _extract_subject_id(row) -> str:
    """Extract subject ID from row dictionary or File Path."""
    for col in ["subject_id", "participant_id", "Subject", "Subject ID"]:
        if col in row and row[col]:
            return str(row[col])
    
    file_path = row.get("File Path", row.get("file_path", ""))
    if file_path:
        match = re.search(r"sub-[A-Za-z0-9]+", file_path)
        if match:
            return match.group(0)
    
    return "unknown"


def _get_dataset_root(row) -> str:
    """Extract dataset root path from file path."""
    file_path = row.get("File Path", row.get("file_path", ""))
    if file_path:
        parts = os.path.dirname(file_path).split(os.sep)
        for i in range(len(parts), 0, -1):
            check_path = os.path.join(os.sep.join(parts[:i]), "participants.tsv")
            if os.path.exists(check_path):
                return os.sep.join(parts[:i])
    return ""


@dataclass
class OpenNeuroDS005114Kernel:
    """Stage1 kernel for OpenNeuro ds005114 (DPX Cognitive Control Task)."""

    KERNEL_ID: str = "openneuro-ds005114-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to DPX task EEG data."""
        # Extract subject ID and dataset root
        subject_id = _extract_subject_id(row)
        dataset_root = _get_dataset_root(row)
        
        # Load participant metadata
        participants_data = _load_participants_tsv(dataset_root)
        
        # Get subject-specific metadata with defaults
        if subject_id in participants_data:
            subj_meta = participants_data[subject_id]
            age = subj_meta.get("age", "unknown")
            sex = subj_meta.get("sex", "unknown")
            handedness = subj_meta.get("handedness", "unknown")
        else:
            age = "unknown"
            sex = "unknown"
            handedness = "unknown"
        
        # Determine amplifier info from raw info if available
        amplifier = "unknown"
        if raw.info.get("meas_date") is not None:
            amplifier = raw.info.get("device_info", {}).get("type", "unknown")
        if amplifier == "unknown":
            # Try to infer from channel types or other info
            n_channels = len(raw.ch_names)
            if n_channels == 64 or n_channels == 65:
                amplifier = "BioSemi64"
            elif n_channels >= 128:
                amplifier = "BioSemi128"
        
        # Determine cap type from number of channels (common for this dataset)
        cap = "unknown"
        n_channels = len(raw.ch_names)
        if n_channels == 64 or n_channels == 65:
            cap = "BioSemi64-channel"
        elif n_channels >= 128:
            cap = "BioSemi128-channel"
        
        # Apply channel renaming
        raw = _apply_channel_renaming(raw)
        
        # Apply montage if appropriate
        raw = _apply_montage_if_possible(raw)
        
        # Set eegunity_description with all required fields
        raw._eegunity_description = {
            "age": str(age),
            "sex": str(sex),
            "amplifier": str(amplifier),
            "cap": str(cap),
            "handedness": str(handedness),
        }
        
        return raw


KERNEL = OpenNeuroDS005114Kernel()