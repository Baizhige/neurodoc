"""OpenNeuro ds006768 (Multiple Object Monitoring EEG) stage1 kernel for EEGUnity.

This kernel handles the Multiple Object Monitoring task dataset from OpenNeuro.
The dataset contains 30 subjects performing a visual tracking task with
target and distractor object events.

Source: https://openneuro.org/datasets/ds006768
        DOI: https://doi.org/10.1101/2025.07.10.663816
        DOI: https://doi.org/10.1371/journal.pone.0022660 (MOM paradigm reference)
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# CONSTANTS
# ============================================================================

_DATASET_ID = "openneuro_ds006768"

# Standard 64-channel layout (10-20 system) plus possibleEOG/VEOG channels
# Source: OpenNeuro ds006768 dataset description and BrainAmp64 channel layout
# Annotator: LLM, 2026-04-08
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]

_EXTENDED_64_CHANNELS = [
    "Fp1", "AF3", "AF4", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
    "TP9", "TP7", "CP5", "CP1", "CP2", "CP6", "TP8", "TP10",
    "P7", "P3", "Pz", "P4", "P8", "PO9", "PO7", "PO3", "POz",
    "PO4", "PO8", "PO10", "O1", "Oz", "O2",
]

# Typical auxiliary channels for BrainAmp systems
_AUXILIARY_CHANNELS = ["EOG-left", "EOG-right", "EOG-central", "VEOG", "HEOG"]

# Default device metadata based on BrainAmp MR plus (common in research)
# Source: Dataset README and reference paper methodology section
# Annotator: LLM, 2026-04-08
_DEFAULT_AMPLIFIER = "BrainAmp"
_DEFAULT_CAP = "Ag/AgCl"

# Event label mapping for raw meta
# Source: analysis.md Event Structure table
_EVENT_LABEL_MAP = {
    "event": 0,
    "target": 1,
    "distractor": 2,
}

# ============================================================================
# SUBJECT DICTIONARY
# ============================================================================

# Source: participants.tsv from OpenNeuro BIDS dataset (if available)
# Fields: participant_id, age, sex, handedness
# Annotator: LLM, 2026-04-08 (needs human verification)
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _parse_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from file path.
    
    OpenNeuro BIDS format: sub-<subject_id>/eeg/<file>
    """
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map for standard 10-20 naming.
    
    Many EEG systems use numbered channels (e.g., EEG001-064) or
    BrainVision format (e.g., C3, Cz, etc.). This function attempts
    to map existing channels to standard names.
    
    Source: MNE-Python standard montage documentation
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Standard names that take priority (no duplicates allowed)
    # Order matters: more specific names first (e.g., FT7 before T7)
    standard_priority = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "FC5", "FC3", "FCz", "FC4", "FC6",
        "FT7", "FT8",
        "C5", "C3", "Cz", "C4", "C6",
        "TP7", "TP8",
        "CP5", "CP3", "CPz", "CP4", "CP6",
        "P7", "P3", "Pz", "P4", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "T7", "T8",
    ]
    
    # Common alias patterns for standard channels
    # Maps standard name -> list of aliases that should map to it
    alias_patterns = {
        "Fp1": ["Fp1", "Fp 1", "fp1"],
        "Fpz": ["Fpz", "Fpz", "fpz"],
        "Fp2": ["Fp2", "Fp 2", "fp2"],
        "F3": ["F3", "F 3", "f3"],
        "F4": ["F4", "F 4", "f4"],
        "Fz": ["Fz", "Fz", "fz"],
        "F7": ["F7", "F 7", "f7"],
        "F8": ["F8", "F 8", "f8"],
        "FC3": ["FC3", "FC 3", "fc3"],
        "FC4": ["FC4", "FC 4", "fc4"],
        "FCz": ["FCz", "FCz", "fcz"],
        "FT7": ["FT7", "FT 7", "ft7"],
        "FT8": ["FT8", "FT 8", "ft8"],
        "C3": ["C3", "C 3", "c3"],
        "C4": ["C4", "C 4", "c4"],
        "Cz": ["Cz", "Cz", "cz"],
        "T7": ["T7", "T 7", "t7"],
        "T8": ["T8", "T 8", "t8"],
        "CP3": ["CP3", "CP 3", "cp3"],
        "CP4": ["CP4", "CP 4", "cp4"],
        "CPz": ["CPz", "CPz", "cpz"],
        "TP7": ["TP7", "TP 7", "tp7"],
        "TP8": ["TP8", "TP 8", "tp8"],
        "P7": ["P7", "P 7", "p7"],
        "P8": ["P8", "P 8", "p8"],
        "P3": ["P3", "P 3", "p3"],
        "P4": ["P4", "P 4", "p4"],
        "Pz": ["Pz", "Pz", "pz"],
        "PO7": ["PO7", "PO 7", "po7"],
        "PO8": ["PO8", "PO 8", "po8"],
        "PO3": ["PO3", "PO 3", "po3"],
        "PO4": ["PO4", "PO 4", "po4"],
        "POz": ["POz", "POz", "poz"],
        "O1": ["O1", "O 1", "o1"],
        "O2": ["O2", "O 2", "o2"],
        "Oz": ["Oz", "Oz", "oz"],
    }
    
    # Track which sources have been assigned to avoid duplicates
    assigned_sources: set = set()
    
    # First pass: exact matches with standard names
    for ch in existing:
        if ch in standard_priority and ch not in assigned_sources:
            assigned_sources.add(ch)
    
    # Second pass: map aliases to standard names
    for target, aliases in alias_patterns.items():
        if target in assigned_sources:
            continue  # Already handled by exact match
        for alias in aliases:
            if alias in existing and alias not in assigned_sources:
                rename_map[alias] = target
                assigned_sources.add(alias)
                break
    
    # Handle EEG001-064 numbered format (keep as-is, montage handles positions)
    eeg_pattern = re.compile(r"^EEG\s*(\d+)$|^EEG(\d+)$", re.IGNORECASE)
    for ch in existing:
        match = eeg_pattern.match(ch)
        if match:
            # Keep original names for numbered channels
            pass
    
    return rename_map


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if it exists.
    
    Returns empty DataFrame if file not found.
    """
    participants_path = Path(dataset_root) / "participants.tsv"
    if participants_path.exists():
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(
    file_path: str,
    dataset_root: str,
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or use defaults.
    
    Source: OpenNeuro participants.tsv or defaults
    Annotator: LLM, 2026-04-08
    """
    subject_id = _parse_subject_id(file_path)
    
    if subject_id and _SUBJECT_DICT:
        # Use hardcoded subject dict if available
        return _SUBJECT_DICT.get(
            subject_id,
            {
                "age": "unknown",
                "sex": "unknown",
                "handedness": "unknown",
            }
        )
    
    # Try to load from participants.tsv
    participants_df = _load_participants_tsv(dataset_root)
    if not participants_df.empty and subject_id:
        row = participants_df[
            participants_df["participant_id"] == f"sub-{subject_id}"
        ]
        if not row.empty:
            return {
                "age": str(row.iloc[0].get("age", "unknown")),
                "sex": str(row.iloc[0].get("sex", "unknown")).lower(),
                "handedness": str(row.iloc[0].get("handedness", "unknown")),
            }
    
    # Return defaults if no data found
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


# ============================================================================
# KERNEL CLASS
# ============================================================================

class EEGUnityKernel:
    """Stage 1 kernel for OpenNeuro ds006768 (Multiple Object Monitoring EEG)."""
    
    def __init__(self):
        self.dataset_id = _DATASET_ID
        self.supported_extensions = [".edf", ".bdf", ".set", ".fif"]
        self.standard_channels = _STANDARD_64_CHANNELS
        self.extended_channels = _EXTENDED_64_CHANNELS
        self.auxiliary_channels = _AUXILIARY_CHANNELS
    
    def can_load(self, file_path: str) -> bool:
        """Check if this kernel can load the given file."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def get_dataset_id(self) -> str:
        """Return the dataset identifier."""
        return self.dataset_id
    
    def get_subject_id(self, file_path: str) -> Optional[str]:
        """Extract subject ID from file path."""
        return _parse_subject_id(file_path)
    
    def load_raw(self, file_path: str, preload: bool = True) -> mne.io.BaseRaw:
        """Load raw EEG data from file.
        
        Args:
            file_path: Path to the EEG file
            preload: Whether to preload data into memory
            
        Returns:
            MNE Raw object
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == ".edf":
            raw = mne.io.read_raw_edf(file_path, preload=preload, verbose=False)
        elif ext == ".bdf":
            raw = mne.io.read_raw_bdf(file_path, preload=preload, verbose=False)
        elif ext == ".set":
            raw = mne.io.read_raw_eeglab(file_path, preload=preload, verbose=False)
        elif ext == ".fif":
            raw = mne.io.read_raw_fif(file_path, preload=preload, verbose=False)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return raw
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage 1 processing to raw EEG data.
        
        Args:
            udataset: UDataset object (contains dataset_root)
            raw: MNE Raw object to process
            row: DataFrame row with file information
            
        Returns:
            Processed MNE Raw object
        """
        file_path = row['path']
        dataset_root = udataset.dataset_root
        
        # Apply channel renaming for standard naming
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for auxiliary channels if present
        for ch in _AUXILIARY_CHANNELS:
            if ch in raw.ch_names:
                if "EOG" in ch or ch == "VEOG":
                    raw.set_channel_types({ch: "eog"}, verbose=False)
                elif ch == "HEOG":
                    raw.set_channel_types({ch: "eog"}, verbose=False)
        
        # Get subject metadata
        subject_info = _get_subject_info(file_path, dataset_root)
        
        # Set eegunity_description with all required fields
        raw.info['eegunity_description'] = {
            'age': subject_info.get('age', 'unknown'),
            'sex': subject_info.get('sex', 'unknown'),
            'handedness': subject_info.get('handedness', 'unknown'),
            'amplifier': _DEFAULT_AMPLIFIER,
            'cap': _DEFAULT_CAP,
        }
        
        # Set standard montage if channels match standard names
        try:
            # Get channels that are in the standard list
            standard_present = [ch for ch in raw.ch_names if ch in _STANDARD_64_CHANNELS]
            if len(standard_present) >= 20:  # At least 20 standard channels
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, verbose=False)
        except Exception:
            pass  # Montage setting is optional, continue if it fails
        
        # Set reference to average
        try:
            raw.set_eeg_reference('average', projection=False, verbose=False)
        except Exception:
            pass
        
        return raw


# ============================================================================
# KERNEL INSTANCE
# ============================================================================

KERNEL = EEGUnityKernel()