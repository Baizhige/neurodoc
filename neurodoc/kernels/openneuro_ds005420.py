"""OpenNeuro ds005420 stage1 kernel for EEGUnity.

Resting State EEG with Closed Eyes and Open Eyes in Females from 60 to 80 Years Old.
BIDS dataset with continuous recordings; eyes-open/eyes-closed inferred from task labels.

Source: https://openneuro.org/datasets/ds005420
Reference: 10.1109/UBMK67458.2025.11207051
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne


# Source: Dataset documentation and reference paper (DOI: 10.1109/UBMK67458.2025.11207051)
# inferred by LLM, needs human review
_AMPLIFIER = "unknown"  # Not explicitly stated in available documentation
_CAP = "unknown"  # 20-channel system, specific cap type not confirmed
_HANDEDNESS = "unknown"  # Not provided in dataset metadata


def _parse_condition_from_filename(file_path: str) -> Optional[str]:
    """Infer eyes-open/eyes-closed condition from BIDS filename task label.
    
    BIDS task identifiers: 'task-Oa' = eyes-open, 'task-Oc' = eyes-closed.
    Source: Dataset analysis.md and BIDS naming convention.
    """
    filename = os.path.basename(file_path)
    
    # Match task-Oa or task-Oc pattern in BIDS filenames
    match_o = re.search(r'task-Oa', filename, re.IGNORECASE)
    if match_o:
        return "eyes-open (EO)"
    
    match_c = re.search(r'task-Oc', filename, re.IGNORECASE)
    if match_c:
        return "eyes-closed (EC)"
    
    return None


@dataclass
class OpenNeuroDS005420Kernel:
    """Stage1 kernel for OpenNeuro ds005420 dataset."""

    KERNEL_ID: str = "openneuro-ds005420-stage1"

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
            Preprocessed MNE Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        original_description = raw.info.get("description", "")

        # Extract subject metadata from participants.tsv if available
        # Fallback to dataset-level defaults for this female cohort (age 60-80)
        age = "60-80"  # Female cohort age range
        sex = "female"  # Female-only cohort per dataset description
        
        # Try to get subject-specific info from row if available
        if "Age" in row and row["Age"]:
            age = str(row["Age"])
        if "Sex" in row and row["Sex"]:
            sex = str(row["Sex"]).lower()

        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        # This dataset uses standard 10-20 system with 20 channels
        rename_map = _build_channel_rename_map(raw.ch_names)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage for 20-channel EEG
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setup optional, warn only

        return raw


def _build_channel_rename_map(ch_names: list) -> Dict[str, str]:
    """Build rename map for 20-channel EEG to standard 10-20 names.
    
    The dataset uses standard 10-20 nomenclature but may have variations
    in channel naming (e.g., 'EEG Fp1' vs 'Fp1').
    
    Source: Dataset channel configuration, inferred by LLM, needs human review
    """
    rename_map: Dict[str, str] = {}
    
    # Standard 10-20 channel mapping for 20-channel system
    # Common variations: 'EEG Fp1' -> 'Fp1', 'EEG F3' -> 'F3', etc.
    standard_20_channels = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2"
    ]
    
    existing_names = set(ch_names)
    
    for std_name in standard_20_channels:
        # Check for 'EEG ' prefix variant
        eeg_prefixed = f"EEG {std_name}"
        if eeg_prefixed in existing_names:
            rename_map[eeg_prefixed] = std_name
        # Check for 'EEG-' prefix variant
        eeg_hyphen = f"EEG-{std_name}"
        if eeg_hyphen in existing_names:
            rename_map[eeg_hyphen] = std_name
        # Check for lowercase variant
        lower_name = std_name.lower()
        if lower_name in existing_names:
            rename_map[lower_name] = std_name
    
    return rename_map


KERNEL = OpenNeuroDS005420Kernel()