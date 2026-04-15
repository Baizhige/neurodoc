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
                "handedness": str(row.iloc[0].get("handedness", "unknown")).lower(),
            }
    
    # Default values
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _extract_events_from_bids(
    file_path: str,
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Extract events from BIDS events.tsv or raw annotations.
    
    Source: OpenNeuro BIDS structure
    Annotator: LLM, 2026-04-08
    """
    # Try to find events.tsv sidecar
    base_path = Path(file_path)
    eeg_dir = base_path.parent
    
    # Look for events.tsv in the same directory or parent
    for parent in [eeg_dir, eeg_dir.parent]:
        events_tsv = list(parent.glob("*_events.tsv"))
        if events_tsv:
            events_df = pd.read_csv(events_tsv[0], sep="\t")
            
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                onset = events_df["onset"].values
                duration = events_df.get("duration", pd.Series([0.0] * len(onset))).values
                description = events_df["trial_type"].astype(str).values
                
                # Map to integer codes
                descriptions_mapped = []
                for desc in description:
                    desc_lower = str(desc).lower().strip()
                    if desc_lower in _EVENT_LABEL_MAP:
                        descriptions_mapped.append(_EVENT_LABEL_MAP[desc_lower])
                    elif desc_lower == "stimulus" or desc_lower == "response":
                        descriptions_mapped.append(0)
                    else:
                        descriptions_mapped.append(0)
                
                return mne.Annotations(
                    onset=onset,
                    duration=duration,
                    description=descriptions_mapped,
                    ch_names=None,
                )
    
    # Fallback to raw annotations if no events.tsv found
    if len(raw.annotations) > 0:
        return raw.annotations
    
    # Return empty annotations
    return mne.Annotations(onset=[], duration=[], description=[], ch_names=None)


def _apply_montage_if_needed(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard montage if channels match 10-20 system.
    
    Source: MNE-Python standard montage documentation
    Annotator: LLM, 2026-04-08
    """
    # Get current channel names
    ch_names = raw.ch_names
    
    # Check if channels look like standard names
    standard_pattern = re.compile(r"^(Fp[12]?|Fpz|F[1-9]|Fz|F[78]|"
                                   r"FC[1-6]|FCz|FT[78]|C[1-6]|Cz|"
                                   r"T[78]|TP[78]|CP[1-6]|CPz|"
                                   r"P[1-9]|Pz|P[78]|"
                                   r"PO[1-9]|POz|PO10?|O[12]|Oz)$", re.IGNORECASE)
    
    standard_count = sum(1 for ch in ch_names if standard_pattern.match(ch))
    
    # If more than half the channels match standard pattern, try montage
    if standard_count >= len(ch_names) * 0.5:
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Keep original if montage fails
    
    return raw


# ============================================================================
# EEGUNITY KERNEL
# ============================================================================

class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro ds006768 dataset.
    
    This kernel handles Multiple Object Monitoring (MOM) EEG data,
    standardizing channel names, applying montages, and extracting events.
    
    Annotator: LLM, 2026-04-08
    """
    
    def __init__(self):
        """Initialize the EEGUnity kernel."""
        self.dataset_id = _DATASET_ID
        self.version = "1.0.0"
        
        # EEGUnity description metadata
        self.eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "amplifier": _DEFAULT_AMPLIFIER,
            "cap": _DEFAULT_CAP,
            "dataset_id": _DATASET_ID,
            "dataset_version": self.version,
        }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel processing to raw EEG data.
        
        Parameters
        ----------
        udataset : object
            Universal dataset object containing metadata
        raw : mne.io.BaseRaw
            Raw EEG data to process
        row : dict
            Row from dataset containing file paths and metadata
            
        Returns
        -------
        mne.io.BaseRaw
            Processed raw EEG data
        """
        # Extract file path from row
        file_path = row.get("file_path", "") if row else ""
        
        # Update subject info from participants.tsv if available
        dataset_root = row.get("dataset_root", "") if row else ""
        subject_info = _get_subject_info(file_path, dataset_root)
        self.eegunity_description.update(subject_info)
        
        # Step 1: Rename channels to standard names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Step 2: Apply montage if appropriate
        raw = _apply_montage_if_needed(raw)
        
        # Step 3: Extract and set events
        events = _extract_events_from_bids(file_path, raw)
        if len(events.onset) > 0:
            raw.set_annotations(events)
        
        # Step 4: Set channel types for auxiliary channels
        for ch in raw.ch_names:
            ch_lower = ch.lower()
            if "eog" in ch_lower or "veog" in ch_lower or "heog" in ch_lower:
                try:
                    raw.set_channel_types({ch: "eog"})
                except Exception:
                    pass
            elif "emg" in ch_lower:
                try:
                    raw.set_channel_types({ch: "emg"})
                except Exception:
                    pass
            elif "ecg" in ch_lower or "ekg" in ch_lower:
                try:
                    raw.set_channel_types({ch: "ecg"})
                except Exception:
                    pass
        
        # Step 5: Pick only EEG channels (remove auxiliaries for cleaner data)
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) > 0:
            # Keep at least some EEG channels
            raw = raw.pick(picks=eeg_picks)
        
        return raw
    
    def get_description(self) -> Dict[str, str]:
        """Get EEGUnity description metadata.
        
        Returns
        -------
        dict
            Description metadata including age, sex, handedness, etc.
        """
        return self.eegunity_description.copy()
    
    def get_dataset_id(self) -> str:
        """Get the dataset identifier.
        
        Returns
        -------
        str
            Dataset identifier string
        """
        return self.dataset_id


# ============================================================================
# KERNEL INSTANCE
# ============================================================================

KERNEL = EEGUnityKernel()