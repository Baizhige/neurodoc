"""OpenNeuro ds002578 stage1 kernel for EEGUnity.

Visual Oddball Task with 256-channel BioSemi EEG.
Paradigm: 5 squares shown continuously, one attended location,
white disk target oddball appears at attended position.

Source: https://openneuro.org/datasets/ds002578
        DOI: 10.1523/jneurosci.3477-07.2007
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# =============================================================================
# Subject Information
# Source: OpenNeuro participants.tsv or dataset metadata
# =============================================================================

# LLM 推断，需人类复核
# age/sex from dataset metadata or inference; amplifier/cap from BioSemi system
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    },
    "sub-02": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    },
}


# =============================================================================
# Event Mapping (raw meta)
# =============================================================================

# Event structure from analysis.md:
# Target oddball: attend position = cue position
# Non-target distractor: attend position != cue position
_EVENT_MAP: Dict[int, str] = {
    # Admin codes
    203: "admin: marker-203",
    217: "admin: marker-217",
    237: "admin: marker-237",
    # Visual oddball events (attend pos 3)
    31: "distractor: attend-3 cue-1",
    33: "target: attend-3 cue-3",
    34: "distractor: attend-3 cue-4",
    35: "distractor: attend-3 cue-5",
    # Visual oddball events (attend pos 4)
    41: "distractor: attend-4 cue-1",
    42: "distractor: attend-4 cue-2",
    43: "distractor: attend-4 cue-3",
    44: "target: attend-4 cue-4",
    45: "distractor: attend-4 cue-5",
    # Generic events
    999999: "Picture",  # May be mapped from annotation description
}


# =============================================================================
# Channel Rename for BioSemi 256-channel System
# =============================================================================

# BioSemi 256-channel system uses custom naming convention.
# Standard 10-20 positions are named (e.g., FP1, FPz, FP2, F7, F3, Fz, F4, F8, ...)
# Additional channels follow BioSemi naming (e.g., A1, A2, ..., or numbered)
#
# Source: BioSemi 256-channel electrode layout documentation
# For this dataset, channels are likely named with BioSemi convention.
# This kernel attempts to standardize known positions.

# Known standard 10-20 positions that may appear in BioSemi 256-ch data
_BIOSEMI_STANDARD_NAMES = {
    "FP1", "FPz", "FP2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # BioSemi extras
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
    "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19", "A20",
    "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30",
    "A31", "A32",
}


def _detect_paradigm(file_name: str) -> str:
    """Detect paradigm from file name."""
    fname_lower = file_name.lower()
    if "oddball" in fname_lower:
        return "oddball"
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for BioSemi 256-channel system.
    
    Attempts to rename BioSemi-specific channel names to standard 10-20
    nomenclature where applicable. Leaves unknown BioSemi channels unchanged.
    
    Source: BioSemi electrode naming convention, 10-20 international standard
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # BioSemi to standard mapping (common cases)
    # Format: BIO_SEMI_NAME -> STANDARD_NAME
    biosemi_to_standard = {
        # Standard 10-20 positions
        "Fp1": "FP1", "Fp2": "FP2", "Fpz": "FPz",
        "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
        "T7": "T7", "C3": "C3", "Cz": "Cz", "C4": "C4", "T8": "T8",
        "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
        "O1": "O1", "Oz": "Oz", "O2": "O2",
        "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
        "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCz": "FCz", "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
        "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPz": "CPz", "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
        "PO7": "PO7", "PO3": "PO3", "POz": "POz", "PO4": "PO4", "PO8": "PO8",
        # BioSemi auxiliary
        "A1": "A1", "A2": "A2", "A3": "A3", "A4": "A4",
        "A5": "A5", "A6": "A6", "A7": "A7", "A8": "A8",
        "A9": "A9", "A10": "A10", "A11": "A11", "A12": "A12",
        "A13": "A13", "A14": "A14", "A15": "A15", "A16": "A16",
        "A17": "A17", "A18": "A18", "A19": "A19", "A20": "A20",
        "A21": "A21", "A22": "A22", "A23": "A23", "A24": "A24",
        "A25": "A25", "A26": "A26", "A27": "A27", "A28": "A28",
        "A29": "A29", "A30": "A30", "A31": "A31", "A32": "A32",
    }
    
    for bio_name, std_name in biosemi_to_standard.items():
        if bio_name in existing:
            rename_map[bio_name] = std_name
    
    return rename_map


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Remap annotation descriptions to canonical event labels.
    
    Source: analysis.md event structure table
    Annotator: LLM, 2026-04-08
    """
    annotations = raw.annotations.copy()
    
    new_descriptions = []
    for desc in annotations.description:
        desc_str = str(desc)
        
        # Check if it's a numeric event code
        try:
            event_code = int(float(desc_str))
            if event_code in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[event_code])
            else:
                new_descriptions.append(f"event: {desc_str}")
        except (ValueError, TypeError):
            # Keep original string if not numeric
            new_descriptions.append(desc_str)
    
    new_annotations = mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )
    
    return new_annotations


def _extract_subject_info(row) -> Dict[str, str]:
    """Extract subject information from locator row.
    
    Source: OpenNeuro participants.tsv or dataset metadata
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    subject_id = str(row.get("subject_id", "unknown"))
    
    # Try to get from subject dict first
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id].copy()
    
    # Default unknown values
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


class OpenNeuroDs002578Kernel:
    """Stage1 kernel for OpenNeuro ds002578 dataset.
    
    Visual Oddball Task with 256-channel BioSemi EEG.
    Supports three tasks:
    1. Visual Oddball Target Detection (classification)
    2. Target Reaction Time Regression (regression)
    3. Response-Locked Motor Analysis (classification)
    """
    
    KERNEL_ID: str = "openneuro-ds002578-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least file path and subject info.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata.
        """
        file_path = str(row.get("File Path", ""))
        file_name = os.path.basename(file_path)
        
        # ---------------------------------------------------------------------
        # Step 1: Remap annotations to canonical event labels
        # ---------------------------------------------------------------------
        raw.set_annotations(_remap_annotations(raw))
        
        # ---------------------------------------------------------------------
        # Step 2: Rename channels (before set_montage)
        # ---------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)
        
        # ---------------------------------------------------------------------
        # Step 3: Try to set montage for standard positions
        # ---------------------------------------------------------------------
        # Get standard positions that exist in the data
        available_standard = []
        for ch in raw.ch_names:
            # Check if channel matches standard 10-20 pattern
            if ch in _BIOSEMI_STANDARD_NAMES:
                available_standard.append(ch)
        
        if available_standard:
            try:
                # Try to set standard 1020 montage for available channels
                montage = mne.channels.make_standard_montage("standard_1020")
                
                # Get channels that are in both data and montage
                common_channels = list(set(montage.ch_names) & set(raw.ch_names))
                
                if common_channels:
                    # Create info with only common channels for montage
                    ch_info_montage = mne.pick_info(raw.info, 
                                                    mne.pick_channels(raw.ch_names, 
                                                                      include=common_channels,
                                                                      ordered=False))
                    
                    # Set montage (subset)
                    raw.set_montage(montage, on_missing='ignore')
            except Exception:
                # Montage setting failed, continue without it
                pass
        
        # ---------------------------------------------------------------------
        # Step 4: Update raw.info["description"] with eegunity metadata
        # ---------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        subject_info = _extract_subject_info(row)
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BioSemi 256-channel",  # Known from dataset
                "cap": "BioSemi 256-channel",  # LLM 推断，需人类复核
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # ---------------------------------------------------------------------
        # Step 5: Detect and store paradigm info in annotations description
        # ---------------------------------------------------------------------
        paradigm = _detect_paradigm(file_name)
        if paradigm != "unknown":
            # Add paradigm info to existing annotations
            current_annots = raw.annotations
            paradigm_descriptions = [f"{paradigm.upper()}: {d}" for d in current_annots.description]
            
            new_annotations = mne.Annotations(
                onset=current_annots.onset,
                duration=current_annots.duration,
                description=paradigm_descriptions,
                orig_time=current_annots.orig_time,
            )
            raw.set_annotations(new_annotations)
        
        return raw


KERNEL = OpenNeuroDs002578Kernel()