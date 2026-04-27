"""OpenNeuro DS003775 (SRM Resting-State EEG) stage1 kernel for EEGUnity.

Dataset: openneuro_ds003775
URL: https://openneuro.org/datasets/ds003775
Year: 2022
Subjects: 111
Files: 153
Channels: 64
Sampling Rate: 1024 Hz

Paradigm: Four minutes of eyes-closed resting-state EEG.

Source: https://doi.org/10.1016/j.dib.2022.108647 (dataset descriptor paper)
         https://doi.org/10.1016/j.clinph.2024.09.019 (age correlation study)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# Standard 64-channel layout based on BrainCap 64-channel system (10-20 system extended)
# Source: Dataset documentation (openneuro_ds003775)
# Annotator: LLM, 2026-04-08; needs human verification
_EEG_CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8",
    "T7", "T8",
    "TP7", "TP8",
    "T9", "T10",
    "M1", "M2",
    "A1", "A2",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]


def _detect_channel_type(ch_name: str) -> str:
    """Detect channel type from channel name."""
    ch_upper = ch_name.upper()
    if any(x in ch_upper for x in ["EOG", "VEOG", "HEOG", "EOG-"]):
        return "eog"
    elif any(x in ch_upper for x in ["ECG", "EKG"]):
        return "ecg"
    elif any(x in ch_upper for x in ["EMG"]):
        return "emg"
    elif any(x in ch_upper for x in ["TRIGGER", "STIM", "MARKER"]):
        return "stim"
    elif ch_upper.startswith("EEG"):
        return "eeg"
    elif ch_upper in ["M1", "M2", "A1", "A2", "TP9", "TP10", "T9", "T10"]:
        return "misc"  # Mastoid/earlab references
    elif ch_upper in ["CB1", "CB2"]:
        return "misc"
    return "eeg"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map to convert raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common non-standard naming patterns in EEG data
    patterns = [
        # BrainAmp style: EEG + number
        ("EEG ", "EEG-"),
    ]
    
    for old, new in patterns:
        if old in existing:
            rename_map[old] = new
    
    # Check for numbered EEG channels (e.g., EEG 1, EEG 001, EEG001)
    for ch in list(existing):
        ch_upper = ch.upper()
        # Match EEG-001, EEG001, EEG 001 patterns
        if ch_upper.startswith("EEG"):
            rest = ch[3:].strip()
            if rest.isdigit():
                # Convert to EEG-XXX format for matching
                idx = int(rest) - 1  # 0-indexed
                if 0 <= idx < len(_EEG_CHANNEL_STANDARD_NAMES):
                    std_name = _EEG_CHANNEL_STANDARD_NAMES[idx]
                    if std_name in existing:
                        # If standard name already exists, skip
                        continue
                    rename_map[ch] = std_name
    
    return rename_map


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if it exists."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


class DS003775Kernel:
    """Stage1 kernel for OpenNeuro DS003775 (SRM Resting-State EEG)."""

    KERNEL_ID: str = "openneuro-ds003775-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (in-memory)
        row : Locator row with File Path and metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        dataset_path = row.get("Dataset Path", "")
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "unknown")
        
        # Store original description
        original_desc = raw.info.get("description", "")
        
        # Build eegunity_description
        eegunity_desc: Dict[str, str] = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",  # LLM 推断，需人类复核
            "cap": "unknown",  # LLM 推断，需人类复核
            "handedness": "unknown",
        }
        
        # Try to load participant info from participants.tsv
        if dataset_path:
            df = _load_participants_tsv(dataset_path)
            if not df.empty:
                # Match subject ID format (e.g., sub-001 or 001)
                subj_col = None
                for col in ["participant_id", "subject_id", "subject"]:
                    if col in df.columns:
                        subj_col = col
                        break
                
                if subj_col:
                    # Normalize subject ID for matching
                    norm_id = subject_id.replace("sub-", "").replace("sub", "")
                    for _, p_row in df.iterrows():
                        p_id = str(p_row.get(subj_col, "")).replace("sub-", "")
                        if p_id == norm_id:
                            # Extract age
                            for age_col in ["age", "Age", "AGE"]:
                                if age_col in df.columns:
                                    age_val = p_row.get(age_col)
                                    if pd.notna(age_val):
                                        try:
                                            eegunity_desc["age"] = str(int(float(age_val)))
                                        except (ValueError, TypeError):
                                            eegunity_desc["age"] = "unknown"
                                    break
                            
                            # Extract sex
                            for sex_col in ["sex", "Sex", "gender", "Gender"]:
                                if sex_col in df.columns:
                                    sex_val = str(p_row.get(sex_col, "")).lower().strip()
                                    if sex_val in ["m", "male", "f", "female"]:
                                        eegunity_desc["sex"] = "male" if sex_val.startswith("m") else "female"
                                    break
                            
                            # Extract handedness if available
                            for hand_col in ["handedness", "hand", "dominant_hand"]:
                                if hand_col in df.columns:
                                    hand_val = str(p_row.get(hand_col, "")).lower().strip()
                                    if hand_val in ["r", "right", "l", "left"]:
                                        eegunity_desc["handedness"] = "right" if hand_val.startswith("r") else "left"
                                    break
                            
                            break
        
        # Device info from dataset documentation
        # Source: Dataset descriptor paper (10.1016/j.dib.2022.108647)
        # Annotator: LLM, 2026-04-08; needs human verification
        eegunity_desc["amplifier"] = "BrainAmp"  # LLM 推断，需人类复核
        eegunity_desc["cap"] = "Ag/AgCl"  # LLM 推断，需人类复核
        
        # Set description
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard names BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only existing channels
            rename_map = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if rename_map:
                print(f"[DS003775] Renaming channels: {rename_map}")
                raw.rename_channels(rename_map)
        
        # Set channel types based on names
        new_channel_types = {}
        for ch in raw.ch_names:
            ch_type = _detect_channel_type(ch)
            if ch_type != "eeg":
                new_channel_types[ch] = ch_type
        
        if new_channel_types:
            raw.set_channel_types(new_channel_types)
        
        # Try to set montage (standard 1020 or 10-20 extended)
        # Based on 64-channel description, likely BrainCap 64
        # Source: Dataset documentation
        # Annotator: LLM, 2026-04-08; needs human verification
        try:
            # Try standard 1020 first (works for 64 channels with extended positions)
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Get channels that exist in both raw and montage
            ch_names_raw = set(raw.ch_names)
            ch_names_montage = set(montage.ch_names)
            
            # Common channels to pick from extended montage
            common_channels = ch_names_raw & ch_names_montage
            
            if len(common_channels) >= 20:
                # Enough channels match, use standard montage
                # Pick only channels that exist in raw data
                picked_montage = montage.pick_channels(list(common_channels))
                raw.set_montage(picked_montage, on_missing="warn")
                print(f"[DS003775] Applied standard_1020 montage with {len(common_channels)} channels")
            else:
                print(f"[DS003775] Warning: Only {len(common_channels)} channels match standard montage")
        except Exception as e:
            print(f"[DS003775] Warning: Could not set montage: {e}")
        
        # For resting-state EEG, there are no events
        # Create a single annotation indicating resting-state
        # This serves as the raw meta marker
        n_samples = raw.n_times
        sfreq = raw.info["sfreq"]
        duration = n_samples / sfreq
        
        annotations = mne.Annotations(
            onset=[0.0],
            duration=[duration],
            description=["resting-state-eyes-closed"],
        )
        raw.set_annotations(annotations)
        
        return raw


KERNEL = DS003775Kernel()