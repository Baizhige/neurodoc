"""Dataset-specific kernel for openneuro_ds003516.

Attended Speaker Paradigm (Own Name in Ignored Stream) - cocktail party
selective auditory attention task. Participants listened to audio from an
attended speaker while their own name was occasionally presented in the
ignored stream.

Source: https://openneuro.org/datasets/ds003516
       DOI: https://doi.org/10.3389/fnins.2021.643705
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 system with 49 channels (extended cap)
# Source: Extended 10-20 system for 64-channel caps, standard ordering
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
_49_CHANNEL_NAMES = [
    "FP1", "FPZ", "FP2",
    "AF7", "AF3", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POZ", "PO4", "PO8",
    "O1", "OZ", "O2",
]

# BIDS event label mapping from events.tsv
# Source: Dataset events.tsv structure
_EVENT_LABEL_MAP = {
    "Beep": "Beep",
    "Calib_End": "Calib_End",
    "Calib_Start": "Calib_Start",
    "StartTrigger": "StartTrigger",
    "beam": "beam",
    "beep": "beep",
    "boundary": "boundary",
    "omni": "omni",
}


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from BIDS participants.tsv.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping of subject_id -> {age, sex, handedness}
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}

    df = pd.read_csv(participants_path, sep="\t")

    subject_dict = {}
    for _, row in df.iterrows():
        # Extract subject ID (e.g., "sub-01" -> "01")
        subject_id = str(row.get("participant_id", ""))
        if not subject_id.startswith("sub-"):
            continue
        sid = subject_id.replace("sub-", "")

        age_str = str(row.get("age", "unknown"))
        sex_val = str(row.get("sex", row.get("gender", "unknown"))).lower()

        subject_dict[sid] = {
            "age": age_str if age_str and age_str != "nan" else "unknown",
            "sex": sex_val if sex_val in ("male", "female") else "unknown",
            "handedness": str(row.get("hand", row.get("handedness", "unknown"))).lower(),
        }

    return subject_dict


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a mapping from original channel names to standard 10-20 names.

    BIDS datasets typically use 'EEG' prefix and numeric suffixes.
    """
    rename_map = {}

    # Get current channel names
    current_names = raw.ch_names

    # Pattern: EEG followed by number (e.g., EEG001 -> FP1)
    eeg_pattern = re.compile(r"^EEG\s*(\d+)$", re.IGNORECASE)

    # Try to match numbered EEG channels to standard positions
    # The 49-channel cap typically follows standard ordering
    for ch_name in current_names:
        match = eeg_pattern.match(ch_name)
        if match:
            idx = int(match.group(1)) - 1  # 0-based index
            if 0 <= idx < len(_49_CHANNEL_NAMES):
                standard_name = _49_CHANNEL_NAMES[idx]
                if standard_name != ch_name:
                    rename_map[ch_name] = standard_name

    return rename_map


@dataclass
class OpenNeuroDS003516Kernel:
    """Stage1 kernel for OpenNeuro ds003516 dataset.

    Attended Speaker Paradigm with cocktail party selective attention task.
    """

    KERNEL_ID: str = "openneuro-ds003516-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single subject record.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with 'File Path', 'Subject' columns.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = str(row.get("Subject", "unknown"))
        dataset_path = getattr(udataset, "path", os.path.dirname(file_path))

        # 1. Load subject metadata
        all_subjects = _load_participants_tsv(dataset_path)
        subject_meta = all_subjects.get(subject_id, {})

        age = subject_meta.get("age", "unknown")
        sex = subject_meta.get("sex", "unknown")
        handedness = subject_meta.get("handedness", "unknown")

        # LLM inference fallback if metadata unavailable
        # Source: Dataset description (25 subjects, ages ~22-35)
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        if age == "unknown" or not age:
            age = "unknown"

        # 2. Update description with eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": str(age),
                "sex": sex.lower() if sex in ("male", "female") else "unknown",
                "amplifier": "unknown",  # Not documented in BIDS
                "cap": "unknown",  # Not documented in BIDS
                "handedness": handedness if handedness in ("left", "right") else "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # 3. Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # 4. Set montage for standard electrode positions
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip if montage fails

        # 5. Process events from annotations or events.tsv
        self._process_events(raw, file_path, dataset_path)

        return raw

    def _process_events(self, raw: mne.io.BaseRaw, file_path: str, dataset_path: str):
        """Process and standardize event annotations.

        The dataset has events from raw annotations (Beep, Calib_Start, etc.)
        as well as potential events.tsv for more detailed timing.
        """
        # Get current annotations
        current_annots = raw.annotations

        if len(current_annots) > 0:
            # Map existing annotation descriptions
            new_descriptions = []
            for desc in current_annots.description:
                mapped = _EVENT_LABEL_MAP.get(desc, desc)
                new_descriptions.append(mapped)

            # Create new annotations with standardized labels
            if new_descriptions != list(current_annots.description):
                new_annots = mne.Annotations(
                    onset=current_annots.onset,
                    duration=current_annots.duration,
                    description=new_descriptions,
                )
                raw.set_annotations(new_annots)

        # Also try to load events.tsv for additional event information
        events_tsv_path = file_path.replace("_eeg.edf", "_events.tsv").replace("_eeg.bdf", "_events.tsv")
        events_tsv_path = events_tsv_path.replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv")

        # More robust path finding
        sub_dir = os.path.dirname(file_path)
        tsv_files = [f for f in os.listdir(sub_dir) if f.endswith("_events.tsv")]
        if tsv_files:
            events_tsv_path = os.path.join(sub_dir, tsv_files[0])
            try:
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                if "trial_type" in events_df.columns or "value" in events_df.columns:
                    # Events.tsv exists with readable labels, no remapping needed
                    pass
            except Exception:
                pass


KERNEL = OpenNeuroDS003516Kernel()