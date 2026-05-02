"""OpenNeuro DS005586 stage1 kernel for EEGUnity.

EEG responses to the number of objects in partially occluded and uncovered scenes.
23 subjects, 63 EEG channels, 1000 Hz sampling rate.

Event codes: 1xx prefix = occluded condition (4 visible pieces);
             2xx prefix = uncovered condition (32 visible pieces).
Last digit encodes number of uncovered pieces (1-8).

Source: https://openneuro.org/datasets/ds005586
Paper: https://doi.org/10.1162/jocn_a_02264
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Event Code Mapping
# ============================================================================
# Source: Dataset description and paper analysis
# 1xx codes = occluded condition (4 visible pieces)
# 2xx codes = uncovered condition (32 visible pieces)
# Last digit (1-8) = number of uncovered pieces

_EVENT_CODE_MAP: Dict[str, str] = {
    "Stimulus/S 95": "catch/fixation",
    "Stimulus/S 11": "occluded_4vis_1uncovered",
    "Stimulus/S 21": "uncovered_32vis_1uncovered",
    "Stimulus/S 15": "occluded_4vis_5uncovered",
    "Stimulus/S127": "occluded_4vis_7uncovered",
    "Stimulus/S223": "uncovered_32vis_3uncovered",
    "Stimulus/S111": "occluded_4vis_1uncovered",
    "Stimulus/S124": "occluded_4vis_4uncovered",
    "Stimulus/S224": "uncovered_32vis_4uncovered",
    "Stimulus/S226": "uncovered_32vis_6uncovered",
    "Stimulus/S126": "occluded_4vis_6uncovered",
    "Stimulus/S215": "uncovered_32vis_5uncovered",
    "Stimulus/S115": "occluded_4vis_5uncovered",
    "Stimulus/S118": "occluded_4vis_8uncovered",
    "Stimulus/S218": "uncovered_32vis_8uncovered",
}

# Additional event codes that may appear based on 1xx/2xx pattern
_EXTENDED_EVENT_CODES: Dict[str, str] = {
    "Stimulus/S112": "occluded_4vis_2uncovered",
    "Stimulus/S113": "occluded_4vis_3uncovered",
    "Stimulus/S114": "occluded_4vis_4uncovered",
    "Stimulus/S116": "occluded_4vis_6uncovered",
    "Stimulus/S117": "occluded_4vis_7uncovered",
    "Stimulus/S121": "occluded_4vis_1uncovered",
    "Stimulus/S122": "occluded_4vis_2uncovered",
    "Stimulus/S123": "occluded_4vis_3uncovered",
    "Stimulus/S125": "occluded_4vis_5uncovered",
    "Stimulus/S128": "occluded_4vis_8uncovered",
    "Stimulus/S211": "uncovered_32vis_1uncovered",
    "Stimulus/S212": "uncovered_32vis_2uncovered",
    "Stimulus/S213": "uncovered_32vis_3uncovered",
    "Stimulus/S214": "uncovered_32vis_4uncovered",
    "Stimulus/S216": "uncovered_32vis_6uncovered",
    "Stimulus/S217": "uncovered_32vis_7uncovered",
    "Stimulus/S218": "uncovered_32vis_8uncovered",
    "Stimulus/S221": "uncovered_32vis_1uncovered",
    "Stimulus/S222": "uncovered_32vis_2uncovered",
    "Stimulus/S225": "uncovered_32vis_5uncovered",
    "Stimulus/S227": "uncovered_32vis_7uncovered",
    "Stimulus/S228": "uncovered_32vis_8uncovered",
}

# Combine all event codes
ALL_EVENT_CODES = {**_EVENT_CODE_MAP, **_EXTENDED_EVENT_CODES}


def _parse_event_code(description: str) -> str:
    """Parse event description to standardized label.
    
    Parameters
    ----------
    description : str
        Raw event description from the data (e.g., "Stimulus/S 95")
    
    Returns
    -------
    str
        Standardized event label
    """
    # First check if we have an exact match
    if description in ALL_EVENT_CODES:
        return ALL_EVENT_CODES[description]
    
    # Try to extract the numeric code
    match = re.search(r"Stimulus/S\s*(\d+)", description)
    if match:
        code = int(match.group(1))
        
        # Determine condition based on prefix
        if 111 <= code <= 128:
            # Occluded condition (1xx)
            uncovered = code % 10
            return f"occluded_4vis_{uncovered}uncovered"
        elif 211 <= code <= 228:
            # Uncovered condition (2xx)
            uncovered = code % 10
            return f"uncovered_32vis_{uncovered}uncovered"
        elif code == 95:
            return "catch/fixation"
    
    # Return original if no match
    return description


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path (if applicable).
    
    This dataset has a single paradigm, so returns empty string.
    Reserved for future multi-paradigm datasets.
    """
    return ""


# ============================================================================
# Subject Information
# ============================================================================
# Source: Dataset does not provide participant demographics in accessible format
# LLM inference

_SUBJECT_INFO: Dict[str, Dict[str, str]] = {
    # All subjects have unknown demographics
    # Source: Dataset does not include participants.tsv with this information
}


def _get_subject_info(subject_id: str) -> Dict[str, str]:
    """Get subject metadata.
    
    Parameters
    ----------
    subject_id : str
        Subject identifier (e.g., "sub-001")
    
    Returns
    -------
    Dict[str, str]
        Subject info with age, sex, handedness
    """
    # Extract numeric part of subject ID
    sub_num = re.search(r"(\d+)", subject_id)
    if sub_num:
        key = f"sub-{sub_num.group(1).zfill(3)}"
        if key in _SUBJECT_INFO:
            return _SUBJECT_INFO[key]
    
    # Default unknown values
    # inferred by LLM, needs human review
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


# ============================================================================
# Channel Name Standardization
# ============================================================================
# Source: Standard 64-channel EEG cap (10-20 system) with 63 channels
# inferred by LLM, needs human review
# Typical 64-channel setup:Fp1, Fp2, F7, F3, Fz, F4, F8, T7, C3, Cz, C4, T8,
# P7, P3, Pz, P4, P8, PO9, O1, Oz, O2, PO10, F1, F2, F5, F6, FT7, FC3, FC4,
# FT8, TP7, CP3, CP4, TP8, P1, P2, P5, P6, PO3, PO4, POz, F9, F10, T9, T10,
# TP9, TP10, P9, P10, Oz, PO9, PO10, O9, O10 + 2 EOG channels

# Standard 10-20 64-channel names (BioSemi 64-cap layout)
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz", "PO9", "PO10",
    "EOG-left", "EOG-right", "EOG-central",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with current channel names
    
    Returns
    -------
    Dict[str, str]
        Mapping from original to standardized channel names
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common variations of channel naming
    alias_groups = [
        # Frontopolar
        ("Fp1", ["Fp1", "EEG-Fp1", "fp1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "fp2"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "fpz"]),
        
        # Frontocentral
        ("F7", ["F7", "EEG-F7", "f7"]),
        ("F3", ["F3", "EEG-F3", "f3"]),
        ("Fz", ["Fz", "EEG-Fz", "fz"]),
        ("F4", ["F4", "EEG-F4", "f4"]),
        ("F8", ["F8", "EEG-F8", "f8"]),
        
        # Central
        ("T7", ["T7", "T3", "EEG-T7", "EEG-T3", "t7"]),
        ("C3", ["C3", "EEG-C3", "c3"]),
        ("Cz", ["Cz", "EEG-Cz", "cz"]),
        ("C4", ["C4", "EEG-C4", "c4"]),
        ("T8", ["T8", "T4", "EEG-T8", "EEG-T4", "t8"]),
        
        # Parietal
        ("P7", ["P7", "P3", "EEG-P7", "p7"]),
        ("P3", ["P3", "EEG-P3", "p3"]),
        ("Pz", ["Pz", "EEG-Pz", "pz"]),
        ("P4", ["P4", "EEG-P4", "p4"]),
        ("P8", ["P8", "P4", "EEG-P8", "p8"]),
        
        # Occipital
        ("O1", ["O1", "EEG-O1", "o1"]),
        ("Oz", ["Oz", "EEG-Oz", "oz"]),
        ("O2", ["O2", "EEG-O2", "o2"]),
        
        # EOG channels
        ("EOG-left", ["EOG-left", "EOG-L", "veog_l", "VEOG-L"]),
        ("EOG-right", ["EOG-right", "EOG-R", "veog_r", "VEOG-R"]),
        ("EOG-central", ["EOG-central", "EOG-C", "veog_c", "VEOG-C"]),
    ]
    
    for target, aliases in alias_groups:
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    # Handle numbered channels (e.g., EEG-1, EEG-2)
    numbered_pattern = re.compile(r"^(?:EEG-)?(\d+)$")
    for ch in existing:
        match = numbered_pattern.match(ch)
        if match:
            # These need manual mapping based on actual cap layout
            # Skip for now - will use set_montage with standard_1020
            pass
    
    return rename_map


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Set standard montage if channels match 10-20 system.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object to set montage on
    """
    try:
        # Try standard 1020 montage first
        montage = mne.channels.make_standard_montage("standard_1020")
        
        # Get channel names that exist in both raw and montage
        raw_chs = set(raw.ch_names)
        montage_chs = set(montage.ch_names)
        
        common_chs = raw_chs & montage_chs
        
        if len(common_chs) >= 20:  # At least 20 channels should match
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Montage setting is best-effort


# ============================================================================
# Main Kernel Class
# ============================================================================

class OpenNeuroDS005586Kernel:
    """Stage1 kernel for OpenNeuro DS005586 dataset.
    
    Dataset: EEG responses to the number of objects in partially occluded
    and uncovered scenes.
    
    Parameters
    ----------
    udataset
        EEGUnity dataset context
    raw
        MNE Raw object
    row
        Locator row with file information
    
    Returns
    -------
    mne.io.BaseRaw
        Processed Raw object with standardized events and metadata
    """
    
    KERNEL_ID: str = "openneuro-ds005586-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to raw data.
        
        Parameters
        ----------
        udataset : Any
            EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG data
        row : Any
            Row from locator with file path and metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Processed raw data
        """
        # Get file path for subject identification
        file_path = row.get("File Path", "") if hasattr(row, "get") else getattr(row, "File Path", "")
        
        # Extract subject ID
        subject_id = "unknown"
        if file_path:
            match = re.search(r"sub-[a-zA-Z0-9]+", file_path)
            if match:
                subject_id = match.group()
        
        # Get subject info
        subject_info = _get_subject_info(subject_id)
        
        # Build channel rename map and apply
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Try to set standard montage
        _set_montage_if_possible(raw)
        
        # Process events from annotations or stim channel
        self._process_events(raw)
        
        # Update description with metadata
        self._update_description(raw, subject_id, subject_info)
        
        return raw
    
    def _process_events(self, raw: mne.io.BaseRaw) -> None:
        """Process events from raw data annotations or stim channel.
        
        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object to process events from
        """
        # Check if there are existing annotations
        if raw.annotations:
            # Remap annotation descriptions to standardized labels
            new_descriptions = []
            for desc in raw.annotations.description:
                new_desc = _parse_event_code(desc)
                new_descriptions.append(new_desc)
            
            # Create new annotations with remapped descriptions
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descriptions,
                orig_time=raw.annotations.orig_time,
            )
            raw.set_annotations(new_annotations)
        else:
            # Check for stim/misc channels
            stim_channel = None
            for ch in raw.ch_names:
                if "stim" in ch.lower() or "trigger" in ch.lower():
                    stim_channel = ch
                    break
            
            # Also check for MISC channel with stimulus data
            if stim_channel is None:
                ch_types = raw.get_channel_types()
                for i, ch_type in enumerate(ch_types):
                    if ch_type == "stim":
                        stim_channel = raw.ch_names[i]
                        break
            
            if stim_channel:
                # Extract events from stim channel
                events_data = raw[stim_channel][0]
                
                # Find event onsets (where value changes from 0)
                threshold = 0.5
                event_mask = events_data.flatten() > threshold
                
                # Find transitions
                diff = np.diff(np.concatenate([[0], event_mask.astype(int)]))
                onsets_idx = np.where(diff > 0)[0]
                
                # Get event values at onsets
                event_values = events_data.flatten()[onsets_idx]
                
                # Create annotations
                sfreq = raw.info["sfreq"]
                onsets = onsets_idx / sfreq
                
                # Map event values to descriptions
                descriptions = []
                for val in event_values:
                    val_int = int(val)
                    # Try to find in event code map
                    desc = f"stim_{val_int}"
                    for code, label in ALL_EVENT_CODES.items():
                        if str(val_int) in code:
                            desc = label
                            break
                    descriptions.append(desc)
                
                if onsets.size > 0:
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=np.zeros(len(onsets)),
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
    
    def _update_description(
        self,
        raw: mne.io.BaseRaw,
        subject_id: str,
        subject_info: Dict[str, str],
    ) -> None:
        """Update raw.info['description'] with metadata.
        
        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object to update
        subject_id : str
            Subject identifier
        subject_info : Dict[str, str]
            Subject metadata (age, sex, handedness)
        """
        original_desc = raw.info.get("description", "")
        
        # inferred by LLM, needs human review - amplifier and cap info from typical EEG lab setup
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # inferred by LLM, needs human review
                "cap": "unknown",  # inferred by LLM, needs human review
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        
        raw.info["description"] = json.dumps(description_dict)


KERNEL = OpenNeuroDS005586Kernel()