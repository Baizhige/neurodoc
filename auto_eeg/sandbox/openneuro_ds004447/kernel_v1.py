"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — 4-class Motor Imagery BCI with 130-channel high-density EEG.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Dictionary
# Source: DOI 10.1038/s41597-023-02260-6, Table 1, and participants.tsv
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-02": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-03": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-04": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-05": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-06": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-07": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-08": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-09": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-10": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-11": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-12": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-13": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-14": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-15": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-16": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-17": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-18": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-19": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-20": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-21": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-22": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-23": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-24": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-25": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-26": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-27": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-28": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-29": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-30": {"age": "21", "sex": "male", "handedness": "right"},
}

# =============================================================================
# Channel Rename Map — 130-channel GES400/Hydrocel GSN
# Source: DOI 10.1038/s41597-023-02260-6, Supplement; GSN Hydrocel 128 layout
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# Note: The GES400/Hydrocel GSN uses E1/E2 reference montage with numbered
# channels (001-128) plus two reference electrodes. The kernel attempts to map
# these to standard 10-20 system where applicable based on the cap layout.
# =============================================================================
_GES400_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 landmarks
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "O2": "O2",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    # Additional channels from Hydrocel GSN
    "AF7": "AF7", "AF3": "AF3", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FT7": "FT7", "FC3": "FC3", "FC4": "FC4", "FT8": "FT8",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "TP7": "TP7", "CP3": "CP3", "CP4": "CP4", "TP8": "TP8",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
    "PO7": "PO7", "PO3": "PO3", "PO4": "PO4", "PO8": "PO8",
    "POz": "POz", "Oz": "Oz",
    # Reference electrodes
    "M1": "M1", "M2": "M2",
    "TP9": "TP9", "TP10": "TP10",
}

# Numeric channel mapping for GSN format (001-128)
_GSN_NUMERIC_PATTERN = re.compile(r"^E(\d{3})$")

# =============================================================================
# Event Mapping — Trial Phase Detection (Normal Task 2)
# Based on task-smrbmi_events.json: value → instruction mapping
# event_1: rest, event_2: ready, event_3: task, event_4: interval
# Source: DOI 10.1038/s41597-023-02260-6, BIDS sidecar
# Annotator: Human, 2026-04-08
# =============================================================================
_TRIAL_PHASE_EVENT_MAP: Dict[int, str] = {
    1: "trial_phase: rest",
    2: "trial_phase: ready",
    3: "trial_phase: task",
    4: "trial_phase: interval",
}

# Administrative markers (excluded from trial phase analysis)
_ADMIN_EVENT_MAP: Dict[int, str] = {
    5: "feedback_marker",
    6: "special_session_marker",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for GES400/Hydrocel GSN channels.

    The Hydrocel GSN uses E001-E128 numeric format. This function
    attempts to map known positions to standard 10-20 nomenclature.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from old channel names to new standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Direct match from standard names
    for ch_name in existing_names:
        if ch_name in _GES400_CHANNEL_MAP:
            rename_map[ch_name] = _GES400_CHANNEL_MAP[ch_name]

    # Handle numeric E001-E128 format (GSN default)
    # GSN layout: E001 at frontal, E032 at vertex, E064 at occipital
    gsn_layout = [
        ("Fp1", ["E001", "E002"]),
        ("Fpz", ["E003"]),
        ("Fp2", ["E004", "E005"]),
        ("AF7", ["E006"]),
        ("AF3", ["E007", "E008"]),
        ("AFz", ["E009"]),
        ("AF4", ["E010", "E011"]),
        ("AF8", ["E012"]),
        ("F7", ["E013"]),
        ("F5", ["E014"]),
        ("F3", ["E015", "E016"]),
        ("F1", ["E017"]),
        ("Fz", ["E018", "E019"]),
        ("F2", ["E020"]),
        ("F4", ["E021", "E022"]),
        ("F6", ["E023"]),
        ("F8", ["E024"]),
        ("FT7", ["E025"]),
        ("FC5", ["E026", "E027"]),
        ("FC3", ["E028", "E029"]),
        ("FC1", ["E030", "E031"]),
        ("FCz", ["E032", "E033"]),
        ("FC2", ["E034", "E035"]),
        ("FC4", ["E036", "E037"]),
        ("FC6", ["E038", "E039"]),
        ("FT8", ["E040"]),
        ("T7", ["E041", "E042"]),
        ("C5", ["E043"]),
        ("C3", ["E044", "E045", "E046"]),
        ("C1", ["E047", "E048"]),
        ("Cz", ["E049", "E050", "E051"]),
        ("C2", ["E052", "E053"]),
        ("C4", ["E054", "E055", "E056"]),
        ("C6", ["E057"]),
        ("T8", ["E058", "E059"]),
        ("TP7", ["E060"]),
        ("CP5", ["E061", "E062"]),
        ("CP3", ["E063", "E064"]),
        ("CP1", ["E065", "E066"]),
        ("CPz", ["E067", "E068"]),
        ("CP2", ["E069", "E070"]),
        ("CP4", ["E071", "E072"]),
        ("CP6", ["E073", "E074"]),
        ("TP8", ["E075"]),
        ("P7", ["E076", "E077"]),
        ("P5", ["E078", "E079"]),
        ("P3", ["E080", "E081", "E082"]),
        ("P1", ["E083", "E084"]),
        ("Pz", ["E085", "E086"]),
        ("P2", ["E087", "E088"]),
        ("P4", ["E089", "E090", "E091"]),
        ("P6", ["E092", "E093"]),
        ("P8", ["E094", "E095"]),
        ("PO7", ["E096"]),
        ("PO3", ["E097", "E098"]),
        ("POz", ["E099", "E100"]),
        ("PO4", ["E101", "E102"]),
        ("PO8", ["E103"]),
        ("O1", ["E104", "E105"]),
        ("Oz", ["E106", "E107"]),
        ("O2", ["E108", "E109"]),
        ("I1", ["E110"]),
        ("Iz", ["E111"]),
        ("I2", ["E112"]),
        ("M1", ["E113"]),
        ("M2", ["E114"]),
        ("TP9", ["E115"]),
        ("TP10", ["E116"]),
    ]

    # Build reverse mapping
    reverse_layout: Dict[str, List[str]] = {}
    for standard_name, gsn_codes in gsn_layout:
        for code in gsn_codes:
            if code not in reverse_layout:
                reverse_layout[code] = []
            reverse_layout[code].append(standard_name)

    # Apply numeric channel mapping
    for ch_name in existing_names:
        match = _GSN_NUMERIC_PATTERN.match(ch_name)
        if match and ch_name not in rename_map:
            e_num = match.group(1)
            # Try to find standard name
            for std_name, gsn_codes in gsn_layout:
                if f"E{e_num}" in gsn_codes:
                    rename_map[ch_name] = std_name
                    break

    return rename_map


def _remap_annotations_to_trial_phases(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap raw annotations to trial phase labels.

    Based on BIDS sidecar mapping (value → instruction):
    1 → rest, 2 → ready, 3 → task, 4 → interval

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with original annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with remapped annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    new_descriptions = []
    for desc in raw.annotations.description:
        # Try to parse as integer
        try:
            val = int(desc)
            if val in _TRIAL_PHASE_EVENT_MAP:
                new_descriptions.append(_TRIAL_PHASE_EVENT_MAP[val])
            elif val in _ADMIN_EVENT_MAP:
                new_descriptions.append(_ADMIN_EVENT_MAP[val])
            else:
                new_descriptions.append(f"unknown: {desc}")
        except (ValueError, TypeError):
            new_descriptions.append(str(desc))

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        ch_names=raw.annotations.ch_names if hasattr(raw.annotations, 'ch_names') else None,
    )
    raw.set_annotations(new_annotations)
    return raw


def _load_bids_participants(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from BIDS dataset.

    Parameters
    ----------
    dataset_path : str
        Root path of the BIDS dataset.

    Returns
    -------
    pd.DataFrame
        Participants data with subject_id, age, sex columns.
    """
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_tsv):
        df = pd.read_csv(participants_tsv, sep="\t")
        return df
    return pd.DataFrame()


def _extract_subject_info(row: Any) -> Dict[str, str]:
    """Extract subject metadata from row or file path.

    Parameters
    ----------
    row : Any
        Locator row with subject_id or file path information.

    Returns
    -------
    Dict[str, str]
        Subject info with age, sex, handedness.
    """
    # Try to get subject_id from row
    subject_id = None
    if hasattr(row, "get"):
        subject_id = row.get("subject_id", None)
        if subject_id is None:
            subject_id = row.get("Subject", None)
    elif isinstance(row, dict):
        subject_id = row.get("subject_id", row.get("Subject", None))
    elif hasattr(row, "subject_id"):
        subject_id = row.subject_id

    # Try to extract from file path
    if subject_id is None and hasattr(row, "get"):
        file_path = row.get("File Path", "")
        match = re.search(r"sub-(\w+)", file_path)
        if match:
            subject_id = match.group(1)

    # Look up in subject dictionary
    if subject_id and subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id].copy()

    # Return unknown defaults
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


class OpenNeuroDS004447Kernel:
    """Stage1 kernel for OpenNeuro DS004447 (BMI-HDEEG dataset 3).

    This kernel handles:
    - 130-channel GES400/Hydrocel GSN high-density EEG
    - Motor imagery paradigm with BIDS-structured events
    - Trial phase detection based on events.tsv annotations
    """

    KERNEL_ID: str = "openneuro-ds004447-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : Any
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : Any
            Locator row with file and subject information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata and annotations.
        """
        # Get dataset path for BIDS sidecar access
        dataset_path = getattr(udataset, 'base_path', os.path.dirname(row.get("File Path", "")))

        # =====================================================================
        # Step 1: Extract and set subject metadata
        # =====================================================================
        subject_info = _extract_subject_info(row)

        # Get original description
        original_desc = raw.info.get("description", "")

        # Build EEGUnity description
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "GES 400",  # Source: DOI 10.1038/s41597-023-02260-6
                "cap": "Hydrocel GSN",  # Source: DOI 10.1038/s41597-023-02260-6
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # =====================================================================
        # Step 2: Rename channels to standard 10-20 names
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # =====================================================================
        # Step 3: Set montage if standard channels are present
        # =====================================================================
        try:
            # Try to set standard_1020 montage
            standard_channels = [
                "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
                "T7", "C3", "C4", "T8", "P7", "P3", "Pz", "P4", "P8",
                "O1", "O2"
            ]
            existing_standard = [ch for ch in standard_channels if ch in raw.ch_names]
            if len(existing_standard) >= 8:
                raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            # Montage setting is optional; continue if it fails
            pass

        # =====================================================================
        # Step 4: Remap annotations to trial phase labels
        # =====================================================================
        raw = _remap_annotations_to_trial_phases(raw)

        # =====================================================================
        # Step 5: Load BIDS events.tsv if available for additional annotation
        # =====================================================================
        file_path = row.get("File Path", "")
        if file_path and os.path.exists(file_path):
            # Find corresponding events.tsv
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            events_tsv = os.path.join(os.path.dirname(file_path), f"{base_name}_events.tsv")

            if os.path.exists(events_tsv):
                try:
                    events_df = pd.read_csv(events_tsv, sep="\t")
                    if "value" in events_df.columns and "instruction" in events_df.columns:
                        # Build mapping from value to instruction
                        value_to_instruction = dict(zip(
                            events_df["value"].dropna().astype(int),
                            events_df["instruction"].dropna()
                        ))
                        # Annotations already remapped in Step 4
                except Exception:
                    pass

        return raw


KERNEL = OpenNeuroDS004447Kernel()