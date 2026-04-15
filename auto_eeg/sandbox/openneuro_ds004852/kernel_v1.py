"""InsurgentCivilian (ds004852) stage1 kernel for EEGUnity.

Threat-classification EEG dataset with social-cognitive paradigm.
64 channels, 128 Hz, BrainVision format (OpenNeuro).

Tasks supported:
  - Threat Stimulus Classification (multiclass, 10 classes)
  - Response Monitoring (response-locked)

Source: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Annotator: LLM, 2026-04-08
# Source: Dataset README and paper (DOI: 10.1038/s41598-025-24919-3)
# LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "default": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    },
}

# Annotator: LLM, 2026-04-08
# Source: OpenNeuro dataset description (ds004852)
# 64-channel EEG typically uses standard 1020 cap layout (BioSemi ActiveTwo or equivalent)
# LLM 推断，需人类复核
_AMPLIFIER = "unknown"
_CAP = "unknown"

# Threat stimulus event mapping (Task 1)
_STIMULUS_EVENT_MAP: Dict[int, Dict[str, Any]] = {
    51011: {"y": 0, "label": "threat_cat_1", "meaning": "Threat stimulus category 1"},
    52011: {"y": 1, "label": "threat_cat_2", "meaning": "Threat stimulus category 2"},
    53011: {"y": 2, "label": "threat_cat_3", "meaning": "Threat stimulus category 3"},
    54011: {"y": 3, "label": "threat_cat_4", "meaning": "Threat stimulus category 4"},
    55011: {"y": 4, "label": "threat_cat_5", "meaning": "Threat stimulus category 5"},
    71011: {"y": 5, "label": "threat_cat_6", "meaning": "Threat stimulus category 6"},
    72011: {"y": 6, "label": "threat_cat_7", "meaning": "Threat stimulus category 7"},
    73011: {"y": 7, "label": "threat_cat_8", "meaning": "Threat stimulus category 8"},
    74011: {"y": 8, "label": "threat_cat_9", "meaning": "Threat stimulus category 9"},
    75011: {"y": 9, "label": "threat_cat_10", "meaning": "Threat stimulus category 10"},
}

# Response event mapping (Task 2)
_RESPONSE_EVENT_MAP: Dict[int, Dict[str, Any]] = {
    1:    {"y": 0, "label": "response_primary", "meaning": "Primary response marker"},
    1103: {"y": 1, "label": "response_type_A", "meaning": "Response type A"},
    1113: {"y": 2, "label": "response_type_B", "meaning": "Response type B"},
    2090: {"y": 3, "label": "response_variant_0", "meaning": "Response variant 0"},
    2091: {"y": 4, "label": "response_variant_1", "meaning": "Response variant 1"},
    2092: {"y": 5, "label": "response_variant_2", "meaning": "Response variant 2"},
    2093: {"y": 6, "label": "response_variant_3", "meaning": "Response variant 3"},
    2094: {"y": 7, "label": "response_variant_4", "meaning": "Response variant 4"},
    2095: {"y": 8, "label": "response_variant_5", "meaning": "Response variant 5"},
    2096: {"y": 9, "label": "response_variant_6", "meaning": "Response variant 6"},
    2097: {"y": 10, "label": "response_variant_7", "meaning": "Response variant 7"},
    2098: {"y": 11, "label": "response_variant_8", "meaning": "Response variant 8"},
}

# Trial-structure markers (excluded from classification tasks)
_TRIAL_STRUCTURE_EVENTS = {
    2200: "trial_fixation",
    2201: "trial_marker",
}


def _detect_file_format(file_path: str) -> str:
    """Detect file format from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".vhdr", ".eeg", ".vmrk"]:
        return "brainvision"
    elif ext in [".edf", ".bdf"]:
        return "edf"
    elif ext in [".set", ".fdt"]:
        return "eeglab"
    else:
        return "unknown"


def _load_raw_brainvision(file_path: str) -> mne.io.BaseRaw:
    """Load BrainVision format file."""
    # Find .vhdr file
    base_path = file_path
    if base_path.endswith(".eeg") or base_path.endswith(".vmrk"):
        base_path = re.sub(r"\.(eeg|vmrk)$", "", base_path)
    
    vhdr_path = base_path + ".vhdr"
    if not os.path.exists(vhdr_path):
        # Try other naming conventions
        dir_path = os.path.dirname(file_path)
        basename = os.path.splitext(os.path.basename(file_path))[0]
        vhdr_path = os.path.join(dir_path, basename + ".vhdr")
    
    raw = mne.io.read_raw_brainvision(vhdr_path, preload=False, verbose=False)
    return raw


def _extract_annotations_from_brainvision(vhdr_path: str, sfreq: float) -> mne.Annotations:
    """Extract trigger annotations from BrainVision marker file."""
    base_path = vhdr_path.replace(".vhdr", "")
    vmrk_path = base_path + ".vmrk"
    
    if not os.path.exists(vmrk_path):
        # Try to find vmrk file
        dir_path = os.path.dirname(vhdr_path)
        for f in os.listdir(dir_path):
            if f.endswith(".vmrk"):
                vmrk_path = os.path.join(dir_path, f)
                break
    
    onsets = []
    descriptions = []
    durations = []
    
    # Parse VMrk file for trigger markers
    with open(vmrk_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Find Marker sections
    for match in re.finditer(r"\[Marker\s*\d+\](.*?)(?=\[Marker|\Z)", content, re.DOTALL):
        marker_block = match.group(1)
        
        # Extract fields
        type_m = re.search(r"Type=\s*(\S+)", marker_block)
        desc_m = re.search(r"Description=\s*(.+)", marker_block)
        time_m = re.search(r"Time=\s*(\d+)", marker_block)
        duration_m = re.search(r"Duration=\s*(\d+)", marker_block)
        
        if type_m and desc_m and time_m:
            marker_type = type_m.group(1).strip()
            description = desc_m.group(1).strip()
            time_ms = int(time_m.group(1))
            onset_sec = time_ms / 1000.0
            
            if marker_type == "Stimulus":
                # Try to parse numeric code from description
                code_match = re.search(r"(\d+)", description)
                if code_match:
                    code = int(code_match.group(1))
                    onsets.append(onset_sec)
                    descriptions.append(f"stim_{code}")
                    durations.append(0.0)
    
    if not onsets:
        # Fallback: use MNE's annotation parsing
        return None
    
    annotations = mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )
    return annotations


def _map_event_to_label(code: int) -> str:
    """Map event code to human-readable label."""
    if code in _STIMULUS_EVENT_MAP:
        return _STIMULUS_EVENT_MAP[code]["label"]
    elif code in _RESPONSE_EVENT_MAP:
        return _RESPONSE_EVENT_MAP[code]["label"]
    elif code in _TRIAL_STRUCTURE_EVENTS:
        return _TRIAL_STRUCTURE_EVENTS[code]
    else:
        return f"event_{code}"


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed."""
    ch_names = raw.ch_names
    
    # Common patterns: EEG001 -> FC3, etc.
    rename_map = {}
    eeg_channels = [c for c in ch_names if c.startswith("EEG") or c.startswith("eeg")]
    
    # Standard 64-channel layout (Extended 10-20)
    standard_64 = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "FT7", "FC3", "FCz", "FC4", "FT8",
        "T7", "C3", "Cz", "C4", "T8",
        "TP7", "CP3", "CPz", "CP4", "TP8",
        "P7", "P3", "Pz", "P4", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        # Additional channels for 64-channel cap
        "FPO1", "FPO2", "AF7", "AF3", "AFz", "AF4", "AF8",
        "FTT7", "FTT8", "TTP7", "TTP8",
        "POO1", "POO2",
        # Continue with remaining...
    ]
    
    # For BrainVision data, channels are often named EEG001, EEG002, etc.
    # or numbered like 1, 2, 3...
    if len(eeg_channels) >= 64:
        # Assume standard layout
        for i, ch in enumerate(eeg_channels):
            if i < len(standard_64):
                if ch != standard_64[i]:
                    rename_map[ch] = standard_64[i]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


@dataclass
class InsurgentCivilianKernel:
    """Stage1 kernel for InsurgentCivilian (ds004852) dataset."""

    KERNEL_ID: str = "insurgent-civilian-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", "")
        
        # Detect file format
        fmt = _detect_file_format(file_path)
        
        # Update description with metadata
        original_desc = raw.info.get("description", "")
        
        # Try to extract subject info from dataset
        subject_info = _SUBJECT_DICT.get("default", {})
        
        # Check for participants.tsv in dataset
        participants_tsv = os.path.join(dataset_path, "participants.tsv")
        if os.path.exists(participants_tsv):
            import pandas as pd
            try:
                df = pd.read_csv(participants_tsv, sep="\t")
                if len(df) > 0:
                    row_data = df.iloc[0]
                    subject_info = {
                        "age": str(int(row_data.get("age", "unknown"))) if pd.notna(row_data.get("age")) else "unknown",
                        "sex": str(row_data.get("sex", "unknown")).lower() if pd.notna(row_data.get("sex")) else "unknown",
                        "handedness": str(row_data.get("handedness", "unknown")).lower() if pd.notna(row_data.get("handedness")) else "unknown",
                    }
            except Exception:
                pass
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard names if needed
        raw = _rename_channels_to_standard(raw)
        
        # Try to set standard montage
        try:
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        
        # Create annotations from trigger events
        # BrainVision format stores triggers in .vmrk file
        if fmt == "brainvision":
            vhdr_path = file_path
            if vhdr_path.endswith(".eeg") or vhdr_path.endswith(".vmrk"):
                vhdr_path = re.sub(r"\.(eeg|vmrk)$", "", vhdr_path)
            vhdr_path = vhdr_path + ".vhdr"
            
            annotations = _extract_annotations_from_brainvision(vhdr_path, raw.info["sfreq"])
            if annotations:
                raw.set_annotations(annotations)
        
        return raw


KERNEL = InsurgentCivilianKernel()