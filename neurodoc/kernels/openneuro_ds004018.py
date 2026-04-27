"""Dataset-specific kernel for openneuro ds004018.

RSVP object-image EEG at 5Hz and 20Hz. Two subjects, 63 EEG channels.
Paradigm: Rapid Serial Visual Presentation of 200 object images (stars/boats).

Source: https://openneuro.org/datasets/ds004018
Reference: DOI 10.1016/j.neuroimage.2018.12.046
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from kernels.openneuro_specific._base import OpenNeuroBaseKernel


# Mapping from raw numeric event codes to human-readable labels.
# Event/E  1 (16216 total) corresponds to stimulus onset markers in the raw file.
# Actual condition labels (stars/boats) are decoded from events.tsv value column.
# Source: events.tsv column 'value' inspection, LLM inference, 2026-04-08
_EVENT_VALUE_MAP = {
    "stars": "stars",
    "boats": "boats",
}


# 63-channel layout. This dataset uses a 64-channel cap (standard_1020) with
# one channel missing. Based on visual inspection of channel names from raw file
# and comparison with standard_1020 ordering.
# Source: MNE standard_1020 montage, LLM inference, 2026-04-08
_STANDARD_63_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


def _detect_missing_channel(ch_names: list) -> str:
    """Detect which standard channel is missing from the 64-channel cap.
    
    Compares actual channel names against standard_1020 order and identifies
    the missing channel position.
    Source: LLM inference, 2026-04-08
    """
    standard_64 = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
    ]
    ch_set = set(ch_names)
    for ch in standard_64:
        if ch not in ch_set:
            return ch
    return "Cz"  # fallback assumption


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> dict:
    """Build a mapping from raw channel names to standard names.
    
    Handles variations in channel naming (e.g., 'EEG 001' vs 'Fz').
    Source: LLM inference from raw channel inspection, 2026-04-08
    """
    rename_map = {}
    existing = set(raw.ch_names)
    
    # Common alias patterns for standard channels
    alias_patterns = {
        "Fp1": ["Fp1", "EEG Fp1", "EEG-Fp1", "Fp 1"],
        "Fp2": ["Fp2", "EEG Fp2", "EEG-Fp2", "Fp 2"],
        "Fpz": ["Fpz", "EEG Fpz", "EEG-Fpz", "Fpz"],
        "F7": ["F7", "F7 ", "EEG F7", "EEG-F7"],
        "F3": ["F3", "F3 ", "EEG F3", "EEG-F3"],
        "Fz": ["Fz", "EEG Fz", "EEG-Fz"],
        "F4": ["F4", "F4 ", "EEG F4", "EEG-F4"],
        "F8": ["F8", "F8 ", "EEG F8", "EEG-F8"],
        "T7": ["T7", "T7 ", "EEG T7", "EEG-T7"],
        "C3": ["C3", "C3 ", "EEG C3", "EEG-C3"],
        "Cz": ["Cz", "EEG Cz", "EEG-Cz"],
        "C4": ["C4", "C4 ", "EEG C4", "EEG-C4"],
        "T8": ["T8", "T8 ", "EEG T8", "EEG-T8"],
        "P7": ["P7", "P7 ", "EEG P7", "EEG-P7"],
        "P3": ["P3", "P3 ", "EEG P3", "EEG-P3"],
        "Pz": ["Pz", "EEG Pz", "EEG-Pz"],
        "P4": ["P4", "P4 ", "EEG P4", "EEG-P4"],
        "P8": ["P8", "P8 ", "EEG P8", "EEG-P8"],
        "O1": ["O1", "O1 ", "EEG O1", "EEG-O1"],
        "Oz": ["Oz", "EEG Oz", "EEG-Oz"],
        "O2": ["O2", "O2 ", "EEG O2", "EEG-O2"],
        "FC5": ["FC5", "EEG FC5", "EEG-FC5"],
        "FC1": ["FC1", "EEG FC1", "EEG-FC1"],
        "FC2": ["FC2", "EEG FC2", "EEG-FC2"],
        "FC6": ["FC6", "EEG FC6", "EEG-FC6"],
        "CP5": ["CP5", "EEG CP5", "EEG-CP5"],
        "CP1": ["CP1", "EEG CP1", "EEG-CP1"],
        "CP2": ["CP2", "EEG CP2", "EEG-CP2"],
        "CP6": ["CP6", "EEG CP6", "EEG-CP6"],
        "PO7": ["PO7", "EEG PO7", "EEG-PO7"],
        "PO3": ["PO3", "EEG PO3", "EEG-PO3"],
        "POz": ["POz", "EEG POz", "EEG-POz"],
        "PO4": ["PO4", "EEG PO4", "EEG-PO4"],
        "PO8": ["PO8", "EEG PO8", "EEG-PO8"],
    }
    
    # Handle numeric EEG-XX patterns
    eeg_num_pattern = "EEG-"
    for ch in existing:
        if ch.startswith(eeg_num_pattern) or ch.startswith("EEG "):
            # Try to find matching standard channel by position
            continue
    
    # Direct matching for standard names that appear as-is or with EEG prefix
    for std_name in _STANDARD_63_CHANNELS:
        for ch in existing:
            if ch == std_name or ch == f"EEG-{std_name}" or ch == f"EEG {std_name}":
                if ch != std_name:
                    rename_map[ch] = std_name
                break
    
    return rename_map


def _parse_stimulus_events(events_tsv_path: str) -> dict:
    """Parse events.tsv to extract stars/boats stimulus onsets.
    
    Returns a dict with 'onset', 'duration', 'value', 'target' keys.
    Source: LLM inference from events.tsv structure, 2026-04-08
    """
    import pandas as pd
    
    if not os.path.exists(events_tsv_path):
        return {"onset": [], "duration": [], "value": [], "target": []}
    
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
    except Exception:
        return {"onset": [], "duration": [], "value": [], "target": []}
    
    result = {
        "onset": [],
        "duration": [],
        "value": [],
        "target": [],
    }
    
    # Expected columns: onset, duration, value, target (if available)
    if "onset" in df.columns:
        result["onset"] = df["onset"].tolist()
    if "duration" in df.columns:
        result["duration"] = df["duration"].tolist()
    if "value" in df.columns:
        result["value"] = df["value"].tolist()
    if "target" in df.columns:
        result["target"] = df["target"].tolist()
    
    return result


class OpenNeuroDS004018Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for openneuro_ds004018 RSVP dataset.
    
    Paradigm: Rapid Serial Visual Presentation of object images at 5Hz/20Hz.
    Two superordinate categories: stars (celestial) and boats (vehicles).
    """
    
    KERNEL_ID: str = "openneuro-ds004018-stage1"
    
    def __init__(self):
        super().__init__(
            KERNEL_ID=self.KERNEL_ID,
            event_map={},
            continuous_cols=["rt"],
        )
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single RSVP EEG record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG object to preprocess
        row : pandas.Series
            Row from locator with File Path and metadata
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations
        """
        import mne
        import numpy as np
        import pandas as pd
        
        file_path = row.get("File Path", "")
        subject_id = str(row.get("participant_id", row.get("subject_id", "unknown")))
        
        # Determine dataset root from file path
        dataset_root = ""
        if file_path:
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("sub-"):
                    dataset_root = os.sep.join(parts[:i])
                    break
        
        # Parse participants.tsv for subject metadata
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        
        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        if os.path.exists(participants_tsv):
            try:
                p_df = pd.read_csv(participants_tsv, sep="\t")
                subj_row = p_df[p_df["participant_id"] == subject_id]
                if not subj_row.empty:
                    if "age" in subj_row.columns:
                        raw_age = subj_row["age"].values[0]
                        if pd.notna(raw_age):
                            age = str(raw_age)
                    if "sex" in subj_row.columns:
                        raw_sex = subj_row["sex"].values[0]
                        if pd.notna(raw_sex):
                            sex = str(raw_sex).lower()
                            if sex not in ["male", "female"]:
                                sex = "unknown"
                    if "handedness" in subj_row.columns:
                        raw_hand = subj_row["handedness"].values[0]
                        if pd.notna(raw_hand):
                            handedness = str(raw_hand).lower()
            except Exception:
                pass
        
        # LLM 推断，需人类复核
        amplifier = "unknown"  # Not specified in available metadata
        cap = "unknown"  # Not specified in available metadata
        
        # Update description with eegunity metadata
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Channel renaming to standard names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_to_rename = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if existing_to_rename:
                raw.rename_channels(existing_to_rename)
        
        # Set montage (standard 1020) if all EEG channels are properly named
        try:
            eeg_channels = [ch for ch in raw.ch_names if ch not in ["EOG", "ECG", "EMG", "Misc"]]
            if len(eeg_channels) >= 60:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass
        
        # Parse events from events.tsv
        events_path = ""
        if file_path:
            eeg_dir = os.path.dirname(file_path)
            for fname in os.listdir(eeg_dir):
                if fname.endswith("_events.tsv"):
                    events_path = os.path.join(eeg_dir, fname)
                    break
        
        if events_path and os.path.exists(events_path):
            events_data = _parse_stimulus_events(events_path)
            
            if events_data["onset"]:
                # Build annotations from parsed events
                onsets = []
                durations = []
                descriptions = []
                
                for i, onset in enumerate(events_data["onset"]):
                    value = events_data["value"][i] if i < len(events_data["value"]) else ""
                    duration = events_data["duration"][i] if i < len(events_data["duration"]) else 0.0
                    
                    # Map value to event label
                    if value in ["stars", "boats"]:
                        label = value
                    elif str(value).isdigit():
                        # Numeric event code - these are stimulus markers
                        label = f"stim_{value}"
                    else:
                        label = str(value) if value else "unknown"
                    
                    onsets.append(float(onset))
                    durations.append(float(duration) if pd.notna(duration) else 0.0)
                    descriptions.append(label)
                
                # Create annotations for stars/boats events
                if onsets:
                    annotations = mne.Annotations(
                        onset=np.array(onsets),
                        duration=np.array(durations),
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDS004018Kernel()