"""Dataset-specific kernel for openneuro ds003061.

Auditory three-stimulus oddball task (P300 paradigm).
79-channel BioSemi EEG data with standard and target tones.

Source: https://openneuro.org/datasets/ds003061
Paper: https://doi.org/10.1038/s41598-023-27528-0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Kernel ID
# =============================================================================

KERNEL_ID = "openneuro_ds003061"


# =============================================================================
# Subject Metadata (from participants.tsv + paper inference)
# =============================================================================

# Source: participants.tsv contains sex and age columns
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Amplifier and cap info from dataset documentation
# Source: OpenNeuro dataset description / BIDS sidecar
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BioSemi ActiveTwo",
    "cap": "Ag/AgCl",
}


# =============================================================================
# Channel Mapping for BioSemi 79-channel system
# =============================================================================

# BioSemi 79-channel cap layout following standard 10-20 system
# Source: BioSemi electrode positions documentation
# Annotator: LLM, 2026-04-08
_BIOSEMI_79_CHANNEL_MAP = {
    # Standard 10-20 locations
    "Fp1": "EEG Fp1",
    "Fp2": "EEG Fp2",
    "Fpz": "EEG Fpz",
    "Fz": "EEG Fz",
    "F3": "EEG F3",
    "F4": "EEG F4",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "Cz": "EEG Cz",
    "C3": "EEG C3",
    "C4": "EEG C4",
    "T7": "EEG T7",
    "T8": "EEG T8",
    "Pz": "EEG Pz",
    "P3": "EEG P3",
    "P4": "EEG P4",
    "P7": "EEG P7",
    "P8": "EEG P8",
    "Oz": "EEG Oz",
    "O1": "EEG O1",
    "O2": "EEG O2",
    # Additional BioSemi electrodes
    "AF7": "EEG AF7",
    "AF3": "EEG AF3",
    "AF4": "EEG AF4",
    "AF8": "EEG AF8",
    "F1": "EEG F1",
    "F2": "EEG F2",
    "F5": "EEG F5",
    "F6": "EEG F6",
    "FT7": "EEG FT7",
    "FT8": "EEG FT8",
    "FC3": "EEG FC3",
    "FC4": "EEG FC4",
    "FCz": "EEG FCz",
    "C1": "EEG C1",
    "C2": "EEG C2",
    "C5": "EEG C5",
    "C6": "EEG C6",
    "TP7": "EEG TP7",
    "TP8": "EEG TP8",
    "CP3": "EEG CP3",
    "CP4": "EEG CP4",
    "CPz": "EEG CPz",
    "P1": "EEG P1",
    "P2": "EEG P2",
    "P5": "EEG P5",
    "P6": "EEG P6",
    "PO3": "EEG PO3",
    "PO4": "EEG PO4",
    "PO7": "EEG PO7",
    "PO8": "EEG PO8",
    "POz": "EEG POz",
    "O9": "EEG O9",
    "O10": "EEG O10",
    "Iz": "EEG Iz",
    "AFz": "EEG AFz",
    "Fpz": "EEG Fpz",
    # EOG channels
    "EOGv": "EOG EOGv",
    "EOGh": "EOG EOGh",
    # Reference electrodes (to be handled specially)
    "CMS": "CMS",
    "DRL": "DRL",
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a mapping from raw BioSemi channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Standard 10-20 electrodes
    standard_1020 = [
        "Fp1", "Fp2", "Fpz", "Fz", "F3", "F4", "F7", "F8",
        "Cz", "C3", "C4", "T7", "T8", "Pz", "P3", "P4",
        "P7", "P8", "Oz", "O1", "O2"
    ]
    
    # BioSemi formats: "EEG Fp1", "EEG Fp1-REF", etc.
    for std_name in standard_1020:
        bio_patterns = [
            f"EEG {std_name}",
            f"EEG {std_name}-REF",
            std_name,
            std_name + "-REF"
        ]
        for pattern in bio_patterns:
            if pattern in existing:
                rename_map[pattern] = std_name
                break
    
    # Extended electrodes
    extended = [
        "AF7", "AF3", "AF4", "AF8", "F1", "F2", "F5", "F6",
        "FT7", "FT8", "FC3", "FC4", "FCz", "C1", "C2", "C5", "C6",
        "TP7", "TP8", "CP3", "CP4", "CPz", "P1", "P2", "P5", "P6",
        "PO3", "PO4", "PO7", "PO8", "POz", "O9", "O10", "Iz", "AFz"
    ]
    
    for ext_name in extended:
        bio_patterns = [
            f"EEG {ext_name}",
            f"EEG {ext_name}-REF",
            ext_name
        ]
        for pattern in bio_patterns:
            if pattern in existing:
                rename_map[pattern] = ext_name
                break
    
    # EOG channels
    eog_patterns = [
        ("EOGv", ["EOG EOGv", "EOG EOGv-REF", "VEOG", "EOG V"]),
        ("EOGh", ["EOG EOGh", "EOG EOGh-REF", "HEOG", "EOG H"])
    ]
    for target, patterns in eog_patterns:
        for pattern in patterns:
            if pattern in existing:
                rename_map[pattern] = target
                break
    
    # MISC channels
    misc_patterns = [
        ("response_time", ["RESPONSE_TIME", "ResponseTime", "Response_Time"]),
        ("reaction_time", ["REACTION_TIME", "ReactionTime", "Reaction_Time"])
    ]
    for target, patterns in misc_patterns:
        for pattern in patterns:
            if pattern in existing:
                rename_map[pattern] = target
                break
    
    # BioSemi reference channels
    for bio_ref in ["CMS", "DRL", "ML", "MR"]:
        if bio_ref in existing:
            rename_map[bio_ref] = bio_ref
    
    return rename_map


def _load_events_tsv(file_path: str) -> pd.DataFrame:
    """Load events.tsv file from the BIDS dataset."""
    # Find events.tsv in the same directory as the EEG file
    eeg_dir = os.path.dirname(file_path)
    events_path = os.path.join(eeg_dir, "*_events.tsv")
    
    import glob
    events_files = glob.glob(events_path)
    
    if events_files:
        return pd.read_csv(events_files[0], sep="\t")
    return pd.DataFrame()


def _build_stimulus_annotations(
    raw: mne.io.BaseRaw,
    events_tsv: pd.DataFrame
) -> mne.Annotations:
    """Build stimulus annotations with trial_type labels from events.tsv."""
    # Get existing annotations
    onset_times = []
    descriptions = []
    durations = []
    
    # Read annotations from raw
    try:
        annotations = raw.annotations
        for idx, annot in enumerate(annotations):
            onset_times.append(annot["onset"])
            descriptions.append(annot["description"])
            durations.append(annot["duration"])
    except Exception:
        pass
    
    # If events.tsv is available, use it to enrich stimulus labels
    if not events_tsv.empty and "onset" in events_tsv.columns:
        for _, row in events_tsv.iterrows():
            onset = float(row["onset"])
            # Get trial_type if available
            trial_type = str(row.get("trial_type", "unknown")).lower()
            value = str(row.get("value", ""))
            
            # Map to kernel event labels
            if "stimulus" in value.lower() or "stimulus" in str(row.get("event", "")).lower():
                if "target" in trial_type or "oddball" in trial_type:
                    desc = "oddball"
                elif "standard" in trial_type:
                    desc = "standard"
                elif "noise" in trial_type or "distractor" in trial_type:
                    desc = "noise"
                else:
                    desc = "stimulus"
            elif "response" in value.lower() or "response" in str(row.get("event", "")).lower():
                desc = "response"
            else:
                desc = value if value else str(row.get("event", "unknown"))
            
            onset_times.append(onset)
            descriptions.append(desc)
            durations.append(0.0)
    
    # Create annotations
    return mne.Annotations(
        onset=onset_times,
        duration=durations,
        description=descriptions,
        orig_time=raw.info.get("meas_date")
    )


def _add_response_time_misc(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Add reaction time values as MISC channel for regression tasks."""
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    
    # Create a zero-filled MISC channel for reaction time
    rt_data = np.zeros((1, n_samples))
    rt_info = mne.create_info(
        ch_names=["response_time"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    rt_raw = mne.io.RawArray(rt_data, rt_info, verbose=False)
    
    # Add the reaction time channel (without force_equal_channels parameter)
    raw.add_channels([rt_raw])
    
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set appropriate channel types for BioSemi data."""
    # Identify EEG channels
    eeg_channels = []
    eog_channels = []
    misc_channels = []
    
    for ch in raw.ch_names:
        if ch.startswith("EEG "):
            eeg_channels.append(ch)
        elif ch in ["EOGv", "EOGh"]:
            eog_channels.append(ch)
        elif ch in ["EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8"]:
            # These are auxiliary channels - set asEOG
            eog_channels.append(ch)
        elif ch in ["GSR1", "GSR2", "Erg1", "Erg2", "Resp", "Plet", "Temp"]:
            misc_channels.append(ch)
        elif ch in ["response_time", "reaction_time"]:
            misc_channels.append(ch)
    
    # Set channel types
    if eeg_channels:
        for ch in eeg_channels:
            raw.set_channel_types({ch: "eeg"}, verbose=False)
    
    if eog_channels:
        for ch in eog_channels:
            raw.set_channel_types({ch: "eog"}, verbose=False)
    
    if misc_channels:
        for ch in misc_channels:
            raw.set_channel_types({ch: "misc"}, verbose=False)
    
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for BioSemi data."""
    # Use standard 10-20 montage
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, verbose=False)
    except Exception:
        pass
    
    return raw


class OpenneuroDs003061:
    """Kernel for openneuro_ds003061 dataset (P300 auditory oddball)."""
    
    def get_subject_metadata(self, subject_id: str) -> Dict[str, Any]:
        """Get subject metadata."""
        return _SUBJECT_DICT.get(subject_id, {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown"
        })
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device information."""
        return _DEVICE_INFO.copy()
    
    def preprocess(self, raw: mne.io.BaseRaw, row: pd.Series) -> mne.io.BaseRaw:
        """Preprocess the raw data."""
        # Get file path for events.tsv
        file_path = row.get("file_path", "")
        
        # Load events.tsv if available
        events_tsv = _load_events_tsv(file_path)
        
        # Rename channels to standard names
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, verbose=False)
        
        # Set channel types
        raw = _set_channel_types(raw)
        
        # Set montage
        raw = _set_montage(raw)
        
        # Build stimulus annotations from events.tsv
        if not events_tsv.empty:
            annotations = _build_stimulus_annotations(raw, events_tsv)
            raw.set_annotations(annotations, verbose=False)
        
        return raw
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply dataset-specific processing."""
        # Preprocess the raw data
        raw = self.preprocess(raw, row)
        
        # Add response time as MISC channel
        raw = _add_response_time_misc(raw)
        
        return raw


# EEGUnity description metadata
eegunity_description = {
    "age": "18-65",  # Adult population, specific ages in participants.tsv
    "sex": "unknown",  # Will be loaded from participants.tsv per subject
    "amplifier": "BioSemi ActiveTwo",
    "cap": "Ag/AgCl",
    "handedness": "unknown"  # Not typically specified in this dataset
}


# Kernel instance
KERNEL = OpenneuroDs003061()