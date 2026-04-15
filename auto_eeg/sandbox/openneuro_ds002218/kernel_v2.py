"""OpenNeuro ds002218 stage1 kernel for EEGUnity.

Auditory and Visual Rhythm Omission EEG dataset.
32 channels, 256 Hz, BioSemi amplifier.
Paradigm: rhythmic tones and flashes with occasional omissions.

Event mapping (hypothesized from event counts, requires validation):
  - 2: tone_non-omission (2520 events)
  - 4: tone_omission (2520 events)
  - 5: flash_non-omission (2520 events)
  - 6: flash_omission (2520 events)

Source: https://openneuro.org/datasets/ds002218
Reference: DOI 10.1111/ejn.15314
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Hypothesized event mapping based on analysis.md event counts
# Each stimulus type has exactly 2520 events per the dataset structure
# Annotator: LLM, 2026-04-08, requires human validation against events.tsv
_EVENT_MAP: Dict[int, str] = {
    2: "tone_non-omission",
    4: "tone_omission",
    5: "flash_non-omission",
    6: "flash_omission",
}

# BioSemi standard 32-channel layout (ActiCAP 32ch)
# Standard 1020 system with 32 electrode positions
# Annotator: LLM, 2026-04-08, inferred from BioSemi standard montage
_32CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-Fp1": "Fp1",
    "EEG-Fp2": "Fp2",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-Fz": "Fz",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-T7": "T7",
    "EEG-C3": "C3",
    "EEG-Cz": "Cz",
    "EEG-C4": "C4",
    "EEG-T8": "T8",
    "EEG-P7": "P7",
    "EEG-P3": "P3",
    "EEG-Pz": "Pz",
    "EEG-P4": "P4",
    "EEG-P8": "P8",
    "EEG-O1": "O1",
    "EEG-Oz": "Oz",
    "EEG-O2": "O2",
    "EEG-FC1": "FC1",
    "EEG-FC2": "FC2",
    "EEG-FC5": "FC5",
    "EEG-FC6": "FC6",
    "EEG-CP1": "CP1",
    "EEG-CP2": "CP2",
    "EEG-CP5": "CP5",
    "EEG-CP6": "CP6",
    "EEG-FT9": "FT9",
    "EEG-FT10": "FT10",
    "EEG-TP9": "TP9",
    "EEG-TP10": "TP10",
}


def _load_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Load events.tsv from BIDS structure."""
    events_path = file_path.replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv")
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t", encoding="latin-1")
    return None


def _build_annotations_from_events_tsv(
    raw: mne.io.BaseRaw, events_df: pd.DataFrame, event_map: Dict[int, str]
) -> mne.Annotations:
    """Build MNE annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return raw.annotations

    onset_list = []
    duration_list = []
    description_list = []

    for _, row in events_df.iterrows():
        if "value" in row.index and "trial_type" in row.index:
            event_val = row.get("value", None)
            trial_type = row.get("trial_type", "")
            
            if pd.notna(event_val):
                event_int = int(float(event_val))
                if event_int in event_map:
                    onset_list.append(float(row["onset"]))
                    duration_list.append(float(row.get("duration", 0)))
                    description_list.append(event_map[event_int])
                elif trial_type and str(trial_type).strip():
                    onset_list.append(float(row["onset"]))
                    duration_list.append(float(row.get("duration", 0)))
                    description_list.append(str(trial_type))

    if onset_list:
        return mne.Annotations(
            onset=np.array(onset_list),
            duration=np.array(duration_list),
            description=np.array(description_list),
        )
    return raw.annotations


def _apply_channel_renames(raw: mne.io.BaseRaw, rename_map: Dict[str, str]) -> mne.io.BaseRaw:
    """Rename EEG channels to standard 1020 names."""
    existing_renames = {}
    for old_name, new_name in rename_map.items():
        if old_name in raw.ch_names:
            existing_renames[old_name] = new_name

    if existing_renames:
        raw.rename_channels(existing_renames)
    return raw


def _get_subject_info(udataset, row) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv."""
    subject_id = row.get("participant_id", "")
    age = "unknown"
    sex = "unknown"
    handedness = "unknown"

    participants_path = os.path.join(os.path.dirname(row.get("File Path", "")), "..", "..", "participants.tsv")
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t", encoding="latin-1")
            subject_row = df[df["participant_id"] == subject_id]
            if not subject_row.empty:
                age_val = subject_row.iloc[0].get("age", "unknown")
                sex_val = subject_row.iloc[0].get("sex", "unknown")
                hand_val = subject_row.iloc[0].get("handedness", "unknown")

                if pd.notna(age_val):
                    age = str(int(float(age_val)))
                if pd.notna(sex_val):
                    sex = str(sex_val).lower().strip()
                    if sex not in ["male", "female", "unknown"]:
                        sex = "unknown"
                if pd.notna(hand_val):
                    handedness = str(hand_val).lower().strip()
        except Exception:
            pass

    return {
        "age": age,
        "sex": sex,
        "handedness": handedness,
    }


class OpenNeuroDS002218Kernel:
    """Stage1 kernel for OpenNeuro ds002218 dataset."""

    KERNEL_ID: str = "openneuro-ds002218-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (BioSemi EDF/BDF)
        row : pandas Series with file metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized events and metadata
        """
        original_description = raw.info.get("description", "")

        # Step 1: Apply channel renaming before set_montage
        raw = _apply_channel_renames(raw, _32CHANNEL_RENAME_MAP)

        # Step 2: Set standard 1020 montage (BioSemi 32ch standard)
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass

        # Step 3: Extract subject metadata
        subject_info = _get_subject_info(udataset, row)

        # Step 4: Load events from events.tsv and build annotations
        events_df = _load_events_tsv(row.get("File Path", ""))
        annotations = _build_annotations_from_events_tsv(raw, events_df, _EVENT_MAP)
        raw.set_annotations(annotations)

        # Step 5: Write eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BioSemi",
                "cap": "Ag/AgCl",
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS002218Kernel()