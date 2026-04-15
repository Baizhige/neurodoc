"""OpenNeuro DS004661 stage1 kernel for EEGUnity.

Dataset: ANDI - Auditory N-back Dual-task EEG
Source: https://doi.org/10.18112/openneuro.ds004661.v1.1.0

Event structure:
- Code 10: Non-target trial (dominant condition, ~29820 events)
- Code 11: N-back target match (minority condition, ~2948 events)

Binary classification with ~10:1 class imbalance.
Sampling rate: 128 Hz (limited spectral resolution).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np


# =============================================================================
# Channel Rename Map (64-channel standard 10-20 system)
# =============================================================================
# Source: Standard 10-20 electrode placement system, 64-channel layout
# Annotator: LLM, 2026-04-08 (inferred from standard 64-channel cap naming)
# Note: Actual channel names may vary; map includes common aliases.
# LLM 推断，需人类复核
_EEG_CHANNEL_MAP: Dict[str, list] = {
    "Fp1": ["Fp1", "EEG-Fp1"],
    "Fp2": ["Fp2", "EEG-Fp2"],
    "Fpz": ["Fpz", "EEG-Fpz"],
    "F7": ["F7", "EEG-F7"],
    "F3": ["F3", "EEG-F3"],
    "Fz": ["Fz", "EEG-Fz"],
    "F4": ["F4", "EEG-F4"],
    "F8": ["F8", "EEG-F8"],
    "T7": ["T7", "EEG-T7", "T3"],
    "C3": ["C3", "EEG-C3"],
    "Cz": ["Cz", "EEG-Cz"],
    "C4": ["C4", "EEG-C4"],
    "T8": ["T8", "EEG-T8", "T4"],
    "P7": ["P7", "EEG-P7", "T5"],
    "P3": ["P3", "EEG-P3"],
    "Pz": ["Pz", "EEG-Pz"],
    "P4": ["P4", "EEG-P4"],
    "P8": ["P8", "EEG-P8", "T6"],
    "O1": ["O1", "EEG-O1"],
    "Oz": ["Oz", "EEG-Oz"],
    "O2": ["O2", "EEG-O2"],
    "FC5": ["FC5", "EEG-FC5"],
    "FC3": ["FC3", "EEG-FC3"],
    "FC1": ["FC1", "EEG-FC1"],
    "FCz": ["FCz", "EEG-FCz"],
    "FC2": ["FC2", "EEG-FC2"],
    "FC4": ["FC4", "EEG-FC4"],
    "FC6": ["FC6", "EEG-FC6"],
    "CP5": ["CP5", "EEG-CP5"],
    "CP3": ["CP3", "EEG-CP3"],
    "CP1": ["CP1", "EEG-CP1"],
    "CPz": ["CPz", "EEG-CPz"],
    "CP2": ["CP2", "EEG-CP2"],
    "CP4": ["CP4", "EEG-CP4"],
    "CP6": ["CP6", "EEG-CP6"],
    "AF3": ["AF3", "EEG-AF3"],
    "AF4": ["AF4", "EEG-AF4"],
    "F5": ["F5", "EEG-F5"],
    "F1": ["F1", "EEG-F1"],
    "F2": ["F2", "EEG-F2"],
    "F6": ["F6", "EEG-F6"],
    "C5": ["C5", "EEG-C5"],
    "C1": ["C1", "EEG-C1"],
    "C2": ["C2", "EEG-C2"],
    "C6": ["C6", "EEG-C6"],
    "P5": ["P5", "EEG-P5"],
    "P1": ["P1", "EEG-P1"],
    "P2": ["P2", "EEG-P2"],
    "P6": ["P6", "EEG-P6"],
    "AF7": ["AF7", "EEG-AF7"],
    "AF8": ["AF8", "EEG-AF8"],
    "FT7": ["FT7", "EEG-FT7"],
    "FT8": ["FT8", "EEG-FT8"],
    "TP7": ["TP7", "EEG-TP7"],
    "TP8": ["TP8", "EEG-TP8"],
    "PO7": ["PO7", "EEG-PO7"],
    "PO8": ["PO8", "EEG-PO8"],
    "AFz": ["AFz", "EEG-AFz"],
    "POz": ["POz", "EEG-POz"],
    "FT9": ["FT9", "EEG-FT9"],
    "FT10": ["FT10", "EEG-FT10"],
    "TP9": ["TP9", "EEG-TP9"],
    "TP10": ["TP10", "EEG-TP10"],
    "PO9": ["PO9", "EEG-PO9"],
    "PO10": ["PO10", "EEG-PO10"],
    "PO3": ["PO3", "EEG-PO3"],
    "PO4": ["PO4", "EEG-PO4"],
    "Fpz": ["Fpz", "EEG-Fpz"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for standard 10-20 electrode names.
    
    Source: Standard 10-20 system, 64-channel extended montage
    Annotator: LLM, 2026-04-08
    LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in _EEG_CHANNEL_MAP.items():
        for alias in aliases:
            if alias in existing_names and alias != target_name:
                rename_map[alias] = target_name
                break
    
    return rename_map


def _load_participants_tsv(dataset_path: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """Load subject metadata from BIDS participants.tsv.
    
    Source: OpenNeuro BIDS structure
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_file):
        return None
    
    import pandas as pd
    try:
        df = pd.read_csv(participants_file, sep="\t")
        subject_dict: Dict[str, Dict[str, Any]] = {}
        
        for _, row in df.iterrows():
            subj_id = str(row.get("participant_id", ""))
            if not subj_id:
                continue
            
            # Normalize subject ID (remove 'sub-' prefix if present)
            subj_id = subj_id.replace("sub-", "")
            
            age = str(row.get("age", "unknown"))
            sex = str(row.get("sex", row.get("gender", "unknown"))).lower()
            
            # Normalize sex values
            if sex in ["m", "male", "man"]:
                sex = "male"
            elif sex in ["f", "female", "woman"]:
                sex = "female"
            else:
                sex = "unknown"
            
            subject_dict[subj_id] = {
                "age": age,
                "sex": sex,
            }
        
        return subject_dict
    except Exception:
        return None


# =============================================================================
# Event Mapping
# =============================================================================
_EVENT_CODE_MAP: Dict[int, str] = {
    10: "non-target",
    11: "target",
}


def _map_events_to_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Map numeric event codes to human-readable annotation labels.
    
    Source: OpenNeuro dataset metadata, analysis.md event structure
    Event codes: 10 = non-target, 11 = target (N-back task)
    """
    events, event_id = mne.events_from_annotations(raw)
    
    # Create reverse mapping from event ID to annotation description
    id_to_desc = {v: k for k, v in event_id.items()}
    
    # Map to canonical event labels
    canonical_map: Dict[str, str] = {}
    for orig_desc, orig_id in event_id.items():
        # Try to convert description to int
        try:
            code = int(orig_desc)
            if code in _EVENT_CODE_MAP:
                canonical_map[orig_desc] = _EVENT_CODE_MAP[code]
            else:
                canonical_map[orig_desc] = orig_desc
        except (ValueError, TypeError):
            canonical_map[orig_desc] = orig_desc
    
    # Build new annotations with canonical labels
    new_onsets = []
    new_durations = []
    new_descriptions = []
    
    for i, event in enumerate(events):
        code = event[2]
        desc = canonical_map.get(str(code), str(code))
        new_onsets.append(event[0] / raw.info["sfreq"])
        new_durations.append(0.0)
        new_descriptions.append(desc)
    
    if new_onsets:
        annotations = mne.Annotations(
            onset=new_onsets,
            duration=new_durations,
            description=new_descriptions,
        )
        raw.set_annotations(annotations)
    
    return raw


class OpenNeuroDS004661Kernel:
    """Stage1 kernel for OpenNeuro DS004661 (ANDI dataset).
    
    Dataset: ANDI - Auditory N-back Dual-task EEG
    Source: https://doi.org/10.18112/openneuro.ds004661.v1.1.0
    Reference: Ries, et al., 2016
    
    Task: Binary classification (target vs non-target N-back trials)
    Events: Code 10 (non-target), Code 11 (target)
    Class imbalance: ~10:1 (29820 vs 2948 events)
    """
    
    KERNEL_ID: str = "openneuro-ds004661-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to DS004661 recording.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object for the recording.
        row
            Locator row with file path and subject info.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata.
        """
        # Get dataset path from locator row
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(os.path.dirname(file_path)) if file_path else ""
        
        # -------------------------------------------------------------------------
        # 1. Extract Subject Metadata
        # -------------------------------------------------------------------------
        subject_id = str(row.get("Subject", row.get("participant_id", "unknown")))
        subject_id = subject_id.replace("sub-", "")
        
        # Load participants.tsv for subject metadata
        subject_dict = _load_participants_tsv(dataset_path)
        if subject_dict and subject_id in subject_dict:
            age = subject_dict[subject_id]["age"]
            sex = subject_dict[subject_id]["sex"]
        else:
            # LLM 推断，需人类复核
            age = "unknown"
            sex = "unknown"
        
        # -------------------------------------------------------------------------
        # 2. Channel Rename (BEFORE set_montage)
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # -------------------------------------------------------------------------
        # 3. Set Montage (Standard 10-20 system)
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if standard montage fails
        
        # -------------------------------------------------------------------------
        # 4. Device Metadata (from OpenNeuro metadata)
        # -------------------------------------------------------------------------
        # Source: OpenNeuro dataset_description.json / Ries et al., 2016
        # Annotator: LLM, 2026-04-08
        # LLM 推断，需人类复核
        amplifier = "unknown"
        cap = "unknown"
        handedness = "unknown"
        
        # Try to read from dataset_description.json
        if dataset_path:
            desc_file = os.path.join(dataset_path, "dataset_description.json")
            if os.path.exists(desc_file):
                try:
                    with open(desc_file) as f:
                        desc_data = json.load(f)
                    # Extract any available EEG reference info
                    eeg_ref = desc_data.get("EEGReference", "")
                    if eeg_ref:
                        amplifier = eeg_ref
                except Exception:
                    pass
        
        # -------------------------------------------------------------------------
        # 5. Map Events to Annotations
        # -------------------------------------------------------------------------
        raw = _map_events_to_annotations(raw)
        
        # -------------------------------------------------------------------------
        # 6. Write eegunity_description
        # -------------------------------------------------------------------------
        original_description = raw.info.get("description", "")
        if isinstance(original_description, dict):
            original_description = json.dumps(original_description)
        
        description_dict = {
            "original_description": str(original_description) if original_description else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004661Kernel()