"""OpenNeuro DS004514 stage1 kernel for EEGUnity.

Semantic decoding dataset: simultaneous EEG and fNIRS recordings for 
imagined animals and tools across four modalities (visual imagery, 
silent naming, auditory imagery, drawing imagery).

Source: https://openneuro.org/datasets/ds004514
Paper: DOI 10.1038/s41597-025-04967-0

32 channels, 500 Hz, 22 subjects
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

_EEG_CHANNEL_NAMES_STANDARD = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "POz",
    "O1", "Oz", "O2"
]

_EVENT_CODE_MAP: Dict[int, str] = {
    1: "animal_visual_image",
    2: "tool_visual_image",
    3: "audio_animal",
    4: "audio_tool",
    5: "written_animal",
    6: "written_tool",
    7: "animal_drawing",
    8: "tool_drawing",
    127: "animal_visual_imagery_task",
    128: "tool_visual_imagery_task",
    129: "animal_silent_naming_task",
    130: "tool_silent_naming_task",
    131: "animal_auditory_imagery_task",
    132: "tool_auditory_imagery_task",
    133: "animal_drawing_imagery_task",
    134: "tool_drawing_imagery_task",
    255: "rest",
}


def _detect_paradigm(file_path: str) -> str:
    basename = os.path.basename(file_path)
    if "eeg" in basename.lower():
        return ""
    return ""


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "fp1", "EEG.Fp1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "fpz", "EEG.Fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "fp2", "EEG.Fp2"]),
        ("F7", ["F7", "EEG-F7", "f7", "EEG.F7"]),
        ("F3", ["F3", "EEG-F3", "f3", "EEG.F3"]),
        ("Fz", ["Fz", "EEG-Fz", "fz", "EEG.Fz"]),
        ("F4", ["F4", "EEG-F4", "f4", "EEG.F4"]),
        ("F8", ["F8", "EEG-F8", "f8", "EEG.F8"]),
        ("FC5", ["FC5", "EEG-FC5", "fc5", "EEG.FC5"]),
        ("FC1", ["FC1", "EEG-FC1", "fc1", "EEG.FC1"]),
        ("FCz", ["FCz", "EEG-FCz", "fcz", "EEG.FCz"]),
        ("FC2", ["FC2", "EEG-FC2", "fc2", "EEG.FC2"]),
        ("FC6", ["FC6", "EEG-FC6", "fc6", "EEG.FC6"]),
        ("T7", ["T7", "EEG-T7", "t7", "EEG.T7"]),
        ("C3", ["C3", "EEG-C3", "c3", "EEG.C3"]),
        ("Cz", ["Cz", "EEG-Cz", "cz", "EEG.Cz"]),
        ("C4", ["C4", "EEG-C4", "c4", "EEG.C4"]),
        ("T8", ["T8", "EEG-T8", "t8", "EEG.T8"]),
        ("CP5", ["CP5", "EEG-CP5", "cp5", "EEG.CP5"]),
        ("CP1", ["CP1", "EEG-CP1", "cp1", "EEG.CP1"]),
        ("CPz", ["CPz", "EEG-CPz", "cpz", "EEG.CPz"]),
        ("CP2", ["CP2", "EEG-CP2", "cp2", "EEG.CP2"]),
        ("CP6", ["CP6", "EEG-CP6", "cp6", "EEG.CP6"]),
        ("P7", ["P7", "EEG-P7", "p7", "EEG.P7"]),
        ("P3", ["P3", "EEG-P3", "p3", "EEG.P3"]),
        ("Pz", ["Pz", "EEG-Pz", "pz", "EEG.Pz"]),
        ("P4", ["P4", "EEG-P4", "p4", "EEG.P4"]),
        ("P8", ["P8", "EEG-P8", "p8", "EEG.P8"]),
        ("POz", ["POz", "EEG-POz", "poz", "EEG.POz"]),
        ("O1", ["O1", "EEG-O1", "o1", "EEG.O1"]),
        ("Oz", ["Oz", "EEG-Oz", "oz", "EEG.Oz"]),
        ("O2", ["O2", "EEG-O2", "o2", "EEG.O2"]),
        ("M1", ["M1", "A1", "EEG-A1"]),
        ("M2", ["M2", "A2", "EEG-A2"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _process_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw.rename_channels(rename_map)
    
    eeg_channels = [ch for ch in raw.ch_names if ch not in ["M1", "M2", "EOG"]]
    other_channels = [ch for ch in raw.ch_names if ch in ["M1", "M2"]]
    
    if eeg_channels:
        raw = raw.pick_channels(eeg_channels + other_channels, ordered=True)
    
    return raw


def _map_events_from_stim_channel(raw: mne.io.BaseRaw) -> mne.Annotations:
    sfreq = raw.info["sfreq"]
    
    stim_ch = None
    ch_type = mne.pick_types(raw.info, stim=True, meg=False, eeg=False)
    if ch_type.size > 0:
        stim_ch = raw.ch_names[ch_type[0]]
    
    if stim_ch is None:
        for ch_name in raw.ch_names:
            if "stim" in ch_name.lower() or "trigger" in ch_name.lower():
                stim_ch = ch_name
                break
    
    if stim_ch is None:
        return raw.annotations if len(raw.annotations) > 0 else mne.Annotations(onset=[], duration=[], description=[])
    
    stim_data, _ = raw[stim_ch]
    stim_data = stim_data.flatten()
    
    diff_data = np.diff(stim_data)
    changes = np.where(np.abs(diff_data) > 0)[0] + 1
    
    if len(changes) == 0:
        return raw.annotations if len(raw.annotations) > 0 else mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = changes / sfreq
    codes = stim_data[changes].astype(int)
    
    valid_mask = np.isin(codes, list(_EVENT_CODE_MAP.keys()))
    onsets = onsets[valid_mask]
    codes = codes[valid_mask]
    descriptions = [_EVENT_CODE_MAP[int(c)] for c in codes]
    
    if len(onsets) == 0:
        return raw.annotations if len(raw.annotations) > 0 else mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(onset=onsets.tolist(), duration=[0.0] * len(onsets), description=descriptions)


def _get_subject_info(row: pd.Series) -> Dict[str, str]:
    subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
    
    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", ""),
            "handedness": info.get("handedness", "unknown"),
        }
    
    return {
        "age": "unknown",
        "sex": "",
        "handedness": "unknown",
    }


def _load_dataset_description(udataset) -> Dict[str, Any]:
    try:
        if hasattr(udataset, 'dataset_path') and os.path.exists(udataset.dataset_path):
            desc_path = os.path.join(udataset.dataset_path, "dataset_description.json")
            if os.path.exists(desc_path):
                with open(desc_path) as f:
                    return json.load(f)
    except Exception:
        pass
    return {}


class DatasetKernel:
    KERNEL_ID = "openneuro_ds004514"
    
    eegunity_description = {
        "age": "unknown",
        "sex": "",
        "handedness": "unknown",
        "amplifier": "BrainAmp MR plus",
        "cap": "32-channel actiCAP",
    }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        desc = _load_dataset_description(udataset)
        
        subject_info = _get_subject_info(row)
        self.eegunity_description.update(subject_info)
        
        if hasattr(udataset, 'dataset_path'):
            self.eegunity_description["dataset_path"] = udataset.dataset_path
        
        self.eegunity_description["amplifier"] = desc.get("EEGReference", self.eegunity_description["amplifier"])
        self.eegunity_description["cap"] = desc.get("CapType", self.eegunity_description["cap"])
        
        raw = _process_channels(raw)
        
        try:
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        
        annotations = _map_events_from_stim_channel(raw)
        if len(annotations) > 0:
            raw.set_annotations(annotations)
        
        return raw
    
    def load_raw(self, udataset, subject_id: Optional[str] = None, session: Optional[str] = None) -> Optional[str]:
        base_path = getattr(udataset, 'dataset_path', None)
        if not base_path:
            return None
        
        subject_prefix = f"sub-{subject_id}" if subject_id else ""
        
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if f.endswith('.edf') or f.endswith('.fif') or f.endswith('.set'):
                    if subject_id and subject_prefix in f:
                        return os.path.join(root, f)
                    elif not subject_id:
                        return os.path.join(root, f)
        
        return None


KERNEL = DatasetKernel()