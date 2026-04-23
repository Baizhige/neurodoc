"""Dataset-specific kernel for openneuro_ds001785.

Evidence accumulation / vibrotactile detection task.
71-channel EEG at 1024 Hz from 21 subjects.
BIDS format with events.tsv and participants.tsv.

Supports:
- Raw meta: stimulus events 200/201, response 100, SDT outcomes 101-104
- Super meta: confidence ratings, response times, stimulus amplitude/latency
- Derived misc channels: confidence, response_time, response_time2, stimamp, stimon

Source: https://doi.org/10.1038/s41467-021-23540-y
"""

from __future__ import annotations

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Channel rename map for 71-channel system
# Source: Paper supplementary materials / standard 10-20 extended montage
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "Fpz": "Fpz",
    "Af7": "AF7",
    "Af3": "AF3",
    "Af4": "AF4",
    "Af8": "AF8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "Fcz": "FCz",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC3": "FC3",
    "FC4": "FC4",
    "FC5": "FC5",
    "FC6": "FC6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP3": "CP3",
    "CP4": "CP4",
    "CP5": "CP5",
    "CP6": "CP6",
    "CPz": "CPz",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO1": "PO1",
    "PO2": "PO2",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO5": "PO5",
    "PO6": "PO6",
    "POz": "POz",
    "VEOG": "VEOG",
    "HEOG": "HEOG",
    "EOGvu": "VEOG",
    "EOGhl": "HEOG",
    "EOG": "EOG",
    "Ref": "REF",
    "Reference": "REF",
    "Gnd": "GND",
    "Ground": "GND",
}

_DEVICE_INFO = {
    "amplifier": "BrainAmp MR plus",
    "cap": "Ag/AgCl",
}


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r'sub-(\d+)', os.path.basename(file_path))
    if match:
        return match.group(1)
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith('sub-'):
            return part.replace('sub-', '')
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    base = file_path.rsplit('_eeg.', 1)[0]
    events_path = base + '_events.tsv'
    if os.path.exists(events_path):
        return events_path
    
    base_no_run = base.rsplit('_run-', 1)[0] if '_run-' in base else base
    for suffix in ['_events.tsv']:
        alt_path = base_no_run + suffix
        if os.path.exists(alt_path):
            return alt_path
    
    eeg_dir = os.path.dirname(file_path)
    fname_base = os.path.basename(base)
    for f in os.listdir(eeg_dir):
        if f.endswith('_events.tsv') and f.startswith(fname_base.split('_run-')[0]):
            return os.path.join(eeg_dir, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from dataset root."""
    current = os.path.dirname(file_path)
    for _ in range(5):
        cand = os.path.join(current, 'participants.tsv')
        if os.path.exists(cand):
            return os.path.realpath(cand)
        current = os.path.dirname(current)
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t', dtype=str, keep_default_na=False)
        return df
    except Exception:
        return pd.DataFrame()


def _read_participants_tsv(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep='\t', dtype=str, keep_default_na=False)
        sub_col = 'participant_id'
        if sub_col not in df.columns:
            return {}
        
        sub_ids = df[sub_col].astype(str)
        matches = df[sub_ids == subject_id]
        if matches.empty:
            matches = df[sub_ids == f'sub-{subject_id}']
        if matches.empty:
            matches = df[sub_ids == f'sub-{int(subject_id):02d}']
        if matches.empty:
            try:
                sid_num = int(subject_id)
                matches = df[pd.to_numeric(sub_ids.str.replace('sub-', '', regex=False), errors='coerce') == sid_num]
            except ValueError:
                pass
        
        if matches.empty:
            return {}
        
        row = matches.iloc[0]
        result = {}
        for col in df.columns:
            if col != sub_col:
                result[col] = str(row[col]) if pd.notna(row[col]) and str(row[col]) != '' else 'unknown'
        return result
    except Exception:
        return {}


def _create_derived_misc_channel(raw: mne.io.BaseRaw, channel_name: str, events_df: pd.DataFrame, 
                                  value_col: str, onset_col: str = 'onset') -> None:
    """Create a derived MISC channel from events.tsv data."""
    if not raw.preload:
        raw.load_data()
    
    sfreq = raw.info['sfreq']
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))
    
    if events_df.empty or value_col not in events_df.columns or onset_col not in events_df.columns:
        info = mne.create_info([channel_name], sfreq, ch_types=['misc'])
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp, verbose=False)
        raw.add_channels([misc_raw], force_update_info=True)
        return
    
    for _, event_row in events_df.iterrows():
        try:
            onset_sec = float(event_row[onset_col])
            onset_sample = int(onset_sec * sfreq)
            
            val_str = str(event_row[value_col])
            if val_str == '' or val_str.lower() == 'n/a':
                continue
            val = float(val_str)
            
            duration_sec = 0
            if 'duration' in event_row and str(event_row['duration']) not in ['', 'n/a', 'N/A']:
                try:
                    duration_sec = float(event_row['duration'])
                except ValueError:
                    duration_sec = 0
            
            if duration_sec > 0:
                end_sample = min(int((onset_sec + duration_sec) * sfreq), n_samples)
            else:
                end_sample = n_samples
            
            if onset_sample < n_samples:
                data[0, onset_sample:end_sample] = val
        except (ValueError, KeyError):
            continue
    
    info = mne.create_info([channel_name], sfreq, ch_types=['misc'])
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp, verbose=False)
    raw.add_channels([misc_raw], force_update_info=True)


def _create_constant_misc_channel(raw: mne.io.BaseRaw, channel_name: str, value: float) -> None:
    """Create a constant-value MISC channel."""
    if not raw.preload:
        raw.load_data()
    
    sfreq = raw.info['sfreq']
    n_samples = raw.n_times
    data = np.full((1, n_samples), value)
    
    info = mne.create_info([channel_name], sfreq, ch_types=['misc'])
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp, verbose=False)
    raw.add_channels([misc_raw], force_update_info=True)


def _add_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> None:
    """Add annotations from events.tsv to raw."""
    if events_df.empty or 'onset' not in events_df.columns:
        return
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        try:
            onset = float(row['onset'])
        except (ValueError, TypeError):
            continue
        
        try:
            duration = float(row['duration']) if 'duration' in row and str(row['duration']) not in ['', 'n/a', 'N/A'] else 0.0
        except (ValueError, TypeError):
            duration = 0.0
        
        # Use event_value column for the annotation description to preserve numeric event IDs
        # This ensures mne.events_from_annotations returns the expected event IDs
        desc = ''
        # Priority: event_value (numeric IDs like '10', '100', '101', etc.), then trial_type
        for col in ['event_value', 'value', 'trial_type', 'event_type', 'stim_type']:
            if col in row and str(row[col]) not in ['', 'n/a', 'N/A']:
                desc = str(row[col])
                break
        
        if not desc:
            desc = 'unknown'
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    if onsets:
        # Remove any existing annotations to avoid conflicts
        raw.set_annotations(None)
        annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
        raw.set_annotations(annot)


class OpenneuroDs001785Kernel:
    """Dataset kernel for openneuro_ds001785."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get('file_path', row.get('path', ''))
        if not file_path:
            return raw
        
        # Extract subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants.tsv for subject info
        participants_info = {}
        participants_path = _find_participants_tsv(file_path)
        if participants_path and subject_id:
            participants_info = _read_participants_tsv(participants_path, subject_id)
        
        # Read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = pd.DataFrame()
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Add annotations from events.tsv (pass through literal labels, no remapping)
        # Use event_value column to preserve numeric event IDs required by downstream tasks
        if not events_df.empty:
            _add_annotations_from_events_tsv(raw, events_df)
        
        # Build eegunity_description with required fields from participants.tsv
        eegunity_description = {
            "age": participants_info.get('age', 'unknown'),
            "sex": participants_info.get('sex', 'unknown'),
            "amplifier": _DEVICE_INFO.get('amplifier', 'unknown'),
            "cap": _DEVICE_INFO.get('cap', 'unknown'),
            "handedness": participants_info.get('handedness', participants_info.get('hand', 'unknown')),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = str(raw.info.get("description", "")) if raw.info.get("description") else ""
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Create derived misc channels from events.tsv columns
        # confidence, response_time, response_time2, stimamp, stimon
        events_value_map = {
            'confidence': 'confidence',
            'response_time': 'response_time',
            'response_time2': 'response_time2',
            'stimamp': 'stim_amplitude',  # or 'stimulus_amplitude'
            'stimon': 'stimulus_onset',   # or 'stim_onset'
        }
        
        # Try alternative column names
        alt_names = {
            'confidence': ['confidence', 'conf', 'Confidence'],
            'response_time': ['response_time', 'rt', 'RT', 'responseTime', 'response time'],
            'response_time2': ['response_time2', 'rt2', 'RT2', 'responseTime2'],
            'stimamp': ['stimamp', 'stim_amplitude', 'stimulus_amplitude', 'amplitude', 'stimAmp'],
            'stimon': ['stimon', 'stim_onset', 'stimulus_onset', 'stimOn'],
        }
        
        for channel_name, possible_cols in alt_names.items():
            for col in possible_cols:
                if col in events_df.columns:
                    _create_derived_misc_channel(raw, channel_name, events_df, col)
                    break
            else:
                # Column not found, create zero-filled channel
                _create_constant_misc_channel(raw, channel_name, 0.0)
        
        # Rename channels according to standard montage
        raw.rename_channels(lambda x: _CHANNEL_RENAME_MAP.get(x, x))
        
        # Set standard 10-20 montage if not already set
        if raw.get_montage() is None:
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, match_case=False, on_missing='ignore')
            except Exception:
                pass
        
        return raw


KERNEL = OpenneuroDs001785Kernel()