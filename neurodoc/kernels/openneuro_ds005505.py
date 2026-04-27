"""OpenNeuro DS005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

This kernel processes the Healthy Brain Network (HBN) EEG Release 1 dataset,
a large-scale developmental battery with 129-channel EEG recordings at 500 Hz
collected from children and adolescents (ages 5.2–21.7).

The dataset contains six experimental paradigms: naturalistic movie watching,
eyes-open/closed resting state, sensory contrast detection, surrounding
suppression, sequence learning, and symbol search tasks.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1101/2024.10.03.615261

Channel naming: The HBN dataset uses standard 10-20 extended montage with
129 channels. Original channel names may have prefixes like "EEG" that need
standardization.

Required info fields: age, sex, amplifier, cap, handedness, attention, ehq_total, externalizing, full_pheno, internalizing, p_factor, seqLearning6target
Required derived misc: accuracy (from user_answer vs correct_answer), response_time
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# HBN 129-channel standard montage channel names (10-20 extended system)
# Source: HBN dataset documentation and BrainVision channel files
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_HBN_129_CHANNELS = [
    # Standard 10-20 channels
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # Extra channels for 129-channel system
    "F9", "F10",
    "FT9", "FT10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "PO1", "PO2",
    # Reference and EOG channels commonly present
    "M1", "M2",
    "VEO", "HEO", "VEOG", "HEOG",
    "CB1", "CB2",
    "A1", "A2",
    "REF", "CzREF",
    "Status", "Trigger",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for HBN 129-channel standard montage.
    
    The HBN EEG data may have channel names with various prefixes
    (e.g., 'EEG 001', 'CH01', 'Fp1') that need standardization.
    
    Returns
    -------
    Dict[str, str]
        Dictionary mapping original names to standard names.
    """
    rename_map = {}
    existing_names = list(raw.ch_names)
    used_targets = set()
    
    for ch in existing_names:
        cleaned = ch.strip()
        original_cleaned = cleaned
        
        # Strip common prefixes: "EEG ", "EEG-", "eeg_", "CH", "Ch ", "Ch"
        for prefix in ["EEG ", "EEG-", "eeg_", "Ch ", "CH", "Ch"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Handle "X1" format where X is a letter (common in some systems)
        # e.g., "E1", "E2" -> keep number part if it maps
        
        # Try to match cleaned name to standard channel list
        target = None
        
        # Direct match
        if cleaned in _HBN_129_CHANNELS and cleaned not in used_targets:
            target = cleaned
        # Case-insensitive match
        elif cleaned.upper() in [c.upper() for c in _HBN_129_CHANNELS]:
            for std_ch in _HBN_129_CHANNELS:
                if std_ch.upper() == cleaned.upper() and std_ch not in used_targets:
                    target = std_ch
                    break
        # Handle "001", "002" -> try to map by position if we have a position map
        # For HBN 129, numeric channels typically map to specific positions
        # Source: HBN documentation; Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
        
        if target is not None:
            rename_map[ch] = target
            used_targets.add(target)
    
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # Match patterns like sub-NDARAB123ABC or sub-01
    match = re.search(r'sub-([A-Za-z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file relative to the data file."""
    # Walk up directory tree looking for participants.tsv
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # Limit search depth
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-X_task-Y_eeg.edf -> sub-X_task-Y_events.tsv
    base = file_path.replace("_eeg.edf", "_events.tsv")
    base = base.replace("_eeg.set", "_events.tsv")
    base = base.replace("_eeg.vhdr", "_events.tsv")
    base = base.replace("_eeg.eeg", "_events.tsv")
    base = base.replace("_eeg.fif", "_events.tsv")
    
    # Also check in eeg/ subdirectory
    dir_name = os.path.dirname(file_path)
    parent_dir = os.path.dirname(dir_name)
    
    candidates = [
        base,
        os.path.join(dir_name, os.path.basename(base)),
        os.path.join(parent_dir, "eeg", os.path.basename(base)),
    ]
    
    for cand in candidates:
        cand = os.path.normpath(cand)
        if os.path.exists(cand):
            return cand
    
    # Try pattern matching in same directory
    try:
        files_in_dir = os.listdir(dir_name)
        for f in files_in_dir:
            if f.endswith("_events.tsv"):
                return os.path.join(dir_name, f)
    except OSError:
        pass
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t')
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns: onset, (duration), trial_type or value
    if 'onset' not in events_df.columns:
        return None
    
    onsets = events_df['onset'].values
    
    # Duration
    if 'duration' in events_df.columns:
        durations = events_df['duration'].values
        # Handle n/a or missing
        durations = [0.0 if pd.isna(d) or str(d).lower() in ('n/a', 'na', '') else float(d) for d in durations]
    else:
        durations = [0.0] * len(onsets)
    
    # Description: prefer trial_type, then value, then stim_type
    if 'trial_type' in events_df.columns:
        descriptions = events_df['trial_type'].astype(str).values
    elif 'value' in events_df.columns:
        # Convert to string, handling numeric values
        descriptions = []
        for v in events_df['value'].values:
            if pd.isna(v):
                descriptions.append('unknown')
            else:
                descriptions.append(str(v))
    elif 'stim_type' in events_df.columns:
        descriptions = events_df['stim_type'].astype(str).values
    else:
        descriptions = ['event'] * len(onsets)
    
    # Filter out empty descriptions
    valid_idx = [i for i, d in enumerate(descriptions) if d and str(d).lower() not in ('nan', 'n/a', 'na', '')]
    if len(valid_idx) == 0:
        return None
    
    onsets = [onsets[i] for i in valid_idx]
    durations = [durations[i] for i in valid_idx]
    descriptions = [descriptions[i] for i in valid_idx]
    
    # Convert onsets from seconds to the format MNE expects (already in seconds for BIDS)
    # MNE Annotations expects onsets in seconds relative to the recording start
    try:
        annot = mne.Annotations(
            onset=[float(o) for o in onsets],
            duration=[float(d) for d in durations],
            description=descriptions,
        )
        return annot
    except Exception:
        return None


def _read_participants_tsv(participants_path: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv file."""
    try:
        df = pd.read_csv(participants_path, sep='\t')
        return df
    except Exception:
        return None


def _get_subject_info_from_participants(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract subject information from participants dataframe."""
    if participants_df is None or len(participants_df) == 0:
        return {}
    
    # Find row matching subject_id
    # BIDS participant_id column typically has format "sub-NDARAB123ABC"
    participant_id_col = 'participant_id'
    if participant_id_col not in participants_df.columns:
        # Try alternatives
        for col in participants_df.columns:
            if col.lower() in ('participant_id', 'subject_id', 'sub_id'):
                participant_id_col = col
                break
    
    if participant_id_col not in participants_df.columns:
        return {}
    
    # Match subject_id - handle both "sub-NDARAB123ABC" and "NDARAB123ABC" formats
    search_id = subject_id if subject_id.startswith('sub-') else f"sub-{subject_id}"
    search_id_short = subject_id.replace('sub-', '') if subject_id.startswith('sub-') else subject_id
    
    mask = (
        (participants_df[participant_id_col].astype(str) == search_id) |
        (participants_df[participant_id_col].astype(str) == search_id_short)
    )
    
    matching_rows = participants_df[mask]
    if len(matching_rows) == 0:
        return {}
    
    row = matching_rows.iloc[0]
    info = {}
    for col in participants_df.columns:
        val = row[col]
        if pd.isna(val):
            info[col] = ""
        else:
            info[col] = str(val)
    
    return info


def _find_task_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS task name from file path."""
    match = re.search(r'task-([a-zA-Z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


class OpenNeuroDS005505Kernel:
    """Stage-1 kernel for OpenNeuro DS005505 (HBN EEG Release 1)."""
    
    DATASET_NAME = "openneuro_ds005505"
    DATASET_PATH = "openneuro/ds005505"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("file_path", "")) if hasattr(row, "get") else str(getattr(row, "file_path", ""))
        subject_id = _get_subject_id_from_path(file_path)
        task_name = _find_task_from_path(file_path)
        
        # Read participants.tsv for subject info
        participants_path = _find_participants_tsv(file_path)
        participants_df = _read_participants_tsv(participants_path) if participants_path else None
        subject_info = _get_subject_info_from_participants(participants_df, subject_id) if participants_df else {}
        
        # Build eegunity_description with required fields from participants.tsv
        eegunity_description = {
            "age": subject_info.get("age", ""),
            "sex": subject_info.get("sex", ""),
            "amplifier": subject_info.get("amplifier", ""),
            "cap": subject_info.get("cap", ""),
            "handedness": subject_info.get("handedness", ""),
            "attention": subject_info.get("attention", ""),
            "ehq_total": subject_info.get("ehq_total", ""),
            "externalizing": subject_info.get("externalizing", ""),
            "full_pheno": subject_info.get("full_pheno", ""),
            "internalizing": subject_info.get("internalizing", ""),
            "p_factor": subject_info.get("p_factor", ""),
            "seqLearning6target": subject_info.get("seqLearning6target", ""),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Standardize channel names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set standard 10-20 extended montage if possible
        try:
            montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
            raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
        except Exception:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
            except Exception:
                pass
        
        # Process events from events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path) if events_path else None
        
        if events_df is not None and len(events_df) > 0:
            # Convert events to annotations and add to raw
            annot = _events_to_annotations(events_df, raw.info["sfreq"])
            if annot is not None:
                # Check if raw already has annotations
                if raw.annotations is not None and len(raw.annotations) > 0:
                    # Combine existing with new
                    raw.set_annotations(raw.annotations + annot)
                else:
                    raw.set_annotations(annot)
        
        # Create derived misc channels: accuracy and response_time
        # These are derived from events.tsv columns if available
        n_times = len(raw.times)
        sfreq = raw.info["sfreq"]
        
        # accuracy: from user_answer vs correct_answer in events.tsv
        accuracy_data = None
        if events_df is not None:
            if "user_answer" in events_df.columns and "correct_answer" in events_df.columns:
                # Create trial-locked step function
                if "onset" in events_df.columns:
                    accuracy_data = np.zeros((1, n_times))
                    for _, ev_row in events_df.iterrows():
                        onset_sample = int(float(ev_row["onset"]) * sfreq)
                        if onset_sample < n_times:
                            user_ans = str(ev_row.get("user_answer", "")).strip().lower()
                            correct_ans = str(ev_row.get("correct_answer", "")).strip().lower()
                            if user_ans and correct_ans and user_ans not in ("n/a", "na", "", "nan"):
                                acc = 1.0 if user_ans == correct_ans else 0.0
                            else:
                                acc = np.nan
                            end_sample = min(onset_sample + int(sfreq), n_times)  # 1 second duration or to end
                            accuracy_data[0, onset_sample:end_sample] = acc
                    # Fill NaN with 0 for finite requirement, or use np.nan_to_num
                    accuracy_data = np.nan_to_num(accuracy_data, nan=0.0)
        
        if accuracy_data is None:
            # Constant broadcast from participants.tsv if available, else zeros
            accuracy_val = float(subject_info.get("accuracy", 0.0)) if "accuracy" in subject_info else 0.0
            accuracy_data = np.full((1, n_times), accuracy_val)
        
        # response_time: from events.tsv
        response_time_data = None
        if events_df is not None:
            if "response_time" in events_df.columns:
                if "onset" in events_df.columns:
                    response_time_data = np.zeros((1, n_times))
                    for _, ev_row in events_df.iterrows():
                        onset_sample = int(float(ev_row["onset"]) * sfreq)
                        if onset_sample < n_times:
                            rt = ev_row.get("response_time", 0.0)
                            try:
                                rt_val = float(rt) if not pd.isna(rt) else 0.0
                            except (ValueError, TypeError):
                                rt_val = 0.0
                            end_sample = min(onset_sample + int(sfreq), n_times)
                            response_time_data[0, onset_sample:end_sample] = rt_val
        
        if response_time_data is None:
            # Constant broadcast from participants.tsv if available, else zeros
            rt_val = float(subject_info.get("response_time", 0.0)) if "response_time" in subject_info else 0.0
            response_time_data = np.full((1, n_times), rt_val)
        
        # Add misc channels using add_channels
        info_acc = mne.create_info(ch_names=["accuracy"], sfreq=sfreq, ch_types=["misc"])
        raw_acc = mne.io.RawArray(accuracy_data, info_acc, first_samp=raw.first_samp)
        
        info_rt = mne.create_info(ch_names=["response_time"], sfreq=sfreq, ch_types=["misc"])
        raw_rt = mne.io.RawArray(response_time_data, info_rt, first_samp=raw.first_samp)
        
        raw = raw.add_channels([raw_acc, raw_rt], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS005505Kernel()