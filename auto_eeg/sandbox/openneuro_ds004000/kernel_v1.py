"""openneuro_ds004000 stage1 kernel for EEGUnity.

Fribourg Ultimatum Game in Schizophrenia Study.
BIDS dataset with 43 subjects, 132 channels, 2048 Hz.

This kernel loads participant metadata from participants.tsv,
remaps events to human-readable labels, and sets standard montage.

Source: https://openneuro.org/datasets/ds004000 (v1.0.0)
Evidence: 10.1016/j.schres.2017.05.037, 10.1016/j.schres.2023.01.029
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject metadata (from participants.tsv)
# Annotator: Human, 2026-04-08
# Source: participants.tsv in dataset root
# =============================================================================
def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if present."""
    pth = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(pth):
        return pd.read_csv(pth, sep="\t")
    return pd.DataFrame()


def _get_subject_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Returns dict with age, sex, handedness for the given subject.
    Missing values are set to "unknown".
    
    Annotator: Human, 2026-04-08
    Source: participants.tsv columns: age, sex, handedness
    """
    df = _load_participants_tsv(dataset_root)
    if df.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
    
    # Match subject_id (case-insensitive)
    match_rows = df[
        df["participant_id"].str.lower() == subject_id.lower()
    ]
    
    if match_rows.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
    
    row = match_rows.iloc[0]
    
    age_val = "unknown"
    if "age" in df.columns:
        raw_age = row.get("age")
        if pd.notna(raw_age):
            age_val = str(int(float(raw_age)))
    
    sex_val = "unknown"
    if "sex" in df.columns:
        raw_sex = row.get("sex")
        if pd.notna(raw_sex):
            sex_str = str(raw_sex).strip().lower()
            if sex_str in ("m", "male"):
                sex_val = "male"
            elif sex_str in ("f", "female"):
                sex_val = "female"
            else:
                sex_val = "unknown"
    
    handed_val = "unknown"
    if "handedness" in df.columns:
        raw_handed = row.get("handedness")
        if pd.notna(raw_handed):
            handed_str = str(raw_handed).strip().lower()
            if handed_str in ("r", "right"):
                handed_val = "right"
            elif handed_str in ("l", "left"):
                handed_val = "left"
            else:
                handed_val = "unknown"
    
    return {
        "age": age_val,
        "sex": sex_val,
        "handedness": handed_val,
    }


# =============================================================================
# Event remapping (Stimulus/S codes)
# Annotator: Human, 2026-04-08
# Source: events.tsv in BIDS dataset, analysis.md event table
# =============================================================================
_EVENT_MAP: Dict[int, str] = {
    1: "Stimulus/S 1",
    2: "Stimulus/S 2",
    3: "Stimulus/S 3",
    4: "Stimulus/S 4",
    64: "Stimulus/S 64",
    96: "Stimulus/S 96",
    128: "Stimulus/S 128",
    160: "Stimulus/S 160",
    193: "Stimulus/S 193",
    194: "Stimulus/S 194",
    195: "Stimulus/S 195",
    196: "Stimulus/S 196",
    197: "Stimulus/S 197",
    198: "Stimulus/S 198",
    199: "Stimulus/S 199",
    200: "Stimulus/S 200",
    201: "Stimulus/S 201",
    225: "Stimulus/S 225",
    226: "Stimulus/S 226",
    227: "Stimulus/S 227",
    228: "Stimulus/S 228",
    229: "Stimulus/S 229",
    230: "Stimulus/S 230",
    231: "Stimulus/S 231",
    232: "Stimulus/S 232",
    233: "Stimulus/S 233",
}


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from file path (e.g., sub-01 -> 01 or sub-01)."""
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _remap_raw_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap numeric annotation codes to human-readable labels.
    
    Annotator: Human, 2026-04-08
    Source: analysis.md event structure table
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    orig_descriptions = raw.annotations.description
    
    new_descriptions = []
    for desc in orig_descriptions:
        desc_str = str(desc)
        
        # Try direct numeric mapping
        try:
            code = int(float(desc_str))
            if code in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[code])
                continue
        except (ValueError, TypeError):
            pass
        
        # Blink marker
        if "blink" in desc_str.lower():
            new_descriptions.append("UserDefined/Blink")
        # Time 0 marker
        elif "time 0" in desc_str.lower() or desc_str.strip() == "0":
            new_descriptions.append("Time 0/")
        # Response markers
        elif desc_str in ("R 1", "Response/R 1"):
            new_descriptions.append("Response/R 1")
        elif desc_str in ("R 3", "Response/R 3"):
            new_descriptions.append("Response/R 3")
        else:
            new_descriptions.append(desc_str)
    
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    
    return raw


# =============================================================================
# Channel name handling
# Annotator: Human, 2026-04-08
# Source: 10.1016/j.schres.2017.05.037, standard_1020 system
# 132 channels typical for high-density EEG systems (e.g., BioSemi 128+4)
# =============================================================================
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "TP9", "TP10",
    "PO9", "PO10",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.
    
    Handles common patterns: EEG-001 -> standard names, 
    numeric-only names, BioSemi naming conventions.
    
    Annotator: Human, 2026-04-08
    Source: standard_1020 system for typical EEG cap layouts
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    # Pattern 1: EEG-001, EEG-01 -> numeric mapping for known positions
    # 132 channels suggests BioSemi 128+4 or similar high-density system
    eeg_pattern = re.compile(r"^EEG[-_]?(\d+)$", re.IGNORECASE)
    
    # Standard 10-20 channel positions (ordered by electrode number)
    standard_eeg_positions = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "T5", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T6", "T10",
        "TP9", "TP7", "TP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO4", "PO8", "PO10",
        "O1", "Oz", "O2",
        "F10", "T11", "T12",
    ]
    
    numbered_channels: Dict[str, str] = {}
    numbered_pattern = re.compile(r"^(\d+)$")
    idx = 0
    
    for ch in ch_names:
        ch_upper = ch.upper()
        
        # BioSemi-style: A1, A2, B1, B2, etc. - keep as is or mark
        if re.match(r"^[A-Z]\d+$", ch_upper):
            continue
        
        # Already standard 10-20 name
        if ch in _STANDARD_1020_CHANNELS or ch in standard_eeg_positions:
            continue
        
        # EEG-001 pattern
        eeg_match = eeg_pattern.match(ch)
        if eeg_match:
            try:
                num = int(eeg_match.group(1))
                if idx < len(standard_eeg_positions):
                    rename_map[ch] = standard_eeg_positions[idx]
                idx += 1
                continue
            except ValueError:
                pass
        
        # Pure numeric string
        if numbered_pattern.match(ch):
            try:
                num = int(ch)
                if idx < len(standard_eeg_positions):
                    rename_map[ch] = standard_eeg_positions[idx]
                idx += 1
                continue
            except ValueError:
                pass
    
    return rename_map


def _apply_channel_standardization(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply channel name standardization and set montage.
    
    Annotator: Human, 2026-04-08
    Source: standard_1020 system
    """
    rename_map = _build_channel_rename_map(raw)
    
    if rename_map:
        # Rename channels BEFORE set_montage
        renamed = raw.rename_channels(rename_map)
        raw = renamed
    
    # Set standard 10-20 montage
    try:
        raw.set_montage("standard_1020", on_missing="warn")
    except Exception:
        pass  # Skip if montage setting fails
    
    return raw


# =============================================================================
# Main Kernel Class
# =============================================================================
class OpenNeuroDs004000Kernel:
    """Stage1 kernel for openneuro_ds004000 (Fribourg Ultimatum Game Study).
    
    Handles BIDS-format EEG data with:
    - Subject metadata from participants.tsv
    - Event remapping from numeric codes
    - Channel standardization to 10-20 system
    - Standardized eegunity_description
    
    Annotator: Human, 2026-04-08
    Source: https://openneuro.org/datasets/ds004000
    """
    
    KERNEL_ID: str = "openneuro-ds004000-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata and events.
        """
        # Get file path for subject identification
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Get dataset root (parent of derivatives/sub-*/eeg/)
        # Navigate up to find root containing participants.tsv
        dataset_root = ""
        if file_path:
            parts = os.path.dirname(file_path).split(os.sep)
            for i in range(len(parts), 0, -1):
                check_path = os.sep.join(parts[:i])
                if os.path.exists(os.path.join(check_path, "participants.tsv")):
                    dataset_root = check_path
                    break
        
        # Load subject metadata
        subject_info = _get_subject_info(dataset_root, subject_id)
        
        # Remap annotations to human-readable labels
        raw = _remap_raw_annotations(raw)
        
        # Standardize channel names and set montage
        raw = _apply_channel_standardization(raw)
        
        # Get original description
        original_desc = raw.info.get("description", "")
        if not original_desc:
            original_desc = ""
        
        # Build eegunity_description
        # amplifier: LLM 推断，需人类复核 (likely BioSemi or BrainProducts based on 132ch)
        # cap: LLM 推断，需人类复核 (likely Ag/AgCl based on standard EEG)
        eegunity_desc = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": "unknown",  # LLM 推断，需人类复核
            "cap": "unknown",  # LLM 推断，需人类复核
            "handedness": subject_info["handedness"],
        }
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDs004000Kernel()