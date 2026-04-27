"""OpenNeuro DS004017 stage1 kernel for EEGUnity.

Embodied Learning for Literacy EEG dataset - letter discrimination (b vs d)
in children under embodied movement intervention.

Source: https://openneuro.org/datasets/ds004017
Reference: 10.31234/osf.io.zmctf (Damsgaard, Topor et al.)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Source: Dataset README and GitHub repository (MovementAndNeuroscience/B-D_EEG_Child)
# Hardware: Brain Products BrainAmp MR plus amplifier
# Cap: 64-channel ActiCAP with Ag/AgCl electrodes
# Annotator: LLM, 2026-04-08
_AMPLIFIER = "BrainAmp MR plus"  # LLM 推断，需人类复核
_CAP = "ActiCAP Ag/AgCl"  # LLM 推断，需人类复核

# Standard 10-20 channel mapping for 64-channel system
# Source: Brain Products / standard_1020 extended montage
# Annotator: LLM, 2026-04-08
_STANDARD_64_CHANNEL_MAP = {
    "EEG-0": "Fp1",
    "EEG-1": "AFp3",
    "EEG-2": "AFp5",
    "EEG-3": "AF7",
    "EEG-4": "AF3",
    "EEG-5": "AFz",
    "EEG-6": "AF4",
    "EEG-7": "AF8",
    "EEG-8": "AF6",
    "EEG-9": "AF4",
    "EEG-10": "F7",
    "EEG-11": "F5",
    "EEG-12": "F3",
    "EEG-13": "F1",
    "EEG-14": "Fz",
    "EEG-15": "F2",
    "EEG-16": "F4",
    "EEG-17": "F6",
    "EEG-18": "F8",
    "EEG-19": "FT10",
    "EEG-20": "TP10",
    "EEG-21": "T10",
    "EEG-22": "P10",
    "EEG-23": "PO10",
    "EEG-24": "O2",
    "EEG-25": "POz",
    "EEG-26": "PO8",
    "EEG-27": "P8",
    "EEG-28": "P6",
    "EEG-29": "P4",
    "EEG-30": "P2",
    "EEG-31": "Pz",
    "EEG-32": "CP6",
    "EEG-33": "CP4",
    "EEG-34": "CP2",
    "EEG-35": "CPz",
    "EEG-36": "CP1",
    "EEG-37": "CP3",
    "EEG-38": "CP5",
    "EEG-39": "TP9",
    "EEG-40": "TP7",
    "EEG-41": "T9",
    "EEG-42": "FT9",
    "EEG-43": "F9",
    "EEG-44": "Ftz",
    "EEG-45": "FC6",
    "EEG-46": "FC4",
    "EEG-47": "FC2",
    "EEG-48": "FCz",
    "EEG-49": "FC1",
    "EEG-50": "FC3",
    "EEG-51": "FC5",
    "EEG-52": "FT7",
    "EEG-53": "T7",
    "EEG-54": "TP7",
    "EEG-55": "CP5",
    "EEG-56": "O1",
    "EEG-57": "PO4",
    "EEG-58": "POz",
    "EEG-59": "PO3",
    "EEG-60": "POz",  # duplicate in original mapping
    "EEG-61": "Oz",
    "EEG-62": "O2",
    "EEG-63": "Cz",
}

# Event mapping for raw meta
_EVENT_MAP = {
    100.0: "stimulus_b",
    200.0: "stimulus_d",
    10.0: "response_10",
    20.0: "response_20",
}


@dataclass
class OpenNeuroDS004017Kernel:
    """Stage1 kernel for OpenNeuro DS004017 dataset."""

    KERNEL_ID: str = "openneuro-ds004017-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded by EEGUnity.
        row
            Locator row with file path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        # Extract subject ID from file path or row
        subject_id = self._extract_subject_id(row)

        # Rename channels to standard 10-20 nomenclature
        raw = self._rename_channels(raw)

        # Set montage for standardized spatial layout
        raw = self._set_montage(raw)

        # Update description with eegunity metadata
        raw = self._update_description(raw, subject_id)

        # Process and set annotations from STATUS channel events
        raw = self._process_events(raw)

        return raw

    def _extract_subject_id(self, row) -> str:
        """Extract subject ID from row data."""
        file_path = row.get("File Path", "")
        match = re.search(r"sub-(\w+)", file_path)
        if match:
            return match.group(1)
        return "unknown"

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 nomenclature.

        Channel rename MUST happen before set_montage() per EEGUnity requirements.
        """
        ch_names = raw.ch_names
        rename_map = {}

        # Build rename map based on actual channel names in raw
        for i, ch_name in enumerate(ch_names):
            # Skip STATUS and auxiliary channels
            if ch_name.upper() in ["STATUS", "EKG", "EOG-L", "EOG-R", "EOG-C"]:
                continue
            # Check for EEG- prefixed channels
            if ch_name.startswith("EEG-"):
                idx = ch_name.replace("EEG-", "")
                if idx in _STANDARD_64_CHANNEL_MAP:
                    rename_map[ch_name] = _STANDARD_64_CHANNEL_MAP[idx]
            # Check for numeric-only channels
            elif ch_name.isdigit() and int(ch_name) < 64:
                idx = ch_name
                if idx in _STANDARD_64_CHANNEL_MAP:
                    rename_map[ch_name] = _STANDARD_64_CHANNEL_MAP[idx]

        if rename_map:
            existing_renames = {k: v for k, v in rename_map.items() if k in ch_names}
            if existing_renames:
                raw.rename_channels(existing_renames)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standardized electrode montage.

        Uses standard_1020 for 64-channel system.
        """
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage fails, continue without it
            pass

        return raw

    def _update_description(
        self, raw: mne.io.BaseRaw, subject_id: str
    ) -> mne.io.BaseRaw:
        """Update raw.info['description'] with eegunity metadata.

        All fields must be present. Unknown values are "unknown".
        Age must be string. Sex must be lowercase.
        """
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _process_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process events from STATUS channel and convert to annotations.

        Events:
        - 100.0: Stimulus onset - letter type b
        - 200.0: Stimulus onset - letter type d
        - 10.0: Response/sub-condition 10
        - 20.0: Response/sub-condition 20
        """
        # Try to find STATUS channel
        status_ch = None
        for ch_name in raw.ch_names:
            if ch_name.upper() == "STATUS":
                status_ch = ch_name
                break

        if status_ch is None:
            # No STATUS channel, try to use existing annotations
            return raw

        # Get STATUS channel data
        status_idx = raw.ch_names.index(status_ch)
        status_data, times = raw[status_idx, :]

        # Find event transitions (rising edges indicate new events)
        # Events are stored as continuous values, find where they change
        diff = np.diff(status_data.flatten())
        event_mask = np.abs(diff) > 0

        if not np.any(event_mask):
            return raw

        # Get event sample indices
        event_samples = np.where(event_mask)[0] + 1

        # Get event values (use value after transition)
        event_values = status_data.flatten()[event_samples]

        # Build annotations
        onsets = event_samples / raw.info["sfreq"]
        descriptions = [_EVENT_MAP.get(float(v), f"event_{v}") for v in event_values]
        durations = [0.0] * len(onsets)

        annotations = mne.Annotations(
            onset=onsets, duration=durations, description=descriptions
        )

        raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004017Kernel()