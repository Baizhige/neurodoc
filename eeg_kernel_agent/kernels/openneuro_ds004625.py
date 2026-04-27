"""OpenNeuro ds004625 stage1 kernel for EEGUnity.

Dataset: Mind in Motion: Young Adults Walking Over Uneven Terrain
Source: https://openneuro.org/datasets/ds004625
284-channel high-density EEG, 500 Hz, 32 subjects.
Paradigm: Locomotor control during uneven terrain walking.

This kernel extends the generic BIDS kernel with dataset-specific
channel renaming, events.tsv annotation loading, and hardcoded
amplifier metadata derived from the accompanying reference papers.

Required info fields from participants.tsv: age, gender, handedness, speed
Required event IDs: LHS, LTO, RHS, RTO, TrialEnd, TrialStart

Annotator: LLM (gpt-4o), 2025-01-15
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants derived from dataset documentation / reference papers
# ---------------------------------------------------------------------------
# Source: 10.1162/imag.a.1039, 10.3390/s23020928 — BioSemi ActiveTwo used
# Annotator: LLM, 2025-01-15
_AMPLIFIER: str = "BioSemi ActiveTwo"
# Source: BioSemi 256+ channel cap with Ag/AgCl active electrodes
# Annotator: LLM, 2025-01-15
_CAP: str = "BioSemi 256-channel Ag/AgCl"

# ---------------------------------------------------------------------------
# High-density channel naming — BioSemi 256-channel naming convention
# ---------------------------------------------------------------------------
# Source: BioSemi 256-channel cap layout documentation
# Annotator: LLM, 2025-01-15 — 由 LLM 推断，需人类复核
_BIOSEMI_256_MAP: Dict[str, str] = {
    # Standard 10-20
    "Fp1": "Fp1", "Fpz": "Fpz", "Fp2": "Fp2",
    "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "Fz": "Fz",
    "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
    "FT7": "FT7", "FT8": "FT8",
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCz": "FCz",
    "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    "T7": "T7", "C5": "C5", "C3": "C3", "C1": "C1", "Cz": "Cz",
    "C2": "C2", "C4": "C4", "C6": "C6", "T8": "T8",
    "TP7": "TP7", "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPz": "CPz",
    "CP2": "CP2", "CP4": "CP4", "CP6": "CP6", "TP8": "TP8",
    "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "Pz": "Pz",
    "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
    "PO7": "PO7", "PO3": "PO3", "POz": "POz", "PO4": "PO4", "PO8": "PO8",
    "O1": "O1", "Oz": "Oz", "O2": "O2",
    "Iz": "Iz",
    # Extended 10-10 / BioSemi 256
    "Fp1h": "Fp1h", "Fp2h": "Fp2h",
    "AFp1": "AFp1", "AFp2": "AFp2",
    "AFF1": "AFF1", "AFF2": "AFF2", "AFF5h": "AFF5h", "AFF6h": "AFF6h",
    "F7h": "F7h", "F5h": "F5h", "F3h": "F3h", "F1h": "F1h",
    "F2h": "F2h", "F4h": "F4h", "F6h": "F6h", "F8h": "F8h",
    "FFT7h": "FFT7h", "FFC5h": "FFC5h", "FFC3h": "FFC3h", "FFC1h": "FFC1h",
    "FFC2h": "FFC2h", "FFC4h": "FFC4h", "FFC6h": "FFC6h", "FFT8h": "FFT8h",
    "FT7h": "FT7h", "FC5h": "FC5h", "FC3h": "FC3h", "FC1h": "FC1h",
    "FC2h": "FC2h", "FC4h": "FC4h", "FC6h": "FC6h", "FT8h": "FT8h",
    "FTT7h": "FTT7h", "FCC5h": "FCC5h", "FCC3h": "FCC3h", "FCC1h": "FCC1h",
    "FCC2h": "FCC2h", "FCC4h": "FCC4h", "FCC6h": "FCC6h", "FTT8h": "FTT8h",
    "T7h": "T7h", "C5h": "C5h", "C3h": "C3h", "C1h": "C1h",
    "C2h": "C2h", "C4h": "C4h", "C6h": "C6h", "T8h": "T8h",
    "TTP7h": "TTP7h", "CCP5h": "CCP5h", "CCP3h": "CCP3h", "CCP1h": "CCP1h",
    "CCP2h": "CCP2h", "CCP4h": "CCP4h", "CCP6h": "CCP6h", "TTP8h": "TTP8h",
    "TP7h": "TP7h", "CP5h": "CP5h", "CP3h": "CP3h", "CP1h": "CP1h",
    "CP2h": "CP2h", "CP4h": "CP4h", "CP6h": "CP6h", "TP8h": "TP8h",
    "TPP7h": "TPP7h", "CPP5h": "CPP5h", "CPP3h": "CPP3h", "CPP1h": "CPP1h",
    "CPP2h": "CPP2h", "CPP4h": "CPP4h", "CPP6h": "CPP6h", "TPP8h": "TPP8h",
    "P7h": "P7h", "P5h": "P5h", "P3h": "P3h", "P1h": "P1h",
    "P2h": "P2h", "P4h": "P4h", "P6h": "P6h", "P8h": "P8h",
    "PPO7h": "PPO7h", "PPO3h": "PPO3h", "PPO1h": "PPO1h", "PPO2h": "PPO2h",
    "PPO4h": "PPO4h", "PPO6h": "PPO6h", "PPO8h": "PPO8h",
    "PO7h": "PO7h", "PO5h": "PO5h", "PO3h": "PO3h", "PO1": "PO1",
    "PO2": "PO2", "PO4h": "PO4h", "PO6h": "PO6h", "PO8h": "PO8h",
    "POO9h": "POO9h", "POO3h": "POO3h", "POO4h": "POO4h", "POO10h": "POO10h",
    "O1h": "O1h", "O2h": "O2h",
    "OI1h": "OI1h", "OI2h": "OI2h",
    "I1": "I1", "I2": "I2",
    # Additional BioSemi 256 channels
    "A1": "A1", "A2": "A2", "A3": "A3", "A4": "A4", "A5": "A5",
    "A6": "A6", "A7": "A7", "A8": "A8", "A9": "A9", "A10": "A10",
    "A11": "A11", "A12": "A12", "A13": "A13", "A14": "A14", "A15": "A15",
    "A16": "A16", "A17": "A17", "A18": "A18", "A19": "A19", "A20": "A20",
    "A21": "A21", "A22": "A22", "A23": "A23", "A24": "A24", "A25": "A25",
    "A26": "A26", "A27": "A27", "A28": "A28", "A29": "A29", "A30": "A30",
    "A31": "A31", "A32": "A32",
    "B1": "B1", "B2": "B2", "B3": "B3", "B4": "B4", "B5": "B5",
    "B6": "B6", "B7": "B7", "B8": "B8", "B9": "B9", "B10": "B10",
    "B11": "B11", "B12": "B12", "B13": "B13", "B14": "B14", "B15": "B15",
    "B16": "B16", "B17": "B17", "B18": "B18", "B19": "B19", "B20": "B20",
    "B21": "B21", "B22": "B22", "B23": "B23", "B24": "B24", "B25": "B25",
    "B26": "B26", "B27": "B27", "B28": "B28", "B29": "B29", "B30": "B30",
    "B31": "B31", "B32": "B32",
    "EXG1": "EXG1", "EXG2": "EXG2", "EXG3": "EXG3", "EXG4": "EXG4",
    "EXG5": "EXG5", "EXG6": "EXG6", "EXG7": "EXG7", "EXG8": "EXG8",
    "GSR1": "GSR1", "GSR2": "GSR2",
    "Erg1": "Erg1", "Erg2": "Erg2",
    "Resp": "Resp", "Plet": "Plet", "Temp": "Temp",
    # Common aliases
    "EXG1": "EXG1", "EXG2": "EXG2", "EXG3": "EXG3", "EXG4": "EXG4",
    "EXG5": "EXG5", "EXG6": "EXG6", "EXG7": "EXG7", "EXG8": "EXG8",
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    used_targets: set = set()

    # First pass: exact matches in our map
    for src, dst in _BIOSEMI_256_MAP.items():
        if src in existing and dst not in used_targets:
            rename_map[src] = dst
            used_targets.add(dst)

    # Handle common BioSemi prefix patterns (A1-A32, B1-B32, etc.)
    for ch in raw.ch_names:
        if ch in rename_map:
            continue
        # Direct match with case variations
        ch_upper = ch.upper()
        for src, dst in _BIOSEMI_256_MAP.items():
            if ch_upper == src.upper() and dst not in used_targets:
                rename_map[ch] = dst
                used_targets.add(dst)
                break

    # Keep EXG channels as-is for EMG/EOG
    for ch in raw.ch_names:
        if ch not in rename_map:
            if ch.startswith(("EXG", "AUX", "GSR", "Erg", "Resp", "Plet", "Temp")):
                rename_map[ch] = ch

    return rename_map


def _set_montage_safe(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard_1020 montage on raw, skipping unavailable channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        # Only use channels that exist in both raw and montage
        montage_chs = set(montage.ch_names)
        raw_chs = set(raw.ch_names)
        common_chs = list(montage_chs & raw_chs)
        if common_chs:
            montage_subset = montage.copy()
            # Pick only common channels
            picks = [i for i, ch in enumerate(montage.ch_names) if ch in common_chs]
            if hasattr(montage_subset, 'pick_channels'):
                montage_subset.pick_channels(common_chs)
            raw.set_montage(montage_subset, on_missing="ignore")
    except Exception:
        pass
    return raw


def _load_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load participant info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id (e.g., "sub-01" or "01")
        sub_col = "participant_id"
        if sub_col not in df.columns:
            return {}
        # Normalize subject_id format
        if not subject_id.startswith("sub-"):
            search_id = f"sub-{subject_id}"
        else:
            search_id = subject_id
        row = df[df[sub_col] == search_id]
        if row.empty:
            # Try without prefix
            row = df[df[sub_col] == subject_id.replace("sub-", "")]
        if row.empty:
            return {}
        return {col: str(row.iloc[0][col]) for col in df.columns}
    except Exception:
        return {}


def _load_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Load events from events.tsv file."""
    if not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _add_misc_channels(raw: mne.io.BaseRaw, info_dict: Dict[str, str], required_fields: List[str]) -> mne.io.BaseRaw:
    """Add misc channels for participants.tsv derived fields."""
    # Determine which fields to add as misc channels (exclude basic metadata)
    basic_fields = {"participant_id", "age", "gender", "handedness", "sex", "handedness"}
    misc_fields = [f for f in required_fields if f not in basic_fields and f in info_dict]
    
    if not misc_fields:
        return raw
    
    # Create misc channel data
    sfreq = raw.info["sfreq"]
    n_times = len(raw.times)
    new_data = []
    new_ch_names = []
    new_ch_types = []
    
    for field in misc_fields:
        # Broadcast constant value
        value = info_dict[field]
        # Try to convert to float, otherwise use 0.0
        try:
            float_val = float(value)
        except (ValueError, TypeError):
            float_val = 0.0
        ch_data = np.full((1, n_times), float_val)
        new_data.append(ch_data)
        new_ch_names.append(field)
        new_ch_types.append("misc")
    
    if not new_data:
        return raw
    
    # Create new info and RawArray
    new_info = mne.create_info(ch_names=new_ch_names, sfreq=sfreq, ch_types=new_ch_types)
    new_raw = mne.io.RawArray(np.concatenate(new_data, axis=0), new_info)
    
    # Add to existing raw
    raw.add_channels([new_raw], force_update_info=True)
    return raw


class OpenNeuroDS004625Kernel:
    KERNEL_ID = "openneuro_ds004625"
    DATASET_NAME = "ds004625"
    REQUIRED_INFO_FIELDS = ["age", "gender", "handedness", "speed"]
    DERIVED_MISC_CHANNELS = ["speed"]
    EVENT_IDS = ["LHS", "LTO", "RHS", "RTO", "TrialEnd", "TrialStart"]

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get dataset path and subject info
        dataset_path = getattr(udataset, "dataset_path", str(udataset))
        subject_id = str(row.get("subject", row.get("participant_id", "")))
        
        # Load participants info
        participants_info = _load_participants_info(dataset_path, subject_id)
        
        # Build and apply channel rename map
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known channels
        eeg_picks = [ch for ch in raw.ch_names if ch in _BIOSEMI_256_MAP and not ch.startswith(("EXG", "AUX", "GSR", "Erg", "Resp", "Plet", "Temp"))]
        misc_picks = [ch for ch in raw.ch_names if ch.startswith(("EXG", "AUX", "GSR", "Erg", "Resp", "Plet", "Temp"))]
        
        if eeg_picks:
            raw.set_channel_types({ch: "eeg" for ch in eeg_picks})
        if misc_picks:
            raw.set_channel_types({ch: "misc" for ch in misc_picks})
        
        # Set montage safely
        raw = _set_montage_safe(raw)
        
        # Load events from events.tsv
        # Determine events file path from row or construct from BIDS layout
        events_path = None
        if "path" in row:
            # Replace _eeg.* with _events.tsv
            eeg_path = str(row["path"])
            events_path = re.sub(r"_eeg\.[^.]+$", "_events.tsv", eeg_path)
            if events_path == eeg_path:
                # Try alternative: same directory, events.tsv
                base = os.path.splitext(eeg_path)[0]
                events_path = base.replace("_eeg", "_events") + ".tsv"
                if not os.path.exists(events_path):
                    events_path = os.path.join(os.path.dirname(eeg_path), "events.tsv")
        else:
            # Construct from dataset path
            sub_clean = subject_id.replace("sub-", "")
            events_path = os.path.join(dataset_path, f"sub-{sub_clean}", "eeg", f"sub-{sub_clean}_task-walk_events.tsv")
        
        # Load and apply events
        events_df = _load_events_tsv(events_path) if events_path and os.path.exists(events_path) else None
        
        if events_df is not None and not events_df.empty:
            # Check required columns
            onset_col = "onset" if "onset" in events_df.columns else "sample"
            duration_col = "duration" if "duration" in events_df.columns else None
            trial_type_col = "trial_type" if "trial_type" in events_df.columns else "value" if "value" in events_df.columns else None
            
            if onset_col in events_df.columns and trial_type_col in events_df.columns:
                onsets = events_df[onset_col].values
                # Convert from samples to seconds if needed
                if onset_col == "sample":
                    onsets = onsets / raw.info["sfreq"]
                
                durations = events_df[duration_col].values if duration_col and duration_col in events_df.columns else np.zeros(len(onsets))
                descriptions = events_df[trial_type_col].astype(str).values
                
                # Create annotations
                annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annotations)
        
        # Add derived misc channels
        raw = _add_misc_channels(raw, participants_info, self.DERIVED_MISC_CHANNELS)
        
        # Build description with required info fields
        original_desc = raw.info.get("description", "")
        eegunity_description = {
            "age": str(participants_info.get("age", "")),
            "sex": str(participants_info.get("gender", participants_info.get("sex", ""))),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": str(participants_info.get("handedness", "")),
        }
        # Add any additional required fields
        for field in self.REQUIRED_INFO_FIELDS:
            if field not in eegunity_description and field in participants_info:
                eegunity_description[field] = str(participants_info[field])
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS004625Kernel()