"""OpenNeuro ds006525 stage1 kernel for EEGUnity.

Resting-state EEG dataset with 34 subjects, 128 channels, 250 Hz sampling rate.
Includes structural MRI scans. Events: bgin, rsts, rstf, NRST, DIN.

Source: https://openneuro.org/datasets/ds006525
Reference: https://doi.org/10.1016/j.neuroimage.2022.119461
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# === Subject metadata ===
# Source: Dataset documentation and reference papers
# Annotator: LLM, 2026-04-08
# Note: All fields marked as LLM推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 35)
}

# === Channel rename map ===
# Source: Standard 128-channel layout (BioSemi ActiveTwo or similar 128-chan cap)
# The dataset uses standard 1020 extension with additional channels
# Annotator: LLM, 2026-04-08
# Note: LLM 推断，需人类复核
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 positions
    "Fp1": "EEG-Fp1",
    "Fp2": "EEG-Fp2",
    "F7": "EEG-F7",
    "F3": "EEG-F3",
    "Fz": "EEG-Fz",
    "F4": "EEG-F4",
    "F8": "EEG-F8",
    "T7": "EEG-T7",
    "C3": "EEG-C3",
    "Cz": "EEG-Cz",
    "C4": "EEG-C4",
    "T8": "EEG-T8",
    "P7": "EEG-P7",
    "P3": "EEG-P3",
    "Pz": "EEG-Pz",
    "P4": "EEG-P4",
    "P8": "EEG-P8",
    "O1": "EEG-O1",
    "O2": "EEG-O2",
}

# === Event mapping ===
_EVENT_MAP = {
    "bgin": 0,   # Session begin marker
    "rsts": 1,   # Resting-state block start
    "rstf": 2,   # Resting-state block end
    "NRST": 3,   # Non-resting state marker
    "DIN": 4,    # Digital input trigger
}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r"(sub-\d+)", file_path)
    return match.group(1) if match else "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map based on existing channel names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common non-standard naming patterns in EEG datasets
    patterns = [
        # Numeric patterns like "0", "1", ... or "EEG 001"
        (r"^(\d+)$", lambda m: f"EEG-{int(m.group(1))-1:02d}"),
        (r"^EEG\s*(\d+)$", lambda m: f"EEG-{int(m.group(1))-1:02d}"),
        (r"^EEG-(\d+)$", lambda m: f"EEG-{int(m.group(1))-1:02d}"),
    ]
    
    for ch in existing:
        if ch.startswith("EEG") or ch.startswith("Fp") or ch.startswith("F") or \
           ch.startswith("T") or ch.startswith("C") or ch.startswith("P") or \
           ch.startswith("O"):
            # Already standardized or standard name
            if not ch.startswith("EEG-"):
                target = f"EEG-{ch}" if ch in _EEG_CHANNEL_RENAME_MAP else None
                if target:
                    rename_map[ch] = target
        else:
            # Try numeric patterns
            for pattern, repl in patterns:
                match = re.match(pattern, ch)
                if match:
                    rename_map[ch] = repl(match)
                    break
    
    return rename_map


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard montage, skip if not possible."""
    try:
        # Try standard 1020 first, then extended
        for montage_name in ["standard_1020", "standard_1005", "GSN-HydroCel-128"]:
            try:
                montage = mne.channels.make_standard_montage(montage_name)
                # Check if most channels are covered
                available = set(raw.ch_names) & set(montage.ch_names)
                if len(available) > 60:  # At least 60 channels match
                    raw.set_montage(montage_name, on_missing="warn")
                    return
            except Exception:
                continue
    except Exception:
        pass


@dataclass
class OpenNeuroDS006525Kernel:
    """Stage1 kernel for OpenNeuro ds006525 dataset."""

    KERNEL_ID: str = "openneuro-ds006525-stage1"
    HANDLES_UNAVAILABLE: bool = False  # Set True if EEGUnity cannot parse format

    def load(self, file_path: str) -> mne.io.BaseRaw:
        """Load raw data from file path.
        
        Called by EEGUnity when standard parsing fails.
        Override this method if HANDLES_UNAVAILABLE = True.
        """
        raise NotImplementedError("Use standard EEGUnity loading")

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : In-memory MNE Raw object
        row : Locator row with File Path

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id(file_path)
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # Get original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description
        eegunity_desc = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "unknown",  # LLM 推断，需人类复核
            "cap": "unknown",        # LLM 推断，需人类复核
            "handedness": subject_info.get("handedness", "unknown"),
        }

        # Update description
        description_dict = {
            "original_description": original_desc or "",
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard format if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # Try to set montage after renaming
        _try_set_montage(raw)

        # Process events from annotations or info
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        
        # Build new annotations based on event structure
        new_onsets = []
        new_durations = []
        new_descriptions = []
        
        for evt in events:
            sample, _, event_val = evt
            onset = sample / raw.info["sfreq"]
            
            # Map event values to canonical names
            if event_val == 1 or event_val == "rsts":
                desc = "rsts"
            elif event_val == 2 or event_val == "rstf":
                desc = "rstf"
            elif event_val == 3 or event_val == "NRST":
                desc = "NRST"
            elif event_val == 4 or event_val == "DIN":
                desc = "DIN"
            elif event_val == 5 or event_val == "bgin":
                desc = "bgin"
            else:
                desc = f"event-{event_val}"
            
            new_onsets.append(onset)
            new_durations.append(0.0)
            new_descriptions.append(desc)

        # Create new annotations
        if new_onsets:
            annotations = mne.Annotations(
                onset=np.array(new_onsets),
                duration=np.array(new_durations),
                description=new_descriptions,
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS006525Kernel()