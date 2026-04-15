"""OpenNeuro DS004584 stage1 kernel for EEGUnity.

Resting-state EEG dataset (Parkinson's Disease Study).
149 participants (100 PD + 49 healthy controls), eyes-open ~2 min.
63-channel EEG, 500 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004584
Paper: DOI 10.21203/rs.3.rs-2666578/v1 (LEAPD cognitive impairment)
Paper: DOI 10.1038/s41531-023-00602-0 (LPC coefficients)
Paper: DOI 10.1038/s41398-025-03506-0 (PD vs HC classification)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Default device metadata (hardcoded based on typical lab equipment for this study)
# Source: Inferred from standard EEG lab setup for Parkinson's research studies
# Annotator: LLM, 2026-04-08
_DEFAULT_AMPLIFIER = "unknown"
_DEFAULT_CAP = "unknown"
_DEFAULT_HANDEDNESS = "unknown"


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load and parse participants.tsv from the BIDS dataset root."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_info(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv."""
    subject_row = None
    for col in ["participant_id", "subject_id", "subject"]:
        if col in participants_df.columns:
            search_id = subject_id
            if not search_id.startswith("sub-"):
                search_id = f"sub-{search_id}"
            matches = participants_df[participants_df[col] == search_id]
            if len(matches) > 0:
                subject_row = matches.iloc[0]
                break

    if subject_row is None:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    age = "unknown"
    for age_col in ["age", "subject_age", "participant_age"]:
        if age_col in participants_df.columns:
            val = subject_row.get(age_col)
            if pd.notna(val):
                try:
                    age = str(int(float(val)))
                except (ValueError, TypeError):
                    age = str(val)
            break

    sex = "unknown"
    for sex_col in ["sex", "gender"]:
        if sex_col in participants_df.columns:
            val = subject_row.get(sex_col)
            if pd.notna(val):
                val_lower = str(val).lower().strip()
                if val_lower in ["m", "male", "man"]:
                    sex = "male"
                elif val_lower in ["f", "female", "woman"]:
                    sex = "female"
            break

    handedness = "unknown"
    for hand_col in ["handedness", "hand"]:
        if hand_col in participants_df.columns:
            val = subject_row.get(hand_col)
            if pd.notna(val):
                val_lower = str(val).lower().strip()
                if "right" in val_lower:
                    handedness = "right"
                elif "left" in val_lower:
                    handedness = "left"
            break

    return {
        "age": age,
        "sex": sex,
        "handedness": handedness,
    }


def _detect_channel_type(channel_name: str) -> Optional[str]:
    """Infer channel type from channel name."""
    name_upper = channel_name.upper()
    
    if any(x in name_upper for x in ["FP", "AF", "F", "FT", "T", "TP", "P", "PO", "O", "C"]):
        if not any(x in name_upper for x in ["EOG", "ECG", "EMG", "TRG", "STIM", "REF"]):
            return "eeg"
    
    if "EOG" in name_upper or "OCULO" in name_upper:
        return "eog"
    
    if "ECG" in name_upper or "CARDIAC" in name_upper:
        return "ecg"
    
    if "EMG" in name_upper:
        return "emg"
    
    if any(x in name_upper for x in ["STIM", "TRIGGER", "RESPONSE", "KEY", "RESP"]):
        return "stim"
    
    return None


def _standardize_channel_name(ch_name: str) -> str:
    """Standardize a channel name to 10-20 system format."""
    name = ch_name.strip()
    name = name.replace("EEG-", "").replace("eeg-", "")
    name = name.replace("EEG ", "").replace("eeg ", "")
    
    standard_mappings = {
        "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
        "AF7": "AF7", "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4", "AF8": "AF8",
        "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "FZ": "Fz", 
        "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
        "FT7": "FT7", "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCZ": "FCz",
        "FC2": "FC2", "FC4": "FC4", "FC6": "FC6", "FT8": "FT8",
        "T7": "T7", "C5": "C5", "C3": "C3", "C1": "C1", "CZ": "Cz",
        "C2": "C2", "C4": "C4", "C6": "C6", "T8": "T8",
        "TP7": "TP7", "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPZ": "CPz",
        "CP2": "CP2", "CP4": "CP4", "CP6": "CP6", "TP8": "TP8",
        "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "PZ": "Pz",
        "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
        "PO7": "PO7", "PO3": "PO3", "POZ": "POz", "PO4": "PO4", "PO8": "PO8",
        "O1": "O1", "OZ": "Oz", "O2": "O2",
        "POO3": "PO3", "POO1": "PO1",
    }
    
    for std_name in standard_mappings.values():
        if name.upper() == std_name.upper():
            return std_name
    
    for alias, standard in standard_mappings.items():
        if name.upper() == alias.upper():
            return standard
    
    return ch_name


def _rename_channels_if_needed(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channels to standard 10-20 names."""
    rename_map = {}
    for ch in raw.ch_names:
        try:
            ch_type = raw.get_channel_types(picks=[ch])[0]
        except Exception:
            continue
        if ch_type != "eeg":
            continue
        
        standardized = _standardize_channel_name(ch)
        if standardized != ch:
            rename_map[ch] = standardized
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard montage if all channels are recognized."""
    try:
        raw.set_montage("standard_1020", on_missing="warn")
    except Exception:
        pass
    return raw


def _get_dataset_root(file_path: str) -> str:
    """Infer dataset root from file path."""
    path = os.path.dirname(file_path)
    max_iterations = 20
    iteration = 0
    while path and path != "/" and iteration < max_iterations:
        if os.path.exists(os.path.join(path, "participants.tsv")):
            return path
        path = os.path.dirname(path)
        iteration += 1
    return os.path.dirname(file_path)


class OpenNeuroDS004584Kernel:
    """Stage1 kernel for OpenNeuro DS004584 (Parkinson's Disease Resting-State EEG)."""

    KERNEL_ID = "openneuro-ds004584-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording."""
        dataset_root = getattr(udataset, 'root', None)
        if dataset_root is None:
            dataset_root = row.get('dataset_root', '/data')
        
        participants_df = _load_participants_tsv(dataset_root)
        
        subject_id = str(row.get('subject_id', row.get('subject', 'unknown')))
        
        subject_info = _extract_subject_info(participants_df, subject_id)
        
        if hasattr(udataset, 'eegunity_description'):
            udataset.eegunity_description = {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEFAULT_AMPLIFIER,
                "cap": _DEFAULT_CAP,
                "handedness": subject_info["handedness"],
            }
        
        raw = _rename_channels_if_needed(raw)
        raw = _set_montage_if_possible(raw)
        
        return raw


KERNEL = OpenNeuroDS004584Kernel()