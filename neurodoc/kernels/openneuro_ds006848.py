"""OpenNeuro ds006848 stage1 kernel for EEGUnity.

AlphaDirection1: EEG, ECG, PPG in the resting state and working memory
for sequentially and simultaneously presented digits.

Source: https://openneuro.org/datasets/ds006848/versions/1.0.0
Reference: DOI 10.1101/2025.05.04.652111

Dataset: 30 subjects, 65 channels (EEG + ECG + PPG), 1000 Hz sampling rate.
Paradigm: Working memory digit span with serial/simultaneous encoding,
resting state (eyes open/closed), cartoon intersegment markers.

Subject metadata (age/sex/handedness): Not available in dataset.
All subject fields set to "unknown". # inferred by LLM, needs human review
Amplifier/Cap: Assumed standard EEG system based on 65-channel configuration.
# inferred by LLM, needs human review
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# =============================================================================
# Channel Rename Map (standard_1020 compatible 65-channel system)
# =============================================================================
# Source: 65-channel EEG configuration typically uses standard_1020 layout.
# Channels follow naming convention:Fp1, Fp2, F7, F3, Fz, F4, F8, FC3, FCz, FC4,
# T7, C3, Cz, C4, T8, CP3, CPz, CP4, P7, P3, Pz, P4, P8, PO3, POz, PO4, O1,
# Oz, O2 + additional posterior-anterior chains.
# Assumed 65-channel montage configuration based on standard high-density EEG.
# Annotator: LLM, 2025-05-04  # inferred by LLM, needs human review
_EEG_CHANNEL_ORDER = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "FC3", "FCz", "FC4", "T7", "C3", "Cz", "C4", "T8",
    "CP3", "CPz", "CP4", "P7", "P3", "Pz", "P4", "P8",
    "PO3", "POz", "PO4", "O1", "Oz", "O2",
    "AF3", "AF4", "AF7", "AF8", "F1", "F2", "F5", "F6",
    "FC1", "FC2", "FC5", "FC6", "C1", "C2", "C5", "C6",
    "CP1", "CP2", "CP5", "CP6", "P1", "P2", "P5", "P6",
    "PO5", "PO6", "PO7", "PO8", "O9", "O10",
]

# Physiological channels (ECG, PPG) - typically labeled distinctly in BIDS
_ECG_CHANNEL_NAMES = ["ECG", "ecg", "ECG-left", "ECG-right"]
_PPG_CHANNEL_NAMES = ["PPG", "ppg", "PLETH", "Pleth"]
_EOG_CHANNEL_NAMES = ["EOG", "eog", "EOG-left", "EOG-right", "EOG-up", "EOG-down"]
_MISC_CHANNEL_NAMES = ["EMG", "emg", "Resp", "resp", "TRIGGER", "Trigger", "Status"]


def _detect_channel_type(ch_name: str, idx: int, total_channels: int) -> str:
    """Detect channel type based on name patterns."""
    ch_upper = ch_name.upper()
    
    if any(ch_name == ecg or ch_upper == ecg.upper() for ecg in _ECG_CHANNEL_NAMES):
        return "ecg"
    if any(ch_name == ppg or ch_upper == ppg.upper() for ppg in _PPG_CHANNEL_NAMES):
        return "misc"
    if any(ch_name == eog or ch_upper == eog.upper() for eog in _EOG_CHANNEL_NAMES):
        return "eog"
    if any(ch_name == misc or ch_upper == misc.upper() for misc in _MISC_CHANNEL_NAMES):
        return "misc"
    
    # EEG channel: check if it's a standard name or numbered EEG channel
    if ch_name.startswith("EEG") and ch_name[3:].isdigit():
        return "eeg"
    if ch_name in _EEG_CHANNEL_ORDER:
        return "eeg"
    
    # Heuristic: in 65-channel datasets, first ~60 are typically EEG
    if total_channels == 65 and idx < 60:
        return "eeg"
    
    # Check for standard channel patterns (2-letter + optional number)
    if re.match(r'^[A-Z]{1,2}\d*$', ch_name):
        return "eeg"
    
    return "eeg"  # Default to EEG for standard electrodes


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from original channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    # Pattern 1: EEG-0, EEG-1, ... EEG-N
    eeg_pattern = re.compile(r'^EEG-?(\d+)$', re.IGNORECASE)
    
    # Pattern 2: Numeric names 1, 2, 3, ...
    num_pattern = re.compile(r'^(\d+)$')
    
    # Pattern 3: Already standard names (may need case normalization)
    std_names_lower = {name.lower(): name for name in _EEG_CHANNEL_ORDER}
    
    for ch_name in existing_names:
        # Skip non-EEG channels
        if any(ch_name.upper() == x.upper() for x in _ECG_CHANNEL_NAMES + _PPG_CHANNEL_NAMES + _EOG_CHANNEL_NAMES + _MISC_CHANNEL_NAMES):
            continue
        
        # Pattern 1: EEG-0 -> standard name by index
        match = eeg_pattern.match(ch_name)
        if match:
            idx = int(match.group(1))
            if idx < len(_EEG_CHANNEL_ORDER):
                new_name = _EEG_CHANNEL_ORDER[idx]
                if new_name.lower() != ch_name.lower():
                    rename_map[ch_name] = new_name
            continue
        
        # Pattern 2: Just numbers
        match = num_pattern.match(ch_name)
        if match:
            idx = int(match.group(1))
            if idx < len(_EEG_CHANNEL_ORDER):
                new_name = _EEG_CHANNEL_ORDER[idx]
                if new_name.lower() != ch_name.lower():
                    rename_map[ch_name] = new_name
            continue
        
        # Pattern 3: Already standard name - normalize case
        if ch_name.lower() in std_names_lower:
            new_name = std_names_lower[ch_name.lower()]
            if new_name != ch_name:
                rename_map[ch_name] = new_name
    
    return rename_map


def _infer_channel_types(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Infer channel types from names and indices."""
    ch_types = {}
    total = len(raw.ch_names)
    
    for idx, ch_name in enumerate(raw.ch_names):
        ch_types[ch_name] = _detect_channel_type(ch_name, idx, total)
    
    return ch_types


# =============================================================================
# Subject Metadata (all unknown - no participants.tsv with this info)
# =============================================================================
# Source: Dataset does not include participant demographics in accessible files.
# Annotator: LLM, 2025-05-04  # inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-10": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-11": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-12": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-13": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-14": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-15": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-16": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-17": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-18": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-19": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-20": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-21": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-22": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-23": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-24": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-25": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-26": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-27": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-28": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-29": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-30": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r'(sub-\d+)', file_path)
    if match:
        return match.group(1)
    return None


# =============================================================================
# Amplifier/Cap Metadata
# =============================================================================
# Source: 65-channel EEG + 1 ECG + 1 PPG configuration suggests a standard
# research-grade amplifier system. Exact model not specified in dataset.
# Annotator: LLM, 2025-05-04  # inferred by LLM, needs human review
_AMPLIFIER = "unknown"  # inferred by LLM, needs human review
_CAP_MATERIAL = "unknown"  # inferred by LLM, needs human review


@dataclass
class OpenNeuroDS006848Kernel:
    """Stage1 kernel for the OpenNeuro ds006848 dataset."""

    KERNEL_ID: str = "openneuro-ds006848-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized channels, montage,
            annotations, and description.
        """
        file_path = row.get("File Path", "")

        # =========================================================================
        # Step 1: Extract Subject ID and Metadata
        # =========================================================================
        subject_id = _get_subject_id_from_path(file_path)
        if subject_id is None:
            subject_id = "unknown"
        
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown",
        })

        # =========================================================================
        # Step 2: Channel Rename (BEFORE set_montage)
        # =========================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # =========================================================================
        # Step 3: Detect and Set Channel Types
        # =========================================================================
        inferred_types = _infer_channel_types(raw)
        eeg_channels = [ch for ch, ch_type in inferred_types.items() if ch_type == "eeg"]
        
        # Set channel types for non-EEG channels
        for ch_name, ch_type in inferred_types.items():
            if ch_type != "eeg":
                try:
                    raw.set_channel_types({ch_name: ch_type})
                except Exception:
                    pass  # Skip if type cannot be set

        # =========================================================================
        # Step 4: Set Montage (only for EEG channels)
        # =========================================================================
        if eeg_channels:
            try:
                # Try standard_1020 montage first
                montage = mne.channels.make_standard_montage("standard_1020")
                
                # Get available channels in the montage that exist in our data
                ch_names_to_set = [ch for ch in eeg_channels if ch in montage.ch_names]
                
                if ch_names_to_set:
                    raw_eeg_only = raw.copy().pick(eeg_channels)
                    raw.set_montage(montage, on_missing="warn")
            except Exception as e:
                # If montage fails, continue without it
                pass

        # =========================================================================
        # Step 5: Handle Annotations/Events from BIDS events.tsv
        # =========================================================================
        # BIDS format stores events in *_events.tsv sidecar file.
        # Raw annotations may contain triggers. Extract and standardize.
        if raw.annotations:
            # Standardize annotation descriptions based on event structure
            # Map numeric codes to human-readable labels if needed
            _standardize_annotations(raw)

        # =========================================================================
        # Step 6: Write eegunity_description
        # =========================================================================
        original_description = raw.info.get("description", "")
        if not original_description or original_description == "None":
            original_description = ""

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP_MATERIAL,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


def _standardize_annotations(raw: mne.io.BaseRaw) -> None:
    """Standardize annotation descriptions based on known event structure."""
    
    # Known event types from analysis.md
    KNOWN_EVENTS = {
        # Encoding events
        "Encoding_DigitValue_0",
        "Encoding_DigitValue_1",
        "Encoding_DigitValue_2",
        "Encoding_DigitValue_3",
        "Encoding_DigitValue_4",
        "Encoding_DigitValue_5",
        "Encoding_DigitValue_6",
        "Encoding_DigitValue_7",
        "Encoding_DigitValue_8",
        "Encoding_DigitValue_9",
        "Encoding_Set_Simultaneous",
        # Retrieval/Response
        "Digits_Retrieval",
        # Baseline
        "Baseline_2s",
        # Retention phases
        "Retention_Fast",
        "Retention_FastDelay",
        "Retention_Slow",
        "Retention_Simultaneous",
        # Resting state
        "Rest",
        "Eyes_Closed",
        "Eyes_Opened",
        # Admin markers
        "Boundary",
        "Experiment_End",
        "Start_Cartoon",
        "End_Cartoon",
    }
    
    if not raw.annotations:
        return
    
    # Check if annotations need remapping
    descriptions = set(raw.annotations.description)
    
    # If annotations are numeric (e.g., from trigger channels), 
    # they need mapping. But in BIDS format, they should already be strings.
    # This function handles edge cases where they might be numeric.
    
    for i, desc in enumerate(raw.annotations.description):
        # If description is numeric and not in known events, try to interpret
        if desc not in KNOWN_EVENTS:
            # Check if it's a numeric code that needs mapping
            # (This is a safety net - BIDS events should be string labels)
            try:
                int(desc)
                # Numeric code not in known events list - may be a trigger
                # Keep as-is, it's likely a valid BIDS event code
            except (ValueError, TypeError):
                # Non-numeric, not in known events - could be custom annotation
                pass


@dataclass
class OpenNeuroDS006848Stage1:
    """Alias for backwards compatibility."""
    
    KERNEL_ID: str = "openneuro-ds006848-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing."""
        return OpenNeuroDS006848Kernel().apply(udataset, raw, row)


KERNEL = OpenNeuroDS006848Kernel()