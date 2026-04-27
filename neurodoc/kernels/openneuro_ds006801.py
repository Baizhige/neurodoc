"""OpenNeuro DS006801 stage1 kernel for EEGUnity.

Resting-state EEG before and after different study methods.
21 subjects, 42 files (pre/post intervention sessions).
31 channels at 500 Hz.

Source: https://openneuro.org/datasets/ds006801
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import pandas as pd


# LLM 推断，需人类复核
# Source: Dataset documentation / paper indicates standard 32-channel EEG cap
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# age/sex will be populated from participants.tsv at runtime


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from the BIDS dataset root."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row, participants_df: Optional[pd.DataFrame]) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or use defaults."""
    subject_id = row.get("Subject", row.get("subject_id", "unknown"))
    
    # Initialize with defaults
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    if participants_df is not None and not participants_df.empty:
        # Try to find the subject in participants.tsv
        # BIDS format: participant_id column with "sub-XX" values
        subj_col = "participant_id"
        if subj_col in participants_df.columns:
            # Match against subject_id format
            subject_row = participants_df[
                participants_df[subj_col].str.contains(
                    subject_id.replace("sub-", ""), na=False
                )
            ]
            if not subject_row.empty:
                row_data = subject_row.iloc[0]
                if "age" in row_data.index and pd.notna(row_data["age"]):
                    subject_info["age"] = str(int(row_data["age"]))
                if "sex" in row_data.index and pd.notna(row_data["sex"]):
                    sex_val = str(row_data["sex"]).lower()
                    if sex_val in ["m", "male", "f", "female"]:
                        subject_info["sex"] = "male" if sex_val in ["m", "male"] else "female"
                if "handedness" in row_data.index and pd.notna(row_data["handedness"]):
                    handedness = str(row_data["handedness"]).lower()
                    if handedness in ["r", "right", "l", "left"]:
                        subject_info["handedness"] = "right" if handedness in ["r", "right"] else "left"
    
    return subject_info


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    Source: Standard 10-20 system electrode naming convention
    Annotator: LLM, 2026-04-08 - 需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Standard 10-20 channel naming patterns
    # Common aliases that may appear in EEG data
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "fp1", "Fp 1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "fp2", "Fp 2"]),
        ("F7", ["F7", "EEG-F7", "f7", "F 7"]),
        ("F3", ["F3", "EEG-F3", "f3", "F 3"]),
        ("Fz", ["Fz", "EEG-Fz", "fz", "F z"]),
        ("F4", ["F4", "EEG-F4", "f4", "F 4"]),
        ("F8", ["F8", "EEG-F8", "f8", "F 8"]),
        ("T7", ["T7", "EEG-T7", "t7", "T 7", "T3", "T 3"]),
        ("C3", ["C3", "EEG-C3", "c3", "C 3"]),
        ("Cz", ["Cz", "EEG-Cz", "cz", "C z"]),
        ("C4", ["C4", "EEG-C4", "c4", "C 4"]),
        ("T8", ["T8", "EEG-T8", "t8", "T 8", "T4", "T 4"]),
        ("P7", ["P7", "EEG-P7", "p7", "P 7"]),
        ("P3", ["P3", "EEG-P3", "p3", "P 3"]),
        ("Pz", ["Pz", "EEG-Pz", "pz", "P z"]),
        ("P4", ["P4", "EEG-P4", "p4", "P 4"]),
        ("P8", ["P8", "EEG-P8", "p8", "P 8"]),
        ("O1", ["O1", "EEG-O1", "o1", "O 1"]),
        ("Oz", ["Oz", "EEG-Oz", "oz", "O z"]),
        ("O2", ["O2", "EEG-O2", "o2", "O 2"]),
        ("FC1", ["FC1", "EEG-FC1", "fc1"]),
        ("FC2", ["FC2", "EEG-FC2", "fc2"]),
        ("FC5", ["FC5", "EEG-FC5", "fc5"]),
        ("FC6", ["FC6", "EEG-FC6", "fc6"]),
        ("CP1", ["CP1", "EEG-CP1", "cp1"]),
        ("CP2", ["CP2", "EEG-CP2", "cp2"]),
        ("CP5", ["CP5", "EEG-CP5", "cp5"]),
        ("CP6", ["CP6", "EEG-CP6", "cp6"]),
        ("PO1", ["PO1", "EEG-PO1", "po1"]),
        ("PO2", ["PO2", "EEG-PO2", "po2"]),
        ("AF7", ["AF7", "EEG-AF7", "af7"]),
        ("AF8", ["AF8", "EEG-AF8", "af8"]),
        ("AFz", ["AFz", "EEG-AFz", "afz"]),
        ("FT7", ["FT7", "EEG-FT7", "ft7"]),
        ("FT8", ["FT8", "EEG-FT8", "ft8"]),
        ("TP7", ["TP7", "EEG-TP7", "tp7"]),
        ("TP8", ["TP8", "EEG-TP8", "tp8"]),
        ("POz", ["POz", "EEG-POz", "poz"]),
        ("F1", ["F1", "EEG-F1", "f1"]),
        ("F2", ["F2", "EEG-F2", "f2"]),
        ("F5", ["F5", "EEG-F5", "f5"]),
        ("F6", ["F6", "EEG-F6", "f6"]),
        ("C1", ["C1", "EEG-C1", "c1"]),
        ("C2", ["C2", "EEG-C2", "c2"]),
        ("C5", ["C5", "EEG-C5", "c5"]),
        ("C6", ["C6", "EEG-C6", "c6"]),
        ("P1", ["P1", "EEG-P1", "p1"]),
        ("P2", ["P2", "EEG-P2", "p2"]),
        ("P5", ["P5", "EEG-P5", "p5"]),
        ("P6", ["P6", "EEG-P6", "p6"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _is_admin_event(description: str) -> bool:
    """Check if an event is an admin marker to be excluded from analysis."""
    admin_markers = [
        "New Segment",
        "LostSamples",
        "Boundary",
        "boundary",
        "admin",
    ]
    return any(marker.lower() in description.lower() for marker in admin_markers)


class OpenNeuroDS006801Kernel:
    """Stage1 kernel for OpenNeuro DS006801 dataset."""

    KERNEL_ID: str = "openneuro-ds006801-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file path information

        Returns
        -------
        mne.io.BaseRaw
        """
        # Get dataset path from udataset or row
        file_path = row.get("File Path", row.get("file_path", ""))
        dataset_path = getattr(udataset, "path", os.path.dirname(file_path) or ".")

        # Load participants.tsv for subject metadata
        participants_df = _load_participants_tsv(dataset_path)

        # Get subject info
        subject_info = _get_subject_info(row, participants_df)

        # Update description with eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "unknown",  # LLM 推断，需人类复核 - 需从数据集文档确认
                "cap": "unknown",  # LLM 推断，需人类复核 - 需从数据集文档确认
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[DS006801] Renaming {len(rename_map)} channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Set standard montage if possible (10-20 system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only use channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 20:  # At least 20 matching channels
                raw.set_montage(montage, on_missing="ignore")
            else:
                print(f"[DS006801] Warning: Only {len(common_channels)} channels match standard montage")
        except Exception as e:
            print(f"[DS006801] Warning: Could not set montage: {e}")

        # Process annotations - keep only meaningful events, mark admin events
        if raw.annotations is not None and len(raw.annotations) > 0:
            new_descriptions = []
            for desc in raw.annotations.description:
                if _is_admin_event(desc):
                    new_descriptions.append("admin: " + desc)
                else:
                    new_descriptions.append(desc)
            
            # Update annotations with marked admin events
            if new_descriptions != list(raw.annotations.description):
                raw.annotations.description = new_descriptions

        return raw


KERNEL = OpenNeuroDS006801Kernel()