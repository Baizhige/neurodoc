"""PEARL-Neuro Database (openneuro_ds004796) stage1 kernel for EEGUnity.

A multimodal neuroimaging database of healthy middle-aged adults (50-63 years)
carrying Alzheimer's risk genes (APOE, PICALM). The EEG protocol includes
resting-state recordings (eyes open and closed) and two active cognitive tasks:
the Multi-Source Interference Task (MSIT) and Sternberg's memory task.

Source: https://openneuro.org/datasets/ds004796
DOI: 10.1038/s41597-024-03106-5
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# 被试者元信息硬编码（数据集级别默认值）
# =============================================================================

# Source: DOI 10.1038/s41597-024-03106-5 (PEARL-Neuro paper)
# "healthy middle-aged adults (50–63 years)" → age range string
# LLM 推断，需人类复核
_SUBJECT_AGE_RANGE: str = "50-63"

# Source: DOI 10.1038/s41597-024-03106-5
# "healthy middle-aged adults" → sex distribution unknown at dataset level
# LLM 推断，需人类复核
_SUBJECT_SEX_DEFAULT: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# 127-channel EEG system used for PEARL-Neuro data collection
# LLM 推断，需人类复核
_AMPLIFIER: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# High-density EEG cap used in PEARL-Neuro study
# LLM 推断，需人类复核
_CAP: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# Handedness information not explicitly stated in available documentation
# LLM 推断，需人类复核
_HANDEDNESS: str = "unknown"


# =============================================================================
# 通道重映射
# =============================================================================

# PEARL-Neuro uses 127-channel EEG cap based on standard_1020 system.
# The actual channel naming follows standard 10-20 nomenclature in the BIDS data.
# No renaming needed for standard channels, but we handle potential non-standard names.
# Source: Dataset documentation / paper 10.1038/s41597-024-03106-5
# Annotator: LLM, 2025-01-01
# LLM 推断，需人类复核

# Common non-standard channel name patterns that might appear in raw data
_CHANNEL_RENAME_PATTERNS: Dict[str, str] = {
    # EEG prefix patterns
    "EEG-Fp1": "Fp1",
    "EEG-Fp2": "Fp2",
    "EEG-Fpz": "Fpz",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-Fz": "Fz",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-FC5": "FC5",
    "EEG-FC3": "FC3",
    "EEG-FC1": "FC1",
    "EEG-FCz": "FCz",
    "EEG-FC2": "FC2",
    "EEG-FC4": "FC4",
    "EEG-FC6": "FC6",
    "EEG-T7": "T7",
    "EEG-C5": "C5",
    "EEG-C3": "C3",
    "EEG-C1": "C1",
    "EEG-Cz": "Cz",
    "EEG-C2": "C2",
    "EEG-C4": "C4",
    "EEG-C6": "C6",
    "EEG-T8": "T8",
    "EEG-TP7": "TP7",
    "EEG-CP5": "CP5",
    "EEG-CP3": "CP3",
    "EEG-CP1": "CP1",
    "EEG-CPz": "CPz",
    "EEG-CP2": "CP2",
    "EEG-CP4": "CP4",
    "EEG-CP6": "CP6",
    "EEG-TP8": "TP8",
    "EEG-P7": "P7",
    "EEG-P5": "P5",
    "EEG-P3": "P3",
    "EEG-P1": "P1",
    "EEG-Pz": "Pz",
    "EEG-P2": "P2",
    "EEG-P4": "P4",
    "EEG-P6": "P6",
    "EEG-P8": "P8",
    "EEG-PO7": "PO7",
    "EEG-PO5": "PO5",
    "EEG-PO3": "PO3",
    "EEG-POz": "POz",
    "EEG-PO4": "PO4",
    "EEG-PO6": "PO6",
    "EEG-PO8": "PO8",
    "EEG-O1": "O1",
    "EEG-Oz": "Oz",
    "EEG-O2": "O2",
    "EEG-AF7": "AF7",
    "EEG-AF3": "AF3",
    "EEG-AF4": "AF4",
    "EEG-AF8": "AF8",
    "EEG-F5": "F5",
    "EEG-F1": "F1",
    "EEG-F2": "F2",
    "EEG-F6": "F6",
    "EEG-FT7": "FT7",
    "EEG-FT8": "FT8",
    "EEG-TP9": "TP9",
    "EEG-TP10": "TP10",
    "EEG-P9": "P9",
    "EEG-P10": "P10",
    "EEG-PO9": "PO9",
    "EEG-PO10": "PO10",
    "EEG-I1": "I1",
    "EEG-I2": "I2",
    # EOG prefix patterns
    "EOG-HEOG_left": "HEOG_left",
    "EOG-HEOG_right": "HEOG_right",
    "EOG-VEOG_lower": "VEOG_lower",
    "EOG-VEOG_upper": "VEOG_upper",
    # Alternative EOG naming
    "EOG1": "HEOG_left",
    "EOG2": "HEOG_right",
    "EOG3": "VEOG_lower",
    "EOG4": "VEOG_upper",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_RENAME_PATTERNS:
            rename_map[ch_name] = _CHANNEL_RENAME_PATTERNS[ch_name]
    return rename_map


# =============================================================================
# 事件映射（范式前缀约定）
# =============================================================================

# The dataset contains two paradigms: MSIT and Sternberg
# Event codes overlap between paradigms (S 1-5 for MSIT, S 10-12 for Sternberg)
# We use paradigm prefix to disambiguate
# Source: task-msit_events.json and task-sternberg_events.json in dataset
# Annotator: LLM, 2025-01-01
# LLM 推断，需人类复核

_MSIT_EVENT_MAP: Dict[str, str] = {
    "S  1": "MSIT: response_button_1",
    "S  2": "MSIT: response_button_2",
    "S  3": "MSIT: response_button_3",
    "S  4": "MSIT: FS_condition",
    "S  5": "MSIT: OO_condition",
}

_STERNBERG_EVENT_MAP: Dict[str, str] = {
    "S 10": "Sternberg: encoding",
    "S 11": "Sternberg: maintenance",
    "S 12": "Sternberg: retrieval",
}

# Combined event map for raw meta
_EVENT_MAP: Dict[str, str] = {**_MSIT_EVENT_MAP, **_STERNBERG_EVENT_MAP}

# Admin codes (cross-paradigm, no prefix)
_ADMIN_CODES: Dict[str, str] = {
    "New Segment": "admin: new_segment",
    "Time 0": "admin: time_zero",
}


def _detect_paradigm(file_path: str) -> Optional[str]:
    """Detect paradigm from BIDS file path/name.
    
    Returns 'MSIT', 'Sternberg', or None.
    """
    fname_lower = os.path.basename(file_path).lower()
    if "msit" in fname_lower:
        return "MSIT"
    elif "sternberg" in fname_lower:
        return "Sternberg"
    # Check parent directory
    dir_lower = os.path.dirname(file_path).lower()
    if "msit" in dir_lower:
        return "MSIT"
    elif "sternberg" in dir_lower:
        return "Sternberg"
    return None


def _get_paradigm_event_map(paradigm: Optional[str]) -> Dict[str, str]:
    """Get event map for specific paradigm."""
    if paradigm == "MSIT":
        return _MSIT_EVENT_MAP.copy()
    elif paradigm == "Sternberg":
        return _STERNBERG_EVENT_MAP.copy()
    else:
        return _EVENT_MAP.copy()


# =============================================================================
# participants.tsv 列名
# =============================================================================

# Required info fields from kernel requirements
_REQUIRED_INFO_FIELDS: List[str] = [
    "BDI", "BMI", "CVLT_1", "CVLT_9", "EHI", "HSV_r",
    "NEO_NEU", "PICALM_rs3851179", "RPM", "age", "coffee_status",
    "dementia_history_parents", "education", "hypertension", "sex",
    "smoking_status", "total_cholesterol", "triglycerides",
]

# Source field for derived misc
_APOE_SOURCE_FIELD: str = "APOE_haplotype"


# =============================================================================
# Derived misc channel specifications
# =============================================================================

_DERIVED_MISC_CHANNELS: List[Dict[str, Any]] = [
    {
        "name": "APOE4_binary_status",
        "source_field": "APOE_haplotype",
        "derivation": "Map APOE_haplotype to binary: APOE4+ if contains e4 allele (e2/e4, e3/e4, e4/e4), else APOE4-. Create y in {0,1} where 0=APOE4-, 1=APOE4+.",
    }
]


# =============================================================================
# Helper functions
# =============================================================================

def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # Match sub-XX pattern
    match = re.search(r'sub-([a-zA-Z0-9]+)', os.path.basename(file_path))
    if match:
        return f"sub-{match.group(1)}"
    # Try from directory
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to a data file."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    # Walk up to find participants.tsv
    for _ in range(5):  # Limit search depth
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
            os.path.join(current_dir, "..", "..", "participants.tsv"),
        ]
        for candidate in candidates:
            candidate = os.path.normpath(candidate)
            if os.path.isfile(candidate):
                return candidate
        # Move up one directory
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _read_participants_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv if found."""
    tsv_path = _find_participants_tsv(file_path)
    if tsv_path and os.path.isfile(tsv_path):
        try:
            return pd.read_csv(tsv_path, sep='\t')
        except Exception:
            pass
    return None


def _get_subject_info(participants_df: pd.DataFrame, subject_id: str) -> Optional[Dict[str, Any]]:
    """Get subject row from participants dataframe."""
    if participants_df is None or 'participant_id' not in participants_df.columns:
        return None
    mask = participants_df['participant_id'] == subject_id
    if mask.any():
        row = participants_df[mask].iloc[0].to_dict()
        # Convert to str for JSON safety
        return {k: ("" if pd.isna(v) else str(v)) for k, v in row.items()}
    return None


def _compute_apoe4_binary_status(apoe_haplotype: str) -> int:
    """Compute APOE4 binary status from APOE haplotype string.
    
    Returns 1 if any e4 allele present, 0 otherwise.
    """
    hap = str(apoe_haplotype).strip().lower()
    # Common formats: "e3e4", "E3/E4", "e4/e4", etc.
    if 'e4' in hap:
        return 1
    return 0


def _add_misc_channel(raw: mne.io.BaseRaw, name: str, data: np.ndarray) -> mne.io.BaseRaw:
    """Add a misc-type channel to raw data.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw data to add channel to.
    name : str
        Channel name.
    data : np.ndarray
        Data array of shape (1, n_times).
    
    Returns
    -------
    mne.io.BaseRaw
        Raw with added channel.
    """
    # Create info for new channel
    new_info = mne.create_info([name], raw.info['sfreq'], ['misc'])
    new_raw = mne.io.RawArray(data, new_info)
    # Add to existing raw
    raw.add_channels([new_raw], force_update_info=True)
    return raw


# =============================================================================
# Kernel class
# =============================================================================

class OpenneuroDs004796Kernel:
    """Stage-1 kernel for openneuro_ds004796 (PEARL-Neuro)."""

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        file_path = str(row.get("file_path", ""))
        
        # Detect paradigm
        paradigm = _detect_paradigm(file_path)
        
        # Get subject info from participants.tsv
        subject_id = _get_subject_id_from_path(file_path)
        participants_df = _read_participants_tsv(file_path)
        subject_info = _get_subject_info(participants_df, subject_id) if subject_id else None
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": _SUBJECT_AGE_RANGE,
            "sex": _SUBJECT_SEX_DEFAULT,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": _HANDEDNESS,
        }
        
        # Override with participant-specific values if available
        if subject_info:
            if 'age' in subject_info and subject_info['age']:
                eegunity_description['age'] = subject_info['age']
            if 'sex' in subject_info and subject_info['sex']:
                eegunity_description['sex'] = subject_info['sex']
            # Add required info fields
            for field in _REQUIRED_INFO_FIELDS:
                if field in subject_info:
                    eegunity_description[field] = subject_info[field]
        
        # Set description
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity": eegunity_description,
        })
        
        # Rename channels if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known non-EEG channels
        eog_channels = [ch for ch in raw.ch_names if ch.startswith(('EOG', 'HEOG', 'VEOG'))]
        if eog_channels:
            raw.set_channel_types({ch: 'eog' for ch in eog_channels})
        
        # Handle events/annotations
        paradigm_event_map = _get_paradigm_event_map(paradigm)
        
        # Process existing annotations
        if raw.annotations:
            new_descriptions = []
            for desc in raw.annotations.description:
                # Check paradigm-specific map first, then admin codes
                mapped = paradigm_event_map.get(desc)
                if mapped is None:
                    mapped = _ADMIN_CODES.get(desc, desc)
                new_descriptions.append(mapped)
            # Create new annotations with mapped descriptions
            raw.set_annotations(mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descriptions,
                orig_time=raw.annotations.orig_time,
            ))
        
        # Add derived misc channels from participants.tsv
        n_times = raw.n_times
        sfreq = raw.info['sfreq']
        
        for spec in _DERIVED_MISC_CHANNELS:
            source_field = spec["source_field"]
            channel_name = spec["name"]
            
            # Skip if source field not available in subject info
            if subject_info is None or source_field not in subject_info:
                continue
            
            source_value = subject_info[source_field]
            if not source_value or str(source_value).strip() == "":
                continue
            
            # Compute derived value based on channel name
            if channel_name == "APOE4_binary_status":
                derived_value = _compute_apoe4_binary_status(source_value)
            else:
                # Unknown channel, skip
                continue
            
            # Create broadcasted data array
            data = np.full((1, n_times), float(derived_value), dtype=np.float64)
            
            # Add as misc channel
            raw = _add_misc_channel(raw, channel_name, data)
        
        return raw


KERNEL = OpenneuroDs004796Kernel()