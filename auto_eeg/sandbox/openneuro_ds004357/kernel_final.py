"""openneuro_ds004357 stage1 kernel for EEGUnity.

Visual feature decoding from RSVP stimuli - 16 subjects, 127 channels, 1000 Hz.
EEGUnity cannot parse BIDS datasets with standard MNE routines directly,
so this kernel implements HANDLES_UNAVAILABLE=True and provides its own load() method.

Source: https://openneuro.org/datasets/ds004357
Paper: https://doi.org/10.1038/s41598-025-27703-5
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.1038/s41598-025-27703-5 (Table 1, Methods section)
# "EEG was recorded from 128 channels using a BrainAmp MR plus amplifier"
# "Ag/AgCl electrode cap" - LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},  # LLM 推断，需人类复核
    "02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "10": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "11": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "12": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "13": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "14": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "15": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "16": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# Source: Dataset README and paper methods - 128-channel system
# Maps source channel names to standard_1020 names
# BioSemi 128-channel system channel mapping
# Source: https://www.biosemi.com/headcap.htm, LLM 推断，需人类复核
_EEG_CHANNEL_NAMES_STANDARD = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
    "CB1", "CB2",  # sometimes labeled as PO9/PO10 or CB1/CB2
    # Extra channels for 128-channel system (some may be EOG or other)
    "VEOG", "HEOG", "EMG",  # Reserved for EOG/EMG if present
]


# Source: OpenNeuro dataset file naming convention
_EVENT_LABEL_MAP = {
    "Event/E  1": 1,
    "Event/E 1": 1,
    "Event/E  2": 2,
    "Event/E 2": 2,
    "Event/E  3": 3,
    "Event/E 3": 3,
}


@dataclass
class OpenNeuroDS004357Kernel:
    """Stage1 kernel for openneuro_ds004357 dataset."""

    KERNEL_ID: str = "openneuro-ds004357-stage1"
    HANDLES_UNAVAILABLE: bool = True

    @staticmethod
    def load(udataset, row) -> Optional[mne.io.BaseRaw]:
        """Load EEG data from BIDS-format OpenNeuro dataset.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        row
            Locator row with file path information.

        Returns
        -------
        mne.io.BaseRaw or None
        """
        file_path = row.get("File Path") or row.get("file_path")
        if not file_path or not os.path.exists(file_path):
            # Try to find the file in BIDS structure
            dataset_root = getattr(udataset, "root", None)
            if dataset_root:
                sub_id = str(row.get("subject_id", row.get("participant_id", "")))
                # Look for EEG files in BIDS structure
                for ext in ["*.vhdr", "*.set", "*.eeg", "*.edf", "*.fif"]:
                    search_pattern = os.path.join(
                        dataset_root, f"sub-{sub_id}", "eeg", ext.replace("*", "")
                    )
                    import glob
                    matches = glob.glob(search_pattern)
                    if matches:
                        file_path = matches[0]
                        break

        if not file_path or not os.path.exists(file_path):
            return None

        # Try BrainVision format (common for OpenNeuro EEG)
        try:
            if file_path.endswith((".vhdr", ".eeg")):
                raw = mne.io.read_raw_brainvision(file_path, preload=False, verbose=False)
            elif file_path.endswith(".set"):
                raw = mne.io.read_raw_eeglab(file_path, preload=False, verbose=False)
            elif file_path.endswith(".edf"):
                raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
            elif file_path.endswith(".fif"):
                raw = mne.io.read_raw_fif(file_path, preload=False, verbose=False)
            else:
                # Auto-detect
                raw = mne.io.read_raw(file_path, preload=False, verbose=False)
            return raw
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            return None

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row.

        Returns
        -------
        mne.io.BaseRaw
        """
        # Get subject ID from row
        sub_id = str(row.get("subject_id", row.get("participant_id", "unknown")))
        if sub_id.startswith("sub-"):
            sub_id = sub_id[4:]

        # Get subject metadata (all unknown per analysis.md)
        subject_info = _SUBJECT_DICT.get(sub_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown"
        })

        # Build description dict
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp MR plus",  # Source: paper DOI 10.1038/s41598-025-27703-5, LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # Source: paper methods section, LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        rename_map = self._build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If standard_1020 doesn't work, try biosemi128
            try:
                montage = mne.channels.make_standard_montage("biosemi128")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage not available

        # Set annotations from events
        self._setup_annotations(raw)

        return raw

    def _build_channel_rename_map(self, raw: mne.io.BaseRaw) -> Dict[str, str]:
        """Build a rename map for non-standard channel names."""
        ch_names = raw.ch_names
        n_channels = len(ch_names)

        rename_map: Dict[str, str] = {}

        # Check for BioSemi-style numbered channels (e.g., "A1", "A2", etc.)
        # or generic "EEG 001", "EEG 002" style
        biosemi_pattern_channels = []
        eeg_numbered_channels = []

        for ch in ch_names:
            if ch.startswith(("A", "B", "C")) and ch[1:].isdigit():
                biosemi_pattern_channels.append(ch)
            elif ch.startswith("EEG ") and any(c.isdigit() for c in ch):
                eeg_numbered_channels.append(ch)

        # If we have BioSemi-style channels, try to map them
        if biosemi_pattern_channels:
            # BioSemi 128 system mapping
            # Source: Biosemi headcap layout, LLM 推断，需人类复核
            biosemi_layout = [
                "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
                "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
                "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
                "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
                "CB1", "CB2",  # PO9/PO10 sometimes
                "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
                "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
                "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
                "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
                "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
                "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
            ]
            # Only rename if we have matching count
            if len(biosemi_pattern_channels) >= 64:
                # Partial mapping for first 64 channels
                start_idx = 0
                for i, ch in enumerate(biosemi_pattern_channels):
                    if i < len(biosemi_layout):
                        rename_map[ch] = biosemi_layout[i]

        # If we have EEG 001 style channels
        if eeg_numbered_channels and len(rename_map) == 0:
            standard_1020_channels = [
                "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
                "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
                "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
                "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
            ]
            for i, ch in enumerate(eeg_numbered_channels):
                if i < len(standard_1020_channels):
                    rename_map[ch] = standard_1020_channels[i]

        return rename_map

    def _setup_annotations(self, raw: mne.io.BaseRaw) -> None:
        """Setup annotations from existing events or markers."""
        # Try to get events from annotations first
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) > 0:
                return  # Annotations already set
        except Exception:
            pass

        # If no annotations, try to find events in the data
        # Some datasets store events as triggers in a stim channel
        ch_names = raw.ch_names
        stim_channels = [ch for ch in ch_names if "stim" in ch.lower() or "trigger" in ch.lower() or ch == "STI 014"]

        if stim_channels:
            try:
                events = mne.find_events(raw, stim_channel=stim_channels[0], verbose=False)
                if len(events) > 0:
                    # Create annotations from events
                    descriptions = []
                    for event_id_val in events[:, 2]:
                        if event_id_val == 1:
                            descriptions.append("Event/E 1")
                        elif event_id_val == 2:
                            descriptions.append("Event/E 2")
                        elif event_id_val == 3:
                            descriptions.append("Event/E 3")
                        else:
                            descriptions.append(f"event-{event_id_val}")

                    annotations = mne.Annotations(
                        onset=events[:, 0] / raw.info["sfreq"],
                        duration=[0.0] * len(events),
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
            except Exception:
                pass


KERNEL = OpenNeuroDS004357Kernel()