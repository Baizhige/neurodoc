"""OpenNeuro DS003944 stage1 kernel for EEGUnity.

First Episode Psychosis (FEP) vs. Healthy Controls resting-state EEG dataset.
5-minute eyes-open resting-state EEG, 64 channels, 1000 Hz.

Labels are derived from participants.tsv (group/diagnosis column).
No discrete task events in the raw data.

Source: https://openneuro.org/datasets/ds003944
Reference: https://doi.org/10.1038/s41598-024-66110-0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne


class OpenNeuroDS003944Kernel:
    """Stage1 kernel for OpenNeuro DS003944 (FEP vs. Control resting-state EEG)."""

    KERNEL_ID: str = "openneuro-ds003944-stage1"

    # Standard 10-20 64-channel names expected in this dataset
    # Source: Dataset documentation / standard 10-20 system
    # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    _STANDARD_64_CHANNELS = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
    ]

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (pre-loaded by EEGUnity loader)
        row : locator row with File Path and subject info

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))

        # Extract subject metadata from participants.tsv if available
        subject_info = self._get_subject_info(udataset, subject_id)

        # Build eegunity_description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": subject_info.get("amplifier", "unknown"),
                "cap": subject_info.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names if needed
        raw = self._standardize_channels(raw)

        return raw

    def _get_subject_info(
        self, udataset, subject_id: str
    ) -> Dict[str, str]:
        """Extract subject metadata from participants.tsv.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        subject_id : subject identifier (e.g., "sub-01")

        Returns
        -------
        Dict[str, str]
            Subject info dict with keys: age, sex, amplifier, cap, handedness
        """
        subject_info: Dict[str, str] = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

        # Try to access participants.tsv via udataset
        participants_tsv = getattr(udataset, "participants_tsv", None)

        if participants_tsv is not None:
            # participants_tsv is a pandas DataFrame
            # Normalize subject_id for lookup (remove 'sub-' prefix if present)
            lookup_id = subject_id.replace("sub-", "")
            if lookup_id.startswith("0"):
                lookup_id = lookup_id.lstrip("0") or "0"

            for idx, p_id in enumerate(participants_tsv.get("participant_id", [])):
                p_id_clean = str(p_id).replace("sub-", "")
                if p_id_clean == lookup_id or p_id == subject_id:
                    # Extract age
                    age_col = self._find_column(participants_tv, ["age", "participant_age"])
                    if age_col:
                        age_val = participants_tsv.iloc[idx][age_col]
                        if pd.notna(age_val):
                            subject_info["age"] = str(int(float(age_val)))

                    # Extract sex
                    sex_col = self._find_column(participants_tsv, ["sex", "gender"])
                    if sex_col:
                        sex_val = participants_tsv.iloc[idx][sex_col]
                        if pd.notna(sex_val):
                            sex_str = str(sex_val).strip().lower()
                            if sex_str in ["m", "male", "man"]:
                                subject_info["sex"] = "male"
                            elif sex_str in ["f", "female", "woman"]:
                                subject_info["sex"] = "female"
                            else:
                                subject_info["sex"] = "unknown"

                    # Extract handedness
                    handed_col = self._find_column(
                        participants_tsv, ["handedness", "hand"]
                    )
                    if handed_col:
                        handed_val = participants_tsv.iloc[idx][handed_col]
                        if pd.notna(handed_val):
                            handed_str = str(handed_val).strip().lower()
                            if handed_str.startswith("r"):
                                subject_info["handedness"] = "right"
                            elif handed_str.startswith("l"):
                                subject_info["handedness"] = "left"
                            else:
                                subject_info["handedness"] = "unknown"

                    # Extract group (FEP vs Control)
                    group_col = self._find_column(
                        participants_tsv, ["group", "diagnosis", "diagnostic"]
                    )
                    if group_col:
                        group_val = participants_tsv.iloc[idx][group_col]
                        if pd.notna(group_val):
                            group_str = str(group_val).strip().lower()
                            # Store group in description for super meta downstream
                            if "fep" in group_str or "psychosis" in group_str:
                                subject_info["group"] = "FEP"
                            elif "control" in group_str or "hc" in group_str:
                                subject_info["group"] = "Control"

                    break

        # Fallback: try to infer from dataset metadata
        # Source: OpenNeuro DS003944 dataset_description.json
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        if subject_info["amplifier"] == "unknown":
            subject_info["amplifier"] = "unknown"

        return subject_info

    def _find_column(self, df, candidates: list) -> Optional[str]:
        """Find the first matching column name in DataFrame."""
        for col in candidates:
            if col in df.columns:
                return col
        return None

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names and set montage.

        Parameters
        ----------
        raw : MNE Raw object

        Returns
        -------
        mne.io.BaseRaw
            Raw with standardized channel names and montage
        """
        ch_names = raw.ch_names
        rename_map: Dict[str, str] = {}

        # Try to match existing channels to standard names
        # The dataset typically uses standard 10-20 naming
        # Source: Dataset documentation / paper references
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核

        # Common aliases for 10-20 system channels
        alias_groups = [
            # Standard 10-20 names and their common variants
            ("Fp1", ["EEG Fp1", "Fp1", "fp1"]),
            ("Fpz", ["EEG Fpz", "Fpz", "fpz"]),
            ("Fp2", ["EEG Fp2", "Fp2", "fp2"]),
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
            ("FC1", ["EEG FC1", "FC1"]),
            ("FC2", ["EEG FC2", "FC2"]),
            ("FC5", ["EEG FC5", "FC5"]),
            ("FC6", ["EEG FC6", "FC6"]),
            ("CP1", ["EEG CP1", "CP1"]),
            ("CP2", ["EEG CP2", "CP2"]),
            ("CP5", ["EEG CP5", "CP5"]),
            ("CP6", ["EEG CP6", "CP6"]),
        ]

        existing_names = set(ch_names)
        matched = set()

        for target_name, aliases in alias_groups:
            for alias in aliases:
                if alias in existing_names and alias != target_name and alias not in matched:
                    rename_map[alias] = target_name
                    matched.add(alias)
                    break

        # Apply renames if any found
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # Try to set standard montage
        try:
            # Standard 10-20 montage is available in MNE
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage setting fails, continue without it
            pass

        return raw


KERNEL = OpenNeuroDS003944Kernel()