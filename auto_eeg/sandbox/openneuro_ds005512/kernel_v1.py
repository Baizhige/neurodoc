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
_SUBJECT_METADATA: Dict[str, Dict[str, Any]] = {
    # Format: sub-<ID>: {"age": "XX", "sex": "male/female", "handedness": "unknown"}
    # Actual values loaded from participants.tsv at runtime
}

# ============================================================================
# DSM-V Diagnosis Labels (for super meta)
# ============================================================================
# Source: HBN participants.tsv (diagnostic columns: ADHD, ODD, ANX, MDD, ASD, SLD, CD)
# Annotator: Human, 2026-04-08
_DIAGNOSIS_COLUMNS: List[str] = [
    "ADHD", "ODD", "ANX", "MDD", "ASD", "SLD", "CD"
]
# Binary vector per subject (1=diagnosis present, 0=no diagnosis)

# ============================================================================
# Channel Mapping for HBN 128-channel HydroCel GSN
# ============================================================================
# Source: HBN EEG equipment documentation (BrainAmp MR plus with 128-channel HydroCel GSN)
# Annotator: LLM (model: unknown), 2026-04-08 - 需要人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard HydroCel GSN channel naming to 10-20 standard names
    # HBN uses E128 layout with standard naming
    "FP1": "Fp1",
    "FP2": "Fp2",
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
    
    # Try to find in participants.tsv
    participants_df = _load_participants_tsv(dataset_path)
    
    if not participants_df.empty and "participant_id" in participants_df.columns:
        match = participants_df[participants_df["participant_id"] == subject_id]
        if not match.empty:
            row_data = match.iloc[0]
            age = str(int(row_data.get("age", 0))) if pd.notna(row_data.get("age")) else "unknown"
            sex = str(row_data.get("sex", "unknown")).lower()
            handedness = str(row_data.get("handedness", "unknown")).lower()
            return {"age": age, "sex": sex, "handedness": handedness}
    
    # LLM inference - 需要人类复核
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
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
        # Check if channel needs renaming based on mapping
        if ch_name in _CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    # Try to set standard 1020 montage (HBN uses HydroCel GSN 128)
    try:
        # Use standard 1020 for 129-channel (standard 128 + 1 reference)
        montage = mne.channels.make_standard_montage("standard_1020")
        
        # Get existing channel names that should be in standard montage
        montage_names = set(montage.ch_names)
        current_names = set(raw.ch_names)
        
        # Only set montage if most channels match standard names
        matching = len(current_names & montage_names)
        if matching >= 50:  # At least 50 channels match standard names
            raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass  # Skip montage if standard names don't match
    
    return raw


def _process_events(raw: mne.io.BaseRaw, events_tsv_path: Optional[str] = None) -> mne.io.BaseRaw:
    """Process events from BIDS events.tsv or existing annotations.
    
    Handles HBN-specific event labels from events.tsv:
    - stim_ON (contrast detection stimulus onset)
    - fixpoint_ON (trial start cue)
    - left_target / right_target (target stimuli)
    - instructed_toCloseEyes / resting_start (eyes-closed resting)
    - etc.
    """
    # If events.tsv exists, load and create annotations
    if events_tsv_path and os.path.exists(events_tsv_path):
        try:
            events_df = pd.read_csv(events_tsv_path, sep="\t")
            
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                # Standard BIDS events.tsv format
                sfreq = raw.info["sfreq"]
                
                onsets = events_df["onset"].values
                durations = events_df.get("duration", pd.Series([0.0] * len(events_df))).values
                descriptions = events_df["trial_type"].astype(str).values
                
                # Fill missing durations with 0
                durations = np.nan_to_num(durations, nan=0.0)
                
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations.tolist(),
                    description=descriptions.tolist(),
                )
                raw.set_annotations(annotations)
                
        except Exception:
            pass  # Fall back to existing annotations
    
    # If no annotations exist, try to extract from stim channels
    if raw.annotations is None or len(raw.annotations) == 0:
        try:
            events, event_ids = mne.events_from_annotations(raw)
            
            # Map numeric event IDs to HBN event labels
            new_event_id = {v: k for k, v in _EVENT_ID_MAP.items()}
            
            # Create new annotations with HBN labels
            descriptions = []
            for event_id in events[:, 2]:
                label = new_event_id.get(event_id, f"event_{event_id}")
                descriptions.append(label)
            
            annotations = mne.Annotations(
                onset=events[:, 0] / raw.info["sfreq"],
                duration=[0.0] * len(events),
                description=descriptions,
            )
            raw.set_annotations(annotations)
        except Exception:
            pass  # No events found
    
    return raw


class HBNEEGWKernel:
    """Stage1 kernel for Healthy Brain Network (HBN) EEG dataset.
    
    Handles:
    - BIDS format EEG data (129 channels, 500 Hz)
    - Resting-state epochs (eyes-closed, 40s blocks)
    - Contrast detection task events
    - DSM-V psychiatric diagnosis labels (super meta)
    """
    
    KERNEL_ID: str = "openneuro-ds005512-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to HBN EEG data.
        
        Parameters
        ----------
        udataset : EEGUnity UnifiedDataset
            Dataset context with path information
        raw : mne.io.BaseRaw
            In-memory MNE Raw object
        row : pd.Series
            Locator row with File Path and metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata
        """
        file_path = row.get("File Path", "")
        dataset_path = udataset.path if hasattr(udataset, "path") else os.path.dirname(file_path)
        
        # ====================================================================
        # Step 1: Update description with subject and device metadata
        # ====================================================================
        subject_info = _get_subject_info(row, dataset_path)
        diagnosis_vector = _get_diagnosis_vector(row, dataset_path)
        
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp MR plus",  # HBN standard amplifier
                "cap": "HydroCel GSN 128",  # HBN uses 128-channel HydroCel
                "handedness": subject_info["handedness"],
            },
            # DSM-V diagnosis vector for super meta (7 categories)
            "diagnosis_vector": diagnosis_vector,
            "diagnosis_columns": _DIAGNOSIS_COLUMNS,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # ====================================================================
        # Step 2: Rename channels and set montage (BEFORE set_montage)
        # ====================================================================
        raw = _rename_channels(raw)
        
        # ====================================================================
        # Step 3: Process events from BIDS events.tsv
        # ====================================================================
        # Try to find corresponding events.tsv
        bids_dir = os.path.dirname(os.path.dirname(file_path))  # .../sub-XX/eeg/ -> .../sub-XX/
        eeg_dir = os.path.dirname(file_path)  # .../sub-XX/eeg/
        
        # Common patterns for events.tsv location
        possible_events_paths = [
            file_path.replace("_eeg.rdata", "_events.tsv").replace(".vhdr", "_events.tsv"),
            file_path.replace("_eeg.set", "_events.tsv"),
            os.path.join(eeg_dir, os.path.basename(file_path).split(".")[0] + "_events.tsv"),
            os.path.join(eeg_dir, "events.tsv"),
        ]
        
        events_tsv = None
        for path in possible_events_paths:
            if os.path.exists(path):
                events_tsv = path
                break
        
        raw = _process_events(raw, events_tsv)
        
        # ====================================================================
        # Step 4: Add super meta annotations (DSM-V diagnosis labels)
        # ====================================================================
        # Create super meta annotations from diagnosis vector
        subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
        
        if diagnosis_vector and any(diagnosis_vector):
            # Subject has at least one diagnosis
            diagnosis_labels = []
            for i, col in enumerate(_DIAGNOSIS_COLUMNS):
                if diagnosis_vector[i] == 1:
                    diagnosis_labels.append(col)
            
            # Add diagnosis info as description annotation
            existing_annot = raw.annotations
            if existing_annot is not None and len(existing_annot) > 0:
                # Append diagnosis info to last annotation description
                last_desc = existing_annot.description[-1] if len(existing_annot.description) > 0 else ""
                if isinstance(last_desc, str) and "diagnosis:" not in last_desc:
                    new_desc = last_desc + f" [diagnosis: {','.join(diagnosis_labels)}]"
                    # Create new annotations array with updated description
                    new_descriptions = list(existing_annot.description)
                    new_descriptions[-1] = new_desc
                    
                    updated_annot = mne.Annotations(
                        onset=existing_annot.onset,
                        duration=existing_annot.duration,
                        description=new_descriptions,
                    )
                    raw.set_annotations(updated_annot)
        
        # ====================================================================
        # Step 5: Final info cleanup
        # ====================================================================
        # Ensure device info is properly set
        if raw.info.get("device_info") is None:
            raw.info["device_info"] = "BrainAmp MR plus"
        
        return raw


KERNEL = HBNEEGWKernel()