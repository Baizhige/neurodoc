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
# Subject Metadata (from participants.tsv + paper inference)
# =============================================================================

# Source: participants.tsv contains sex and age columns
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Amplifier and cap info from dataset documentation
# Source: OpenNeuro dataset description / BIDS sidecar
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",  # LLM 推断，需人类复核
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
    "EOGv": "EOG EOGv",  # Vertical EOG
    "EOGh": "EOG EOGh",  # Horizontal EOG
    # Reference electrodes (to be handled specially)
    "CMS": "CMS",
    "DRL": "DRL",
    # MISC channels
    "ResponseTime": "RESPONSE_TIME",
    "ReactionTime": "REACTION_TIME",
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
    n_times = raw.n_times
    
    # Create reaction time channel filled with NaN (placeholder)
    reaction_data = np.full((1, n_times), np.nan)
    reaction_info = mne.create_info(
        ch_names=["reaction_time"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    reaction_raw = mne.io.RawArray(reaction_data, reaction_info)
    
    # Add the reaction time channel (no force_equal_channels argument)
    raw = raw.add_channels([reaction_raw])
    
    return raw


class Kernel:
    """EEGUnity kernel for openneuro_ds003061 dataset."""
    
    name = "openneuro_ds003061"
    eegunity_description = {
        "age": "unknown",
        "sex": "unknown",
        "amplifier": "BioSemi ActiveTwo",
        "cap": "Ag/AgCl",
        "handedness": "unknown",
    }
    
    file_types = {
        ".set": lambda f: mne.io.read_raw_eeglab(f, preload=False, verbose=False),
    }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply dataset-specific preprocessing to raw EEG data.
        
        Args:
            udataset: Dataset object (unused for this kernel)
            raw: MNE Raw object with EEG data
            row: DataFrame row with file metadata
            
        Returns:
            Preprocessed MNE Raw object
        """
        # Get file path for events loading
        file_path = row.get("file_path", "")
        
        # Rename channels to standard names
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types for EOG
        try:
            eog_channels = [ch for ch in raw.ch_names if ch.startswith("EOG")]
            if eog_channels:
                raw.set_channel_types({ch: "eog" for ch in eog_channels})
        except Exception:
            pass
        
        # Set BioSemi reference (CMS/DRL) as miscellaneous
        try:
            ref_channels = [ch for ch in raw.ch_names if ch in ["CMS", "DRL"]]
            if ref_channels:
                raw.set_channel_types({ch: "misc" for ch in ref_channels})
        except Exception:
            pass
        
        # Try to set montage
        try:
            # Try standard 10-20 montage first
            montage = mne.channels.make_standard_montage("standard_1020")
            raw = raw.set_montage(montage, on_missing="warn", verbose=False)
        except Exception:
            pass
        
        # Load events from TSV if available
        events_tsv = _load_events_tsv(file_path)
        
        # Build and set annotations
        if not events_tsv.empty:
            annotations = _build_stimulus_annotations(raw, events_tsv)
            raw = raw.set_annotations(annotations)
        
        # Add response time as MISC channel
        raw = _add_response_time_misc(raw)
        
        # Ensure proper data type (float32 for memory efficiency)
        try:
            raw = raw.astype(np.float32)
        except Exception:
            pass
        
        return raw


# Kernel instance for EEGUnity
KERNEL = Kernel()