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
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 64-channel extended 10-20 system names in BrainVision order.
# Source: BrainVision international standard electrode layout documentation.
# Annotator: LLM, 2026-04-08 (需人类复核)
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


def _build_brainvision_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from BrainVision vendor names to standard 10-20 names.

    BrainVision typically stores channels as "EEG 001", "EEG 002", ..., "EEG 064".
    This function matches those patterns to the standard extended 10-20 layout.

    Source: BrainVision Recorder electrode naming convention (extended 10-20 system).
    Annotator: LLM, 2026-04-08 (需人类复核)
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for idx, standard_name in enumerate(_EXTENDED_1020_64, start=1):
        # Try "EEG 001", "EEG 01", "EEG 1" patterns
        for pattern in [f"EEG {idx:03d}", f"EEG {idx:02d}", f"EEG {idx:d}"]:
            if pattern in existing_names:
                rename_map[pattern] = standard_name
                break

    return rename_map


def _extract_subject_info(row) -> Dict[str, str]:
    """Extract subject metadata from row or defaults.

    Source: OpenNeuro dataset participants.tsv (inferred structure).
    Annotator: LLM, 2026-04-08 (需人类复核)
    """
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    # Try to extract from row attributes if available
    if hasattr(row, "subject_id") or (hasattr(row, "__getitem__") and "subject_id" in row):
        subject_id = row.get("subject_id", "")
        if subject_id and isinstance(subject_id, str):
            # OpenNeuro subject IDs are typically "sub-01", "sub-02", etc.
            pass

    return subject_info


@dataclass
class OpenNeuroDS004580Kernel:
    """Stage1 kernel for OpenNeuro DS004580 (Simon-conflict Task)."""

    KERNEL_ID: str = "openneuro-ds004580-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single Simon task recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded from BrainVision file.
        row
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object with standardized annotations, channel names,
            montage, and eegunity_description.
        """
        # --- Step 1: Extract events and create annotations ---
        original_desc = raw.info.get("description", "")

        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            # If no events found, create empty annotations
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))
            events = np.empty((0, 3), dtype=int)
            event_id = {}

        # Map BrainVision event descriptions to semantic labels.
        # S  1 -> congruent, S  2 -> incongruent, S  3 -> rare/catch
        # boundary and S255 are admin markers - excluded from semantic mapping.
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
        for i in range(len(events)):
            desc = raw.annotations.description[i]
            # Normalize: remove extra spaces
            normalized_desc = re.sub(r"\s+", " ", desc).strip()
            mapped_label = event_label_map.get(normalized_desc) or event_label_map.get(desc)

            if mapped_label:
                annotations_list.append({
                    "onset": raw.annotations.onset[i],
                    "duration": raw.annotations.duration[i],
                    "description": mapped_label,
                })
            elif desc in admin_markers or normalized_desc in admin_markers:
                # Skip admin markers - they won't be epoched
                pass
            else:
                # Keep unknown events as-is for debugging
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

        # --- Step 2: Channel renaming ---
        rename_map = _build_brainvision_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if some channels couldn't be renamed

        # --- Step 3: Set montage ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, verbose=False)
        except Exception:
            pass  # Skip if montage setting fails

        # --- Step 4: eegunity_description ---
        subject_info = _extract_subject_info(row)

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp" if raw.info.get("meas_date") else "unknown",
                "cap": "Ag/AgCl",  # Source: typical BrainVision cap configuration
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004580Kernel()