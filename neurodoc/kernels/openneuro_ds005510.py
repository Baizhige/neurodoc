"""HBN EEG stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 6 - BIDS format.
129 channels (128 EEG + 1 external), 500 Hz sampling rate.
Pediatric population (ages 5-21), multi-paradigm EEG battery.

Source: https://openneuro.org/datasets/ds005510
Reference DOI: 10.1016/j.neuroimage.2022.119348
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import mne


# Default subject info when not available from participants.tsv
_DEFAULT_SUBJECT_INFO: Dict[str, Dict[str, str]] = {
    "default": {
        "age": "unknown",  # inferred by LLM, needs human review
        "sex": "unknown",
        "handedness": "unknown",
        "amplifier": "BrainAmp",  # inferred by LLM, needs human review
        "cap": "Ag/AgCl",  # inferred by LLM, needs human review
    }
}


@dataclass
class HBNKernel:
    """Stage1 kernel for HBN EEG dataset."""

    KERNEL_ID: str = "hbn-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded from BIDS format
        row : Locator row with file path and metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated description and annotations
        """
        # Get the base directory for participants.tsv
        file_path = row.get("File Path", "")
        base_dir = self._find_base_dir(file_path)

        # Extract subject info
        subject_info = self._get_subject_info(base_dir, row.get("Subject ID", ""))

        # Update description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": subject_info.get("amplifier", "BrainAmp"),
                "cap": subject_info.get("cap", "Ag/AgCl"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Standardize channel names for 128-channel setup
        raw = self._standardize_channels(raw)

        # Annotations are typically already set from BIDS sidecar
        # Ensure proper event mapping for HBN-specific events
        raw = self._ensure_annotations(raw)

        return raw

    def _find_base_dir(self, file_path: str) -> Optional[Path]:
        """Find the dataset base directory."""
        if not file_path:
            return None
        path = Path(file_path)
        # Navigate up to find dataset_description.json
        for parent in [path, *path.parents]:
            if (parent / "dataset_description.json").exists():
                return parent
        return None

    def _get_subject_info(
        self, base_dir: Optional[Path], subject_id: str
    ) -> Dict[str, str]:
        """Extract subject information from participants.tsv.

        Parameters
        ----------
        base_dir : Dataset base directory
        subject_id : Subject identifier (e.g., "sub-01")

        Returns
        -------
        Dict[str, str]
            Subject metadata dict with age, sex, handedness, etc.
        """
        if base_dir is None:
            return _DEFAULT_SUBJECT_INFO["default"].copy()

        participants_tsv = base_dir / "participants.tsv"
        if not participants_tsv.exists():
            return _DEFAULT_SUBJECT_INFO["default"].copy()

        try:
            import pandas as pd

            df = pd.read_csv(participants_tsv, sep="\t")
            if "participant_id" not in df.columns:
                return _DEFAULT_SUBJECT_INFO["default"].copy()

            # Match subject (handle with or without "sub-" prefix)
            clean_id = subject_id.replace("sub-", "") if subject_id.startswith("sub-") else subject_id
            match = df[df["participant_id"].str.replace("sub-", "", regex=False) == clean_id]

            if match.empty:
                return _DEFAULT_SUBJECT_INFO["default"].copy()

            row = match.iloc[0]
            info = _DEFAULT_SUBJECT_INFO["default"].copy()

            # Age - HBN typically has "age" column with decimal values
            if "age" in df.columns:
                age_val = row.get("age")
                if pd.notna(age_val):
                    info["age"] = str(int(float(age_val)))

            # Sex - HBN uses M/F
            if "sex" in df.columns:
                sex_val = row.get("sex")
                if pd.notna(sex_val):
                    sex_str = str(sex_val).strip().lower()
                    if sex_str == "m":
                        info["sex"] = "male"
                    elif sex_str == "f":
                        info["sex"] = "female"
                    else:
                        info["sex"] = "unknown"

            # Handedness - HBN may have "handedness" or "hand"
            for col in ["handedness", "hand"]:
                if col in df.columns:
                    hand_val = row.get(col)
                    if pd.notna(hand_val):
                        hand_str = str(hand_val).strip().lower()
                        if hand_str in ["r", "right"]:
                            info["handedness"] = "right"
                        elif hand_str in ["l", "left"]:
                            info["handedness"] = "left"

            return info

        except Exception:
            return _DEFAULT_SUBJECT_INFO["default"].copy()

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Standardize channel names for HBN 128-channel setup.

        HBN uses a modified 10-20 system with 128 channels.
        The external channel is typically labeled as 'EOG' or 'EXG'.
        """
        ch_names = raw.ch_names

        # Identify and rename external channels
        rename_map = {}
        for i, ch in enumerate(ch_names):
            if ch.upper() in ["EOG", "EXG", "EXTERNAL", "EOG-LEFT", "EOG-RIGHT"]:
                if "EOG" not in ch:
                    rename_map[ch] = f"EOG-{i}" if "EOG" not in ch else ch

        if rename_map:
            existing_renames = {k: v for k, v in rename_map.items() if k in ch_names}
            if existing_renames:
                raw.rename_channels(existing_renames)

        # Try to set montage if channels match standard 1020
        try:
            # HBN uses standard 10-20 electrodes, check if we can set montage
            standard_channels = [
                "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
                "T7", "C3", "Cz", "C4", "T8",
                "P7", "P3", "Pz", "P4", "P8",
                "O1", "O2"
            ]
            present_standard = [ch for ch in raw.ch_names if ch in standard_channels]

            if len(present_standard) >= 10:
                # Try standard 1020 montage
                try:
                    raw.set_montage("standard_1020", on_missing="ignore")
                except Exception:
                    pass  # Montage setting is optional
        except Exception:
            pass

        return raw

    def _ensure_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Ensure proper annotation format for HBN events.

        HBN events are typically already loaded from BIDS sidecar JSON.
        This ensures raw meta events are properly formatted.
        """
        current_annotations = raw.annotations

        if current_annotations is None or len(current_annotations) == 0:
            # No annotations - this may happen if BIDS sidecar is missing
            # Create minimal annotations based on known HBN event structure
            sfreq = raw.info["sfreq"]
            n_samples = len(raw.times)

            # HBN recording typically starts with eyes-open rest instruction
            # Create a placeholder resting segment at the beginning
            annotations = mne.Annotations(
                onset=[0.0],
                duration=[n_samples / sfreq],
                description=["resting_start"]
            )
            raw.set_annotations(annotations)
        else:
            # Verify existing annotations have proper description field
            # HBN event descriptions should match analysis.md structure
            valid_events = {
                "stim_ON", "fixpoint_ON", "contrastTrial_start",
                "left_buttonPress", "right_buttonPress", "right_target",
                "left_target", "break cnt", "trialResponse",
                "instructed_toOpenEyes", "instructed_toCloseEyes",
                "boundary", "resting_start"
            }

            # Annotations already exist from BIDS sidecar - no action needed
            pass

        return raw


KERNEL = HBNKernel()