"""OpenNeuro ds005385 stage1 kernel for EEGUnity.

Dataset: Resting-State EEG Before and After Cognitive Activity Across the Adult Lifespan (5-Year Follow-Up)
Source: https://openneuro.org/datasets/ds005385
DOI: 10.1038/s41597-024-03797-w

68-channel BrainVision format resting-state EEG (64 EEG + 4 auxiliary), 1000 Hz.
S-codes encode session/condition structure (eyes open/closed, pre/post tasks).

Metadata status:
- age: NOT in dataset; must be derived from external source or marked unknown
- sex: NOT in dataset; marked unknown
- amplifier: NOT in dataset; marked unknown
- cap: standard_1020 64-channel (inferred from publication)
- handedness: NOT in dataset; marked unknown

Event structure:
- S 4-S 7: Session markers
- S 11, S 12, S 14, S 15: Eyes-closed condition markers
- S 13, S 16, S 17, S 18, S 19: Eyes-open condition markers
- S196-S207: Session/condition index codes
- boundary: BrainVision segment boundary (admin code, exclude)

Annotator: LLM, 2026-05-28
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Kernel Metadata
# ============================================================================

KERNEL_ID = "openneuro_ds005385"

eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "unknown",
    "cap": "standard_1020",
    "handedness": "unknown",
}


# ============================================================================
# Channel Configuration
# ============================================================================

_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO5", "PO1", "PO2", "PO6",
    "F9", "F10",
    "FT9", "FT10",
    "TP9", "TP10",
    "A1", "A2",
    "M1", "M2",
    "T9", "T10",
]

_SOURCE_CHANNEL_ALIASES: Dict[str, List[str]] = {
    "Fp1": ["Fp1", "EEG Fp1"],
    "Fpz": ["Fpz", "EEG Fpz"],
    "Fp2": ["Fp2", "EEG Fp2"],
    "F7": ["F7", "EEG F7"],
    "F3": ["F3", "EEG F3"],
    "Fz": ["Fz", "EEG Fz"],
    "F4": ["F4", "EEG F4"],
    "F8": ["F8", "EEG F8"],
    "T7": ["T7", "T3", "EEG T7", "EEG T3"],
    "C3": ["C3", "EEG C3"],
    "Cz": ["Cz", "EEG Cz"],
    "C4": ["C4", "EEG C4"],
    "T8": ["T8", "T4", "EEG T8", "EEG T4"],
    "P7": ["P7", "T5", "EEG P7", "EEG T5"],
    "P3": ["P3", "EEG P3"],
    "Pz": ["Pz", "EEG Pz"],
    "P4": ["P4", "EEG P4"],
    "P8": ["P8", "T6", "EEG P8", "EEG T6"],
    "PO7": ["PO7", "PO3", "EEG PO7"],
    "PO3": ["PO3", "EEG PO3"],
    "POz": ["POz", "EEG POz"],
    "PO4": ["PO4", "EEG PO4"],
    "PO8": ["PO8", "EEG PO8"],
    "O1": ["O1", "EEG O1"],
    "Oz": ["Oz", "EEG Oz"],
    "O2": ["O2", "EEG O2"],
    "F5": ["F5", "EEG F5"],
    "F1": ["F1", "EEG F1"],
    "F2": ["F2", "EEG F2"],
    "F6": ["F6", "EEG F6"],
    "FC5": ["FC5", "EEG FC5"],
    "FC1": ["FC1", "EEG FC1"],
    "FC2": ["FC2", "EEG FC2"],
    "FC6": ["FC6", "EEG FC6"],
    "C5": ["C5", "EEG C5"],
    "C1": ["C1", "EEG C1"],
    "C2": ["C2", "EEG C2"],
    "C6": ["C6", "EEG C6"],
    "CP5": ["CP5", "EEG CP5"],
    "CP1": ["CP1", "EEG CP1"],
    "CP2": ["CP2", "EEG CP2"],
    "CP6": ["CP6", "EEG CP6"],
    "P5": ["P5", "EEG P5"],
    "P1": ["P1", "EEG P1"],
    "P2": ["P2", "EEG P2"],
    "P6": ["P6", "EEG P6"],
    "PO5": ["PO5", "EEG PO5"],
    "PO1": ["PO1", "EEG PO1"],
    "PO2": ["PO2", "EEG PO2"],
    "PO6": ["PO6", "EEG PO6"],
    "F9": ["F9", "EEG F9"],
    "F10": ["F10", "EEG F10"],
    "FT9": ["FT9", "EEG FT9"],
    "FT10": ["FT10", "EEG FT10"],
    "TP9": ["TP9", "EEG TP9"],
    "TP10": ["TP10", "EEG TP10"],
    "A1": ["A1", "EEG A1"],
    "A2": ["A2", "EEG A2"],
    "M1": ["M1", "EEG M1", "Mastoid Left"],
    "M2": ["M2", "EEG M2", "Mastoid Right"],
    "T9": ["T9", "EEG T9"],
    "T10": ["T10", "EEG T10"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    used_target_names: set[str] = set()

    for target_name, aliases in _SOURCE_CHANNEL_ALIASES.items():
        if target_name in used_target_names:
            continue
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                used_target_names.add(target_name)
                break

    numeric_pattern = re.compile(r"^(\d+)$")
    for ch_name in raw.ch_names:
        if numeric_pattern.match(ch_name):
            pass

    return rename_map


# ============================================================================
# Event Mapping
# ============================================================================

_SCODE_EVENT_MAP: Dict[str, str] = {
    "S 4": "session_marker",
    "S 5": "session_marker",
    "S 6": "session_marker",
    "S 7": "session_marker",
    "S 11": "eyes_closed",
    "S 12": "eyes_closed",
    "S 14": "eyes_closed",
    "S 15": "eyes_closed",
    "S 13": "eyes_open",
    "S 16": "eyes_open",
    "S 17": "eyes_open",
    "S 18": "eyes_open",
    "S 19": "eyes_open",
    "S196": "condition_index",
    "S197": "condition_index",
    "S198": "condition_index",
    "S199": "condition_index",
    "S200": "condition_index",
    "S201": "condition_index",
    "S202": "condition_index",
    "S203": "condition_index",
    "S204": "condition_index",
    "S205": "condition_index",
    "S206": "condition_index",
    "S207": "condition_index",
}

_ADMIN_CODES = {"boundary", "S 91", "S 92", "S 99"}


def _map_scode_to_label(scode: str) -> str:
    """Map BrainVision S-code to human-readable label."""
    return _SCODE_EVENT_MAP.get(scode, scode)


def _is_admin_event(description: str) -> bool:
    """Check if event is an admin code to exclude."""
    desc_clean = description.strip()
    if desc_clean in _ADMIN_CODES:
        return True
    if desc_clean.startswith("boundary"):
        return True
    return False


# ============================================================================
# Age Binning for Super Meta
# ============================================================================

_AGE_BINS = [
    ("20", "29"),
    ("30", "39"),
    ("40", "49"),
    ("50", "59"),
    ("60", "70"),
]


def _bin_age(age_str: str) -> Optional[str]:
    """Bin age string into age group category."""
    try:
        age = int(age_str)
    except (ValueError, TypeError):
        return None
    for low, high in _AGE_BINS:
        if low <= str(age) <= high:
            return f"age_{low}_{high}"
    return None


# ============================================================================
# EEGUnity Kernel Class
# ============================================================================

class EEGUnityKernel:
    """OpenNeuro ds005385 stage1 kernel for EEGUnity."""

    KERNEL_ID = KERNEL_ID

    def __init__(self):
        self.kernel_id = KERNEL_ID
        self.description = eegunity_description

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data.
        
        Args:
            udataset: UserDataset object containing dataset info
            raw: mne.io.BaseRaw object with raw EEG data
            row: DataFrame row with subject/session metadata
            
        Returns:
            Processed mne.io.BaseRaw object
        """
        raw = raw.copy()
        
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        annotations = raw.annotations
        if annotations is not None and len(annotations) > 0:
            new_descriptions = []
            new_onsets = []
            new_durations = []
            new_ch_names = []
            
            for desc, onset, duration in zip(
                annotations.description,
                annotations.onset,
                annotations.duration
            ):
                if not _is_admin_event(desc):
                    new_desc = _map_scode_to_label(desc)
                    new_descriptions.append(new_desc)
                    new_onsets.append(onset)
                    new_durations.append(duration)
                    new_ch_names.append(None)
            
            if new_descriptions:
                raw.set_annotations(
                    mne.Annotations(
                        onset=new_onsets,
                        duration=new_durations,
                        description=new_descriptions,
                        ch_names=new_ch_names,
                    )
                )
        
        return raw


KERNEL = EEGUnityKernel()