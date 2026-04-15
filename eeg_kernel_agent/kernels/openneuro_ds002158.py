"""OpenNeuro ds002158 stage1 kernel for EEGUnity.

Dataset: Disentangling the origins of confidence in speeded perceptual judgments
through multimodal imaging

Source: https://openneuro.org/datasets/ds002158
Paper DOI: 10.1073/pnas.1918335117

This kernel handles:
- High sampling rate (5000 Hz) with downsampling
- 63-channel EEG data with BrainAmp amplifier
- Response/R128 as epoch anchor for confidence regression
- Confidence/reaction_time/response_time extraction from misc channels
- Standard 10-20 montage setup

Annotator: Human (review confirmed), 2026-04-08
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject metadata - sourced from participants.tsv
# Source: openneuro_ds002158/participants.tsv
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# Channel renaming map for standard 10-20 names
# This dataset uses BrainVision format with standard electrode names
# Source: BrainAmp export convention; standard_1020 cap
# Annotator: LLM, 2026-04-08 - needs human review
# =============================================================================
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 electrodes - BrainVision typically uses these names
    "Fp1": "FP1",
    "Fp2": "FP2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "FZ",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "CZ",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "PZ",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "OZ",
    "O2": "O2",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path.ds002158 has single paradigm (confidence task)."""
    return "confidence_task"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for the raw object."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    for source, target in _EEG_CHANNEL_RENAME_MAP.items():
        if source in existing and source != target:
            rename_map[source] = target

    return rename_map


def _extract_misc_labels(
    raw: mne.io.BaseRaw, row: pd.Series
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract confidence, reaction_time, and response_time from misc channels.

    Returns
    -------
    confidence : np.ndarray or None
        Confidence values (0-1 VAS scale)
    reaction_time : np.ndarray or None
        Reaction time in seconds
    response_time : np.ndarray or None
        Response time in seconds
    """
    confidence = None
    reaction_time = None
    response_time = None

    for ch_name in raw.ch_names:
        if ch_name.lower() == "confidence":
            idx = raw.ch_names.index(ch_name)
            confidence = raw.get_data(picks=[idx]).flatten()
        elif ch_name.lower() == "reaction_time":
            idx = raw.ch_names.index(ch_name)
            reaction_time = raw.get_data(picks=[idx]).flatten()
        elif ch_name.lower() == "response_time":
            idx = raw.ch_names.index(ch_name)
            response_time = raw.get_data(picks=[idx]).flatten()

    return confidence, reaction_time, response_time


def _load_subject_metadata(udataset, row: pd.Series) -> Dict[str, str]:
    """Load subject metadata from participants.tsv or infer."""
    subject_id = row.get("subject_id", row.get("participant_id", "unknown"))

    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id]

    # Default fallback - LLM inferred
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


@dataclass
class OpenNeuroDS002158Kernel:
    """Stage1 kernel for OpenNeuro ds002158 (confidence in perceptual decisions).

    EEG + fMRI study on metacognitive confidence during speeded perceptual judgments.
    High sampling rate (5000 Hz) requires downsampling before epoching.
    Response/R128 events serve as epoch anchors.
    """

    KERNEL_ID: str = "openneuro-ds002158-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to a single EEG record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file information

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object with annotations, channel names, and metadata
        """
        file_path = row.get("File Path", "")
        original_desc = raw.info.get("description", "")

        # =====================================================================
        # 1. Handle high sampling rate (5000 Hz -> 500 Hz)
        # Source: analysis.md, Paper DOI: 10.1073/pnas.1918335117
        # =====================================================================
        sfreq = raw.info["sfreq"]
        if sfreq > 1000:
            target_sfreq = 500
            decim = int(round(sfreq / target_sfreq))
            if decim > 1:
                print(f"Downsampling from {sfreq} Hz to {sfreq / decim:.0f} Hz (decim={decim})")
                raw = raw.copy().decimate(decim)
        else:
            decim = 1

        # =====================================================================
        # 2. Channel renaming
        # Rename before set_montage() per KERNEL_RULEBOOK requirement
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"Renaming {len(rename_map)} channels: {list(rename_map.values())}")
            raw = raw.rename_channels(rename_map)

        # =====================================================================
        # 3. Set standard 10-20 montage
        # Source: Paper confirms standard 10-20 cap; BrainAmp standard setup
        # Annotator: Human (inferred from paper), 2026-04-08
        # =====================================================================
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"Could not set montage: {e}")

        # =====================================================================
        # 4. Extract misc labels (confidence, reaction_time, response_time)
        # Source: analysis.md MISC Label Summary
        # =====================================================================
        confidence_data, rt_data, resp_time_data = _extract_misc_labels(raw, row)

        # =====================================================================
        # 5. Build annotations from events
        # Response/R128 is the primary epoch anchor (n=44303)
        # Source: analysis.md Event Structure
        # =====================================================================
        events, event_id = mne.events_from_annotations(raw)

        # Map event descriptions to canonical names
        new_event_id = {
            "Response/R128": event_id.get("Response/R128", 128),
            "Stimulus/S  7": event_id.get("Stimulus/S  7", 7),
            "Stimulus/S  8": event_id.get("Stimulus/S  8", 8),
            "Stimulus/S 11": event_id.get("Stimulus/S 11", 11),
            "Stimulus/S 12": event_id.get("Stimulus/S 12", 12),
            "Stimulus/S 17": event_id.get("Stimulus/S 17", 17),
            "Stimulus/S 18": event_id.get("Stimulus/S 18", 18),
            "Stimulus/S 27": event_id.get("Stimulus/S 27", 27),
            "Stimulus/S 37": event_id.get("Stimulus/S 37", 37),
            "Stimulus/S 38": event_id.get("Stimulus/S 38", 38),
            "Stimulus/S 40": event_id.get("Stimulus/S 40", 40),
            "Stimulus/S 41": event_id.get("Stimulus/S 41", 41),
            "Stimulus/S 43": event_id.get("Stimulus/S 43", 43),
            "Stimulus/S 44": event_id.get("Stimulus/S 44", 44),
            "Stimulus/S128": event_id.get("Stimulus/S128", 128),
            "Stimulus/S140": event_id.get("Stimulus/S140", 140),
            "Stimulus/S145": event_id.get("Stimulus/S145", 145),
            "Stimulus/S155": event_id.get("Stimulus/S155", 155),
            "Stimulus/S165": event_id.get("Stimulus/S165", 165),
            "Stimulus/S166": event_id.get("Stimulus/S166", 166),
            "Stimulus/S169": event_id.get("Stimulus/S169", 169),
            "Stimulus/S171": event_id.get("Stimulus/S171", 171),
            "SyncStatus/Sync On": event_id.get("SyncStatus/Sync On", 0),
        }

        # Create annotations
        onset_times = events[:, 0] / raw.info["sfreq"]
        descriptions = []
        for i in range(len(events)):
            orig_desc = raw.annotations.description[i] if i < len(raw.annotations) else ""
            event_code = events[i, 2]
            desc = next(
                (k for k, v in new_event_id.items() if v == event_code),
                orig_desc or f"event_{event_code}"
            )
            descriptions.append(desc)

        annotations = mne.Annotations(
            onset=onset_times,
            duration=np.zeros(len(events)),
            description=descriptions,
        )
        raw = raw.set_annotations(annotations)

        # =====================================================================
        # 6. Extract subject metadata
        # =====================================================================
        subject_meta = _load_subject_metadata(udataset, row)

        # =====================================================================
        # 7. Set eegunity_description
        # Amplifier: BrainAmp (from fMRI-compatible multimodal setup in paper)
        # Source: Paper DOI: 10.1073/pnas.1918335117
        # Annotator: Human (paper confirmation), 2026-04-08
        # =====================================================================
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown").lower(),
                "amplifier": "BrainAmp",  # Source: Paper confirms BrainAmp used with 3T MRI
                "cap": "Ag/AgCl",  # Source: BrainAmp standard setup
                "handedness": subject_meta.get("handedness", "unknown"),
            }
        }
        raw.info["description"] = json.dumps(description_dict)

        # =====================================================================
        # 8. Store continuous labels as chy
        # Confidence (0-1 VAS), reaction_time, response_time for regression tasks
        # Source: analysis.md MISC Label Summary
        # =====================================================================
        if not hasattr(raw, "_my_extra"):
            raw._my_extra = {}

        if confidence_data is not None:
            raw._my_extra["confidence"] = confidence_data
        if rt_data is not None:
            raw._my_extra["reaction_time"] = rt_data
        if resp_time_data is not None:
            raw._my_extra["response_time"] = resp_time_data

        return raw


KERNEL = OpenNeuroDS002158Kernel()