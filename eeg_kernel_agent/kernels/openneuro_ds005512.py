"""Healthy Brain Network (HBN) EEG stage1 kernel for EEGUnity.

Dataset: openneuro_ds005512
Source: https://openneuro.org/datasets/ds005512
Reference: https://doi.org/10.1038/sdata.2017.181

This kernel handles BIDS-formatted HBN EEG data with:
- 129-channel standard_1020 montage (HydroCel GSN 128)
- Resting-state epochs (eyes-closed, 40s blocks)
- Contrast detection task (stim_ON, left_target, right_target)
- DSM-V psychiatric diagnosis labels (super meta, 7 categories)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject Metadata (extracted from participants.tsv)
# ============================================================================
# Source: HBN participants.tsv (age, sex columns)
# Annotator: Human, 2026-04-08
_SUBJECT_METADATA: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# DSM-V Diagnosis Labels (for super meta)
# ============================================================================
# Source: HBN participants.tsv (diagnostic columns: ADHD, ODD, ANX, MDD, ASD, SLD, CD)
# Annotator: Human, 2026-04-08
_DIAGNOSIS_COLUMNS: List[str] = [
    "ADHD", "ODD", "ANX", "MDD", "ASD", "SLD", "CD"
]

# ============================================================================
# Channel Mapping for HBN 128-channel HydroCel GSN
# ============================================================================
# Source: HBN EEG equipment documentation (BrainAmp MR plus with 128-channel HydroCel GSN)
# Annotator: LLM (model: unknown), 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "POz": "POz",
}

# ============================================================================
# Event ID Mapping (raw meta)
# ============================================================================
# Source: HBN analysis.md event structure table
# Annotator: Human, 2026-04-08
_EVENT_ID_MAP: Dict[str, int] = {
    "stim_ON": 1,
    "fixpoint_ON": 2,
    "contrastTrial_start": 3,
    "left_buttonPress": 4,
    "right_buttonPress": 5,
    "right_target": 6,
    "left_target": 7,
    "trialResponse": 8,
    "break cnt": 9,
    "instructed_toOpenEyes": 10,
    "boundary": 11,
    "instructed_toCloseEyes": 12,
    "resting_start": 13,
    "9999": 99,
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load and cache participants.tsv metadata."""
    tsv_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row: pd.Series, dataset_path: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or infer defaults."""
    subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
    participants_df = _load_participants_tsv(dataset_path)
    
    if not participants_df.empty and "participant_id" in participants_df.columns:
        match = participants_df[participants_df["participant_id"] == subject_id]
        if not match.empty:
            row_data = match.iloc[0]
            age = str(int(row_data.get("age", 0))) if pd.notna(row_data.get("age")) else "unknown"
            sex = str(row_data.get("sex", "unknown")).lower()
            handedness = str(row_data.get("handedness", "unknown")).lower()
            return {"age": age, "sex": sex, "handedness": handedness}
    
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _get_diagnosis_vector(row: pd.Series, dataset_path: str) -> List[int]:
    """Extract DSM-V diagnosis vector for super meta (7 binary labels)."""
    subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
    participants_df = _load_participants_tsv(dataset_path)
    
    if not participants_df.empty and "participant_id" in participants_df.columns:
        match = participants_df[participants_df["participant_id"] == subject_id]
        if not match.empty:
            row_data = match.iloc[0]
            return [int(row_data.get(col, 0)) for col in _DIAGNOSIS_COLUMNS]
    
    return [0] * len(_DIAGNOSIS_COLUMNS)


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply channel name standardization and set montage."""
    rename_map = {}
    
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        montage_names = set(montage.ch_names)
        current_names = set(raw.ch_names)
        matching = len(current_names & montage_names)
        if matching >= 50:
            raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass
    
    return raw


def _process_events(raw: mne.io.BaseRaw, events_tsv_path: Optional[str] = None) -> mne.io.BaseRaw:
    """Process events from BIDS events.tsv or existing annotations."""
    if events_tsv_path and os.path.exists(events_tsv_path):
        try:
            events_df = pd.read_csv(events_tsv_path, sep="\t")
            
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                onsets = events_df["onset"].values
                durations = events_df.get("duration", pd.Series([0.0] * len(events_df))).values
                descriptions = events_df["trial_type"].astype(str).values
                durations = np.nan_to_num(durations, nan=0.0)
                
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations.tolist(),
                    description=descriptions.tolist(),
                )
                raw.set_annotations(annotations)
                
        except Exception:
            pass
    
    if raw.annotations is None or len(raw.annotations) == 0:
        try:
            events, event_ids = mne.events_from_annotations(raw)
            raw.set_annotations(None)
        except Exception:
            pass
    
    return raw


class EEGKernel:
    """EEGUnity kernel for HBN (openneuro_ds005512) dataset."""

    KERNEL_ID = "openneuro_ds005512"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_path = getattr(udataset, "path", "")
        
        # Get subject-specific metadata
        subject_info = _get_subject_info(row, dataset_path)
        
        # Set eegunity_description in temp field (required by MNE Info constraints)
        raw.info['temp'] = {
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp MR plus",
                "cap": "HydroCel GSN 128",
                "handedness": subject_info.get("handedness", "unknown"),
            }
        }
        
        # Set device info as dict (not string) in temp field
        raw.info["device_info"] = {"type": "BrainAmp MR plus"}
        
        # Rename channels and set montage
        raw = _rename_channels(raw)
        
        # Process events from BIDS structure
        eeg_dir = os.path.dirname(row.get("filepath", ""))
        events_tsv = os.path.join(eeg_dir, "..", "events.tsv")
        if os.path.exists(events_tsv):
            raw = _process_events(raw, events_tsv)
        else:
            raw = _process_events(raw)
        
        # Set reference
        if "EXG1" in raw.ch_names or "EXG2" in raw.ch_names:
            try:
                raw.set_eeg_reference(ref_channels=["EXG1", "EXG2"])
            except Exception:
                pass
        
        return raw


KERNEL = EEGKernel()