"""Dataset-specific kernel for openneuro ds002680.

Go-nogo categorization and detection task.
31-channel EEG with stimulus+response events and response_time.
Animal categorization + target-image recognition tasks.
Source: https://openneuro.org/datasets/ds002680
"""

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 channel names for 31-channel cap used in this dataset
# Source: BIDS sidecar eeg.json and standard 10-20 layout for 31 channels
# Cz is typically the reference, leaving 31 active channels
# LLM 推断，需人类复核
_CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "O2", "Oz",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "POz",
]

# Mapping from common alternate names to standard 10-20 names
# LLM 推断，需人类复核
_CHANNEL_RENAME_ALIASES: Dict[str, str] = {
    # EEG prefixed variants
    "EEG-Fp1": "Fp1", "EEG-Fp2": "Fp2",
    "EEG-F7": "F7", "EEG-F3": "F3", "EEG-Fz": "Fz", "EEG-F4": "F4", "EEG-F8": "F8",
    "EEG-T7": "T7", "EEG-C3": "C3", "EEG-Cz": "Cz", "EEG-C4": "C4", "EEG-T8": "T8",
    "EEG-P7": "P7", "EEG-P3": "P3", "EEG-Pz": "Pz", "EEG-P4": "P4", "EEG-P8": "P8",
    "EEG-O1": "O1", "EEG-O2": "O2", "EEG-Oz": "Oz",
    "EEG-FT7": "FT7", "EEG-FC3": "FC3", "EEG-FCz": "FCz", "EEG-FC4": "FC4", "EEG-FT8": "FT8",
    "EEG-TP7": "TP7", "EEG-CP3": "CP3", "EEG-CPz": "CPz", "EEG-CP4": "CP4", "EEG-TP8": "TP8",
    "EEG-POz": "POz",
    # Numeric variants (0-indexed 31 channels)
    "EEG-0": "Fp1", "EEG-1": "Fp2", "EEG-2": "F7", "EEG-3": "F3", "EEG-4": "Fz",
    "EEG-5": "F4", "EEG-6": "F8", "EEG-7": "T7", "EEG-8": "C3", "EEG-9": "Cz",
    "EEG-10": "C4", "EEG-11": "T8", "EEG-12": "P7", "EEG-13": "P3", "EEG-14": "Pz",
    "EEG-15": "P4", "EEG-16": "P8", "EEG-17": "O1", "EEG-18": "O2", "EEG-19": "Oz",
    "EEG-20": "FT7", "EEG-21": "FC3", "EEG-22": "FCz", "EEG-23": "FC4", "EEG-24": "FT8",
    "EEG-25": "TP7", "EEG-26": "CP3", "EEG-27": "CPz", "EEG-28": "CP4", "EEG-29": "TP8",
    "EEG-30": "POz",
    # Simple numeric
    "0": "Fp1", "1": "Fp2", "2": "F7", "3": "F3", "4": "Fz",
    "5": "F4", "6": "F8", "7": "T7", "8": "C3", "9": "Cz",
    "10": "C4", "11": "T8", "12": "P7", "13": "P3", "14": "Pz",
    "15": "P4", "16": "P8", "17": "O1", "18": "O2", "19": "Oz",
    "20": "FT7", "21": "FC3", "22": "FCz", "23": "FC4", "24": "FT8",
    "25": "TP7", "26": "CP3", "27": "CPz", "28": "CP4", "29": "TP8",
    "30": "POz",
    # Additional aliases for this dataset
    "FP1": "Fp1", "FP2": "Fp2",
    "FZ": "Fz", "PZ": "Pz", "CZ": "Cz", "OZ": "Oz",
    "T3": "T7", "T4": "T8", "T5": "P7", "T6": "P8",
    "CB1": "TP7", "CB2": "TP8",
    "I": "Iz",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for source_name, target_name in _CHANNEL_RENAME_ALIASES.items():
        if source_name in existing_names and source_name != target_name:
            # Avoid collision: if target already exists from another source, skip
            if target_name not in existing_names or source_name == target_name:
                rename_map[source_name] = target_name
    
    # Handle case where channels are already standard names
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    basename = os.path.basename(file_path)
    # Match sub-XXX pattern
    if basename.startswith("sub-"):
        parts = basename.split("_")
        if parts:
            return parts[0]
    # Also try from directory structures
    for part in file_path.replace("\\", "/").split("/"):
        if part.startswith("sub-"):
            return part
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XXX_ses-YYY_task-ZZZ_run-WW_eeg.<ext>
    # events: sub-XXX_ses-YYY_task-ZZZ_run-WW_events.tsv
    base = file_path.rsplit(".", 1)[0]
    # Remove _eeg suffix if present
    if base.endswith("_eeg"):
        base = base[:-4]
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run level
    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    parts = basename.split("_")
    # Remove run-XX and eeg.ext, keep sub-*, ses-*, task-*
    non_run_parts = [p for p in parts if not p.startswith("run-") and not p.startswith("eeg.")]
    if non_run_parts:
        base2 = "_".join(non_run_parts)
        events_path2 = os.path.join(dir_path, base2 + "_events.tsv")
        if os.path.exists(events_path2):
            return events_path2
    
    # Search in same directory
    if dir_path:
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from dataset root."""
    # Walk up to find participants.tsv
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # Limit search depth
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    result: Dict[str, str] = {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        sub_col = None
        for col in df.columns:
            if col.lower() in ("participant_id", "subject_id", "sub_id"):
                sub_col = col
                break
        if sub_col is None:
            sub_col = df.columns[0]  # Assume first column
        
        # Match subject ID
        mask = df[sub_col].astype(str) == subject_id
        if not mask.any():
            # Try without "sub-" prefix
            mask = df[sub_col].astype(str) == subject_id.replace("sub-", "")
        
        if mask.any():
            row = df[mask].iloc[0]
            for col in df.columns:
                if col == sub_col:
                    continue
                val = row[col]
                if pd.isna(val):
                    result[col] = "unknown"
                else:
                    result[col] = str(val)
    except Exception:
        pass
    
    return result


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _create_response_time_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel for response_time from events.tsv.
    
    Read response_time column from events.tsv; for each stimulus event with a subsequent response, assign the response_time value to a derived misc channel as a step function aligned to stimulus onset. Trials without response (nogo correct) receive NaN.
    """
    if events_df is None or events_df.empty:
        return raw
    
    # Check required columns
    required_cols = ["onset", "trial_type"]
    if not all(c in events_df.columns for c in required_cols):
        return raw
    
    # Ensure raw is preloaded before adding channels
    if not raw.preload:
        raw.load_data()
    
    # Check if response_time column exists
    if "response_time" not in events_df.columns:
        return raw
    
    # Get stimulus events (target/distractor types)
    stim_mask = events_df["trial_type"].isin([
        "animal_target", "animal_distractor", "object_target", "object_distractor"
    ])
    stim_events = events_df[stim_mask].copy()
    
    if stim_events.empty:
        # No stimulus events found, skip creating channel
        return raw
    
    # Build response_time step function
    sfreq = raw.info["sfreq"]
    n_times = len(raw.times)
    response_time_data = np.full((1, n_times), np.nan)
    
    for _, stim_row in stim_events.iterrows():
        onset = stim_row["onset"]
        rt = None
        
        # Direct response_time from stimulus event
        if pd.notna(stim_row.get("response_time")):
            rt = float(stim_row["response_time"])
        else:
            # Look for associated response event
            stim_onset = stim_row["onset"]
            response_mask = events_df["trial_type"].isin(["response", "response_correct", "response_incorrect", "button_press"])
            if response_mask.any():
                potential_responses = events_df[response_mask]
                # Find closest response after stimulus
                time_diff = potential_responses["onset"] - stim_onset
                valid_responses = potential_responses[time_diff > 0]
                if not valid_responses.empty:
                    closest_response = valid_responses.loc[time_diff[time_diff > 0].idxmin()]
                    if pd.notna(closest_response.get("response_time")):
                        rt = float(closest_response["response_time"])
        
        # Assign to step function: from stimulus onset to end
        if rt is not None:
            start_idx = int(round(onset * sfreq))
            start_idx = max(0, min(start_idx, n_times - 1))
            response_time_data[0, start_idx:] = rt
    
    # Create and add misc channel
    info = mne.create_info(["response_time_misc"], raw.info["sfreq"], ["misc"])
    misc_raw = mne.io.RawArray(response_time_data, info, first_samp=raw.first_samp)
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


class OpenneuroDs002680Kernel:
    """Dataset kernel for OpenNeuro ds002680 (Go-nogo categorization)."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"] if "file_path" in row else str(row.get("path", ""))
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants.tsv for required_info_fields
        participants_info = {}
        if subject_id:
            participants_path = _find_participants_tsv(file_path)
            if participants_path:
                participants_info = _read_participants_info(participants_path, subject_id)
        
        # Get gender from participants_info (required_info_fields: ['gender'])
        gender = participants_info.get("gender", "unknown")
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participants_info.get("age", "unknown"),
            "sex": gender,
            "amplifier": participants_info.get("amplifier", "unknown"),
            "cap": participants_info.get("cap", "unknown"),
            "handedness": participants_info.get("handedness", "unknown"),
        }
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for all non-misc channels to eeg
        eeg_picks = [i for i, ch_type in enumerate(raw.get_channel_types()) if ch_type not in ("misc", "stim", "bio")]
        if eeg_picks:
            raw.set_channel_types({raw.ch_names[i]: "eeg" for i in eeg_picks})
        
        # Ensure raw is preloaded for adding channels
        if not raw.preload:
            raw.load_data()
        
        # Find and read events.tsv for derived misc channels
        events_path = _find_events_tsv(file_path)
        events_df = None
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Create response_time_misc derived channel from events.tsv:response_time
        if events_df is not None:
            raw = _create_response_time_misc(raw, events_df)
        
        return raw


KERNEL = OpenneuroDs002680Kernel()