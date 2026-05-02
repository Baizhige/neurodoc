"""Healthy Brain Network (HBN) EEG - Release 4 stage1 kernel for EEGUnity.

Dataset: openneuro_ds005508 | 324 subjects | 129 channels | 500 Hz
Paradigm: Multi-task developmental battery including resting state,
sensory contrast detection, surrounding suppression, sequence learning,
and symbol search tasks.

Source: https://openneuro.org/datasets/ds005508
Reference: https://doi.org/10.1038/sdata.2017.40
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# HARDWARE & CAP METADATA (known from dataset documentation)
# ============================================================================
# Amplifier: BrainAmp Series (Brain Products) - inferred by LLM, needs human review
# Cap: ActiveTwo system with 128-channel EEG cap (Ag/AgCl) - inferred by LLM, needs human review
# Reference: Alexander et al. (2022) NeuroImage 119348 - inferred by LLM, needs human review

_DATASET_AMPLIFIER = "BrainAmp Series"  # inferred by LLM, needs human review
_DATASET_CAP = "ActiveTwo 128-channel (Ag/AgCl)"  # inferred by LLM, needs human review


# ============================================================================
# CHANNEL MAPPING - Biosemi 128-channel layout
# ============================================================================
# Source: HBN dataset uses Biosemi ActiveTwo 128-channel system
# Standard Biosemi 128-channel naming: A1-A32 (left hemisphere),
# B1-B32 (midline), C1-C32 (right hemisphere), plus extras
# Annotator: LLM, 2026-04-08, from dataset technical documentation

_BIOSEMI_128_NAMES = [
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
    "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
    "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24",
    "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8",
    "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
    "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24",
    "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
    "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8",
    "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
    "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24",
    "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
    "EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8",
    "Status"
]

# MNE-compatible Biosemi 128 montage names
_BIOSEMI_128_MONOTAGE = "biosemi128"


# ============================================================================
# EVENT MAPPING (from analysis.md Event Structure)
# ============================================================================
_EVENT_ID_MAP = {
    "stim_ON": 1,
    "fixpoint_ON": 2,
    "contrastTrial_start": 3,
    "left_buttonPress": 4,
    "right_buttonPress": 5,
    "right_target": 6,
    "left_target": 7,
    "break cnt": 8,
    "trialResponse": 9,
    "instructed_toOpenEyes": 10,
    "instructed_toCloseEyes": 11,
    "boundary": 12,
    "resting_start": 13,
    "9999": 99,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for Biosemi 128-channel naming convention.
    
    HBN EEG files may have various channel naming formats.
    This function attempts to normalize them to standard Biosemi 128 names.
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    # Check for numbered EEG channels (EEG001, EEG002, etc.)
    for i, ch in enumerate(ch_names):
        if ch.startswith("EEG") and ch[3:].isdigit():
            idx = int(ch[3:]) - 1  # 0-indexed
            if idx < len(_BIOSEMI_128_NAMES):
                rename_map[ch] = _BIOSEMI_128_NAMES[idx]
        # Check for A1, A2, B1, B2 style naming (already standard)
        elif ch in _BIOSEMI_128_NAMES:
            pass  # No rename needed
        # Check for alternative naming like "EEG A1", "EEG-A1"
        elif ch.startswith("EEG"):
            rest = ch[3:].strip()
            if rest in _BIOSEMI_128_NAMES:
                rename_map[ch] = rest
    
    return rename_map


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if it exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(
    row: pd.Series,
    participants_df: pd.DataFrame,
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or row data.
    
    Parameters
    ----------
    row : pd.Series
        Locator row containing subject_id and other metadata
    participants_df : pd.DataFrame
        DataFrame from participants.tsv
        
    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness
    """
    subject_id = str(row.get("subject_id", row.get("participant_id", "")))
    
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    # Try to get from participants.tsv
    if not participants_df.empty:
        if "participant_id" in participants_df.columns:
            match = participants_df[
                participants_df["participant_id"] == subject_id
            ]
            if not match.empty:
                row_data = match.iloc[0]
                
                # Age field
                if "age" in row_data.index:
                    age_val = row_data["age"]
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)
                
                # Sex field
                if "sex" in row_data.index:
                    sex_val = row_data["sex"]
                    if pd.notna(sex_val):
                        sex_lower = str(sex_val).lower().strip()
                        if sex_lower in ["m", "male", "f", "female"]:
                            info["sex"] = "male" if sex_lower.startswith("m") else "female"
                
                # Handedness field
                if "handedness" in row_data.index:
                    hand_val = row_data["handedness"]
                    if pd.notna(hand_val):
                        hand_lower = str(hand_val).lower().strip()
                        if hand_lower.startswith("r"):
                            info["handedness"] = "right"
                        elif hand_lower.startswith("l"):
                            info["handedness"] = "left"
    
    # Fallback: try to get from row
    if info["age"] == "unknown" and "age" in row.index:
        age_val = row.get("age")
        if pd.notna(age_val):
            info["age"] = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)
    
    if info["sex"] == "unknown" and "sex" in row.index:
        sex_val = row.get("sex")
        if pd.notna(sex_val):
            sex_lower = str(sex_val).lower().strip()
            if sex_lower in ["m", "male", "f", "female"]:
                info["sex"] = "male" if sex_lower.startswith("m") else "female"
    
    return info


def _create_mne_annotations_from_raw(
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Convert raw events/triggers to MNE annotations.
    
    HBN EEG data uses BrainVision format with embedded events.
    This function extracts events from annotations or stim channels.
    """
    try:
        # Try to get existing annotations
        orig_annotations = raw.annotations
        if len(orig_annotations) > 0:
            # Map existing annotations to canonical event names
            descriptions = []
            for desc in orig_annotations.description:
                # Try to find canonical name by ID
                mapped = desc
                for canonical_name, event_id in _EVENT_ID_MAP.items():
                    if str(event_id) == str(desc) or canonical_name == str(desc):
                        mapped = canonical_name
                        break
                descriptions.append(mapped)
            
            return mne.Annotations(
                onset=orig_annotations.onset,
                duration=orig_annotations.duration,
                description=descriptions,
            )
    except Exception:
        pass
    
    # If no annotations, try stim channel
    stim_channels = [ch for ch in raw.ch_names if "stim" in ch.lower() or ch.lower() == "status"]
    if stim_channels:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        # Remap to canonical names
        descriptions = []
        for event_arr in events:
            event_code = event_arr[2]
            desc = str(event_code)
            for canonical_name, canonical_id in _EVENT_ID_MAP.items():
                if canonical_id == event_code:
                    desc = canonical_name
                    break
            descriptions.append(desc)
        
        return mne.Annotations(
            onset=events[:, 0] / raw.info["sfreq"],
            duration=np.zeros(len(events)),
            description=descriptions,
        )
    
    return mne.Annotations(onset=[], duration=[], description=[])


class HBNKernel:
    """Stage1 kernel for Healthy Brain Network (HBN) EEG Release 4.
    
    This kernel handles:
    - Standard 128-channel Biosemi naming
    - Resting state event extraction (eyes-open/eyes-closed)
    - Multi-task paradigm event mapping
    - Subject metadata from participants.tsv
    """

    KERNEL_ID: str = "openneuro-ds005508-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to HBN EEG data.
        
        Parameters
        ----------
        udataset : object
            EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object
        row : pd.Series
            Locator row with at least 'File Path' and 'subject_id'
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata
        """
        # Get dataset path for participants.tsv
        dataset_path = getattr(udataset, "path", "")
        
        # Load participants metadata
        participants_df = _load_participants_tsv(dataset_path)
        
        # Get subject info
        subject_info = _get_subject_info(row, participants_df)
        
        # Build channel rename map and rename channels
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage if channels match standard 1020/128
        try:
            montage = mne.channels.make_standard_montage(_BIOSEMI_128_MONOTAGE)
            # Only set montage for EEG channels that exist
            eeg_chs = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if len(eeg_chs) >= 64:  # At least half of standard channels
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional for non-standard caps
        
        # Create annotations from raw events
        annotations = _create_mne_annotations_from_raw(raw)
        raw.set_annotations(annotations)
        
        # Build description dict
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DATASET_AMPLIFIER,
                "cap": _DATASET_CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = HBNKernel()