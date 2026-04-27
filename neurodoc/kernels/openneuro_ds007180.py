"""OpenNeuro DS007180 (Exo-EEG) stage1 kernel for EEGUnity.

Dataset: Exoskeleton-assisted upper and lower limb movement EEG.
Source: https://openneuro.org/datasets/ds007180
Paper: DOI 10.1371/journal.pone.0182578 (upper limb MI/executed movement)
Channels: 63 EEG + 1+ trigger channels
Sampling Rate: 500 Hz

Note on metadata:
- age/sex/handedness not in original data; set to "unknown" (LLM 推断，需人类复核)
- amplifier inferred from dataset documentation as BrainAmp (LLM 推断，需人类复核)
- cap inferred as Ag/AgCl gel-based (LLM 推断，需人类复核)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


_AMPLIFIER = "BrainAmp"
_CAP = "Ag/AgCl"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 64-channel BrainAmp/BrainVision standard cap."""
    standard_64_channels = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO3", "POz", "PO4", "PO8", "PO10",
        "O1", "Oz", "O2",
        "Iz", "AFz", "Fz", "Cz", "Pz", "Oz"
    ]

    eeg_63_standard = [
        "Fp1", "Fpz", "Fp2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "Iz"
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    eeg_num_pattern = re.compile(r"^EEG-?(\d+)$", re.IGNORECASE)
    for ch in existing_names:
        match = eeg_num_pattern.match(ch)
        if match:
            idx = int(match.group(1))
            if idx < len(eeg_63_standard):
                target = eeg_63_standard[idx]
                if target != ch:
                    rename_map[ch] = target

    alias_map = {
        "fp1": "Fp1", "FP1": "Fp1",
        "fp2": "Fp2", "FP2": "Fp2",
        "fpz": "Fpz", "FPz": "Fpz",
        "f7": "F7", "F7": "F7",
        "f3": "F3", "F3": "F3",
        "fz": "Fz", "FZ": "Fz",
        "f4": "F4", "F4": "F4",
        "f8": "F8", "F8": "F8",
        "t7": "T7", "T7": "T7",
        "c3": "C3", "C3": "C3",
        "cz": "Cz", "CZ": "Cz",
        "c4": "C4", "C4": "C4",
        "t8": "T8", "T8": "T8",
        "p7": "P7", "P7": "P7",
        "p3": "P3", "P3": "P3",
        "pz": "Pz", "PZ": "Pz",
        "p4": "P4", "P4": "P4",
        "p8": "P8", "P8": "P8",
        "o1": "O1", "O1": "O1",
        "o2": "O2", "O2": "O2",
        "oz": "Oz", "OZ": "Oz",
    }

    for ch in existing_names:
        if ch in alias_map and ch != alias_map[ch]:
            rename_map[ch] = alias_map[ch]

    return rename_map


def _map_stim_to_annotation(stim_channel: np.ndarray, sfreq: float) -> mne.Annotations:
    """Convert BrainVision STIM channel data to MNE annotations."""
    events_idx = np.where(stim_channel != 0)[0]

    if len(events_idx) == 0:
        return mne.Annotations(onset=[], duration=[], description=[], orig_time=None)

    onsets = events_idx / sfreq
    durations = [0.0] * len(events_idx)
    descriptions = [f"S{int(stim_channel[i])}" for i in events_idx]

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=None
    )


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".vhdr":
        return "brainvision"
    elif ext == ".set":
        return "eeglab"
    elif ext == ".edf":
        return "edf"
    elif ext == ".gdf":
        return "gdf"
    else:
        return "unknown"


class OpenNeuroDS007180Kernel:
    """Stage1 kernel for OpenNeuro DS007180 Exo-EEG dataset."""

    KERNEL_ID: str = "openneuro-ds007180-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording."""
        original_description = raw.info.get("description", "") or ""

        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if existing_renames:
                try:
                    raw.rename_channels(existing_renames)
                except Exception:
                    pass

        stim_channels = [ch for ch in raw.ch_names if "STIM" in ch.upper() or "TRIGGER" in ch.upper()]
        for stim_ch in stim_channels:
            try:
                stim_data = raw.get_data(picks=[stim_ch]).flatten()
                annotations = _map_stim_to_annotation(stim_data, raw.info["sfreq"])
                if len(annotations.onset) > 0:
                    raw.set_annotations(raw.annotations + annotations)
                    break
            except Exception:
                continue

        return raw


KERNEL = OpenNeuroDS007180Kernel()