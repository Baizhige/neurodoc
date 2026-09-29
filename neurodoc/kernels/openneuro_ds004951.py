"""OpenNeuro ds004951 stage1 kernel for EEGUnity.

Braille Letters EEG dataset - tactile stimulation of Braille letters
to left/right index fingers, comparing sighted controls and blind individuals.

Source: https://openneuro.org/datasets/ds004951
DOI: 10.7554/eLife.98148

Paradigm: Braille letter identification (16 letters, S1-S16)
         8-class subset: B, C, D, L, M, N, V, Z

Device: BrainVision MR plus (64-channel EEG, 1000 Hz)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Dataset documentation / OpenNeuro ds004951 README
# BrainVision standard 64-channel cap with standard_1020 extended layout
# Channel names are already standard in the .vhdr/.eeg files
# Annotator: LLM, 2026-04-08, verified from standard BrainVision 64ch layout
# No renaming needed for this dataset - channels already use standard_1020 names

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]

# Required native misc channels
_REQUIRED_NATIVE_MISC = ["HEOG"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["trial_onset_time"]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to the data file."""
    current_dir = os.path.dirname(file_path)
    # Walk up to find dataset root (where participants.tsv should be)
    for _ in range(5):  # BIDS max depth is usually < 5
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
            os.path.join(current_dir, "../..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.isfile(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for a data file."""
    # BIDS naming: sub-XX_ses-YY_task-ZZ_run-WW_eeg.<ext> -> sub-XX_ses-YY_task-ZZ_run-WW_events.tsv
    base = file_path
    # Remove common EEG extensions
    for ext in ['.eeg', '.vhdr', '.vmrk', '.edf', '.bdf', '.set', '.fif']:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Try exact BIDS replacement
    events_path = base.replace('_eeg', '_events') + '.tsv'
    if os.path.isfile(events_path):
        return events_path
    
    # Try direct sibling
    events_path = base + '_events.tsv'
    if os.path.isfile(events_path):
        return events_path
    
    # Try in parent directory (some BIDS layouts)
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    events_path = os.path.join(dir_name, base_name + '_events.tsv')
    if os.path.isfile(events_path):
        return events_path
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep='\t')
        # Normalize subject_id format
        if not subject_id.startswith('sub-'):
            subject_id = f"sub-{subject_id}"
        
        # Find row for this subject
        subj_col = 'participant_id'
        if subj_col not in df.columns:
            # Try alternatives
            for col in df.columns:
                if 'participant' in col.lower() or 'subject' in col.lower():
                    subj_col = col
                    break
        
        row = df[df[subj_col] == subject_id]
        if row.empty:
            # Try without 'sub-' prefix
            row = df[df[subj_col] == subject_id.replace('sub-', '')]
        
        if row.empty:
            return {}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in row.columns:
                val = row[field].values[0]
                # Handle missing/NaN
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val).strip()
            else:
                result[field] = "unknown"
        
        return result
    except Exception:
        return {}


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t')
        return df
    except Exception:
        return None


def _create_trial_onset_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'trial_onset_time' from events.tsv onset column.
    
    Creates a step function channel where each trial's onset value is held
    from that trial's onset until the next trial's onset (or end of recording).
    Between trials, value is 0.
    """
    sfreq = raw.info['sfreq']
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))
    
    # Get onset values in samples
    onsets_sec = events_df['onset'].values
    onsets_samp = (onsets_sec * sfreq).astype(int)
    onset_values = events_df['onset'].values  # The actual onset time values
    
    # Create step function: at each onset, set value until next onset
    for i in range(len(onsets_samp)):
        start = onsets_samp[i]
        if i + 1 < len(onsets_samp):
            end = onsets_samp[i + 1]
        else:
            end = n_samples
        
        # Clamp to valid range
        start = max(0, min(start, n_samples))
        end = max(0, min(end, n_samples))
        
        if start < end:
            data[0, start:end] = onset_values[i]
    
    # Create RawArray for the new channel
    info = mne.create_info(
        ch_names=['trial_onset_time'],
        sfreq=sfreq,
        ch_types=['misc']
    )
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    
    # Add to existing raw
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


def _derive_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Derive MNE Annotations from events.tsv when raw lacks embedded events.
    
    BrainVision .eeg files without .vmrk or with empty event tables need
    annotations reconstructed from the BIDS events.tsv sidecar.
    """
    if events_df is None or events_df.empty:
        return raw
    
    # Handle BOM-prefixed column names from the dataset
    col_map = {}
    for col in events_df.columns:
        clean = col.lstrip('\ufeff')
        col_map[clean] = col
    
    onset_col = col_map.get('onset', 'onset')
    duration_col = col_map.get('duration', 'duration')
    trial_type_col = col_map.get('trial_type', 'trial_type')
    value_col = col_map.get('value', 'value')
    
    if onset_col not in events_df.columns:
        return raw
    
    onsets = events_df[onset_col].values
    durations = events_df[duration_col].values if duration_col in events_df.columns else np.zeros(len(onsets))
    
    # Description: prefer trial_type (contains distinguishable labels like "Stimulus/S101")
    # This column carries meaningful, distinguishable event labels per the evidence.
    # Fallback to value only if trial_type is missing/empty.
    descriptions = []
    for i in range(len(onsets)):
        desc = None
        if trial_type_col in events_df.columns:
            val = events_df[trial_type_col].iloc[i]
            if pd.notna(val):
                desc = str(val).strip()
        if desc is None and value_col in events_df.columns:
            val = events_df[value_col].iloc[i]
            if pd.notna(val):
                desc = str(val).strip()
        if desc is None:
            desc = "event"
        descriptions.append(desc)
    
    # Create annotations with orig_time=None to match raw time base
    # Onsets are in seconds relative to recording start
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=None
    )
    
    raw.set_annotations(annotations)
    return raw


class OpenNeuroDS004951Kernel:
    KERNEL_ID = "openneuro_ds004951"
    DATASET_NAME = "OpenNeuro ds004951: Braille Letters EEG"
    DATASET_URL = "https://openneuro.org/datasets/ds004951"
    CITATION = "10.7554/eLife.98148"
    VERSION = "1.0.0"

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        
        # Extract subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants.tsv info
        participants_path = _find_participants_tsv(file_path)
        participants_info = {}
        if participants_path and subject_id:
            participants_info = _read_participants_info(participants_path, subject_id)
        
        # Ensure all required fields are present
        for field in _REQUIRED_INFO_FIELDS:
            if field not in participants_info:
                participants_info[field] = "unknown"
        
        # Read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = None
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Derive annotations from events.tsv — the BrainVision .eeg files have no
        # embedded markers, so we MUST reconstruct annotations from the BIDS sidecar.
        # The trial_type column carries distinguishable labels (e.g. "Stimulus/S101").
        if events_df is not None and not events_df.empty:
            raw = _derive_annotations_from_events_tsv(raw, events_df)
        
        # Create derived misc channel for trial onset times
        if events_df is not None and not events_df.empty:
            raw = _create_trial_onset_misc_channel(raw, events_df)
        
        # Set standard montage (BrainVision 64ch standard_1020)
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='warn')
        except Exception:
            pass
        
        # Ensure HEOG is marked as misc if present
        for ch_name in raw.ch_names:
            if ch_name.upper() == 'HEOG' or ch_name.upper().startswith('HEOG'):
                idx = raw.ch_names.index(ch_name)
                if raw.get_channel_types()[idx] != 'misc':
                    raw.set_channel_types({ch_name: 'misc'})
        
        # Build eegunity_description
        description = {
            "dataset_id": self.KERNEL_ID,
            "dataset_name": self.DATASET_NAME,
            "dataset_url": self.DATASET_URL,
            "citation": self.CITATION,
            "kernel_version": self.VERSION,
            "subject_id": subject_id or "unknown",
            "age": participants_info.get("age", "unknown"),
            "sex": participants_info.get("sex", "unknown"),
            "handedness": participants_info.get("handedness", "unknown"),
            "amplifier": participants_info.get("amplifier", "unknown"),
            "cap": participants_info.get("cap", "unknown"),
            "task": "letters",
            "paradigm": "Braille letter identification",
            "stimulus_type": "tactile",
            "n_channels": len(raw.ch_names),
            "sfreq": raw.info['sfreq'],
            "recording_duration_sec": raw.n_times / raw.info['sfreq'],
            "has_events_tsv": events_path is not None,
            "events_tsv_path": events_path or "none",
            "n_events_from_tsv": len(events_df) if events_df is not None else 0,
            "n_annotations": len(raw.annotations) if raw.annotations is not None else 0,
            "required_native_misc": _REQUIRED_NATIVE_MISC,
            "required_derived_misc": _REQUIRED_DERIVED_MISC,
            "present_native_misc": [c for c in raw.ch_names if c.upper() == 'HEOG' or c.upper().startswith('HEOG')],
            "present_derived_misc": [c for c in raw.ch_names if c == 'trial_onset_time'],
        }
        
        # Store description in raw.info['description'] as JSON
        raw.info['description'] = json.dumps(description)
        
        return raw


KERNEL = OpenNeuroDS004951Kernel()