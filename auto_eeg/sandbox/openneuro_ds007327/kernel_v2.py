"""OpenNeuro DS007327 stage1 kernel for EEGUnity.

EEG During Sport-Related Motor Imagery and Observation Tasks.
35 subjects × 3 task types (ballpass, dribble, passing) = 105 EDF files.
88 channels (64 EEG + 24 BIP/EMG); 1000 Hz sampling.

Source: https://openneuro.org/datasets/ds007327
Paradigm: 2x2 factorial crossing motor intention (MI) with movement 
observation (MO), yielding four compound conditions (MIMI/MIMO/MOMI/MOMO)
plus single-factor conditions and baselines.

This kernel:
1. Parses BIDS-style events.tsv for raw meta labels
2. Excludes BIP/EMG channels (BIP01-BIP24) from EEG analysis
3. Sets standard_1020 montage after channel rename
4. Writes eegunity_description with subject metadata
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# Source: OpenNeuro participants.tsv (extracted during kernel development)
# Note: age/sex from participants.tsv; amplifier/cap/handedness unknown
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",
        "sex": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
        "handedness": "unknown",
    }
    for i in range(1, 36)
}

# =============================================================================
# BIP/EMG Channel Exclusion List
# Source: Dataset analysis notes (88 total channels includes 24 BIP)
# Annotator: Human, 2026-04-08
# =============================================================================
_BIP_CHANNEL_PATTERNS: List[str] = [
    f"BIP{i:02d}" for i in range(1, 25)
]

# =============================================================================
# Raw Meta Event Mapping (from analysis.md)
# Events are prefixed by task type: A=single-factor, B=compound task B, C=compound task C
# =============================================================================
_RAW_EVENT_MAP: Dict[str, str] = {
    # Task A - single-factor conditions
    "A11": "Motor observation (Task A)",
    "A22": "Motor intention (Task A)",
    "A44": "Resting baseline (Task A)",
    "A66": "Static baseline (Task A)",
    "A88": "Motor observation with intention (Task A)",
    # Task B - 2x2 compound conditions
    "B12": "MIMI (Task B)",
    "B14": "MIMO (Task B)",
    "B16": "MOMI (Task B)",
    "B18": "MOMO (Task B)",
    # Task C - 2x2 compound conditions
    "C12": "MIMI (Task C)",
    "C14": "MIMO (Task C)",
    "C16": "MOMI (Task C)",
    "C18": "MOMO (Task C)",
}

# Administrative markers to exclude
_ADMIN_EVENTS: set = {
    "A98", "A99", "B96", "B98", "B99", "C96", "C98", "C99",
    "Impedance", "boundary"
}


def _detect_task_prefix(file_path: str) -> str:
    """Detect task prefix (A/B/C) from filename.
    
    Filenames follow pattern: *_pass_*edf, *_dribble_*edf, *_ballpass_*edf
    or sub-XX_*_task-A/B/C_*run-*.edf
    """
    basename = os.path.basename(file_path).lower()
    
    # Try explicit task prefix in filename
    match = re.search(r'_task-([ABC])_', basename)
    if match:
        return match.group(1)
    
    # Infer from task keywords
    if 'ballpas' in basename or '_pass' in basename:
        return 'A'
    elif 'dribbl' in basename:
        return 'B'
    else:
        return 'A'


def _find_events_tsv(eeg_file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for an EDF file."""
    base_dir = os.path.dirname(eeg_file_path)
    eeg_basename = os.path.splitext(os.path.basename(eeg_file_path))[0]
    
    # Try BIDS structure: sub-XX/eeg/sub-XX_task-*_run-*_events.tsv
    possible_paths = [
        os.path.join(base_dir, eeg_basename + "_events.tsv"),
        os.path.join(base_dir, "..", "eeg", eeg_basename + "_events.tsv"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def _load_events_tsv(events_tsv_path: str) -> pd.DataFrame:
    """Load events from BIDS-style TSV file."""
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
        return df
    except Exception:
        return pd.DataFrame()


def _build_annotations_from_raw(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Build annotations from raw annotations or stim channel."""
    # First try existing annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        return raw.annotations
    
    # Try stim channel (last channel is often stim)
    stim_ch = None
    for ch in raw.ch_names:
        if 'stim' in ch.lower() or 'trigger' in ch.lower():
            stim_ch = ch
            break
    
    if stim_ch is None:
        stim_ch = raw.ch_names[-1]
    
    # Extract events from stim channel
    stim_data, _ = raw[stim_ch]
    threshold = np.percentile(stim_data, 95)
    stim_flat = stim_data.flatten()
    onsets = np.where(np.diff(np.concatenate([[0], stim_flat > threshold])) > 0)[0]
    
    if len(onsets) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    descriptions = [str(int(stim_flat[onsets[i]])) for i in range(len(onsets))]
    
    return mne.Annotations(
        onset=onsets / raw.info['sfreq'],
        duration=[0.0] * len(onsets),
        description=descriptions
    )


def _build_annotations_from_events_tsv(
    events_tsv_path: str, 
    raw: mne.io.BaseRaw
) -> mne.Annotations:
    """Build MNE annotations from events.tsv file."""
    df = _load_events_tsv(events_tsv_path)
    
    if df.empty or 'onset' not in df.columns:
        return _build_annotations_from_raw(raw)
    
    # Normalize onset times
    try:
        onsets = pd.to_numeric(df['onset'], errors='coerce').dropna().values
    except Exception:
        onsets = []
    
    if len(onsets) == 0:
        return _build_annotations_from_raw(raw)
    
    # Get duration (default 0 if not present)
    durations = [0.0] * len(onsets)
    if 'duration' in df.columns:
        try:
            durations = pd.to_numeric(df['duration'], errors='coerce').fillna(0).values
        except Exception:
            pass
    
    # Get trial type / label
    descriptions = []
    for col in ['trial_type', 'value', 'event', 'condition', 'stimulus']:
        if col in df.columns:
            descriptions = df[col].fillna('').astype(str).tolist()
            break
    
    if not descriptions:
        descriptions = [str(i) for i in range(len(onsets))]
    
    # Apply event mapping for standardized labels
    mapped_descriptions = []
    for desc in descriptions:
        desc_clean = desc.strip()
        if desc_clean in _RAW_EVENT_MAP:
            mapped_descriptions.append(_RAW_EVENT_MAP[desc_clean])
        elif desc_clean in _ADMIN_EVENTS:
            continue
        else:
            mapped_descriptions.append(desc_clean)
    
    # Filter out onsets corresponding to admin events
    final_onsets = []
    final_durations = []
    final_descriptions = []
    for i, desc in enumerate(descriptions):
        if desc.strip() not in _ADMIN_EVENTS:
            final_onsets.append(onsets[i])
            final_durations.append(durations[i])
            final_descriptions.append(mapped_descriptions[i])
    
    if not final_onsets:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(
        onset=np.array(final_onsets),
        duration=np.array(final_durations),
        description=final_descriptions
    )


class EEGUnityKernel:
    """Kernel for OpenNeuro DS007327 dataset processing."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply EEGUnity kernel to raw data.
        
        Parameters
        ----------
        udataset : object
            Dataset accessor with file paths and metadata
        raw : mne.io.BaseRaw
            Raw EEG data object
        row : dict
            Row from dataset listing
            
        Returns
        -------
        raw : mne.io.BaseRaw
            Processed raw data with annotations and channel selections
        """
        # Extract subject ID from row or file path
        subject_id = "sub-01"
        if 'subject' in row:
            subject_id = f"sub-{str(row['subject']).zfill(2)}"
        elif 'file_path' in row:
            match = re.search(r'sub-(\d+)', str(row['file_path']))
            if match:
                subject_id = f"sub-{match.group(1).zfill(2)}"
        
        # Find and load events.tsv
        file_path = row.get('file_path', '')
        events_tsv = None
        if file_path:
            events_tsv = _find_events_tsv(file_path)
        
        # Build annotations
        if events_tsv and os.path.exists(events_tsv):
            annotations = _build_annotations_from_events_tsv(events_tsv, raw)
        else:
            annotations = _build_annotations_from_raw(raw)
        
        raw.set_annotations(annotations)
        
        # Identify EEG channels (exclude BIP/EMG)
        eeg_channels = []
        for ch in raw.ch_names:
            is_bip = any(bip in ch for bip in _BIP_CHANNEL_PATTERNS)
            if not is_bip:
                eeg_channels.append(ch)
        
        # Pick only EEG channels
        if eeg_channels:
            raw.pick(eeg_channels)
        
        # Try to set standard_1020 montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        
        # Get subject metadata
        subject_info = _SUBJECT_DICT.get(subject_id, _SUBJECT_DICT["sub-01"])
        
        # Store eegunity_description
        raw.info['eegunity_description'] = {
            'age': subject_info['age'],
            'sex': subject_info['sex'],
            'amplifier': subject_info['amplifier'],
            'cap': subject_info['cap'],
            'handedness': subject_info['handedness'],
            'dataset': 'openneuro_ds007327',
            'subject': subject_id,
        }
        
        return raw


# Kernel instance for EEGUnity
KERNEL = EEGUnityKernel()