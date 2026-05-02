"""OpenNeuro DS006269 stage1 kernel for EEGUnity.

Tethered EEG Recordings in Syngap1 Rats - BIDS-format dataset with
subject-level genotype metadata used for super meta classification.

Source: https://openneuro.org/datasets/ds006269
DOI: 10.1016/j.celrep.2024.114733
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Subject metadata extracted from participants.tsv
# Source: openneuro_ds006269/participants.tsv
# inferred by LLM, needs human review
_GENOTYPE_MAP: Dict[str, int] = {}
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load and parse participants.tsv from BIDS dataset root."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _initialize_subject_metadata(dataset_root: str) -> None:
    """Initialize subject dictionaries from participants.tsv if not already done."""
    global _GENOTYPE_MAP, _SUBJECT_DICT

    if _GENOTYPE_MAP:  # Already initialized
        return

    df = _load_participants_tsv(dataset_root)
    if df.empty:
        return

    # Check for available columns
    for _, row in df.iterrows():
        subject_id = str(row.get("participant_id", "")).strip()
        if not subject_id:
            continue

        # Extract genotype (wildtype=0, Syngap1=1)
        genotype = str(row.get("genotype", "unknown")).strip().lower()
        if "syngap1" in genotype or "heterozygous" in genotype or "mutant" in genotype:
            _GENOTYPE_MAP[subject_id] = 1
        elif "wildtype" in genotype or "wt" in genotype:
            _GENOTYPE_MAP[subject_id] = 0

        # Build subject info dict
        sex = str(row.get("sex", "unknown")).strip().lower()
        age = str(row.get("age", "unknown")).strip()

        # Normalize sex values
        if sex in ["m", "male"]:
            sex = "male"
        elif sex in ["f", "female"]:
            sex = "female"
        else:
            sex = "unknown"

        _SUBJECT_DICT[subject_id] = {
            "age": age if age and age != "nan" else "unknown",
            "sex": sex,
            "genotype": genotype,
        }


@dataclass
class OpenNeuroDS006269Kernel:
    """Stage1 kernel for OpenNeuro DS006269 - Syngap1 Rat EEG dataset."""

    KERNEL_ID: str = "openneuro-ds006269-stage1"

    # Dataset-level metadata
    _dataset_root: Optional[str] = None
    _initialized: bool = field(default=False, repr=False)

    def _ensure_initialized(self, udataset) -> None:
        """Lazy initialization of dataset metadata."""
        if self._initialized:
            return

        # Get dataset root from udataset
        if hasattr(udataset, "dataset_root") and udataset.dataset_root:
            self._dataset_root = udataset.dataset_root
        elif hasattr(udataset, "root") and udataset.root:
            self._dataset_root = udataset.root
        else:
            # Try to infer from locator
            pass

        if self._dataset_root:
            _initialize_subject_metadata(self._dataset_root)

        self._initialized = True

    def _extract_subject_id(self, row) -> str:
        """Extract subject ID from locator row."""
        # Try common column names
        for col in ["subject_id", "participant_id", "subject", "participant"]:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()

        # Try file path extraction
        if "File Path" in row:
            path = str(row["File Path"])
            # Extract sub-XX from path
            import re
            match = re.search(r"sub-([A-Za-z0-9]+)", path)
            if match:
                return match.group(1)

        return "unknown"

    def _get_genotype_label(self, subject_id: str) -> str:
        """Get genotype label for a subject."""
        if subject_id in _GENOTYPE_MAP:
            return "Syngap1" if _GENOTYPE_MAP[subject_id] == 1 else "wildtype"
        return "unknown"

    def _get_genotype_y(self, subject_id: str) -> int:
        """Get numeric genotype label (y) for classification."""
        if subject_id in _GENOTYPE_MAP:
            return _GENOTYPE_MAP[subject_id]
        return -1  # Unknown

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file path information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        # Ensure metadata is initialized
        self._ensure_initialized(udataset)

        # Extract subject ID
        subject_id = self._extract_subject_id(row)

        # Build eegunity_description
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # Rat EEG - no handedness applicable
        handedness = "unknown"

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # inferred by LLM, needs human review
                "cap": "unknown",  # inferred by LLM, needs human review
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Handle channel naming for rat EEG
        # 33 channels - rat EEG setup, not standard 10-20
        channel_rename_map = self._build_rat_channel_map(raw.ch_names)
        if channel_rename_map:
            try:
                raw.rename_channels(channel_rename_map)
            except Exception:
                pass  # Skip if renaming fails

        # Update annotation descriptions for raw meta
        # Dataset only has "unknown" events - these are admin markers
        if raw.annotations:
            updated_descriptions = []
            for desc in raw.annotations.description:
                if desc.lower() in ["unknown", ""]:
                    updated_descriptions.append("admin: unknown")
                else:
                    updated_descriptions.append(desc)
            if updated_descriptions:
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=updated_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annotations)

        # Add genotype as super meta annotation
        # This enables the classification task: wildtype=0, Syngap1=1
        genotype_label = self._get_genotype_label(subject_id)
        genotype_y = self._get_genotype_y(subject_id)

        # Create super meta annotation at the start of recording
        super_meta_desc = f"super:genotype={genotype_label}"
        if genotype_y >= 0:
            super_meta_annot = mne.Annotations(
                onset=[0.0],
                duration=[raw.times[-1]],  # Cover entire recording
                description=[super_meta_desc],
            )
            # Merge with existing annotations
            if raw.annotations:
                combined_annotations = mne.Annotations(
                    onset=list(raw.annotations.onset) + list(super_meta_annot.onset),
                    duration=list(raw.annotations.duration) + list(super_meta_annot.duration),
                    description=list(raw.annotations.description) + list(super_meta_annot.description),
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(combined_annotations)
            else:
                raw.set_annotations(super_meta_annot)

        # Store subject metadata in raw info for downstream use
        if hasattr(raw, "info"):
            raw.info["subject_info"] = {
                "subject_id": subject_id,
                "genotype": genotype_label,
                "genotype_y": genotype_y,
            }

        return raw

    def _build_rat_channel_map(self, ch_names: List[str]) -> Dict[str, str]:
        """Build channel rename map for rat EEG montage.

        Rat EEG typically uses numbered electrode channels without standard names.
        This attempts to standardize based on common rat EEG conventions.

        Source: General rat EEG electrode placement conventions
        inferred by LLM, needs human review
        """
        rename_map = {}
        eeg_channels = []

        for ch in ch_names:
            ch_upper = ch.upper()
            ch_type = None
            try:
                ch_type = mne.pick_types(raw.info, eeg=False, meg=False, misc=False).count()
            except Exception:
                pass

            # Identify EEG-like channels (non-standard naming)
            if ch.isdigit() or ch.startswith("EEG") or ch.startswith("CH"):
                eeg_channels.append(ch)

        # Rename to standard format EEG001, EEG002, etc.
        for i, ch in enumerate(sorted(eeg_channels), start=1):
            if ch != f"EEG{i:03d}":
                rename_map[ch] = f"EEG{i:03d}"

        return rename_map


KERNEL = OpenNeuroDS006269Kernel()