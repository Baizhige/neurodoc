"""OpenNeuro DS001849 stage1 kernel for EEGUnity.

Resting-state EEG data recorded with Transcranial Magnetic Stimulation (TMS).
30-channel EEG at 5000 Hz sampling rate. BrainVision format.
R128 is a BrainVision system/recording artifact marker, not a task event.

Source: https://openneuro.org/datasets/ds001849
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 10-20 30-channel layout - LLM 推断，需人类复核
# Source: Based on standard 10-20 system with 30 channels typically used in TMS-EEG studies
_30_CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming."""
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "Fp 1", "fp1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "Fpz", "fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "Fp 2", "fp2"]),
        ("F7",  ["F7",  "EEG-F7",  "F7",  "f7"]),
        ("F3",  ["F3",  "EEG-F3",  "F3",  "f3"]),
        ("Fz",  ["Fz",  "EEG-Fz",  "Fz",  "fz"]),
        ("F4",  ["F4",  "EEG-F4",  "F4",  "f4"]),
        ("F8",  ["F8",  "EEG-F8",  "F8",  "f8"]),
        ("FT7", ["FT7", "EEG-FT7", "FT7", "T7"]),
        ("FC3", ["FC3", "EEG-FC3", "FC3", "fc3"]),
        ("FCz", ["FCz", "EEG-FCz", "FCz", "fcz"]),
        ("FC4", ["FC4", "EEG-FC4", "FC4", "fc4"]),
        ("FT8", ["FT8", "EEG-FT8", "FT8", "T8"]),
        ("T7",  ["T7",  "EEG-T7",  "T7",  "t7"]),
        ("C3",  ["C3",  "EEG-C3",  "C3",  "c3"]),
        ("Cz",  ["Cz",  "EEG-Cz",  "Cz",  "cz"]),
        ("C4",  ["C4",  "EEG-C4",  "C4",  "c4"]),
        ("T8",  ["T8",  "EEG-T8",  "T8",  "t8"]),
        ("TP7", ["TP7", "EEG-TP7", "TP7", "TP7"]),
        ("CP3", ["CP3", "EEG-CP3", "CP3", "cp3"]),
        ("CPz", ["CPz", "EEG-CPz", "CPz", "cpz"]),
        ("CP4", ["CP4", "EEG-CP4", "CP4", "cp4"]),
        ("TP8", ["TP8", "EEG-TP8", "TP8", "TP8"]),
        ("P7",  ["P7",  "EEG-P7",  "P7",  "p7"]),
        ("P3",  ["P3",  "EEG-P3",  "P3",  "p3"]),
        ("Pz",  ["Pz",  "EEG-Pz",  "Pz",  "pz"]),
        ("P4",  ["P4",  "EEG-P4",  "P4",  "p4"]),
        ("P8",  ["P8",  "EEG-P8",  "P8",  "p8"]),
        ("O1",  ["O1",  "EEG-O1",  "O1",  "o1"]),
        ("Oz",  ["Oz",  "EEG-Oz",  "Oz",  "oz"]),
        ("O2",  ["O2",  "EEG-O2",  "O2",  "o2"]),
    ]
    
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    basename = os.path.basename(file_path)
    match = re.search(r'sub-([A-Za-z0-9]+)', basename)
    if match:
        return match.group(1)
    return "unknown"


class OpenNeuroDS001849Kernel:
    """Stage1 kernel for OpenNeuro DS001849 dataset."""

    KERNEL_ID: str = "openneuro-ds001849-stage1"

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
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id(file_path)

        # Preserve original description.
        original_description = raw.info.get("description", "")

        # Build eegunity_description with known and inferred values.
        # Source: Dataset analysis.md indicates age/sex/device are missing.
        # All unknown values marked as "unknown" per KERNEL_RULEBOOK.
        # amplifier/cap: LLM 推断，需人类复核
        eegunity_description = {
            "age": "unknown",       # LLM 推断，需人类复核
            "sex": "unknown",       # LLM 推断，需人类复核
            "amplifier": "unknown", # LLM 推断，需人类复核 - likely BrainAmp based on BrainVision format
            "cap": "unknown",       # LLM 推断，需人类复核
            "handedness": "unknown" # LLM 推断，需人类复核
        }

        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 nomenclature if applicable.
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # Attempt to set standard 10-20 montage for 30-channel layout.
        # If channels are successfully renamed to standard names, apply montage.
        standard_names_found = sum(1 for ch in raw.ch_names if ch in _30_CHANNEL_STANDARD_NAMES)
        if standard_names_found >= 20:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass

        # Process annotations - remap R128 to admin marker.
        if raw.annotations:
            descriptions = []
            for desc in raw.annotations.description:
                if desc == "R128":
                    descriptions.append("admin: R128")
                elif desc in ("boundary", "Boundary"):
                    descriptions.append("admin: boundary")
                else:
                    descriptions.append(str(desc))
            
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=descriptions,
                orig_time=raw.annotations.orig_time
            )
            raw.set_annotations(new_annotations)

        # Add admin annotation for R128 if not present but events exist.
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        if "R128" in event_id and "admin: R128" not in event_id:
            r128_mask = events[:, 2] == event_id["R128"]
            if np.any(r128_mask):
                r128_onsets = events[r128_mask, 0] / raw.info["sfreq"]
                r128_durations = [0.0] * len(r128_onsets)
                r128_descriptions = ["admin: R128"] * len(r128_onsets)
                
                current_annotations = raw.annotations
                new_admin_annotations = mne.Annotations(
                    onset=list(current_annotations.onset) + r128_onsets.tolist(),
                    duration=list(current_annotations.duration) + r128_durations,
                    description=list(current_annotations.description) + r128_descriptions,
                    orig_time=current_annotations.orig_time
                )
                raw.set_annotations(new_admin_annotations)

        # Add note about missing TMS event markers.
        # Source: analysis.md - TMS pulses were delivered but corresponding event markers are missing.
        if raw.annotations:
            existing_descriptions = set(raw.annotations.description)
            if not any("TMS" in desc or "tms" in desc for desc in existing_descriptions):
                pass  # Informational only - TMS triggers may be in separate channel

        return raw


KERNEL = OpenNeuroDS001849Kernel()