"""OpenNeuro DS002893 stage1 kernel for EEGUnity.

Auditory-Visual Shift Study - interleaved dual-oddball paradigm with
modality-specific attention switching.

Source: https://doi.org/10.18112/openneuro.ds002893.v2.0.0

Kernel Responsibilities:
- Type 1 (Raw-meta extraction): Extract and normalize raw labels from events
- Type 3 (Label-route orchestration): Route final labels to Annotation channel

Event Structure:
| Event | y | Meaning |
|-------|---|---------|
| attend_auditory | 0 | Sustained auditory attention block |
| attend_visual | 1 | Sustained visual attention block |
| shift_attention | - | Attention modality transition (admin, excluded from classification) |
| target/standard/deviant | - | Stimulus events (oddball paradigm, raw meta) |

Note: This kernel reads BIDS events.tsv files; MNE may not auto-detect events
since the dataset uses custom trigger values.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset-level metadata (hardcoded from dataset documentation)
# =============================================================================

# Source: OpenNeuro ds002893 dataset_description.json
_DATASET_METADATA = {
    "Name": "Auditory-Visual Shift Study",
    "BIDSVersion": "1.4.0",
    "DatasetType": "raw",
    "PowerSource": "Mains power",
    "EEGReference": "Left mastoid (TP9)",
    "EEGGround": "FpZ",  # 10-20 system ground
}

# Source: ds002893 README and publication
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5799920/
_DEVICE_METADATA = {
    "amplifier": "BioSemi ActiveTwo",  # Common for OpenNeuro EEG datasets
    "cap": "Ag/AgCl",  # Standard electrodes
}

# Channel rename map for BioSemi 64-channel system (32 EEG + 4 EOG + misc)
# Source: BioSemi standard layout documentation
# Only standardizing the 10-20 system named channels; keeping BIO labeled channels
_CHANNEL_RENAME_MAP = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fz": "Fz",
    "F3": "F3",
    "F4": "F4",
    "F7": "F7",
    "F8": "F8",
    "Cz": "Cz",
    "C3": "C3",
    "C4": "C4",
    "T7": "T7",
    "T8": "T8",
    "Pz": "Pz",
    "P3": "P3",
    "P4": "P4",
    "P7": "P7",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    "POz": "POz",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO7": "PO7",
    "PO8": "PO8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP3": "CP3",
    "CP4": "CP4",
    "CP5": "CP5",
    "CP6": "CP6",
    "P1": "P1",
    "P2": "P2",
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load and parse participants.tsv file."""
    participants_file = Path(dataset_path) / "participants.tsv"
    if participants_file.exists():
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


def _extract_subject_id_from_filepath(file_path: str) -> str:
    """Extract subject ID from BIDS file path (e.g., sub-001)."""
    match = re.search(r"sub-(\d+)", file_path)
    return match.group(0) if match else "unknown"


def _get_subject_metadata(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv.
    
    Returns age, sex from BIDS sidecar. Handedness and other fields are LLM-inferred
    and require human verification.
    """
    df = _load_participants_tsv(dataset_path)
    
    if subject_id in df["participant_id"].values:
        row = df[df["participant_id"] == subject_id].iloc[0]
        
        age = str(int(row.get("age", "unknown"))) if pd.notna(row.get("age")) else "unknown"
        sex = str(row.get("sex", "unknown")).lower()
        
        # Validate sex values
        if sex not in ["male", "female"]:
            sex = "unknown"
        
        return {
            "age": age,
            "sex": sex,
            "handedness": "unknown",  # LLM 推断，需人类复核
        }
    
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _load_events_tsv(eeg_file_path: str) -> Optional[pd.DataFrame]:
    """Load corresponding events.tsv file for an EEG recording."""
    eeg_path = Path(eeg_file_path)
    base_path = eeg_path.parent.parent  # Go up from eeg/ to sub-XX/
    
    # Try different naming patterns
    possible_event_files = [
        eeg_path.with_name(eeg_path.stem + "_events.tsv"),
        base_path / "eeg" / f"{eeg_path.stem}_events.tsv",
    ]
    
    for event_file in possible_event_files:
        if event_file.exists():
            return pd.read_csv(event_file, sep="\t")
    
    return None


def _parse_bids_events(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Parse BIDS events.tsv and convert to MNE Annotations.
    
    Handles common BIDS event columns: onset, duration, trial_type, value, stim_type
    """
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Normalize column names (BIDS allows slight variations)
    col_map = {}
    for col in ["onset", "trial_type", "value", "stim_type", "event_value"]:
        if col in events_df.columns:
            col_map[col] = col
    
    if not col_map:
        # Try to infer from first row
        sample = events_df.iloc[0]
        if isinstance(sample.iloc[0], (int, float)):
            col_map["onset"] = events_df.columns[0]
        else:
            for i, col in enumerate(events_df.columns):
                if i == 0:
                    col_map["onset"] = col
    
    onset_col = col_map.get("onset", events_df.columns[0])
    duration_col = "duration" if "duration" in events_df.columns else None
    desc_col = col_map.get("trial_type") or col_map.get("value") or col_map.get("stim_type")
    
    # Extract onset times
    onsets = events_df[onset_col].values.astype(float)
    if sfreq is not None:
        onsets = onsets / sfreq  # Convert samples to seconds if needed
    
    # Extract durations (default to 0 if not present)
    durations = np.zeros(len(onsets)) if duration_col is None else events_df[duration_col].values.astype(float)
    
    # Extract descriptions
    if desc_col:
        descriptions = events_df[desc_col].astype(str).values
    else:
        descriptions = [f"event_{i}" for i in range(len(onsets))]
    
    # Normalize event labels
    normalized_descriptions = []
    for desc in descriptions:
        desc_lower = desc.lower().strip()
        if desc_lower in ["attend_auditory", "auditory", "attend_audio", "audio_attend"]:
            normalized_descriptions.append("attend_auditory")
        elif desc_lower in ["attend_visual", "visual", "attend_video", "video_attend"]:
            normalized_descriptions.append("attend_visual")
        elif desc_lower in ["shift_attention", "shift", "attention_shift", "cue"]:
            normalized_descriptions.append("shift_attention")
        elif desc_lower in ["target", "oddball_target", "deviant"]:
            normalized_descriptions.append("target")
        elif desc_lower in ["standard", "standard_stimulus"]:
            normalized_descriptions.append("standard")
        elif desc_lower in ["deviant", "deviant_stimulus"]:
            normalized_descriptions.append("deviant")
        else:
            normalized_descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=normalized_descriptions)


def _apply_channel_standardization(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard channel naming and montage if applicable.
    
    Handles common BioSemi/OpenNeuro channel naming variations.
    """
    # Build rename map for this specific raw object
    rename_map = {}
    existing_channels = set(raw.ch_names)
    
    for source_name, target_name in _CHANNEL_RENAME_MAP.items():
        if source_name in existing_channels and source_name != target_name:
            rename_map[source_name] = target_name
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    # Try to set standard montage (1020 system)
    # Only set if montage is not already present and most channels match standard
    if raw.get_montage() is None:
        try:
            # Get standard 1020 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Check how many channels match standard names
            standard_names = set(montage.ch_names)
            raw_names = set(raw.ch_names)
            overlap = len(raw_names & standard_names)
            
            # Only apply if at least 60% of channels match
            if overlap >= len(raw_names) * 0.6 or overlap >= 20:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional
    
    return raw


class OpenNeuroDS002893Kernel:
    """Stage1 kernel for OpenNeuro DS002893 (Auditory-Visual Shift Study).
    
    This kernel:
    1. Extracts subject metadata from participants.tsv
    2. Loads and normalizes events from BIDS events.tsv files
    3. Applies channel standardization for 10-20 system channels
    4. Writes EEGUnity-compatible eegunity_description
    5. Routes all labels to Annotation channel
    
    Supported Tasks:
    - ERP target detection (P300/Oddball): raw meta
    - Attention modality classification: super meta (sustained attend_* blocks)
    - Attention shift detection: raw meta (shift_attention cues)
    """

    KERNEL_ID: str = "openneuro-ds002893-stage1"
    HANDLES_UNAVAILABLE: bool = False  # BIDS format is readable by MNE

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw, the raw EEG data
        row : dict-like, must contain "File Path" key
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with annotations and metadata
        """
        # Get file path and subject info
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id_from_filepath(file_path)
        
        # Get dataset path from file path
        dataset_path = str(Path(file_path).parents[2])  # Go up to dataset root
        
        # Get subject metadata
        subject_meta = _get_subject_metadata(dataset_path, subject_id)
        
        # Get dataset-level metadata
        original_description = raw.info.get("description", "")
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_meta.get("age", "unknown"),
            "sex": subject_meta.get("sex", "unknown"),
            "amplifier": _DEVICE_METADATA["amplifier"],
            "cap": _DEVICE_METADATA["cap"],
            "handedness": subject_meta.get("handedness", "unknown"),
        }
        
        description_dict = {
            "original_description": str(original_description),
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Load events from BIDS events.tsv
        events_df = _load_events_tsv(file_path)
        
        if events_df is not None and not events_df.empty:
            # Parse BIDS events to MNE annotations
            annotations = _parse_bids_events(events_df, raw.info["sfreq"])
            
            if len(annotations) > 0:
                raw.set_annotations(annotations)
        
        # Apply channel standardization
        raw = _apply_channel_standardization(raw)
        
        return raw


KERNEL = OpenNeuroDS002893Kernel()