"""Dataset-specific kernel for openneuro ds004595.

RL Task (3-Armed Bandit) with Alcohol Cues in Hazardous Drinkers.
53 subjects, 66 channels, 500 Hz.

This kernel extends the OpenNeuro base kernel with dataset-specific:
- Channel renaming for standard 1020 compatibility
- Event mapping for all task events
- Subject metadata extraction from participants.tsv

Source: https://openneuro.org/datasets/ds004595 | DOI: 10.5334/cpsy.96
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# Source: participants.tsv (BIDS) | Extractor: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load and parse participants.tsv if available."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(udataset, row) -> Dict[str, str]:
    """Extract subject age, sex from participants.tsv or defaults."""
    # Try to get from participants.tsv via dataset path
    dataset_path = getattr(udataset, "dataset_path", None)
    if dataset_path is None:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}

    df = _load_participants_tsv(dataset_path)
    if df.empty:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}

    # Match subject ID from row (e.g., sub-01 -> 01)
    subject_id = row.get("subject_id", "")
    if not subject_id:
        # Try to extract from file path
        file_path = row.get("File Path", "")
        match = re.search(r"sub-(\w+)", file_path)
        if match:
            subject_id = match.group(1)

    # Normalize: find row where participant_id matches
    col_match = "participant_id" if "participant_id" in df.columns else "subject_id"
    if col_match in df.columns:
        subj_row = df[df[col_match] == subject_id]
        if not subj_row.empty:
            age = subj_row.iloc[0].get("age", "unknown")
            sex = subj_row.iloc[0].get("sex", "unknown")
            handedness = subj_row.iloc[0].get("handedness", "unknown")
            return {
                "age": str(age) if pd.notna(age) else "unknown",
                "sex": str(sex).lower() if pd.notna(sex) else "unknown",
                "handedness": str(handedness).lower() if pd.notna(handedness) else "unknown",
            }

    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


# =============================================================================
# Channel Renaming
# Source: 64-channel EEG cap layout (inferred from 66 total channels)
# Annotator: LLM 推断，需人类复核
# =============================================================================
# Standard 64-channel layout + 2 EOG channels
_STANDARD_1020_CHANNELS = [
    "FP1", "Fpz", "FP2", "AF3", "AFz", "AF4",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8",
    "O1", "Oz", "O2",
    "EOG-left", "EOG-right",  # EOG channels
    "CB1", "CB2",  # or VEOG if applicable
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 1020 names.

    This dataset uses BrainVision format with channel names like:
    'Fp1', 'Fp2', 'F3', 'Fz', 'F4', 'C3', 'Cz', 'C4', ...
    which are already standard. Only non-standard aliases need remapping.
    """
    rename_map: Dict[str, str] = {}

    # Common aliases that may appear in BrainVision files
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "FP1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "FP2"]),
        ("AF3", ["AF3", "EEG-AF3"]),
        ("AFz", ["AFz", "EEG-AFz"]),
        ("AF4", ["AF4", "EEG-AF4"]),
        ("F7", ["F7", "EEG-F7"]),
        ("F5", ["F5", "EEG-F5"]),
        ("F3", ["F3", "EEG-F3"]),
        ("F1", ["F1", "EEG-F1"]),
        ("Fz", ["Fz", "EEG-Fz"]),
        ("F2", ["F2", "EEG-F2"]),
        ("F4", ["F4", "EEG-F4"]),
        ("F6", ["F6", "EEG-F6"]),
        ("F8", ["F8", "EEG-F8"]),
        ("FC5", ["FC5", "EEG-FC5"]),
        ("FC3", ["FC3", "EEG-FC3"]),
        ("FC1", ["FC1", "EEG-FC1"]),
        ("FCz", ["FCz", "EEG-FCz"]),
        ("FC2", ["FC2", "EEG-FC2"]),
        ("FC4", ["FC4", "EEG-FC4"]),
        ("FC6", ["FC6", "EEG-FC6"]),
        ("T7", ["T7", "EEG-T7", "T3"]),
        ("C5", ["C5", "EEG-C5"]),
        ("C3", ["C3", "EEG-C3"]),
        ("C1", ["C1", "EEG-C1"]),
        ("Cz", ["Cz", "EEG-Cz"]),
        ("C2", ["C2", "EEG-C2"]),
        ("C4", ["C4", "EEG-C4"]),
        ("C6", ["C6", "EEG-C6"]),
        ("T8", ["T8", "EEG-T8", "T4"]),
        ("TP7", ["TP7", "EEG-TP7"]),
        ("CP5", ["CP5", "EEG-CP5"]),
        ("CP3", ["CP3", "EEG-CP3"]),
        ("CP1", ["CP1", "EEG-CP1"]),
        ("CPz", ["CPz", "EEG-CPz"]),
        ("CP2", ["CP2", "EEG-CP2"]),
        ("CP4", ["CP4", "EEG-CP4"]),
        ("CP6", ["CP6", "EEG-CP6"]),
        ("TP8", ["TP8", "EEG-TP8"]),
        ("P7", ["P7", "EEG-P7"]),
        ("P5", ["P5", "EEG-P5"]),
        ("P3", ["P3", "EEG-P3"]),
        ("P1", ["P1", "EEG-P1"]),
        ("Pz", ["Pz", "EEG-Pz"]),
        ("P2", ["P2", "EEG-P2"]),
        ("P4", ["P4", "EEG-P4"]),
        ("P6", ["P6", "EEG-P6"]),
        ("P8", ["P8", "EEG-P8"]),
        ("PO7", ["PO7", "EEG-PO7"]),
        ("PO5", ["PO5", "EEG-PO5"]),
        ("PO3", ["PO3", "EEG-PO3"]),
        ("POz", ["POz", "EEG-POz"]),
        ("PO4", ["PO4", "EEG-PO4"]),
        ("PO6", ["PO6", "EEG-PO6"]),
        ("PO8", ["PO8", "EEG-PO8"]),
        ("O1", ["O1", "EEG-O1"]),
        ("Oz", ["Oz", "EEG-Oz"]),
        ("O2", ["O2", "EEG-O2"]),
        ("EOG-left", ["EOG-left", "EOG-L", "VEOG"]),
        ("EOG-right", ["EOG-right", "EOG-R"]),
        ("CB1", ["CB1", "EOG-CB1"]),
        ("CB2", ["CB2", "EOG-CB2"]),
    ]

    existing_names = set(raw.ch_names)
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


# =============================================================================
# Event Mapping
# Source: analysis.md + DOI 10.5334/cpsy.96
# =============================================================================
_EVENT_MAP = {
    # Novel cue events (S101-S106) - 6 arm order permutations
    "S101": "novel cue: order 1",
    "S102": "novel cue: order 2",
    "S103": "novel cue: order 3",
    "S104": "novel cue: order 4",
    "S105": "novel cue: order 5",
    "S106": "novel cue: order 6",
    # Feedback valence events
    "S200": "feedback: win",      # LLM 推断，需人类复核
    "S201": "feedback: loss",     # LLM 推断，需人类复核
    # Response events
    "R  6": "response: left arm",
    "R 12": "response: right arm",
    # Task structure events (cue-related)
    "S  1": "cue: alcohol",       # LLM 推断，需人类复核
    "S  2": "cue: neutral",       # LLM 推断，需人类复核
    "S  3": "choice display",     # LLM 推断，需人类复核
    "S  4": "choice display",     # LLM 推断，需人类复核
    "S  5": "trial: start",       # LLM 推断，需人类复核
    "S  6": "trial: baseline",    # LLM 推断，需人类复核
    "S  7": "trial: end",         # LLM 推断，需人类复核
    "S  8": "instruction",        # LLM 推断，需人类复核
    "S  9": "break start",        # LLM 推断，需人类复核
    "S 10": "break end",          # LLM 推断，需人类复核
    # Admin / marker events
    "S 99": "admin: marker-99",
    "S199": "admin: marker-199",
}


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Remap annotations to kernel canonical event names."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw.annotations

    new_descriptions = []
    for desc in raw.annotations.description:
        # Normalize: strip whitespace and map
        normalized = desc.strip()
        remapped = _EVENT_MAP.get(normalized, _EVENT_MAP.get(desc, desc))
        new_descriptions.append(remapped)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    return new_annotations


# =============================================================================
# Dataset Metadata
# Source: DOI 10.5334/cpsy.96 | Annotator: LLM 推断，需人类复核
# =============================================================================
_DATASET_METADATA = {
    "amplifier": "BrainAmp",      # LLM 推断，需人类复核
    "cap": "Ag/AgCl",             # LLM 推断，需人类复核
}


# =============================================================================
# Main Kernel Class
# =============================================================================
class OpenNeuroDs004595Kernel:
    """Stage1 kernel for openneuro_ds004595 (3-Armed Bandit RL Task)."""

    KERNEL_ID: str = "openneuro-ds004595"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata.
        """
        # ---------------------------------------------------------------------
        # 1. Extract subject metadata
        # ---------------------------------------------------------------------
        subject_info = _get_subject_info(udataset, row)

        # ---------------------------------------------------------------------
        # 2. Rename channels to standard 1020 names
        # ---------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # ---------------------------------------------------------------------
        # 3. Set montage if all channels are standard
        # ---------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Non-standard channels present, skip montage

        # ---------------------------------------------------------------------
        # 4. Remap event annotations
        # ---------------------------------------------------------------------
        if raw.annotations is not None and len(raw.annotations) > 0:
            raw.set_annotations(_remap_annotations(raw))

        # ---------------------------------------------------------------------
        # 5. Build and set description
        # ---------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DATASET_METADATA.get("amplifier", "unknown"),
                "cap": _DATASET_METADATA.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


# =============================================================================
# Module-level KERNEL object
# =============================================================================
KERNEL = OpenNeuroDs004595Kernel()