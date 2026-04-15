"""Healthy Brain Network (HBN) EEG - Release 5 stage1 kernel for EEGUnity.

Dataset: openneuro_ds005509
Source: https://openneuro.org/datasets/ds005509
Reference: Alexander et al. (2017) Scientific Data, DOI:10.1038/sdata.2017.40

This kernel handles BIDS format data from the HBN study with 129-channel
EEG recordings at 500 Hz. It extracts subject metadata from participants.tsv,
maps raw event codes to human-readable event labels, and sets standard montage.

HBN paradigm summary:
  - Resting state (eyes open/closed)
  - Contrast detection (stim_ON, left/right targets, button presses)
  - Sequence learning
  - Symbol search
  - Surrounding suppression

Author: LLM (inferrer), 2026-04-08
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np


# ============================================================================
# CHANNEL MAPPING
# BioSemi 128-channel cap layout: ABC layout with 64 front + 64 back
# Standard 10-20 positions approximated for 129-channel system.
# Ref: HBN data description, BioSemi ActiveTwo configuration
# Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
# ============================================================================

_EEG129_CHANNEL_RENAME: Dict[str, str] = {
    # Standard 10-20 electrodes (29 channels)
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fz": "Fz",
    "F3": "F3",
    "F4": "F4",
    "F7": "F7",
    "F8": "F8",
    "Cz": "Cz",
    "C3": "C3",
    "C4": "C4",
    "T7": "T7",
    "T8": "T8",
    "Pz": "Pz",
    "P3": "P3",
    "P4": "P4",
    "P7": "P7",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    "POz": "POz",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO7": "PO7",
    "PO8": "PO8",
    "Iz": "Iz",
    "FT9": "FT9",
    "FT10": "FT10",
    # BioSemi extras / extended 10-20
    "AFz": "AFz",
    "AF3": "AF3",
    "AF4": "AF4",
    "AF7": "AF7",
    "AF8": "AF8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FCz": "FCz",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC3": "FC3",
    "FC4": "FC4",
    "FC5": "FC5",
    "FC6": "FC6",
    "CPz": "CPz",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP3": "CP3",
    "CP4": "CP4",
    "CP5": "CP5",
    "CP6": "CP6",
    "TP9": "TP9",
    "TP10": "TP10",
    "M-left": "M-left",
    "M-right": "M-right",
    "M1": "M1",
    "M2": "M2",
    # Common alternate names in BioSemi data
    "A1": "M1",
    "A2": "M2",
    "TP7": "TP7",
    "TP8": "TP8",
    "P9": "P9",
    "P10": "P10",
    "F9": "F9",
    "F10": "F10",
    "P1": "P1",
    "P2": "P2",
}


# ============================================================================
# EVENT CODE MAPPING
# HBN uses BIOSEMI event codes embedded in raw annotations or events.tsv.
# Ref: HBN events.tsv documentation, Alexander et al. (2017)
# Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
# ============================================================================

_EVENT_CODE_MAP: Dict[int, str] = {
    1: "fixpoint_ON",
    2: "stim_ON",
    3: "left_target",
    4: "right_target",
    5: "left_buttonPress",
    6: "right_buttonPress",
    7: "contrastTrial_start",
    8: "trialResponse",
    11: "instructed_toOpenEyes",
    12: "instructed_toCloseEyes",
    13: "resting_start",
    15: "break cnt",
    16: "boundary",
    9999: "9999",
}


def _detect_hbn_event_description(raw: mne.io.BaseRaw) -> None:
    """Inspect raw annotations and detect HBN event encoding format.

    HBN events appear either as:
      1. Numeric codes in raw.annotations (BIOSEMI default)
      2. Strings in events.tsv (BIDS formatted)

    This helper examines the raw.annotations and rebuilds them with
    canonical event names if numeric codes are detected.

    Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
    """
    annotations = raw.annotations
    if annotations is None or len(annotations) == 0:
        return

    # Check if descriptions look like numeric codes
    sample_desc = annotations.description[0] if len(annotations) > 0 else ""
    if isinstance(sample_desc, (int, float)):
        # Numeric codes detected — remap
        new_descriptions = []
        for desc in annotations.description:
            desc_int = int(desc) if not isinstance(desc, str) else desc
            mapped = _EVENT_CODE_MAP.get(desc_int, str(desc_int))
            new_descriptions.append(mapped)
        raw.set_annotations(
            mne.Annotations(
                onset=annotations.onset,
                duration=annotations.duration,
                description=new_descriptions,
            )
        )


def _get_subject_metadata(udataset, row) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.

    Attempts to read age and sex from the BIDS participants.tsv file.
    Falls back to 'unknown' if fields are missing.

    Returns
    -------
    dict with keys: age, sex, handedness (all strings)

    Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
    """
    result = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    if udataset is None or not hasattr(udataset, "dataset_path"):
        return result

    dataset_path = getattr(udataset, "dataset_path", "")
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    if not os.path.exists(participants_tsv):
        return result

    try:
        import pandas as pd

        df = pd.read_csv(participants_tsv, sep="\t")
        subject_id = row.get("subject_id") or row.get("participant_id") or ""

        # Normalize subject ID: sub-XXX or just XXX
        if subject_id.startswith("sub-"):
            subject_id = subject_id.replace("sub-", "")
        elif subject_id.startswith("sub_"):
            subject_id = subject_id.replace("sub_", "")

        # Try to find matching row
        id_col = None
        for col in ["participant_id", "subject_id", "participant"]:
            if col in df.columns:
                id_col = col
                break

        if id_col is not None:
            # Normalize participant IDs in df
            df_ids = df[id_col].str.replace("sub-", "", regex=False).str.replace(
                "sub_", "", regex=False
            )
            match = df[df_ids == subject_id]
            if len(match) == 0 and subject_id:
                # Try exact match without normalization
                match = df[df[id_col] == subject_id]

            if len(match) > 0:
                row_data = match.iloc[0]

                # Extract age
                if "age" in df.columns:
                    age_val = row_data.get("age", "unknown")
                    if age_val != "unknown" and not pd.isna(age_val):
                        result["age"] = str(int(float(age_val)))

                # Extract sex
                if "sex" in df.columns:
                    sex_val = str(row_data.get("sex", "")).strip().lower()
                    if sex_val in ("m", "male"):
                        result["sex"] = "male"
                    elif sex_val in ("f", "female"):
                        result["sex"] = "female"
                    else:
                        result["sex"] = "unknown"

                # Extract handedness
                if "handedness" in df.columns:
                    hand_val = str(row_data.get("handedness", "")).strip().lower()
                    if hand_val in ("r", "right"):
                        result["handedness"] = "right"
                    elif hand_val in ("l", "left"):
                        result["handedness"] = "left"
                    else:
                        result["handedness"] = "unknown"

    except Exception:
        pass

    return result


def _apply_channel_renaming(raw: mne.io.BaseRaw) -> None:
    """Rename EEG channels to standard 10-20 names where applicable.

    Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
    """
    rename_map = {}
    existing = set(raw.ch_names)

    for target, source in _EEG129_CHANNEL_RENAME.items():
        if source in existing:
            if source != target:
                rename_map[source] = target

    if rename_map:
        mne.rename_channels(raw.info, rename_map)


class HBNStage1Kernel:
    """Stage1 kernel for the HBN EEG dataset (openneuro_ds005509).

    This kernel:
      1. Reads subject metadata from participants.tsv
      2. Remaps BIOSEMI event codes to canonical event names
      3. Renames EEG channels to standard 10-20 nomenclature
      4. Sets standard montage for spatial reference

    KERNEL_ID: hbn-eeg-stage1
    """

    KERNEL_ID: str = "hbn-eeg-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "") if hasattr(row, "get") else ""

        # --- Detect and remap event codes ---
        _detect_hbn_event_description(raw)

        # --- Extract subject metadata ---
        subject_meta = _get_subject_metadata(udataset, row)

        # --- Set EEGUnity description ---
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, bytes):
            original_desc = original_desc.decode("utf-8", errors="replace")

        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": "BioSemi ActiveTwo",  # Ref: HBN data description
                "cap": "BioSemi 128-channel (Ag/AgCl)",  # Ref: HBN data description
                "handedness": subject_meta["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # --- Rename channels before setting montage ---
        _apply_channel_renaming(raw)

        # --- Set standard montage (10-20 system) ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass

        return raw


KERNEL = HBNStage1Kernel()