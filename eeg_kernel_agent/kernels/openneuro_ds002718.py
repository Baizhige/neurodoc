"""openneuro_ds002718 stage1 kernel for EEGUnity.

Face processing EEG dataset with famous/unfamiliar/scrambled face categories
and symmetry judgment paradigm.

Source: https://openneuro.org/datasets/ds002718 (DOI: 10.1038/sdata.2015.1)
Dataset: 18 subjects, 74 channels, 250 Hz sampling rate.
Events: stimulus presentations (famous/unfamiliar/scrambled × new/early/late)
        and response events (left/right × sym/nonsym).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: dataset README / paper DOI 10.1038/sdata.2015.1
# 74-channel EEG cap with standard electrode positions
# Annotator: Human, 2026-04-08
_STANDARD_74_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "Iz",
    "CB1", "CB2",
]

# Source: 10.1038/sdata.2015.1 - BrainAmp amplifier system
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_AMPLIFIER = "BrainAmp"
_CAP_MATERIAL = "Ag/AgCl"  # LLM 推断，需人类复核


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, Any]]:
    """Load subject information from BIDS participants.tsv.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping from subject_id to {age, sex, handedness}.
    """
    tsv_path = Path(dataset_path) / "participants.tsv"
    if not tsv_path.exists():
        return {}

    df = pd.read_csv(tsv_path, sep="\t")
    subject_dict: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        subj_id = str(row.get("participant_id", "")).strip()
        if not subj_id:
            continue

        info: Dict[str, Any] = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        # Handle age column (may be named 'age', 'Age', or similar)
        age_col = "age" if "age" in df.columns else next(
            (c for c in df.columns if c.lower() == "age"), None
        )
        if age_col and age_col in df.columns:
            age_val = row.get(age_col)
            if pd.notna(age_val):
                info["age"] = str(int(float(age_val)))

        # Handle sex/gender column
        sex_col = next(
            (c for c in df.columns if c.lower() in ("sex", "gender")),
            None
        )
        if sex_col and sex_col in df.columns:
            sex_val = str(row.get(sex_col)).strip().lower()
            if sex_val in ("m", "male"):
                info["sex"] = "male"
            elif sex_val in ("f", "female"):
                info["sex"] = "female"
            elif sex_val:
                info["sex"] = sex_val

        # Handle handedness column
        hand_col = next(
            (c for c in df.columns if "hand" in c.lower()),
            None
        )
        if hand_col and hand_col in df.columns:
            hand_val = str(row.get(hand_col)).strip().lower()
            if "right" in hand_val:
                info["handedness"] = "right"
            elif "left" in hand_val:
                info["handedness"] = "left"

        subject_dict[subj_id] = info

    return subject_dict


def _build_channel_rename_map(
    raw: mne.io.BaseRaw,
) -> Dict[str, str]:
    """Build a channel rename map for non-standard channel names.

    Handles common patterns: EEG-001, eeg_ref, etc. -> standard names.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: EEG-001, EEG-01, EEG-1 -> standard 1020 names
    eeg_pattern = [
        "EEG 001", "EEG 002", "EEG 003", "EEG 004", "EEG 005",
        "EEG 006", "EEG 007", "EEG 008", "EEG 009", "EEG 010",
        "EEG 011", "EEG 012", "EEG 013", "EEG 014", "EEG 015",
        "EEG 016", "EEG 017", "EEG 018", "EEG 019", "EEG 020",
        "EEG 021", "EEG 022", "EEG 023", "EEG 024", "EEG 025",
        "EEG 026", "EEG 027", "EEG 028", "EEG 029", "EEG 030",
        "EEG 031", "EEG 032", "EEG 033", "EEG 034", "EEG 035",
        "EEG 036", "EEG 037", "EEG 038", "EEG 039", "EEG 040",
        "EEG 041", "EEG 042", "EEG 043", "EEG 044", "EEG 045",
        "EEG 046", "EEG 047", "EEG 048", "EEG 049", "EEG 050",
        "EEG 051", "EEG 052", "EEG 053", "EEG 054", "EEG 055",
        "EEG 056", "EEG 057", "EEG 058", "EEG 059", "EEG 060",
        "EEG 061", "EEG 062", "EEG 063", "EEG 064", "EEG 065",
        "EEG 066", "EEG 067", "EEG 068", "EEG 069", "EEG 070",
        "EEG 071", "EEG 072", "EEG 073", "EEG 074",
    ]

    # Standard 1020 positions for 74 channels (subset matching 10-20 system)
    standard_order = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
    ]

    for old_name in eeg_pattern:
        if old_name in existing:
            idx = eeg_pattern.index(old_name)
            if idx < len(standard_order):
                new_name = standard_order[idx]
                if new_name not in rename_map.values():
                    rename_map[old_name] = new_name

    # Pattern 2: lowercase eeg-001 -> EEG 001
    for ch in existing:
        if ch.lower().startswith("eeg-"):
            standardized = ch.upper().replace("-", " ")
            if standardized not in rename_map:
                rename_map[ch] = standardized

    # Pattern 3: handle reference electrodes
    ref_aliases = [
        ("EXG1", "EOG-left"),
        ("EXG2", "EOG-right"),
        ("EXG3", "EOG-central"),
        ("EXG4", "EOG-upper"),
        ("EXG5", "EOG-lower"),
        ("EOG left", "EOG-left"),
        ("EOG right", "EOG-right"),
        ("EOG up", "EOG-upper"),
        ("EOG down", "EOG-lower"),
    ]
    for old, new in ref_aliases:
        if old in existing:
            rename_map[old] = new

    return rename_map


@dataclass
class OpenNeuroDS002718Kernel:
    """Stage1 kernel for the openneuro ds002718 face processing dataset."""

    KERNEL_ID: str = "openneuro-ds002718-stage1"

    _subject_info: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _dataset_path: Optional[str] = field(default=None, repr=False)

    def _get_dataset_path(self, row) -> str:
        """Extract dataset path from row or use cached value."""
        if self._dataset_path:
            return self._dataset_path

        file_path = row.get("File Path", "")
        if file_path:
            # Navigate up from sub-XX/eeg/*.edf to dataset root
            path = Path(file_path)
            for _ in range(4):
                path = path.parent
            if path.name == "openneuro_ds002718":
                self._dataset_path = str(path)
                return self._dataset_path
            # Try single level up for BIDS structure
            parent = Path(file_path).parent
            for _ in range(3):
                if (parent / "participants.tsv").exists():
                    self._dataset_path = str(parent)
                    return self._dataset_path
                parent = parent.parent

        return ""

    def _load_subject_info(self, dataset_path: str) -> None:
        """Load subject info from participants.tsv if not already loaded."""
        if not self._subject_info and dataset_path:
            self._subject_info = _load_participants_tsv(dataset_path)

    def _extract_subject_id(self, row) -> str:
        """Extract subject ID from file path or row."""
        file_path = str(row.get("File Path", ""))
        # BIDS pattern: sub-XX
        import re
        match = re.search(r"sub-(\w+)", file_path)
        if match:
            return match.group(1)
        return "unknown"

    def _get_subject_description(self, row) -> Dict[str, str]:
        """Build eegunity_description dict for subject."""
        subject_id = self._extract_subject_id(row)

        # Get from loaded participants.tsv
        if subject_id in self._subject_info:
            info = self._subject_info[subject_id]
            return {
                "original_description": "",
                "eegunity_description": {
                    "age": info.get("age", "unknown"),
                    "sex": info.get("sex", "unknown"),
                    "amplifier": _AMPLIFIER,
                    "cap": _CAP_MATERIAL,
                    "handedness": info.get("handedness", "unknown"),
                },
            }

        # Fallback: unknown for all fields
        return {
            "original_description": "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": _AMPLIFIER,
                "cap": _CAP_MATERIAL,
                "handedness": "unknown",
            },
        }

    def _remap_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Ensure annotations use canonical event names from analysis.md."""
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        canonical_names = {
            "boundary",
            "famous_new",
            "famous_second_early",
            "famous_second_late",
            "unfamiliar_new",
            "unfamiliar_second_early",
            "unfamiliar_second_late",
            "scrambled_new",
            "scrambled_second_early",
            "scrambled_second_late",
            "left_nonsym",
            "left_sym",
            "right_nonsym",
            "right_sym",
        }

        new_descriptions = []
        for desc in raw.annotations.description:
            desc_str = str(desc).strip()
            if desc_str in canonical_names:
                new_descriptions.append(desc_str)
            elif desc_str.startswith("boundary"):
                new_descriptions.append("boundary")
            else:
                new_descriptions.append(desc_str)

        annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(annotations)
        return raw

    def apply(
        self, udataset, raw: mne.io.BaseRaw, row
    ) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized metadata.
        """
        # Step 1: Load dataset path and subject info
        dataset_path = self._get_dataset_path(row)
        self._load_subject_info(dataset_path)

        # Step 2: Update description with eegunity_description
        desc_dict = self._get_subject_description(row)
        raw.info["description"] = json.dumps(desc_dict)

        # Step 3: Rename channels to standard names (BEFORE set_montage)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Step 4: Set standard 1020 montage
        try:
            standard_montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(standard_montage, on_missing="warn")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: could not set montage: {e}")

        # Step 5: Remap annotations to canonical event names
        raw = self._remap_annotations(raw)

        return raw


KERNEL = OpenNeuroDS002718Kernel()