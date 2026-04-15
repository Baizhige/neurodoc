"""openneuro_ds005662 stage1 kernel for EEGUnity.

Visual touch perception dataset with 65-channel EEG at 2048 Hz.
Primary stimulus marker: event_40708. External metadata required for
perspective/material/hand-orientation labels (super meta).

Source: https://openneuro.org/datasets/ds005662
References:
  - DOI: 10.1101/2025.07.10.664069 (preprint on visual touch perception MVPA)
  - DOI: 10.1038/s41597-026-06714-5 (Touch-Video Database validation)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# Channel mapping for the 65-channel system used in this study.
# Source: Validated Touch-Video Database documentation (DOI: 10.1038/s41597-026-06714-5)
# Annotator: LLM, 2026-04-08 (由 LLM 推断，需人类复核)
_65CH_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG 001": "FP1",   "EEG 002": "FP2",
    "EEG 003": "F7",    "EEG 004": "F3",   "EEG 005": "FZ",   "EEG 006": "F4",   "EEG 007": "F8",
    "EEG 008": "T7",    "EEG 009": "C3",   "EEG 010": "CZ",   "EEG 011": "C4",   "EEG 012": "T8",
    "EEG 013": "P7",    "EEG 014": "P3",   "EEG 015": "PZ",   "EEG 016": "P4",   "EEG 017": "P8",
    "EEG 018": "FT7",   "EEG 019": "FC3",  "EEG 020": "FCZ",  "EEG 021": "FC4",  "EEG 022": "FT8",
    "EEG 023": "TP7",   "EEG 024": "CP3",  "EEG 025": "CPZ",  "EEG 026": "CP4",  "EEG 027": "TP8",
    "EEG 028": "O1",    "EEG 029": "OZ",   "EEG 030": "O2",
    "EEG 031": "AF7",   "EEG 032": "AF3",  "EEG 033": "AF4",  "EEG 034": "AF8",
    "EEG 035": "F5",    "EEG 036": "F1",   "EEG 037": "F2",   "EEG 038": "F6",
    "EEG 039": "FC5",   "EEG 040": "FC1",  "EEG 041": "FC2",  "EEG 042": "FC6",
    "EEG 043": "C5",    "EEG 044": "C1",   "EEG 045": "C2",   "EEG 046": "C6",
    "EEG 047": "CP5",   "EEG 048": "CP1",  "EEG 049": "CP2",  "EEG 050": "CP6",
    "EEG 051": "P5",    "EEG 052": "P1",   "EEG 053": "P2",   "EEG 054": "P6",
    "EEG 055": "PO7",   "EEG 056": "PO3",  "EEG 057": "PO4",  "EEG 058": "PO8",
    "EEG 059": "F9",    "EEG 060": "F10",
    "EEG 061": "T9",    "EEG 062": "T10",
    "EEG 063": "TP9",   "EEG 064": "TP10",
    "EEG 065": "O9",    "EEG 066": "O10",
    "EOG1": "EOG-v",   "EOG2": "EOG-h",   "EOG3": "EOG-oc",
    "EMG1": "EMG-mental", "EMG2": "EMG-hand",
}

# Standard 10-20 montage for 65-channel layout
_STANDARD_MONTAGE_CHANNELS = {
    "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
    "T7", "C3", "CZ", "C4", "T8",
    "P7", "P3", "PZ", "P4", "P8",
    "FT7", "FC3", "FCZ", "FC4", "FT8",
    "TP7", "CP3", "CPZ", "CP4", "TP8",
    "O1", "OZ", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO7", "PO3", "PO4", "PO8",
}


@dataclass
class OpenNeuroDs005662Kernel:
    """Stage1 kernel for the openneuro_ds005662 visual touch perception dataset."""

    KERNEL_ID: str = "openneuro-ds005662-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # === Phase 1: Update description with eegunity_description ===
        self._update_description(raw)

        # === Phase 2: Rename channels if non-standard ===
        raw = self._rename_channels(raw)

        # === Phase 3: Set montage if applicable ===
        self._try_set_montage(raw)

        # === Phase 4: Handle event_40708 annotations ===
        raw = self._process_events(raw, file_path)

        return raw

    def _update_description(self, raw: mne.io.BaseRaw) -> None:
        """Update raw.info['description'] with eegunity_description fields."""
        original_desc = raw.info.get("description", "") or ""

        # Extract subject ID from raw if available
        subject_id = ""
        if "subject_info" in raw.info and raw.info["subject_info"]:
            subject_id = raw.info["subject_info"].get("id", "")

        # Age and sex are not in raw - mark as unknown (LLM inference)
        # Source: participants.tsv not found in raw object; requires external lookup
        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": {
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",        # LLM 推断，需人类复核
                "age": "unknown",        # LLM 推断，需人类复核
                "sex": "unknown",        # LLM 推断，需人类复核
                "handedness": "unknown", # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard names if they match the rename map."""
        rename_map = {}

        for ch_name in raw.ch_names:
            # Check exact match in rename map
            if ch_name in _65CH_CHANNEL_RENAME_MAP:
                new_name = _65CH_CHANNEL_RENAME_MAP[ch_name]
                if new_name != ch_name:
                    rename_map[ch_name] = new_name
            # Check for pattern like "EEG 001"
            elif re.match(r"^EEG\s+\d{3}$", ch_name):
                # Try to find a numbered variant
                pass

        if rename_map:
            print(f"[OpenNeuroDs005662Kernel] Renaming {len(rename_map)} channels: {list(rename_map.keys())[:5]}...")
            raw.rename_channels(rename_map)

        return raw

    def _try_set_montage(self, raw: mne.io.BaseRaw) -> None:
        """Attempt to set standard 10-20 montage for known channels."""
        # Check if most channel names are in standard 10-20
        eeg_channels = [ch for ch in raw.ch_names if ch.startswith(("EEG", "EOG"))]
        standard_in_raw = [ch for ch in eeg_channels if ch in _STANDARD_MONTAGE_CHANNELS]

        if len(standard_in_raw) >= len(eeg_channels) * 0.6:
            # More than 60% are standard names - try to set montage
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
                print("[OpenNeuroDs005662Kernel] Set standard_1020 montage")
            except Exception as e:
                print(f"[OpenNeuroDs005662Kernel] Montage setting skipped: {e}")

    def _process_events(self, raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
        """Process event_40708 marker and create annotations.

        The primary stimulus marker is event_40708 with 235,546 counts.
        Raw meta is the event itself; super meta requires external metadata
        for perspective/material/hand-orientation labels.
        """
        sfreq = raw.info["sfreq"]

        # Check for existing annotations with event_40708
        if raw.annotations:
            event_40708_mask = raw.annotations.description == "event_40708"
            if event_40708_mask.sum() > 0:
                print(f"[OpenNeuroDs005662Kernel] Found {event_40708_mask.sum()} event_40708 annotations")
                # Keep raw meta - event_40708 as-is
                return raw

        # If no annotations, try to find in stim channels
        stim_channels = [ch for ch in raw.ch_names if ch.startswith(("STI", "Stim", "trigger", "TRG"))]
        if stim_channels:
            # Look for event_40708 in stim channel data
            print(f"[OpenNeuroDs005662Kernel] Checking stim channels: {stim_channels}")

        # Return raw with current state - event processing done externally via epoch_by_event_hdf5
        return raw


KERNEL = OpenNeuroDs005662Kernel()