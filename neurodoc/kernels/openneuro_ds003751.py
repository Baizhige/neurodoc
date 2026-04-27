"""DENS (openneuro_ds003751) stage1 kernel for EEGUnity.

Dataset: Emotion with Naturalistic Stimuli
- 40 subjects, 132 channels, 250 Hz
- EEG/ECG/EMG during naturalistic video viewing
- Tasks: Binary VAD classification, 8-class VAD emotion classification

Source: https://openneuro.org/datasets/ds003751
DOI: 10.1101/2021.08.05.455187
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Dataset documentation and paper - 132-channel EEG system
# Amplifier and cap information not explicitly stated in available docs
# LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {"sex": "unknown", "age": "unknown", "handedness": "unknown"}
    for i in range(1, 41)
}

# Annotator: LLM, 2026-04-08
# Source: Paper indicates standard electrode placement system
# 132 channels suggest extended 10-10 or 10-5 system montage
# LLM 推断，需人类复核
_AMPLIFIER = "unknown"  # LLM 推断，需人类复核
_CAP = "unknown"  # LLM 推断，需人类复核

# Event ID mapping based on analysis.md
_EVENT_MAP = {
    "stm": "stimulus",
    "IBEG": "interval_begin",
    "base": "baseline",
    "bend": "baseline_end",
    "IEND": "interval_end",
    "vlnc": "valence_negative_centered",
    "arsl": "arousal_low",
    "dmns": "dominance",
    "lkng": "looking",
    "relv": "relief",
    "fmrt": "frustration",
    "cate": "category",
    "clic": "click",
    "trno": "trial_number",
    "fixL": "fixation_left",
    "quiz": "quiz",
    "qdon": "quiz_done",
    "stop": "stop",
    "puse": "pause",
    "rsrt": "restart",
    "net": "net",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path (if applicable)."""
    return ""


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard naming.

    Handles common naming variations in EEG datasets.
    For 132-channel systems, attempts to map to standard 10-10 positions.

    Annotator: LLM, 2026-04-08
    Source: Standard 10-10 and 10-5 electrode naming conventions
    LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common standard 10-20 channel aliases
    standard_aliases = [
        ("Fp1", ["Fp1", "EEG-Fp1", "fp1", "FP1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "fp2", "FP2"]),
        ("F7", ["F7", "EEG-F7", "f7", "F7"]),
        ("F3", ["F3", "EEG-F3", "f3", "F3"]),
        ("Fz", ["Fz", "EEG-Fz", "fz", "FZ"]),
        ("F4", ["F4", "EEG-F4", "f4", "F4"]),
        ("F8", ["F8", "EEG-F8", "f8", "F8"]),
        ("T7", ["T7", "EEG-T7", "t7", "T7", "T3"]),
        ("C3", ["C3", "EEG-C3", "c3", "C3"]),
        ("Cz", ["Cz", "EEG-Cz", "cz", "CZ"]),
        ("C4", ["C4", "EEG-C4", "c4", "C4"]),
        ("T8", ["T8", "EEG-T8", "t8", "T8", "T4"]),
        ("P7", ["P7", "EEG-P7", "p7", "P7", "T5"]),
        ("P3", ["P3", "EEG-P3", "p3", "P3"]),
        ("Pz", ["Pz", "EEG-Pz", "pz", "PZ"]),
        ("P4", ["P4", "EEG-P4", "p4", "P4"]),
        ("P8", ["P8", "EEG-P8", "p8", "P8", "T6"]),
        ("O1", ["O1", "EEG-O1", "o1", "O1"]),
        ("Oz", ["Oz", "EEG-Oz", "oz", "OZ"]),
        ("O2", ["O2", "EEG-O2", "o2", "O2"]),
        ("AF7", ["AF7", "EEG-AF7", "af7"]),
        ("AF3", ["AF3", "EEG-AF3", "af3"]),
        ("AFz", ["AFz", "EEG-AFz", "afz"]),
        ("AF4", ["AF4", "EEG-AF4", "af4"]),
        ("AF8", ["AF8", "EEG-AF8", "af8"]),
        ("F5", ["F5", "EEG-F5", "f5"]),
        ("F1", ["F1", "EEG-F1", "f1"]),
        ("F2", ["F2", "EEG-F2", "f2"]),
        ("F6", ["F6", "EEG-F6", "f6"]),
        ("FC5", ["FC5", "EEG-FC5", "fc5"]),
        ("FC3", ["FC3", "EEG-FC3", "fc3"]),
        ("FC1", ["FC1", "EEG-FC1", "fc1"]),
        ("FCz", ["FCz", "EEG-FCz", "fcz"]),
        ("FC2", ["FC2", "EEG-FC2", "fc2"]),
        ("FC4", ["FC4", "EEG-FC4", "fc4"]),
        ("FC6", ["FC6", "EEG-FC6", "fc6"]),
        ("C5", ["C5", "EEG-C5", "c5"]),
        ("C1", ["C1", "EEG-C1", "c1"]),
        ("C2", ["C2", "EEG-C2", "c2"]),
        ("C6", ["C6", "EEG-C6", "c6"]),
        ("CP5", ["CP5", "EEG-CP5", "cp5"]),
        ("CP3", ["CP3", "EEG-CP3", "cp3"]),
        ("CP1", ["CP1", "EEG-CP1", "cp1"]),
        ("CPz", ["CPz", "EEG-CPz", "cpz"]),
        ("CP2", ["CP2", "EEG-CP2", "cp2"]),
        ("CP4", ["CP4", "EEG-CP4", "cp4"]),
        ("CP6", ["CP6", "EEG-CP6", "cp6"]),
        ("P5", ["P5", "EEG-P5", "p5"]),
        ("P1", ["P1", "EEG-P1", "p1"]),
        ("P2", ["P2", "EEG-P2", "p2"]),
        ("P6", ["P6", "EEG-P6", "p6"]),
        ("PO7", ["PO7", "EEG-PO7", "po7"]),
        ("PO3", ["PO3", "EEG-PO3", "po3"]),
        ("POz", ["POz", "EEG-POz", "poz"]),
        ("PO4", ["PO4", "EEG-PO4", "po4"]),
        ("PO8", ["PO8", "EEG-PO8", "po8"]),
    ]

    for target_name, aliases in standard_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    # Handle numbered EEG channels (e.g., EEG-001 -> EEG001 format)
    for ch in existing_names:
        if ch.startswith("EEG-") and ch[4:].isdigit():
            rename_map[ch] = f"EEG{ch[4:].zfill(3)}"
        elif ch.startswith("EEG") and len(ch) > 3 and ch[3:].isdigit():
            continue  # Already in correct format

    return rename_map


def _set_eeg_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types for non-EEG channels.

    Annotator: LLM, 2026-04-08
    Source: Dataset description - ECG and EMG channels present
    LLM 推断，需人类复核
    """
    # Detect EOG, ECG, EMG channels by common naming patterns
    eog_patterns = ["EOG", "VEOG", "HEOG", "eog", "veog", "heog"]
    ecg_patterns = ["ECG", "ecg", "EKG", "ekg"]
    emg_patterns = ["EMG", "emg", " EMG"]

    ch_types = {}
    for ch in raw.ch_names:
        ch_upper = ch.upper()
        if any(p.upper() in ch_upper for p in eog_patterns):
            ch_types[ch] = "eog"
        elif any(p.upper() in ch_upper for p in ecg_patterns):
            ch_types[ch] = "ecg"
        elif any(p.upper() in ch_upper for p in emg_patterns):
            ch_types[ch] = "emg"

    if ch_types:
        raw.set_channel_types(ch_types)

    return raw


class DENSKernel:
    """Stage1 kernel for DENS (openneuro_ds003751) dataset."""

    KERNEL_ID: str = "openneuro-ds003751-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file information.

        Returns
        -------
        mne.io.BaseRaw
            Processed MNE Raw object with standardized metadata.
        """
        # Get subject ID from row
        subject_id = row.get("participant_id", "unknown")
        if isinstance(subject_id, str) and subject_id.startswith("sub-"):
            subject_key = subject_id
        else:
            subject_key = f"sub-{str(subject_id).zfill(2)}"

        # Get subject info from dictionary
        subject_info = _SUBJECT_DICT.get(subject_key, {})
        sex = subject_info.get("sex", "unknown")
        age = subject_info.get("age", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        # Store original description
        original_description = raw.info.get("description", "")

        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex).lower() if sex != "unknown" else "unknown",
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": str(handedness),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for non-EEG channels
        raw = _set_eeg_channel_types(raw)

        # Try to set a standard montage, skip if insufficient channels
        try:
            # Get available channels that match standard names
            available_chs = set(raw.ch_names)
            standard_1020 = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "Cz",
                             "C4", "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "Oz", "O2",
                             "AF7", "AF3", "AFz", "AF4", "AF8"]
            montage_chs = [ch for ch in standard_1020 if ch in available_chs]
            if len(montage_chs) >= 4:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if it fails

        # Extract events from current annotations
        try:
            events_array, event_id_dict = mne.events_from_annotations(raw)
        except Exception:
            events_array = np.array([[0, 0, 0]])
            event_id_dict = {}

        # Build event_desc dict with string values only
        event_desc: Dict[int, str] = {}
        for orig_desc, event_id in event_id_dict.items():
            # Convert description to string (handle both int and str keys)
            desc_str = str(orig_desc)
            # Try to find a mapping, otherwise use the string itself
            if desc_str in _EVENT_MAP:
                event_desc[int(event_id)] = _EVENT_MAP[desc_str]
            else:
                event_desc[int(event_id)] = desc_str

        # If no events found, create empty annotations
        if len(events_array) == 0 or (len(events_array) == 1 and events_array[0][2] == 0):
            raw.set_annotations(mne.Annotations(
                onset=[], duration=[], description=[], orig_time=raw.info.get("meas_date")
            ))
        else:
            # Create new annotations using string descriptions
            try:
                new_annotations = mne.annotations_from_events(
                    events=events_array,
                    event_desc=event_desc,
                    sfreq=raw.info["sfreq"],
                    orig_time=raw.info.get("meas_date"),
                )
                raw.set_annotations(new_annotations)
            except Exception:
                pass  # Keep original annotations if conversion fails

        return raw


KERNEL = DENSKernel()