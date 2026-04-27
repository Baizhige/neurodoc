"""OpenNeuro DS001784 stage1 kernel for EEGUnity.

Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant
depression (EEG). BIDS-formatted dataset with 65 channels at 1450 Hz.

Dataset: openneuro_ds001784 | Year: 2019 | DOI: https://doi.org/10.1038/s41467-019-09557-4
Paradigm: MSIT with emotional stimuli + DBS ON/OFF

This kernel:
- Reads participants.tsv for age/sex/dbs metadata and required info fields
- Parses events.tsv to extract trial_type labels and map to canonical event IDs
- Maps raw events (event_2/4/6) to semantic labels with paradigm prefix
- Sets standard 10-20 montage for 65-channel EEG
- Creates derived misc channel: madrs_change from participants.tsv madrs_bl - madrs_fu

Source: https://openneuro.org/datasets/ds001784
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Required info fields from participants.tsv (from kernel requirements)
# =============================================================================
_REQUIRED_INFO_FIELDS: List[str] = [
    "age",
    "dbs_stim_freq",
    "gender",
    "hypomania",
    "madrs_bl",
    "madrs_fu",
    "responder",
    "ybocs_bl",
]

# =============================================================================
# Derived misc channels to create
# =============================================================================
_DERIVED_MISC_CHANNELS: List[Dict[str, Any]] = [
    {
        "name": "madrs_change",
        "source_field": "madrs_bl",  # participants.tsv column
        "derivation": "madrs_bl - madrs_fu",
    },
]

# =============================================================================
# Raw Event Mapping (from analysis.md Event Structure table and task requirements)
# Event ID mapping corrected: event_2=control, event_4=IAPS onset, event_6=interference
# =============================================================================
_EVENT_RAW_MAP: Dict[str, str] = {
    "2": "afMSIT: control_trial",
    "4": "afMSIT: iaps_onset",
    "6": "afMSIT: interference_trial",
}

# Numeric codes for events_from_annotations compatibility
_EVENT_ID_MAP: Dict[str, int] = {
    "afMSIT: control_trial": 2,
    "afMSIT: iaps_onset": 4,
    "afMSIT: interference_trial": 6,
}

# =============================================================================
# Channel Rename Map for 64-65 Channel Standard Systems
# Source: Widge et al. 2019 Nature Communications, 65-channel extended 10-20 layout
# Annotator: LLM, 2026-04-08 — by LLM 推断，需人类复核
# =============================================================================
_CHANNEL_ALIAS_GROUPS: List[List[str]] = [
    ["Fp1", "FP1", "fp1", "EEG-Fp1"],
    ["Fpz", "FPz", "fpz", "EEG-Fpz"],
    ["Fp2", "FP2", "fp2", "EEG-Fp2"],
    ["AF7", "AF7", "EEG-AF7"],
    ["AF3", "AF3", "EEG-AF3"],
    ["AFz", "AFz", "EEG-AFz"],
    ["AF4", "AF4", "EEG-AF4"],
    ["AF8", "AF8", "EEG-AF8"],
    ["F7", "F7", "EEG-F7"],
    ["F5", "F5", "EEG-F5"],
    ["F3", "F3", "EEG-F3"],
    ["F1", "F1", "EEG-F1"],
    ["Fz", "Fz", "EEG-Fz"],
    ["F2", "F2", "EEG-F2"],
    ["F4", "F4", "EEG-F4"],
    ["F6", "F6", "EEG-F6"],
    ["F8", "F8", "EEG-F8"],
    ["FT7", "FT7", "EEG-FT7"],
    ["FC5", "FC5", "EEG-FC5"],
    ["FC3", "FC3", "EEG-FC3"],
    ["FC1", "FC1", "EEG-FC1"],
    ["FCz", "FCz", "EEG-FCz"],
    ["FC2", "FC2", "EEG-FC2"],
    ["FC4", "FC4", "EEG-FC4"],
    ["FC6", "FC6", "EEG-FC6"],
    ["FT8", "FT8", "EEG-FT8"],
    ["T7", "T7", "EEG-T7", "T3"],
    ["C5", "C5", "EEG-C5"],
    ["C3", "C3", "EEG-C3"],
    ["C1", "C1", "EEG-C1"],
    ["Cz", "Cz", "EEG-Cz"],
    ["C2", "C2", "EEG-C2"],
    ["C4", "C4", "EEG-C4"],
    ["C6", "C6", "EEG-C6"],
    ["T8", "T8", "EEG-T8", "T4"],
    ["TP7", "TP7", "EEG-TP7"],
    ["CP5", "CP5", "EEG-CP5"],
    ["CP3", "CP3", "EEG-CP3"],
    ["CP1", "CP1", "EEG-CP1"],
    ["CPz", "CPz", "EEG-CPz"],
    ["CP2", "CP2", "EEG-CP2"],
    ["CP4", "CP4", "EEG-CP4"],
    ["CP6", "CP6", "EEG-CP6"],
    ["TP8", "TP8", "EEG-TP8"],
    ["P7", "P7", "EEG-P7"],
    ["P5", "P5", "EEG-P5"],
    ["P3", "P3", "EEG-P3"],
    ["P1", "P1", "EEG-P1"],
    ["Pz", "Pz", "EEG-Pz"],
    ["P2", "P2", "EEG-P2"],
    ["P4", "P4", "EEG-P4"],
    ["P6", "P6", "EEG-P6"],
    ["P8", "P8", "EEG-P8"],
    ["PO7", "PO7", "EEG-PO7"],
    ["PO3", "PO3", "EEG-PO3"],
    ["POz", "POz", "EEG-POz"],
    ["PO4", "PO4", "EEG-PO4"],
    ["PO8", "PO8", "EEG-PO8"],
    ["O1", "O1", "EEG-O1"],
    ["Oz", "Oz", "EEG-Oz"],
    ["O2", "O2", "EEG-O2"],
    ["Iz", "Iz", "EEG-Iz"],
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in [(group[0], group) for group in _CHANNEL_ALIAS_GROUPS]:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load participant info from participants.tsv.
    
    Returns dict with all required info fields, using "unknown" for missing values.
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    info: Dict[str, str] = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
    
    if not os.path.exists(participants_path):
        return info
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        
        # Normalize subject_id to match participants.tsv format
        # participants.tsv uses "sub-01", file paths use "sub-01"
        if not subject_id.startswith("sub-"):
            # Extract numeric part if given as just "01"
            subject_id = f"sub-{int(subject_id):02d}"
        
        # Find matching row
        subj_row = df[df["participant_id"] == subject_id]
        if subj_row.empty:
            # Try without leading zeros
            subj_row = df[df["participant_id"] == subject_id.replace("sub-0", "sub-")]
        
        if not subj_row.empty:
            row_data = subj_row.iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row_data.index:
                    val = row_data[field]
                    # Handle NaN/missing
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
    except Exception:
        # If any error, keep all as unknown
        pass
    
    return info


def _compute_madrs_change(participants_info: Dict[str, str]) -> Optional[float]:
    """Compute madrs_change = madrs_bl - madrs_fu from participants info."""
    try:
        madrs_bl = float(participants_info.get("madrs_bl", "nan"))
        madrs_fu = float(participants_info.get("madrs_fu", "nan"))
        if not (np.isnan(madrs_bl) or np.isnan(madrs_fu)):
            return madrs_bl - madrs_fu
    except (ValueError, TypeError):
        pass
    return None


def _parse_events_tsv(events_path: str) -> Optional[mne.Annotations]:
    """Parse BIDS events.tsv file and return MNE Annotations."""
    if not os.path.exists(events_path):
        return None
    
    try:
        df = pd.read_csv(events_path, sep="\t")
        
        # Required columns
        if "onset" not in df.columns or "trial_type" not in df.columns:
            return None
        
        onsets = df["onset"].values
        durations = df["duration"].values if "duration" in df.columns else np.zeros(len(df))
        
        # Map trial_type to canonical event descriptions
        descriptions = []
        for tt in df["trial_type"]:
            tt_str = str(tt)
            # Map to canonical event ID then to description
            if tt_str in _EVENT_RAW_MAP:
                descriptions.append(_EVENT_RAW_MAP[tt_str])
            else:
                # Try to find by value
                descriptions.append(f"afMSIT: {tt_str}")
        
        return mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
    except Exception:
        return None


def _add_misc_channel(raw: mne.io.BaseRaw, name: str, value: float) -> mne.io.BaseRaw:
    """Add a constant-valued misc channel to the raw object."""
    # Create constant data array matching the raw data shape
    data = np.full((1, raw.n_times), value, dtype=raw._data.dtype)
    
    # Create info for the new channel
    ch_info = mne.create_info(
        ch_names=[name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    
    # Create a RawArray for the new channel
    raw_misc = mne.io.RawArray(data, ch_info, verbose=False)
    
    # Add to existing raw
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


@dataclass
class OpenNeuroDS001784Kernel:
    """Stage1 kernel for OpenNeuro ds001784 dataset."""
    
    KERNEL_ID: str = "openneuro-ds001784-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        # BIDS path: sub-XX/ses-YY/eeg/sub-XX_ses-YY_task-afmsit_eeg.bdf
        path_parts = file_path.replace("\\", "/").split("/")
        subject_id = "unknown"
        for part in path_parts:
            if part.startswith("sub-"):
                subject_id = part
                break
        
        # ---------------------------------------------------------------------
        # 1. Load participants.tsv info
        # ---------------------------------------------------------------------
        participants_info = _load_participants_info(dataset_path, subject_id)
        
        # ---------------------------------------------------------------------
        # 2. Determine sex from gender field (lowercase standardization)
        # ---------------------------------------------------------------------
        gender_raw = participants_info.get("gender", "unknown")
        sex = "unknown"
        if gender_raw.lower() in ("m", "male"):
            sex = "male"
        elif gender_raw.lower() in ("f", "female"):
            sex = "female"
        
        # ---------------------------------------------------------------------
        # 3. Determine age (always string)
        # ---------------------------------------------------------------------
        age = participants_info.get("age", "unknown")
        
        # ---------------------------------------------------------------------
        # 4. Device metadata
        # Source: Widge et al. 2019 Nature Communications — 65-channel BioSemi ActiveTwo
        # Annotator: LLM, 2026-04-08 — by LLM 推断，需人类复核
        # ---------------------------------------------------------------------
        amplifier = "BioSemi ActiveTwo"  # LLM 推断，需人类复核
        cap = "BioSemi 64-channel with external CMS/DRL"  # LLM 推断，需人类复核
        
        # ---------------------------------------------------------------------
        # 5. Handedness (not reported in dataset, set to unknown)
        # ---------------------------------------------------------------------
        handedness = "unknown"
        
        # ---------------------------------------------------------------------
        # 6. Build eegunity_description with required info fields
        # ---------------------------------------------------------------------
        eegunity_desc = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add all required info fields from participants.tsv as strings
        for field in _REQUIRED_INFO_FIELDS:
            eegunity_desc[field] = participants_info.get(field, "unknown")
        
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # ---------------------------------------------------------------------
        # 7. Rename channels to standard 10-20 names
        # ---------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, verbose=False)
        
        # ---------------------------------------------------------------------
        # 8. Set standard 10-20 montage
        # ---------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn", verbose=False)
        except Exception:
            pass
        
        # ---------------------------------------------------------------------
        # 9. Load and set annotations from events.tsv
        # ---------------------------------------------------------------------
        # Construct events.tsv path from BIDS file path
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        # Replace eeg extension with events.tsv
        base_name = file_name.split("_eeg")[0]
        events_file = os.path.join(file_dir, f"{base_name}_events.tsv")
        
        annotations = _parse_events_tsv(events_file)
        if annotations is not None:
            raw.set_annotations(annotations, verbose=False)
        
        # ---------------------------------------------------------------------
        # 10. Create derived misc channels from participants.tsv
        # ---------------------------------------------------------------------
        # madrs_change = madrs_bl - madrs_fu
        madrs_change = _compute_madrs_change(participants_info)
        if madrs_change is not None:
            raw = _add_misc_channel(raw, "madrs_change", madrs_change)
        
        # ---------------------------------------------------------------------
        # 11. Set event IDs for events_from_annotations compatibility
        # ---------------------------------------------------------------------
        # Store event mapping in info for downstream use
        if "temp" not in raw.info:
            raw.info["temp"] = {}
        raw.info["temp"]["event_id_map"] = _EVENT_ID_MAP
        
        return raw


KERNEL = OpenNeuroDS001784Kernel()