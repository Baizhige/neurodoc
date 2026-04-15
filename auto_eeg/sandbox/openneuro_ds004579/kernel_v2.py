"""OpenNeuro DS004579 stage1 kernel for EEGUnity.

Interval Timing Task dataset - 30 subjects, 64 channels, 512 Hz.

Events: S 1-S 7 (timing conditions), R 3 (button press response),
boundary, S255 (BrainVision system marker).

Source: https://openneuro.org/datasets/ds004579
Reference: DOI 10.1523/JNEUROSCI.1675-24.2025
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

import mne


# Standard 64-channel EEG montage (extended 10-20 system)
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Cz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]

# BrainVision channel naming patterns
_BV_CHANNEL_PATTERNS = {
    "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
    "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4",
    "F3": "F3", "FZ": "Fz", "F4": "F4",
    "F7": "F7", "F8": "F8",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "T7": "T7", "T8": "T8",
    "C3": "C3", "CZ": "Cz", "C4": "C4",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    "P7": "P7", "P3": "P3", "PZ": "Pz", "P4": "P4", "P8": "P8",
    "PO7": "PO7", "PO3": "PO3", "POZ": "POz", "PO4": "PO4", "PO8": "PO8",
    "O1": "O1", "OZ": "Oz", "O2": "O2",
}


def _detect_channel_pattern(ch_names: List[str]) -> str:
    sample_names = ch_names[:10] if len(ch_names) >= 10 else ch_names
    standard_count = sum(1 for ch in sample_names if ch in _STANDARD_64_CHANNELS)
    if standard_count >= len(sample_names) * 0.5:
        return "standard"
    bv_count = sum(1 for ch in sample_names if ch.upper() in _BV_CHANNEL_PATTERNS)
    if bv_count >= len(sample_names) * 0.5:
        return "brainvision"
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    ch_names = raw.ch_names
    pattern = _detect_channel_pattern(ch_names)
    rename_map: Dict[str, str] = {}
    
    if pattern == "brainvision":
        for ch in ch_names:
            upper_ch = ch.upper()
            if upper_ch in _BV_CHANNEL_PATTERNS:
                target = _BV_CHANNEL_PATTERNS[upper_ch]
                if ch != target:
                    rename_map[ch] = target
    
    return rename_map


def _parse_subject_id(row) -> str:
    file_path = ''
    subject_id = ''
    
    if hasattr(row, 'get'):
        file_path = str(row.get('File Path', row.get('file_path', '')))
        subject_id = str(row.get('subject_id', row.get('subject', '')))
    elif isinstance(row, dict):
        file_path = str(row.get('File Path', row.get('file_path', '')))
        subject_id = str(row.get('subject_id', row.get('subject', '')))
    
    if not subject_id and file_path:
        match = re.search(r'sub-(\w+)', file_path, re.IGNORECASE)
        if match:
            subject_id = match.group(1)
    
    return subject_id or "unknown"


def _remap_annotations(descriptions: List[str]) -> List[str]:
    new_descs = []
    for desc in descriptions:
        desc = str(desc).strip()
        if desc.startswith('S '):
            code = desc[2:].strip()
            new_descs.append(f"stimulus_{code}")
        elif desc.startswith('S'):
            code = desc[1:].strip()
            new_descs.append(f"stimulus_{code}")
        elif desc.startswith('R '):
            code = desc[2:].strip()
            new_descs.append(f"response_{code}")
        elif desc == 'boundary':
            new_descs.append('boundary')
        else:
            new_descs.append(desc)
    return new_descs


# Required eegunity_description for DS004579
eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "unknown",
    "cap": "unknown",
    "handedness": "unknown",
}


class OpenNeuroDS004579Kernel:
    """Stage1 kernel for OpenNeuro DS004579 Interval Timing Task."""

    KERNEL_ID: str = "openneuro-ds004579-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        subject_id = _parse_subject_id(row)
        
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        n_channels = len(raw.ch_names)
        if n_channels == 64:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="warn")
            except Exception:
                pass
        
        if len(raw.annotations) > 0:
            descs = list(raw.annotations.description)
            new_descs = _remap_annotations(descs)
            if new_descs != descs:
                raw.annotations.description = new_descs
        
        raw.info['subject_info'] = {
            'id': subject_id,
            'sex': eegunity_description.get('sex', 'unknown'),
            'handedness': eegunity_description.get('handedness', 'unknown'),
        }
        raw.info['kernel_id'] = self.KERNEL_ID
        
        return raw


KERNEL = OpenNeuroDS004579Kernel()