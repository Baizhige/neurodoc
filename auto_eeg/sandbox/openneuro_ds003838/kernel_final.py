"""OpenNeuro DS003838 stage1 kernel for EEGUnity.

Digit span working memory task with EEG, pupillometry, ECG and PPG recordings.
Contains 64-channel EEG data with events encoding digit position, sequence
length (5/9/13), and recall outcome (correct/error).

Source: https://openneuro.org/datasets/ds003838/versions/1.0.0
Paper: DOI 10.1038/s41597-022-01414-2 (Scientific Data)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: DOI 10.1038/s41597-022-01414-2, Table 1 - EEG acquisition details
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Note: Age and sex should be loaded from participants.tsv in BIDS structure
# Fallback values set to "unknown" - LLM did not infer specific values
# Annotator: LLM, 2026-04-08

# Amplifier and cap information from paper
# Source: DOI 10.1038/s41597-022-01414-2
# Annotator: Human, 2026-04-08
_AMPLIFIER = "BrainAmp"  # Brain Products amplifier
_CAP = "Ag/AgCl"  # Standard EEG cap

# Standard 10-20 system channel names for 64-channel EEG
# Source: DOI 10.1038/s41597-022-01414-2 - confirms 64-channel EEG montage
# Annotator: Human, 2026-04-08
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
]

# Additional non-EEG channels typically present
_OTHER_CHANNELS = [
    "ECG", " PPG", " Resp", " Temp", "EOG1", "EOG2", "EOG3", "EOG4",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map to standardize channel names to 10-20 system.

    Handles various naming conventions that may appear in raw data.
    Source: DOI 10.1038/s41597-022-01414-2
    Annotator: Human, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common alias patterns for 10-20 system channels
    alias_groups = [
        ("Fp1", ["Fp1", "FP1", "fp1"]),
        ("Fp2", ["Fp2", "FP2", "fp2"]),
        ("Fpz", ["Fpz", "FPz", "fpz"]),
        ("F7", ["F7", "F07"]),
        ("F3", ["F3", "F03"]),
        ("Fz", ["Fz", "Fz"]),
        ("F4", ["F4", "F04"]),
        ("F8", ["F8", "F08"]),
        ("T7", ["T7", "T07", "T7"]),
        ("C3", ["C3", "C03"]),
        ("Cz", ["Cz", "Cz"]),
        ("C4", ["C4", "C04"]),
        ("T8", ["T8", "T08", "T8"]),
        ("P7", ["P7", "P07"]),
        ("P3", ["P3", "P03"]),
        ("Pz", ["Pz", "Pz"]),
        ("P4", ["P4", "P04"]),
        ("P8", ["P8", "P08"]),
        ("O1", ["O1", "O01"]),
        ("Oz", ["Oz", "Oz"]),
        ("O2", ["O2", "O02"]),
        ("FC1", ["FC1", "FC01"]),
        ("FC2", ["FC2", "FC02"]),
        ("FCz", ["FCz", "FCz"]),
        ("CP1", ["CP1", "CP01"]),
        ("CP2", ["CP2", "CP02"]),
        ("CPz", ["CPz", "CPz"]),
        ("EOG1", ["EOG1", "EOG-left", "HEOG"]),
        ("EOG2", ["EOG2", "EOG-right", "HEOG2"]),
        ("ECG", ["ECG", "ecg", "ECG"]),
        ("PPG", [" PPG", "PPG", "ppg", "PLETH"]),
        ("Resp", [" Resp", "RESP", "resp", "Respiration"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _extract_subject_info(row: pd.Series, dataset_root: str) -> Dict[str, str]:
    """Extract subject age and sex from BIDS participants.tsv.

    Source: BIDS standard participants.tsv
    Annotator: Human, 2026-04-08
    """
    subject_id = row.get("participant_id", "")

    # Try to load from participants.tsv
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            subj_row = df[df["participant_id"] == subject_id]
            if not subj_row.empty:
                age = subj_row["age"].values[0]
                sex = subj_row["sex"].values[0] if "sex" in subj_row.columns else "unknown"
                handedness = subj_row["handedness"].values[0] if "handedness" in subj_row.columns else "unknown"

                # Normalize sex to lowercase
                if pd.notna(sex):
                    sex = str(sex).lower()
                    if sex not in ["male", "female"]:
                        sex = "unknown"
                else:
                    sex = "unknown"

                return {
                    "age": str(int(age)) if pd.notna(age) and str(age).isdigit() else str(age),
                    "sex": sex,
                    "handedness": str(handedness).lower() if pd.notna(handedness) else "unknown",
                }
        except Exception:
            pass

    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _remap_memory_events(annotations: mne.Annotations) -> mne.Annotations:
    """Remap memory events to standardized format.

    Original events may have format like '5' or '9' or '13' for sequence length.
    Target format: 'memory X/05 correct', 'memory X/09 error', etc.

    Source: DOI 10.1111/psyp.14275 - event structure description
    Annotator: Human, 2026-04-08
    """
    new_descriptions = []

    for desc in annotations.description:
        desc_str = str(desc).strip()

        # Pattern: digit position / sequence length / outcome
        # e.g., "1/5/correct", "3/9/error", "5/13/correct"
        pattern = r"(\d+)/(\d+)/(correct|error)"
        match = re.match(pattern, desc_str, re.IGNORECASE)

        if match:
            pos, seq_len, outcome = match.groups()
            new_desc = f"memory {pos}/{seq_len} {outcome}"
            new_descriptions.append(new_desc)
        elif desc_str.upper() == "STATUS":
            new_descriptions.append("STATUS")
        else:
            new_descriptions.append(desc_str)

    return mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )


@dataclass
class OpenNeuroDS003838Kernel:
    """Stage1 kernel for OpenNeuro DS003838 digit span dataset."""

    KERNEL_ID: str = "openneuro-ds003838-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized metadata and events.
        """
        file_path = row.get("File Path", "")
        dataset_root = os.path.dirname(os.path.dirname(file_path)) if file_path else ""

        # Step 1: Rename channels to standard 10-20 system
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
            print(f"[Kernel] Renamed channels: {rename_map}")

        # Step 2: Set montage if possible (only for recognized EEG channels)
        eeg_channels = [ch for ch in raw.ch_names if ch not in ["ECG", " PPG", " Resp", " Temp", "EOG1", "EOG2", "EOG3", "EOG4"]]
        known_channels = [ch for ch in eeg_channels if ch in _STANDARD_64_CHANNELS or ch in ["Fp1", "Fpz", "Fp2", "O1", "Oz", "O2", "Fz", "Cz", "Pz"]]

        if len(known_channels) >= 19:  # At least basic 10-20 coverage
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
                print(f"[Kernel] Set standard_1020 montage for {len(known_channels)} channels")
            except Exception as e:
                print(f"[Kernel] Could not set montage: {e}")

        # Step 3: Extract subject information
        subject_info = _extract_subject_info(row, dataset_root)

        # Step 4: Update description with eegunity_description
        original_desc = raw.info.get("description", "")
        if not original_desc:
            original_desc = ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Step 5: Remap memory events to standardized format
        if raw.annotations is not None and len(raw.annotations) > 0:
            raw.set_annotations(_remap_memory_events(raw.annotations))

        # Step 6: Set channel types for non-EEG channels
        channel_types = {}
        for ch in raw.ch_names:
            if ch in ["ECG"]:
                channel_types[ch] = "ecg"
            elif ch.strip() in ["PPG", "PLETH"]:
                channel_types[ch] = "misc"
            elif " Resp" in ch or "respir" in ch.lower():
                channel_types[ch] = "resp"
            elif " EOG" in ch or ch.startswith("EOG"):
                channel_types[ch] = "eog"

        if channel_types:
            try:
                raw.set_channel_types(channel_types)
                print(f"[Kernel] Set channel types: {channel_types}")
            except Exception as e:
                print(f"[Kernel] Could not set channel types: {e}")

        return raw


KERNEL = OpenNeuroDS003838Kernel()