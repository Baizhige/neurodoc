"""OpenNeuro DS006839 stage1 kernel for EEGUnity.

EEG recordings during sham neurofeedback in virtual reality.
Dataset: 144 subjects, 29 channels, 1000 Hz.

Event mapping (BIDS scan / events.tsv):
    "Stimulus/S  1" -> trial onset / block start
    "Stimulus/S  2" -> positive sham neurofeedback condition
    "Stimulus/S  3" -> negative sham neurofeedback condition
    "Stimulus/S  4" -> control (neutral) feedback condition
    "Stimulus/S  5" -> null/reset event (admin, exclude)

Source: https://doi.org/10.18112/openneuro.ds006839.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Channel rename map (standard_1020 based on 29-channel VR setup)
# Source: Dataset README / paper reference (DOI: 10.3389/fnins.2025.1476264)
# Annotator: LLM, 2026-04-08
# Note: inferred by LLM, needs human review - confirm exact channel layout from official cap layout
# =============================================================================
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "FC5": "FC5",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC6": "FC6",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "CP5": "CP5",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP6": "CP6",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "EOG1": "EOG1",
    "EOG2": "EOG2",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names in raw data."""
    rename_map: Dict[str, str] = {}
    existing_chs = set(raw.ch_names)

    for standard_name, aliases in _EEG_CHANNEL_RENAME_MAP.items():
        if standard_name in existing_chs:
            continue
        for alias in aliases if isinstance(aliases, list) else [aliases]:
            if alias in existing_chs and alias != standard_name:
                rename_map[alias] = standard_name
                break

    return rename_map


def _load_subject_info(row: Any, dataset_root: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv.

    Returns a dict with keys: age, sex, handedness.
    Amplifier/cap are hardcoded based on dataset documentation.
    """
    subject_id = row.get("Subject", row.get("participant_id", "unknown"))

    # Try to read participants.tsv
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    subject_info: Dict[str, str] = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Match subject ID column (may be participant_id or sub-XXX format)
            id_col = None
            for col in ["participant_id", "Subject ID", "subject_id"]:
                if col in df.columns:
                    id_col = col
                    break
            if id_col is None:
                id_col = df.columns[0]

            # Try exact match or stripped match
            subj_row = df[df[id_col].astype(str).str.strip() == str(subject_id).strip()]
            if subj_row.empty and str(subject_id).startswith("sub-"):
                subj_row = df[df[id_col].astype(str).str.contains(str(subject_id)[4:], na=False)]

            if not subj_row.empty:
                first_row = subj_row.iloc[0]
                # Age
                age_val = first_row.get("age", "unknown")
                if age_val != "unknown" and not pd.isna(age_val):
                    subject_info["age"] = str(int(float(age_val)))
                # Sex
                sex_val = str(first_row.get("sex", "unknown")).lower().strip()
                if sex_val in ["m", "male"]:
                    subject_info["sex"] = "male"
                elif sex_val in ["f", "female"]:
                    subject_info["sex"] = "female"
                else:
                    subject_info["sex"] = "unknown"
                # Handedness
                hand_val = str(first_row.get("hand", first_row.get("handedness", "unknown"))).lower().strip()
                if "right" in hand_val:
                    subject_info["handedness"] = "right"
                elif "left" in hand_val:
                    subject_info["handedness"] = "left"
                else:
                    subject_info["handedness"] = "unknown"
        except Exception:
            pass

    return subject_info


def _remap_stimulus_events(raw: mne.io.BaseRaw) -> None:
    """Remap Stimulus/S N annotations to human-readable descriptions.

    Mapping:
        "Stimulus/S  1" -> trial onset
        "Stimulus/S  2" -> positive feedback
        "Stimulus/S  3" -> negative feedback
        "Stimulus/S  4" -> control feedback
        "Stimulus/S  5" -> null/reset event
    """
    stim_mapping = {
        "Stimulus/S  1": "trial onset",
        "Stimulus/S  2": "positive feedback",
        "Stimulus/S  3": "negative feedback",
        "Stimulus/S  4": "control feedback",
        "Stimulus/S  5": "null/reset event",
    }

    if raw.annotations is None or len(raw.annotations) == 0:
        return

    descriptions = list(raw.annotations.description)
    new_descriptions = []
    for desc in descriptions:
        desc_stripped = str(desc).strip()
        new_desc = stim_mapping.get(desc_stripped, desc_stripped)
        new_descriptions.append(new_desc)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)


class OpenNeuroDS006839Kernel:
    """Stage1 kernel for OpenNeuro DS006839 (Sham Neurofeedback in VR)."""

    KERNEL_ID: str = "openneuro-ds006839-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw, in-memory raw EEG data
        row : locator row with file path and metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated description and annotations.
        """
        # Determine dataset root from row or udataset
        dataset_root = ""
        if hasattr(udataset, "root_path"):
            dataset_root = getattr(udataset, "root_path", "")
        elif hasattr(row, "get"):
            dataset_root = row.get("Dataset Root", row.get("dataset_root", ""))

        # -------------------------------------------------------------------------
        # Step 1: Channel rename (before set_montage)
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[DS006839] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # -------------------------------------------------------------------------
        # Step 2: Set standard 10-20 montage if applicable
        # -------------------------------------------------------------------------
        try:
            standard_montage = mne.channels.make_standard_montage("standard_1020")
            existing_for_montage = [ch for ch in raw.ch_names if ch in standard_montage.ch_names]
            if len(existing_for_montage) >= 10:
                raw.set_montage(standard_montage, on_missing="warn")
        except Exception as e:
            print(f"[DS006839] Montage warning: {e}")

        # -------------------------------------------------------------------------
        # Step 3: Load subject metadata
        # -------------------------------------------------------------------------
        subject_info = _load_subject_info(row, dataset_root)

        # -------------------------------------------------------------------------
        # Step 4: Update info["description"] with eegunity_description
        # -------------------------------------------------------------------------
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                # Amplifier/cap from dataset documentation (VR EEG system)
                # Source: OpenNeuro DS006839 README / hardware specs
                # Annotator: LLM, 2026-04-08
                "amplifier": "unknown",  # inferred by LLM, needs human review
                "cap": "unknown",       # inferred by LLM, needs human review
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # Step 5: Remap stimulus events to human-readable labels
        # -------------------------------------------------------------------------
        _remap_stimulus_events(raw)

        return raw


KERNEL = OpenNeuroDS006839Kernel()