"""OpenNeuro ds005345 (Le Petit Prince Multitalker) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds005345
EEG recorded during 7T fMRI with 64-channel actiCAP system.
Paradigm: naturalistic listening to single-talker and multi-talker speech.

Source: DOI 10.1038/s41597-025-05158-7 (Nature Scientific Data, 2025)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Known metadata from dataset documentation
# Source: Dataset description and DOI 10.1038/s41597-025-05158-7
# Annotator: Human, 2025-06-20
_DATASET_METADATA = {
    "amplifier": "BrainAmp MR plus",  # 7T MRI-compatible EEG system
    "cap": "actiCAP 64-channel",  # From "Comment/actiCAP Data On" marker
}

# Event mapping from raw event codes to human-readable labels
# Source: DOI 10.1101/2025.04.03.646958 (validation paper)
# Annotator: Human, 2025-06-20
_EVENT_MAP = {
    11: "Stimulus/S 11",
    31: "Stimulus/S 31",
    32: "Stimulus/S 32",
    33: "Stimulus/S 33",
    34: "Stimulus/S 34",
}


def _load_bids_participants(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_info(row: pd.Series, dataset_path: str) -> Dict[str, Any]:
    """Extract subject info from BIDS participants.tsv or infer defaults."""
    subject_id = row.get("participant_id", "unknown")
    participants_df = _load_bids_participants(dataset_path)
    
    if not participants_df.empty and "participant_id" in participants_df.columns:
        subj_row = participants_df[participants_df["participant_id"] == subject_id]
        if not subj_row.empty:
            age = subj_row.iloc[0].get("age", "unknown")
            sex = subj_row.iloc[0].get("sex", "unknown")
            handedness = subj_row.iloc[0].get("hand", "unknown")
            
            # Normalize sex to lowercase
            if pd.notna(sex):
                sex = str(sex).lower()
                if sex not in ["male", "female"]:
                    sex = "unknown"
            else:
                sex = "unknown"
            
            # Normalize handedness
            if pd.notna(handedness):
                handedness = str(handedness).lower()
                if handedness not in ["right", "left"]:
                    handedness = "unknown"
            else:
                handedness = "unknown"
            
            # Age as string
            if pd.notna(age):
                age = str(int(float(age)))
            else:
                age = "unknown"
            
            return {"age": age, "sex": sex, "handedness": handedness}
    
    # Defaults for missing metadata
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _build_annotations_from_events(
    raw: mne.io.BaseRaw, 
    events_tsv_path: str
) -> mne.Annotations:
    """Build MNE annotations from BIDS *_events.tsv file."""
    if not os.path.exists(events_tsv_path):
        # Fallback: try to extract from existing annotations
        existing = raw.annotations
        if len(existing) > 0:
            return existing
        return mne.Annotations([], [], [])
    
    events_df = pd.read_csv(events_tsv_path, sep="\t")
    
    # Standard BIDS events columns
    onset_col = None
    duration_col = None
    value_col = None
    
    for col in ["onset", "timestamp"]:
        if col in events_df.columns:
            onset_col = col
            break
    
    for col in ["duration", "duration_s"]:
        if col in events_df.columns:
            duration_col = col
            break
    
    for col in ["value", "trial_type", "stim_type", "event_code"]:
        if col in events_df.columns:
            value_col = col
            break
    
    if onset_col is None:
        return mne.Annotations([], [], [])
    
    onsets = events_df[onset_col].values
    durations = events_df[duration_col].values if duration_col else [0.0] * len(onsets)
    descriptions = events_df[value_col].values if value_col else ["unknown"] * len(onsets)
    
    # Convert onset to seconds if needed (handle milliseconds)
    if onsets.max() > raw.times[-1] * 2:  # Likely in ms
        onsets = onsets / 1000.0
    
    annotations = mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist() if hasattr(durations, 'tolist') else list(durations),
        description=[str(d) for d in descriptions],
    )
    
    return annotations


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 naming if needed."""
    # Standard actiCAP 64-channel layout follows 10-20 system
    ch_names = raw.ch_names
    
    # Check if channels are already standard (e.g., 'FC3', 'Cz')
    standard_count = sum(1 for ch in ch_names if any(s in ch for s in ["F", "C", "P", "T", "O", "z"]))
    
    if standard_count > 40:  # Likely already standard naming
        return raw
    
    # Otherwise, channels might be in BrainVision format or numbered
    # Common pattern: 'O1' -> 'O1', 'Cz' -> 'Cz' are standard
    # If numbered (e.g., '1', '2'), try to map based on actiCAP 64 layout
    
    rename_map = {}
    for i, ch in enumerate(ch_names):
        if ch.isdigit() or ch.startswith("EEG"):
            # Try to infer standard name from position
            # actiCAP 64 channels follow 10-20 system
            pass  # Keep original if cannot determine
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    # Try to set montage if standard names detected
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw = raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Montage not critical for processing
    
    return raw


class OpenNeuroDS005345Kernel:
    """Stage1 kernel for OpenNeuro ds005345 (Le Petit Prince Multitalker)."""

    KERNEL_ID: str = "openneuro-ds005345-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (in-memory)
        row : Locator row with 'File Path' and 'participant_id'

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw with updated description and annotations
        """
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(os.path.dirname(file_path))  # Go up from sub-*/eeg/
        subject_id = row.get("participant_id", "unknown")
        
        # Extract subject metadata
        subject_info = _extract_subject_info(row, dataset_path)
        
        # Build eegunity_description
        eegunity_desc = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "handedness": subject_info["handedness"],
            "amplifier": _DATASET_METADATA["amplifier"],
            "cap": _DATASET_METADATA["cap"],
        }
        
        # Build description JSON
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Find and load events.tsv
        eeg_dir = os.path.dirname(file_path)
        events_files = [
            os.path.join(eeg_dir, f) 
            for f in os.listdir(eeg_dir) 
            if f.endswith("_events.tsv")
        ]
        
        if events_files:
            annotations = _build_annotations_from_events(raw, events_files[0])
            raw = raw.set_annotations(annotations)
        
        # Rename channels to standard names before set_montage
        raw = _rename_channels_to_standard(raw)
        
        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that match standard names
            present_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if len(present_channels) >= 32:  # At least half of 64 channels
                raw = raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
        
        return raw


KERNEL = OpenNeuroDS005345Kernel()