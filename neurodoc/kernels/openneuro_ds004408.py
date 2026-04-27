"""OpenNeuro DS004408 stage1 kernel for EEGUnity.

Dataset: EEG responses to continuous naturalistic speech (audiobook listening).
380 subjects, 128 channels, 512 Hz, continuous paradigm with no discrete events.
Used for cortical entrainment / mTRF encoding model analysis.

Source: https://openneuro.org/datasets/ds004408
DOI: 10.18112/openneuro.ds004408.v1.0.8
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# No subject info available in dataset metadata.
# All fields marked as LLM inference, require human review.
# Source: analysis.md (openneuro_ds004408), 2025-01
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Subject metadata not available in BIDS sidecar or participants.tsv.
# Source: LLM inference, 2025-01, requires human review


# Channel naming: 128-channel system (likely BioSemi 128-channel cap).
# Standard channel names follow 10-20 system with extended coverage.
# Source: Dataset documentation / paper 10.1016/j.neuroimage.2020.117586
# Annotator: LLM, 2025-01, requires human review
_EEG_128_CHANNEL_RENAME_MAP = {
    # Standard 10-20 positions
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fz": "Fz",
    "F7": "F7",
    "F3": "F3",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    # Extended 10-10 positions (128-channel layout)
    "AFp1": "AFp1",
    "AFp2": "AFp2",
    "AFz": "AFz",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCz": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPz": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "O9": "O9",
    "O10": "O10",
    # Additional 128-channel positions (typical BioSemi 128 layout)
    "I1": "I1",
    "I2": "I2",
    "OIz": "OIz",
    "AFF1": "AFF1",
    "AFF2": "AFF2",
    "AFF5": "AFF5",
    "AFF6": "AFF6",
    "AFF7": "AFF7",
    "AFF8": "AFF8",
    "FTT7": "FTT7",
    "FTT8": "FTT8",
    "FTT9": "FTT9",
    "FTT10": "FTT10",
    "FT7": "FT7",
    "FT8": "FT8",
    "FT9": "FT9",
    "FT10": "FT10",
    "FTR7": "FTR7",
    "FTR8": "FTR8",
    "FTR9": "FTR9",
    "FTR10": "FTR10",
    "T9": "T9",
    "T10": "T10",
    "TTP7": "TTP7",
    "TTP8": "TTP8",
    "TTP9": "TTP9",
    "TTP10": "TTP10",
    "TP7": "TP7",
    "TP8": "TP8",
    "TP9": "TP9",
    "TP10": "TP10",
    "TPR7": "TPR7",
    "TPR8": "TPR8",
    "TPR9": "TPR9",
    "TPR10": "TPR10",
    "PTT7": "PTT7",
    "PTT8": "PTT8",
    "PTT9": "PTT9",
    "PTT10": "PTT10",
    "PPO7": "PPO7",
    "PPO3": "PPO3",
    "PPOz": "PPOz",
    "PPO4": "PPO4",
    "PPO8": "PPO8",
    "PO9": "PO9",
    "PO10": "PO10",
    "POO1": "POO1",
    "POO2": "POO2",
    "POO9": "POO9",
    "POO10": "POO10",
    "P1h": "P1h",
    "P2h": "P2h",
    "CPP1": "CPP1",
    "CPP2": "CPP2",
    "CPP3": "CPP3",
    "CPP4": "CPP4",
    "CPP5": "CPP5",
    "CPP6": "CPP6",
    "FCC3": "FCC3",
    "FCC4": "FCC4",
    "FCC5": "FCC5",
    "FCC6": "FCC6",
    "CCP3": "CCP3",
    "CCP4": "CCP4",
    "CCP5": "CCP5",
    "CCP6": "CCP6",
    "FFC1": "FFC1",
    "FFC2": "FFC2",
    "FFC3": "FFC3",
    "FFC4": "FFC4",
    "FFC5": "FFC5",
    "FFC6": "FFC6",
    "A1": "A1",
    "A2": "A2",
    "M1": "M1",
    "M2": "M2",
    "TPP7": "TPP7",
    "TPP8": "TPP8",
    "TPP9": "TPP9",
    "TPP10": "TPP10",
    "P9": "P9",
    "P10": "P10",
    "PPO1": "PPO1",
    "PPO2": "PPO2",
    "PPO9": "PPO9",
    "PPO10": "PPO10",
    "OI1": "OI1",
    "OI2": "OI2",
    "OzIz": "OzIz",
    # Common aliases for BioSemi 128-channel system
    "A3": "A3",
    "A4": "A4",
    "A5": "A5",
    "A6": "A6",
    "A7": "A7",
    "A8": "A8",
    "A9": "A9",
    "A10": "A10",
    "A11": "A11",
    "A12": "A12",
    "A13": "A13",
    "A14": "A14",
    "A15": "A15",
    "A16": "A16",
    "A17": "A17",
    "A18": "A18",
    "A19": "A19",
    "A20": "A20",
    "A21": "A21",
    "A22": "A22",
    "A23": "A23",
    "A24": "A24",
    "A25": "A25",
    "A26": "A26",
    "A27": "A27",
    "A28": "A28",
    "A29": "A29",
    "A30": "A30",
    "A31": "A31",
    "A32": "A32",
    "B1": "B1",
    "B2": "B2",
    "B3": "B3",
    "B4": "B4",
    "B5": "B5",
    "B6": "B6",
    "B7": "B7",
    "B8": "B8",
    "B9": "B9",
    "B10": "B10",
    "B11": "B11",
    "B12": "B12",
    "B13": "B13",
    "B14": "B14",
    "B15": "B15",
    "B16": "B16",
    "B17": "B17",
    "B18": "B18",
    "B19": "B19",
    "B20": "B20",
    "B21": "B21",
    "B22": "B22",
    "B23": "B23",
    "B24": "B24",
    "B25": "B25",
    "B26": "B26",
    "B27": "B27",
    "B28": "B28",
    "B29": "B29",
    "B30": "B30",
    "B31": "B31",
    "B32": "B32",
}


def _get_subject_info_from_participants(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv if available."""
    import pandas as pd
    
    # Navigate to dataset root
    current_dir = os.path.dirname(file_path)
    participants_path = None
    
    # Search up to 3 levels for participants.tsv
    for _ in range(5):
        potential_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(potential_path):
            participants_path = potential_path
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    
    if participants_path is None:
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject ID (handle both 'sub-01' and '01' formats)
        sub_col = "participant_id"
        if sub_col not in df.columns:
            return {}
        
        # Normalize subject ID for matching
        search_id = subject_id
        if not search_id.startswith("sub-"):
            search_id = f"sub-{search_id}"
        
        row = df[df[sub_col] == search_id]
        if row.empty:
            # Try without sub- prefix
            search_id = subject_id.replace("sub-", "")
            row = df[df[sub_col].str.replace("sub-", "", regex=False) == search_id]
        
        if row.empty:
            return {}
        
        info = {}
        # Extract age
        if "age" in row.columns:
            age_val = row["age"].values[0]
            if pd.notna(age_val):
                info["age"] = str(int(float(age_val)))
        
        # Extract sex
        if "sex" in row.columns:
            sex_val = row["sex"].values[0]
            if pd.notna(sex_val):
                sex_lower = str(sex_val).lower()
                if sex_lower in ("m", "male"):
                    info["sex"] = "male"
                elif sex_lower in ("f", "female"):
                    info["sex"] = "female"
        
        # Extract handedness if available
        if "handedness" in row.columns:
            hand_val = row["handedness"].values[0]
            if pd.notna(hand_val):
                info["handedness"] = str(hand_val).lower()
        
        # Extract any other fields as strings
        for col in row.columns:
            if col not in ("participant_id", "age", "sex", "handedness"):
                val = row[col].values[0]
                if pd.notna(val):
                    info[col] = str(val)
        
        return info
    
    except Exception:
        return {}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    # Typical pattern: sub-XX/... or sub-XX_ses-YY_...
    basename = os.path.basename(file_path)
    parts = basename.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    # Try from directory structure
    path_parts = file_path.replace("\\", "/").split("/")
    for part in path_parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standardization."""
    rename_map = {}
    existing = set(raw.ch_names)
    
    for standard_name, target_name in _EEG_128_CHANNEL_RENAME_MAP.items():
        if standard_name in existing and standard_name != target_name:
            rename_map[standard_name] = target_name
    
    # Handle common BioSemi 128 naming patterns
    # BioSemi often uses numbered channels or A1-A32, B1-B32, etc.
    biosemi_aliases = {
        # If channels are named with standard 10-20/10-10/10-5 names, keep them
        # Common alternative naming schemes for 128-channel systems
    }
    
    for alias, target in biosemi_aliases.items():
        if alias in existing and alias not in rename_map:
            rename_map[alias] = target
    
    return rename_map


@dataclass
class OpenNeuroDS004408Kernel:
    """Stage1 kernel for OpenNeuro DS004408 dataset."""

    KERNEL_ID: str = "openneuro-ds004408-stage1"
    HANDLES_UNAVAILABLE: bool = False

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _extract_subject_id(file_path)
        
        # Get subject info from participants.tsv
        subject_info = _get_subject_info_from_participants(file_path, subject_id)
        
        # Fallback to hardcoded dict if available
        if subject_id in _SUBJECT_DICT:
            subject_info = {**_SUBJECT_DICT[subject_id], **subject_info}
        
        # Build eegunity_description
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")
        
        # Ensure sex is lowercase and valid
        if sex not in ("male", "female", "unknown"):
            sex_lower = sex.lower()
            if sex_lower in ("m", "male"):
                sex = "male"
            elif sex_lower in ("f", "female"):
                sex = "female"
            else:
                sex = "unknown"
        
        # Device info from dataset documentation
        # Source: analysis.md, paper 10.1016/j.neuroimage.2020.117586
        # Annotator: LLM, 2025-01, requires human review
        # LLM 推断，需人类复核
        amplifier = "BioSemi ActiveTwo"  # LLM 推断，需人类复核
        cap = "BioSemi 128-channel cap"  # LLM 推断，需人类复核
        
        # Handle channel renaming BEFORE set_montage
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage for standard 128-channel layout
        # Source: Dataset uses standard BioSemi 128-channel layout
        # Annotator: LLM, 2025-01, requires human review
        try:
            # Try to use standard 10-10 montage as approximation for 128 channels
            montage = mne.channels.make_standard_montage("biosemi128")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            # Fallback: try standard 10-05 or 10-20
            try:
                montage = mne.channels.make_standard_montage("standard_1005")
                raw.set_montage(montage, match_case=False, on_missing="warn")
            except Exception:
                # LLM 推断，需人类复核
                pass  # Skip montage if not available
        
        # Ensure all EEG channels have correct type
        # Set any non-standard types to EEG
        ch_types = raw.get_channel_types()
        type_map = {}
        for ch_name, ch_type in zip(raw.ch_names, ch_types):
            # Keep known non-EEG types, set unknown to EEG
            if ch_type not in ("eeg", "eog", "ecg", "emg", "misc", "stim"):
                type_map[ch_name] = "eeg"
        
        if type_map:
            raw.set_channel_types(type_map)
        
        # Handle events: continuous speech listening paradigm
        # No discrete trial events; continuous recording
        # If events.tsv exists, create annotations from it
        events_tsv_path = file_path.replace(".set", "_events.tsv").replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv").replace(".fif", "_events.tsv")
        
        if os.path.exists(events_tsv_path):
            try:
                import pandas as pd
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                
                if not events_df.empty and "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df.get("duration", np.zeros(len(onsets))).values
                    descriptions = events_df.get("trial_type", events_df.get("value", "continuous_speech_listening")).values
                    
                    # Ensure descriptions are strings
                    descriptions = [str(d) if pd.notna(d) else "continuous_speech_listening" for d in descriptions]
                    
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
            except Exception:
                # If events.tsv parsing fails, add a single continuous annotation
                pass
        
        # If no annotations exist, add a single continuous annotation for the entire recording
        if raw.annotations is None or len(raw.annotations) == 0:
            annotations = mne.Annotations(
                onset=[0],
                duration=[raw.times[-1]],
                description=["continuous_speech_listening"],
            )
            raw.set_annotations(annotations)
        
        # Build description with required fields
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_description = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add any extra fields from participants.tsv
        for key, value in subject_info.items():
            if key not in ("age", "sex", "handedness"):
                eegunity_description[key] = str(value)
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004408Kernel()