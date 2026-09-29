"""OpenNeuro DS004475 stage1 kernel for EEGUnity.

Mobile EEG split-belt walking study. High-density EEG (260 channels including
motion capture markers) recorded during split-belt treadmill walking.
30 participants, 512 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004475
Paradigm: split-belt treadmill walking, gait adaptation study
Reference: https://doi.org/10.1113/jp284505
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Set

import mne
import numpy as np


# =============================================================================
# Channel Classification
# =============================================================================
# The dataset contains 260 channels. Standard EEG caps typically use 64-128 channels.
# Motion capture markers are non-EEG channels that must be excluded.
# This list represents EEG, EOG, reference, and ground channels identified by
# standard naming patterns.
# Source: Pattern-based classification from standard_1020 naming conventions
# Annotator: LLM, 2026-04-10, # inferred by LLM, needs human review
_EEG_COMPATIBLE_PATTERNS: List[re.Pattern] = [
    re.compile(r"^(?:EEG|EOG|ECG|EMG)\s*[-_]?\d*$", re.IGNORECASE),
    re.compile(r"^(?:F|C|P|O|T)\d*[a-z]?$", re.IGNORECASE),
    re.compile(r"^(?:Fp|AF|F|FC|C|CP|P|PO|O|I)\d*$", re.IGNORECASE),
    re.compile(r"^(?:F|C|P|O)\s*\d+\s*[lrLR]?$"),
    re.compile(r"^(?:T[789]|[FT]\d+)", re.IGNORECASE),
    re.compile(r"^(?:Cz|Pz|Fz|Oz|Fp\d)", re.IGNORECASE),
    re.compile(r"^(?:A[12]|M[12]|[XYZ]\d+|[lr]ear)", re.IGNORECASE),
    re.compile(r"^(?:Ref|Gnd|Ground)", re.IGNORECASE),
    re.compile(r"^(?:EKG|EMG|GSR)", re.IGNORECASE),
    re.compile(r"^(?:CB\d+|C[123])", re.IGNORECASE),
    re.compile(r"^(?:EX\d+|MX\d+)", re.IGNORECASE),
    re.compile(r"^(?:Cz)", re.IGNORECASE),
]

# Explicitly known EEG channel names from standard 10-20 system
_STANDARD_EEG_CHANNELS: Set[str] = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "FC5", "FC1", "FC2", "FC6",
    "CP5", "CP1", "CP2", "CP6",
    "FT7", "FT8", "TP7", "TP8",
    "AF3", "AF4", "AF7", "AF8",
    "PO3", "PO4", "PO7", "PO8",
    "F1", "F2", "F5", "F6",
    "C1", "C2", "C5", "C6",
    "P1", "P2", "P5", "P6",
    "FC3", "FC4", "CP3", "CP4",
}


def _is_eeg_compatible_channel(ch_name: str) -> bool:
    """Check if channel name is compatible with EEG standard naming."""
    ch_clean = ch_name.strip()
    
    # Check exact standard names first
    if ch_clean in _STANDARD_EEG_CHANNELS:
        return True
    
    # Check against patterns
    for pattern in _EEG_COMPATIBLE_PATTERNS:
        if pattern.match(ch_clean):
            return True
    
    # Additional checks for common EEG naming variants
    if ch_clean.startswith("EEG ") or ch_clean.startswith("EEG-"):
        return True
    
    return False


def _get_eeg_channel_indices(raw: mne.io.BaseRaw) -> List[int]:
    """Get indices of channels that are EEG-compatible."""
    all_chs = raw.ch_names
    all_types = raw.get_channel_types()
    
    eeg_indices = []
    for idx, (ch_name, ch_type) in enumerate(zip(all_chs, all_types)):
        # MNE-correctly typed channels
        if ch_type in ("eeg", "eog", "ecg", "emg", "ref_meg"):
            eeg_indices.append(idx)
            continue
        
        # Pattern-based classification for unknown types
        if _is_eeg_compatible_channel(ch_name):
            eeg_indices.append(idx)
    
    return eeg_indices


def _filter_to_eeg(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Filter recording to EEG-compatible channels only."""
    eeg_idx = _get_eeg_channel_indices(raw)
    
    if len(eeg_idx) == len(raw.ch_names):
        # All channels are EEG-compatible
        return raw
    
    # Pick only EEG channels
    raw_eeg = raw.copy().pick(eeg_idx)
    return raw_eeg


# =============================================================================
# Event Mapping
# =============================================================================
# Raw annotations may contain various markers. Map to canonical gait event labels.
# Admin markers (boundary, 9633791) are excluded from processing.
# Source: Dataset analysis.md event structure table
# Annotator: Human, 2026-04-10
_GAIT_EVENT_MAP: Dict[str, str] = {
    "LHS": "LHS",
    "RHS": "RHS",
    "LTO": "LTO",
    "RTO": "RTO",
    "left_heel_strike": "LHS",
    "right_heel_strike": "RHS",
    "left_toe_off": "LTO",
    "right_toe_off": "RTO",
}

_BLOCK_EVENTS: Set[str] = {
    "SB1", "SB2", "B1", "B2", "B3", "P1", "P2",
    "End SB1", "End SB2", "End B1", "End B2", "End B3", "End P1", "End P2",
    "TRIG", "BUTTON",
}

_ADMIN_EVENTS: Set[str] = {
    "boundary", "9633791", "admin",
}


def _process_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Clean and standardize annotations for downstream use."""
    annotations = raw.annotations
    
    if annotations is None or len(annotations) == 0:
        return raw
    
    new_descriptions = []
    new_onsets = []
    new_durations = []
    
    for onset, duration, desc in zip(
        annotations.onset, annotations.duration, annotations.description
    ):
        desc_str = str(desc).strip()
        
        # Skip admin markers
        if desc_str in _ADMIN_EVENTS:
            continue
        
        # Map to canonical gait event or keep block event label
        if desc_str in _GAIT_EVENT_MAP:
            desc_str = _GAIT_EVENT_MAP[desc_str]
        elif desc_str not in _BLOCK_EVENTS:
            # Unknown event - keep as-is but log
            pass
        
        new_descriptions.append(desc_str)
        new_onsets.append(onset)
        new_durations.append(duration)
    
    if new_descriptions:
        clean_annotations = mne.Annotations(
            onset=np.array(new_onsets),
            duration=np.array(new_durations),
            description=new_descriptions,
            orig_time=annotations.orig_time,
        )
        raw.set_annotations(clean_annotations)
    
    return raw


# =============================================================================
# Subject Metadata
# =============================================================================
# Age, sex, and handedness are not available in the dataset.
# Amplifier and cap information not documented.
# All values set to "unknown" per kernel rulebook.
# Source: Dataset analysis.md Info field
# Annotator: LLM, 2026-04-10, # inferred by LLM, needs human review
_SUBJECT_METADATA_DEFAULTS: Dict[str, Any] = {
    "age": "unknown",
    "sex": "unknown",
    "handedness": "unknown",
    "amplifier": "unknown",
    "cap": "unknown",
}


# =============================================================================
# Kernel Implementation
# =============================================================================

class OpenNeuroDS004475Kernel:
    """Stage1 kernel for OpenNeuro DS004475 split-belt walking dataset."""

    KERNEL_ID: str = "openneuro-ds004475-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw, in-memory raw object
        row : locator row with file path

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized metadata and annotations
        """
        # Get original description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""

        # Build eegunity_description
        # All values are "unknown" since dataset lacks subject metadata
        # Source: Dataset analysis.md Info table
        # Annotator: LLM, 2026-04-10, # inferred by LLM, needs human review
        eegunity_description = {
            "age": _SUBJECT_METADATA_DEFAULTS["age"],
            "sex": _SUBJECT_METADATA_DEFAULTS["sex"],
            "amplifier": _SUBJECT_METADATA_DEFAULTS["amplifier"],
            "cap": _SUBJECT_METADATA_DEFAULTS["cap"],
            "handedness": _SUBJECT_METADATA_DEFAULTS["handedness"],
        }

        # Set description JSON
        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Filter to EEG-compatible channels
        # Remove motion capture markers and other non-EEG channels
        raw = _filter_to_eeg(raw)

        # Standardize annotations
        raw = _process_annotations(raw)

        # Set montage if standard EEG channels detected
        # Skip montage if channels are non-standard (motion capture remaining)
        eeg_types = [ch for ch in raw.get_channel_types() if ch == "eeg"]
        if len(eeg_types) >= 16:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # Montage setting failed - non-standard channels may remain
                pass

        return raw


KERNEL = OpenNeuroDS004475Kernel()