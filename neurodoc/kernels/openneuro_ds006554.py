"""OpenNeuro DS006554 stage1 kernel for EEGUnity.

Social Observation EEG dataset with 47 subjects, 64 channels, 500 Hz.
Paradigm: social observation tasks with multi-factorial trigger coding.

Source: https://openneuro.org/datasets/ds006554
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# All metadata fields are unknown for this dataset.
# Source: analysis.md indicates subject_age, subject_sex, device all missing.
# Annotator: LLM, 2026-04-08
_SUBJECT_DEFAULT: Dict[str, Any] = {
    "age": "unknown",
    "sex": "unknown",
    "handedness": "unknown",
    "amplifier": "unknown",
    "cap": "unknown",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.

    OpenNeuro EEG datasets typically use standard 10-20 names, but some
    files may have prefixes or alternative naming (e.g., 'A1' -> 'Fp1').
    This function handles common aliases found in EEG datasets.

    Source: Common channel naming conventions in OpenNeuro EEG datasets.
    Annotator: LLM, 2026-04-08
    """
    alias_groups = [
        # Standard 10-20 frontal
        ("Fp1", ["Fp1", "A1", "EEG Fp1"]),
        ("Fp2", ["Fp2", "A2", "EEG Fp2"]),
        ("Fpz", ["Fpz", "EEG Fpz"]),
        ("F7", ["F7", "EEG F7"]),
        ("F3", ["F3", "EEG F3"]),
        ("Fz", ["Fz", "EEG Fz"]),
        ("F4", ["F4", "EEG F4"]),
        ("F8", ["F8", "EEG F8"]),
        # Standard 10-20 central
        ("T7", ["T7", "T3", "EEG T7"]),
        ("C3", ["C3", "EEG C3"]),
        ("Cz", ["Cz", "EEG Cz"]),
        ("C4", ["C4", "EEG C4"]),
        ("T8", ["T8", "T4", "EEG T8"]),
        # Standard 10-20 parietal
        ("P7", ["P7", "T5", "EEG P7"]),
        ("P3", ["P3", "EEG P3"]),
        ("Pz", ["Pz", "EEG Pz"]),
        ("P4", ["P4", "EEG P4"]),
        ("P8", ["P8", "T6", "EEG P8"]),
        # Standard 10-20 occipital
        ("O1", ["O1", "EEG O1"]),
        ("Oz", ["Oz", "EEG Oz"]),
        ("O2", ["O2", "EEG O2"]),
        # Standard 10-20 additional
        ("AF7", ["AF7", "EEG AF7"]),
        ("AF3", ["AF3", "EEG AF3"]),
        ("AFz", ["AFz", "EEG AFz"]),
        ("AF4", ["AF4", "EEG AF4"]),
        ("AF8", ["AF8", "EEG AF8"]),
        ("F5", ["F5", "EEG F5"]),
        ("F1", ["F1", "EEG F1"]),
        ("F2", ["F2", "EEG F2"]),
        ("F6", ["F6", "EEG F6"]),
        ("FC5", ["FC5", "EEG FC5"]),
        ("FC3", ["FC3", "EEG FC3"]),
        ("FC1", ["FC1", "EEG FC1"]),
        ("FCz", ["FCz", "EEG FCz"]),
        ("FC2", ["FC2", "EEG FC2"]),
        ("FC4", ["FC4", "EEG FC4"]),
        ("FC6", ["FC6", "EEG FC6"]),
        ("C5", ["C5", "EEG C5"]),
        ("C1", ["C1", "EEG C1"]),
        ("C2", ["C2", "EEG C2"]),
        ("C6", ["C6", "EEG C6"]),
        ("CP5", ["CP5", "EEG CP5"]),
        ("CP3", ["CP3", "EEG CP3"]),
        ("CP1", ["CP1", "EEG CP1"]),
        ("CPz", ["CPz", "EEG CPz"]),
        ("CP2", ["CP2", "EEG CP2"]),
        ("CP4", ["CP4", "EEG CP4"]),
        ("CP6", ["CP6", "EEG CP6"]),
        ("P5", ["P5", "EEG P5"]),
        ("P1", ["P1", "EEG P1"]),
        ("P2", ["P2", "EEG P2"]),
        ("P6", ["P6", "EEG P6"]),
        ("PO3", ["PO3", "EEG PO3"]),
        ("POz", ["POz", "EEG POz"]),
        ("PO4", ["PO4", "EEG PO4"]),
        ("PO7", ["PO7", "EEG PO7"]),
        ("PO8", ["PO8", "EEG PO8"]),
        # EOG channels
        ("EOG-left", ["EOG-left", "VEOG-L", "VEOGL"]),
        ("EOG-right", ["EOG-right", "VEOG-R", "VEOGR"]),
        ("EOG-up", ["EOG-up", "HEOG-L", "HEOG"]),
        # Reference/misc
        ("Mastoid", ["Mastoid", "REF", "Reference"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


class OpenNeuroDS006554Kernel:
    """Stage1 kernel for OpenNeuro DS006554 (Social Observation EEG)."""

    KERNEL_ID: str = "openneuro-ds006554-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : locator row with file information

        Returns
        -------
        mne.io.BaseRaw
        """
        # Get original description
        original_description = raw.info.get("description", "")

        # Write eegunity_description with all unknown values
        # Source: analysis.md indicates all metadata fields missing.
        # Annotator: LLM, 2026-04-08
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # Try to set standard 10-20 montage for 64-channel EEG
        try:
            # standard_1020 works for 64-channel setups
            montage = mne.channels.make_standard_montage("standard_1020")
            # Remove channels not in montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 20:  # Only set if enough channels match
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If montage fails, skip (possibly non-standard cap)
            pass

        # Handle events from annotations or stim channel
        # The dataset has 30 event codes (social stimulus conditions)
        # Map numeric annotations to readable strings
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Convert numeric annotations to descriptive strings
            desc_map = {}
            for desc in np.unique(raw.annotations.description):
                try:
                    code = int(desc)
                    desc_map[desc] = f"condition_{code}"
                except (ValueError, TypeError):
                    # Keep original if not numeric
                    desc_map[desc] = str(desc)

            new_descriptions = [desc_map.get(a, str(a)) for a in raw.annotations.description]
            annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descriptions,
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS006554Kernel()