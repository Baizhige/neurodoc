"""openneuro_ds007176 stage1 kernel for EEGUnity.

Longitudinal resting-state EEG dataset with 43 subjects recorded across
multiple sessions over two years. Continuous EEG without experimental events.

Source: https://openneuro.org/datasets/ds007176
        DOI: 10.1016/j.bspc.2026.109484
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Source: OpenNeuro ds007176 dataset_description.json
# EEG amplifier information not explicitly stated in sidecars.
# Annotator: LLM, 2026-04-10
# inferred by LLM, needs human review
_AMPLIFIER_DEFAULT = "unknown"

# Source: Based on 60-channel setup typical for resting-state EEG studies.
# Annotator: LLM, 2026-04-10
# inferred by LLM, needs human review
_CAP_DEFAULT = "Ag/AgCl"

# Source: Dataset README indicates standard EEG cap without specific model.
# Annotator: LLM, 2026-04-10
# inferred by LLM, needs human review
_HANDEDNESS_MISSING_REASON = "Not collected in original study protocol"


@dataclass
class OpenNeuroDs007176Kernel:
    """Stage1 kernel for openneuro_ds007176 dataset."""

    KERNEL_ID: str = "openneuro-ds007176-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", "")

        # Extract subject_id from file path or row
        subject_id = row.get("subject_id", "")
        if not subject_id and file_path:
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("sub-"):
                    subject_id = part.split("_")[0].replace("sub-", "")
                    break

        # Read participants.tsv for subject metadata
        subject_info = self._get_subject_info(dataset_root, subject_id)

        # Get original description or empty string
        original_description = raw.info.get("description", "")

        # Build eegunity_description
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER_DEFAULT,
            "cap": _CAP_DEFAULT,
            "handedness": subject_info.get("handedness", "unknown"),
        }

        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names if needed
        raw = self._standardize_channels(raw)

        # Set standard 10-20 montage
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass  # Proceed without montage if standard montage fails

        # There are no meaningful experimental events in this dataset.
        # Event code 0 appears 2 times as a null trigger marker.
        # Source: analysis.md Event Structure table
        # The data is continuous resting-state; downstream tasks should
        # use epoch_by_segmentation_hdf5 for reliability analysis.

        return raw

    def _get_subject_info(
        self, dataset_root: str, subject_id: str
    ) -> Dict[str, str]:
        """Extract subject metadata from participants.tsv.

        Parameters
        ----------
        dataset_root
            Root directory of the dataset.
        subject_id
            Subject identifier (e.g., "001").

        Returns
        -------
        Dict[str, str]
            Dictionary with age, sex, handedness fields.
        """
        info: Dict[str, str] = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        if not dataset_root:
            return info

        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        if not os.path.exists(participants_tsv):
            return info

        try:
            df = pd.read_csv(participants_tsv, sep="\t")
        except Exception:
            return info

        # Normalize subject_id column names
        # BIDS may use participant_id or subject_id
        subject_col = None
        for col in ["participant_id", "subject_id", "participant id"]:
            if col in df.columns:
                subject_col = col
                break

        if subject_col is None:
            return info

        # Find the row for this subject
        subject_patterns = [f"sub-{subject_id}", subject_id]
        mask = df[subject_col].astype(str).isin(subject_patterns)
        if not mask.any():
            # Try partial match
            for pattern in subject_patterns:
                if df[subject_col].astype(str).str.contains(pattern).any():
                    mask = df[subject_col].astype(str).str.contains(pattern)
                    break

        if not mask.any():
            return info

        row = df[mask].iloc[0]

        # Extract age
        if "age" in df.columns:
            age_val = row.get("age")
            if age_val is not None and str(age_val).strip():
                info["age"] = str(age_val).strip()
            else:
                info["age"] = "unknown"
        elif "Age" in df.columns:
            age_val = row.get("Age")
            if age_val is not None and str(age_val).strip():
                info["age"] = str(age_val).strip()

        # Extract sex/gender
        sex_col = None
        for col in ["sex", "gender", "Sex", "Gender"]:
            if col in df.columns:
                sex_col = col
                break

        if sex_col:
            sex_val = str(row.get(sex_col, "")).strip().lower()
            if sex_val in ["m", "male"]:
                info["sex"] = "male"
            elif sex_val in ["f", "female"]:
                info["sex"] = "female"
            else:
                info["sex"] = "unknown"
        else:
            info["sex"] = "unknown"

        # Extract handedness
        for col in ["handedness", "hand", "dominant_hand"]:
            if col in df.columns:
                handedness_val = str(row.get(col, "")).strip().lower()
                if handedness_val in ["r", "right"]:
                    info["handedness"] = "right"
                elif handedness_val in ["l", "left"]:
                    info["handedness"] = "left"
                elif handedness_val:
                    info["handedness"] = handedness_val
                break

        return info

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Standardize channel names to 10-20 system if needed.

        Parameters
        ----------
        raw
            Input Raw object.

        Returns
        -------
        mne.io.BaseRaw
            Raw with standardized channel names.
        """
        ch_names = raw.ch_names
        rename_map: Dict[str, str] = {}

        # Common channel aliases for 60-channel setups
        # Based on standard 10-20 extended layouts
        alias_patterns = [
            # Standard 10-20 names that might have EEG prefix
            ("Fp1", ["EEG Fp1", "Fp1", "fp1", "EEG-Fp1"]),
            ("Fp2", ["EEG Fp2", "Fp2", "fp2", "EEG-Fp2"]),
            ("F7", ["EEG F7", "F7", "f7"]),
            ("F3", ["EEG F3", "F3", "f3"]),
            ("Fz", ["EEG Fz", "Fz", "fz"]),
            ("F4", ["EEG F4", "F4", "f4"]),
            ("F8", ["EEG F8", "F8", "f8"]),
            ("T7", ["EEG T7", "T7", "t7", "T3"]),
            ("C3", ["EEG C3", "C3", "c3"]),
            ("Cz", ["EEG Cz", "Cz", "cz"]),
            ("C4", ["EEG C4", "C4", "c4"]),
            ("T8", ["EEG T8", "T8", "t8", "T4"]),
            ("P7", ["EEG P7", "P7", "p7"]),
            ("P3", ["EEG P3", "P3", "p3"]),
            ("Pz", ["EEG Pz", "Pz", "pz"]),
            ("P4", ["EEG P4", "P4", "p4"]),
            ("P8", ["EEG P8", "P8", "p8"]),
            ("O1", ["EEG O1", "O1", "o1"]),
            ("Oz", ["EEG Oz", "Oz", "oz"]),
            ("O2", ["EEG O2", "O2", "o2"]),
            # Additional extended 10-20 channels
            ("AF7", ["EEG AF7", "AF7"]),
            ("AF3", ["EEG AF3", "AF3"]),
            ("AF4", ["EEG AF4", "AF4"]),
            ("AF8", ["EEG AF8", "AF8"]),
            ("F1", ["EEG F1", "F1"]),
            ("F2", ["EEG F2", "F2"]),
            ("F5", ["EEG F5", "F5"]),
            ("F6", ["EEG F6", "F6"]),
            ("FC5", ["EEG FC5", "FC5"]),
            ("FC1", ["EEG FC1", "FC1"]),
            ("FC2", ["EEG FC2", "FC2"]),
            ("FC6", ["EEG FC6", "FC6"]),
            ("C1", ["EEG C1", "C1"]),
            ("C2", ["EEG C2", "C2"]),
            ("C5", ["EEG C5", "C5"]),
            ("C6", ["EEG C6", "C6"]),
            ("CP5", ["EEG CP5", "CP5"]),
            ("CP1", ["EEG CP1", "CP1"]),
            ("CP2", ["EEG CP2", "CP2"]),
            ("CP6", ["EEG CP6", "CP6"]),
            ("P1", ["EEG P1", "P1"]),
            ("P2", ["EEG P2", "P2"]),
            ("P5", ["EEG P5", "P5"]),
            ("P6", ["EEG P6", "P6"]),
            ("PO3", ["EEG PO3", "PO3"]),
            ("PO4", ["EEG PO4", "PO4"]),
            ("PO7", ["EEG PO7", "PO7"]),
            ("PO8", ["EEG PO8", "PO8"]),
            # Common EOG/ECG/Misc channels
            ("EOG-left", ["EOG L", "EOGL", "EOG_L", "EOG-Left"]),
            ("EOG-right", ["EOG R", "EOGR", "EOG_R", "EOG-Right"]),
            ("EOG-upper", ["EOG U", "EOGU", "EOG_U"]),
            ("ECG", ["ECG", "EKG"]),
        ]

        existing_names = set(ch_names)

        for target_name, aliases in alias_patterns:
            for source_name in aliases:
                if source_name in existing_names and source_name != target_name:
                    rename_map[source_name] = target_name
                    break

        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip renaming if it fails

        return raw


KERNEL = OpenNeuroDs007176Kernel()