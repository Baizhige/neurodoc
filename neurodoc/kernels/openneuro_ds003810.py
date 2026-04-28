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
    "derived_misc_channels": ["age_misc"],
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
    
    # Normalize subject_id format (e.g., "sub-01" -> "sub-01")
    # participants.tsv may use "sub-01" or "01" format
    if subject_id.startswith("sub-"):
        search_id = subject_id
    else:
        search_id = f"sub-{subject_id}"
    
    # Try matching with "sub-" prefix first
    row = df[df["participant_id"] == search_id]
    if row.empty and not subject_id.startswith("sub-"):
        # Try without prefix
        row = df[df["participant_id"] == subject_id]
    if row.empty and subject_id.startswith("sub-"):
        # Try extracting number only
        bare_id = subject_id.replace("sub-", "")
        row = df[df["participant_id"] == bare_id]
    
    if row.empty:
        return {}
    
    info = {}
    row_data = row.iloc[0]
    
    # Age
    if "age" in row_data:
        info["age"] = str(row_data["age"])
    
    # Gender/sex
    if "gender" in row_data:
        gender_val = str(row_data["gender"]).lower().strip()
        if gender_val in ("m", "male"):
            info["sex"] = "male"
        elif gender_val in ("f", "female"):
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    elif "sex" in row_data:
        sex_val = str(row_data["sex"]).lower().strip()
        if sex_val in ("m", "male"):
            info["sex"] = "male"
        elif sex_val in ("f", "female"):
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    
    # Handedness
    if "handedness" in row_data:
        info["handedness"] = str(row_data["handedness"])
    
    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar if it exists."""
    # EDF file path -> construct events.tsv path
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.edf -> sub-XX_task-YY_run-ZZ_events.tsv
    base_path = file_path.replace("_eeg.edf", "").replace(".edf", "")
    events_path = base_path + "_events.tsv"
    
    if not os.path.exists(events_path):
        # Try alternative: same directory, replace extension
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        # Remove .edf and add _events.tsv
        name_without_ext = file_name.replace(".edf", "")
        events_path = os.path.join(dir_name, name_without_ext + "_events.tsv")
    
    if not os.path.exists(events_path):
        return None
    
    return pd.read_csv(events_path, sep="\t")


def _events_tsv_to_annotations(events_df: pd.DataFrame) -> Optional[mne.Annotations]:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return None
    
    # Required columns: onset, duration; optional: trial_type, value, sample
    if "onset" not in events_df.columns:
        return None
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Description priority: trial_type > value > stim_type > "event"
    descriptions = []
    for _, row in events_df.iterrows():
        if "trial_type" in row and pd.notna(row["trial_type"]):
            desc = str(row["trial_type"])
        elif "value" in row and pd.notna(row["value"]):
            desc = str(row["value"])
        elif "stim_type" in row and pd.notna(row["stim_type"]):
            desc = str(row["stim_type"])
        else:
            desc = "event"
        descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    # Typical pattern: sub-01/... or sub-01_ses-...
    basename = os.path.basename(file_path)
    parts = basename.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    # Try from directory structure
    dirs = file_path.split(os.sep)
    for d in dirs:
        if d.startswith("sub-"):
            return d
    return "unknown"


@dataclass
class OpenNeuroDS003810Kernel:
    """Stage1 kernel for OpenNeuro ds003810 dataset."""

    KERNEL_ID: str = "openneuro-ds003810-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Preload raw data to allow adding channels
        raw.load_data()
        
        # ---------------------------------------------------------------------
        # 1. Channel rename (BEFORE set_montage)
        # ---------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for any non-EEG channels (all renamed channels are EEG)
        # Check if there are any non-EEG channels that need special handling
        eeg_channels = [ch for ch in raw.ch_names if ch in _CHANNEL_RENAME_MAP.values()]
        if eeg_channels:
            raw.set_channel_types({ch: "eeg" for ch in eeg_channels})
        
        # ---------------------------------------------------------------------
        # 2. Set standard 10-20 montage
        # ---------------------------------------------------------------------
        # Use standard 10-20 montage for the renamed channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in the montage
            montage_ch_names = set(montage.ch_names)
            existing_ch_names = set(raw.ch_names)
            common_ch_names = list(existing_ch_names & montage_ch_names)
            if common_ch_names:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is best-effort
        
        # ---------------------------------------------------------------------
        # 3. Read participants.tsv info
        # ---------------------------------------------------------------------
        participants_info = _read_participants_info(dataset_path, subject_id)
        
        age_str = participants_info.get("age", "unknown")
        sex_str = participants_info.get("sex", "unknown")
        handedness_str = participants_info.get("handedness", "unknown")
        
        # ---------------------------------------------------------------------
        # 4. Add derived misc channels
        # ---------------------------------------------------------------------
        n_times = len(raw.times)
        sfreq = raw.info["sfreq"]
        
        # age_misc: from participants.tsv column "age" — constant broadcast
        if "age" in participants_info:
            try:
                age_val = float(participants_info["age"])
                age_data = np.full((1, n_times), age_val, dtype=np.float64)
                age_info = mne.create_info(ch_names=["age_misc"], sfreq=sfreq, ch_types=["misc"])
                age_raw = mne.io.RawArray(age_data, age_info)
                raw.add_channels([age_raw], force_update_info=True)
            except (ValueError, TypeError):
                # Cannot parse age as numeric; skip channel
                pass
        
        # ---------------------------------------------------------------------
        # 5. Process events from events.tsv sidecar
        # ---------------------------------------------------------------------
        events_df = _read_events_tsv(file_path)
        annotations = _events_tsv_to_annotations(events_df)
        
        if annotations is not None:
            # Set annotations, replacing any existing ones
            raw.set_annotations(annotations)
        
        # ---------------------------------------------------------------------
        # 6. Set measurement info
        # ---------------------------------------------------------------------
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        eegunity_description = {
            "age": age_str,
            "sex": sex_str,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": handedness_str,
        }
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        return raw


# =============================================================================
# Module-level singleton
# =============================================================================
KERNEL = OpenNeuroDS003810Kernel()