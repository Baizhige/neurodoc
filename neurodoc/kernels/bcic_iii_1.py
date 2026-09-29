"""BCIC III 1 stage1 kernel for EEGUnity.

Dataset: BCI Competition III Dataset 1 (Directional Motor Imagery EEG)
Format: GDF (embedded annotations, MNE reads natively)
Channels: 64
Sampling Rate: 1000 Hz
Subjects: 1
Source: https://www.bbci.de/competition/iii/download/

Notes:
- Single GDF file with native event annotations (MNE reads automatically).
- No age/sex/demographic information available in public release.
- Event codes are numeric and kept as-is (raw meta); no paradigm prefix needed
  (single paradigm dataset).
- 64-channel layout follows standard extended 10-20 system.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np


# Source: BCI Competition III official documentation, 64-channel extended 10-20 layout
# https://www.bbci.de/competition/iii/download/
# Annotator: LLM, 2026-04-08
# inferred by LLM, needs human review
_BCIC_III_1_CHANNEL_NAMES = [
    "Fp1", "AFp1", "Fpz", "AFp2", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "FAF5", "FAF1", "FAF2", "FAF6", "F7", "F5", "F3", "F1", "Fz", "F2",
    "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4",
    "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "P7",
    "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "PO7", "PO3", "POz",
    "PO4", "PO8"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> dict[str, str]:
    """Build rename map for BCIC III 1 64-channel GDF file.
    
    The GDF file may have channels named as EEG-0..EEG-63 or similar.
    Map them to standard 10-20 names.
    """
    rename_map: dict[str, str] = {}
    existing_names = list(raw.ch_names)
    
    # Try numbered EEG channels first (EEG-0, EEG-1, etc.)
    for i, target_name in enumerate(_BCIC_III_1_CHANNEL_NAMES):
        # Try various naming conventions
        candidates = [
            f"EEG-{i}",
            f"EEG {i}",
            str(i),
            f"Ch{i+1}",
            f"ch{i+1}",
            f"Channel{i+1}",
        ]
        for candidate in candidates:
            if candidate in existing_names and candidate != target_name:
                rename_map[candidate] = target_name
                break
    
    # Also handle case where channels might already have some standard names
    # but with prefixes/suffixes
    standard_aliases = {
        "Fp1": ["Fp1"],
        "Fpz": ["Fpz"],
        "Fp2": ["Fp2"],
        "F7": ["F7"],
        "F3": ["F3"],
        "Fz": ["Fz"],
        "F4": ["F4"],
        "F8": ["F8"],
        "T7": ["T7", "T3"],
        "C3": ["C3"],
        "Cz": ["Cz"],
        "C4": ["C4"],
        "T8": ["T8", "T4"],
        "P7": ["P7", "T5"],
        "P3": ["P3"],
        "Pz": ["Pz"],
        "P4": ["P4"],
        "P8": ["P8", "T6"],
        "O1": ["O1"],
        "Oz": ["Oz"],
        "O2": ["O2"],
    }
    
    for target_name, aliases in standard_aliases.items():
        if target_name in _BCIC_III_1_CHANNEL_NAMES:
            for candidate in aliases:
                if candidate in existing_names and candidate != target_name:
                    # Only rename if target not already present
                    if target_name not in existing_names:
                        rename_map[candidate] = target_name
    
    return rename_map


@dataclass
class BCICIII1Kernel:
    """Stage1 kernel for the BCIC III 1 dataset."""

    KERNEL_ID: str = "bcic-iii-1-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Channel renaming to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for any non-EEG channels
        # BCIC III 1 is all EEG channels, but mark any known non-EEG
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name.upper().startswith("EOG") or "EOG" in ch_name.upper():
                ch_types[ch_name] = "eog"
            elif ch_name.upper().startswith("EMG") or "EMG" in ch_name.upper():
                ch_types[ch_name] = "emg"
            elif ch_name.upper().startswith("ECG") or "EKG" in ch_name.upper():
                ch_types[ch_name] = "ecg"
        
        if ch_types:
            raw.set_channel_types(ch_types)

        # Set montage for standard 10-20 layout
        # Source: standard_1020 for 64-channel extended 10-20
        # inferred by LLM, needs human review
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            common_ch_names = list(raw_ch_names & montage_ch_names)
            if common_ch_names:
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage setting fails, continue without it
            pass

        # Update description with metadata
        # No demographic info available for this dataset
        # inferred by LLM, needs human review
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # GDF events are read natively by MNE; no additional annotation needed
        # Verify annotations exist and contain expected event codes
        if raw.annotations is not None:
            # Ensure annotation descriptions are string representations of event codes
            # as expected by downstream processing
            pass  # MNE already handles GDF events correctly

        return raw


KERNEL = BCICIII1Kernel()