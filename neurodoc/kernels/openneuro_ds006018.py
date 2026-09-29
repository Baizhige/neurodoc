"""openneuro_ds006018 stage1 kernel for EEGUnity.

ERP CORE paradigm EEG dataset: 127 young adults performing standardized ERP tasks
(N170, MMN, N2pc, P3, N400, ERN, LRP).

Source: https://openneuro.org/datasets/ds006018
Reference: Kappenman et al. (2021) ERP CORE; DOI: 10.1038/s41597-025-05209-z
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Channel Mapping (Standard 32-channel ERP CORE cap)
# =============================================================================
# Source: ERP CORE electrode layout (Kappenman et al. 2021, Neuroimage)
# 31 EEG channels + 4 EOG channels → standard 1020 montage
# Annotator: LLM, 2026-04-08,
_EEG_CHANNEL_RENAME_MAP = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fz": "Fz",
    "F3": "F3",
    "F4": "F4",
    "F7": "F7",
    "F8": "F8",
    "FCz": "FCz",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC5": "FC5",
    "FC6": "FC6",
    "Cz": "Cz",
    "C3": "C3",
    "C4": "C4",
    "CPz": "CPz",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP5": "CP5",
    "CP6": "CP6",
    "Pz": "Pz",
    "P3": "P3",
    "P4": "P4",
    "P7": "P7",
    "P8": "P8",
    "POz": "POz",
    "PO7": "PO7",
    "PO8": "PO8",
    "O1": "O1",
    "O2": "O2",
    "CB1": "CB1",
}

# Standard 32-channel montage positions for ERP CORE
_STANDARD_32_MONTAGE = [
    "Fp1", "Fp2", "Fz", "F3", "F4", "F7", "F8",
    "FC1", "FC2", "FCz", "FC5", "FC6",
    "Cz", "C3", "C4",
    "CP1", "CP2", "CPz", "CP5", "CP6",
    "Pz", "P3", "P4", "P7", "P8",
    "POz", "PO7", "PO8", "O1", "O2", "CB1", "CB2",
]


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if present."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        df = pd.read_csv(participants_path, sep="\t")
        return df
    return pd.DataFrame()


def _get_subject_info(row: Dict[str, Any], dataset_root: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or defaults."""
    subject_id = row.get("subject_id", row.get("Subject", "unknown"))

    # Try to get from participants.tsv
    participants_df = _load_participants_tsv(dataset_root)
    if not participants_df.empty:
        # Match subject ID format (sub-XX or just XX)
        subj_col = "participant_id" if "participant_id" in participants_df.columns else None
        if subj_col:
            match = participants_df[participants_df[subj_col] == subject_id]
            if match.empty:
                # Try with "sub-" prefix
                match = participants_df[participants_df[subj_col] == f"sub-{subject_id}"]

            if not match.empty:
                row_data = match.iloc[0]
                age = str(int(row_data.get("age", 0))) if pd.notna(row_data.get("age")) else "unknown"
                sex = str(row_data.get("sex", "unknown")).lower()
                if sex not in ("male", "female"):
                    sex = "unknown"
                return {
                    "age": age,
                    "sex": sex,
                    "handedness": str(row_data.get("hand", row_data.get("handedness", "unknown"))).lower(),
                }

    # Default values when not found
    return {
        "age": "unknown",  # inferred by LLM, needs human review
        "sex": "unknown",  # inferred by LLM, needs human review
        "handedness": "unknown",  # inferred by LLM, needs human review
    }


def _apply_channel_rename(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 1020 names if needed."""
    rename_map = {}
    for ch in raw.ch_names:
        if ch in _EEG_CHANNEL_RENAME_MAP:
            rename_map[ch] = _EEG_CHANNEL_RENAME_MAP[ch]

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


def _apply_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard 1020 montage if possible."""
    available_channels = set(raw.ch_names)

    # Try standard 1020 montage
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass

    return raw


def _remap_stimulus_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap stimulus event codes from events.tsv format to clean codes.

    OpenNeuro ERP CORE datasets typically store events as 'Stimulus/S 11'
    in events.tsv. We remap annotations to simple codes like 'S 11'.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    new_descriptions = []
    for desc in raw.annotations.description:
        # Handle 'Stimulus/S 11' -> 'S 11' format
        if desc.startswith("Stimulus/"):
            desc = desc[len("Stimulus/"):]
        # Also handle 'Stimulus/S211' -> 'S211'
        elif desc.startswith("Stimulus/S"):
            desc = desc[len("Stimulus/"):]

        # Clean up any whitespace issues
        desc = desc.strip()

        new_descriptions.append(desc)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)

    return raw


class OpenNeuroDS006018Kernel:
    """Stage1 kernel for OpenNeuro ds006018 (ERP CORE dataset)."""

    KERNEL_ID: str = "openneuro-ds006018-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : dict
            Locator row with File Path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated description and annotations.
        """
        # Get dataset root for participants.tsv lookup
        dataset_root = udataset.dataset_root if hasattr(udataset, "dataset_root") else ""

        # Step 1: Channel rename before montage
        raw = _apply_channel_rename(raw)

        # Step 2: Set montage (standard 1020)
        raw = _apply_montage(raw)

        # Step 3: Remap stimulus events
        raw = _remap_stimulus_events(raw)

        # Step 4: Extract subject metadata
        subject_info = _get_subject_info(row, dataset_root)

        # Step 5: Build eegunity_description
        # ERP CORE uses BrainAmp amplifiers with Ag/AgCl caps
        # Source: Kappenman et al. (2021) ERP CORE paper
        # Annotator: LLM, 2026-04-08,
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS006018Kernel()