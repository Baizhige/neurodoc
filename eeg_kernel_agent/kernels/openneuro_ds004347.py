"""OpenNeuro DS004347 stage1 kernel for EEGUnity.

Symmetry perception and affective responses study.
- 24 subjects, 73 channels (EEG + EMG/EOG)
- Sampling rate: 512 Hz
- Event-based epoching with event_1 (symmetry) and event_3 (asymmetry)

Source: https://openneuro.org/datasets/ds004347
Reference: https://doi.org/10.1016/j.neuropsychologia.2012.10.003
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import mne


# Source: paper DOI 10.1016/j.neuropsychologia.2012.10.003
# Channel names follow BrainVision standard layout with prefixes
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_ALIASES: List[List[str]] = [
    ["Fp1", "Fp 1", "EEG Fp1"],
    ["Fz", "Fz", "EEG Fz"],
    ["Fp2", "Fp 2", "EEG Fp2"],
    ["F3", "F3", "EEG F3"],
    ["F4", "F4", "EEG F4"],
    ["F7", "F7", "EEG F7"],
    ["F8", "F8", "EEG F8"],
    ["FC5", "FC5", "EEG FC5"],
    ["FC1", "FC1", "EEG FC1"],
    ["FC2", "FC2", "EEG FC2"],
    ["FC6", "FC6", "EEG FC6"],
    ["Cz", "Cz", "EEG Cz"],
    ["C3", "C3", "EEG C3"],
    ["C4", "C4", "EEG C4"],
    ["T7", "T7", "EEG T7"],
    ["T8", "T8", "EEG T8"],
    ["CP5", "CP5", "EEG CP5"],
    ["CP1", "CP1", "EEG CP1"],
    ["CP2", "CP2", "EEG CP2"],
    ["CP6", "CP6", "EEG CP6"],
    ["Pz", "Pz", "EEG Pz"],
    ["P3", "P3", "EEG P3"],
    ["P4", "P4", "EEG P4"],
    ["P7", "P7", "EEG P7"],
    ["P8", "P8", "EEG P8"],
    ["POz", "POz", "EEG POz"],
    ["O1", "O1", "EEG O1"],
    ["O2", "O2", "EEG O2"],
    ["Oz", "Oz", "EEG Oz"],
    ["AF7", "AF7", "EEG AF7"],
    ["AF3", "AF3", "EEG AF3"],
    ["AF4", "AF4", "EEG AF4"],
    ["AF8", "AF8", "EEG AF8"],
    ["F1", "F1", "EEG F1"],
    ["F2", "F2", "EEG F2"],
    ["F5", "F5", "EEG F5"],
    ["F6", "F6", "EEG F6"],
    ["FT7", "FT7", "EEG FT7"],
    ["FT8", "FT8", "EEG FT8"],
    ["C1", "C1", "EEG C1"],
    ["C2", "C2", "EEG C2"],
    ["C5", "C5", "EEG C5"],
    ["C6", "C6", "EEG C6"],
    ["TP7", "TP7", "EEG TP7"],
    ["TP8", "TP8", "EEG TP8"],
    ["TP9", "TP9", "EEG TP9"],
    ["TP10", "TP10", "EEG TP10"],
    ["P1", "P1", "EEG P1"],
    ["P2", "P2", "EEG P2"],
    ["P5", "P5", "EEG P5"],
    ["P6", "P6", "EEG P6"],
    ["PO3", "PO3", "EEG PO3"],
    ["PO4", "PO4", "EEG PO4"],
    ["PO7", "PO7", "EEG PO7"],
    ["PO8", "PO8", "EEG PO8"],
    ["PO9", "PO9", "EEG PO9"],
    ["PO10", "PO10", "EEG PO10"],
]

# EMG/EOG channel patterns to exclude
# Source: dataset description - 73 channels includes EMG/EOG
# Annotator: LLM, 2026-04-08
_NON_EEG_PATTERNS = [
    "EMG",
    "EOG",
    "Trigger",
    "SC",
    "Resp",
    "HR",
    "GSR",
    "Status",
    "MISC",
]


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map from raw ch_names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    for aliases in _EEG_CHANNEL_ALIASES:
        target = aliases[0]
        for alias in aliases:
            if alias in existing:
                if alias != target:
                    rename_map[alias] = target
                break

    return rename_map


def _is_eeg_channel(ch_name: str) -> bool:
    """Check if channel is an EEG channel (exclude EMG/EOG/misc)."""
    ch_upper = ch_name.upper()
    for pattern in _NON_EEG_PATTERNS:
        if pattern.upper() in ch_upper:
            return False
    return True


def _load_raw_data(file_path: str) -> mne.io.BaseRaw:
    """Load raw EEG data from BrainVision format."""
    # Try BrainVision format first
    if file_path.endswith((".eeg", ".vhdr", ".vmrk")):
        return mne.io.read_raw_brainvision(file_path, preload=False, verbose=False)
    # Try EDF format
    if file_path.endswith(".edf"):
        return mne.io.read_raw_edf(file_path, preload=False, verbose=False)
    # Fallback: let MNE auto-detect
    return mne.io.read_raw(file_path, preload=False, verbose=False)


@dataclass
class OpenNeuroDS004347Kernel:
    """Stage1 kernel for OpenNeuro DS004347 dataset."""

    KERNEL_ID: str = "openneuro-ds004347-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded from file
        row : Locator row with File Path information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw data with updated metadata
        """
        # Step 1: Rename channels to standard 10-20 names (before set_montage)
        rename_map = _build_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map, verbose=False)

        # Step 2: Try to set montage if channels match standard 1020
        try:
            # Only set montage for channels that are in the standard montage
            available_channels = [
                ch for ch in raw.ch_names
                if ch in mne.channels.make_standard_montage("standard_1020").ch_names
            ]
            if len(available_channels) >= 20:
                raw.set_montage("standard_1020", on_missing="ignore", verbose=False)
        except Exception:
            pass

        # Step 3: Extract or infer subject metadata
        # All values are "unknown" since no participants.tsv in OpenNeuro BIDS structure
        # LLM 推断，需人类复核
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",  # LLM 推断，需人类复核
            "cap": "unknown",  # LLM 推断，需人类复核
            "handedness": "unknown",
        }

        # Step 4: Update description field with eegunity metadata
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = str(original_desc)

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": subject_info,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Step 5: Process events if present in the file
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)

            # Map event IDs to meaningful labels
            # event_1 = symmetry condition, event_3 = asymmetry condition
            # Source: Classical Task 1 definition
            event_label_map = {
                "event_1": "symmetry",
                "event_3": "asymmetry",
            }

            # Create new annotations with descriptive labels
            new_descriptions = []
            for annot in raw.annotations:
                desc = str(annot["description"])
                if desc in event_label_map:
                    new_descriptions.append(event_label_map[desc])
                elif desc.startswith("event_"):
                    new_descriptions.append(desc)
                else:
                    new_descriptions.append(desc)

            if new_descriptions:
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annotations, verbose=False)

        except Exception:
            # No readable events found - set admin marker
            # This matches the "no_events" event structure from analysis.md
            admin_annotations = mne.Annotations(
                onset=[0.0],
                duration=[raw.n_times / raw.info["sfreq"]],
                description=["no_events"],
                orig_time=None,
            )
            raw.set_annotations(admin_annotations, verbose=False)

        return raw


KERNEL = OpenNeuroDS004347Kernel()