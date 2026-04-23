"""OpenNeuro DS003810 stage1 kernel for EEGUnity.

Motor imagery EEG dataset using low-cost consumer-grade EEG system.
Participants performed kinesthetic motor imagery of grasping movements.
Data recorded with OpenViBE (OVTK) event triggers.

BIDS dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds003810
References:
  - DOI: 10.1016/j.dib.2022.108225 (Data in Brief paper)
  - DOI: 10.1016/j.heliyon.2020.e03425 (Original MI-BCI feasibility study)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Kernel Requirements
# =============================================================================
kernel_requirements = {
    "required_info_fields": ["age", "gender"],
    "required_native_misc": [],
    "derived_misc_channels": [],
}

# =============================================================================
# Channel Mapping for Low-Cost 15-Channel EEG System
# =============================================================================
# Source: README and dataset documentation describe 15-channel EEG system.
# Original EDF files use EEG-0..EEG-14. Mapping inferred from standard 10-20
# layout for low-cost consumer-grade EEG with frontocentral coverage optimized
# for motor imagery BCI.
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-0": "Fp1",
    "EEG-1": "Fp2",
    "EEG-2": "F7",
    "EEG-3": "F3",
    "EEG-4": "Fz",
    "EEG-5": "F4",
    "EEG-6": "F8",
    "EEG-7": "T7",
    "EEG-8": "C3",
    "EEG-9": "Cz",
    "EEG-10": "C4",
    "EEG-11": "T8",
    "EEG-12": "P3",
    "EEG-13": "Pz",
    "EEG-14": "P4",
}

# =============================================================================
# Device Information
# =============================================================================
# Source: Papers describe "low-cost consumer-grade EEG system" but specific
# model (Muse, OpenBCI, etc.) is not explicitly stated in available documentation.
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_AMPLIFIER: str = "low-cost consumer-grade EEG"  # LLM 推断，需人类复核
_CAP: str = "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from actual channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    for source_name, target_name in _CHANNEL_RENAME_MAP.items():
        if source_name in raw.ch_names:
            rename_map[source_name] = target_name
    return rename_map


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    df = pd.read_csv(participants_path, sep="\t")
    
    # Match subject_id format (e.g., "sub-01" -> "sub-01")
    row = df[df["participant_id"] == subject_id]
    if row.empty:
        # Try without "sub-" prefix if needed
        row = df[df["participant_id"] == subject_id.replace("sub-", "")]
    
    if row.empty:
        return {}
    
    info = {}
    row_data = row.iloc[0]
    
    # Age
    if "age" in row_data and pd.notna(row_data["age"]):
        info["age"] = str(int(float(row_data["age"])))
    else:
        info["age"] = "unknown"
    
    # Gender/sex
    if "gender" in row_data and pd.notna(row_data["gender"]):
        gender_val = str(row_data["gender"]).lower().strip()
        if gender_val in ["m", "male"]:
            info["sex"] = "male"
        elif gender_val in ["f", "female"]:
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    elif "sex" in row_data and pd.notna(row_data["sex"]):
        sex_val = str(row_data["sex"]).lower().strip()
        if sex_val in ["m", "male"]:
            info["sex"] = "male"
        elif sex_val in ["f", "female"]:
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    else:
        info["sex"] = "unknown"
    
    # Handedness
    if "handedness" in row_data and pd.notna(row_data["handedness"]):
        hand_val = str(row_data["handedness"]).lower().strip()
        if hand_val in ["r", "right"]:
            info["handedness"] = "right"
        elif hand_val in ["l", "left"]:
            info["handedness"] = "left"
        else:
            info["handedness"] = "unknown"
    else:
        info["handedness"] = "unknown"
    
    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for a given EEG file."""
    # Construct events.tsv path from EDF path
    base_path = file_path.replace("_eeg.edf", "_events.tsv")
    if not os.path.exists(base_path):
        # Try alternative naming
        base_path = file_path.replace(".edf", "_events.tsv")
    
    if not os.path.exists(base_path):
        return None
    
    return pd.read_csv(base_path, sep="\t")


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = row.get("onset", 0)
        duration = row.get("duration", 0)
        
        # Use trial_type if available, otherwise value, otherwise stim_type
        if "trial_type" in row and pd.notna(row["trial_type"]):
            desc = str(row["trial_type"])
        elif "value" in row and pd.notna(row["value"]):
            desc = str(row["value"])
        elif "stim_type" in row and pd.notna(row["stim_type"]):
            desc = str(row["stim_type"])
        else:
            desc = "unknown"
        
        onsets.append(float(onset))
        durations.append(float(duration) if duration > 0 else 0)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


@dataclass
class OpenNeuroDS003810Kernel:
    """Stage1 kernel for OpenNeuro ds003810 dataset."""

    KERNEL_ID: str = "openneuro-ds003810-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        # Path format: .../sub-XX/eeg/sub-XX_task-MIvsRest_run-XX_eeg.edf
        basename = os.path.basename(file_path)
        subject_id = basename.split("_")[0]  # e.g., "sub-01"
        
        # =================================================================
        # Channel Rename (BEFORE set_montage)
        # =================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types for any non-EEG channels if present
        # All channels in this dataset are EEG
        eeg_chs = [ch for ch in raw.ch_names if ch not in ["Status", "Trig"]]
        ch_types = {ch: "eeg" for ch in eeg_chs}
        
        # Handle any misc channels if they exist
        for ch in raw.ch_names:
            if ch in ["Status", "Trig", "STI", "STIM"]:
                ch_types[ch] = "misc"
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage for standard 10-20 channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            pass  # Montage setting is best-effort
        
        # =================================================================
        # Read Participants Info
        # =================================================================
        subject_info = _read_participants_info(dataset_path, subject_id)
        
        # =================================================================
        # Read Events from TSV (for EDF files without embedded annotations)
        # =================================================================
        # EDF files in this dataset may not have embedded annotations, so we
        # derive annotations from the sibling events.tsv file
        events_df = _read_events_tsv(file_path)
        
        # Check if raw already has meaningful annotations
        has_native_annotations = (
            raw.annotations is not None 
            and len(raw.annotations) > 0
            and not all(desc == "BAD_" or desc == "" for desc in raw.annotations.description)
        )
        
        if not has_native_annotations and events_df is not None and not events_df.empty:
            # Derive annotations from events.tsv
            annotations = _events_to_annotations(events_df, raw.info["sfreq"])
            raw.set_annotations(annotations)
        
        # =================================================================
        # Build eegunity_description
        # =================================================================
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Add required info fields from participants.tsv
        # These are already included above (age, sex/gender mapping)
        # If gender column exists with different name, ensure it's captured
        participants_path = os.path.join(dataset_path, "participants.tsv")
        if os.path.exists(participants_path):
            p_df = pd.read_csv(participants_path, sep="\t")
            p_row = p_df[p_df["participant_id"] == subject_id]
            if p_row.empty:
                p_row = p_df[p_df["participant_id"] == subject_id.replace("sub-", "")]
            
            if not p_row.empty:
                for field in kernel_requirements.get("required_info_fields", []):
                    if field not in ["age", "gender"]:  # Already handled
                        if field in p_row.columns and pd.notna(p_row.iloc[0][field]):
                            eegunity_description[field] = str(p_row.iloc[0][field])
                        else:
                            eegunity_description[field] = "unknown"
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS003810Kernel()