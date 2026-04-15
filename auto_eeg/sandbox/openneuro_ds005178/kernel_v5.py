"""Ear-EEG Sleep Monitoring 2023 (EESM23) stage1 kernel for EEGUnity.

Dataset: openneuro_ds005178
Source: https://openneuro.org/datasets/ds005178
DOI: 10.3389/fnins.2023.987578, 10.1038/s41597-025-04579-8

Ear-EEG sleep monitoring dataset with 5 in-ear EEG channels at 250 Hz.
Sleep stage annotations (W/N1/N2/N3/REM) are stored in BIDS events.tsv files.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


_SLEEP_STAGE_LABELS = [
    "sleep_stage_W",
    "sleep_stage_N1",
    "sleep_stage_N2",
    "sleep_stage_N3",
    "sleep_stage_REM",
]


def _detect_subject(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-(\d+)", file_path)
    return match.group(1) if match else "unknown"


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root directory."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return None


def _load_subject_info(bids_root: str, subject_id: str) -> Tuple[str, str]:
    """Load subject age and sex from BIDS participants.tsv."""
    df = _read_participants_tsv(bids_root)
    if df is None:
        return "unknown", "unknown"
    
    subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
    if subject_col not in df.columns:
        return "unknown", "unknown"
    
    subject_row = df[df[subject_col] == f"sub-{subject_id}"]
    if subject_row.empty:
        return "unknown", "unknown"
    
    row = subject_row.iloc[0]
    
    age_val = row.get("age", "unknown")
    if pd.notna(age_val):
        age = str(int(age_val)) if isinstance(age_val, float) else str(age_val)
    else:
        age = "unknown"
    
    sex_val = row.get("sex", row.get("gender", "unknown"))
    if pd.notna(sex_val):
        sex_lower = str(sex_val).strip().lower()
        if sex_lower in ["m", "male", "f", "female"]:
            sex = "male" if sex_lower.startswith("m") else "female"
        else:
            sex = "unknown"
    else:
        sex = "unknown"
    
    return age, sex


def _find_bids_root(file_path: str) -> str:
    """Find BIDS root directory from a file path."""
    parts = file_path.split(os.sep)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].startswith("sub-"):
            return os.sep.join(parts[:i])
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] in ["eeg", "ses-001", "ses-003"]:
            continue
        candidate = os.sep.join(parts[:i])
        if os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    return os.path.dirname(file_path)


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for ear-EEG channel naming."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for i in range(1, 6):
        old_name = f"ch{i}"
        if old_name in existing:
            if i <= 4:
                rename_map[old_name] = f"E{i}"
            else:
                rename_map[old_name] = "REF"
    
    for i in range(1, 6):
        old_name = f"EEG {i}"
        if old_name in existing:
            if i <= 4:
                rename_map[old_name] = f"E{i}"
            else:
                rename_map[old_name] = "REF"
    
    ear_eeg_aliases = {
        "E1": ["E1", "e1", "LE", "L"],
        "E2": ["E2", "e2", "RE", "R"],
        "E3": ["E3", "e3", "LRef", "LR"],
        "E4": ["E4", "e4", "RRef", "RR"],
        "REF": ["REF", "ref", "GND", "Ground"],
    }
    for target, aliases in ear_eeg_aliases.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _set_ear_eeg_montage(raw: mne.io.BaseRaw) -> None:
    """Set approximate montage for ear-EEG channels."""
    try:
        ch_names = raw.ch_names
        montage_names = []
        positions = []
        
        for ch in ch_names:
            ch_upper = ch.upper()
            if ch_upper in ["E1", "E3"]:
                montage_names.append(ch)
                positions.append((-0.08, -0.05, 0.0))
            elif ch_upper in ["E2", "E4"]:
                montage_names.append(ch)
                positions.append((0.08, -0.05, 0.0))
            elif ch_upper in ["REF"]:
                montage_names.append(ch)
                positions.append((0.0, 0.08, 0.0))
        
        if len(positions) >= 2:
            dig_points = [
                {
                    "kind": mne.io.constants.FIFF.FIFFV_POINT_EEG,
                    "ident": i,
                    "r": np.array(pos),
                    "frame": "head",
                }
                for i, pos in enumerate(positions)
            ]
            montage = mne.channels.DigMontage(dig_points=dig_points, ch_names=montage_names)
            raw.set_montage(montage, on_missing="warn")
        else:
            raw.set_montage("standard_1020", on_missing="warn")
    except Exception:
        pass


def _load_sleep_events(eeg_dir: str) -> Optional[mne.Annotations]:
    """Load sleep stage events from BIDS events.tsv file."""
    import glob
    
    events_files = glob.glob(os.path.join(eeg_dir, "*_events.tsv"))
    if not events_files:
        return None
    
    events_path = events_files[0]
    
    try:
        events_df = pd.read_csv(events_path, sep="\t")
        
        label_col = None
        for col in ["trial_type", "value", "event_label", "event_name"]:
            if col in events_df.columns:
                label_col = col
                break
        
        if label_col is None:
            return None
        
        onset_col = "onset" if "onset" in events_df.columns else "timestamp"
        duration_col = "duration" if "duration" in events_df.columns else None
        
        sleep_mask = events_df[label_col].astype(str).str.startswith("sleep_stage_")
        sleep_events = events_df[sleep_mask].copy()
        
        if sleep_events.empty:
            return None
        
        onsets = sleep_events[onset_col].astype(float).values
        durations = [0.0] * len(onsets)
        if duration_col and duration_col in sleep_events.columns:
            durations = sleep_events[duration_col].fillna(0.0).astype(float).values
        
        descriptions = sleep_events[label_col].astype(str).values
        annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
        
        return annotations
    except Exception:
        return None


class EEGUnityKernel:
    """EEGUnity kernel for openneuro_ds005178 Ear-EEG Sleep dataset."""
    
    KERNEL_ID = "openneuro_ds005178"
    
    eegunity_description: Dict[str, str] = {
        "age": "unknown",
        "sex": "unknown",
        "amplifier": "unknown",
        "cap": "in-ear electrodes",
        "handedness": "unknown",
    }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        bids_root = _find_bids_root(str(udataset))
        
        file_path = row.get("file_path", row.get("path", ""))
        subject_id = _detect_subject(file_path)
        
        if subject_id != "unknown":
            age, sex = _load_subject_info(bids_root, subject_id)
            if age != "unknown":
                self.eegunity_description["age"] = age
            if sex != "unknown":
                self.eegunity_description["sex"] = sex
        
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        _set_ear_eeg_montage(raw)
        
        eeg_dir = os.path.dirname(file_path)
        annotations = _load_sleep_events(eeg_dir)
        if annotations is not None:
            raw.set_annotations(annotations)
        
        return raw


KERNEL = EEGUnityKernel()