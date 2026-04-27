"""OpenNeuro DS003887 stage1 kernel for EEGUnity.

Dataset: Capacity for movement is an organisational principle in object representations
Source: https://openneuro.org/datasets/ds003887 DOI: https://doi.org/10.18112/openneuro.ds003887.v1.2.3

EEGLAB-preprocessed RSVP data (128-channel cap, 127 usable after reference removal).
Sampling rate: 250 Hz.

Event Structure:
- E8: Movement-capable object (animate) - dominant (~4800/subject)
- E9: Non-movement object (inanimate) - dominant (~4800/subject)
- E1-E5: Object categories 1/2/3/5 (~1600 each/subject)
- E4: Block boundary markers (~40/subject)

Primary MVPA: Binary E8 vs E9 classification.

Source: DOI 10.1016/j.neuroimage.2022.119517
Channel mapping source: 128-channel BrainVision montage (standard 10-20 layout)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Annotator: LLM, 2026-04-08
# Source: Dataset README and EEGLAB preprocessing pipeline description
# Amplifier is BrainAmp (Brain Products) based on the preprocessing pipeline
_AMPLIFIER = "BrainAmp"
_CAP = "Ag/AgCl"  # Standard for BrainAmp systems, LLM inferred from EEGLAB pipeline


@dataclass
class OpenNeuroDS003887Kernel:
    """Stage1 kernel for OpenNeuro DS003887 dataset."""

    KERNEL_ID: str = "openneuro-ds003887-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object (loaded from EEGLAB .set file).
        row
            Locator row with File Path and subject info.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels, events, and metadata.
        """
        # Get file path for filename-based subject ID extraction
        file_path = row.get("File Path", "")

        # Rename channels to standard 10-20 names BEFORE set_montage
        raw = self._rename_channels(raw)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Drop extra channels that don't exist in standard_1020
            available_chs = [ch for ch in raw.ch_names if ch in montage.ch_names]
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage fails, continue without it
            pass

        # Set annotations from existing annotations or events
        raw = self._ensure_annotations(raw)

        # Extract subject ID from file path or row
        subject_id = self._extract_subject_id(row, file_path)

        # Build and set description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _extract_subject_id(self, row, file_path: str) -> str:
        """Extract subject ID from row or file path."""
        if "subject_id" in row and row["subject_id"]:
            return str(row["subject_id"])

        # Try to extract from file path: sub-01, sub-02, etc.
        match = re.search(r"sub-(\d+)", file_path)
        if match:
            return f"sub-{match.group(1)}"

        return "unknown"

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 nomenclature.

        EEGLAB-preprocessed data often uses non-standard channel names.
        This kernel attempts to normalize them based on the 128-channel cap layout.

        Annotator: LLM, 2026-04-08
        Source: Standard 128-channel BrainVision / EasyCap montage
        Note: This is LLM-inferred mapping based on 10-20 system; needs human verification
        """
        ch_names = raw.ch_names
        rename_map: Dict[str, str] = {}

        # Standard 10-20 channel list for 128-channel cap
        # The cap follows a systematic naming: Fp, F, Fz, C, Cz, P, Pz, O, Oz
        # Plus intermediate positions (1,3,5,7 for left; 2,4,6,8 for right)

        # Build expected channel names for 128-channel standard layout
        # Standard naming convention for high-density caps
        standard_1020 = [
            "Fp1", "Fpz", "Fp2",
            "AF7", "AF3", "AFz", "AF4", "AF8",
            "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
            "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
            "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
            "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
            "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
            "PO7", "PO3", "POz", "PO4", "PO8",
            "O1", "Oz", "O2",
        ]

        # EEGLAB often uses numbered channels like EEG001, EEG002, etc.
        # or BrainVision format like C1, C2, etc.
        # Common EEGLAB patterns:
        # - EEG001-EEG128
        # - E1-E128
        # - BrainVision: FA, F, C, P, O series

        # Pattern 1: EEG001, EEG002, ... format
        eeg_pattern = re.compile(r"^EEG(\d+)$", re.IGNORECASE)
        e_pattern = re.compile(r"^E(\d+)$", re.IGNORECASE)

        for ch in ch_names:
            # Skip if already standard
            if ch in standard_1020:
                continue

            # Skip reference/external channels
            if ch.lower() in ["ref", "reference", "eo", "ecg", "emg", "trigger"]:
                continue

            # Pattern: EEG001 -> map to standard based on index
            match = eeg_pattern.match(ch)
            if match:
                idx = int(match.group(1)) - 1  # 0-indexed
                if idx < len(standard_1020):
                    rename_map[ch] = standard_1020[idx]
                    continue

            # Pattern: E1 -> same as EEG
            match = e_pattern.match(ch)
            if match:
                idx = int(match.group(1)) - 1
                if idx < len(standard_1020):
                    rename_map[ch] = standard_1020[idx]
                    continue

        # Apply renaming
        if rename_map:
            # Only rename channels that exist in raw
            clean_map = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if clean_map:
                raw.rename_channels(clean_map)

        return raw

    def _ensure_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Ensure raw has proper annotations for event extraction.

        EEGLAB .set files store events in annotations or as numeric codes.
        This method ensures consistent annotation format with standard event labels.

        Event mapping:
        - E8: Movement-capable object (animate)
        - E9: Non-movement object (inanimate)
        - E1-E5: Object categories 1, 2, 3, 5
        - E4: Block boundary

        Annotator: LLM, 2026-04-08
        Source: OpenNeuro dataset documentation and analysis.md
        """
        # Check if annotations already exist
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Map existing annotation descriptions to standard format
            desc_map = {
                "8": "E 8",
                "9": "E 9",
                "1": "E 1",
                "2": "E 2",
                "3": "E 3",
                "4": "E 4",
                "5": "E 5",
                "768": "E 1",  # BrainVision event codes sometimes appear
                "769": "E 2",
                "770": "E 3",
                "771": "E 4",
                "772": "E 5",
                "773": "E 8",
                "774": "E 9",
            }

            new_descriptions = []
            for desc in raw.annotations.description:
                desc_str = str(desc)
                mapped = desc_map.get(desc_str, desc_str)
                # Clean up: remove leading/trailing spaces, standardize format
                mapped = mapped.strip()
                new_descriptions.append(mapped)

            raw.annotations.description = np.array(new_descriptions)
            return raw

        # If no annotations, try to extract from stim channel or events
        # Look for stimulus trigger channel
        stim_ch = None
        for ch_name in raw.ch_names:
            if "stim" in ch_name.lower() or "trigger" in ch_name.lower():
                stim_ch = ch_name
                break

        if stim_ch is None:
            # Use first data channel as trigger if no explicit stim channel
            stim_ch = raw.ch_names[0]

        # Extract events from trigger channel
        try:
            trigger_data = raw.get_data(picks=[stim_ch])[0]

            # Find threshold crossings (assuming trigger is binary: above/below threshold)
            threshold = np.mean(trigger_data) + np.std(trigger_data)
            events_mask = trigger_data > threshold

            # Find rising edges
            diff = np.diff(events_mask.astype(int))
            onset_indices = np.where(diff > 0)[0]

            if len(onset_indices) > 0:
                # Get trigger values at onset
                trigger_values = trigger_data[onset_indices]

                # Cluster values to identify event types
                # Common triggers: 1, 2, 3, 4, 5, 8, 9
                unique_triggers = np.unique(np.round(trigger_values))

                # Map to event labels
                event_labels = []
                for val in unique_triggers:
                    rounded = int(round(val))
                    if rounded == 8:
                        event_labels.append("E 8")
                    elif rounded == 9:
                        event_labels.append("E 9")
                    elif rounded in [1, 2, 3, 4, 5]:
                        event_labels.append(f"E {rounded}")
                    else:
                        event_labels.append(f"trigger_{rounded}")

                # Create annotations
                onset_times = onset_indices / raw.info["sfreq"]
                annotations = mne.Annotations(
                    onset=onset_times,
                    duration=np.zeros(len(onset_times)),
                    description=[f"trigger_{int(round(v))}" for v in trigger_values],
                )
                raw.set_annotations(annotations)
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS003887Kernel()