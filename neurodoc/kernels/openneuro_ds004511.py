"""openneuro_ds004511 stage1 kernel for EEGUnity.

Dataset: Deception_data (ds004511)
Format: BIDS with EDF files
Channels: 64
Sampling Rate: 512 Hz (downsampled from 3000 Hz in some files)
Subjects: 44 (29 with complete data)
Source: https://openneuro.org/datasets/ds004511

Notes:
- BIDS-compliant dataset with participants.tsv and events.tsv sidecars.
- Only hardware sync marker "Sync(1)" present; no trial-level events.
- Three task types: CC (control/cognitive control), GG (gambling game/deception), Rest.
- Channel names follow standard 10-20 system with some non-standard naming.
- Device info missing from BIDS sidecars; inferred from paper.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# Source: Dataset README and BIDS structure
# https://openneuro.org/datasets/ds004511
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核

# Standard 64-channel layout for this dataset based on BIDS channels.tsv
# The dataset uses standard 10-20 extended system with 64 channels
_STANDARD_CHANNEL_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2"
]

# Mapping from dataset-specific channel names to standard names
# The dataset uses standard names but may have variations
_CHANNEL_RENAME_MAP = {
    # Common variations found in EDF exports
    "A1": "TP9",   # mastoid reference, sometimes labeled A1
    "A2": "TP10",  # mastoid reference, sometimes labeled A2
    "M1": "TP9",
    "M2": "TP10",
    "CB1": "Iz",   # sometimes inion labeled as CB1
    "CB2": "Oz",   # sometimes Oz labeled as CB2
    "VEOG": "Fpz", # vertical EOG, often at Fpz position or nearby
    "HEOG": "FT9", # horizontal EOG, lateral position
    "EOG1": "Fpz",
    "EOG2": "FT9",
    "EMG1": "EMG", # EMG channels if present
    "EMG2": "EMG",
    "STIM": "Status", # trigger channel
    "TRIG": "Status",
    "MKR": "Status",
    "Marker": "Status",
    "Mark": "Status",
    "Sync": "Status", # hardware sync marker channel
}


def _extract_subject_id(file_path: str) -> str | None:
    """Extract BIDS subject ID from file path."""
    # Match patterns like sub-S200116, sub-S200120, etc.
    match = re.search(r'sub-([A-Za-z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


def _extract_task_type(file_path: str) -> str | None:
    """Extract task type from BIDS filename."""
    # Match patterns like task-CC, task-GG, task-Rest
    match = re.search(r'task-([A-Za-z]+)', file_path)
    if match:
        return match.group(1)
    return None


def _read_participants_tsv(dataset_path: str) -> pd.DataFrame | None:
    """Read participants.tsv from dataset root."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _read_events_tsv(file_path: str) -> pd.DataFrame | None:
    """Read events.tsv sidecar for given EEG file."""
    # BIDS sidecar naming: sub-XX_task-YY_run-ZZ_eeg.edf -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.bdf", "").replace("_eeg.set", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    # Try without run level
    base_no_run = re.sub(r'_run-\d+', '', base)
    if base_no_run != base:
        events_path = base_no_run + "_events.tsv"
        if os.path.exists(events_path):
            return pd.read_csv(events_path, sep="\t")
    return None


def _get_subject_info(participants_df: pd.DataFrame | None, subject_id: str) -> dict:
    """Get subject info from participants DataFrame."""
    if participants_df is None or subject_id is None:
        return {}
    
    # Handle subject_id with or without 'sub-' prefix
    search_id = subject_id
    if not search_id.startswith("sub-"):
        search_id = "sub-" + search_id
    
    # Try matching participant_id column
    if "participant_id" in participants_df.columns:
        row = participants_df[participants_df["participant_id"] == search_id]
        if len(row) == 0:
            # Try without sub- prefix
            row = participants_df[participants_df["participant_id"] == subject_id]
        if len(row) > 0:
            return row.iloc[0].to_dict()
    
    return {}


def _compute_age_bin_median(participants_df: pd.DataFrame | None) -> float | None:
    """Compute median age for binning across all subjects."""
    if participants_df is None or "age" not in participants_df.columns:
        return None
    try:
        ages = pd.to_numeric(participants_df["age"], errors="coerce").dropna()
        if len(ages) > 0:
            return float(ages.median())
    except Exception:
        pass
    return None


@dataclass
class OpenNeuroDS004511Kernel:
    """Stage1 kernel for OpenNeuro ds004511 (Deception_data)."""

    KERNEL_ID: str = "openneuro-ds004511-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = row.get("Dataset Path", os.path.dirname(os.path.dirname(file_path)))
        
        # Preload raw data before any channel operations
        if not raw.preload:
            raw.load_data()
        
        # Extract identifiers
        subject_id = _extract_subject_id(file_path)
        task_type = _extract_task_type(file_path)
        
        # Read participants.tsv
        participants_df = _read_participants_tsv(dataset_path)
        subject_info = _get_subject_info(participants_df, subject_id)
        
        # Read events.tsv sidecar
        events_df = _read_events_tsv(file_path)
        
        # --- Channel renaming and type setting ---
        # Build rename map for non-standard channel names
        rename_map = {}
        for ch_name in raw.ch_names:
            upper_name = ch_name.upper()
            # Check direct mapping
            if ch_name in _CHANNEL_RENAME_MAP:
                rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
            elif upper_name in _CHANNEL_RENAME_MAP:
                rename_map[ch_name] = _CHANNEL_RENAME_MAP[upper_name]
            # Check for numbered EEG channels (EEG-0, EEG-1, etc.)
            elif re.match(r'EEG[-_]?\d+', ch_name, re.I):
                idx_match = re.search(r'\d+', ch_name)
                if idx_match:
                    idx = int(idx_match.group())
                    if idx < len(_STANDARD_CHANNEL_NAMES):
                        rename_map[ch_name] = _STANDARD_CHANNEL_NAMES[idx]
        
        # Apply renaming
        if rename_map:
            # Only rename if target doesn't already exist
            existing = set(raw.ch_names)
            safe_rename = {k: v for k, v in rename_map.items() 
                          if k in existing and v not in existing}
            if safe_rename:
                raw.rename_channels(safe_rename)
        
        # Set channel types
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if "EOG" in upper or upper in ("VEOG", "HEOG", "EOG1", "EOG2"):
                ch_types[ch_name] = "eog"
            elif "EMG" in upper:
                ch_types[ch_name] = "emg"
            elif "ECG" in upper or "EKG" in upper:
                ch_types[ch_name] = "ecg"
            elif ch_name in ("Status", "STIM", "TRIG", "MKR", "Marker", "Mark", "Sync"):
                ch_types[ch_name] = "stim"
            elif ch_name.startswith("MISC") or ch_name.startswith("misc"):
                ch_types[ch_name] = "misc"
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage to standard 10-20
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = list(raw_chs & montage_chs)
            if common_chs:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
        
        # --- Handle events and annotations ---
        # The dataset has a "Sync(1)" hardware marker but no trial events
        # Check if there's a stim channel
        stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
        
        if events_df is not None and len(events_df) > 0:
            # Parse events from events.tsv sidecar
            onsets = []
            durations = []
            descriptions = []
            
            for _, event_row in events_df.iterrows():
                onset = float(event_row.get("onset", 0))
                duration = float(event_row.get("duration", 0))
                if duration <= 0:
                    duration = 0.0
                trial_type = str(event_row.get("trial_type", event_row.get("value", "unknown")))
                if trial_type == "nan" or trial_type == "":
                    trial_type = "unknown"
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(trial_type)
            
            # Create annotations from events.tsv
            if len(onsets) > 0:
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)
        elif len(stim_picks) > 0:
            # Try to extract events from stim channel
            try:
                events = mne.find_events(raw, stim_channel="Status", shortest_event=1)
                if len(events) > 0:
                    # Create annotations from events
                    event_id_map = {v: k for k, v in raw.event_id.items()} if hasattr(raw, 'event_id') else {}
                    descriptions = []
                    for ev in events:
                        ev_id = ev[2]
                        desc = event_id_map.get(ev_id, str(ev_id))
                        descriptions.append(desc)
                    
                    onsets = events[:, 0] / raw.info["sfreq"]
                    durations = [0.0] * len(events)
                    annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                    raw.set_annotations(annot)
            except Exception:
                pass
        
        # --- Build eegunity_description from participants.tsv ---
        original_description = raw.info.get("description", "")
        
        # Extract required fields from participants.tsv
        age = str(subject_info.get("age", ""))
        sex = str(subject_info.get("sex", ""))
        handedness = str(subject_info.get("handedness", ""))
        
        # Device info inferred from dataset documentation
        # The dataset uses a NeuroScan SynAmps2 amplifier with a 64-channel cap
        amplifier = "NeuroScan SynAmps2"
        cap = "NeuroScan 64-channel Quick-cap"
        
        # Build eegunity_description
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # --- Create derived misc channels ---
        # age_bin: binary based on median age
        age_val = None
        try:
            age_val = float(age)
        except (ValueError, TypeError):
            pass
        
        age_median = _compute_age_bin_median(participants_df)
        
        if age_val is not None and age_median is not None:
            age_bin_val = 1 if age_val >= age_median else 0
        else:
            age_bin_val = 0  # default when unknown
        
        # deception_binary: 1 for GG task (gambling/deception), 0 otherwise
        deception_binary_val = 1 if task_type == "GG" else 0
        
        # Create misc channels by broadcasting constant values
        n_times = len(raw.times)
        
        # age_bin channel
        age_bin_data = np.full((1, n_times), float(age_bin_val))
        age_bin_info = mne.create_info(
            ch_names=["age_bin"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"]
        )
        age_bin_raw = mne.io.RawArray(age_bin_data, age_bin_info)
        raw.add_channels([age_bin_raw], force_update_info=True)
        
        # deception_binary channel
        deception_data = np.full((1, n_times), float(deception_binary_val))
        deception_info = mne.create_info(
            ch_names=["deception_binary"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"]
        )
        deception_raw = mne.io.RawArray(deception_data, deception_info)
        raw.add_channels([deception_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004511Kernel()