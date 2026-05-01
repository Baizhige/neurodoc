"""OpenNeuro ds006648 stage1 kernel for EEGUnity.

Dataset: Poetry reading EEG (Readpoetry task)
Format: BDF (BioSemi 64+ channels)
Channels: 70 (64 EEG + 6 EXG)
Sampling Rate: 512 Hz
Subjects: 47
Source: https://openneuro.org/datasets/ds006648
        https://doi.org/10.18112/openneuro.ds006648.v1.0.0
        https://doi.org/10.1038/s41597-025-06189-w

Notes:
- BIDS-compliant dataset with participants.tsv and *_events.tsv sidecars.
- BioSemi ActiveTwo system with 64 EEG channels + 6 external channels (EXG1-EXG8, some not used).
- Trigger codes 65281-65288 embedded in BDF status channel; MNE reads these as annotations.
- Events.tsv contains trial_type, value, and rating columns (aesthetic_appeal, etc.).
- Standard 10-20 montage applies after channel renaming.
"""

from __future__ import annotations

import json
import os
import warnings

import mne
import numpy as np
import pandas as pd


# BioSemi 64-channel standard naming (from BDF recorder channel order)
# Source: BioSemi ActiveTwo 64-channel cap documentation, standard 10-20 layout
# https://www.biosemi.com/download/Cap_coords_all.xls
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_BIOSEMI_64_CHANNEL_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2"
]

# EXG channels as they appear in BioSemi BDF files
_BIOSEMI_EXG_NAMES = ["EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8"]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> dict[str, str]:
    """Build rename map for BioSemi BDF channels to standard 10-20 names.
    
    BioSemi BDF files typically name EEG channels as A1-A32, B1-B32 etc.
    or as numbered channels. Map them to standard names.
    """
    rename_map: dict[str, str] = {}
    existing_names = list(raw.ch_names)
    
    # Common BioSemi BDF naming patterns
    # Pattern 1: A1-A32, B1-B32 (BioSemi default)
    biosemi_default_names = []
    for prefix in ["A", "B", "C", "D"]:
        for i in range(1, 33):
            biosemi_default_names.append(f"{prefix}{i}")
    
    # Try to match default BioSemi names to standard 10-20
    for i, target_name in enumerate(_BIOSEMI_64_CHANNEL_NAMES):
        if i < len(biosemi_default_names):
            candidate = biosemi_default_names[i]
            if candidate in existing_names and candidate != target_name:
                rename_map[candidate] = target_name
    
    # Pattern 2: EEG-0, EEG-1, etc.
    for i, target_name in enumerate(_BIOSEMI_64_CHANNEL_NAMES):
        candidates = [
            f"EEG-{i}",
            f"EEG {i}",
            str(i),
            f"Ch{i+1}",
            f"ch{i+1}",
            f"Channel{i+1}",
        ]
        for candidate in candidates:
            if candidate in existing_names and candidate != target_name:
                if candidate not in rename_map:
                    rename_map[candidate] = target_name
                    break
    
    # Pattern 3: Already has some standard names with prefixes
    for target_name in _BIOSEMI_64_CHANNEL_NAMES:
        candidates = [
            f"EEG {target_name}",
            f"EEG-{target_name}",
            f"E{target_name}",
        ]
        for candidate in candidates:
            if candidate in existing_names and candidate != target_name:
                if target_name not in existing_names:  # Don't overwrite if already exists
                    rename_map[candidate] = target_name
                    break
    
    return rename_map


def _set_standard_montage(raw: mne.io.BaseRaw) -> None:
    """Set standard 10-20 montage for renamed channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn")
    except Exception:
        # If montage setting fails, continue without it
        pass


def _read_participants_info(dataset_path: str, subject_id: str) -> dict[str, str]:
    """Read participant info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id like "sub-01" or "01"
        sub_col = "participant_id"
        if sub_col not in df.columns:
            return {}
        
        # Normalize subject ID for matching
        if subject_id.startswith("sub-"):
            search_id = subject_id
        else:
            search_id = f"sub-{subject_id}"
        
        row = df[df[sub_col] == search_id]
        if row.empty:
            # Try without prefix
            row = df[df[sub_col] == subject_id]
        
        if row.empty:
            return {}
        
        info = {}
        for col in df.columns:
            if col != sub_col:
                val = row[col].values[0]
                info[col] = str(val) if pd.notna(val) else "unknown"
        return info
    except Exception:
        return {}


def _read_events_tsv(file_path: str) -> pd.DataFrame | None:
    """Read events.tsv sidecar for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.bdf -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.bdf", "").replace("_eeg.edf", "").replace("_eeg.set", "")
    events_path = base + "_events.tsv"
    
    if not os.path.exists(events_path):
        # Try without run suffix
        dir_path = os.path.dirname(file_path)
        base_name = os.path.basename(file_path).replace("_eeg.bdf", "").replace("_eeg.edf", "").replace("_eeg.set", "")
        # Look for any events.tsv in same directory
        for fname in os.listdir(dir_path):
            if fname.endswith("_events.tsv"):
                events_path = os.path.join(dir_path, fname)
                break
    
    if not os.path.exists(events_path):
        return None
    
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _create_aesthetic_appeal_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame | None) -> mne.io.BaseRaw:
    """Create derived misc channel 'aesthetic_appeal_continuous' from events.tsv.
    
    For each trial, hold the aesthetic appeal rating constant from poem onset (65282)
    to next trial fixation (65281). Uses step function with 0 between trials.
    """
    # Ensure data is loaded before adding channels
    if not raw.preload:
        raw.load_data()
    
    if events_df is None or "aesthetic_appeal" not in events_df.columns:
        # Create empty channel with zeros if no data available
        data = np.zeros((1, len(raw.times)))
        info = mne.create_info(["aesthetic_appeal_continuous"], raw.info["sfreq"], ["misc"])
        misc_raw = mne.io.RawArray(data, info)
        raw.add_channels([misc_raw], force_update_info=True)
        return raw
    
    # Build step function based on events
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    channel_data = np.zeros(n_samples)
    
    # Get poem onset events (65282) with aesthetic appeal ratings
    # and fixation events (65281) to mark trial boundaries
    poem_mask = events_df["value"].astype(str) == "65282"
    fixation_mask = events_df["value"].astype(str) == "65281"
    
    poem_events = events_df[poem_mask].copy()
    fixation_events = events_df[fixation_mask].copy()
    
    if len(poem_events) == 0:
        # No poem events found, create zero channel
        data = np.zeros((1, n_samples))
        info = mne.create_info(["aesthetic_appeal_continuous"], sfreq, ["misc"])
        misc_raw = mne.io.RawArray(data, info)
        raw.add_channels([misc_raw], force_update_info=True)
        return raw
    
    # Sort by onset time
    poem_events = poem_events.sort_values("onset").reset_index(drop=True)
    fixation_events = fixation_events.sort_values("onset").reset_index(drop=True)
    
    # For each poem event, find the next fixation event to determine trial end
    for idx, poem_row in poem_events.iterrows():
        poem_onset = poem_row["onset"]
        appeal_val = poem_row["aesthetic_appeal"]
        
        if pd.isna(appeal_val):
            continue
        
        # Find next fixation after this poem onset
        next_fixations = fixation_events[fixation_events["onset"] > poem_onset]
        if len(next_fixations) == 0:
            # Last trial: extend to end of recording
            trial_end = n_samples / sfreq
        else:
            trial_end = next_fixations.iloc[0]["onset"]
        
        # Convert to sample indices
        start_sample = int(poem_onset * sfreq)
        end_sample = int(trial_end * sfreq)
        
        # Clamp to valid range
        start_sample = max(0, min(start_sample, n_samples))
        end_sample = max(0, min(end_sample, n_samples))
        
        if start_sample < end_sample:
            channel_data[start_sample:end_sample] = float(appeal_val)
    
    # Add as misc channel
    data = channel_data.reshape(1, -1)
    info = mne.create_info(["aesthetic_appeal_continuous"], sfreq, ["misc"])
    misc_raw = mne.io.RawArray(data, info)
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


class OpenNeuroDS006648Kernel:
    """Stage-1 kernel for OpenNeuro ds006648 (Poetry reading EEG)."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract subject ID from row
        subject_id = str(row.get("subject", ""))
        if not subject_id:
            # Try to extract from filepath
            filepath = str(row.get("filepath", ""))
            basename = os.path.basename(filepath)
            if basename.startswith("sub-"):
                subject_id = basename.split("_")[0]
        
        # Get dataset path
        dataset_path = str(udataset.get("dataset_path", "")) if hasattr(udataset, "get") else str(getattr(udataset, "dataset_path", ""))
        
        # Read participants.tsv info
        participants_info = _read_participants_info(dataset_path, subject_id)
        
        # Read events.tsv for this file
        filepath = str(row.get("filepath", ""))
        events_df = _read_events_tsv(filepath)
        
        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types: EEG for standard channels, misc for EXG
        channel_types = {}
        for ch_name in raw.ch_names:
            if ch_name in _BIOSEMI_64_CHANNEL_NAMES:
                channel_types[ch_name] = "eeg"
            elif any(exg in ch_name for exg in _BIOSEMI_EXG_NAMES):
                channel_types[ch_name] = "misc"
            elif ch_name in ["Status", "status", "TRIGGER", "trigger"]:
                channel_types[ch_name] = "stim"
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # Set standard montage
        _set_standard_montage(raw)
        
        # Create derived misc channel for aesthetic appeal
        raw = _create_aesthetic_appeal_misc(raw, events_df)
        
        # Build eegunity_description with required fields
        # required_info_fields: ['participant_original_id'] must be read from participants.tsv
        eegunity_description = {
            "age": participants_info.get("age", "unknown"),
            "sex": participants_info.get("sex", "unknown"),
            "amplifier": "BioSemi ActiveTwo",
            "cap": "BioSemi 64-channel standard 10-20",
            "handedness": participants_info.get("handedness", "unknown"),
            "participant_original_id": participants_info.get("participant_original_id", "unknown"),
        }
        
        # Store original description and add eegunity metadata
        original_desc = raw.info.get("description", "") or ""
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS006648Kernel()