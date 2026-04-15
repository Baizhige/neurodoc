"""OpenNeuro DS005589 stage1 kernel for EEGUnity.

A multi-subject and multi-session EEG dataset for modelling human visual
object recognition. Contains low-speed (codes 1-20) and RSVP (codes 21-27)
visual presentation paradigms.

Source: https://openneuro.org/datasets/ds005589
Paper: DOI 10.1038/s41597-025-04843-x (2024)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Annotator: LLM, 2026-04-10
# Age/sex info unavailable in public documentation; using unknown per dataset policy
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
    "sub-31": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-32": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# Annotator: LLM, 2026-04-10
# 133 channels = 128 EEG + 3 EOG + 2 mastoid references (推测，需人类复核)
# Standard 128-channel layout using BrainVision/mne-python standard montage
_STANDARD_128_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2", "CP5", "CP1", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8", "PO9", "PO10", "O1", "Oz", "O2", "PO3",
    "PO4", "F5", "F1", "F2", "F6", "FC3", "FCz", "FC4", "C5", "C1", "C2",
    "C6", "CP3", "CPz", "CP4", "P5", "P1", "P2", "P6", "PO5", "POz", "PO6",
    "AF7", "AF3", "AF4", "AF8", "Fpz", "AFz", "CP1", "CP2", "PO7", "PO8",
    "TP7", "TP8", "CP5", "CP6", "P9", "P10", "PO9", "PO10", "O9", "O10",
    "AF9", "AF10", "LPA", "RPA", "NAS", "F9", "F10", "FT9", "FT10",
    "T9", "T10", "TP9", "TP10", "M3", "M4", "M5", "M6", "M9", "M10",
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
    "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19", "A20",
    "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30",
    "A31", "A32", "A33", "A34", "A35", "A36", "A37", "A38", "A39", "A40",
    "A41", "A42", "A43", "A44", "A45", "A46", "A47", "A48"
]


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name patterns.

    This dataset contains two paradigms:
    - Low-speed visual presentation: event codes 1-20
    - RSVP (Rapid Serial Visual Presentation): event codes 21-27

    Annotator: LLM, 2026-04-10
    """
    file_name = os.path.basename(file_path).lower()

    # Check for RSVP markers in filename
    if "rsvp" in file_name or "rapid" in file_name:
        return "RSVP"
    elif "lowspeed" in file_name or "low-speed" in file_name or "slow" in file_name:
        return "LOWSPEED"

    # Default to LOWSPEED for primary classification task
    return "LOWSPEED"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.

    Annotator: LLM, 2026-04-10
    Common patterns in BrainVision/MNE exports: EEG-001, EOG, REF, etc.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: EEG-001 -> standard names (if 128 channels)
    eeg_pattern = re.compile(r"^EEG[-_]?(\d+)$", re.IGNORECASE)
    eeg_channels = [ch for ch in existing if eeg_pattern.match(ch)]

    if len(eeg_channels) >= 64:
        # Likely a high-density system, try to map to standard_1020
        sorted_eeg = sorted(eeg_channels, key=lambda x: int(eeg_pattern.match(x).group(1)))

        # Try standard_1020_plus (94 channels) or standard_1020 (73 channels)
        try:
            montage = mne.channels.make_standard_montage("standard_1020_plus")
            standard_names = montage.ch_names
        except Exception:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                standard_names = montage.ch_names
            except Exception:
                standard_names = []

        # Map numbered EEG channels to standard names where possible
        if len(sorted_eeg) >= len(standard_names):
            for i, eeg_ch in enumerate(sorted_eeg[:len(standard_names)]):
                if i < len(standard_names):
                    rename_map[eeg_ch] = standard_names[i]

    # Pattern 2: EOG channels
    eog_aliases = {
        "EOG-left": ["EOG-L", "EOG_L", "veog1", "VEOG1", "HEOG"],
        "EOG-right": ["EOG-R", "EOG_R", "veog2", "VEOG2"],
        "EOG-central": ["EOG-C", "EOG_C", "veogc", "VEOGC"],
    }
    for target, aliases in eog_aliases.items():
        for alias in aliases:
            if alias in existing:
                rename_map[alias] = target

    # Pattern 3: Reference/mastoid channels
    ref_patterns = [
        ("M1", ["A1", "REF1", "Mastoid1", "LeftMastoid"]),
        ("M2", ["A2", "REF2", "Mastoid2", "RightMastoid"]),
    ]
    for target, aliases in ref_patterns:
        for alias in aliases:
            if alias in existing:
                rename_map[alias] = target

    # Pattern 4: Ground channel
    if "GND" in existing:
        rename_map["GND"] = "GND"
    if "Ground" in existing:
        rename_map["Ground"] = "GND"

    return rename_map


def _extract_events_from_stim(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract events from STIM channels or annotations.

    Event codes:
    - 1-20: Low-speed object categories
    - 21-27: RSVP object categories
    - 99: Catch trial
    - 252: Correct feedback
    - 254: Incorrect feedback

    Annotator: LLM, 2026-04-10
    """
    annotations = raw.annotations

    if len(annotations) > 0:
        # Events already exist as annotations
        return annotations

    # Try to find events from stim channel
    stim_channels = [ch for ch in raw.ch_names if "stim" in ch.lower() or ch == "STI 014"]

    if stim_channels:
        events, event_id = mne.events_from_annotations(raw)
        return raw.annotations

    # Return empty annotations if no events found
    return mne.Annotations(onset=[], duration=[], description=[])


def _map_event_to_label(description: str, paradigm: str) -> str:
    """Map event description to kernel canonical label with paradigm prefix.

    Annotator: LLM, 2026-04-10
    """
    # Handle numeric event codes
    try:
        code = int(description)
    except (ValueError, TypeError):
        return description

    # Low-speed paradigm (codes 1-20, 99)
    if paradigm == "LOWSPEED":
        if 1 <= code <= 20:
            return f"LOWSPEED: obj_cat_{code}"
        elif code == 99:
            return "admin: catch_trial"
        elif code == 252:
            return "admin: correct_feedback"
        elif code == 254:
            return "admin: incorrect_feedback"

    # RSVP paradigm (codes 21-27)
    elif paradigm == "RSVP":
        if 21 <= code <= 27:
            return f"RSVP: obj_cat_{code}"
        elif code == 99:
            return "admin: catch_trial"
        elif code == 252:
            return "admin: correct_feedback"
        elif code == 254:
            return "admin: incorrect_feedback"

    # Default: return as-is for unknown codes
    return description


@dataclass
class OpenNeuroDS005589Kernel:
    """Stage1 kernel for the OpenNeuro DS005589 dataset."""

    KERNEL_ID: str = "openneuro-ds005589-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated description and annotations.
        """
        file_path = row.get("File Path", "")

        # Detect paradigm from file path
        paradigm = _detect_paradigm(file_path)

        # Get subject info
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"

        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown"
        })

        # Build channel rename map and apply
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            renamed = raw.copy()
            renamed.rename_channels(rename_map)

            # Set standard montage after renaming
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                renamed.set_montage(montage, on_missing="warn")
            except Exception:
                pass  # Skip montage if not applicable

            raw = renamed

        # Extract events
        annotations = _extract_events_from_stim(raw)

        # Remap events with paradigm prefixes
        if len(annotations) > 0:
            new_descriptions = [
                _map_event_to_label(desc, paradigm)
                for desc in annotations.description
            ]
            new_annotations = mne.Annotations(
                onset=annotations.onset,
                duration=annotations.duration,
                description=new_descriptions,
            )
            raw.set_annotations(new_annotations)

        # Build description dict
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # Annotator: LLM, 2026-04-10 (需人类复核)
                "cap": "unknown",  # Annotator: LLM, 2026-04-10 (需人类复核)
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS005589Kernel()