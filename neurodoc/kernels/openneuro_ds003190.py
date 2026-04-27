"""OpenNeuro ds003190 stage1 kernel for EEGUnity.

P300 ERP experiment evaluating visual stimuli properties.
9-channel EEG, 256 Hz sampling rate, 19 subjects.
Standard 10-20 montage.

Source: https://openneuro.org/datasets/ds003190
DOI: 10.18112/openneuro.ds003190.v1.0.1
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Dataset documentation and analysis.md
# 9-channel standard 10-20 system for P300 paradigm
_STANDARD_1020_CHANNELS = [
    "Fp1",
    "Fp2",
    "Fz",
    "Cz",
    "Pz",
    "O1",
    "O2",
    "T7",
    "T8",
]


def _try_rename_standard_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to rename channels to standard 10-20 names if they are numeric or nonstandard.

    Source: LLM inference based on 9-channel P300 paradigm literature, needs human review.
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    for i, ch in enumerate(raw.ch_names):
        ch_upper = ch.upper()
        ch_lower = ch.lower()

        if ch_upper in _STANDARD_1020_CHANNELS:
            continue
        if ch_lower in [c.lower() for c in _STANDARD_1020_CHANNELS]:
            continue

        if ch.isdigit():
            idx = int(ch)
            if idx < len(_STANDARD_1020_CHANNELS):
                rename_map[ch] = _STANDARD_1020_CHANNELS[idx]

        elif ch.startswith("EEG-") or ch.startswith("eeg-"):
            suffix = ch.split("-")[-1]
            if suffix.isdigit():
                idx = int(suffix)
                if idx < len(_STANDARD_1020_CHANNELS):
                    rename_map[ch] = _STANDARD_1020_CHANNELS[idx]

        elif ch.startswith("CH") or ch.startswith("ch"):
            suffix = ch[2:]
            if suffix.isdigit():
                idx = int(suffix)
                if idx < len(_STANDARD_1020_CHANNELS):
                    rename_map[ch] = _STANDARD_1020_CHANNELS[idx]

    if rename_map:
        try:
            raw.rename_channels(rename_map, verbose=False)
        except Exception:
            pass

    return raw


def _try_set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard 10-20 montage if all channels are standard names.

    Source: LLM inference based on 9-channel P300 paradigm, needs human review.
    Annotator: LLM, 2026-04-08
    """
    try:
        standard_names_lower = [c.lower() for c in _STANDARD_1020_CHANNELS]
        existing_lower = [c.lower() for c in raw.ch_names]

        all_standard = all(c in standard_names_lower for c in existing_lower)

        if all_standard or len(raw.ch_names) >= 9:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, verbose=False)
    except Exception:
        pass

    return raw


@dataclass
class OpenNeuroDS003190Kernel:
    """Stage1 kernel for OpenNeuro ds003190 P300 ERP dataset."""

    KERNEL_ID: str = "openneuro-ds003190-stage1"

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
            Preprocessed MNE Raw object.
        """
        original_desc = raw.info.get("description", "")

        age = "unknown"  # LLM 推断，需人类复核
        sex = "unknown"  # LLM 推断，需人类复核
        amplifier = "unknown"  # LLM 推断，需人类复核
        cap = "unknown"  # LLM 推断，需人类复核
        handedness = "unknown"  # LLM 推断，需人类复核

        try:
            file_path = row.get("File Path", "")
            if file_path and os.path.exists(file_path):
                dataset_root = os.path.dirname(os.path.dirname(file_path))

                participants_tsv = os.path.join(dataset_root, "participants.tsv")
                if os.path.exists(participants_tsv):
                    df = pd.read_csv(participants_tsv, sep="\t")
                    if "participant_id" in df.columns and "age" in df.columns:
                        subject_id = row.get("subject_id", "")
                        if subject_id:
                            subject_row = df[df["participant_id"] == subject_id]
                            if len(subject_row) > 0:
                                age_val = subject_row.iloc[0].get("age", "unknown")
                                if age_val and str(age_val).lower() != "n/a":
                                    age = str(age_val)

                    if "participant_id" in df.columns and "sex" in df.columns:
                        if subject_id:
                            subject_row = df[df["participant_id"] == subject_id]
                            if len(subject_row) > 0:
                                sex_val = subject_row.iloc[0].get("sex", "unknown")
                                if sex_val and str(sex_val).lower() not in ["n/a", ""]:
                                    sex_lower = str(sex_val).lower()
                                    if sex_lower in ["m", "male"]:
                                        sex = "male"
                                    elif sex_lower in ["f", "female"]:
                                        sex = "female"
                                    else:
                                        sex = "unknown"

                sidecar_json = os.path.join(os.path.dirname(file_path), "*.json")
                import glob
                json_files = glob.glob(sidecar_json)
                if json_files:
                    for json_file in json_files:
                        try:
                            with open(json_file, "r") as f:
                                sidecar = json.load(f)
                                if "EEGReference" in sidecar:
                                    ref = sidecar["EEGReference"]
                                    if ref and "activemark" not in str(ref).lower():
                                        pass
                                if "HardwareFilters" in sidecar:
                                    pass
                        except Exception:
                            pass
        except Exception:
            pass

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        raw = _try_rename_standard_channels(raw)

        try:
            raw = _try_set_montage(raw)
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS003190Kernel()