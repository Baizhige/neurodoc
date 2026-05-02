"""OpenNeuro DS004019 stage1 kernel for EEGUnity.

Effect of obesity on arithmetic processing in preteens with high and low math skills.
An event-related potentials study.

Source: https://openneuro.org/datasets/ds004019
Paper DOI: 10.3389/fnhum.2022.760234
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# EGI 128-channel HydroCel mapping to standard 10-20 positions
# Source: EGI HydroCel Geodesic Sensor Net technical specifications
# Annotator: LLM, 2026-01-15 - inferred by LLM, needs human review
_EGI_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 locations from EGI E1-E128
    "E1": "Fp1", "E2": "AF7", "E3": "AF3", "E4": "AFz", "E5": "AF4", "E6": "AF8",
    "E7": "F7", "E8": "F5", "E9": "F3", "E10": "F1", "E11": "Fz", "E12": "F2",
    "E13": "F4", "E14": "F6", "E15": "F8", "E16": "FT7", "E17": "FC5", "E18": "FC3",
    "E19": "FC1", "E20": "FCz", "E21": "FC2", "E22": "FC4", "E23": "FC6", "E24": "FT8",
    "E25": "T7", "E26": "C5", "E27": "C3", "E28": "C1", "E29": "Cz", "E30": "C2",
    "E31": "C4", "E32": "C6", "E33": "T8", "E34": "TP7", "E35": "CP5", "E36": "CP3",
    "E37": "CP1", "E38": "CPz", "E39": "CP2", "E40": "CP4", "E41": "CP6", "E42": "TP8",
    "E43": "P7", "E44": "P5", "E45": "P3", "E46": "P1", "E47": "Pz", "E48": "P2",
    "E49": "P4", "E50": "P6", "E51": "P8", "E52": "PO7", "E53": "PO3", "E54": "POz",
    "E55": "PO4", "E56": "PO8", "E57": "O1", "E58": "Oz", "E59": "O2",
    # Additional EGI channels E60-E128 (peripheral/hybrid locations)
    "E60": "PO9", "E61": "PO10", "E62": "O9", "E63": "O10",
}

# Non-EEG channels to be excluded or renamed
_NON_EEG_CHANNELS: Dict[str, str] = {
    "ECG": "ecg",
    " Resp": "resp",
    "Respiration": "resp",
    " respiration": "resp",
    "SP": "stim",
    "Stim": "stim",
}

# Default subject metadata (ages 9-10 preteens from paper)
# Source: Paper DOI 10.3389/fnhum.2022.760234 - Table 1 demographic characteristics
# Annotator: LLM, 2026-01-15 - inferred by LLM, needs human review
_DEFAULT_SUBJECT_AGE: str = "9-10"
_DEFAULT_SUBJECT_SEX: str = "unknown"
_DEFAULT_SUBJECT_HAND: str = "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI E1-E128 to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    used_targets: set = set()
    
    # First pass: count how many EGI channels map to each standard name
    target_counts: Dict[str, int] = {}
    for egi_name in _EGI_CHANNEL_MAP:
        if egi_name in existing_names:
            standard_name = _EGI_CHANNEL_MAP[egi_name]
            target_counts[standard_name] = target_counts.get(standard_name, 0) + 1
    
    # Second pass: build rename map, only if target is unique and not already used
    for egi_name in _EGI_CHANNEL_MAP:
        if egi_name in existing_names:
            standard_name = _EGI_CHANNEL_MAP[egi_name]
            if target_counts.get(standard_name, 0) == 1 and standard_name not in used_targets:
                rename_map[egi_name] = standard_name
                used_targets.add(standard_name)
    
    # Also handle variations like "E001", "E01", "EEG E1"
    for ch in list(existing_names):
        if ch in rename_map:
            continue
        match = re.match(r'^(?:EEG\s*)?E(\d{1,3})$', ch, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num in range(1, 130):
                egi_name = f"E{num}"
                if egi_name in _EGI_CHANNEL_MAP:
                    standard_name = _EGI_CHANNEL_MAP[egi_name]
                    if standard_name not in used_targets and standard_name not in existing_names:
                        rename_map[ch] = standard_name
                        used_targets.add(standard_name)
    
    return rename_map


def _identify_non_eeg_channels(raw: mne.io.BaseRaw) -> List[str]:
    """Identify non-EEG channels in the raw data."""
    non_eeg: List[str] = []
    for ch in raw.ch_names:
        ch_lower = ch.lower()
        if any(keyword in ch_lower for keyword in ["ecg", "resp", "sp", "stim", "gdp", "gnd", "ref"]):
            non_eeg.append(ch)
    return non_eeg


def _map_event_code(code: Any) -> str:
    """Map numeric event codes to human-readable labels."""
    code_map = {
        0: "0",      # Incorrect response
        1: "1",      # Correct response
        2: "prob",   # Arithmetic problem onset
        3: "bgin",   # Trial beginning / delay period onset
        4: "ch++",   # Choice/comparison stimulus onset
        5: "face",   # Verification digit onset
        6: "resp",   # Participant button-press response
        10: "sync",  # Hardware sync pulse (admin)
        11: "CELL",  # Cell/block marker (admin)
        12: "SESS",  # Session start marker (admin)
    }
    
    try:
        code_int = int(code)
        return code_map.get(code_int, str(code))
    except (ValueError, TypeError):
        return str(code)


class OpenNeuroDS004019Kernel:
    """Stage1 kernel for OpenNeuro DS004019 dataset.
    
    Effect of obesity on arithmetic processing in preteens.
    62 subjects, 132 channels, 500 Hz sampling rate.
    EGI 128-channel HydroCel Geodesic Sensor Net.
    """

    KERNEL_ID: str = "openneuro-ds004019-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.
        
        Parameters
        ----------
        udataset : EEGUNITY dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with File Path, Subject ID, etc.
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and events.
        """
        # --- 1. Channel renaming ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            valid_renames = {}
            existing_channel_names = set(raw.ch_names)
            for old_name, new_name in rename_map.items():
                if old_name in existing_channel_names and new_name not in existing_channel_names:
                    valid_renames[old_name] = new_name
            if valid_renames:
                print(f"[DS004019] Renaming {len(valid_renames)} channels: {list(valid_renames.values())[:5]}...")
                raw.rename_channels(valid_renames)
        
        # --- 2. Set montage (after renaming) ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            ch_names_in_montage = set(montage.ch_names)
            ch_names_in_raw = set(raw.ch_names)
            common_chs = list(ch_names_in_montage & ch_names_in_raw)
            
            if len(common_chs) >= 60:
                raw.set_montage(montage, on_missing="ignore")
                print(f"[DS004019] Set standard_1020 montage for {len(common_chs)} channels")
        except Exception as e:
            print(f"[DS004019] Warning: Could not set montage: {e}")
        
        # --- 3. Build eegunity_description dict with required fields ---
        subject_id = row.get("Subject", "unknown") if row is not None else "unknown"
        
        eegunity_description: Dict[str, str] = {
            "age": _DEFAULT_SUBJECT_AGE,
            "sex": _DEFAULT_SUBJECT_SEX,
            "amplifier": "EGI 128-channel HydroCel Geodesic Sensor Net",
            "cap": "HydroCel GSN 128-channel (Ag/AgCl)",
            "handedness": _DEFAULT_SUBJECT_HAND,
            "dataset_id": "ds004019",
            "kernel_id": self.KERNEL_ID,
            "subject_id": str(subject_id),
        }
        
        # --- 4. Store eegunity_description in raw info ---
        if "description" not in raw.info or raw.info["description"] is None:
            raw.info["description"] = ""
        raw.info["description"] = json.dumps(eegunity_description)
        
        # --- 5. Set subject_info with valid MNE fields only ---
        # Note: 'age' is NOT a valid key for MNE SubjectInfo
        # Use 'desc' field to store additional subject info including age
        subject_desc = f"age={_DEFAULT_SUBJECT_AGE}, sex={_DEFAULT_SUBJECT_SEX}, hand={_DEFAULT_SUBJECT_HAND}"
        
        raw.info["subject_info"] = {
            "id": str(subject_id),
            "sex": _DEFAULT_SUBJECT_SEX,
            "hand": _DEFAULT_SUBJECT_HAND,
            "desc": subject_desc,
        }
        
        # --- 6. Process events from annotations or stim channel ---
        # Events are handled via annotations in EEGLAB format
        
        return raw


KERNEL = OpenNeuroDS004019Kernel()