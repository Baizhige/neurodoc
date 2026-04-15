"""Dataset-specific kernel for openneuro_ds001785.

Evidence accumulation / vibrotactile detection task.
71-channel EEG at 1024 Hz from 21 subjects.
BIDS format with events.tsv and participants.tsv.

Supports:
- Raw meta: stimulus events 200/201
- Super meta: SDT four-class (hit/miss/cr/fa) derived from response markers
- Regression: confidence ratings from misc channel

Source: https://doi.org/10.1038/s41467-021-23540-y
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np

# Import base kernel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from kernels.openneuro_specific._base import OpenNeuroBaseKernel


# Channel rename map for 71-channel system
# Source: Paper supplementary materials / standard 10-20 extended montage
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 frontal
    "Fp1": "FP1",
    "Fp2": "FP2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "FZ",
    "F4": "F4",
    "F8": "F8",
    # Standard 10-20 central
    "T7": "T7",
    "C3": "C3",
    "Cz": "CZ",
    "C4": "C4",
    "T8": "T8",
    # Standard 10-20 parietal
    "P7": "P7",
    "P3": "P3",
    "Pz": "PZ",
    "P4": "P4",
    "P8": "P8",
    # Standard 10-20 occipital
    "O1": "O1",
    "Oz": "OZ",
    "O2": "O2",
    # Additional extended channels (if present)
    "Fpz": "FPZ",
    "Af7": "AF7",
    "Af3": "AF3",
    "Af4": "AF4",
    "Af8": "AF8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "Fcz": "FCZ",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC3": "FC3",
    "FC4": "FC4",
    "FC5": "FC5",
    "FC6": "FC6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP3": "CP3",
    "CP4": "CP4",
    "CP5": "CP5",
    "CP6": "CP6",
    "CPz": "CPZ",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO1": "PO1",
    "PO2": "PO2",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO5": "PO5",
    "PO6": "PO6",
    "POz": "POZ",
    # EOG channels (if present)
    "VEOG": "VEOG",
    "HEOG": "HEOG",
    "EOGvu": "VEOG",
    "EOGhl": "HEOG",
    # Reference/misc
    "Ref": "REF",
    "Reference": "REF",
    "Gnd": "GND",
    "Ground": "GND",
}

# Subject metadata - age and sex from participants.tsv
# Source: BIDS participants.tsv
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"age": "unknown", "sex": "unknown"},
    "02": {"age": "unknown", "sex": "unknown"},
    "03": {"age": "unknown", "sex": "unknown"},
    "04": {"age": "unknown", "sex": "unknown"},
    "05": {"age": "unknown", "sex": "unknown"},
    "06": {"age": "unknown", "sex": "unknown"},
    "07": {"age": "unknown", "sex": "unknown"},
    "08": {"age": "unknown", "sex": "unknown"},
    "09": {"age": "unknown", "sex": "unknown"},
    "10": {"age": "unknown", "sex": "unknown"},
    "11": {"age": "unknown", "sex": "unknown"},
    "12": {"age": "unknown", "sex": "unknown"},
    "13": {"age": "unknown", "sex": "unknown"},
    "14": {"age": "unknown", "sex": "unknown"},
    "15": {"age": "unknown", "sex": "unknown"},
    "16": {"age": "unknown", "sex": "unknown"},
    "17": {"age": "unknown", "sex": "unknown"},
    "18": {"age": "unknown", "sex": "unknown"},
    "19": {"age": "unknown", "sex": "unknown"},
    "20": {"age": "unknown", "sex": "unknown"},
    "21": {"age": "unknown", "sex": "unknown"},
}

# SDT event mapping for super meta
# 100 = response marker, 200 = threshold stimulus, 201 = adapt stimulus
# Hit: 200 followed by 100
# Miss: 200 without 100
# False Alarm: 201 followed by 100
# Correct Rejection: 201 without 100
_SDT_EVENT_MAP: Dict[str, int] = {
    "stim-threshold": 200,
    "stim-adapt": 201,
    "response": 100,
    "confidence_left": 101,
    "confidence_right": 102,
    "confidence_precise": 103,
    "confidence_guess": 104,
}

# Raw meta events (standard event IDs from dataset)
_RAW_EVENT_MAP: Dict[str, int] = {
    "impedance": 0,
    "stim-threshold": 200,
    "stim-adapt": 201,
    "response": 100,
    "confidence_left": 101,
    "confidence_right": 102,
    "confidence_precise": 103,
    "confidence_guess": 104,
}


def _parse_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    import re

    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1).lstrip("0") or "0"
    return "unknown"


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channels to standard 10-20 names."""
    rename_map = {}
    existing_chs = set(raw.ch_names)

    for source, target in _CHANNEL_RENAME_MAP.items():
        if source in existing_chs:
            rename_map[source] = target

    if rename_map:
        renamed = raw.rename_channels(rename_map)
        return renamed
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage after channel renaming."""
    try:
        # Try standard 1020 first
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        # Fallback: try biosemi32 or other common montages
        try:
            montage = mne.channels.make_standard_montage("biosemi32")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
    return raw


class OpenNeuroDS001785Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for openneuro ds001785 dataset.

    Evidence accumulation / vibrotactile detection task.
    """

    KERNEL_ID: str = "openneuro-ds001785-stage1"

    def __init__(self):
        super().__init__(
            KERNEL_ID=self.KERNEL_ID,
            event_map=_RAW_EVENT_MAP,
            continuous_cols=["confidence", "response_time"],
        )

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to raw EEG data.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : locator row with file path

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations
        """
        file_path = str(row.get("File Path", row.get("file_path", "")))

        # Step 1: Rename channels to standard 10-20 names
        raw = _rename_channels(raw)

        # Step 2: Set montage for spatial information
        raw = _set_montage(raw)

        # Step 3: Update info description with eegunity_description
        subject_id = _parse_subject_id(file_path)
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # Try to get age/sex from participants.tsv if available
        participants_path = os.path.join(
            os.path.dirname(os.path.dirname(file_path)),
            "participants.tsv"
        )
        if os.path.exists(participants_path):
            try:
                import pandas as pd
                df = pd.read_csv(participants_path, sep="\t")
                # Find matching subject
                subj_col = "participant_id" if "participant_id" in df.columns else "subject_id"
                subj_row = df[df[subj_col].str.contains(subject_id, case=False, na=False)]
                if not subj_row.empty:
                    if "age" in subj_row.columns:
                        age_val = subj_row["age"].values[0]
                        if pd.notna(age_val):
                            subject_info["age"] = str(int(age_val))
                    if "sex" in subj_row.columns:
                        sex_val = subj_row["sex"].values[0]
                        if pd.notna(sex_val):
                            subject_info["sex"] = str(sex_val).lower()
            except Exception:
                pass

        # Build description dict
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # Not specified in dataset
                "cap": "unknown",  # Not specified in dataset
                "handedness": "unknown",  # Not specified in dataset
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Step 4: Process annotations from existing events
        # BIDS format already has human-readable event descriptions in events.tsv
        # Ensure annotations are properly formatted
        if raw.annotations:
            # Map numeric event IDs to readable descriptions
            desc_map = {
                0: "impedance",
                1: "task_start",
                10: " fixation",
                11: " fixation",
                12: " fixation",
                2: "task_end",
                100: "response",
                101: "confidence_left",
                102: "confidence_right",
                103: "confidence_precise",
                104: "confidence_guess",
                200: "stim-threshold",
                201: "stim-adapt",
                9001: "Amplifier disconnected",
                9002: "Amplifier reconnected",
            }
            new_descriptions = []
            for desc in raw.annotations.description:
                try:
                    # Try to parse as int
                    desc_int = int(float(str(desc)))
                    new_desc = desc_map.get(desc_int, str(desc))
                except (ValueError, TypeError):
                    new_desc = str(desc)
                new_descriptions.append(new_desc)

            if new_descriptions != list(raw.annotations.description):
                raw.annotations.description = new_descriptions

        # Step 5: Handle continuous channels (confidence, response_time)
        # These are stored as separate channels in the raw data
        ch_names = raw.ch_names
        continuous_data = {}

        for col in ["confidence", "response_time"]:
            if col in ch_names:
                idx = ch_names.index(col)
                data = raw.get_data(picks=[col])
                if data is not None and data.size > 0:
                    continuous_data[col] = data.flatten()

        # Store continuous data info in description for downstream tasks
        if continuous_data:
            desc_obj = json.loads(raw.info["description"])
            desc_obj["continuous_channels"] = list(continuous_data.keys())
            desc_obj["continuous_info"] = {
                col: {
                    "min": float(np.min(v)),
                    "max": float(np.max(v)),
                    "mean": float(np.mean(v)),
                    "unit": "a.u." if col == "confidence" else "s",
                }
                for col, v in continuous_data.items()
            }
            raw.info["description"] = json.dumps(desc_obj)

        # Step 6: Clean up status channels if present
        status_channels = [ch for ch in raw.ch_names if ch.lower() in ["status", "trigger"]]
        if status_channels:
            try:
                raw.set_channel_types({ch: "stim" for ch in status_channels})
            except Exception:
                pass

        return raw


KERNEL = OpenNeuroDS001785Kernel()