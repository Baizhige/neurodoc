"""OpenNeuro DS004661 stage1 kernel for EEGUnity.

Dataset: ANDI - Auditory N-back Dual-task EEG
Source: https://doi.org/10.18112/openneuro.ds004661.v1.1.0

Event structure:
- Code 10: Non-target trial (dominant condition, ~29820 events)
- Code 11: N-back target match (minority condition, ~2948 events)

Binary classification with ~10:1 class imbalance.
Sampling rate: 128 Hz (limited spectral resolution).

This dataset uses BIDS format with .set files (EEGLAB). The .set files may
not carry their own event information, so we derive annotations from
sibling *_events.tsv files when needed.
"""

from __future__ import annotations

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Channel Rename Map (64-channel standard 10-20 system)
# =============================================================================
# Source: Standard 10-20 electrode placement system, 64-channel layout
# Annotator: LLM, 2026-04-08 (inferred from standard 64-channel cap naming)
# LLM 推断，需人类复核
_EEG_CHANNEL_MAP: Dict[str, list] = {
    "Fp1": ["Fp1", "EEG-Fp1"],
    "Fp2": ["Fp2", "EEG-Fp2"],
    "Fpz": ["Fpz", "EEG-Fpz"],
    "F7": ["F7", "EEG-F7"],
    "F3": ["F3", "EEG-F3"],
    "Fz": ["Fz", "EEG-Fz"],
    "F4": ["F4", "EEG-F4"],
    "F8": ["F8", "EEG-F8"],
    "T7": ["T7", "EEG-T7", "T3"],
    "C3": ["C3", "EEG-C3"],
    "Cz": ["Cz", "EEG-Cz"],
    "C4": ["C4", "EEG-C4"],
    "T8": ["T8", "EEG-T8", "T4"],
    "P7": ["P7", "EEG-P7", "T5"],
    "P3": ["P3", "EEG-P3"],
    "Pz": ["Pz", "EEG-Pz"],
    "P4": ["P4", "EEG-P4"],
    "P8": ["P8", "EEG-P8", "T6"],
    "O1": ["O1", "EEG-O1"],
    "Oz": ["Oz", "EEG-Oz"],
    "O2": ["O2", "EEG-O2"],
    "FC5": ["FC5", "EEG-FC5"],
    "FC3": ["FC3", "EEG-FC3"],
    "FC1": ["FC1", "EEG-FC1"],
    "FCz": ["FCz", "EEG-FCz"],
    "FC2": ["FC2", "EEG-FC2"],
    "FC4": ["FC4", "EEG-FC4"],
    "FC6": ["FC6", "EEG-FC6"],
    "CP5": ["CP5", "EEG-CP5"],
    "CP3": ["CP3", "EEG-CP3"],
    "CP1": ["CP1", "EEG-CP1"],
    "CPz": ["CPz", "EEG-CPz"],
    "CP2": ["CP2", "EEG-CP2"],
    "CP4": ["CP4", "EEG-CP4"],
    "CP6": ["CP6", "EEG-CP6"],
    "AF3": ["AF3", "EEG-AF3"],
    "AF4": ["AF4", "EEG-AF4"],
    "F5": ["F5", "EEG-F5"],
    "F1": ["F1", "EEG-F1"],
    "F2": ["F2", "EEG-F2"],
    "F6": ["F6", "EEG-F6"],
    "C5": ["C5", "EEG-C5"],
    "C1": ["C1", "EEG-C1"],
    "C2": ["C2", "EEG-C2"],
    "C6": ["C6", "EEG-C6"],
    "P5": ["P5", "EEG-P5"],
    "P1": ["P1", "EEG-P1"],
    "P2": ["P2", "EEG-P2"],
    "P6": ["P6", "EEG-P6"],
    "AF7": ["AF7", "EEG-AF7"],
    "AF8": ["AF8", "EEG-AF8"],
    "FT7": ["FT7", "EEG-FT7"],
    "FT8": ["FT8", "EEG-FT8"],
    "TP7": ["TP7", "EEG-TP7"],
    "TP8": ["TP8", "EEG-TP8"],
    "PO7": ["PO7", "EEG-PO7"],
    "PO8": ["PO8", "EEG-PO8"],
    "AFz": ["AFz", "EEG-AFz"],
    "POz": ["POz", "EEG-POz"],
    "FT9": ["FT9", "EEG-FT9"],
    "FT10": ["FT10", "EEG-FT10"],
    "TP9": ["TP9", "EEG-TP9"],
    "TP10": ["TP10", "EEG-TP10"],
    "PO9": ["PO9", "EEG-PO9"],
    "PO10": ["PO10", "EEG-PO10"],
    "PO3": ["PO3", "EEG-PO3"],
    "PO4": ["PO4", "EEG-PO4"],
    "Iz": ["Iz", "EEG-Iz"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in _EEG_CHANNEL_MAP.items():
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                # Avoid collision: if target already exists from another mapping, skip
                if target_name in existing_names and target_name not in rename_map.values():
                    # Target already exists as a proper name, don't overwrite
                    continue
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _get_subject_from_path(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    # BIDS pattern: sub-<label>
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return ""


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = file_path.replace('.set', '').replace('.fdt', '')
    # Try common BIDS patterns
    candidates = [
        base + '_events.tsv',
        base.replace('_eeg', '') + '_events.tsv',
    ]
    # Also check parent directory patterns
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).replace('.set', '').replace('.fdt', '')
    
    # Look for any *_events.tsv in the same directory or parent
    for check_dir in [dir_name, os.path.dirname(dir_name)]:
        if os.path.isdir(check_dir):
            for f in os.listdir(check_dir):
                if f.endswith('_events.tsv'):
                    # Check if it's for the same subject/task
                    subj = _get_subject_from_path(file_path)
                    if subj in f:
                        candidate = os.path.join(check_dir, f)
                        candidates.append(candidate)
    
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidate = os.path.join(current_dir, 'participants.tsv')
        if os.path.isfile(candidate):
            return candidate
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_tsv = _find_participants_tsv(file_path)
    info: Dict[str, str] = {}
    
    if participants_tsv is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep='\t')
        # Find row for this subject
        subj_col = None
        for col in df.columns:
            if col.lower() in ['participant_id', 'subject', 'subject_id']:
                subj_col = col
                break
        
        if subj_col is None:
            return info
        
        # Match subject ID
        row = df[df[subj_col] == subject_id]
        if row.empty:
            # Try without 'sub-' prefix
            row = df[df[subj_col] == subject_id.replace('sub-', '')]
        if row.empty:
            # Try with 'sub-' prefix
            row = df[df[subj_col] == f"sub-{subject_id.replace('sub-', '')}"]
        
        if not row.empty:
            for col in df.columns:
                if col != subj_col:
                    val = row.iloc[0][col]
                    if pd.notna(val):
                        info[col] = str(val)
                    else:
                        info[col] = "unknown"
    except Exception:
        pass
    
    return info


def _events_tsv_to_annotations(events_tsv_path: str, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    try:
        df = pd.read_csv(events_tsv_path, sep='\t')
        
        # Required columns
        if 'onset' not in df.columns:
            return None
        
        onsets = df['onset'].values
        durations = df['duration'].values if 'duration' in df.columns else np.zeros(len(onsets))
        
        # Description: prefer 'trial_type', then 'value', then 'stim_type'
        if 'trial_type' in df.columns:
            descriptions = df['trial_type'].astype(str).values
        elif 'value' in df.columns:
            descriptions = df['value'].astype(str).values
        elif 'stim_type' in df.columns:
            descriptions = df['stim_type'].astype(str).values
        else:
            # Use any column that might contain event info
            for col in df.columns:
                if col not in ['onset', 'duration', 'sample', 'channel']:
                    descriptions = df[col].astype(str).values
                    break
            else:
                descriptions = np.array(['event'] * len(onsets))
        
        # Ensure non-negative onsets
        onsets = np.maximum(onsets, 0)
        
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
            orig_time=None
        )
        return annot
    except Exception:
        return None


def _add_misc_channels(raw: mne.io.BaseRaw, participants_info: Dict[str, str]) -> mne.io.BaseRaw:
    """Add derived misc channels from participants.tsv info."""
    # No derived misc channels needed for this dataset based on requirements
    return raw


@dataclass
class OpenNeuroDS004661Kernel:
    KERNEL_ID: str = "openneuro_ds004661"
    DATASET_NAME: str = "ANDI - Auditory N-back Dual-task EEG"
    DATASET_URL: str = "https://doi.org/10.18112/openneuro.ds004661.v1.1.0"
    CITATION: str = "OpenNeuro DS004661"
    LICENSE: str = "CC0"
    SUPPORTED_FORMATS: List[str] = None
    EXPECTED_CHANNELS: int = 64
    EXPECTED_SFREQ: float = 128.0
    REQUIRED_INFO_FIELDS: List[str] = None
    DERIVED_MISC_CHANNELS: List[str] = None

    def __post_init__(self):
        if self.SUPPORTED_FORMATS is None:
            self.SUPPORTED_FORMATS = [".set"]
        if self.REQUIRED_INFO_FIELDS is None:
            self.REQUIRED_INFO_FIELDS = ["age", "sex", "handedness"]
        if self.DERIVED_MISC_CHANNELS is None:
            self.DERIVED_MISC_CHANNELS = []

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        
        # Get subject ID
        subject_id = _get_subject_from_path(file_path)
        
        # Read participants info
        participants_info = _read_participants_info(file_path, subject_id)
        
        # Build eegunity_description from required fields
        eegunity_description = {}
        for field in self.REQUIRED_INFO_FIELDS:
            if field in participants_info:
                eegunity_description[field] = participants_info[field]
            else:
                eegunity_description[field] = "unknown"
        
        # Add amplifier and cap info (dataset-specific, not in participants.tsv)
        eegunity_description["amplifier"] = "Brain Products BrainAmp"
        eegunity_description["cap"] = "64-channel standard 10-20"
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Handle events/annotations
        # Check if raw already has annotations
        if raw.annotations is None or len(raw.annotations) == 0:
            # Try to load from events.tsv
            events_tsv = _find_events_tsv(file_path)
            if events_tsv is not None:
                annot = _events_tsv_to_annotations(events_tsv, raw.info['sfreq'])
                if annot is not None:
                    raw.set_annotations(annot)
        
        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage if not already set
        if raw.get_montage() is None:
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, match_case=False, on_missing='ignore')
            except Exception:
                pass
        
        # Add derived misc channels if any
        for misc_name in self.DERIVED_MISC_CHANNELS:
            if misc_name in raw.ch_names:
                continue
            # Create constant broadcast channel from participants info or default
            if misc_name in participants_info:
                val = float(participants_info[misc_name]) if participants_info[misc_name].replace('.','',1).replace('-','').isdigit() else 0.0
            else:
                val = 0.0
            data = np.full((1, len(raw.times)), val)
            info = mne.create_info([misc_name], raw.info['sfreq'], ['misc'])
            raw_misc = mne.io.RawArray(data, info)
            raw.add_channels([raw_misc], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004661Kernel()