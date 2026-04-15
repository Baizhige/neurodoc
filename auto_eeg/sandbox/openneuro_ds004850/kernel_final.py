"""OpenNeuro ds004850 (ODE Social-Cognitive EEG Dataset) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004850 | Year: 2023 | Channels: 64 | Sampling Rate: 128 Hz
Paradigm: Social-cognitive with hierarchically encoded stimulus conditions.

Event Structure (12-class mapping):
    2200  -> y=0  Primary condition code (dominant)
    72011 -> y=1  Category 7, sub-condition 10, variant 1
    52011 -> y=2  Category 5, sub-condition 10, variant 1
    75011 -> y=3  Category 7, sub-condition 50, variant 1
    55011 -> y=4  Category 5, sub-condition 50, variant 1
    73011 -> y=5  Category 7, sub-condition 30, variant 1
    74011 -> y=6  Category 7, sub-condition 40, variant 1
    53011 -> y=7  Category 5, sub-condition 30, variant 1
    54011 -> y=8  Category 5, sub-condition 40, variant 1
    71011 -> y=9  Category 7, sub-condition 10, variant 1
    2201  -> y=10 Primary condition variant
    51011 -> y=11 Category 5, sub-condition 10, variant 1

XYYZZ event code format: X=category, YY=sub-condition, ZZ=variant

Source: https://openneuro.org/datasets/ds004850 DOI: 10.18112/openneuro.ds004850.v1.0.0
Identical event structure to companion datasets ds004849 and ds004852.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# LLM 推断，需人类复核
# Source: OpenNeuro dataset description, single aggregated file, no subject-level separation
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "aggregate": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
    }
}

# Event code to canonical label mapping (raw meta)
_EVENT_TO_LABEL: Dict[str, str] = {
    "2200": "primary_code_0",
    "72011": "cat7_sub10_var1",
    "52011": "cat5_sub10_var1",
    "75011": "cat7_sub50_var1",
    "55011": "cat5_sub50_var1",
    "73011": "cat7_sub30_var1",
    "74011": "cat7_sub40_var1",
    "53011": "cat5_sub30_var1",
    "54011": "cat5_sub40_var1",
    "71011": "cat7_sub10_var1_dup",
    "2201": "primary_code_variant",
    "51011": "cat5_sub10_var1_main",
}

# LLM 推断，需人类复核
# Source: 64-channel standard_1020 cap systems common in social-cognitive paradigms
_CHANNELS_64_STANDARD: List[str] = [
    "FP1", "FPZ", "FP2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POZ", "PO4", "PO8",
    "O1", "OZ", "O2",
    "IO1", "IO2",
    "AFZ", "Fcz", "CPZ", "POZ",
]


def _detect_events_in_raw(raw: mne.io.BaseRaw) -> bool:
    """Detect if raw annotations contain trigger events."""
    annot = raw.annotations
    if len(annot) == 0:
        return False
    descriptions = set(annot.description)
    event_codes = {"2200", "72011", "52011", "75011", "55011", "73011", "74011", "53011", "54011", "71011", "2201", "51011"}
    return bool(descriptions & event_codes)


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file in BIDS structure."""
    base_path = Path(file_path)
    
    # Check sibling directory structure: sub-XX/eeg/ or just directory
    parent = base_path.parent
    
    # Try to find events.tsv in same directory
    events_candidates = [
        parent / "events.tsv",
        parent / f"{base_path.stem}_events.tsv",
    ]
    
    for candidate in events_candidates:
        if candidate.exists():
            return str(candidate)
    
    # Try parent parent (eeg/ under sub-*/)
    if parent.parent.exists():
        grandparent = parent.parent
        events_candidates = [
            grandparent / "events.tsv",
            grandparent / "eeg" / "events.tsv",
        ]
        for candidate in events_candidates:
            if candidate.exists():
                return str(candidate)
    
    return None


def _parse_events_tsv_to_annotations(events_path: str, sfreq: float) -> mne.Annotations:
    """Parse BIDS events.tsv file into MNE Annotations."""
    try:
        df = pd.read_csv(events_path, sep="\t")
    except Exception:
        return None
    
    required_cols = ["onset", "trial_type"]
    if not all(col in df.columns for col in required_cols):
        return None
    
    onset = df["onset"].values.astype(float)
    description = df["trial_type"].values
    
    duration = np.zeros(len(onset))
    if "duration" in df.columns:
        duration = df["duration"].values.astype(float)
    
    return mne.Annotations(onset=onset, duration=duration, description=description)


def _map_annotation_desc(desc: str) -> str:
    """Map annotation description to canonical label."""
    desc_str = str(desc).strip()
    
    # Direct mapping for numeric event codes
    if desc_str in _EVENT_TO_LABEL:
        return _EVENT_TO_LABEL[desc_str]
    
    # Check if it's a numeric code as int
    try:
        code = int(float(desc_str))
        code_str = str(code)
        if code_str in _EVENT_TO_LABEL:
            return _EVENT_TO_LABEL[code_str]
    except (ValueError, TypeError):
        pass
    
    return desc_str


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 64-channel standard_1020 cap."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common non-standard naming patterns for 64-channel systems
    alias_groups = [
        # Standard 10-20 names
        ("FP1", ["Fp1", "fp1", "EEG-Fp1", "EEG_Fp1"]),
        ("FPZ", ["FpZ", "fpz", "Fpz", "EEG-Fpz", "EEG_Fpz"]),
        ("FP2", ["Fp2", "fp2", "EEG-Fp2", "EEG_Fp2"]),
        ("F7", ["F7", "f7", "EEG-F7"]),
        ("F3", ["F3", "f3", "EEG-F3"]),
        ("F1", ["F1", "f1", "EEG-F1"]),
        ("FZ", ["Fz", "fz", "EEG-Fz"]),
        ("F2", ["F2", "f2", "EEG-F2"]),
        ("F4", ["F4", "f4", "EEG-F4"]),
        ("F6", ["F6", "f6", "EEG-F6"]),
        ("F8", ["F8", "f8", "EEG-F8"]),
        ("T7", ["T7", "t7", "T3", "T4" if "T4" not in existing else None], "T8"),
        ("C3", ["C3", "c3", "EEG-C3"]),
        ("C1", ["C1", "c1", "EEG-C1"]),
        ("CZ", ["Cz", "cz", "EEG-Cz"]),
        ("C2", ["C2", "c2", "EEG-C2"]),
        ("C4", ["C4", "c4", "EEG-C4"]),
        ("T8", ["T8", "t8", "T4"]),
        ("P7", ["P7", "p7", "P3" if "P3" not in existing else None], "P8"),
        ("P3", ["P3", "p3", "EEG-P3"]),
        ("P1", ["P1", "p1", "EEG-P1"]),
        ("PZ", ["Pz", "pz", "EEG-Pz"]),
        ("P2", ["P2", "p2", "EEG-P2"]),
        ("P4", ["P4", "p4", "EEG-P4"]),
        ("P8", ["P8", "p8", "P4" if "P4" not in existing else None]),
        ("O1", ["O1", "o1", "EEG-O1"]),
        ("OZ", ["Oz", "oz", "EEG-Oz"]),
        ("O2", ["O2", "o2", "EEG-O2"]),
    ]
    
    for group in alias_groups:
        target = group[0]
        aliases = group[1] if isinstance(group[1], list) else group[:-1]
        for alias in aliases:
            if alias and alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    # Handle numeric EEG-XX pattern
    numeric_pattern = re.compile(r"^(?:EEG[-_]?)?(\d+)$", re.IGNORECASE)
    for ch in raw.ch_names:
        match = numeric_pattern.match(ch)
        if match:
            # Check if this might need renaming based on position
            pass  # Keep as-is unless pattern confirmed
    
    return rename_map


@dataclass
class ODEKernel:
    """Stage1 kernel for OpenNeuro ds004850 (ODE Social-Cognitive EEG Dataset)."""

    KERNEL_ID: str = "openneuro-ds004850-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to ODE dataset.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with File Path

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with annotations and description
        """
        file_path = row.get("File Path", row.get("file_path", ""))
        subject_id = row.get("subject_id", "aggregate")
        
        # Get subject metadata
        subject_meta = _SUBJECT_DICT.get(subject_id, _SUBJECT_DICT["aggregate"])
        
        # Preserve original description
        orig_desc = raw.info.get("description", "")
        
        # Build eegunity_description
        eegunity_desc = {
            "age": subject_meta.get("age", "unknown"),
            "sex": subject_meta.get("sex", "unknown"),
            "handedness": subject_meta.get("handedness", "unknown"),
            "amplifier": subject_meta.get("amplifier", "unknown"),
            "cap": subject_meta.get("cap", "unknown"),
        }
        
        # Write to raw.info["description"]
        raw.info["description"] = json.dumps({
            "original_description": orig_desc,
            "eegunity_description": eegunity_desc,
        })
        
        # Handle channel naming
        current_names = raw.ch_names
        
        # Check for non-standard channel names
        has_numeric_names = any(
            re.match(r"^(?:EEG[-_]?)?\d+$", ch) for ch in current_names
        )
        
        if has_numeric_names or len(current_names) == 64:
            rename_map = _build_channel_rename_map(raw)
            if rename_map:
                try:
                    raw.rename_channels(rename_map)
                except Exception:
                    pass  # Skip if rename fails
        
        # Try to set standard montage if channels look standard
        try:
            standard_channels = {"FP1", "FPZ", "FP2", "F7", "F3", "FZ", "F4", "F8", 
                                 "T7", "C3", "CZ", "C4", "T8", "P7", "P3", "PZ", 
                                 "P4", "P8", "O1", "OZ", "O2"}
            current_set = set(raw.ch_names)
            if len(current_set & standard_channels) >= 10:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if not applicable
        
        # Process annotations
        has_raw_events = _detect_events_in_raw(raw)
        
        if not has_raw_events:
            # Try to find and parse events.tsv
            events_path = _find_events_tsv(file_path)
            if events_path:
                events_annot = _parse_events_tsv_to_annotations(
                    events_path, raw.info["sfreq"]
                )
                if events_annot is not None and len(events_annot) > 0:
                    raw.set_annotations(events_annot)
                    has_raw_events = True
        
        # Remap event descriptions to canonical labels
        if has_raw_events and len(raw.annotations) > 0:
            annot = raw.annotations
            remapped_desc = [_map_annotation_desc(d) for d in annot.description]
            
            # Check if remapping actually changed anything
            if remapped_desc != list(annot.description):
                raw.annotations.description = remapped_desc
        
        return raw


KERNEL = ODEKernel()