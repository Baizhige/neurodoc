"""OpenNeuro DS006519 stage1 kernel for EEGUnity.

Intracranial EEG dataset during cortical stimulations evoking negative motor responses.
Supports Pre- vs Post-Stimulation Classification tasks.

Source: https://openneuro.org/datasets/ds006519
DOI: https://doi.org/10.18112/openneuro.ds006519.v1.0.0

This kernel handles:
- BIDS events extraction (Comment/prestim, Comment/poststim)
- Subject metadata from participants.tsv
- High sampling rate (4096 Hz) downsampling to 1000 Hz
- Intracranial EEG channel handling (patient-specific electrodes)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Event mapping for raw meta (Event ID -> canonical label)
_EVENT_LABEL_MAP: Dict[str, str] = {
    "Comment/prestim": "prestim",
    "Comment/poststim": "poststim",
}

# Inverse mapping for super meta derivation
_EVENT_TO_Y: Dict[str, int] = {
    "prestim": 0,
    "poststim": 1,
}

# Target events for epoching tasks
_TARGET_EVENTS: List[str] = ["Comment/prestim", "Comment/poststim"]


def _detect_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.

    Assumes BIDS structure: .../sub-<subject_id>/...
    """
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return pd.DataFrame()


def _get_subject_info(
    subject_id: str, dataset_root: str
) -> Dict[str, str]:
    """Extract subject metadata.

    Returns dict with age, sex, handedness from participants.tsv.
    Falls back to 'unknown' values if not found.

    Source: participants.tsv (BIDS)
    """
    default_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    df = _load_participants_tsv(dataset_root)
    if df.empty:
        return default_info

    # Match subject ID column (usually participant_id)
    id_col = None
    for col in df.columns:
        if "participant" in col.lower() and "id" in col.lower():
            id_col = col
            break
    if id_col is None and len(df.columns) > 0:
        # Try first column
        id_col = df.columns[0]

    if id_col is None:
        return default_info

    # Find matching row
    mask = df[id_col].astype(str).str.contains(subject_id, na=False)
    if not mask.any():
        return default_info

    row = df[mask].iloc[0]
    info = default_info.copy()

    # Extract age
    age_col = None
    for col in df.columns:
        if col.lower() in ("age", "participant_age"):
            age_col = col
            break
    if age_col is not None:
        val = row.get(age_col)
        if pd.notna(val):
            info["age"] = str(int(float(val))) if isinstance(val, (int, float)) else str(val)

    # Extract sex
    sex_col = None
    for col in df.columns:
        if col.lower() in ("sex", "gender"):
            sex_col = col
            break
    if sex_col is not None:
        val = row.get(sex_col)
        if pd.notna(val):
            sex_str = str(val).lower().strip()
            if sex_str in ("m", "male"):
                info["sex"] = "male"
            elif sex_str in ("f", "female"):
                info["sex"] = "female"
            else:
                info["sex"] = "unknown"

    # Extract handedness
    hand_col = None
    for col in df.columns:
        if "hand" in col.lower():
            hand_col = col
            break
    if hand_col is not None:
        val = row.get(hand_col)
        if pd.notna(val):
            hand_str = str(val).lower().strip()
            if hand_str in ("r", "right"):
                info["handedness"] = "right"
            elif hand_str in ("l", "left"):
                info["handedness"] = "left"
            else:
                info["handedness"] = "unknown"

    return info


def _build_events_from_annotations(
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Convert raw annotations to standardized labels.

    Maps original annotation descriptions to canonical labels
    defined in _EVENT_LABEL_MAP.
    """
    orig_annots = raw.annotations
    if orig_annots is None or len(orig_annots) == 0:
        return orig_annots

    new_descriptions = []
    for desc in orig_annots.description:
        mapped = _EVENT_LABEL_MAP.get(desc, desc)
        new_descriptions.append(mapped)

    return mne.Annotations(
        onset=orig_annots.onset,
        duration=orig_annots.duration,
        description=new_descriptions,
        orig_time=orig_annots.orig_time,
    )


def _apply_common_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Try to apply standard montage if channels are recognizable.

    For intracranial EEG, most channels will not match standard_1020.
    This attempts to set standard montage for any matching channels,
    silently skipping non-matching ones.
    """
    try:
        # Get standard 1020 montage
        standard_montage = mne.channels.make_standard_montage("standard_1020")

        # Find which channels in raw match standard names
        raw_chs = set(raw.ch_names)
        montage_chs = set(standard_montage.ch_names)

        # Only apply if significant overlap
        matching = raw_chs & montage_chs
        if len(matching) >= 8:  # At least 8 channels match
            raw.set_montage("standard_1020", on_missing="ignore")
        else:
            # For intracranial, channels are typically patient-specific
            # Skip montage but note this in processing
            pass
    except Exception:
        # Montage application failed - likely intracranial electrodes
        pass

    return raw


class OpenNeuroDS006519Kernel:
    """Stage1 kernel for OpenNeuro DS006519 (Intracranial EEG NMS)."""

    KERNEL_ID: str = "openneuro-ds006519-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with File Path and other metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata and annotations
        """
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", "")

        # Extract subject ID and metadata
        subject_id = _detect_subject_id(file_path)
        subject_info = _get_subject_info(subject_id, dataset_root)

        # Original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description
        # Amplifier/cap: intracranial EEG - typically unknown or patient-specific
        # Source: dataset documentation indicates intracranial electrode arrays
        # inferred by LLM, needs human review
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # inferred by LLM, needs human review
                "cap": "intracranial",  # inferred by LLM, needs human review
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Convert annotations to standardized labels
        standardized_annots = _build_events_from_annotations(raw)
        if standardized_annots is not None and len(standardized_annots) > 0:
            raw.set_annotations(standardized_annots)

        # Apply montage if applicable (may not apply for intracranial)
        raw = _apply_common_montage(raw)

        # Downsample from 4096 Hz to 1000 Hz for computational efficiency
        # Source: analysis.md recommends downsampling to <=1000 Hz
        if raw.info["sfreq"] > 1000:
            new_sfreq = 1000
            raw, _ = mne.filter.resample(
                raw,
                down=raw.info["sfreq"] / new_sfreq,
                npad="auto",
                method="polyphase",
                verbose=False,
            )

        return raw


# Module-level kernel instance
KERNEL = OpenNeuroDS006519Kernel()