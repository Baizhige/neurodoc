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
    
    # Common alias patterns for standard channels
    alias_patterns = {
        # Direct standard names
        "Fp1": ["Fp1", "Fp 1", "fp1"],
        "Fp2": ["Fp2", "Fp 2", "fp2"],
        "Fpz": ["Fpz", "Fpz", "fpz"],
        "F3": ["F3", "F 3", "f3"],
        "F4": ["F4", "F 4", "f4"],
        "Fz": ["Fz", "Fz", "fz"],
        "F7": ["F7", "F 7", "f7"],
        "F8": ["F8", "F 8", "f8"],
        "FC3": ["FC3", "FC 3", "fc3"],
        "FC4": ["FC4", "FC 4", "fc4"],
        "FCz": ["FCz", "FCz", "fcz"],
        "FT7": ["FT7", "FT 7", "ft7", "T7"],
        "FT8": ["FT8", "FT 8", "ft8", "T8"],
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
    
    for target, aliases in alias_patterns.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    # Handle EEG001-064 numbered format
    eeg_pattern = re.compile(r"^EEG\s*(\d+)$|^EEG(\d+)$|^(\d+)$", re.IGNORECASE)
    for ch in existing:
        match = eeg_pattern.match(ch)
        if match:
            # Keep original names for now, montage will handle positions
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
                
                return mne.Annotations(
                    onset=onset,
                    duration=duration,
                    description=description,
                )
    
    # Fall back to raw annotations if available
    if raw.annotations:
        return raw.annotations
    
    # Return empty annotations if no events found
    return mne.Annotations(onset=[], duration=[], description=[])


def _remap_annotations_to_raw_meta(
    annotations: mne.Annotations,
) -> mne.Annotations:
    """Ensure annotation descriptions match raw meta event labels.
    
    Map common variations to canonical labels:
    - "event", "trial", "stim" -> "event"
    - "target", "Target", "TARGET" -> "target"
    - "distractor", "Distractor", "DISTRACTOR" -> "distractor"
    
    Source: analysis.md Event Structure table
    Annotator: LLM, 2026-04-08
    """
    canonical_labels = {"event", "target", "distractor"}
    
    new_descriptions = []
    for desc in annotations.description:
        desc_lower = str(desc).lower().strip()
        
        if desc_lower in ["event", "trial", "stim", "stimulus", "stimulus onset"]:
            new_descriptions.append("event")
        elif desc_lower in ["target", "target object", "target_onset"]:
            new_descriptions.append("target")
        elif desc_lower in ["distractor", "distractor object", "distractor_onset"]:
            new_descriptions.append("distractor")
        else:
            # Keep original if not in canonical set
            new_descriptions.append(str(desc))
    
    return mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
    )


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 10-20 montage if channels are recognizable.
    
    Source: MNE-Python standard_montage documentation
    Annotator: LLM, 2026-04-08
    """
    try:
        # Try to set standard 1020 montage
        # First, check if enough channels match standard names
        existing_chs = set(raw.ch_names)
        standard_chs = set(_STANDARD_64_CHANNELS)
        
        matching = existing_chs.intersection(standard_chs)
        
        if len(matching) >= 20:  # At least 20 standard channels
            # Select only the channels that are in our standard set
            chs_to_use = list(matching.intersection(standard_chs))
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Keep only channels that exist in the raw data
            chs_available = [ch for ch in montage.ch_names if ch in existing_chs]
            if chs_available:
                raw.set_montage(montage, on_missing="ignore")
        else:
            # Try using unknown names with generic 1020 positions
            # This handles cases where channels are like EEG001-064
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage setting is optional
                
    except Exception:
        # Montage setting is best-effort; don't fail the kernel
        pass


# ============================================================================
# KERNEL CLASS
# ============================================================================


class OpenNeuroDS006768Kernel:
    """Stage1 kernel for OpenNeuro ds006768 (Multiple Object Monitoring EEG).
    
    This kernel handles:
    - Channel naming standardization (before set_montage)
    - Event annotation extraction and normalization
    - Subject metadata population (eegunity_description)
    - BIDS-compatible metadata handling
    
    Source: https://openneuro.org/datasets/ds006768
            DOI: https://doi.org/10.1101/2025.07.10.663816
    """

    KERNEL_ID: str = "openneuro-ds006768-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object loaded from the EEG file.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
            
        Returns
        -------
        mne.io.BaseRaw
            The preprocessed Raw object with standardized metadata and events.
        """
        file_path = row.get("File Path", "")
        
        # =====================================================================
        # Step 1: Extract dataset root for participant info lookup
        # =====================================================================
        if hasattr(row, "get"):
            dataset_root = row.get("Dataset Root", os.path.dirname(file_path))
        else:
            dataset_root = os.path.dirname(file_path)
        
        # Try to find dataset root (parent of sub-* directories)
        path_obj = Path(file_path)
        for parent in path_obj.parents:
            if parent.name.startswith("sub-"):
                dataset_root = str(parent.parent)
                break
        
        # =====================================================================
        # Step 2: Get subject metadata
        # =====================================================================
        subject_info = _get_subject_info(file_path, dataset_root)
        
        # =====================================================================
        # Step 3: Build eegunity_description
        # =====================================================================
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DEFAULT_AMPLIFIER,  # LLM 推断，需人类复核
                "cap": _DEFAULT_CAP,  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =====================================================================
        # Step 4: Rename channels to standard names (BEFORE set_montage)
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # =====================================================================
        # Step 5: Set standard montage if possible
        # =====================================================================
        _set_montage_if_possible(raw)
        
        # =====================================================================
        # Step 6: Extract and normalize events
        # =====================================================================
        annotations = _extract_events_from_bids(file_path, raw)
        normalized_annotations = _remap_annotations_to_raw_meta(annotations)
        raw.set_annotations(normalized_annotations)
        
        # =====================================================================
        # Step 7: Update channel types if needed
        # =====================================================================
        # Identify and set EOG/VEOG channels if present but not typed
        ch_types = raw.get_channel_types()
        for ch_name, ch_type in ch_types.items():
            if ch_type == "eeg":
                # Check for common EOG channel name patterns
                ch_upper = ch_name.upper()
                if any(eog_marker in ch_upper for eog_marker in ["EOG", "VEOG", "HEOG", "EYE"]):
                    # Keep as misc if it's clearly an EOG but not typed
                    if ch_type == "eeg":
                        raw.set_channel_types({ch_name: "misc"})
        
        return raw


# ============================================================================
# KERNEL INSTANCE
# ============================================================================

KERNEL = OpenNeuroDS006768Kernel()