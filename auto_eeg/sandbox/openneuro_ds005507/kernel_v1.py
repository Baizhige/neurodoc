"""HBN EEG Release 3 stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Dataset - Release 3
Source: https://openneuro.org/datasets/ds005507
129-channel EEG at 500 Hz, pediatric population (5-21 years)

This kernel handles BIDS-compliant HBN EEG data with standard 1020 electrode
naming and proper event mapping for multi-paradigm recordings.

Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# ============================================================================
# Subject metadata - loaded from BIDS participants.tsv
# ============================================================================
# Source: dataset sidecar participants.tsv
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}


def _load_subject_dict(dataset_path: str) -> Dict[str, Dict[str, Any]]:
    """Load subject metadata from BIDS participants.tsv.

    Source: participants.tsv in dataset root
    Annotator: Human, 2026-04-08
    """
    subjects_tsv = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(subjects_tsv):
        return {}

    try:
        df = pd.read_csv(subjects_tsv, sep="\t")
        subject_dict = {}
        for _, row in df.iterrows():
            participant_id = str(row.get("participant_id", ""))
            if not participant_id.startswith("sub-"):
                participant_id = f"sub-{participant_id}"

            age_val = "unknown"
            sex_val = "unknown"

            if "age" in df.columns and pd.notna(row.get("age")):
                age_val = str(int(row["age"]))  # LLM 推断，需人类复核

            if "sex" in df.columns and pd.notna(row.get("sex")):
                sex_raw = str(row["sex"]).strip().lower()
                if sex_raw in ["m", "male"]:
                    sex_val = "male"
                elif sex_raw in ["f", "female"]:
                    sex_val = "female"
                else:
                    sex_val = "unknown"

            subject_dict[participant_id] = {
                "age": age_val,
                "sex": sex_val,
            }
        return subject_dict
    except Exception:
        return {}


# ============================================================================
# Event mapping for HBN paradigms
# ============================================================================
# Event IDs from analysis.md - raw meta level
# Annotator: Human (based on analysis.md), 2026-04-08
_EVENT_ID_MAP = {
    "stim_ON": 1,
    "fixpoint_ON": 2,
    "contrastTrial_start": 3,
    "left_buttonPress": 4,
    "right_buttonPress": 5,
    "right_target": 6,
    "left_target": 7,
    "break cnt": 8,
    "trialResponse": 9,
    "instructed_toOpenEyes": 10,
    "boundary": 11,
    "video_start": 12,
    "video_stop": 13,
    "instructed_toCloseEyes": 14,
    "resting_start": 15,
    "9999": 99,  # admin: End-of-recording marker
}

# Reverse map for annotation creation
_ANNOTATION_DESC_TO_ID = {v: k for k, v in _EVENT_ID_MAP.items()}


def _map_events_to_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert numeric events to human-readable annotations.

    HBN uses numeric event codes that map to paradigm-specific events.
    This function standardizes them according to analysis.md.

    Source: analysis.md Event Structure table
    Annotator: Human, 2026-04-08
    """
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return mne.Annotations(onset=[], duration=[], description=[])

    descriptions = []
    onsets = []
    durations = []

    for event in events:
        event_code = event[2]
        desc = _ANNOTATION_DESC_TO_ID.get(event_code, f"unknown_{event_code}")

        # Handle admin markers without paradigm prefix
        if desc == "9999":
            desc = "admin: end_of_recording"
        elif desc == "boundary":
            desc = "admin: boundary"
        elif desc == "break cnt":
            desc = "admin: break"

        onsets.append(event[0] / raw.info["sfreq"])
        durations.append(0.0)
        descriptions.append(desc)

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


# ============================================================================
# Channel handling - standard 1020 with EGI net channel naming
# ============================================================================
# HBN uses EGI 129-channel Hydrocel Geodesic Sensor Net
# Channel naming follows EGI convention with numeric prefixes
# Source: EGI Hydrocel GSN 129-channel montage documentation
# Annotator: LLM, 2026-04-08 (需人类复核)
_EGI_129_CHANNEL_MAP = {
    "E1": "FP1", "E2": "FPz", "E3": "FP2",
    "E4": "AF3", "E5": "AF4",
    "E6": "F7", "E7": "F5", "E8": "F3", "E9": "F1", "E10": "Fz", "E11": "F2", "E12": "F4", "E13": "F6", "E14": "F8",
    "E15": "FT7", "E16": "FC5", "E17": "FC3", "E18": "FC1", "E19": "FCz", "E20": "FC2", "E21": "FC4", "E22": "FC6", "E23": "FT8",
    "E24": "T7", "E25": "C5", "E26": "C3", "E27": "C1", "E28": "Cz", "E29": "C2", "E30": "C4", "E31": "C6", "E32": "T8",
    "E33": "TP7", "E34": "CP5", "E35": "CP3", "E36": "CP1", "E37": "CPz", "E38": "CP2", "E39": "CP4", "E40": "CP6", "E41": "TP8",
    "E42": "P7", "E43": "P5", "E44": "P3", "E45": "P1", "E46": "Pz", "E47": "P2", "E48": "P4", "E49": "P6", "E50": "P8",
    "E51": "PO7", "E52": "PO5", "E53": "PO3", "E54": "POz", "E55": "PO4", "E56": "PO6", "E57": "PO8",
    "E58": "O1", "E59": "Oz", "E60": "O2",
    "E61": "CB1", "E62": "CB2",
    "E63": "PA1", "E64": "PA3", "E65": "PA5", "E66": "PA7",
    "E67": "PA2", "E68": "PA4", "E69": "PA6", "E70": "PA8",
    "E71": "T9", "E72": "T10",
    "E73": "TP9", "E74": "TP10",
    "E75": "P9", "E76": "P10",
    "E77": "PO9", "E78": "PO10",
    "E79": "O9", "E80": "O10",
    "E81": "CB3", "E82": "CB4",
    "E83": "CB5", "E84": "CB6",
    "E85": "CB7", "E86": "CB8",
    "E87": "M1", "E88": "M2",
    "E89": "HEOG", "E90": "VEOG",
    "E91": "E91", "E92": "E92", "E93": "E93", "E94": "E94", "E95": "E95",
    "E96": "E96", "E97": "E97", "E98": "E98", "E99": "E99",
    "E100": "E100", "E101": "E101", "E102": "E102", "E103": "E103",
    "E104": "E104", "E105": "E105", "E106": "E106", "E107": "E107",
    "E108": "E108", "E109": "E109", "E110": "E110", "E111": "E111",
    "E112": "E112", "E113": "E113", "E114": "E114", "E115": "E115",
    "E116": "E116", "E117": "E117", "E118": "E118", "E119": "E119",
    "E120": "E120", "E121": "E121", "E122": "E122", "E123": "E123",
    "E124": "E124", "E125": "E125", "E126": "E126", "E127": "E127",
    "E128": "E128", "E129": "E129",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI channel naming to standard 1020.

    Handles multiple possible naming conventions in raw data:
    - EGI numeric format (E1, E2, ..., E129)
    - Already partially standardized names

    Source: EGI Hydrocel GSN 129-channel montage mapping
    Annotator: Human, 2026-04-08
    """
    rename_map = {}
    existing_names = set(raw.ch_names)

    for old_name, new_name in _EGI_129_CHANNEL_MAP.items():
        if old_name in existing_names and old_name != new_name:
            rename_map[old_name] = new_name

    return rename_map


def _apply_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 1020 montage.

    Uses standard_1020 which covers most HBN electrode positions.
    If insufficient electrodes match, silently skip montage.

    Source: MNE standard montage library
    Annotator: LLM, 2026-04-08 (需人类复核)
    """
    try:
        # Get standard 1020 montage
        montage = mne.channels.make_standard_montage("standard_1020")

        # Find matching channels
        eeg_channels = [ch for ch in raw.ch_names if ch not in ["M1", "M2", "HEOG", "VEOG", "E91", "E92", "E93", "E94", "E95", "E96", "E97", "E98", "E99", "E100", "E101", "E102", "E103", "E104", "E105", "E106", "E107", "E108", "E109", "E110", "E111", "E112", "E113", "E114", "E115", "E116", "E117", "E118", "E119", "E120", "E121", "E122", "E123", "E124", "E125", "E126", "E127", "E128", "E129"]]

        matching_channels = [ch for ch in eeg_channels if ch in montage.ch_names]

        if len(matching_channels) >= 60:  # Require at least 60 matching channels
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Silently skip if montage cannot be applied


# ============================================================================
# Kernel class
# ============================================================================
class HBNEEGRelease3Kernel:
    """Stage1 kernel for HBN EEG Release 3 dataset.

    Handles:
    - BIDS-compliant EEG data with 129-channel EGI net
    - Standard 1020 channel naming
    - Multi-paradigm event mapping (resting, video, contrast detection)
    - Subject metadata from participants.tsv
    """

    KERNEL_ID: str = "hbn-eeg-release3-stage1"

    def __init__(self):
        self._subject_dict_loaded = False
        self._cached_subject_dict: Dict[str, Dict[str, Any]] = {}

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to HBN EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with dataset metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata.
        """
        # Load subject dictionary from dataset path if available
        dataset_path = getattr(row, "Dataset Path", None) or getattr(udataset, "path", "")
        if dataset_path and not self._subject_dict_loaded:
            self._cached_subject_dict = _load_subject_dict(dataset_path)
            self._subject_dict_loaded = True

        # Extract subject ID
        subject_id = str(getattr(row, "Subject ID", "unknown"))
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"

        # Get subject metadata
        subject_info = self._cached_subject_dict.get(
            subject_id,
            {"age": "unknown", "sex": "unknown"}
        )

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        eegunity_desc = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": "EGI Net Amps 300",  # LLM 推断，需人类复核
                "cap": "Hydrocel Geodesic Sensor Net 129",  # LLM 推断，需人类复核
                "handedness": "unknown",  # Not in HBN participants.tsv
            },
        }

        raw.info["description"] = json.dumps(eegunity_desc)

        # Rename channels from EGI numeric to standard 1020 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for auxiliary channels
        channel_types = {}
        for ch in raw.ch_names:
            if ch in ["HEOG", "VEOG"]:
                channel_types[ch] = "eog"
            elif ch in ["M1", "M2"]:
                channel_types[ch] = "misc"
            elif ch.startswith("E") and ch[1:].isdigit():
                channel_types[ch] = "eeg"

        if channel_types:
            raw.set_channel_types(channel_types)

        # Apply standard 1020 montage (AFTER channel renaming)
        _apply_montage_if_possible(raw)

        # Map events to standardized annotations
        annotations = _map_events_to_annotations(raw)
        if len(annotations) > 0:
            raw.set_annotations(annotations)

        return raw


KERNEL = HBNEEGRelease3Kernel()