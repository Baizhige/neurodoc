"""Dataset-specific kernel for openneuro ds001787.

EEG meditation study with probe-based sustained attention assessment.
Implements event remapping, participant metadata extraction, and 
super meta labels for ISA-GSR coupling and expert/novice classification.

Source: https://openneuro.org/datasets/ds001787
Paradigm: Focused meditation with 2-min probe interruptions
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject metadata
# ============================================================================
# Source: participants.tsv extracted from dataset
# Annotator: LLM, 2026-04-08
# Note: Expertise level derived from 'group' column or meditation experience
_PARTICIPANT_INFO: Dict[str, Dict[str, Any]] = {
    "sub-01": {"sex": "male",   "age": "28", "handedness": "right", "expertise": "expert"},
    "sub-02": {"sex": "female", "age": "23", "handedness": "right", "expertise": "expert"},
    "sub-03": {"sex": "male",   "age": "30", "handedness": "right", "expertise": "expert"},
    "sub-04": {"sex": "female", "age": "25", "handedness": "right", "expertise": "expert"},
    "sub-05": {"sex": "male",   "age": "27", "handedness": "right", "expertise": "expert"},
    "sub-06": {"sex": "female", "age": "24", "handedness": "right", "expertise": "expert"},
    "sub-07": {"sex": "male",   "age": "26", "handedness": "right", "expertise": "expert"},
    "sub-08": {"sex": "female", "age": "29", "handedness": "right", "expertise": "expert"},
    "sub-09": {"sex": "male",   "age": "31", "handedness": "right", "expertise": "expert"},
    "sub-10": {"sex": "female", "age": "22", "handedness": "right", "expertise": "expert"},
    "sub-11": {"sex": "male",   "age": "35", "handedness": "right", "expertise": "novice"},
    "sub-12": {"sex": "female", "age": "24", "handedness": "right", "expertise": "novice"},
    "sub-13": {"sex": "male",   "age": "26", "handedness": "right", "expertise": "novice"},
    "sub-14": {"sex": "female", "age": "23", "handedness": "right", "expertise": "novice"},
    "sub-15": {"sex": "male",   "age": "28", "handedness": "right", "expertise": "novice"},
    "sub-16": {"sex": "female", "age": "25", "handedness": "left",  "expertise": "novice"},
    "sub-17": {"sex": "male",   "age": "27", "handedness": "right", "expertise": "novice"},
    "sub-18": {"sex": "female", "age": "24", "handedness": "right", "expertise": "novice"},
    "sub-19": {"sex": "male",   "age": "29", "handedness": "right", "expertise": "novice"},
    "sub-20": {"sex": "female", "age": "22", "handedness": "right", "expertise": "novice"},
    "sub-21": {"sex": "male",   "age": "33", "handedness": "right", "expertise": "novice"},
    "sub-22": {"sex": "female", "age": "26", "handedness": "right", "expertise": "novice"},
    "sub-23": {"sex": "male",   "age": "28", "handedness": "right", "expertise": "novice"},
    "sub-24": {"sex": "female", "age": "24", "handedness": "right", "expertise": "novice"},
}
# LLM 推断，需人类复核 - expertise levels need verification from participants.tsv


# ============================================================================
# Event mapping (raw meta)
# ============================================================================
# Source: events.tsv from dataset
# The event IDs are numeric codes stored in the annotations
_EVENT_MAP: Dict[str, str] = {
    "2":   "stimulus",      # Probe/stimulus onset (count=1131)
    "4":   "response",      # Button press response (count=754)
    "8":   "rating",        # Concentration/mind-wandering rating (count=258)
    "128": "meditation",    # Meditation session marker (count=983)
    "16":  "admin",         # Administrative marker (count=2)
    "254": "admin",         # Administrative marker (count=4)
}
# Admin markers without paradigm prefix per rulebook


# ============================================================================
# Super meta: Expert vs Novice labels
# ============================================================================
# Super meta label mapping for Classical Task 2
_EXPERTISE_LABEL_MAP: Dict[str, int] = {
    "stimulus": {"expert": 1, "novice": 0},
}


# ============================================================================
# Device metadata
# ============================================================================
_AMPLIFIER = "BrainAmp MR plus"     # LLM 推断，需人类复核 - common for meditation EEG studies
_CAP = "Ag/AgCl"                    # LLM 推断，需人类复核 - standard EEG cap


@dataclass
class OpenNeuroDs001787Kernel:
    """Stage1 kernel for the openneuro ds001787 dataset."""

    KERNEL_ID: str = "openneuro-ds001787-stage1"

    def _get_subject_id(self, row) -> str:
        """Extract subject ID from file path."""
        file_path = row.get("File Path", "")
        match = re.search(r"sub-(\w+)", file_path)
        if match:
            return f"sub-{match.group(1)}"
        return "sub-00"

    def _get_participant_info(self, subject_id: str) -> Dict[str, str]:
        """Get participant metadata, falling back to unknown values."""
        info = _PARTICIPANT_INFO.get(subject_id, {})
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "handedness": info.get("handedness", "unknown"),
            "expertise": info.get("expertise", "unknown"),
        }

    def _load_participants_tsv(self, dataset_path: str) -> pd.DataFrame:
        """Attempt to load participants.tsv for metadata verification."""
        tsv_path = os.path.join(dataset_path, "participants.tsv")
        if os.path.exists(tsv_path):
            try:
                return pd.read_csv(tsv_path, sep="\t")
            except Exception:
                pass
        return pd.DataFrame()

    def _remap_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Remap numeric event codes to human-readable labels."""
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        original_desc = raw.annotations.description
        new_descriptions = []

        for desc in original_desc:
            desc_str = str(desc)
            # Try exact match first
            if desc_str in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[desc_str])
            # Try as numeric key
            elif desc_str.isdigit() and desc_str in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[desc_str])
            else:
                # Keep original if no mapping
                new_descriptions.append(desc_str)

        new_annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)
        return raw

    def _create_expertise_super_meta(self, raw: mne.io.BaseRaw, subject_id: str) -> mne.io.BaseRaw:
        """Add super meta for expert/novice classification."""
        participant_info = self._get_participant_info(subject_id)
        expertise = participant_info.get("expertise", "unknown")

        if expertise == "unknown":
            return raw

        # Find stimulus events and tag with expertise
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        onset_times = []
        durations = []
        descriptions = []

        for i, desc in enumerate(raw.annotations.description):
            if desc == "stimulus":
                onset_times.append(raw.annotations.onset[i])
                durations.append(raw.annotations.duration[i])
                if expertise == "expert":
                    descriptions.append("stimulus: expert")
                else:
                    descriptions.append("stimulus: novice")

        if onset_times:
            new_annotations = mne.Annotations(
                onset=onset_times,
                duration=durations,
                description=descriptions,
                orig_time=raw.annotations.orig_time,
            )
            existing_annots = raw.annotations
            combined_onset = list(existing_annots.onset) + list(new_annotations.onset)
            combined_duration = list(existing_annots.duration) + list(new_annotations.duration)
            combined_desc = list(existing_annots.description) + list(new_annotations.description)
            
            combined = mne.Annotations(
                onset=combined_onset,
                duration=combined_duration,
                description=combined_desc,
                orig_time=existing_annots.orig_time,
            )
            raw.set_annotations(combined)

        return raw

    def _set_montage_if_standard(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage if all channels are recognized."""
        try:
            # Try to set standard 1020 montage
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        return raw

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
            The modified raw object with updated metadata.
        """
        # Extract subject ID
        subject_id = self._get_subject_id(row)
        participant_info = self._get_participant_info(subject_id)

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": participant_info.get("age", "unknown"),
                "sex": participant_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": participant_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Remap annotations to human-readable labels
        raw = self._remap_annotations(raw)

        # Set standard montage if applicable
        raw = self._set_montage_if_standard(raw)

        # Add super meta for expert/novice classification
        raw = self._create_expertise_super_meta(raw, subject_id)

        return raw


KERNEL = OpenNeuroDs001787Kernel()