"""zenodo_saa stage1 kernel for EEGUnity.

Spatial Auditory Attention (SAA) dataset from Zenodo.
- 18 subjects, BioSemi ActiveTwo 32-channel EEG + 8 external channels = 41 channels
- Variable sampling rates (1024, 2048, or 4096 Hz)
- Events encoded in BioSemi Status channel (trigger codes)
- BDF format with BioSemi naming convention

Source: https://doi.org/10.5281/zenodo.3357164
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import mne
import numpy as np


# BioSemi standard 32-channel layout (A1-A32 mapped to standard 10-20 names)
# Source: BioSemi ActiveTwo 32-channel cap documentation, standard naming
# Annotator: LLM, 2026-04-08
# Note: By LLM inference, needs human review
_BIOSEMI_32_MAP = {
    "A1": "Fp1",
    "A2": "AF3",
    "A3": "F7",
    "A4": "F3",
    "A5": "FC1",
    "A6": "FC5",
    "A7": "T7",
    "A8": "C3",
    "A9": "CP1",
    "A10": "CP5",
    "A11": "P7",
    "A12": "P3",
    "A13": "Pz",
    "A14": "PO3",
    "A15": "O1",
    "A16": "Oz",
    "A17": "O2",
    "A18": "PO4",
    "A19": "P4",
    "A20": "P8",
    "A21": "CP6",
    "A22": "CP2",
    "A23": "C4",
    "A24": "T8",
    "A25": "FC6",
    "A26": "FC2",
    "A27": "F4",
    "A28": "F8",
    "A29": "AF4",
    "A30": "Fp2",
    "A31": "Fz",
    "A32": "Cz",
}

# External channels typically include EXG1-EXG8 (EOG, EMG, etc.)
# Source: BioSemi documentation; exact usage varies by study
# Annotator: LLM, 2026-04-08
# Note: By LLM inference, needs human review
_EXG_CHANNEL_MAP = {
    "EXG1": "EXG1",
    "EXG2": "EXG2",
    "EXG3": "EXG3",
    "EXG4": "EXG4",
    "EXG5": "EXG5",
    "EXG6": "EXG6",
    "EXG7": "EXG7",
    "EXG8": "EXG8",
}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    # Files named like S12.bdf, S13.bdf, etc.
    basename = os.path.basename(file_path)
    match = re.match(r'(S\d+)', basename)
    if match:
        return match.group(1)
    return "unknown"


def _get_channel_rename_map(raw: mne.io.BaseRaw) -> dict[str, str]:
    """Build rename map for BioSemi channels to standard 10-20 names."""
    rename_map = {}
    for ch_name in raw.ch_names:
        # Check for A1-A32 pattern (may have prefixes like 'A 1' or 'A1')
        clean_name = ch_name.strip()
        # Match patterns like "A 1", "A1", "A-1", etc.
        match = re.match(r'^[Aa][\s\-]?(\d{1,2})$', clean_name)
        if match:
            idx = int(match.group(1))
            key = f"A{idx}"
            if key in _BIOSEMI_32_MAP:
                rename_map[ch_name] = _BIOSEMI_32_MAP[key]
        # Also check if already in standard form
        elif clean_name in _BIOSEMI_32_MAP:
            # Already BioSemi name, map to 10-20
            rename_map[ch_name] = _BIOSEMI_32_MAP[clean_name]
    
    # Handle EXG channels - keep as-is but ensure consistent naming
    for ch_name in raw.ch_names:
        clean_name = ch_name.strip()
        match = re.match(r'^[Ee][Xx][Gg][\s\-]?(\d)$', clean_name)
        if match:
            idx = int(match.group(1))
            standard_exg = f"EXG{idx}"
            if clean_name != standard_exg:
                rename_map[ch_name] = standard_exg
    
    return rename_map


def _find_status_channel(raw: mne.io.BaseRaw) -> str | None:
    """Find the BioSemi Status trigger channel."""
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        # Common BioSemi status channel names
        if upper in ["STATUS", "TRIGGER", "STI", "STIM", "STI 014", "STI014"]:
            return ch_name
        if "STATUS" in upper:
            return ch_name
    return None


@dataclass
class ZenodoSAAKernel:
    """Stage1 kernel for the Zenodo Spatial Auditory Attention dataset."""

    KERNEL_ID: str = "zenodo-saa-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _extract_subject_id(file_path)

        # Channel renaming to standard 10-20
        rename_map = _get_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Set channel types
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in _BIOSEMI_32_MAP.values() or ch_name in ["Fz", "Cz", "Pz", "Oz"]:
                ch_types[ch_name] = "eeg"
            elif ch_name.startswith("EXG"):
                # EXG channels are typically EOG or other external signals
                # Default to misc; common convention: EXG1-EXG2 = HEOG, EXG3-EXG4 = VEOG
                ch_types[ch_name] = "misc"
            elif "STATUS" in ch_name.upper() or "TRIGGER" in ch_name.upper() or "STI" in ch_name.upper():
                ch_types[ch_name] = "stim"
            else:
                ch_types[ch_name] = "misc"
        
        # Only set types for channels that exist
        existing_ch_types = {k: v for k, v in ch_types.items() if k in raw.ch_names}
        if existing_ch_types:
            raw = raw.set_channel_types(existing_ch_types)

        # Set montage for EEG channels
        eeg_ch_names = [ch for ch in raw.ch_names if ch in _BIOSEMI_32_MAP.values()]
        if eeg_ch_names:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Only set montage for channels that exist in the montage
                montage_ch_names = set(montage.ch_names)
                available_eeg = [ch for ch in eeg_ch_names if ch in montage_ch_names]
                if available_eeg:
                    raw = raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage not critical

        # Extract events from Status channel
        status_ch = _find_status_channel(raw)
        if status_ch is None:
            # Try to find any stim channel
            for ch_name in raw.ch_names:
                if raw.get_channel_types(picks=[ch_name])[0] == "stim":
                    status_ch = ch_name
                    break
        
        if status_ch:
            # Find events using MNE's find_events on the status channel
            try:
                # BioSemi trigger codes are typically 24-bit values in the Status channel
                events = mne.find_events(raw, stim_channel=status_ch, shortest_event=1, verbose=False)
                if len(events) > 0:
                    # Create annotations from events
                    # Trigger codes ~3856-3966 for stimuli, 65530-65532 for control
                    unique_codes = np.unique(events[:, 2])
                    
                    # Build annotations
                    onsets = events[:, 0] / raw.info["sfreq"]
                    durations = np.zeros(len(events))
                    descriptions = [f"trigger-{code}" for code in events[:, 2]]
                    
                    # Remove existing annotations first to avoid duplicates
                    raw.set_annotations(None)
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    raw = raw.set_annotations(annotations)
            except Exception:
                pass  # If event extraction fails, continue without annotations

        # Build eegunity_description
        # No participants.tsv available for this dataset; all demographic info unknown
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = ZenodoSAAKernel()