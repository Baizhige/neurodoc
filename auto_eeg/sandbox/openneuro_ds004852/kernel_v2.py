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
from typing import Any, Dict

import mne
import numpy as np


_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "default": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    },
}

_AMPLIFIER = "unknown"
_CAP = "unknown"

_STIMULUS_EVENT_MAP: Dict[int, Dict[str, Any]] = {
    51011: {"y": 0, "label": "threat_cat_1"},
    52011: {"y": 1, "label": "threat_cat_2"},
    53011: {"y": 2, "label": "threat_cat_3"},
    54011: {"y": 3, "label": "threat_cat_4"},
    55011: {"y": 4, "label": "threat_cat_5"},
    71011: {"y": 5, "label": "threat_cat_6"},
    72011: {"y": 6, "label": "threat_cat_7"},
    73011: {"y": 7, "label": "threat_cat_8"},
    74011: {"y": 8, "label": "threat_cat_9"},
    75011: {"y": 9, "label": "threat_cat_10"},
}

_RESPONSE_EVENT_MAP: Dict[int, Dict[str, Any]] = {
    1:    {"y": 0, "label": "response_primary"},
    1103: {"y": 1, "label": "response_type_A"},
    1113: {"y": 2, "label": "response_type_B"},
    2090: {"y": 3, "label": "response_variant_0"},
    2091: {"y": 4, "label": "response_variant_1"},
    2092: {"y": 5, "label": "response_variant_2"},
    2093: {"y": 6, "label": "response_variant_3"},
    2094: {"y": 7, "label": "response_variant_4"},
    2095: {"y": 8, "label": "response_variant_5"},
    2096: {"y": 9, "label": "response_variant_6"},
    2097: {"y": 10, "label": "response_variant_7"},
    2098: {"y": 11, "label": "response_variant_8"},
}

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
    return "unknown"


def _find_vhdr_path(file_path: str) -> str | None:
    """Find .vhdr file path from any BrainVision component."""
    base = file_path
    for ext in [".eeg", ".vmrk", ".vhdr"]:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    vhdr_path = base + ".vhdr"
    if os.path.exists(vhdr_path):
        return vhdr_path
    
    dir_path = os.path.dirname(file_path)
    basename = os.path.splitext(os.path.basename(base))[0]
    vhdr_candidate = os.path.join(dir_path, basename + ".vhdr")
    if os.path.exists(vhdr_candidate):
        return vhdr_candidate
    
    return None


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed."""
    ch_names = raw.ch_names
    eeg_channels = [c for c in ch_names if c.startswith("EEG") or c.startswith("eeg")]
    
    if not eeg_channels:
        return raw
    
    standard_64 = [
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "FT7", "FC3", "FCz", "FC4", "FT8", "T7", "C3", "Cz", "C4", "T8",
        "TP7", "CP3", "CPz", "CP4", "TP8", "P7", "P3", "Pz", "P4", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
        "FPO1", "FPO2", "AF7", "AF3", "AFz", "AF4", "AF8",
        "FTT7", "FTT8", "TTP7", "TTP8", "POO1", "POO2",
    ]
    
    rename_map = {}
    for i, ch in enumerate(eeg_channels):
        if i < len(standard_64):
            if ch != standard_64[i]:
                rename_map[ch] = standard_64[i]
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _extract_annotations(vhdr_path: str) -> mne.Annotations | None:
    """Extract trigger annotations from BrainVision marker file."""
    base_path = vhdr_path.replace(".vhdr", "")
    vmrk_path = base_path + ".vmrk"
    
    if not os.path.exists(vmrk_path):
        dir_path = os.path.dirname(vhdr_path)
        for f in os.listdir(dir_path):
            if f.endswith(".vmrk"):
                vmrk_path = os.path.join(dir_path, f)
                break
        else:
            return None
    
    onsets = []
    descriptions = []
    durations = []
    
    try:
        with open(vmrk_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return None
    
    marker_pattern = re.compile(r"\[Marker\s*\d+\](.*?)(?=\[Marker|\Z)", re.DOTALL)
    for match in marker_pattern.finditer(content):
        marker_block = match.group(1)
        
        type_m = re.search(r"Type=\s*(\S+)", marker_block)
        desc_m = re.search(r"Description=\s*(.+)", marker_block)
        time_m = re.search(r"Time=\s*(\d+)", marker_block)
        
        if type_m and desc_m and time_m:
            if type_m.group(1).strip() == "Stimulus":
                code_match = re.search(r"(\d+)", desc_m.group(1).strip())
                if code_match:
                    onsets.append(int(time_m.group(1)) / 1000.0)
                    descriptions.append(f"stim_{code_match.group(1)}")
                    durations.append(0.0)
    
    if not onsets:
        return None
    
    return mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )


def _map_event_to_label(code: int) -> str:
    """Map event code to human-readable label."""
    if code in _STIMULUS_EVENT_MAP:
        return _STIMULUS_EVENT_MAP[code]["label"]
    elif code in _RESPONSE_EVENT_MAP:
        return _RESPONSE_EVENT_MAP[code]["label"]
    elif code in _TRIAL_STRUCTURE_EVENTS:
        return _TRIAL_STRUCTURE_EVENTS[code]
    return f"event_{code}"


def _apply_event_mapping(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply event mapping to annotations."""
    if len(raw.annotations) == 0:
        return raw
    
    new_descriptions = []
    for desc in raw.annotations.description:
        if desc.startswith("stim_"):
            try:
                code = int(desc.split("_")[1])
                new_descriptions.append(_map_event_to_label(code))
            except (ValueError, IndexError):
                new_descriptions.append(desc)
        else:
            new_descriptions.append(desc)
    
    raw.set_annotations(mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
    ))
    
    return raw


eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "unknown",
    "cap": "unknown",
    "handedness": "unknown",
}


class Kernel:
    """EEGUnity kernel for openneuro_ds004852 dataset."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("filepath", "")
        file_format = _detect_file_format(file_path)
        
        if file_format == "unknown":
            return raw
        
        if file_format == "brainvision":
            vhdr_path = _find_vhdr_path(file_path)
            if vhdr_path:
                raw = mne.io.read_raw_brainvision(vhdr_path, preload=False, verbose=False)
                raw = _rename_channels_to_standard(raw)
                annotations = _extract_annotations(vhdr_path)
                if annotations is not None:
                    raw.set_annotations(annotations)
                raw = _apply_event_mapping(raw)
        
        return raw


KERNEL = Kernel()