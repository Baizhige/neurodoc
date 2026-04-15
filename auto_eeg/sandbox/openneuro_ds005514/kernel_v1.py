"""HBN EEG (OpenNeuro ds005514) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 9 - large-scale multi-task developmental
battery with resting-state, contrast detection, and other paradigms.
129-channel EEG at 500 Hz.

Source: https://openneuro.org/datasets/ds005514
Reference: Alexander et al. (2022) NeuroImage 119348; 
           DOI: 10.1016/j.neuroimage.2022.119348
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants / Look-up tables
# ---------------------------------------------------------------------------

# HBN uses BrainAmp MR plus amplifiers with 128 EEG + 1 reference channel.
# Source: HBN data dictionary / Alexander et al. (2017) Scientific Data
# Annotator: Human, based on official HBN documentation
AMPLIFIER = "BrainAmp MR plus"
CAP = "Ag/AgCl"

# Standard 10-20 129-channel layout used by HBN (Biosemi-style naming).
# Source: HBN electrode layout documentation; 10-20 system extended to 129 ch
# Annotator: Human, based on official HBN cap documentation
_HBN_129_CHANNEL_MAP = {
    "Fp1": "EEG Fp1",
    "AFp1": "EEG AFp1",
    "AFp2": "EEG AFp2",
    "Fpz": "EEG Fpz",
    "AF7": "EEG AF7",
    "AF3": "EEG AF3",
    "AF4": "EEG AF4",
    "AF8": "EEG AF8",
    "Fz": "EEG Fz",
    "F1": "EEG F1",
    "F2": "EEG F2",
    "F3": "EEG F3",
    "F4": "EEG F4",
    "F5": "EEG F5",
    "F6": "EEG F6",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "FT9": "EEG FT9",
    "FT7": "EEG FT7",
    "FC5": "EEG FC5",
    "FC3": "EEG FC3",
    "FC1": "EEG FC1",
    "FCz": "EEG FCz",
    "FC2": "EEG FC2",
    "FC4": "EEG FC4",
    "FC6": "EEG FC6",
    "FT8": "EEG FT8",
    "FT10": "EEG FT10",
    "T7": "EEG T7",
    "C5": "EEG C5",
    "C3": "EEG C3",
    "C1": "EEG C1",
    "Cz": "EEG Cz",
    "C2": "EEG C2",
    "C4": "EEG C4",
    "C6": "EEG C6",
    "T8": "EEG T8",
    "TP9": "EEG TP9",
    "TP7": "EEG TP7",
    "CP5": "EEG CP5",
    "CP3": "EEG CP3",
    "CP1": "EEG CP1",
    "CPz": "EEG CPz",
    "CP2": "EEG CP2",
    "CP4": "EEG CP4",
    "CP6": "EEG CP6",
    "TP8": "EEG TP8",
    "TP10": "EEG TP10",
    "P9": "EEG P9",
    "P7": "EEG P7",
    "P5": "EEG P5",
    "P3": "EEG P3",
    "P1": "EEG P1",
    "Pz": "EEG Pz",
    "P2": "EEG P2",
    "P4": "EEG P4",
    "P6": "EEG P6",
    "P8": "EEG P8",
    "P10": "EEG P10",
    "PO7": "EEG PO7",
    "PO3": "EEG PO3",
    "POz": "EEG POz",
    "PO4": "EEG PO4",
    "PO8": "EEG PO8",
    "O1": "EEG O1",
    "O2": "EEG O2",
    "Oz": "EEG Oz",
    "Iz": "EEG Iz",
    "F9": "EEG F9",
    "F10": "EEG F10",
    "T9": "EEG T9",
    "T10": "EEG T10",
    "A1": "EEG A1",
    "A2": "EEG A2",
    "M1": "EEG M1",
    "M2": "EEG M2",
    "Cbl1": "EEG Cbl1",
    "Cbl2": "EEG Cbl2",
    "Cbl3": "EEG Cbl3",
    "Cbl4": "EEG Cbl4",
    "Cbl5": "EEG Cbl5",
    "Cbl6": "EEG Cbl6",
    "Cbl7": "EEG Cbl7",
    "Cbl8": "EEG Cbl8",
    "Status": "Status",
}

# Reverse lookup: standard_name -> original_prefixed_name
_CHANNEL_STANDARD_TO_ORIGINAL = {v: k for k, v in _HBN_129_CHANNEL_MAP.items()}

# Raw event annotation mapping from HBN event codes to human-readable labels.
# Source: HBN EEG event code documentation (ds005514)
# Annotator: Human, based on HBN event structure table
_RAW_EVENT_ID_MAP = {
    "stim_ON": 1,
    "fixpoint_ON": 2,
    "contrastTrial_start": 3,
    "left_buttonPress": 4,
    "right_buttonPress": 5,
    "right_target": 6,
    "left_target": 7,
    "break cnt": 8,
    "trialResponse": 9,
    "instructed_toOpenEyes": 10,
    "boundary": 11,
    "instructed_toCloseEyes": 12,
    "resting_start": 13,
    "9999": 9999,
}
_RAW_ANNOTATION_TO_ID = {v: k for k, v in _RAW_EVENT_ID_MAP.items()}

# Subject metadata cache (populated from participants.tsv at runtime).
# Source: participants.tsv in BIDS dataset root
# Annotator: LLM, populated dynamically via _load_participants_data()
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Phenotypic data cache for super meta labels.
# Source: phenotype/*.csv files in dataset root
# Annotator: LLM, populated dynamically via _load_phenotypic_data()
_PHENOTYPIC_DICT: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _detect_dataset_root(file_path: str) -> str:
    """Locate the BIDS dataset root from a file path."""
    parts = file_path.split(os.sep)
    for i in range(len(parts), 0, -1):
        candidate = os.sep.join(parts[:i])
        if os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    return os.path.dirname(file_path)


def _load_participants_data(dataset_root: str) -> None:
    """Load subject metadata from participants.tsv."""
    global _SUBJECT_DICT
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return
    try:
        df = pd.read_csv(participants_path, sep="\t")
        for _, row in df.iterrows():
            subject_id = str(row.get("participant_id", "")).strip()
            if not subject_id:
                continue
            sex_raw = str(row.get("sex", "unknown")).strip().lower()
            if sex_raw in ("m", "male"):
                sex = "male"
            elif sex_raw in ("f", "female"):
                sex = "female"
            else:
                sex = "unknown"
            age_raw = row.get("age", None)
            if age_raw is not None and str(age_raw).lower() not in ("n/a", "na", ""):
                try:
                    age = str(int(float(age_raw)))
                except (ValueError, TypeError):
                    age = "unknown"
            else:
                age = "unknown"
            handedness_raw = str(row.get("handedness", "unknown")).strip().lower()
            if handedness_raw in ("r", "right"):
                handedness = "right"
            elif handedness_raw in ("l", "left"):
                handedness = "left"
            else:
                handedness = "unknown"
            _SUBJECT_DICT[subject_id] = {
                "age": age,
                "sex": sex,
                "handedness": handedness,
            }
    except Exception:
        pass


def _load_phenotypic_data(dataset_root: str) -> None:
    """Load phenotypic CSV files for super meta labels."""
    global _PHENOTYPIC_DICT
    phenotype_dir = os.path.join(dataset_root, "phenotype")
    if not os.path.exists(phenotype_dir):
        return
    csv_files = [
        "p_factor_scores.csv",
        "clinical_diagnoses.csv",
        "questionnaire_scores.csv",
    ]
    for csv_file in csv_files:
        csv_path = os.path.join(phenotype_dir, csv_file)
        if not os.path.exists(csv_path):
            continue
        try:
            df = pd.read_csv(csv_path, sep="\t")
            subject_col = None
            for col in ["participant_id", "subject_id", "bids_id", "id"]:
                if col in df.columns:
                    subject_col = col
                    break
            if subject_col is None:
                continue
            for _, row in df.iterrows():
                subject_id = str(row.get(subject_col, "")).strip()
                if not subject_id:
                    continue
                if subject_id not in _PHENOTYPIC_DICT:
                    _PHENOTYPIC_DICT[subject_id] = {}
                for col in df.columns:
                    if col == subject_col:
                        continue
                    val = row.get(col, None)
                    if val is not None and str(val).lower() not in ("n/a", "na", ""):
                        try:
                            _PHENOTYPIC_DICT[subject_id][col] = float(val)
                        except (ValueError, TypeError):
                            _PHENOTYPIC_DICT[subject_id][col] = str(val)
        except Exception:
            pass


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from BIDS file path (e.g., sub-01)."""
    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for HBN 129-channel naming convention."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    for standard_name, original_name in _HBN_129_CHANNEL_MAP.items():
        if original_name in existing_names:
            rename_map[original_name] = standard_name
    return rename_map


def _map_raw_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Map numeric annotation codes to human-readable event labels."""
    original_annotations = raw.annotations
    if original_annotations is None or len(original_annotations) == 0:
        return raw
    new_descriptions = []
    for desc in original_annotations.description:
        try:
            code = int(float(desc))
            mapped = _RAW_ANNOTATION_TO_ID.get(code, f"code_{code}")
        except (ValueError, TypeError):
            mapped = str(desc)
        new_descriptions.append(mapped)
    new_annotations = mne.Annotations(
        onset=original_annotations.onset,
        duration=original_annotations.duration,
        description=new_descriptions,
        orig_time=original_annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    return raw


def _add_super_meta_annotations(raw: mne.io.BaseRaw, subject_id: str) -> mne.io.BaseRaw:
    """Add super meta annotations from phenotypic data for resting-state epochs."""
    phenotype = _PHENOTYPIC_DICT.get(subject_id, {})
    if not phenotype:
        return raw
    current_annotations = raw.annotations
    descriptions = list(current_annotations.description)
    onsets = list(current_annotations.onset)
    durations = list(current_annotations.duration)
    resting_mask = [d == "resting_start" for d in descriptions]
    if not any(resting_mask):
        return raw
    # Map phenotypic values to annotation descriptions for super meta.
    super_meta_labels = [
        "p_factor",
        "internalizing_factor",
        "externalizing_factor",
        "SCARED_GAD",
        "SWAN_IN",
        "SWAN_HY",
        "SRS_2_SCI",
        "SRS_2_RRB",
        "WISC_VCI",
        "WMI",
    ]
    for label in super_meta_labels:
        value = phenotype.get(label)
        if value is not None:
            for idx, is_resting in enumerate(resting_mask):
                if is_resting:
                    descriptions.append(f"super_meta:{label}")
                    onsets.append(current_annotations.onset[idx])
                    durations.append(0.0)
    if len(descriptions) > len(current_annotations.description):
        new_annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
            orig_time=current_annotations.orig_time,
        )
        raw.set_annotations(new_annotations)
    return raw


def _infer_subject_info(subject_id: str) -> Dict[str, str]:
    """Infer subject metadata when participants.tsv is unavailable.
    
    LLM 推断，需人类复核
    """
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _get_eegunity_description(
    raw: mne.io.BaseRaw,
    subject_id: str,
) -> Dict[str, Any]:
    """Build the eegunity_description dict for raw.info['description']."""
    original_desc = raw.info.get("description", "")
    subject_info = _SUBJECT_DICT.get(subject_id)
    if subject_info is None:
        # LLM 推断，需人类复核
        subject_info = _infer_subject_info(subject_id)
    return {
        "original_description": str(original_desc) if original_desc else "",
        "eegunity_description": {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": AMPLIFIER,
            "cap": CAP,
            "handedness": subject_info.get("handedness", "unknown"),
        },
    }


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

@dataclass
class HBNKernel:
    """Stage1 kernel for the HBN EEG dataset (OpenNeuro ds005514)."""

    KERNEL_ID: str = "hbn-eeg-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (loaded via standard BIDS pipeline)
        row : locator row with File Path

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw with standardized channels, events, and metadata.
        """
        file_path = str(row.get("File Path", ""))
        dataset_root = _detect_dataset_root(file_path)

        # Load subject/phenotypic data once per session.
        if not _SUBJECT_DICT:
            _load_participants_data(dataset_root)
            _load_phenotypic_data(dataset_root)

        subject_id = _extract_subject_id(file_path)

        # --- Step 1: Channel renaming (BEFORE set_montage) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # --- Step 2: Set montage (standard 10-20, 129-channel) ---
        try:
            montage = mne.channels.make_standard_montage("standard_alphabetic")
            # Pick only the channels present in the data
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 64:
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass

        # --- Step 3: Map raw annotations to human-readable labels ---
        raw = _map_raw_annotations(raw)

        # --- Step 4: Add super meta annotations from phenotypic data ---
        raw = _add_super_meta_annotations(raw, subject_id)

        # --- Step 5: Write eegunity_description ---
        description_dict = _get_eegunity_description(raw, subject_id)
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = HBNKernel()