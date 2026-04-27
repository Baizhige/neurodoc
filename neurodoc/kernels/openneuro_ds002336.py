"""OpenNeuro DS002336 stage1 kernel for EEGUnity.

Motor imagery neurofeedback dataset with simultaneous EEG-fMRI acquisition.
64-channel BrainVision data recorded at 5000 Hz inside MRI scanner.

Source: https://openneuro.org/datasets/ds002336
Paper: 10.1038/s41597-020-0498-3
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 10-20 64-channel layout (extended)
# Source: standard 10-20 system extended for 64-channel caps
# Annotator: LLM 推断，需人类复核
_EEG_CHANNEL_ORDER = [
    "Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO9", "PO7", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F9", "F10",
    "M1", "M2"
]


# Events to exclude (MRI artifacts and admin markers)
_MRI_ARTIFACT_KEYWORDS = [
    "TPULSE", "Pulse Artifact", "Time 0", "R128", "admin"
]


@dataclass
class OpenNeuroDS002336Kernel:
    """Stage1 kernel for OpenNeuro DS002336 dataset."""

    KERNEL_ID: str = "openneuro-ds002336-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object (BrainVision format).
        row
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized channels and annotations.
        """
        file_path = row.get("File Path", "")

        # Phase 1: Rename channels to standard 10-20 names BEFORE set_montage()
        raw = self._rename_channels(raw)

        # Phase 2: Set standard 10-20 montage
        raw = self._set_montage(raw)

        # Phase 3: Process events (annotations)
        raw = self._process_annotations(raw)

        # Phase 4: Update description with metadata
        raw = self._update_description(raw)

        return raw

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 nomenclature."""
        original_ch_names = raw.ch_names.copy()

        # Try to detect channel naming pattern and map accordingly
        rename_map: Dict[str, str] = {}

        # Detect if channels are numbered (EEG001, EEG002, ...) or use other patterns
        numbered_pattern = re.compile(r'^EEG-?\d+$', re.IGNORECASE)
        has_numbers = any(
            numbered_pattern.match(ch) for ch in original_ch_names
        )

        if has_numbers:
            # Extract and sort channel numbers
            channel_pairs: Dict[int, str] = {}
            for ch in original_ch_names:
                match = numbered_pattern.match(ch)
                if match:
                    # Extract number
                    num_str = re.search(r'\d+', ch).group()
                    channel_pairs[int(num_str)] = ch

            sorted_channels = sorted(channel_pairs.items())
            n_eeg = len(sorted_channels)

            # Map to standard 10-20 names
            if n_eeg <= len(_EEG_CHANNEL_ORDER):
                for idx, (_, original_name) in enumerate(sorted_channels):
                    if original_name != _EEG_CHANNEL_ORDER[idx]:
                        rename_map[original_name] = _EEG_CHANNEL_ORDER[idx]
            else:
                # If more channels than standard order, keep original names
                pass
        else:
            # Try to match based on common alias patterns
            alias_groups = [
                ("Fp1", ["Fp1", "EEG-Fp1", "FP1"]),
                ("Fp2", ["Fp2", "EEG-Fp2", "FP2"]),
                ("Fpz", ["Fpz", "EEG-Fpz", "FPz"]),
                ("F7", ["F7", "F3'", "F5'"]),
                ("F3", ["F3", "F1'"]),
                ("Fz", ["Fz", "F2'"]),
                ("F4", ["F4", "F2'"]),
                ("F8", ["F8", "F4'"]),
                ("T7", ["T7", "T3", "TA1"]),
                ("C3", ["C3", "C1'"]),
                ("Cz", ["Cz", "C2'"]),
                ("C4", ["C4", "C2'"]),
                ("T8", ["T8", "T4", "TA2"]),
                ("P7", ["P7", "P3'"]),
                ("P3", ["P3", "P1'"]),
                ("Pz", ["Pz", "P2'"]),
                ("P4", ["P4", "P2'"]),
                ("P8", ["P8", "P4'"]),
                ("O1", ["O1", "O9"]),
                ("Oz", ["Oz"]),
                ("O2", ["O2", "O10"]),
                ("M1", ["M1", "A1", "LeftMastoid", "LM"]),
                ("M2", ["M2", "A2", "RightMastoid", "RM"]),
            ]

            for target, aliases in alias_groups:
                for original in aliases:
                    if original in original_ch_names and original != target:
                        rename_map[original] = target
                        break

        # Apply renames
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage for EEG channels."""
        try:
            # Use standard 10-20 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage fails (e.g., channels not in standard set), skip
            pass

        return raw

    def _process_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process annotations: standardize names and exclude MRI artifacts."""
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        # Get current annotations
        descriptions = np.array(raw.annotations.description)
        onsets = raw.annotations.onset.copy()
        durations = raw.annotations.duration.copy()

        # Standardize event names and filter out MRI artifacts
        new_descriptions: List[str] = []

        for desc in descriptions:
            desc_upper = desc.upper()

            # Check if this is an MRI artifact marker to exclude
            is_artifact = any(
                keyword.upper() in desc_upper
                for keyword in _MRI_ARTIFACT_KEYWORDS
            )

            if is_artifact:
                # Skip MRI artifact markers
                continue

            # Standardize BrainVision event names
            standardized = self._standardize_event_name(desc)
            new_descriptions.append(standardized)

        # Filter annotations
        valid_mask = [
            not any(
                kw.upper() in desc.upper()
                for kw in _MRI_ARTIFACT_KEYWORDS
            )
            for desc in descriptions
        ]

        filtered_onsets = onsets[valid_mask]
        filtered_durations = durations[valid_mask]
        filtered_descriptions = [
            self._standardize_event_name(desc)
            for desc in descriptions[valid_mask]
        ]

        if len(filtered_descriptions) > 0:
            new_annotations = mne.Annotations(
                onset=filtered_onsets,
                duration=filtered_durations,
                description=filtered_descriptions,
            )
            raw.set_annotations(new_annotations)
        else:
            raw.set_annotations(mne.Annotations(
                onset=[], duration=[], description=[]
            ))

        return raw

    def _standardize_event_name(self, original: str) -> str:
        """Convert BrainVision event names to canonical names."""
        original_stripped = original.strip()

        # BrainVision format mapping
        event_map = {
            "Rest": "Rest",
            "Task-NF": "Task-NF",
            "Task-ME": "Task-ME",
            "Task-MI": "Task-MI",
            "S 99": "Rest",
            "S 2": "Task-NF",
            "S  2": "Task-NF",
            "S 99": "Rest",
        }

        # Check direct mapping
        if original_stripped in event_map:
            return event_map[original_stripped]

        # Check case-insensitive
        for key, value in event_map.items():
            if key.lower() == original_stripped.lower():
                return value

        # Extract numeric code from "Stimulus/S xx" format
        stimulus_match = re.match(r'[Ss]timulus[/ ]?[Ss]? ?(\d+)', original_stripped)
        if stimulus_match:
            code = int(stimulus_match.group(1))
            if code == 99:
                return "Rest"
            elif code == 2:
                return "Task-NF"
            else:
                return f"Stimulus/S {code}"

        # Extract numeric code from "Response/R xxx" format
        response_match = re.match(r'[Rr]esponse[/ ]?[Rr]? ?(\d+)', original_stripped)
        if response_match:
            code = int(response_match.group(1))
            if code == 128:
                return "admin: marker-128"
            else:
                return f"Response/R {code}"

        # Keep original if no mapping found
        return original_stripped

    def _update_description(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Update raw.info['description'] with standardized metadata."""
        # Extract subject info from row if available
        subject_id = str(row.get("Subject", "unknown"))
        session_id = str(row.get("Session", "unknown"))

        # Get device info from data if available
        original_desc = raw.info.get("description", "")

        # Try to infer device from channel info or data
        # Based on paper: BrainAmp MR plus (EEG-fMRI compatible amplifier)
        # Source: 10.1038/s41597-020-0498-3
        # Annotator: LLM 推断，需人类复核
        amplifier = "BrainAmp MR plus"

        # Build description dict
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核 - dataset documentation does not specify age
                "sex": "unknown",  # LLM 推断，需人类复核 - dataset documentation does not specify sex
                "amplifier": amplifier,
                "cap": "unknown",  # LLM 推断，需人类复核 - cap type not specified in available documentation
                "handedness": "unknown",  # LLM 推断，需人类复核 - handedness not specified in available documentation
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS002336Kernel()