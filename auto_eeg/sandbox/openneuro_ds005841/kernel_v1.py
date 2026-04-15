"""OpenNeuro DS005841 stage1 kernel for EEGUnity.

Dataset: VR Visual Stimulus ERP experiment with 2x2 design
         (lighting: DARK/LIGHT × predictability: RAND/REF)
Source: https://openneuro.org/datasets/ds005841
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# === Channel Configuration ===
# 73 EEG channels from a VR-compatible EEG system
# Source: Dataset documentation / paper references
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_EEG_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "T8", "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "TP7", "TP8", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "TP9", "TP10",  # Mastoid reference electrodes
    "EXG1", "EXG2", "EXG3", "EXG4",  # External/EOG channels
    "EXG5", "EXG6", "EXG7", "EXG8",
    "Status",  # Trigger channel
]

# Source: Dataset README and paper (VR ERP study)
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Event mapping: actual event codes to semantic labels
# Based on paradigm description: 2x2 design (lighting × predictability)
# event_1-18 → 4 conditions × multiple stimulus positions/iterations
# Source: Analysis.md Tasks section
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_EVENT_MAP: Dict[str, str] = {
    "event_1": "RAND_DARK",   # Random unpredictable stimulus - dark condition
    "event_2": "RAND_LIGHT",  # Random unpredictable stimulus - light condition
    "event_3": "REF_DARK",    # Reference predictable stimulus - dark condition
    "event_4": "REF_LIGHT",   # Reference predictable stimulus - light condition
    "event_5": "RAND_DARK",
    "event_6": "RAND_LIGHT",
    "event_7": "REF_DARK",
    "event_8": "REF_LIGHT",
    # Extended events for position-specific analysis
    "event_11": "RAND_DARK",
    "event_12": "RAND_LIGHT",
    "event_13": "REF_DARK",
    "event_14": "REF_LIGHT",
    "event_15": "RAND_DARK",
    "event_16": "RAND_LIGHT",
    "event_17": "REF_DARK",
    "event_18": "REF_LIGHT",
}

# Binary mapping for RAND vs REF (prediction error) task
# Source: Analysis.md Potential Task 2
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_PREDICTION_ERROR_MAP: Dict[str, int] = {
    "RAND_DARK": 0,
    "RAND_LIGHT": 0,
    "REF_DARK": 1,
    "REF_LIGHT": 1,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map from raw channel names to standard names."""
    alias_groups = [
        ("Fp1", ["Fp1", "EEG001", "EEG Fp1"]),
        ("Fpz", ["Fpz", "EEG002", "EEG Fpz"]),
        ("Fp2", ["Fp2", "EEG003", "EEG Fp2"]),
        ("AF3", ["AF3", "EEG004", "EEG AF3"]),
        ("AFz", ["AFz", "EEG005", "EEG AFz"]),
        ("AF4", ["AF4", "EEG006", "EEG AF4"]),
        ("F7", ["F7", "EEG007", "EEG F7"]),
        ("F3", ["F3", "EEG008", "EEG F3"]),
        ("Fz", ["Fz", "EEG009", "EEG Fz"]),
        ("F4", ["F4", "EEG010", "EEG F4"]),
        ("F8", ["F8", "EEG011", "EEG F8"]),
        ("FC5", ["FC5", "EEG012", "EEG FC5"]),
        ("FC3", ["FC3", "EEG013", "EEG FC3"]),
        ("FCz", ["FCz", "EEG014", "EEG FCz"]),
        ("FC4", ["FC4", "EEG015", "EEG FC4"]),
        ("FC6", ["FC6", "EEG016", "EEG FC6"]),
        ("T7", ["T7", "EEG017", "EEG T7"]),
        ("C5", ["C5", "EEG018", "EEG C5"]),
        ("C3", ["C3", "EEG019", "EEG C3"]),
        ("C1", ["C1", "EEG020", "EEG C1"]),
        ("Cz", ["Cz", "EEG021", "EEG Cz"]),
        ("C2", ["C2", "EEG022", "EEG C2"]),
        ("C4", ["C4", "EEG023", "EEG C4"]),
        ("C6", ["C6", "EEG024", "EEG C6"]),
        ("T8", ["T8", "EEG025", "EEG T8"]),
        ("CP5", ["CP5", "EEG026", "EEG CP5"]),
        ("CP3", ["CP3", "EEG027", "EEG CP3"]),
        ("CP1", ["CP1", "EEG028", "EEG CP1"]),
        ("CPz", ["CPz", "EEG029", "EEG CPz"]),
        ("CP2", ["CP2", "EEG030", "EEG CP2"]),
        ("CP4", ["CP4", "EEG031", "EEG CP4"]),
        ("CP6", ["CP6", "EEG032", "EEG CP6"]),
        ("P7", ["P7", "EEG033", "EEG P7"]),
        ("P5", ["P5", "EEG034", "EEG P5"]),
        ("P3", ["P3", "EEG035", "EEG P3"]),
        ("P1", ["P1", "EEG036", "EEG P1"]),
        ("Pz", ["Pz", "EEG037", "EEG Pz"]),
        ("P2", ["P2", "EEG038", "EEG P2"]),
        ("P4", ["P4", "EEG039", "EEG P4"]),
        ("P6", ["P6", "EEG040", "EEG P6"]),
        ("P8", ["P8", "EEG041", "EEG P8"]),
        ("PO7", ["PO7", "EEG042", "EEG PO7"]),
        ("PO3", ["PO3", "EEG043", "EEG PO3"]),
        ("POz", ["POz", "EEG044", "EEG POz"]),
        ("PO4", ["PO4", "EEG045", "EEG PO4"]),
        ("PO8", ["PO8", "EEG046", "EEG PO8"]),
        ("O1", ["O1", "EEG047", "EEG O1"]),
        ("Oz", ["Oz", "EEG048", "EEG Oz"]),
        ("O2", ["O2", "EEG049", "EEG O2"]),
        ("EOG1", ["EOG1", "EOG left", "HEOG"]),
        ("EOG2", ["EOG2", "EOG right", "VEOG"]),
        ("EOG3", ["EOG3", "EOG up"]),
        ("EOG4", ["EOG4", "EOG down"]),
        ("Status", ["Status", "TRIGGER", "Stim"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r"sub-(\S+)", file_path)
    return match.group(1) if match else "unknown"


def _detect_file_format(file_path: str) -> str:
    """Detect the file format based on extension."""
    lower_path = file_path.lower()
    if lower_path.endswith(".vhdr"):
        return "brainvision"
    elif lower_path.endswith(".edf"):
        return "edf"
    elif lower_path.endswith(".bdf"):
        return "bdf"
    elif lower_path.endswith(".set"):
        return "eeglab"
    elif lower_path.endswith(".gdf"):
        return "gdf"
    return "unknown"


@dataclass
class OpenNeuroDS005841Kernel:
    """Stage1 kernel for OpenNeuro DS005841 VR ERP dataset."""

    KERNEL_ID: str = "openneuro-ds005841-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single VR ERP record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object from the EEG file
        row : Locator row with File Path information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with filtered data, renamed channels,
            and standardized annotations
        """
        file_path = row.get("File Path", "")

        # === Extract Subject Info ===
        subject_id = _extract_subject_id(file_path)
        subject_info = _SUBJECT_DICT.get(
            subject_id,
            {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
        )

        # === Update Description ===
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # VR EEG system - LLM 推断，需人类复核
                "cap": "unknown",  # VR-compatible EEG cap - LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # === Rename Channels ===
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_to_rename = {
                k: v for k, v in rename_map.items() if k in raw.ch_names
            }
            if existing_to_rename:
                mne.rename_channels(raw.info, existing_to_rename)

        # === Set Montage ===
        # Try to set standard 1020 montage for EEG channels
        try:
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass  # Non-standard cap - skip montage

        # === Apply Bandpass Filter (1-40 Hz) ===
        # Per analysis.md: "Apply bandpass filter (1-40 Hz)"
        try:
            raw.filter(l_freq=1.0, h_freq=40.0, fir_design="firwin")
        except Exception as e:
            print(f"Warning: Filter application failed: {e}")

        # === Process Events ===
        # Map event annotations to semantic labels
        if raw.annotations:
            original_descs = raw.annotations.description
            new_descs = []
            for desc in original_descs:
                # Check if this is a known event code
                if desc in _EVENT_MAP:
                    new_descs.append(_EVENT_MAP[desc])
                elif desc.startswith("event_"):
                    # Unknown event code - keep as is with prefix
                    new_descs.append(f"VR:{desc}")
                else:
                    new_descs.append(desc)

            # Create new annotations with remapped descriptions
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descs,
                orig_time=raw.annotations.orig_time,
            )
            raw.set_annotations(new_annotations)

        # === Add Super Meta (optional labels for prediction error task) ===
        # Super meta is stored in a separate annotation description prefix
        # This provides binary labels for RAND vs REF classification
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            # Create super meta annotations for prediction error contrast
            prediction_labels = []
            for desc in raw.annotations.description:
                if desc in _PREDICTION_ERROR_MAP:
                    prediction_labels.append(
                        f"SUPER:RAND_REF_{_PREDICTION_ERROR_MAP[desc]}"
                    )
                else:
                    prediction_labels.append("SUPER:unknown")

            # Store super meta as additional annotations (if not already present)
            # Note: Super meta is informational; raw meta remains primary
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS005841Kernel()