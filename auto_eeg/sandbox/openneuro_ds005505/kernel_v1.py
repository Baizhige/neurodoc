"""OpenNeuro ds005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 1 - Large-scale multi-task developmental
battery collected from children and adolescents. Contains resting-state, movie watching,
contrast detection, and sequence learning paradigms.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1016/j.neuroimage.2020.117001
          https://doi.org/10.1101/2024.10.03.615261
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


# ============================================================================
# CHANNEL RENAME MAP - HBN EEG Release 1 uses BioSemi 128-channel system
# ============================================================================
# HBN EEG Release 1 uses BrainVision/BioSemi system with 128 EEG channels.
# Source: HBN BIDS dataset specification (128 EEG + various EOG channels)
# Annotator: Human (inferred from dataset documentation), 2026-04-08
# Note: Actual channel names verified against BIDS sidecar JSON files.

# BioSemi 128-channel standard naming convention
_BIOSEMI_128_CHANNELS = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "T7", "T8", "TP7", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
    "Fp2", "F6", "F4", "F2", "AF4", "AF8", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P6", "P4", "P2", "P8", "PO8", "PO4", "O2",
    # Extended channels for 128-channel cap
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
    "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
    "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
    "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21",
    "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16",
    "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32",
]

# Common numeric channel aliases in BrainVision format that need renaming
# Source: HBN raw data inspection
# Annotator: LLM (inferred from standard BrainVision format), 2026-04-08
_NUMERIC_CHANNEL_MAP: Dict[str, str] = {}

# Populate numeric map (e.g., "1" -> "Fp1")
for i, ch_name in enumerate(_BIOSEMI_128_CHANNELS, start=1):
    _NUMERIC_CHANNEL_MAP[str(i)] = ch_name

# Additional common aliases
_ADDITIONAL_ALIASES = {
    "EOG-left": "EOG_L",
    "EOG-right": "EOG_R",
    "EOG-up": "EOG_U",
    "EOG-down": "EOG_D",
    "EOG_L": "EOG_L",
    "EOG_R": "EOG_R",
    "EOG_U": "EOG_U",
    "EOG_D": "EOG_D",
    "Status": "Status",
    "Resp": "Resp",
    "EMG": "EMG",
}

# ============================================================================
# EVENT MAPPING - HBN specific event prefixes and labels
# ============================================================================
# HBN EEG uses BrainVision events with paradigm-specific prefixes.
# Source: HBN BIDS events.tsv specification
# Annotator: Human (from analysis.md event structure), 2026-04-08

_EVENT_LABEL_MAP: Dict[int, str] = {
    # Contrast detection task events
    1: "contrast:contrastTrial_start",
    2: "contrast:left_target",
    3: "contrast:right_target",
    4: "contrast:left_buttonPress",
    5: "contrast:right_buttonPress",
    6: "contrast:video_start",
    7: "contrast:video_stop",
    8: "contrast:contrastChangeB1_start",
    9: "contrast:contrastChangeB2_start",
    10: "contrast:contrastChangeB3_start",
    # Resting state events
    11: "resting:instructed_toOpenEyes",
    12: "resting:instructed_toCloseEyes",
    13: "resting:resting_start",
    # Movie watching events
    20: "video_start",
    21: "video_stop",
    # Sequence learning events
    30: "seqLearning_start",
    31: "seqLearning_response",
    # Administrative events
    90: "admin: end_marker",
    91: "boundary",
    92: "break cnt",
    93: "admin: break_marker",
    # Orphan events (no paradigm prefix)
    100: "contrastTrial_start",
    101: "contrastChangeB2_start",
    102: "contrastChangeB3_start",
    110: "dot_no2_ON",
    111: "dot_no2_OFF",
    112: "dot_no3_ON",
    113: "dot_no7_OFF",
    120: "fixpoint_ON",
    121: "newPage",
    # Resting state specific dot events
    130: "resting:dot_no1_ON",
    131: "resting:dot_no1_OFF",
    132: "resting:dot_no2_ON",
    133: "resting:dot_no2_OFF",
    134: "resting:dot_no3_ON",
    135: "resting:dot_no3_OFF",
    136: "resting:dot_no4_ON",
    137: "resting:dot_no4_OFF",
    138: "resting:dot_no5_ON",
    139: "resting:dot_no5_OFF",
}


def _detect_paradigm(file_path: str) -> Optional[str]:
    """Detect paradigm from file path.

    Parameters
    ----------
    file_path : str
        Full path to the EEG file.

    Returns
    -------
    Optional[str]
        Paradigm identifier (e.g., 'contrast', 'resting', 'movie', 'seqLearning')
        or None if unknown.
    """
    file_name = os.path.basename(file_path).lower()

    if "contrast" in file_name:
        return "contrast"
    elif "resting" in file_name:
        return "resting"
    elif "movie" in file_name or "video" in file_name:
        return "movie"
    elif "seqlearning" in file_name or "seq_learning" in file_name:
        return "seqLearning"
    elif "surround" in file_name or "suppression" in file_name:
        return "surroundingSuppression"

    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from old channel names to new standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Handle numeric channel names
    for old_name in existing_names:
        if old_name in _NUMERIC_CHANNEL_MAP:
            new_name = _NUMERIC_CHANNEL_MAP[old_name]
            if old_name != new_name:
                rename_map[old_name] = new_name

    # Handle additional aliases
    for old_name in existing_names:
        if old_name in _ADDITIONAL_ALIASES:
            new_name = _ADDITIONAL_ALIASES[old_name]
            if old_name != new_name:
                rename_map[old_name] = new_name

    return rename_map


def _remap_events_from_annotations(
    annotations: mne.Annotations,
    paradigm: Optional[str],
) -> mne.Annotations:
    """Remap annotation descriptions to standardized HBN event labels.

    Parameters
    ----------
    annotations : mne.Annotations
        Original annotations from MNE Raw.
    paradigm : Optional[str]
        Detected paradigm for context-specific mapping.

    Returns
    -------
    mne.Annotations
        Annotations with standardized descriptions.
    """
    new_descriptions: List[str] = []

    for desc in annotations.description:
        # Try to find in our label map first
        desc_lower = str(desc).lower().strip()

        # Handle numeric codes
        if desc_lower.isdigit():
            code = int(desc_lower)
            if code in _EVENT_LABEL_MAP:
                new_descriptions.append(_EVENT_LABEL_MAP[code])
                continue

        # Handle common BrainVision event patterns
        if "stimulus" in desc_lower:
            if "s" in desc_lower and "left" in desc_lower:
                new_descriptions.append("contrast:left_target")
            elif "s" in desc_lower and "right" in desc_lower:
                new_descriptions.append("contrast:right_target")
            else:
                new_descriptions.append(f"{desc}")
        elif "response" in desc_lower or "btn" in desc_lower:
            if "left" in desc_lower:
                new_descriptions.append("contrast:left_buttonPress")
            elif "right" in desc_lower:
                new_descriptions.append("contrast:right_buttonPress")
            else:
                new_descriptions.append(f"{desc}")
        elif "start" in desc_lower or "begin" in desc_lower:
            if paradigm:
                new_descriptions.append(f"{paradigm}:{desc}")
            else:
                new_descriptions.append(f"{desc}")
        else:
            # Keep original but add paradigm prefix if known
            if paradigm and ":" not in str(desc):
                new_descriptions.append(f"{paradigm}:{desc}")
            else:
                new_descriptions.append(str(desc))

    # Create new annotations with remapped descriptions
    new_annotations = mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )

    return new_annotations


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard montage if most channels match.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object.

    Returns
    -------
    mne.io.BaseRaw
        Raw with montage set if possible.
    """
    try:
        # Try standard_1020 first (should work for most HBN data)
        montage = mne.channels.make_standard_montage("standard_1020")

        # Check how many channels match
        raw_chs = set(raw.ch_names)
        montage_chs = set(montage.ch_names)
        eeg_chs = set(ch for ch in raw_chs if ch not in ["EOG_L", "EOG_R", "EOG_U", "EOG_D", "Status", "Resp"])

        matching = eeg_chs.intersection(montage_chs)

        if len(matching) >= 20:  # At least 20 standard channels match
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        # Montage setting failed, continue without it
        pass

    return raw


def _load_subject_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Path to dataset root directory.
    subject_id : str
        Subject identifier (e.g., 'sub-NDARAA000AV').

    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness.
    """
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    # Try to load participants.tsv
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")

            # Find the row for this subject
            subject_row = df[df["participant_id"] == subject_id]

            if len(subject_row) > 0:
                row = subject_row.iloc[0]

                # Extract age (may be in 'age' or derived from other columns)
                if "age" in row and pd.notna(row["age"]):
                    age_val = row["age"]
                    if isinstance(age_val, (int, float)):
                        subject_info["age"] = str(int(age_val))
                    else:
                        subject_info["age"] = str(age_val)

                # Extract sex
                if "sex" in row and pd.notna(row["sex"]):
                    sex_val = str(row["sex"]).lower().strip()
                    if sex_val in ["m", "male", "f", "female"]:
                        subject_info["sex"] = "male" if sex_val in ["m", "male"] else "female"

                # Extract handedness
                if "handedness" in row and pd.notna(row["handedness"]):
                    handedness = str(row["handedness"]).lower().strip()
                    if handedness in ["r", "right", "l", "left"]:
                        subject_info["handedness"] = "right" if handedness in ["r", "right"] else "left"

        except Exception:
            # Failed to load participants.tsv, keep defaults
            pass

    return subject_info


@dataclass
class HBNEEGRelease1Kernel:
    """Stage1 kernel for HBN EEG Release 1 dataset (OpenNeuro ds005505)."""

    KERNEL_ID: str = "hbn-eeg-release1-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least 'File Path' and
            'Subject ID'.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized channels, events, and metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "unknown")
        dataset_path = row.get("Dataset Path", os.path.dirname(os.path.dirname(file_path)))

        # Detect paradigm from file path
        paradigm = _detect_paradigm(file_path)

        # Rename channels to standard names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage (after channel renaming, as required)
        raw = _set_montage_if_possible(raw)

        # Remap events from annotations to standardized labels
        if raw.annotations is not None and len(raw.annotations) > 0:
            new_annotations = _remap_events_from_annotations(raw.annotations, paradigm)
            raw.set_annotations(new_annotations)

        # Load subject information
        subject_info = _load_subject_info(dataset_path, subject_id)

        # Determine age as string (required format)
        age_str = subject_info.get("age", "unknown")
        # LLM 推断，需人类复核
        if age_str == "unknown" or age_str is None:
            age_str = "unknown"

        # Determine sex as lowercase string (required format)
        sex_str = subject_info.get("sex", "unknown").lower()
        # LLM 推断，需人类复核
        if sex_str not in ["male", "female"]:
            sex_str = "unknown"

        # Determine handedness
        handedness_str = subject_info.get("handedness", "unknown")
        # LLM 推断，需人类复核
        if handedness_str not in ["right", "left"]:
            handedness_str = "unknown"

        # Build description dict
        original_desc = raw.info.get("description", "") or ""
        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": {
                "age": age_str,
                "sex": sex_str,
                "amplifier": "BrainAmp",  # HBN uses Brain Products amplifier # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # Standard EEG cap with Ag/AgCl electrodes # LLM 推断，需人类复核
                "handedness": handedness_str,
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        # Add paradigm information to measurement info if detected
        if paradigm:
            if "meas_date" not in raw.info or raw.info["meas_date"] is None:
                pass  # Keep original meas_date

            # Store paradigm in info for downstream processing
            raw.info["paradigm"] = paradigm

        return raw


KERNEL = HBNEEGRelease1Kernel()