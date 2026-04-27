"""OpenNeuro DS001787 stage1 kernel for EEGUnity.

EEG Meditation Study - Focused meditation with 2-min probe interruptions.
80-channel BioSemi ActiveTwo system (64 EEG + 16 misc including GSR, Plet, Resp, Temp).
24 subjects (12 expert, 12 novice meditators).

Source: https://openneuro.org/datasets/ds001787
Paradigm: Focused meditation with probe-based sustained attention assessment
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Required info fields from participants.tsv (kernel_requirements)
# ============================================================================
_REQUIRED_INFO_FIELDS = ["age", "gender", "group"]

# ============================================================================
# Required native misc channels (already in raw data, ensure type is 'misc')
# ============================================================================
_REQUIRED_NATIVE_MISC = ["GSR1", "Plet", "Resp", "Temp"]

# ============================================================================
# Required derived misc channels (kernel MUST create these)
# ============================================================================
# - probe_response_value: from events.tsv:value, step-function for response after stimulus
_REQUIRED_DERIVED_MISC = ["probe_response_value"]

# ============================================================================
# BioSemi ActiveTwo 64-channel standard naming
# ============================================================================
# Source: BioSemi 64-channel cap layout (standard_1020 extension)
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_BIOSEMI_64_CH_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
]

# ============================================================================
# Auxiliary channel names for channels 65-80 (BioSemi convention)
# ============================================================================
# Source: BioSemi documentation; dataset has 80 channels total, 64 EEG + 16 aux
# The actual names in the data may vary; we map common BioSemi aux names
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_BIOSEMI_AUX_CH_NAMES = [
    "EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8",
    "GSR1", "Erg1", "Erg2", "Resp", "Plet", "Temp",
]

# Full 80-channel name list
_FULL_BIOSEMI_80_CH_NAMES = _BIOSEMI_64_CH_NAMES + _BIOSEMI_AUX_CH_NAMES + ["Status"]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS convention: *_eeg.<ext> has sibling *_events.tsv
    base = re.sub(r'_eeg\.[^.]+$', '', file_path)
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: same directory, matching subject
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    match = re.match(r'(sub-[a-zA-Z0-9]+).*?_eeg\.', basename)
    if match:
        sub_id = match.group(1)
        for f in os.listdir(dirname):
            if f.startswith(sub_id) and f.endswith('_events.tsv'):
                return os.path.join(dirname, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "participants.csv"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_for_subject(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and extract fields for given subject."""
    result = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
    
    try:
        df = pd.read_csv(participants_path, sep='\t')
    except Exception:
        return result
    
    # Normalize subject_id format
    if not subject_id.startswith('sub-'):
        subject_id = f"sub-{subject_id}"
    
    # Find matching row
    participant_col = 'participant_id' if 'participant_id' in df.columns else 'Participant ID'
    if participant_col not in df.columns:
        # Try case-insensitive match
        for col in df.columns:
            if col.lower() in ['participant_id', 'participant id', 'subject_id', 'subject id']:
                participant_col = col
                break
    
    if participant_col not in df.columns:
        return result
    
    # Normalize participant IDs in dataframe
    df[participant_col] = df[participant_col].astype(str)
    
    # Try exact match, then without 'sub-' prefix
    mask = df[participant_col] == subject_id
    if not mask.any():
        mask = df[participant_col] == subject_id.replace('sub-', '')
    if not mask.any():
        mask = df[participant_col] == subject_id.replace('sub-', 'sub-')
    
    if mask.any():
        row = df[mask].iloc[0]
        for field in _REQUIRED_INFO_FIELDS:
            if field in row.index:
                val = row[field]
                if pd.notna(val):
                    result[field] = str(val).strip()
    
    return result


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for BioSemi channels to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    used_targets = set()
    
    # Common patterns in BioSemi data
    # Pattern 1: A1-A64 -> standard names
    # Pattern 2: EEG 001-EEG 080 -> standard names  
    # Pattern 3: Already named but non-standard
    
    for i, std_name in enumerate(_FULL_BIOSEMI_80_CH_NAMES, 1):
        # Skip if target already used
        if std_name in used_targets:
            continue
            
        # Try various naming conventions
        candidates = [
            f"A{i}",           # BioSemi A1-A80
            f"A{i:02d}",       # A01-A80
            f"EEG {i:03d}",    # EEG 001-EEG 080
            f"EEG {i}",        # EEG 1-EEG 80
            f"Ch{i}",          # Ch1-Ch80
            f"Channel {i}",    # Channel 1-80
        ]
        # For first 64, also try standard_1020 names that might be slightly off
        if i <= 64:
            candidates.extend([
                std_name.upper(),  # FP1 instead of Fp1
                std_name.lower(),  # fp1 instead of Fp1
            ])
        
        for cand in candidates:
            if cand in existing and cand not in rename_map:
                rename_map[cand] = std_name
                used_targets.add(std_name)
                break
    
    return rename_map


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard BioSemi names."""
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw = raw.rename_channels(rename_map)
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types for BioSemi channels."""
    # EEG channels: standard 10-20 names
    eeg_pattern = re.compile(r'^(Fp[12z]|AF[zr]?[378]?|F[zr]?[12345678]?|FT[78]|FC[zr]?[123456]?|C[zr]?[123456]?|T[78]|TP[78]|CP[zr]?[123456]?|P[zr]?[123456789]|P10|PO[zr]?[378]?|O[12]|Iz)$')
    
    # Misc channels from our list
    misc_names = set(_BIOSEMI_AUX_CH_NAMES)
    
    ch_types = {}
    for ch_name in raw.ch_names:
        if eeg_pattern.match(ch_name):
            ch_types[ch_name] = 'eeg'
        elif ch_name in misc_names:
            ch_types[ch_name] = 'misc'
        elif ch_name == 'Status':
            ch_types[ch_name] = 'stim'
        elif ch_name.startswith('EXG'):
            ch_types[ch_name] = 'misc'
    
    if ch_types:
        raw = raw.set_channel_types(ch_types)
    
    return raw


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t')
        return df
    except Exception:
        return None


def _create_probe_response_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create probe_response_value misc channel from events.tsv.
    
    Creates a step-function channel where:
    - At each stimulus onset (trial_type == 'stimulus'), value is set
    - Between stimulus and next event, value persists
    - Default is 0 when no stimulus active
    """
    n_times = len(raw.times)
    sfreq = raw.info['sfreq']
    probe_values = np.zeros((1, n_times))
    
    # Sort events by onset
    events_df = events_df.sort_values('onset').reset_index(drop=True)
    
    # Find stimulus events and their values
    stimulus_mask = events_df['trial_type'].str.lower() == 'stimulus'
    response_mask = events_df['trial_type'].str.lower() == 'response'
    
    # For each stimulus, set the step function from stimulus onset to next stimulus or end
    for idx, row in events_df[stimulus_mask].iterrows():
        onset_sample = int(row['onset'] * sfreq)
        
        # Find the next stimulus or response to determine duration
        # Or use a fixed window, or until next event
        next_events = events_df[events_df.index > idx]
        if len(next_events) > 0:
            next_onset = next_events.iloc[0]['onset']
            end_sample = int(next_onset * sfreq)
        else:
            end_sample = n_times
        
        # Clamp
        onset_sample = max(0, min(onset_sample, n_times))
        end_sample = max(0, min(end_sample, n_times))
        
        if onset_sample < end_sample:
            # Get value from events.tsv, default to 0
            val = 0
            if 'value' in row and pd.notna(row['value']):
                try:
                    val = float(row['value'])
                except (ValueError, TypeError):
                    val = 0
            probe_values[0, onset_sample:end_sample] = val
    
    # Create info for new channel
    ch_info = mne.create_info(
        ch_names=['probe_response_value'],
        sfreq=sfreq,
        ch_types=['misc']
    )
    
    # Create RawArray and add to raw
    raw_misc = mne.io.RawArray(probe_values, ch_info, first_samp=raw.first_samp)
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


def _load_events_as_annotations(raw: mne.io.BaseRaw, events_path: str) -> mne.io.BaseRaw:
    """Load events from events.tsv as MNE annotations.
    
    HC-5: Pass literal tsv labels through to raw.annotations, no remapping.
    """
    df = _read_events_tsv(events_path)
    if df is None or df.empty:
        return raw
    
    # Build annotations from events.tsv
    # Use 'value' column as the annotation description since it contains the
    # distinguishable trigger labels ('128', '2', '4', '8', '16', '254', etc.)
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in df.iterrows():
        onset = float(row['onset']) if pd.notna(row['onset']) else 0.0
        
        # duration: use if available, else 0.0
        if 'duration' in row and pd.notna(row['duration']):
            try:
                duration = float(row['duration'])
                if duration <= 0 or str(duration).lower() in ('n/a', 'na'):
                    duration = 0.0
            except (ValueError, TypeError):
                duration = 0.0
        else:
            duration = 0.0
        
        # Use 'value' column as description (contains numeric trigger codes)
        # Fall back to 'trial_type' if value is missing
        if 'value' in row and pd.notna(row['value']):
            desc = str(row['value'])
        elif 'trial_type' in row and pd.notna(row['trial_type']):
            desc = str(row['trial_type'])
        else:
            desc = 'unknown'
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    # Create annotations and set on raw
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=raw.annotations.orig_time if hasattr(raw, 'annotations') and raw.annotations else None
    )
    
    raw = raw.set_annotations(annotations)
    
    return raw


class OpenNeuroDS001787Kernel:
    """Stage-1 kernel for OpenNeuro ds001787 (EEG Meditation Study)."""
    
    def __init__(self):
        self.dataset_name = "ds001787"
        self.dataset_description = "EEG Meditation Study - Focused meditation with 2-min probe interruptions"
    
    def _load_raw(self, file_path: str) -> mne.io.BaseRaw:
        """Load raw EEG file based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.bdf':
            # BioSemi BDF format
            raw = mne.io.read_raw_bdf(file_path, preload=True)
        elif ext in ('.set', '.fdt'):
            # EEGLAB format
            raw = mne.io.read_raw_eeglab(file_path, preload=True)
        elif ext in ('.vhdr', '.vmrk', '.eeg'):
            # BrainVision format
            raw = mne.io.read_raw_brainvision(file_path, preload=True)
        elif ext == '.edf':
            # EDF format
            raw = mne.io.read_raw_edf(file_path, preload=True)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return raw
    
    def process(self, file_path: str) -> Tuple[mne.io.BaseRaw, str]:
        """Process a single EEG file and return (raw, eegunity_description_json)."""
        # Load raw data
        raw = self._load_raw(file_path)
        
        # Find events.tsv
        events_path = _find_events_tsv(file_path)
        
        # Load events as annotations BEFORE any processing that might need them
        if events_path and os.path.exists(events_path):
            raw = _load_events_as_annotations(raw, events_path)
            events_df = _read_events_tsv(events_path)
        else:
            events_df = None
        
        # Rename channels to standard BioSemi names
        raw = _rename_channels(raw)
        
        # Set channel types
        raw = _set_channel_types(raw)
        
        # Create derived misc channels if events available
        if events_df is not None and not events_df.empty:
            raw = _create_probe_response_misc(raw, events_df)
        
        # Extract subject info
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants info
        participants_path = _find_participants_tsv(file_path)
        subject_info = {}
        if participants_path and subject_id:
            subject_info = _read_participants_for_subject(participants_path, subject_id)
        
        # Build eegunity_description
        description = {
            "dataset": self.dataset_name,
            "dataset_description": self.dataset_description,
            "file_path": file_path,
            "subject_id": subject_id,
            "age": subject_info.get("age", "unknown"),
            "gender": subject_info.get("gender", "unknown"),
            "group": subject_info.get("group", "unknown"),
            "n_channels": len(raw.ch_names),
            "sfreq": raw.info["sfreq"],
            "duration_sec": raw.times[-1] if len(raw.times) > 0 else 0,
            "n_annotations": len(raw.annotations) if raw.annotations else 0,
            "channel_types": {k: v for k, v in raw.get_channel_types().items()},
            "required_native_misc_present": [
                ch for ch in _REQUIRED_NATIVE_MISC if ch in raw.ch_names
            ],
            "required_derived_misc_present": [
                ch for ch in _REQUIRED_DERIVED_MISC if ch in raw.ch_names
            ],
        }
        
        eegunity_description = json.dumps(description, ensure_ascii=False, default=str)
        
        return raw, eegunity_description


KERNEL = OpenNeuroDS001787Kernel()