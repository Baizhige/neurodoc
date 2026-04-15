"""OpenNeuro ds003800 stage1 kernel for EEGUnity.

Auditory Gamma Entrainment dataset - 40 Hz amplitude-modulated auditory stimulation
in elderly participants with dementia.

Source: https://openneuro.org/datasets/ds003800
Reference: https://doi.org/10.1016/j.dib.2022.107839
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.1016/j.dib.2022.107839 - Dataset descriptor
# Annotator: LLM, 2026-04-08
_SUBJECT_METADATA: Dict[str, Dict[str, str]] = {
    # Subject IDs are numeric (e.g., sub-01, sub-02, etc.)
    # Age and sex information not publicly available in dataset
    # All fields marked as unknown pending human review
}
_SUBJECT_METADATA_SOURCE = "Dataset paper (DOI: 10.1016/j.dib.2022.107839) - LLM 推断，需人类复核"


# Standard 10-20 system channel mapping for 19 channels
# Source: Standard 10-20 montage, 19-channel configuration
# Annotator: LLM, 2026-04-08
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T3", "C3", "Cz", "C4", "T4",
    "T5", "P3", "Pz", "P4", "T6",
    "O1", "O2"
]


def _detect_channel_format(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Detect and map channel names to standard 10-20 names.

    Source: Standard 10-20 electrode placement system
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    for i, ch in enumerate(ch_names):
        ch_upper = ch.upper().strip()
        if ch_upper in [c.upper() for c in _STANDARD_1020_CHANNELS]:
            for std_ch in _STANDARD_1020_CHANNELS:
                if ch.upper() == std_ch.upper():
                    if ch != std_ch:
                        rename_map[ch] = std_ch
                    break
        elif ch_upper.startswith("EEG"):
            if i < len(_STANDARD_1020_CHANNELS):
                new_name = _STANDARD_1020_CHANNELS[i]
                if ch != new_name:
                    rename_map[ch] = new_name

    return rename_map


def _build_event_mapping() -> Dict[str, int]:
    """Build event code mapping for Stimulus vs Rest paradigm.

    Event codes from dataset descriptor (DOI: 10.1016/j.dib.2022.107839):
    - Code 1: Rest (resting/quiet period)
    - Code 2: Stimulus (40 Hz AM auditory stimulation)
    """
    return {
        "Rest": 1,
        "Stimulus": 2,
    }


def _remap_annotations_to_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap numeric annotations to human-readable event labels.

    Source: Dataset descriptor (DOI: 10.1016/j.dib.2022.107839)
    """
    EVENT_CODE_MAP = {
        1: "Rest",
        2: "Stimulus",
    }

    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    descriptions = []
    for desc in raw.annotations.description:
        try:
            code = int(float(desc))
            if code in EVENT_CODE_MAP:
                descriptions.append(EVENT_CODE_MAP[code])
            else:
                descriptions.append(str(desc))
        except (ValueError, TypeError):
            descriptions.append(str(desc))

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    return raw


@dataclass
class OpenNeuroDS003800Kernel:
    """Stage1 kernel for OpenNeuro ds003800 - Auditory Gamma Entrainment."""

    KERNEL_ID: str = "openneuro-ds003800-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object with standardized metadata.
        """
        file_path = row.get("File Path", "")

        # Extract subject ID from file path or row
        subject_id = row.get("subject_id", "")
        if not subject_id and file_path:
            parts = file_path.split(os.sep)
            for part in parts:
                if part.startswith("sub-"):
                    subject_id = part.replace("sub-", "")
                    break

        # Get subject metadata
        subject_info = _SUBJECT_METADATA.get(subject_id, {})
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        # Channel renaming before set_montage
        rename_map = _detect_channel_format(raw)
        if rename_map:
            # Source: Standard 10-20 system, LLM 推断，需人类复核
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels present in the data
            common_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if common_channels:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if standard montage fails

        # Remap annotations from numeric codes to readable labels
        raw = _remap_annotations_to_events(raw)

        # Determine amplifier info - LLM 推断，需人类复核
        amplifier = "unknown"  # LLM 推断，需人类复核
        cap = "unknown"  # LLM 推断，需人类复核

        # Build description dict
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003800Kernel()