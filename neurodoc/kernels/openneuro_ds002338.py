"""OpenNeuro DS002338 stage1 kernel for EEGUnity.

Dataset: Motor imagery neurofeedback with simultaneous EEG-fMRI.
64-channel EEG recorded at 5000 Hz using BrainVision system.

Source: https://openneuro.org/datasets/ds002338
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Source: DOI 10.1038/s41597-020-0498-3 (dataset descriptor)
# LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    for i in range(1, 17)
}

# Standard 64-channel names for 64-channel MR-compatible EEG cap
# Source: BrainVision electrode layout documentation
# LLM 推断，需人类复核
_64CH_STANDARD_NAMES = [
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

# BrainVision vendor channel naming pattern (e.g., "EEG 001", "EEG 064")
# LLM 推断，需人类复核
_VENDOR_CHANNEL_PATTERN = "EEG {:03d}"


def _build_brainvision_channel_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Map BrainVision vendor channel names to standard 10-20 names.

    BrainVision files use "EEG 001", "EEG 002" ... "EEG 064" naming.
    This maps them to standard 10-20 electrode positions.
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names

    for i, std_name in enumerate(_64CH_STANDARD_NAMES, start=1):
        vendor_name = _VENDOR_CHANNEL_PATTERN.format(i)
        if vendor_name in existing_names:
            rename_map[vendor_name] = std_name

    return rename_map


def _map_brainvision_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Map BrainVision marker annotations to canonical event names.

    BrainVision markers include:
    - S 99: Rest block start (mapped to 'Rest')
    - S 2: Task-NF block start (mapped to 'Task-NF')
    - TPULSE/*, Response/*, admin codes: excluded
    """
    original_annotations = raw.annotations

    if original_annotations is None or len(original_annotations) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])

    # Event mapping for paradigm-relevant markers
    marker_map = {
        "Stimulus/S 99": "Rest",
        "Stimulus/S  2": "Task-NF",  # Note: double space in some BV exports
        "Stimulus/S 2": "Task-NF",
    }

    keep_indices = []
    keep_descriptions = []

    for idx, desc in enumerate(original_annotations.description):
        mapped_desc = marker_map.get(desc, None)
        if mapped_desc is not None:
            keep_indices.append(idx)
            keep_descriptions.append(mapped_desc)

    if not keep_indices:
        return mne.Annotations(onset=[], duration=[], description=[])

    keep_onsets = np.array(original_annotations.onset)[keep_indices]
    keep_durations = np.array(original_annotations.duration)[keep_indices]

    return mne.Annotations(
        onset=keep_onsets.tolist(),
        duration=keep_durations.tolist(),
        description=keep_descriptions,
    )


@dataclass
class OpenNeuroDS002338Kernel:
    """Stage1 kernel for OpenNeuro DS002338 dataset.

    Handles BrainVision format EEG-fMRI data with motor imagery
    neurofeedback paradigm. Excludes MRI gradient artifacts marked
    by TPULSE markers.
    """

    KERNEL_ID: str = "openneuro-ds002338-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
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
            Preprocessed raw object with standardized channel names,
            annotations, and metadata.
        """
        file_path = row["File Path"]

        # Extract subject ID from file path
        subject_id = "unknown"
        if "sub-" in file_path:
            parts = file_path.split("sub-")
            if len(parts) > 1:
                subject_id = "sub-" + parts[1].split("/")[0].split("\\")[0]

        # Get subject info
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        })

        # Build eegunity_description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp MR plus",  # Source: DOI 10.1038/s41597-020-0498-3
                "cap": "Ag/AgCl",  # Source: DOI 10.1038/s41597-020-0498-3
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names BEFORE set_montage()
        rename_map = _build_brainvision_channel_map(raw)
        if rename_map:
            channel_count = len(rename_map)
            raw.rename_channels(rename_map)
            print(f"[DS002338] Renamed {channel_count} channels to standard 10-20 names")

        # Set standard 1020 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
            print("[DS002338] Applied standard_1020 montage")
        except Exception as e:
            print(f"[DS002338] Warning: Could not set montage: {e}")

        # Map BrainVision annotations to canonical event names
        # This excludes MRI artifacts (TPULSE/*, Response/*, admin codes)
        new_annotations = _map_brainvision_annotations(raw)
        raw.set_annotations(new_annotations)

        event_counts = {}
        for desc in new_annotations.description:
            event_counts[desc] = event_counts.get(desc, 0) + 1
        print(f"[DS002338] Events after filtering: {event_counts}")

        # High-pass filter to remove MRI gradient artifacts (if needed)
        # MRI artifacts are below 100 Hz; motor imagery is 8-30 Hz
        #raw.filter(l_freq=1.0, h_freq=None, fir_design="firwin")

        return raw


KERNEL = OpenNeuroDS002338Kernel()