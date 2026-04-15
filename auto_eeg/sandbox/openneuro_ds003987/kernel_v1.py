"""openneuro_ds003987 stage1 kernel for EEGUnity.

Amphetamine trials with 5CCPT and PST tasks.
23 subjects x 3 sessions (placebo/low/high dose) = 69 files.

Events:
  - 5CCPT: 21, 22, 23, 25 (attention task)
  - PST: 31, 32, 39 (probabilistic selection task)
  - STATUS: 65535 (admin marker, exclude from analysis)

Source: https://openneuro.org/datasets/ds003987
Reference: 10.1007/s00213-022-06082.z (Cavanagh et al., 2022)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

import mne
import numpy as np


# Paradigm detection based on file naming convention
def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name."""
    basename = os.path.basename(file_path).lower()
    if "5ccpt" in basename or "_5c" in basename:
        return "5CCPT"
    elif "pst" in basename or "prob" in basename:
        return "PST"
    return ""


# Event mapping with paradigm prefix
# STATUS (65535) is admin marker, excluded from analysis
_PST_EVENT_MAP = {
    31: "31 PST",   # reward feedback
    32: "32 PST",   # punishment feedback
    39: "39 PST",   # neutral feedback
}

_5CCPT_EVENT_MAP = {
    21: "21 5CCPT",
    22: "22 5CCPT",
    23: "23 5CCPT",
    25: "25 5CCPT",
}


def _build_annotations_from_raw(raw: mne.io.BaseRaw, file_path: str) -> mne.Annotations:
    """Build annotations from raw events with paradigm-aware labeling."""
    paradigm = _detect_paradigm(file_path)
    
    # Get events from raw
    events, event_id = mne.events_from_annotations(raw, verbose=False)
    
    descriptions = []
    onsets = []
    durations = []
    
    for event in events:
        code = event[2]
        
        # Skip STATUS (admin marker)
        if code == 65535:
            continue
        
        # Map to paradigm-prefixed label
        if paradigm == "PST":
            label = _PST_EVENT_MAP.get(code)
        elif paradigm == "5CCPT":
            label = _5CCPT_EVENT_MAP.get(code)
        else:
            # Fallback: try all maps
            label = _PST_EVENT_MAP.get(code) or _5CCPT_EVENT_MAP.get(code)
        
        if label is None:
            # Unknown event code
            label = f"unknown_{code}"
        
        onsets.append(event[0] / raw.info["sfreq"])
        durations.append(0.0)
        descriptions.append(label)
    
    return mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )


class OpenNeuroDs003987Kernel:
    """Stage1 kernel for openneuro_ds003987 dataset."""

    KERNEL_ID: str = "openneuro-ds003987-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")

        # Build and set paradigm-aware annotations
        annotations = _build_annotations_from_raw(raw, file_path)
        raw.set_annotations(annotations)

        # Rename channels if needed (standard_1020 expected)
        # Check for non-standard channel names
        rename_map: Dict[str, str] = {}
        for ch in raw.ch_names:
            # Handle potential numeric-prefixed channels like "1" -> "EEG001"
            if ch.isdigit() or (ch.startswith("EEG") and ch[3:].isdigit()):
                pass  # Keep as-is, format_channel_name will handle
            # Standard channels should be fine
            elif ch.upper() in {
                "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
                "T3", "C3", "CZ", "C4", "T4",
                "T5", "P3", "PZ", "P4", "T6",
                "O1", "OZ", "O2",
                "AF7", "AF3", "AF4", "AF8",
                "F1", "F2", "F5", "F6",
                "FC5", "FC3", "FC1", "FC2", "FC4", "FC6",
                "C1", "C2", "C5", "C6",
                "CP5", "CP3", "CP1", "CP2", "CP4", "CP6",
                "P1", "P2", "P5", "P6",
                "PO7", "PO3", "PO4", "PO8",
                "FT7", "FT8", "TP7", "TP8",
                "T1", "T2",
            }:
                pass  # Standard naming, no rename needed
            # EOG channels
            elif ch.upper() in {"EOG", "VEOG", "HEOG", "EOG-LEFT", "EOG-RIGHT", "EOG-UP"}:
                rename_map[ch] = ch.upper().replace("-", "-").replace(" ", "-")
            # Other EEG-like channels - keep as-is
        
        if rename_map:
            raw.rename_channels(rename_map)

        # Try to set montage (standard 1020 cap expected)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Non-standard cap or unknown layout

        # Write description with eegunity_description
        # All metadata unknown for this dataset
        # Source: analysis.md indicates subject_age and subject_sex are missing
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",        # LLM 推断，需人类复核
                "handedness": "unknown", # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDs003987Kernel()