"""ArEEG (openneuro_ds005262) stage1 kernel for EEGUnity.

ArEEG: Arabic Inner Speech EEG Dataset.
8-channel EEG, 250 Hz, 12 subjects.
Paradigm: imagined speech (Up, Down, Left, Right, Select, Rest) with Arabic visual cues.

File format: OpenNeuro BIDS (EDF/BDF).
Channels: 8 EEG electrodes.

Source: https://doi.org/10.1038/s41597-025-05387-w
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne


# Channel mapping for 8-channel EEG cap.
# Source: paper DOI 10.1038/s41597-025-05387-w (ArEEG paper) — 8-channel EEG cap layout.
# Annotator: LLM, 2026-04-09 — LLM 推断，需人类复核
_CHANNEL_RENAME_MAP = {
    "Ch1": "Fp1",
    "Ch2": "Fp2",
    "Ch3": "F7",
    "Ch4": "F3",
    "Ch5": "F4",
    "Ch6": "F8",
    "Ch7": "T7",
    "Ch8": "C4",
    # Also support alternative names from some OpenNeuro exports
    "EEG 001": "Fp1",
    "EEG 002": "Fp2",
    "EEG 003": "F7",
    "EEG 004": "F3",
    "EEG 005": "F4",
    "EEG 006": "F8",
    "EEG 007": "T7",
    "EEG 008": "C4",
}

# Standard 10-20 8-channel montage positions (subset of standard_1020).
_8CH_MONTAGE_CHANNELS = ["Fp1", "Fp2", "F7", "F3", "F4", "F8", "T7", "C4"]

# Fallback full 10-20 montage for matching if available
_FALLBACK_MONTAGE = mne.channels.make_standard_montage("standard_1020")


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load participants.tsv if present, return dict keyed by subject ID."""
    tsv_path = os.path.join(dataset_path, "participants.tsv")
    subject_dict: Dict[str, Dict[str, str]] = {}
    if os.path.isfile(tsv_path):
        try:
            import pandas as pd

            df = pd.read_csv(tsv_path, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).strip()
                if not subj_id:
                    continue
                # Map columns to eegunity_description fields
                subject_dict[subj_id] = {
                    "age": str(int(row["age"])) if "age" in row and pd.notna(row["age"]) else "unknown",
                    "sex": str(row["sex"]).lower() if "sex" in row and pd.notna(row["sex"]) else "unknown",
                    "handedness": str(row["handedness"]).lower() if "handedness" in row and pd.notna(row.get("handedness", "")) else "unknown",
                }
        except Exception:
            pass
    return subject_dict


def _detect_subject_id(raw: mne.io.BaseRaw, row) -> str:
    """Extract subject ID from raw info or row metadata."""
    # Try from raw info['subject_info']
    subj_info = raw.info.get("subject_info", {})
    if subj_info:
        return str(subj_info.get("his_id", ""))
    # Try from row
    for col in ["Subject ID", "subject_id", "participant_id"]:
        if col in row and row[col]:
            return str(row[col])
    return "unknown"


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    for ch in raw.ch_names:
        if ch in _CHANNEL_RENAME_MAP:
            rename_map[ch] = _CHANNEL_RENAME_MAP[ch]
    if rename_map:
        raw.rename_channels(rename_map)
    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for 8-channel layout if all channels match."""
    existing = set(raw.ch_names)
    if existing.issubset(_FALLBACK_MONTAGE.ch_names):
        raw.set_montage(_FALLBACK_MONTAGE, on_missing="warn")
    else:
        # Build subset montage for the 8 channels we have
        try:
            sub_montage = _FALLBACK_MONTAGE.copy()
            sub_montage.rename_channels({ch: ch for ch in existing if ch in sub_montage.ch_names})
            raw.set_montage(sub_montage, on_missing="warn")
        except Exception:
            pass
    return raw


class ArEEGKernel:
    """Stage1 kernel for the ArEEG (openneuro_ds005262) dataset."""

    KERNEL_ID = "openneuro-ds005262-stage1"

    def __init__(self, dataset_path: Optional[str] = None):
        self._dataset_path = dataset_path
        self._participant_dict: Dict[str, Dict[str, str]] = {}

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        original_desc = raw.info.get("description", "")

        # Detect subject
        subject_id = _detect_subject_id(raw, row)

        # Load participants.tsv for per-subject metadata
        if self._dataset_path and not self._participant_dict:
            self._participant_dict = _load_participants_tsv(self._dataset_path)

        # Get subject-specific info or use unknown
        if subject_id in self._participant_dict:
            subj_info = self._participant_dict[subject_id]
            age = subj_info["age"]
            sex = subj_info["sex"]
            handedness = subj_info["handedness"]
        else:
            age = "unknown"  # LLM 推断，需人类复核
            sex = "unknown"  # LLM 推断，需人类复核
            handedness = "unknown"  # LLM 推断，需人类复核

        # Build description dict
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # LLM 推断，需人类复核 (ArEEG paper DOI 10.1038/s41597-025-05387-w does not specify amplifier model)
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels BEFORE set_montage()
        raw = _rename_channels(raw)

        # Set standard 10-20 montage for spatial reference
        raw = _set_montage_if_possible(raw)

        # Reconstruct annotations from existing events if needed
        # ArEEG stores events as annotations with Comment/* descriptions
        existing_ann = raw.annotations
        if len(existing_ann) == 0:
            # Try to reconstruct from stim channels if present
            pass  # Keep as-is; EEGUnity handles annotations downstream

        return raw


# Module-level singleton
KERNEL = ArEEGKernel()