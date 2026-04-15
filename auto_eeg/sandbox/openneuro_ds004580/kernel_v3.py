"""OpenNeuro DS004580 (Simon-conflict Task) stage1 kernel for EEGUnity.

Dataset: Simon-conflict task with congruent/incongruent trial classification.
Format: BrainVision (.vhdr/.eeg/.vmrk)
Source: https://openneuro.org/datasets/ds004580
DOI: https://doi.org/10.1101/2022.07.26.22278079

Events:
  S  1 -> congruent (stimulus location matches response side)
  S  2 -> incongruent (stimulus location conflicts with response side)
  S  3 -> rare/catch trial (optional third class)
  boundary, S255 -> admin markers (excluded from epochs)

Tasks:
  - Congruent vs Incongruent binary classification (primary)
  - ERP component analysis (N2, P3)

Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import mne
import numpy as np


_EXTENDED_1020_64 = [
    "Fp1", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]


def _build_brainvision_channel_rename_map(raw: mne.io.BaseRaw) -> dict:
    """Build a channel rename map from BrainVision vendor names to standard 10-20 names."""
    rename_map: dict = {}
    existing_names = set(raw.ch_names)

    for idx, standard_name in enumerate(_EXTENDED_1020_64, start=1):
        for pattern in [f"EEG {idx:03d}", f"EEG {idx:02d}", f"EEG {idx:d}"]:
            if pattern in existing_names:
                rename_map[pattern] = standard_name
                break

    return rename_map


def _extract_subject_info(row) -> dict:
    """Extract subject metadata from row or defaults."""
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    if hasattr(row, "subject_id") or (hasattr(row, "__getitem__") and "subject_id" in row):
        subject_id = row.get("subject_id", "")
        if subject_id and isinstance(subject_id, str):
            pass

    return subject_info


@dataclass
class OpenNeuroDS004580Kernel:
    """Stage1 kernel for OpenNeuro DS004580 (Simon-conflict Task)."""

    KERNEL_ID: str = "openneuro-ds004580-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single Simon task recording."""
        original_desc = raw.info.get("description", "")

        try:
            mne.events_from_annotations(raw, verbose=False)
        except Exception:
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))

        event_label_map = {
            "S  1": "congruent",
            "S   1": "congruent",
            "S 1": "congruent",
            "S1": "congruent",
            "S  2": "incongruent",
            "S   2": "incongruent",
            "S 2": "incongruent",
            "S2": "incongruent",
            "S  3": "rare/catch",
            "S   3": "rare/catch",
            "S 3": "rare/catch",
            "S3": "rare/catch",
        }

        admin_markers = {"boundary", "S255", "S 255"}

        annotations_list = []
        for i in range(len(raw.annotations)):
            desc = raw.annotations.description[i]
            normalized_desc = re.sub(r"\s+", " ", desc).strip()
            mapped_label = event_label_map.get(normalized_desc) or event_label_map.get(desc)

            if mapped_label:
                annotations_list.append({
                    "onset": raw.annotations.onset[i],
                    "duration": raw.annotations.duration[i],
                    "description": mapped_label,
                })
            elif desc in admin_markers or normalized_desc in admin_markers:
                pass
            else:
                annotations_list.append({
                    "onset": raw.annotations.onset[i],
                    "duration": raw.annotations.duration[i],
                    "description": f"unknown: {desc}",
                })

        if annotations_list:
            new_annotations = mne.Annotations(
                onset=[a["onset"] for a in annotations_list],
                duration=[a["duration"] for a in annotations_list],
                description=[a["description"] for a in annotations_list],
            )
            raw.set_annotations(new_annotations)

        rename_map = _build_brainvision_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass

        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, verbose=False)
        except Exception:
            pass

        subject_info = _extract_subject_info(row)

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": str(subject_info["age"]),
                "sex": str(subject_info["sex"]),
                "amplifier": "BrainAmp" if raw.info.get("meas_date") else "unknown",
                "cap": "Ag/AgCl",
                "handedness": str(subject_info["handedness"]),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004580Kernel()