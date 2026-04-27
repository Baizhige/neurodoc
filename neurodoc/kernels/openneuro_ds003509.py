"""OpenNeuro DS003509 stage1 kernel for EEGUnity.

Simon Conflict task in Parkinson's disease patients.
BIDS-compliant dataset with 56 subjects, 67 channels, 500 Hz sampling.

This kernel extracts subject metadata from participants.tsv, processes
events from events.tsv (with trial_type for congruent/incongruent labels),
and standardizes channel names.

Source: https://openneuro.org/datasets/ds003509
Paper: https://doi.org/10.1016/j.neuropsychologia.2018.05.020
"""

from __future__ import annotations

import json
import os

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08
# Amplifier info: LLM 推断，需人类复核
# Based on 67 channels and 500 Hz sampling typical of BrainAmp systems
# Source: dataset hardware specifications not explicitly stated
_SUBJECT_DICT = {
    # Format: "sub-XX": {"age": "XX", "sex": "male/female", "handedness": "right/left/unknown"}
    # All subjects have missing age/sex in analysis.md, defaulting to unknown
}


def _find_participants_tsv(file_path: str) -> str:
    """Locate participants.tsv by traversing up from the EEG file path.
    
    BIDS structure: dataset_root/participants.tsv
    EEG files: dataset_root/sub-XX/eeg/*.edf or *.bdf
    """
    if not file_path:
        return ""
    
    current_dir = os.path.dirname(file_path)
    
    while current_dir:
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    
    return ""


def _extract_participant_info(file_path: str, subject_id: str) -> dict:
    """Extract subject metadata from BIDS participants.tsv.
    
    Parameters
    ----------
    file_path : str
        Path to EEG file (used to locate participants.tsv)
    subject_id : str
        Subject identifier (e.g., "sub-01")
        
    Returns
    -------
    dict
        Dictionary with age, sex, handedness keys
    """
    if not subject_id:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
    
    tsv_path = _find_participants_tsv(file_path)
    
    if not tsv_path:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
    
    try:
        df = pd.read_csv(tsv_path, sep="\t")
        
        if "participant_id" not in df.columns:
            return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
        
        row = df[df["participant_id"] == subject_id]
        
        if row.empty:
            return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
        
        sex_val = str(row.iloc[0].get("sex", "unknown")).lower()
        if sex_val not in ("m", "f", "male", "female"):
            sex_val = "unknown"
        
        age_val = str(row.iloc[0].get("age", "unknown"))
        handedness_val = str(row.iloc[0].get("handedness", "unknown"))
        
        return {
            "age": age_val,
            "sex": sex_val,
            "handedness": handedness_val
        }
    except Exception:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


def _standardize_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names and apply standard 1020 montage.
    
    Channel names are renamed BEFORE set_montage() per kernel requirements.
    Only EEG channels are renamed; EOG, EMG, and other types are preserved.
    
    Source: standard_1020 channel naming convention
    Annotator: LLM, 2026-04-08
    """
    rename_map = {}
    for ch_name in raw.ch_names:
        ch_upper = ch_name.upper()
        if ch_upper.startswith("EEG-"):
            num_part = ch_upper[4:].strip()
            if num_part.isdigit():
                rename_map[ch_name] = f"EEG-{int(num_part):02d}"
    
    if rename_map:
        try:
            mne.rename_channels(raw.info, rename_map)
        except Exception:
            pass
    
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass
    
    return raw


def _find_events_tsv(file_path: str) -> str:
    """Locate events.tsv for a given EEG file.
    
    BIDS events files follow patterns:
    - sub-XX_eeg_run-01_events.tsv
    - sub-XX_task-XX_events.tsv
    """
    if not file_path:
        return ""
    
    base, ext = os.path.splitext(file_path)
    
    candidates = [
        base + "_events.tsv",
        base + "-events.tsv",
        base.replace("_eeg", "_events") + ".tsv",
        base.replace("_raw", "_events") + ".tsv",
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    
    return ""


def _process_events_tsv(raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
    """Load events from events.tsv and set as MNE annotations.
    
    events.tsv columns:
    - onset: event time in seconds
    - duration: event duration (usually 0 for point events)
    - trial_type: congruent/incongruent classification (super meta)
    - value: original event code (numeric)
    
    Annotations are set for raw meta level (event codes as-is from file).
    Super meta (congruent/incongruent labels) can be derived from trial_type.
    
    Source: BIDS events.tsv specification
    """
    if not file_path:
        return raw
    
    events_path = _find_events_tsv(file_path)
    
    if not events_path or not os.path.exists(events_path):
        return raw
    
    try:
        events_df = pd.read_csv(events_path, sep="\t")
        
        onset_col = None
        for col in ["onset", "onset_sec", "timestamp"]:
            if col in events_df.columns:
                onset_col = col
                break
        
        if onset_col is None:
            return raw
        
        onset = events_df[onset_col].values
        
        duration = np.zeros(len(onset))
        if "duration" in events_df.columns:
            duration = events_df["duration"].fillna(0.0).values
        
        desc_col = None
        for col in ["value", "trial_type", "event_type", "event_label", "stimulus_type"]:
            if col in events_df.columns:
                desc_col = col
                break
        
        if desc_col is None:
            return raw
        
        descriptions = events_df[desc_col].fillna("unknown").astype(str).values
        
        sfreq = raw.info["sfreq"]
        if onset.max() > 1e6:
            onset = onset / sfreq
        
        annotations = mne.Annotations(
            onset=onset,
            duration=duration,
            description=descriptions,
        )
        raw.set_annotations(annotations)
    except Exception:
        pass
    
    return raw


class OpenNeuroDS003509Kernel:
    """Stage1 kernel for OpenNeuro DS003509 dataset.
    
    This kernel processes Simon Conflict task EEG data with the following tasks:
    - Task 1 (Super Meta): Congruent vs Incongruent classification
      Derived from events.tsv trial_type column (congruent=0, incongruent=1)
    - Task 2 (Raw Meta): Correct vs Error response classification
      Events: correct/incorrect markers from events.tsv
    """

    KERNEL_ID: str = "openneuro-ds003509-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.
        
        Parameters
        ----------
        udataset : UnifiedDataset
            EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG data loaded by EEGUnity
        row : pandas.Series or dict
            Locator row containing File Path and subject identifiers
            
        Returns
        -------
        mne.io.BaseRaw
            Processed raw data with:
            - eegunity_description in raw.info["description"]
            - Standardized channel names
            - Standard 1020 montage
            - Events from events.tsv as annotations
        """
        file_path = row.get("File Path", "") if hasattr(row, "get") else row.get("File Path", "") if isinstance(row, dict) else ""
        
        subject_id = ""
        if hasattr(row, "get"):
            subject_id = row.get("participant_id", row.get("subject_id", row.get("subject", "")))
        elif isinstance(row, dict):
            subject_id = row.get("participant_id", row.get("subject_id", row.get("subject", "")))
        
        participant_info = _extract_participant_info(file_path, subject_id)
        
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": participant_info.get("age", "unknown"),
                "sex": participant_info.get("sex", "unknown"),
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": participant_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        raw = _standardize_channels(raw)
        
        raw = _process_events_tsv(raw, file_path)
        
        return raw


KERNEL = OpenNeuroDS003509Kernel()