"""EESM17 stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2017 (EESM17) - OpenNeuro ds004348
9 subjects, 35 channels, 200 Hz sampling rate
Sleep monitoring with ear-EEG and partial polysomnography

Source: https://openneuro.org/datasets/ds004348
Reference: DOI 10.1186/s12938-017-0400-5
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Subject info - all unknown since not in dataset metadata
# Source: analysis.md indicates subject_age and subject_sex are missing
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.
    
    Args:
        file_path: Path to the EEG file
        
    Returns:
        Subject ID string (e.g., '01', '02')
    """
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1).zfill(2)
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for ear-EEG channel standardization.
    
    Ear-EEG uses non-standard in-ear electrode names. This function
    maps common ear-EEG channel naming patterns to standard nomenclature.
    
    Source: Ear-EEG standard electrode naming conventions
    (Looney et al. 2018, Kidmose et al. 2013)
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common ear-EEG channel name patterns
    ear_patterns = {
        # Left ear electrodes
        r"(?:EEG-)?L(?:eft)?-?(?:Fp1|Fp\d|E1)\b": "Lp1",
        r"(?:EEG-)?L(?:eft)?-?(?:F[37]|F\d|E2)\b": "Lf7",
        r"(?:EEG-)?L(?:eft)?-?(?:T[37]|T\d|E3)\b": "Lt7",
        r"(?:EEG-)?L(?:eft)?-?(?:C[37]|C\d|E4)\b": "Lc3",
        # Right ear electrodes
        r"(?:EEG-)?R(?:ight)?-?(?:Fp2|Fp\d|E5)\b": "Rp2",
        r"(?:EEG-)?R(?:ight)?-?(?:F[48]|F\d|E6)\b": "Rf8",
        r"(?:EEG-)?R(?:ight)?-?(?:T[48]|T\d|E7)\b": "Rt8",
        r"(?:EEG-)?R(?:ight)?-?(?:C[48]|C\d|E8)\b": "Rc4",
    }
    
    for ch_name in existing_names:
        # Keep ECG, EMG, respiratory channels as-is (not EEG)
        if ch_name.upper() in ["ECG", "EMG", "RESP", "THOR", "ABDO", 
                               "CHIN", "LEG", "FLOW", "SNORE", "OXIM"]:
            continue
        
        # Check for standard 10-20 names - keep as-is
        standard_10_20 = ["Fp1", "Fp2", "F3", "F4", "Fz", "F7", "F8",
                         "C3", "C4", "Cz", "T3", "T4", "T5", "T6",
                         "P3", "P4", "Pz", "O1", "O2", "Oz",
                         "AFz", "FCz", "CPz", "POz"]
        if ch_name in standard_10_20 or ch_name.upper() in [s.upper() for s in standard_10_20]:
            continue
            
        # Handle EEG- prefixed channels
        if ch_name.startswith("EEG-"):
            base_name = ch_name[4:]  # Remove EEG- prefix
            
            # Try to map ear-specific channel names
            if base_name.upper() in ["L1", "L2", "L3", "L4"]:
                rename_map[ch_name] = f"L{base_name.lower()}"
            elif base_name.upper() in ["R1", "R2", "R3", "R4"]:
                rename_map[ch_name] = f"R{base_name.lower()}"
            # Keep other EEG- channels for now
    
    return rename_map


def _detect_ear_eeg_montage(raw: mne.io.BaseRaw) -> Optional[str]:
    """Detect appropriate montage for ear-EEG data.
    
    Ear-EEG uses specialized in-ear electrode placements that may not
    be in the standard 10-20 system. This function attempts to detect
    the appropriate montage or returns None if unknown.
    
    Source: EESM17 paradigm description
    Annotator: LLM, 2026-04-08
    """
    ch_names_upper = [ch.upper() for ch in raw.ch_names]
    
    # Check for ear-specific channel patterns
    ear_patterns = [["LP1", "LF7"], ["RP2", "RF8"]]  # Left/Right ear pairs
    left_ear_present = any("L" in ch.upper() and any(p in ch.upper() for p in ["P1", "F7", "T7", "C3"])
                          for ch in raw.ch_names)
    right_ear_present = any("R" in ch.upper() and any(p in ch.upper() for p in ["P2", "F8", "T8", "C4"])
                           for ch in raw.ch_names)
    
    if left_ear_present or right_ear_present:
        return "standard_1020"  # Best approximation for ear-EEG
    
    return None


def _remap_annotations_to_raw_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap annotation descriptions to standardized raw meta event names.
    
    The EESM17 dataset has specific event markers that need standardization
    for consistent downstream processing.
    
    Source: analysis.md Event Structure table
    Annotator: Human, 2026-04-08
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    # Event mapping from raw annotations to standardized names
    event_mapping = {
        "Lights Off": "Lights Off",
        "Lights On": "Lights On",
        "Awake": "Awake",
        "Artifact": "Artifact",
        "Arousal": "Arousal",
        "Beginning of Recording": "Beginning of Recording",
        "End of Study": "End of Study",
        "Montage": "Montage",
        "Started Analyzer - Sleep Events": "Started Analyzer - Sleep Events",
        "Started Analyzer - ECG": "Started Analyzer - ECG",
        "Stopped Analyzer - ECG": "Stopped Analyzer - ECG",
        "Started Analyzer - Auto-Staging": "Started Analyzer - Auto-Staging",
        "Stopped Analyzer - Auto-Staging": "Stopped Analyzer - Auto-Staging",
        "512": "512",
    }
    
    # Update annotation descriptions
    new_descriptions = []
    for desc in raw.annotations.description:
        new_desc = event_mapping.get(desc, desc)
        new_descriptions.append(new_desc)
    
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    
    raw.set_annotations(new_annotations)
    return raw


def _filter_eeg_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Filter to EEG and reference channels only, removing PSG auxiliary channels.
    
    The EESM17 dataset includes PSG channels (ECG, respiratory, etc.) that
    should be filtered out for EEG-specific analysis.
    
    Source: analysis.md Kernel Notes
    Annotator: LLM, 2026-04-08
    """
    # Define non-EEG channel patterns to exclude
    exclude_patterns = [
        "ECG", "EMG", "CHIN", "LEG",  # EMG channels
        "RESP", "THOR", "ABDO", "FLOW", "SNORE",  # Respiratory
        "OXIM", "SAO2", "SPO2",  # Oximetry
        "TEMP", "BODY",  # Temperature
        "PR", "HR",  # Heart rate derived
    ]
    
    eeg_chs = []
    for ch in raw.ch_names:
        exclude = False
        ch_upper = ch.upper()
        for pattern in exclude_patterns:
            if pattern in ch_upper:
                exclude = True
                break
        if not exclude:
            eeg_chs.append(ch)
    
    if len(eeg_chs) < len(raw.ch_names):
        print(f"Filtered {len(raw.ch_names) - len(eeg_chs)} non-EEG channels, "
              f"keeping {len(eeg_chs)} EEG channels")
        raw = raw.pick_channels(eeg_chs)
    
    return raw


class EESM17Kernel:
    """Stage1 kernel for the Ear-EEG Sleep Monitoring 2017 (EESM17) dataset."""
    
    KERNEL_ID: str = "eesm17-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EESM17 recording.
        
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
            Preprocessed Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id(file_path)
        
        # Get subject info if available
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown",
        })
        
        # Remap annotations to standardized raw meta events
        raw = _remap_annotations_to_raw_events(raw)
        
        # Filter out non-EEG channels (ECG, respiratory, etc.)
        raw = _filter_eeg_channels(raw)
        
        # Rename ear-EEG channels to standardized names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)
        
        # Try to set montage if ear-EEG positions are detectable
        montage_name = _detect_ear_eeg_montage(raw)
        if montage_name:
            try:
                montage = mne.channels.make_standard_montage(montage_name)
                raw.set_montage(montage, on_missing="warn")
            except Exception as e:
                print(f"Could not set montage: {e}")
        else:
            # For non-standard ear-EEG, set default EEG type without montage
            print("Ear-EEG montage not detected, skipping montage setting")
        
        # Update description with eegunity_description
        original_description = raw.info.get("description", "")
        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "ear-EEG",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = EESM17Kernel()