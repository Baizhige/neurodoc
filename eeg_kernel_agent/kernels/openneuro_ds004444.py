"""Dataset-specific kernel for openneuro_ds004444 (BMI-HDEEG Dataset 1).

BIDS-compliant high-density EEG dataset for 4-class motor imagery BCI.
130 channels, 1000 Hz, BrainVision .eeg format with events.tsv sidecars.

Source: https://openneuro.org/datasets/ds004444
Source: DOI 10.1038/s41597-023-02260-6 (data descriptor for BMI-HDEEG Dataset 1)

Channel naming: standard extended 10-10 system, 128 EEG + reference + ground
Device: BrainAmp MR plus (inferred from paper, LLM 推断，需人类复核)
Cap: actiCAP 128Ch (inferred from paper, LLM 推断，需人类复核)

Event Mapping (raw meta, from events.tsv value column):
    1 -> rest
    2 -> ready
    3 -> task
    4 -> interval

Super meta (motor imagery class labels, from events.tsv instruction column):
    left hand -> left_hand_MI
    right hand -> right_hand_MI
    feet -> feet_MI
    tongue -> tongue_MI

Note: Event 3 (feet MI / task with instruction="feet") has 0 events across dataset per scan.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


KERNEL_ID = "openneuro_ds004444"

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "gender", "handedness"]

# Native misc channels (if any mislabeled by loader)
_NATIVE_MISC_CHANNELS = []

# Derived misc channels to create
_DERIVED_MISC_CHANNELS = ["trial_index"]

# Event mapping for raw meta (trial phases from value column)
_RAW_EVENT_MAP: Dict[str, str] = {
    "1": "rest",
    "2": "ready", 
    "3": "task",
    "4": "interval",
}

# Super meta: instruction column -> MI class label
# Only task events (value=3) have meaningful MI instructions
_SUPER_MI_MAP: Dict[str, str] = {
    "left hand": "left_hand_MI",
    "right hand": "right_hand_MI",
    "feet": "feet_MI",
    "tongue": "tongue_MI",
}

# Standard 128-channel extended 10-10 naming for BMI-HDEEG
# Source: DOI 10.1038/s41597-023-02260-6, Methods section
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_STANDARD_128_CHANNELS = [
    'Fp1', 'Fpz', 'Fp2', 'AF7', 'AF3', 'AFz', 'AF4', 'AF8',
    'F7', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 'F8',
    'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8',
    'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
    'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8',
    'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8',
    'PO7', 'PO5', 'PO3', 'POz', 'PO4', 'PO6', 'PO8',
    'O1', 'Oz', 'O2', 'Iz',
    # Lower density ring / additional channels for 128ch layout
    'F9', 'F10', 'FT9', 'FT10', 'TP9', 'TP10', 'P9', 'P10',
    'PO9', 'PO10', 'O9', 'O10',
    # Additional intermediate positions common in 128ch caps
    'FFC1h', 'FFC2h', 'FFC3h', 'FFC4h', 'FFC5h', 'FFC6h',
    'FCC1h', 'FCC2h', 'FCC3h', 'FCC4h', 'FCC5h', 'FCC6h',
    'CCP1h', 'CCP2h', 'CCP3h', 'CCP4h', 'CCP5h', 'CCP6h',
    'CPP1h', 'CPP2h', 'CPP3h', 'CPP4h', 'CPP5h', 'CPP6h',
    'PPO1h', 'PPO2h', 'PPO3h', 'PPO4h', 'PPO5h', 'PPO6h',
    'POO1h', 'POO2h', 'POO3h', 'POO4h', 'POO5h', 'POO6h',
    'OI1h', 'OI2h',
    # Reference and ground
    'FCz',  # often used as online reference
]

# Channel rename patterns: non-standard -> standard
# Source: common BrainVision export variants
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_CHANNEL_ALIASES: Dict[str, str] = {
    # Reference electrodes
    'REF': 'FCz',
    'Ref': 'FCz',
    'ref': 'FCz',
    'Reference': 'FCz',
    # Ground
    'GND': 'AFz',
    'Gnd': 'AFz',
    'gnd': 'AFz',
    'Ground': 'AFz',
    # Common BrainVision prefixes
    '1': 'Fp1',
    '2': 'Fpz',
    '3': 'Fp2',
    # Extended numbering if needed
}


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for i, part in enumerate(parts):
        if part.startswith('sub-'):
            # BIDS root is parent of sub-*/
            return os.sep.join(parts[:i]) if i > 0 else '.'
    return None


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XXX[_ses-YYY]_task-ZZZ[_run-RR]_eeg.eeg
    # events: sub-XXX[_ses-YYY]_task-ZZZ[_run-RR]_events.tsv
    base = file_path.replace('_eeg.eeg', '').replace('_eeg.vhdr', '').replace('_eeg.edf', '')
    events_path = f"{base}_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run suffix
    base_no_run = re.sub(r'_run-\d+', '', base)
    if base_no_run != base:
        events_path = f"{base_no_run}_events.tsv"
        if os.path.exists(events_path):
            return events_path
    
    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    if eeg_dir and os.path.isdir(eeg_dir):
        for fname in os.listdir(eeg_dir):
            if fname.endswith('_events.tsv'):
                return os.path.join(eeg_dir, fname)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from file path."""
    bids_root = _find_bids_root(file_path)
    if bids_root:
        participants_path = os.path.join(bids_root, 'participants.tsv')
        if os.path.exists(participants_path):
            return participants_path
    return None


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
    
    participants_tsv = _find_participants_tsv(file_path)
    if participants_tsv is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep='\t')
        # Match subject_id (handle 'sub-001' vs '001')
        search_id = subject_id.replace('sub-', '')
        
        # Try different column names for participant ID
        id_col = None
        for col in df.columns:
            if col.lower() in ['participant_id', 'participant id', 'subject_id', 'subject id']:
                id_col = col
                break
        
        if id_col is None:
            # Assume first column
            id_col = df.columns[0]
        
        # Find matching row
        mask = df[id_col].astype(str).str.replace('sub-', '', regex=False) == search_id
        if not mask.any():
            mask = df[id_col].astype(str) == subject_id
        
        if mask.any():
            row = df[mask].iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row.index:
                    val = row[field]
                    if pd.notna(val):
                        info[field] = str(val).strip()
    except Exception:
        pass
    
    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file if it exists."""
    events_path = _find_events_tsv(file_path)
    if events_path and os.path.exists(events_path):
        try:
            return pd.read_csv(events_path, sep='\t')
        except Exception:
            pass
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map to standardize channel names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for old_name in existing:
        # Direct alias match
        if old_name in _CHANNEL_ALIASES:
            new_name = _CHANNEL_ALIASES[old_name]
            if new_name not in existing or new_name == old_name:
                rename_map[old_name] = new_name
                continue
        
        # Check for numbered channels (e.g., '1', '2', 'Ch1', 'EEG001')
        num_match = re.match(r'^(?:EEG|Ch|Channel)?(\d+)$', old_name, re.IGNORECASE)
        if num_match:
            idx = int(num_match.group(1)) - 1  # 1-based
            if 0 <= idx < len(_STANDARD_128_CHANNELS):
                new_name = _STANDARD_128_CHANNELS[idx]
                if new_name not in existing or new_name == old_name:
                    rename_map[old_name] = new_name
                    continue
    
    return rename_map


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard naming."""
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw.rename_channels(rename_map)
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types based on names."""
    eeg_channels = []
    misc_channels = []
    eog_channels = []
    ecg_channels = []
    
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        if upper in ['FCZ', 'AFZ'] and 'REF' in upper or upper in ['GND', 'GROUND']:
            misc_channels.append(ch_name)
        elif any(x in upper for x in ['EOG', 'EYE', 'HEOG', 'VEOG']):
            eog_channels.append(ch_name)
        elif any(x in upper for x in ['ECG', 'EKG']):
            ecg_channels.append(ch_name)
        elif ch_name in _STANDARD_128_CHANNELS or re.match(r'^[A-Z][a-z]*\d+[a-z]*$', ch_name):
            eeg_channels.append(ch_name)
        else:
            misc_channels.append(ch_name)
    
    type_map = {}
    for ch in eeg_channels:
        type_map[ch] = 'eeg'
    for ch in eog_channels:
        type_map[ch] = 'eog'
    for ch in ecg_channels:
        type_map[ch] = 'ecg'
    for ch in misc_channels:
        type_map[ch] = 'misc'
    
    if type_map:
        raw.set_channel_types(type_map)
    
    return raw


def _add_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return raw
    
    # Required columns in events.tsv
    if 'onset' not in events_df.columns or 'duration' not in events_df.columns:
        return raw
    
    # The onset column is in samples (integer values like 4202, 10145), not seconds.
    # Convert to seconds using sampling frequency.
    sfreq = raw.info['sfreq']
    onsets = events_df['onset'].values / sfreq
    durations = events_df['duration'].values / sfreq
    
    # Use the 'value' column directly as annotation descriptions to preserve event IDs
    # This ensures mne.events_from_annotations(raw) yields the expected event IDs
    descriptions = []
    for _, row in events_df.iterrows():
        # Use 'value' column as the primary description (literal string, no remapping per HC-5)
        if 'value' in row and pd.notna(row['value']):
            val_str = str(int(row['value'])) if float(row['value']) == int(float(row['value'])) else str(row['value'])
            descriptions.append(val_str)
        elif 'trial_type' in row and pd.notna(row['trial_type']):
            descriptions.append(str(row['trial_type']))
        else:
            descriptions.append('unknown')
    
    # Create annotations
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions
    )
    
    raw.set_annotations(annotations)
    return raw


def _add_derived_misc_channels(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Add derived misc channels to raw."""
    sfreq = raw.info['sfreq']
    n_times = len(raw.times)
    
    for ch_name in _DERIVED_MISC_CHANNELS:
        if ch_name == "trial_index":
            # Create trial index channel: step function that increments at each trial onset
            data = np.zeros((1, n_times))
            
            if events_df is not None and 'trial' in events_df.columns and 'onset' in events_df.columns:
                # Sort by onset to ensure proper ordering
                sorted_df = events_df.sort_values('onset')
                for trial_num, onset in zip(sorted_df['trial'].values, sorted_df['onset'].values):
                    # onset is in samples, convert to time index
                    sample_idx = int(onset)
                    if 0 <= sample_idx < n_times:
                        data[0, sample_idx:] = float(trial_num)
            
            info = mne.create_info([ch_name], sfreq, ch_types=['misc'])
            raw_trial = mne.io.RawArray(data, info)
            raw.add_channels([raw_trial], force_update_info=True)
    
    return raw


class Kernel:
    """Dataset kernel for openneuro_ds004444."""

    def __init__(self):
        self.kernel_id = KERNEL_ID

    def process(self, file_path: str) -> Dict[str, Any]:
        """Process a single EEG file and return standardized output."""
        # Determine file type and load
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.eeg':
            # BrainVision format - need .vhdr header
            vhdr_path = file_path.replace('.eeg', '.vhdr')
            if os.path.exists(vhdr_path):
                raw = mne.io.read_raw_brainvision(vhdr_path, preload=False)
            else:
                # Try finding .vhdr in same directory
                eeg_dir = os.path.dirname(file_path)
                base_name = os.path.basename(file_path).replace('.eeg', '')
                vhdr_path = os.path.join(eeg_dir, base_name + '.vhdr')
                if os.path.exists(vhdr_path):
                    raw = mne.io.read_raw_brainvision(vhdr_path, preload=False)
                else:
                    raise FileNotFoundError(f"Cannot find .vhdr for {file_path}")
        elif file_ext == '.vhdr':
            raw = mne.io.read_raw_brainvision(file_path, preload=False)
        elif file_ext == '.edf':
            raw = mne.io.read_raw_edf(file_path, preload=False)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Rename channels to standard naming
        raw = _rename_channels(raw)

        # Set channel types
        raw = _set_channel_types(raw)

        # Read events.tsv
        events_df = _read_events_tsv(file_path)

        # Add annotations from events.tsv - this is critical for event extraction
        if events_df is not None:
            raw = _add_annotations_from_events_tsv(raw, events_df)

        # Add derived misc channels
        raw = _add_derived_misc_channels(raw, events_df)

        # Extract subject info
        subject_id = _get_subject_id_from_path(file_path)
        subject_info = _read_participants_info(file_path, subject_id or "unknown")

        # Build eegunity_description
        description = {
            "kernel_id": self.kernel_id,
            "dataset_id": "ds004444",
            "dataset_name": "BMI-HDEEG Dataset 1",
            "file_path": file_path,
            "subject_id": subject_id,
            "sampling_frequency": raw.info['sfreq'],
            "n_channels": len(raw.ch_names),
            "n_times": len(raw.times),
            "duration_sec": raw.times[-1] if len(raw.times) > 0 else 0,
            "channel_names": raw.ch_names,
            "eeg_channels": [ch for ch, t in raw.get_channel_types(picks=None).items() if t == 'eeg'],
            "misc_channels": [ch for ch, t in raw.get_channel_types(picks=None).items() if t == 'misc'],
            "eog_channels": [ch for ch, t in raw.get_channel_types(picks=None).items() if t == 'eog'],
            "ecg_channels": [ch for ch, t in raw.get_channel_types(picks=None).items() if t == 'ecg'],
            "event_count": len(raw.annotations) if raw.annotations else 0,
            "event_descriptions": list(set(raw.annotations.description)) if raw.annotations else [],
            "subject_age": subject_info.get("age", "unknown"),
            "subject_gender": subject_info.get("gender", "unknown"),
            "subject_handedness": subject_info.get("handedness", "unknown"),
            "has_events_tsv": events_df is not None,
            "events_tsv_columns": list(events_df.columns) if events_df is not None else [],
            "bids_root": _find_bids_root(file_path),
        }

        return {
            "raw": raw,
            "eegunity_description": json.dumps(description, default=str),
        }


KERNEL = Kernel()