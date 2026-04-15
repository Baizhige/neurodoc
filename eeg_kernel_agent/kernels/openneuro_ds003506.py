"""Stage1 kernel for openneuro ds003506 - Reward Positivity in Parkinson's.

This dataset contains EEG recordings from a reinforcement learning paradigm
investigating the RewP (Reward Positivity) ERP component in Parkinson's
disease patients vs healthy controls.

Source: https://openneuro.org/datasets/ds003506
Paper DOI: 10.1016/j.brainres.2019.146541

Event structure:
- S  1: Instruction (Choose/volitional)
- S  2: Right Button Choice
- S  3: Feedback +1 (reward)
- S  4: Feedback 0 (no-reward)
- S  5: Instruction (Match/instructed)
- S 10: Imperative Stimulus
- S 11: STATUS (admin)
- S 12: Left Button Choice
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Mapping from Stimulus codes (S  x) to readable event labels
# Source: events.tsv column 'value' + events structure from analysis.md
# Annotator: LLM, 2026-04-10 (需人类复核)
_EVENT_CODE_MAP = {
    "S  1": "Instr: Choose",     # Instruction: volitional choice trial
    "S  2": "Right Button Choice",  # Right-hand response
    "S  3": "FB: +1",            # Reward feedback
    "S  4": "FB: 0",             # No-reward feedback
    "S  5": "Instr: Match",      # Instruction: instructed match trial
    "S 10": "Imperative Stimulus",  # Cue requiring response
    "S 11": "STATUS",            # System status marker (admin)
    "S 12": "Left Button Choice",  # Left-hand response
}

# Reverse map for remapping events array
_CODE_TO_ID = {code: idx + 1 for idx, code in enumerate(_EVENT_CODE_MAP.keys())}
_EVENT_ID_MAP = {label: idx + 1 for idx, label in enumerate(_EVENT_CODE_MAP.values())}

# Standard 10-20 channel names expected (67 total including VEOG and XYZ)
# Source: standard_1020 montage
# The dataset uses standard electrode naming compatible with 10-20 system
_STANDARD_EEG_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO7", "PO3", "PO4", "PO8",
    "FT7", "FT8",
    "TP7", "TP8",
    "POz",
]

# Non-EEG channels to handle
_MISC_CHANNELS = ["VEOG", "X", "Y", "Z"]


def _load_participants_data(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv.
    
    Source: participants.tsv (BIDS standard)
    Returns dict: {subject_id: {age, sex, handedness}}
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            subject_dict = {}
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).strip()
                if subj_id:
                    age_val = row.get("age", "unknown")
                    sex_val = str(row.get("sex", "unknown")).lower()
                    
                    # Ensure age is string
                    if pd.isna(age_val):
                        age_str = "unknown"
                    else:
                        age_str = str(int(age_val)) if isinstance(age_val, (int, float)) else str(age_val)
                    
                    subject_dict[subj_id] = {
                        "age": age_str,
                        "sex": sex_val if sex_val in ["male", "female"] else "unknown",
                    }
            return subject_dict
        except Exception:
            pass
    return {}


def _detect_subject_id(row) -> str:
    """Extract subject ID from row."""
    if hasattr(row, "get"):
        return str(row.get("subject_id", row.get("participant_id", "unknown")))
    return str(getattr(row, "subject_id", getattr(row, "participant_id", "unknown")))


def _remap_stim_channel_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap stimulus channel events to readable annotations.
    
    This dataset uses a stimulus channel with event codes like 'S  1', 'S  2', etc.
    We convert these to readable labels.
    """
    original_desc = ""
    
    # Get existing annotations if any
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        if event_id:
            # Already has annotations
            return raw
    except Exception:
        pass
    
    # Check if there's a stimulus channel
    stim_chs = [ch for ch in raw.ch_names if 'stim' in ch.lower() or ch == 'STI']
    if not stim_chs:
        return raw
    
    stim_ch = stim_chs[0]
    
    # Get data from stimulus channel
    stim_idx = raw.ch_names.index(stim_ch)
    stim_data, times = raw[stim_idx, :]
    
    # Find events (threshold crossings)
    threshold = 0.5 * np.max(np.abs(stim_data))
    above_threshold = np.diff((stim_data > threshold).astype(int))
    event_indices = np.where(above_threshold > 0)[1]
    
    if len(event_indices) == 0:
        return raw
    
    # Extract event codes at these indices
    sfreq = raw.info["sfreq"]
    onsets = times[event_indices]
    
    # Get event codes (the stimulus channel often has the code value)
    codes = stim_data[0, event_indices]
    
    # Build annotations
    descriptions = []
    valid_onsets = []
    
    for idx, (onset, code) in enumerate(zip(onsets, codes)):
        # Find closest event code match
        code_str = str(int(code)).zfill(3)
        matched_label = None
        
        for stim_code, label in _EVENT_CODE_MAP.items():
            code_num = int(stim_code.replace("S", "").strip())
            if code_num == int(code):
                matched_label = label
                break
        
        if matched_label is None:
            matched_label = f"stim: {int(code)}"
        
        descriptions.append(matched_label)
        valid_onsets.append(onset)
    
    if valid_onsets:
        annotations = mne.Annotations(
            onset=valid_onsets,
            duration=[0.0] * len(valid_onsets),
            description=descriptions,
        )
        raw.set_annotations(annotations)
    
    return raw


def _set_channel_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for EEG channels.
    
    Attempts to set montage based on available channels.
    Non-standard channel names are kept as-is.
    """
    # Get current channel names
    ch_names = raw.ch_names
    
    # Find EEG-like channels
    eeg_channels = []
    other_channels = []
    
    for ch in ch_names:
        ch_upper = ch.upper()
        # Check if it's a standard 10-20 channel
        if any(std in ch_upper for std in _STANDARD_EEG_CHANNELS):
            eeg_channels.append(ch)
        elif ch in _MISC_CHANNELS:
            other_channels.append(ch)
        elif ch.upper().startswith("EEG"):
            eeg_channels.append(ch)
        else:
            other_channels.append(ch)
    
    # Try to set montage for EEG channels
    try:
        # Get the subset that can be mapped
        existing_eeg = [ch for ch in _STANDARD_EEG_CHANNELS if ch in ch_names]
        if len(existing_eeg) >= 10:  # Only set if we have enough standard channels
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Rename channels to match montage if needed
            rename_map = {}
            for ch in ch_names:
                if ch in montage.ch_names:
                    rename_map[ch] = ch
            
            if rename_map:
                raw.rename_channels(rename_map)
            
            raw.set_montage("standard_1020", verbose=False)
    except Exception:
        pass  # Montage setting is best-effort
    
    return raw


def _get_subject_metadata(row, dataset_path: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or infer defaults.
    
    Returns dict with age, sex, handedness, amplifier, cap.
    """
    subject_id = _detect_subject_id(row)
    participants_data = _load_participants_data(dataset_path)
    
    if subject_id in participants_data:
        subj_data = participants_data[subject_id]
        return {
            "age": subj_data.get("age", "unknown"),
            "sex": subj_data.get("sex", "unknown"),
            "handedness": "unknown",  # Not in participants.tsv per analysis
            "amplifier": "unknown",    # Need to check dataset_description.json
            "cap": "unknown",
        }
    
    # Default values if not found
    return {
        "age": "unknown",      # LLM 推断，需人类复核
        "sex": "unknown",      # LLM 推断，需人类复核
        "handedness": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
    }


class OpenNeuroDS003506Kernel:
    """Stage1 kernel for openneuro ds003506 dataset.
    
    This kernel handles:
    - Event remapping from stimulus codes to readable labels
    - Channel montage setting (standard 10-20)
    - eegunity_description metadata
    - Support for RewP analysis tasks (FB +1 vs FB 0 classification)
    """
    
    KERNEL_ID: str = "openneuro-ds003506-stage1"
    
    # Event mapping for downstream tasks
    TARGET_EVENTS = {
        "FB: +1": 1,      # Reward feedback
        "FB: 0": 0,       # No-reward feedback
        "Instr: Choose": 1,   # Volitional choice
        "Instr: Match": 0,   # Instructed match
        "Left Button Choice": 0,
        "Right Button Choice": 1,
    }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to a single EEG recording.
        
        Parameters
        ----------
        udataset : UnifiedDataset
            EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG data
        row : pd.Series
            Row from dataset index containing file paths and metadata
            
        Returns
        -------
        mne.io.BaseRaw
            Processed raw data with annotations and metadata
        """
        # Get dataset path for loading participants.tsv
        dataset_path = ""
        if hasattr(row, "get"):
            file_path = row.get("File Path", row.get("file_path", ""))
            if file_path:
                # Infer dataset path from file path
                parts = file_path.split(os.sep)
                for i, part in enumerate(parts):
                    if part.startswith("sub-"):
                        dataset_path = os.sep.join(parts[:i])
                        break
        
        # Store original description
        original_desc = raw.info.get("description", "")
        
        # Remap stimulus channel events to readable annotations
        raw = _remap_stim_channel_events(raw)
        
        # Set channel montage for standard 10-20 system
        raw = _set_channel_montage(raw)
        
        # Get subject metadata
        subject_meta = _get_subject_metadata(row, dataset_path)
        
        # Build eegunity_description
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": subject_meta["amplifier"],
                "cap": subject_meta["cap"],
                "handedness": subject_meta["handedness"],
            }
        }
        
        raw.info["description"] = json.dumps(description_dict)
        
        # Set channel types for non-EEG channels
        ch_types = {}
        for ch in raw.ch_names:
            ch_upper = ch.upper()
            if ch_upper == "VEOG":
                ch_types[ch] = "eog"
            elif ch_upper in ["X", "Y", "Z"]:
                ch_types[ch] = "misc"
            elif ch_upper.startswith("EOG"):
                ch_types[ch] = "eog"
        
        if ch_types:
            try:
                raw.set_channel_types(ch_types)
            except Exception:
                pass
        
        return raw


KERNEL = OpenNeuroDS003506Kernel()