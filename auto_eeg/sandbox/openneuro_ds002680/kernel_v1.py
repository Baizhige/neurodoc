"""Dataset-specific kernel for openneuro ds002680.

Go-nogo categorization and detection task.
31-channel EEG with stimulus+response events and reaction_time.
Animal categorization + target-image recognition tasks.
Source: https://openneuro.org/datasets/ds002680
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import mne

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from kernels.openneuro_specific._base import OpenNeuroBaseKernel


# Source: Dataset documentation / publications
# 14 subjects, age range reported in DOI 10.1016/j.cogbrainres.2003.11.010
# LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-01": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-02": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-03": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-04": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-05": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-06": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-07": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-08": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-09": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-10": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-11": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-12": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-13": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-14": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
}

# Standard 32-channel montage minus Cz (31 channels) - standard_1020 system
# Source: Dataset BIDS sidecar or common practice for 31-channel EEG caps
# LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    "FT7": "FT7",
    "FC3": "FC3",
    "FCz": "FCz",
    "FC4": "FC4",
    "TP7": "TP7",
    "CP3": "CP3",
    "CPz": "CPz",
    "CP4": "CP4",
    "TP8": "TP8",
    "F1": "F1",
    "F2": "F2",
    "P1": "P1",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 1020 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Try exact match first
    for source_name in existing_names:
        if source_name in _CHANNEL_RENAME_MAP and source_name != _CHANNEL_RENAME_MAP[source_name]:
            rename_map[source_name] = _CHANNEL_RENAME_MAP[source_name]
    
    # Handle numeric EEG channel names (EEG-001, etc.)
    for ch_name in existing_names:
        if ch_name.startswith("EEG ") and ch_name[4:].isdigit():
            idx = int(ch_name[4:]) - 1
            standard_names = [
                "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "C4",
                "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "O2", "Oz", "FT7",
                "FC3", "FCz", "FC4", "TP7", "CP3", "CPz", "CP4", "TP8", "F1",
                "F2", "P1", "P2"
            ]
            if idx < len(standard_names) and standard_names[idx] not in rename_map.values():
                rename_map[ch_name] = standard_names[idx]
    
    return rename_map


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 1020 montage after renaming channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass


class OpenNeuroDs002680Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for the openneuro_ds002680 dataset."""

    KERNEL_ID: str = "openneuro-ds002680-stage1"

    def __init__(self):
        super().__init__(
            KERNEL_ID="openneuro-ds002680-stage1",
            event_map={},
            continuous_cols=["response_time"],
        )

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
            
        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata.
        """
        # Get subject ID from row
        subject_id = row.get("subject_id", "unknown")
        
        # Get subject-specific info if available
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown"
        })
        
        # Channel rename BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage
        _set_montage_if_possible(raw)
        
        # Build description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDs002680Kernel()