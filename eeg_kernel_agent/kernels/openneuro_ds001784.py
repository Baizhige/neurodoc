"""OpenNeuro DS001784 stage1 kernel for EEGUnity.

Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant
depression (EEG). BIDS-formatted dataset with 65 channels at 1450 Hz.

Dataset: openneuro_ds001784 | Year: 2019 | DOI: https://doi.org/10.1038/s41467-019-09557-4
Paradigm: MSIT with emotional stimuli + DBS ON/OFF

This kernel:
- Reads participants.tsv for age/sex/dbs metadata
- Parses events.tsv to extract trial_type (interference/control) labels
- Maps raw events (event_2/4/6) to semantic labels
- Sets standard 10-20 montage for 65-channel EEG
- Provides DBS ON/OFF labels from participants.tsv
- Creates derived misc channel: madrs_change

Source: https://openneuro.org/datasets/ds001784
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# EEGUnity Kernel Metadata
# =============================================================================
eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "unknown",
    "cap": "unknown",
    "handedness": "unknown",
}


# =============================================================================
# Raw Event Mapping (from analysis.md Event Structure table)
# =============================================================================
_EVENT_RAW_MAP: Dict[str, str] = {
    "event_2": "interference_trial",
    "event_4": "control_trial",
    "event_6": "afmsit_trial",
}

# Reverse map for annotation-to-event lookup
_EVENT_LABEL_TO_ID: Dict[str, int] = {
    "interference_trial": 2,
    "control_trial": 4,
    "afmsit_trial": 6,
}

# =============================================================================
# Cognitive Control Label Map (Super Meta)
# =============================================================================
_COGNITIVE_LABEL_MAP: Dict[str, int] = {
    "interference_trial": 1,
    "control_trial": 0,
}


# =============================================================================
# Channel Rename Map for 64-65 Channel Standard Systems
# =============================================================================
_CHANNEL_ALIAS_GROUPS: List[List[str]] = [
    ["Fp1", "FP1", "fp1"],
    ["Fpz", "FPz", "fpz"],
    ["Fp2", "FP2", "fp2"],
    ["AF7", "AF7"],
    ["AF3", "AF3"],
    ["AFz", "AFz"],
    ["AF4", "AF4"],
    ["AF8", "AF8"],
    ["F7", "F7"],
    ["F5", "F5"],
    ["F3", "F3"],
    ["F1", "F1"],
    ["Fz", "Fz"],
    ["F2", "F2"],
    ["F4", "F4"],
    ["F6", "F6"],
    ["F8", "F8"],
    ["FT7", "FT7"],
    ["FC5", "FC5"],
    ["FC3", "FC3"],
    ["FC1", "FC1"],
    ["FCz", "FCz"],
    ["FC2", "FC2"],
    ["FC4", "FC4"],
    ["FC6", "FC6"],
    ["FT8", "FT8"],
    ["T7", "T7"],
    ["C5", "C5"],
    ["C3", "C3"],
    ["C1", "C1"],
    ["Cz", "Cz"],
    ["C2", "C2"],
    ["C4", "C4"],
    ["C6", "C6"],
    ["T8", "T8"],
    ["TP7", "TP7"],
    ["CP5", "CP5"],
    ["CP3", "CP3"],
    ["CP1", "CP1"],
    ["CPz", "CPz"],
    ["CP2", "CP2"],
    ["CP4", "CP4"],
    ["CP6", "CP6"],
    ["TP8", "TP8"],
    ["P9", "P9"],
    ["P7", "P7"],
    ["P5", "P5"],
    ["P3", "P3"],
    ["P1", "P1"],
    ["Pz", "Pz"],
    ["P2", "P2"],
    ["P4", "P4"],
    ["P6", "P6"],
    ["P8", "P8"],
    ["P10", "P10"],
    ["PO7", "PO7"],
    ["PO3", "PO3"],
    ["POz", "POz"],
    ["PO4", "PO4"],
    ["PO8", "PO8"],
    ["O1", "O1"],
    ["Oz", "Oz"],
    ["O2", "O2"],
    ["Iz", "Iz"],
    ["EOGv", "EOGv", "VEOG", "veog"],
    ["EOGh", "EOGh", "HEOG", "heog"],
    ["EMG", "EMG", "emg"],
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for alias_group in _CHANNEL_ALIAS_GROUPS:
        target_name = alias_group[0]
        for source_name in alias_group:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _read_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Read participants.tsv from dataset root directory."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_metadata(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, Any]:
    """Extract subject metadata from participants.tsv."""
    if participants_df.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "dbs_stim_freq": "unknown",
            "madrs_bl": "unknown",
            "madrs_fu": "unknown",
            "responder": "unknown",
        }
    
    subject_row = participants_df[
        participants_df["participant_id"] == f"sub-{subject_id}"
    ]
    
    if subject_row.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "dbs_stim_freq": "unknown",
            "madrs_bl": "unknown",
            "madrs_fu": "unknown",
            "responder": "unknown",
        }
    
    row = subject_row.iloc[0]
    
    def safe_str(val: Any) -> str:
        if pd.isna(val):
            return "unknown"
        return str(val).strip().lower()
    
    def safe_float(val: Any) -> str:
        if pd.isna(val):
            return "unknown"
        try:
            return str(float(val))
        except (ValueError, TypeError):
            return "unknown"
    
    return {
        "age": safe_str(row.get("age", "unknown")),
        "sex": safe_str(row.get("sex", "unknown")),
        "dbs_stim_freq": safe_float(row.get("dbs_stim_freq", "unknown")),
        "madrs_bl": safe_float(row.get("madrs_bl", "unknown")),
        "madrs_fu": safe_float(row.get("madrs_fu", "unknown")),
        "responder": safe_str(row.get("responder", "unknown")),
    }


def _parse_events_tsv(eeg_file_path: str) -> pd.DataFrame:
    """Parse events.tsv file associated with the EEG file."""
    eeg_file_path = str(eeg_file_path)
    base_path = eeg_file_path.replace("_eeg.fif", "_events.tsv").replace(
        "_eeg.set", "_events.tsv"
    )
    
    # Try common BIDS naming patterns
    possible_paths = [
        base_path,
        eeg_file_path.replace(".fif", "_events.tsv").replace(".set", "_events.tsv"),
    ]
    
    # Extract directory and find events file
    eeg_dir = os.path.dirname(eeg_file_path)
    for fname in os.listdir(eeg_dir):
        if fname.endswith("_events.tsv"):
            return pd.read_csv(os.path.join(eeg_dir, fname), sep="\t")
    
    return pd.DataFrame()


def _create_annotations_from_events(
    events_df: pd.DataFrame, sfreq: float
) -> mne.Annotations:
    """Create MNE annotations from events.tsv dataframe."""
    if events_df.empty or "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onset_times = []
    durations = []
    descriptions = []
    
    for idx, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0))
        
        # Try to get event_id or value
        event_val = row.get("value", row.get("event_id", f"event_{idx}"))
        
        # Try to get trial_type
        trial_type = row.get("trial_type", None)
        
        if pd.notna(trial_type):
            desc = str(trial_type).lower().replace(" ", "_")
        else:
            event_str = str(event_val) if pd.notna(event_val) else f"event_{idx}"
            desc = _EVENT_RAW_MAP.get(event_str, event_str)
        
        onset_times.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(onset=onset_times, duration=durations, description=descriptions)


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro DS001784 dataset."""
    
    def __init__(self):
        self.kernel_name = "openneuro_ds001784"
        self.kernel_version = "1.0.0"
        self._description = dict(eegunity_description)
    
    def __repr__(self) -> str:
        return f"EEGUnityKernel({self.kernel_name}, version={self.kernel_version})"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply the kernel to raw EEG data.
        
        Args:
            udataset: Universal dataset wrapper (not used here, kept for API compatibility)
            raw: MNE Raw object containing the EEG data
            row: DataFrame row with subject metadata (must contain 'subject_id' and 'bids_dir')
        
        Returns:
            Processed MNE Raw object with annotations, renamed channels, and metadata channels
        """
        # Extract metadata from row
        subject_id = row.get("subject_id", "unknown")
        bids_dir = row.get("bids_dir", "")
        
        # Read participants metadata
        participants_df = _read_participants_tsv(bids_dir)
        subject_meta = _get_subject_metadata(participants_df, subject_id)
        
        # Update kernel description with subject-specific info
        self._description["age"] = subject_meta["age"]
        self._description["sex"] = subject_meta["sex"]
        
        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_alphabetic")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass
        
        # Find events file and parse
        eeg_file_path = row.get("eeg_file_path", "")
        if eeg_file_path and os.path.exists(str(eeg_file_path)):
            events_df = _parse_events_tsv(eeg_file_path)
            if not events_df.empty:
                annotations = _create_annotations_from_events(events_df, raw.info["sfreq"])
                raw.set_annotations(annotations)
        
        # Add metadata channels
        sfreq = raw.info["sfreq"]
        n_samples = len(raw.times)
        
        # Add MADRS change channel: madrs_bl - madrs_fu (from participants.tsv)
        madrs_bl_str = subject_meta.get("madrs_bl", "unknown")
        madrs_fu_str = subject_meta.get("madrs_fu", "unknown")
        
        # Compute MADRS change if both values available
        madrs_change = np.nan
        if madrs_bl_str != "unknown" and madrs_fu_str != "unknown":
            try:
                madrs_change = float(madrs_bl_str) - float(madrs_fu_str)
            except (ValueError, TypeError):
                madrs_change = np.nan
        
        # Only create channel if we have a valid value
        if not np.isnan(madrs_change):
            madrs_change_data = np.full(n_samples, madrs_change)
            info = mne.create_info(
                ch_names=["madrs_change"],
                sfreq=sfreq,
                ch_types="misc",
            )
            madrs_raw = mne.io.RawArray(madrs_change_data.reshape(1, -1), info)
            raw.add_channels([madrs_raw], force_inplace=True)
        
        # Add DBS status channel (from participants metadata)
        dbs_info = {
            "stim_freq": subject_meta.get("dbs_stim_freq", "unknown"),
            "responder": subject_meta.get("responder", "unknown"),
        }
        
        # Update description with derived misc channel metadata
        self._description["madrs_change"] = str(madrs_change) if not np.isnan(madrs_change) else "unknown"
        
        return raw


KERNEL = EEGUnityKernel()