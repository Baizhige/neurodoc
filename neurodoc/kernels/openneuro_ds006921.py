"""OpenNeuro ds006921 stage1 kernel for EEGUnity.

Dataset: High-Density Resting-State EEG of Phantom Limb Pain and Controls
Format: BIDS (BrainVision .eeg/.vhdr/.vmrk, EDF, or SET files)
Channels: 128
Sampling Rate: 2400 Hz
Subjects: 152 (38 with complete metadata for core tasks)
Source: https://openneuro.org/datasets/ds006921
DOI: 10.18112/openneuro.ds006921.v1.1.1

Notes:
- BIDS-compliant dataset with participants.tsv and optional events.tsv sidecars.
- Resting-state recordings: eyes-open and eyes-closed conditions.
- 128-channel high-density EEG; channel names may need standardization.
- No native event markers in continuous resting-state data.
- Required info fields from participants.tsv: Age, AmputationLevel, AmputationSide,
  Amputee, HandLateralization, Pain, Sex.
- Derived misc channels: group_label (3-class from Amputee+Pain), reconstruction_error
  (self-supervised placeholder).
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Dataset-specific constants
# ---------------------------------------------------------------------------

# Source: OpenNeuro ds006921 dataset, 128-channel layout
# https://openneuro.org/datasets/ds006921
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_DS006921_CHANNEL_NAMES_128 = [
    "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz",
    # Extended 128-channel coverage (lower density or additional rows)
    "F9", "F10", "P9", "P10",
    "PO9", "PO10",
    "O9", "O10",
    # Additional channels common in 128-channel systems (e.g., EGI geodesic)
    "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10",
    "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20",
    "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30",
    "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40",
    "E41", "E42", "E43", "E44", "E45", "E46", "E47", "E48", "E49", "E50",
    "E51", "E52", "E53", "E54", "E55", "E56", "E57", "E58", "E59", "E60",
    "E61", "E62", "E63", "E64", "E65", "E66", "E67", "E68", "E69", "E70",
    "E71", "E72", "E73", "E74", "E75", "E76", "E77", "E78", "E79", "E80",
    "E81", "E82", "E83", "E84", "E85", "E86", "E87", "E88", "E89", "E90",
    "E91", "E92", "E93", "E94", "E95", "E96", "E97", "E98", "E99", "E100",
    "E101", "E102", "E103", "E104", "E105", "E106", "E107", "E108", "E109", "E110",
    "E111", "E112", "E113", "E114", "E115", "E116", "E117", "E118", "E119", "E120",
    "E121", "E122", "E123", "E124", "E125", "E126", "E127", "E128",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> dict[str, str]:
    """Build rename map for ds006921 128-channel files.
    
    Maps common non-standard naming conventions to standard 10-20/10-10 names.
    """
    rename_map: dict[str, str] = {}
    existing_names = list(raw.ch_names)
    
    # Common patterns in high-density EEG systems
    for i, target_name in enumerate(_DS006921_CHANNEL_NAMES_128):
        # Numbered EEG channels (EEG-0, EEG-1, etc. or EEG 1, EEG 2, etc.)
        candidates = [
            f"EEG-{i}",
            f"EEG {i}",
            f"EEG_{i}",
            f"Ch{i+1}",
            f"ch{i+1}",
            f"Channel{i+1}",
            f"channel{i+1}",
            f"{i+1}",
            f"E{i+1}",  # EGI style
        ]
        for candidate in candidates:
            if candidate in existing_names and candidate != target_name:
                rename_map[candidate] = target_name
                break
    
    # Handle EGI geodesic net naming (E1, E2, ... already in list above)
    # But also handle zero-padded variants
    for i in range(1, 129):
        padded = f"E{i:03d}"
        unpadded = f"E{i}"
        target = f"E{i}"
        if padded in existing_names and target in _DS006921_CHANNEL_NAMES_128:
            if padded != target:
                rename_map[padded] = target
    
    # Standard 10-20 aliases with prefixes/suffixes
    standard_aliases = {
        "Fp1": ["Fp1", "FP1", "Fp1."],
        "Fpz": ["Fpz", "FPz", "Fpz."],
        "Fp2": ["Fp2", "FP2", "Fp2."],
        "AF7": ["AF7", "AF7."],
        "AF3": ["AF3", "AF3."],
        "AFz": ["AFz", "AFz."],
        "AF4": ["AF4", "AF4."],
        "AF8": ["AF8", "AF8."],
        "F7": ["F7", "F7."],
        "F5": ["F5", "F5."],
        "F3": ["F3", "F3."],
        "F1": ["F1", "F1."],
        "Fz": ["Fz", "Fz."],
        "F2": ["F2", "F2."],
        "F4": ["F4", "F4."],
        "F6": ["F6", "F6."],
        "F8": ["F8", "F8."],
        "FT7": ["FT7", "FT7."],
        "FC5": ["FC5", "FC5."],
        "FC3": ["FC3", "FC3."],
        "FC1": ["FC1", "FC1."],
        "FCz": ["FCz", "FCz."],
        "FC2": ["FC2", "FC2."],
        "FC4": ["FC4", "FC4."],
        "FC6": ["FC6", "FC6."],
        "FT8": ["FT8", "FT8."],
        "T7": ["T7", "T7.", "T3"],
        "C5": ["C5", "C5."],
        "C3": ["C3", "C3."],
        "C1": ["C1", "C1."],
        "Cz": ["Cz", "Cz.", "CZ"],
        "C2": ["C2", "C2."],
        "C4": ["C4", "C4."],
        "C6": ["C6", "C6."],
        "T8": ["T8", "T8.", "T4"],
        "TP7": ["TP7", "TP7."],
        "CP5": ["CP5", "CP5."],
        "CP3": ["CP3", "CP3."],
        "CP1": ["CP1", "CP1."],
        "CPz": ["CPz", "CPz."],
        "CP2": ["CP2", "CP2."],
        "CP4": ["CP4", "CP4."],
        "CP6": ["CP6", "CP6."],
        "TP8": ["TP8", "TP8."],
        "P7": ["P7", "P7.", "T5"],
        "P5": ["P5", "P5."],
        "P3": ["P3", "P3."],
        "P1": ["P1", "P1."],
        "Pz": ["Pz", "Pz.", "PZ"],
        "P2": ["P2", "P2."],
        "P4": ["P4", "P4."],
        "P6": ["P6", "P6."],
        "P8": ["P8", "P8.", "T6"],
        "PO7": ["PO7", "PO7."],
        "PO3": ["PO3", "PO3."],
        "POz": ["POz", "POz."],
        "PO4": ["PO4", "PO4."],
        "PO8": ["PO8", "PO8."],
        "O1": ["O1", "O1."],
        "Oz": ["Oz", "Oz.", "OZ"],
        "O2": ["O2", "O2."],
        "Iz": ["Iz", "Iz."],
    }
    
    for target_name, aliases in standard_aliases.items():
        for candidate in aliases:
            if candidate in existing_names and candidate != target_name:
                if target_name not in existing_names:
                    rename_map[candidate] = target_name
                    break
    
    return rename_map


def _get_participants_info(dataset_path: str, subject_id: str) -> dict[str, str]:
    """Read participants.tsv and extract info for given subject.
    
    Returns dict with all required fields, using "unknown" for missing values.
    """
    required_fields = [
        "Age", "AmputationLevel", "AmputationSide", "Amputee",
        "HandLateralization", "Pain", "Sex"
    ]
    
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {field: "unknown" for field in required_fields}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {field: "unknown" for field in required_fields}
    
    # Find row for this subject
    sub_col = None
    for col in df.columns:
        if col.lower() in ["participant_id", "subject", "subject_id", "participant"]:
            sub_col = col
            break
    
    if sub_col is None:
        sub_col = df.columns[0]
    
    # Normalize subject ID for matching
    search_ids = [subject_id]
    if subject_id.startswith("sub-"):
        search_ids.append(subject_id[4:])
    else:
        search_ids.append(f"sub-{subject_id}")
    
    row_mask = df[sub_col].astype(str).isin(search_ids)
    if not row_mask.any():
        return {field: "unknown" for field in required_fields}
    
    sub_row = df[row_mask].iloc[0]
    
    result = {}
    for field in required_fields:
        if field in sub_row.index:
            val = sub_row[field]
            result[field] = str(val) if pd.notna(val) else "unknown"
        else:
            result[field] = "unknown"
    
    return result


def _derive_group_label(participants_info: dict[str, str]) -> str:
    """Derive 3-class group label from Amputee and Pain fields."""
    amputee = participants_info.get("Amputee", "").lower()
    pain = participants_info.get("Pain", "").lower()
    
    if amputee in ("yes", "true", "1"):
        if pain in ("yes", "true", "1"):
            return "amputee_pain"
        else:
            return "amputee_no_pain"
    else:
        return "control"


class OpenNeuroDS006921Kernel:
    """EEGUnity stage1 kernel for OpenNeuro ds006921."""
    
    KERNEL_ID = "openneuro_ds006921"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_path = udataset.root if hasattr(udataset, "root") else str(udataset)
        subject_id = str(row.get("subject", row.get("participant_id", "unknown")))
        
        # Get participants info
        participants_info = _get_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": participants_info.get("Age", "unknown"),
            "sex": participants_info.get("Sex", "unknown"),
            "amplifier": "unknown",
            "cap": "128-channel",
            "handedness": participants_info.get("HandLateralization", "unknown"),
        }
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Add derived misc channels
        group_label = _derive_group_label(participants_info)
        
        # Create group_label misc channel (constant broadcast)
        group_label_numeric = 0.0  # control
        if group_label == "amputee_no_pain":
            group_label_numeric = 1.0
        elif group_label == "amputee_pain":
            group_label_numeric = 2.0
        
        group_data = np.full((1, len(raw.times)), group_label_numeric)
        group_info = mne.create_info(["group_label"], raw.info["sfreq"], ["misc"])
        group_raw = mne.io.RawArray(group_data, group_info)
        raw.add_channels([group_raw], force_update_info=True)
        
        # Create reconstruction_error misc channel (placeholder constant)
        recon_data = np.zeros((1, len(raw.times)))
        recon_info = mne.create_info(["reconstruction_error"], raw.info["sfreq"], ["misc"])
        recon_raw = mne.io.RawArray(recon_data, recon_info)
        raw.add_channels([recon_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS006921Kernel()