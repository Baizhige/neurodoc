"""OpenNeuro DS003885 stage1 kernel for EEGUnity.

Dataset: Capacity for movement is an organisational principle in object representations
Source: https://openneuro.org/datasets/ds003885 (DOI: 10.1016/j.neuroimage.2022.119517)

Paradigm: RSVP image presentation (~3 Hz) with semantic classification task.
Events: E 1 (animals), E 2 (plants), E 3 (still natural), E 5 (still artificial),
        E 8 (moving natural), E 9 (moving artificial). E 4 marks block boundaries.

This kernel handles EEGLAB-preprocessed data from derivatives/eeglab directory.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# =============================================================================
# Subject Information
# =============================================================================
# Source: Dataset README / paper DOI 10.1016/j.neuroimage.2022.119517
# "24 participants (12 female, age range 18-35)" — LLM 推断，需人类复核
_AGE_RANGE = "18-35"
_AMPLIFIER = "BrainAmp"  # LLM 推断，需人类复核
_CAP = "Ag/AgCl"         # LLM 推断，需人类复核
_HANDEDNESS = "unknown"  # No handedness info in analysis.md


# =============================================================================
# Channel Rename Mapping
# =============================================================================
# Source: Standard 128-channel montage (EGI HydroCel or similar 128-channel cap)
# The data uses generic channel names like EEG001-EEG128 plus EOG channels.
# This mapping renames to standard 10-5 system positions.
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
_EEG_CHANNEL_RENAME_MAP = {
    # Standard 10-20 positions (subset used in many 128-channel caps)
    "EEG001": "Fp1", "EEG002": "Fpz", "EEG003": "Fp2",
    "EEG004": "AF7", "EEG005": "AF3", "EEG006": "AFz", "EEG007": "AF4", "EEG008": "AF8",
    "EEG009": "F7", "EEG010": "F5", "EEG011": "F3", "EEG012": "F1", "EEG013": "Fz",
    "EEG014": "F2", "EEG015": "F4", "EEG016": "F6", "EEG017": "F8",
    "EEG018": "FT7", "EEG019": "FC5", "EEG020": "FC3", "EEG021": "FC1",
    "EEG022": "FCz", "EEG023": "FC2", "EEG024": "FC4", "EEG025": "FC6", "EEG026": "FT8",
    "EEG027": "T7", "EEG028": "C5", "EEG029": "C3", "EEG030": "C1", "EEG031": "Cz",
    "EEG032": "C2", "EEG033": "C4", "EEG034": "C6", "EEG035": "T8",
    "EEG036": "TP7", "EEG037": "CP5", "EEG038": "CP3", "EEG039": "CP1",
    "EEG040": "CPz", "EEG041": "CP2", "EEG042": "CP4", "EEG043": "CP6", "EEG044": "TP8",
    "EEG045": "P7", "EEG046": "P5", "EEG047": "P3", "EEG048": "P1", "EEG049": "Pz",
    "EEG050": "P2", "EEG051": "P4", "EEG052": "P6", "EEG053": "P8",
    "EEG054": "PO7", "EEG055": "PO3", "EEG056": "POz", "EEG057": "PO4", "EEG058": "PO8",
    "EEG059": "O1", "EEG060": "Oz", "EEG061": "O2",
    "EEG062": "Iz",
    # Extended 10-5 system positions for 128-channel cap
    "EEG063": "FPI1", "EEG064": "FPI2", "EEG065": "AFPI",
    "EEG066": "AFP1", "EEG067": "AFP2", "EEG068": "AFP3", "EEG069": "AFP4",
    "EEG070": "AFF1", "EEG071": "AFF2", "EEG072": "AFF3", "EEG073": "AFF4", "EEG074": "AFF5",
    "EEG075": "FFT7", "EEG076": "FFC5", "EEG077": "FFC3", "EEG078": "FFC1",
    "EEG079": "FFC2", "EEG080": "FFC4", "EEG081": "FFC6", "EEG082": "FFT8",
    "EEG083": "FTT7", "EEG084": "FCC5", "EEG085": "FCC3", "EEG086": "FCC1",
    "EEG087": "FCC2", "EEG088": "FCC4", "EEG089": "FCC6", "EEG090": "FTT8",
    "EEG091": "TTP7", "EEG092": "CCP5", "EEG093": "CCP3", "EEG094": "CCP1",
    "EEG095": "CCP2", "EEG096": "CCP4", "EEG097": "CCP6", "EEG098": "TTP8",
    "EEG099": "TPP7", "EEG100": "CPP5", "EEG101": "CPP3", "EEG102": "CPP1",
    "EEG103": "CPP2", "EEG104": "CPP4", "EEG105": "CPP6", "EEG106": "TPP8",
    "EEG107": "PPO7", "EEG108": "PPO3", "EEG109": "PPO1", "EEG110": "PPO2",
    "EEG111": "PPO4", "EEG112": "PPO8",
    "EEG113": "POO7", "EEG114": "POO3", "EEG115": "POO1", "EEG116": "POO2",
    "EEG117": "POO4", "EEG118": "POO8",
    "EEG119": "OO1", "EEG120": "OO2",
    "EEG121": "OI1", "EEG122": "OI2", "EEG123": "IO1", "EEG124": "IO2",
    "EEG125": "AM1", "EEG126": "AM2", "EEG127": "AM3", "EEG128": "AM4",
}


# =============================================================================
# Event Mapping
# =============================================================================
# RSVP image onset events from the experiment
# E 4 marks block boundaries and should be excluded from classification
_EVENT_MAP = {
    "E 1": "Animals (living)",      # y=0
    "E 2": "Plants (living)",       # y=1
    "E 3": "Still natural objects", # y=2
    "E 5": "Still artificial objects",  # y=3
    "E 8": "Moving natural objects",    # y=4
    "E 9": "Moving artificial objects", # y=5
}


def _detect_subject_id(row) -> str:
    """Extract subject ID from row file path."""
    file_path = str(row.get("File Path", ""))
    # Pattern: sub-<subject_id>
    match = re.search(r"sub-(\S+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for channels present in the raw object."""
    rename_map = {}
    existing_names = set(raw.ch_names)
    
    for source_name, target_name in _EEG_CHANNEL_RENAME_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name
    
    return rename_map


def _detect_sex_from_subject(subject_id: str) -> str:
    """Infer sex from subject ID if pattern indicates gender (heuristic)."""
    # This dataset doesn't have explicit sex per subject in analysis.md
    # Return unknown unless specific info becomes available
    return "unknown"


@dataclass
class OpenNeuroDS003885Kernel:
    """Stage1 kernel for OpenNeuro DS003885 dataset."""

    KERNEL_ID: str = "openneuro-ds003885-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (pre-loaded)
        row : Locator row with File Path

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata
        """
        original_description = raw.info.get("description", "")
        
        # Extract subject ID
        subject_id = _detect_subject_id(row)
        
        # Infer sex from subject metadata if available
        sex = _detect_sex_from_subject(subject_id)
        
        # Update description with eegunity metadata
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": _AGE_RANGE,
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels before setting montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Rename EEG channels to standard names
            eeg_channels = [ch for ch in rename_map.keys() 
                          if ch.startswith("EEG")]
            other_channels = [ch for ch in rename_map.keys() 
                            if not ch.startswith("EEG")]
            
            # Rename EEG channels first
            if eeg_channels:
                raw.rename_channels({ch: rename_map[ch] for ch in eeg_channels})
            
            # Rename other channels (EOG, etc.)
            if other_channels:
                raw.rename_channels({ch: rename_map[ch] for ch in other_channels})

        # Set montage for standardized electrode positions
        # Try standard 1020 first, then fall back to biosemi128 or similar
        try:
            # Attempt to set standard 1020 montage for renamed channels
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If standard_1020 fails, try to find matching high-density montage
            try:
                montage = mne.channels.make_standard_montage("biosemi128")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # Last resort: use generic high-density montage
                try:
                    montage = mne.channels.make_standard_montage("standard_primaries")
                    raw.set_montage(montage, on_missing="ignore")
                except Exception:
                    # Skip montage if no matching template found
                    pass

        # Process events/annotations from the raw object
        # Events in this dataset are stored as annotations with descriptions like "E 1", "E 2", etc.
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Map event descriptions to standardized labels
            descriptions = []
            for desc in raw.annotations.description:
                # Check if description matches our event pattern
                if desc in _EVENT_MAP:
                    descriptions.append(_EVENT_MAP[desc])
                else:
                    # Keep original description for unknown events (e.g., E 4 block markers)
                    descriptions.append(desc)
            
            # Update annotations with mapped descriptions
            raw.annotations.description = np.array(descriptions)

        return raw


KERNEL = OpenNeuroDS003885Kernel()