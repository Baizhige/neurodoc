"""OpenNeuro ds004446 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 2 - High-density EEG motor imagery BCI dataset.
3-class motor imagery: left hand, right hand, feet.
130-channel high-density EEG at 1000 Hz.

Source: https://openneuro.org/datasets/ds004446
Paper: https://doi.org/10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Source: Paper DOI 10.1038/s41597-023-02260-6
# High-density EEG setup with 128 EEG channels + 2 EOG channels
# Standard 10-20 electrode naming convention with extended coverage
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
_AMPLIFIER = "BrainAmp"  # LLM 推断，需人类复核
_CAP_MATERIAL = "Ag/AgCl"  # LLM 推断，需人类复核

# Event mapping for motor imagery classes
_EVENT_MAP = {
    "1": "left_hand_MI",
    "2": "right_hand_MI",
    "3": "feet_MI",
}


def _build_channel_rename_map_130ch(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 130-channel high-density EEG.

    Standard 10-20 extended system with 128 EEG + 2 EOG channels.
    Mapping from potential BIDS-standard names to standard 10-20 names.

    Source: Paper DOI 10.1038/s41597-023-02260-6, Table of electrode positions
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    # Standard 10-20 electrode positions for high-density cap
    standard_eeg_channels = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF6", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
        "T9", "T7", "T5", "T3", "T1", "T2", "T4", "T6", "T8", "T10",
        "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
        # Additional extended electrodes often present in 128-ch systems
        "F9h", "F10h", "T9h", "T10h", "P9h", "P10h",
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common aliases for standard channels
    alias_patterns = [
        # BIDS-style with EEG prefix
        (r"^EEG\s*(\d+)$", lambda m: f"EEG-{m.group(1)}"),
        # Clean numbered format
        (r"^(?:EEG[-_])?(\d+)$", lambda m: None),  # Will use index mapping
        # Standard names with potential prefixes
        (r"^(?:EEG[-_])?(Fp[12]?z?)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(AF[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(F[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(FC[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(T[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(TP[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(P[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(PO[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(O[0-9]+)$", lambda m: m.group(1)),
        (r"^(?:EEG[-_])?(Iz)$", lambda m: m.group(1)),
    ]

    for ch in existing_names:
        # Skip already standard names
        if ch in standard_eeg_channels:
            continue

        # Skip EOG and other special channels
        if any(x in ch.upper() for x in ["EOG", "ECG", "EMG", "STIM", "MISC", "REF", "GND"]):
            continue

        # Try to match and rename
        matched = False
        for pattern, replacement in alias_patterns:
            match = re.match(pattern, ch, re.IGNORECASE)
            if match and replacement:
                new_name = replacement(match)
                if new_name and new_name in standard_eeg_channels:
                    rename_map[ch] = new_name
                    matched = True
                    break

    return rename_map


def _extract_subject_info_from_filename(filename: str) -> Dict[str, str]:
    """Extract subject ID from filename for lookup.

    OpenNeuro BIDS format: sub-<subject_id>_eeg.<ext>
    """
    match = re.search(r"sub-(\d+)", os.path.basename(filename))
    if match:
        return {"subject_id": match.group(1)}
    return {}


@dataclass
class OpenNeuroDS004446Kernel:
    """Stage1 kernel for OpenNeuro ds004446 (BMI-HDEEG dataset 2)."""

    KERNEL_ID: str = "openneuro-ds004446-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata.
        """
        file_path = row.get("File Path", "")

        # Build and apply channel rename map
        rename_map = _build_channel_rename_map_130ch(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Set channel types - identify EOG channels
        ch_types_to_set = {}
        for ch in raw.ch_names:
            if any(x in ch.upper() for x in ["EOG", "-LE", "-RE", "-UE"]):
                if "left" in ch.lower() or "-l" in ch.lower():
                    ch_types_to_set[ch] = "eog"
                elif "right" in ch.lower() or "-r" in ch.lower():
                    ch_types_to_set[ch] = "eog"
                elif "eog" in ch.lower():
                    ch_types_to_set[ch] = "eog"

        if ch_types_to_set:
            try:
                raw.set_channel_types(ch_types_to_set)
            except Exception as e:
                print(f"[{self.KERNEL_ID}] Warning: Could not set channel types: {e}")

        # Try to set montage if enough standard channels are present
        try:
            standard_channels = [ch for ch in raw.ch_names if ch in mne.channels.get_standard_montage("standard_1020")]
            if len(standard_channels) >= 20:  # Only set montage if we have sufficient channels
                raw.set_montage("standard_1020", on_missing="ignore")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")

        # Process events/annotations
        # OpenNeuro datasets typically have events in annotations
        original_desc = raw.info.get("description", "")

        # Map numeric events to semantic labels
        if raw.annotations:
            new_descriptions = []
            for ann in raw.annotations:
                desc = str(ann["description"])
                # Try to extract numeric code from description
                numeric_match = re.match(r"^\s*(\d+)\s*$", desc.strip())
                if numeric_match:
                    code = numeric_match.group(1)
                    new_desc = _EVENT_MAP.get(code, desc)
                else:
                    new_desc = desc
                new_descriptions.append(new_desc)

            if any(new_descriptions[i] != str(raw.annotations[i]["description"])
                   for i in range(len(raw.annotations))):
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annotations)

        # Build eegunity_description with metadata
        # Source: Paper DOI 10.1038/s41597-023-02260-6 - dataset demographics
        # are not directly reported in the paper (likely aggregated from
        # the original study protocols). All subject-level info is unknown.
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": _AMPLIFIER,  # LLM 推断，需人类复核
                "cap": _CAP_MATERIAL,  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004446Kernel()