"""OpenNeuro ds007020 stage1 kernel for EEGUnity.

Parkinson's Disease EEG dataset for 3-year mortality classification.
Resting-state EEG (eyes open) from 94 PD patients.

Source: https://openneuro.org/datasets/ds007020
Paper: DOI 10.1016/j.prdoa.2025.100409

Extends the generic BIDS kernel with:
- Mortality label extraction (deceased/living) from participants.tsv
- Channel standardization for 64-channel 10-20 system
- Super meta construction for mortality classification task
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Paper DOI 10.1016/j.prdoa.2025.100409 - "94 PD patients (22 deceased, 72 living)"
# Age range: typical PD population, paper mentions mean age but exact values in participants.tsv
# inferred by LLM, needs human review
_AMPLIFIER = "unknown"
_CAP = "Ag/AgCl"  # inferred by LLM, needs human review

# Standard 10-20 system 64-channel names (excluding VEOG/HEOG for standard set)
# Based on 63 EEG channels mentioned in analysis.md
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC7", "FC3", "FCz", "FC4", "FC8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "Poz", "PO4", "PO8",
    "O1", "Oz", "O2",
    # Additional 10-20 positions
    "AF7", "AF3", "AF4", "AF8",
    "FT7", "FT8",
    "TP9", "TP10",
    "PO9", "PO10",
    "I1", "I2",
    "AFz", "F1", "F2",
    "FC1", "FC2",
    "C1", "C2",
    "CP1", "CP2",
    "P1", "P2",
    "PO5", "PO6",
    "I1", "I2",
    # Extra if needed
    "T9", "T10",
    "P9", "P10",
]

# Common alternative naming patterns in BrainVision data
_ALIAS_GROUPS = [
    ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1"]),
    ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2"]),
    ("Fz", ["Fz", "EEG Fz", "EEG-Fz"]),
    ("F3", ["F3", "EEG F3", "EEG-F3"]),
    ("F4", ["F4", "EEG F4", "EEG-F4"]),
    ("F7", ["F7", "EEG F7", "EEG-F7"]),
    ("F8", ["F8", "EEG F8", "EEG-F8"]),
    ("T7", ["T7", "T7", "EEG T7", "EEG-T7", "TP7"]),
    ("T8", ["T8", "T8", "EEG T8", "EEG-T8", "TP8"]),
    ("C3", ["C3", "EEG C3", "EEG-C3"]),
    ("C4", ["C4", "EEG C4", "EEG-C4"]),
    ("Cz", ["Cz", "EEG Cz", "EEG-Cz"]),
    ("Pz", ["Pz", "EEG Pz", "EEG-Pz"]),
    ("P3", ["P3", "EEG P3", "EEG-P3"]),
    ("P4", ["P4", "EEG P4", "EEG-P4"]),
    ("P7", ["P7", "EEG P7", "EEG-P7"]),
    ("P8", ["P8", "EEG P8", "EEG-P8"]),
    ("O1", ["O1", "EEG O1", "EEG-O1"]),
    ("O2", ["O2", "EEG O2", "EEG-O2"]),
    ("Oz", ["Oz", "EEG Oz", "EEG-Oz"]),
    ("FCz", ["FCz", "EEG FCz", "EEG-FCz"]),
    ("FC3", ["FC3", "EEG FC3", "EEG-FC3"]),
    ("FC4", ["FC4", "EEG FC4", "EEG-FC4"]),
    ("CPz", ["CPz", "EEG CPz", "EEG-CPz"]),
    ("CP3", ["CP3", "EEG CP3", "EEG-CP3"]),
    ("CP4", ["CP4", "EEG CP4", "EEG-CP4"]),
    ("POz", ["POz", "EEG POz", "EEG-POz"]),
    ("PO3", ["PO3", "EEG PO3", "EEG-PO3"]),
    ("PO4", ["PO4", "EEG PO4", "EEG-PO4"]),
    ("Fpz", ["Fpz", "Fpz", "EEG Fpz", "EEG-Fpz"]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to 10-20 standard names.
    
    Source: Standard 10-20 electrode naming convention
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in _ALIAS_GROUPS:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    # Handle numeric EEG-XX patterns
    for ch_name in existing_names:
        if ch_name.startswith("EEG-") or ch_name.startswith("EEG "):
            # Try to extract position number
            num_str = ch_name.replace("EEG-", "").replace("EEG ", "")
            if num_str.isdigit():
                idx = int(num_str)
                # Map based on common BrainVision 64-channel order
                standard_order = _STANDARD_64_CHANNELS
                if idx < len(standard_order):
                    rename_map[ch_name] = standard_order[idx]
    
    return rename_map


def _load_participants_metadata(dataset_path: str) -> pd.DataFrame:
    """Load and parse participants.tsv for subject metadata.
    
    Source: BIDS format participants.tsv
    Annotator: LLM, 2026-04-08
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    
    if not os.path.exists(participants_file):
        return pd.DataFrame()
    
    df = pd.read_csv(participants_file, sep="\t")
    return df


def _extract_subject_info(row: pd.Series, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv row.
    
    Source: participants.tsv columns
    Annotator: LLM, 2026-04-08
    """
    info: Dict[str, str] = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    # Map common column names
    age_cols = ["age", "subject_age", "Age"]
    sex_cols = ["sex", "gender", "Subject Sex", "Sex"]
    handedness_cols = ["handedness", "hand", "Handedness"]
    
    for col in age_cols:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip()
            if val and val.lower() not in ["n/a", "na", "unknown"]:
                info["age"] = val
                break
    
    for col in sex_cols:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip().lower()
            if val in ["m", "male", "f", "female"]:
                info["sex"] = "male" if val in ["m", "male"] else "female"
                break
    
    for col in handedness_cols:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip().lower()
            if val in ["r", "right", "l", "left", "a", "ambidextrous"]:
                if val in ["r", "right"]:
                    info["handedness"] = "right"
                elif val in ["l", "left"]:
                    info["handedness"] = "left"
                break
    
    return info


def _get_mortality_label(row: pd.Series, subject_id: str) -> Optional[str]:
    """Extract mortality label from participants.tsv for super meta.
    
    Mortality labels (deceased/living) are derived from clinical follow-up metadata.
    Source: participants.tsv (3-year mortality outcome column)
    Annotator: LLM, 2026-04-08
    inferred by LLM, needs human review
    """
    # Common column names for mortality/outcome
    outcome_cols = [
        "mortality", "deceased", "death", "outcome", "status",
        "mortality_3yr", "deceased_3yr", "mortality_status",
        "3_year_mortality", "mortality_outcome"
    ]
    
    for col in outcome_cols:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip().lower()
            if val in ["deceased", "dead", "1", "yes", "died"]:
                return "deceased"
            elif val in ["living", "alive", "0", "no", "survived"]:
                return "living"
    
    return None


def _create_super_meta_annotations(
    raw: mne.io.BaseRaw,
    subject_id: str,
    mortality_label: Optional[str]
) -> mne.Annotations:
    """Create super meta annotations for mortality classification.
    
    Annotator: LLM, 2026-04-08
    inferred by LLM, needs human review
    """
    # If we have mortality label, create annotation for entire recording
    if mortality_label is not None:
        onset = 0.0
        duration = raw.times[-1]  # Entire recording duration
        description = f"mortality:{mortality_label}"
        
        return mne.Annotations(
            onset=[onset],
            duration=[duration],
            description=[description],
        )
    
    return mne.Annotations([], [], [])  # Empty annotations if no label


class OpenNeuroDS007020Kernel:
    """Stage1 kernel for OpenNeuro ds007020 - PD Mortality EEG Dataset."""

    KERNEL_ID: str = "openneuro-ds007020-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file and subject information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata
        """
        # Extract subject ID from row
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
        
        # Get dataset path for participants.tsv
        file_path = row.get("File Path", "")
        dataset_path = udataset.path if hasattr(udataset, 'path') else os.path.dirname(file_path)
        
        # Load participants metadata
        participants_df = _load_participants_metadata(dataset_path)
        
        # Find subject row
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
        mortality_label = None
        
        if not participants_df.empty:
            # Try to find subject by various ID column names
            id_cols = ["participant_id", "subject_id", "participant", "subject"]
            subject_row = None
            
            for col in id_cols:
                if col in participants_df.columns:
                    mask = participants_df[col].astype(str).str.contains(
                        subject_id.replace("sub-", ""), case=False, na=False
                    )
                    if mask.any():
                        subject_row = participants_df[mask].iloc[0]
                        break
            
            if subject_row is not None:
                subject_info = _extract_subject_info(subject_row, subject_id)
                mortality_label = _get_mortality_label(subject_row, subject_id)

        # Build channel rename map and apply
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if channels don't match

        # Remove "New Segment/" annotations (admin marker)
        original_annotations = raw.annotations
        if len(original_annotations) > 0:
            mask = ~np.array([
                "New Segment" in desc or "new segment" in desc.lower()
                for desc in original_annotations.description
            ])
            if not mask.all():  # If there are non-admin annotations
                raw.set_annotations(
                    original_annotations[mask]
                )

        # Create description dict with eegunity metadata
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            }
        }
        raw.info["description"] = json.dumps(description_dict)

        # Add super meta annotations for mortality classification
        if mortality_label is not None:
            super_annotations = _create_super_meta_annotations(
                raw, subject_id, mortality_label
            )
            
            # Merge with existing annotations
            if len(raw.annotations) > 0:
                merged_onset = list(raw.annotations.onset) + list(super_annotations.onset)
                merged_duration = list(raw.annotations.duration) + list(super_annotations.duration)
                merged_description = list(raw.annotations.description) + list(super_annotations.description)
                raw.set_annotations(
                    mne.Annotations(
                        onset=merged_onset,
                        duration=merged_duration,
                        description=merged_description,
                    )
                )
            else:
                raw.set_annotations(super_annotations)

        return raw


KERNEL = OpenNeuroDS007020Kernel()