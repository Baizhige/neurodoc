"""OpenNeuro DS004817 stage1 kernel for EEGUnity.

Dataset: EEG-attention-rsvp-exp2 (RSVP Experiment 2)
Source: https://openneuro.org/datasets/ds004817
Reference: https://doi.org/10.51628/001c.21174

Paradigm: Rapid Serial Visual Presentation (RSVP) task investigating
neural dynamics of prioritizing task-relevant information.

Events: E 1, E 2, E 3, Event/E 1, Event/E 2, Event/E 3
- E 1 / Event/E 1: Task-relevant (attended) stimulus
- E 2 / Event/E 2: Task-irrelevant (unattended) stimulus
- E 3 / Event/E 3: Additional stimulus type

Notes: This dataset follows BIDS format. Age/sex from participants.tsv
are marked as missing in the analysis. Channel names are standard 10-20.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


_STANDARD_63_CHANNEL_MAP = {
    "Fp1": "EEG-Fp1",
    "Fpz": "EEG-Fpz",
    "Fp2": "EEG-Fp2",
    "F7": "EEG-F7",
    "F3": "EEG-F3",
    "Fz": "EEG-Fz",
    "F4": "EEG-F4",
    "F8": "EEG-F8",
    "FC5": "EEG-FC5",
    "FC3": "EEG-FC3",
    "FC1": "EEG-FC1",
    "FCz": "EEG-FCz",
    "FC2": "EEG-FC2",
    "FC4": "EEG-FC4",
    "FC6": "EEG-FC6",
    "T7": "EEG-T7",
    "C5": "EEG-C5",
    "C3": "EEG-C3",
    "C1": "EEG-C1",
    "Cz": "EEG-Cz",
    "C2": "EEG-C2",
    "C4": "EEG-C4",
    "C6": "EEG-C6",
    "T8": "EEG-T8",
    "CP5": "EEG-CP5",
    "CP3": "EEG-CP3",
    "CP1": "EEG-CP1",
    "CPz": "EEG-CPz",
    "CP2": "EEG-CP2",
    "CP4": "EEG-CP4",
    "CP6": "EEG-CP6",
    "P7": "EEG-P7",
    "P5": "EEG-P5",
    "P3": "EEG-P3",
    "P1": "EEG-P1",
    "Pz": "EEG-Pz",
    "P2": "EEG-P2",
    "P4": "EEG-P4",
    "P6": "EEG-P6",
    "P8": "EEG-P8",
    "PO7": "EEG-PO7",
    "PO3": "EEG-PO3",
    "POz": "EEG-POz",
    "PO4": "EEG-PO4",
    "PO8": "EEG-PO8",
    "O1": "EEG-O1",
    "Oz": "EEG-Oz",
    "O2": "EEG-O2",
    "AF7": "EEG-AF7",
    "AF3": "EEG-AF3",
    "AFz": "EEG-AFz",
    "AF4": "EEG-AF4",
    "AF8": "EEG-AF8",
    "FT7": "EEG-FT7",
    "FT8": "EEG-FT8",
    "TP7": "EEG-TP7",
    "TP8": "EEG-TP8",
    "PO9": "EEG-PO9",
    "PO10": "EEG-PO10",
    "O9": "EEG-O9",
    "O10": "EEG-O10",
}

_NUMERIC_PATTERN = re.compile(r"EEG-(\d+)")


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for standard 10-20 channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    standard_1020 = {
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "FT7", "FT8", "TP7", "TP8",
        "PO9", "PO10", "O9", "O10",
    }
    
    for ch_name in existing_names:
        if ch_name in standard_1020:
            rename_map[ch_name] = f"EEG-{ch_name}"
    
    return rename_map


def _load_subject_info(row) -> Dict[str, Any]:
    """Load subject information from BIDS participants.tsv if available."""
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _detect_paradigm(row) -> str:
    """Detect paradigm from file path."""
    return "RSVP"


def _map_event_description(desc: str) -> str:
    """Map raw event descriptions to canonical RSVP labels."""
    desc = str(desc).strip()
    
    if desc.startswith("Event/E "):
        parts = desc.split("/")
        if len(parts) > 1:
            desc = "E " + parts[-1].split()[-1]
    
    desc = re.sub(r"\s+", " ", desc)
    
    return desc


@dataclass
class OpenNeuroDS004817Kernel:
    """Stage1 kernel for OpenNeuro DS004817 (RSVP EEG dataset)."""

    KERNEL_ID: str = "openneuro-ds004817-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single RSVP EEG record."""

        # --- 1. Channel Rename (before set_montage) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_renames = {k: v for k, v in rename_map.items() 
                               if k in raw.ch_names}
            if existing_renames:
                print(f"[DS004817] Renaming {len(existing_renames)} channels")
                raw.rename_channels(existing_renames)

        # --- 2. Set Montage (standard 10-20) ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[DS004817] Warning: Could not set montage: {e}")

        # --- 3. Load Subject Info ---
        subject_info = _load_subject_info(row)
        paradigm = _detect_paradigm(row)

        # --- 4. Handle Events ---
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            new_event_id = {}
            for desc, eid in event_id.items():
                mapped_desc = _map_event_description(desc)
                new_event_id[mapped_desc] = eid
        except Exception as e:
            print(f"[DS004817] Warning: Could not read events: {e}")
            events = np.array([]).reshape(0, 3)
            event_id = {}
            new_event_id = {}

        # --- 5. Update Annotations with Mapped Events ---
        if len(events) > 0:
            orig_annotations = raw.annotations
            
            mapped_descriptions = []
            for desc in orig_annotations.description:
                mapped_descriptions.append(_map_event_description(desc))
            
            new_annotations = mne.Annotations(
                onset=orig_annotations.onset,
                duration=orig_annotations.duration,
                description=mapped_descriptions,
                orig_time=orig_annotations.orig_time,
            )
            raw.set_annotations(new_annotations)

        # --- 6. Build Description JSON ---
        original_desc = raw.info.get("description", "")
        if not original_desc:
            original_desc = ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": str(subject_info.get("age", "unknown")),
                "sex": str(subject_info.get("sex", "unknown")),
                "handedness": str(subject_info.get("handedness", "unknown")),
                "amplifier": "unknown",
                "cap": "unknown",
            },
        }
        
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004817Kernel()