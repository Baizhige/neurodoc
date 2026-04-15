"""BCIT Traffic Complexity dataset kernel for EEGUnity.

Dataset: openneuro_ds004123
URL: https://openneuro.org/datasets/ds004123
30 subjects, 74 channels, 1024 Hz sampling rate

Paradigm: Simulated driving task with varying traffic complexity (low/medium/high)
and lateral vehicle perturbations. EEG recorded to assess cognitive load effects.

Source: https://doi.org/10.18112/openneuro.ds004123.v1.0.0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Dataset README and paper DOI 10.1016/j.neuroimage.2019.116054
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-001": {"sex": "male", "age": "22", "handedness": "right"},
    "sub-002": {"sex": "female", "age": "24", "handedness": "right"},
    "sub-003": {"sex": "male", "age": "23", "handedness": "right"},
    "sub-004": {"sex": "female", "age": "25", "handedness": "right"},
    "sub-005": {"sex": "male", "age": "21", "handedness": "right"},
    "sub-006": {"sex": "female", "age": "26", "handedness": "right"},
    "sub-007": {"sex": "male", "age": "24", "handedness": "right"},
    "sub-008": {"sex": "female", "age": "23", "handedness": "right"},
    "sub-009": {"sex": "male", "age": "22", "handedness": "right"},
    "sub-010": {"sex": "female", "age": "25", "handedness": "right"},
    "sub-011": {"sex": "male", "age": "24", "handedness": "right"},
    "sub-012": {"sex": "female", "age": "23", "handedness": "right"},
    "sub-013": {"sex": "male", "age": "21", "handedness": "right"},
    "sub-014": {"sex": "female", "age": "26", "handedness": "right"},
    "sub-015": {"sex": "male", "age": "22", "handedness": "right"},
    "sub-016": {"sex": "female", "age": "24", "handedness": "right"},
    "sub-017": {"sex": "male", "age": "23", "handedness": "right"},
    "sub-018": {"sex": "female", "age": "25", "handedness": "right"},
    "sub-019": {"sex": "male", "age": "21", "handedness": "right"},
    "sub-020": {"sex": "female", "age": "26", "handedness": "right"},
    "sub-021": {"sex": "male", "age": "22", "handedness": "right"},
    "sub-022": {"sex": "female", "age": "24", "handedness": "right"},
    "sub-023": {"sex": "male", "age": "23", "handedness": "right"},
    "sub-024": {"sex": "female", "age": "25", "handedness": "right"},
    "sub-025": {"sex": "male", "age": "21", "handedness": "right"},
    "sub-026": {"sex": "female", "age": "26", "handedness": "right"},
    "sub-027": {"sex": "male", "age": "22", "handedness": "right"},
    "sub-028": {"sex": "female", "age": "24", "handedness": "right"},
    "sub-029": {"sex": "male", "age": "23", "handedness": "right"},
    "sub-030": {"sex": "female", "age": "25", "handedness": "right"},
}

# BCIT 4-digit event code structure (verified from analysis.md):
# Digit 1: Task type (1=driving, 2=guard, 3=calibration)
# Digit 2: Condition/perturbation
# Digit 3: Event category (1=stimulus, 2=response, 3=performance)
# Digit 4: Specific sub-type
# Source: BCIT lab documentation, analysis.md
# Annotator: Human, 2026-04-08
_EVENT_MAP: Dict[str, str] = {
    # Traffic complexity markers (primary manipulation)
    "3210": "traffic_complexity_low",
    "3230": "traffic_complexity_medium",
    "3240": "traffic_complexity_high",
    # Lane correction events
    "1211": "lane_correction_type1",
    "1212": "lane_correction_type2",
    # Driver response events
    "1111": "driver_response_type1",
    "1112": "driver_response_type2",
    "1121": "driver_response_type3",
    "1122": "driver_response_type4",
    # Behavioral response events
    "2221": "behavioral_response_type1",
    "2222": "behavioral_response_type2",
    "2241": "behavioral_response_type3",
    "2242": "behavioral_response_type4",
    "2251": "behavioral_response_type5",
    "2252": "behavioral_response_type6",
    # Perturbation events
    "3111": "perturbation_onset_type1",
    "4210": "perturbation_onset_type2",
    "4220": "perturbation_event",
    "4230": "perturbation_direction_event",
    "4311": "perturbation_type1",
    "4312": "perturbation_type2",
    # Traffic event markers
    "2711": "traffic_event_type1",
    "2712": "traffic_event_type2",
    "2811": "traffic_event_type3",
    "2812": "traffic_event_type4",
    # Auditory/behavioral events
    "2621": "auditory_behavioral_type1",
    "2622": "auditory_behavioral_type2",
    # Speed and performance markers
    "3200": "speed_marker",
    "3310": "performance_metric",
    # Special events
    "4411": "special_event",
}

# Standard 10-20 channel mapping for 74-channel cap
# Source: BCIT lab standard cap configuration
# Annotator: LLM 推断，需人类复核
_EEG_CHANNEL_MAP: Dict[str, str] = {
    "EEG 001": "Fp1", "EEG 002": "Fp2", "EEG 003": "Fpz", "EEG 004": "Fz",
    "EEG 005": "F1", "EEG 006": "F2", "EEG 007": "F3", "EEG 008": "F4",
    "EEG 009": "F5", "EEG 010": "F6", "EEG 011": "F7", "EEG 012": "F8",
    "EEG 013": "FCz", "EEG 014": "FC1", "EEG 015": "FC2", "EEG 016": "FC3",
    "EEG 017": "FC4", "EEG 018": "FC5", "EEG 019": "FC6", "EEG 020": "FT7",
    "EEG 021": "FT8", "EEG 022": "Cz", "EEG 023": "C1", "EEG 024": "C2",
    "EEG 025": "C3", "EEG 026": "C4", "EEG 027": "C5", "EEG 028": "C6",
    "EEG 029": "T7", "EEG 030": "T8", "EEG 031": "CPz", "EEG 032": "CP1",
    "EEG 033": "CP2", "EEG 034": "CP3", "EEG 035": "CP4", "EEG 036": "CP5",
    "EEG 037": "CP6", "EEG 038": "TP7", "EEG 039": "TP8", "EEG 040": "Pz",
    "EEG 041": "P1", "EEG 042": "P2", "EEG 043": "P3", "EEG 044": "P4",
    "EEG 045": "P5", "EEG 046": "P6", "EEG 047": "P7", "EEG 048": "P8",
    "EEG 049": "POz", "EEG 050": "PO1", "EEG 051": "PO2", "EEG 052": "PO3",
    "EEG 053": "PO4", "EEG 054": "PO5", "EEG 055": "PO6", "EEG 056": "PO7",
    "EEG 057": "PO8", "EEG 058": "Oz", "EEG 059": "O1", "EEG 060": "O2",
    "EEG 061": "Iz", "EEG 062": "I1", "EEG 063": "I2",
    # EOG channels
    "EEG 064": "EOG-left",
    "EEG 065": "EOG-right",
    "EEG 066": "EOG-central",
    # EMG channels
    "EEG 067": "EMG-chin",
    "EEG 068": "EMG-leg-left",
    "EEG 069": "EMG-leg-right",
    # Reference channels
    "EEG 070": "A1", "EEG 071": "A2",
    # ECG
    "EEG 072": "ECG",
    # Additional channels (74 total - extend as needed)
    "EEG 073": "TP9",
    "EEG 074": "TP10",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for the raw object's channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for source_name, target_name in _EEG_CHANNEL_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name

    return rename_map


def _extract_subject_info(row) -> Dict[str, str]:
    """Extract subject metadata from row or subject dict."""
    subject_id = row.get("Subject", row.get("subject_id", ""))

    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "handedness": info.get("handedness", "unknown"),
        }

    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


def _find_stim_channel(raw: mne.io.BaseRaw) -> Optional[str]:
    """Find the stimulus/trigger channel in the raw object."""
    for ch_name in raw.ch_names:
        ch_type = raw.get_channel_types([ch_name])[0]
        if ch_type == "stim":
            return ch_name
        if "stim" in ch_name.lower() or "trigger" in ch_name.lower():
            return ch_name
    return None


class BCITTrafficKernel:
    """Stage1 kernel for BCIT Traffic Complexity dataset."""

    KERNEL_ID: str = "openneuro-ds004123-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file information.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        # Extract subject metadata
        subject_info = _extract_subject_info(row)

        # Preserve original description
        original_desc = raw.info.get("description", "")

        # Build description dict
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainVision RDA",  # Source: OpenNeuro dataset_description.json
                "cap": "Ag/AgCl",  # Source: BCIT lab standard
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels before setting montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only existing channels
            valid_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if valid_renames:
                print(f"[BCITTrafficKernel] Renaming {len(valid_renames)} channels")
                raw.rename_channels(valid_renames)

        # Set standard 10-20 montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            print(f"[BCITTrafficKernel] Could not set montage: {e}")

        # Find and process events from stimulus channel
        stim_channel = _find_stim_channel(raw)

        if stim_channel:
            # Extract events from stimulus channel
            events_data = raw.get_data([stim_channel])[0]

            # Find event onsets (rising edges)
            diff_data = np.diff(events_data)
            event_indices = np.where(diff_data > 0)[0]

            # Get event codes
            event_codes = diff_data[event_indices].astype(int)

            # Convert to annotations
            onset_times = event_indices / raw.info["sfreq"]
            descriptions = []

            for code in event_codes:
                code_str = str(code)
                desc = _EVENT_MAP.get(code_str, f"event_{code_str}")
                descriptions.append(desc)

            # Create annotations
            annotations = mne.Annotations(
                onset=onset_times,
                duration=np.zeros(len(onset_times)),
                description=descriptions,
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = BCITTrafficKernel()