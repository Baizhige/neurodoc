"""OpenNeuro DS001810 stage1 kernel for EEGUnity.

EEG study of the attentional blink before, during, and after tDCS.
Dataset: ds001810 | Year: 2019 | URL: https://openneuro.org/datasets/ds001810
Paradigm: RSVP attentional blink task with anodal/cathodal tDCS conditions.

This is a BIDS dataset with BioSemi 64-channel EEG + 8 external channels.
The STATUS channel encodes trial conditions as numeric codes.

Required info fields from participants.tsv: age, gender, tDCS_on_first_day
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


# =============================================================================
# Channel rename map: BioSemi 64 + 8 external channels to standard names
# Source: BioSemi 64-channel cap layout (standard_1020 equivalent)
# BioSemi channel naming: A1-A32, B1-B32 for 64 channels; EX1-EX8 for externals
# Standard 10-20 mapping based on BioSemi documentation
# Annotator: Human, 2026-04-08
# =============================================================================
_BIOSEMI_64_RENAME: Dict[str, str] = {
    # First amplifier (A1-A32)
    "A1": "Fp1", "A2": "AF7", "A3": "AF3", "A4": "F1", "A5": "F3", "A6": "F5", "A7": "F7", "A8": "FT7",
    "A9": "FC5", "A10": "FC3", "A11": "FC1", "A12": "C1", "A13": "C3", "A14": "C5", "A15": "T7", "A16": "TP7",
    "A17": "CP5", "A18": "CP3", "A19": "CP1", "A20": "P1", "A21": "P3", "A22": "P5", "A23": "P7", "A24": "P9",
    "A25": "PO7", "A26": "PO3", "A27": "O1", "A28": "Iz", "A29": "Oz", "A30": "POz", "A31": "Pz", "A32": "CPz",
    # Second amplifier (B1-B32)
    "B1": "Fp2", "B2": "AF8", "B3": "AF4", "B4": "AFz", "B5": "Fz", "B6": "F2", "B7": "F4", "B8": "F6",
    "B9": "F8", "B10": "FT8", "B11": "FC6", "B12": "FC4", "B13": "FC2", "B14": "FCz", "B15": "Cz", "B16": "C2",
    "B17": "C4", "B18": "C6", "B19": "T8", "B20": "TP8", "B21": "CP6", "B22": "CP4", "B23": "CP2", "B24": "P2",
    "B25": "P4", "B26": "P6", "B27": "P8", "B28": "P10", "B29": "PO8", "B30": "PO4", "B31": "O2", "B32": "Status",
    # External channels
    "EX1": "EX1", "EX2": "EX2", "EX3": "EX3", "EX4": "EX4",
    "EX5": "EX5", "EX6": "EX6", "EX7": "EX7", "EX8": "EX8",
}

# Channel types for special channels
_CHANNEL_TYPE_OVERRIDES: Dict[str, str] = {
    "Status": "stim",
    "EX1": "eog", "EX2": "eog", "EX3": "eog", "EX4": "eog",
    "EX5": "misc", "EX6": "misc", "EX7": "misc", "EX8": "misc",
}


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"(sub-[0-9a-zA-Z]+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    base = re.sub(r"_eeg\.[^.]+$", "", file_path)
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternate patterns
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    base_name = re.sub(r"_eeg\.[^.]+$", "", fname)
    
    # Search in same directory
    for f in os.listdir(dir_path):
        if f.endswith("_events.tsv") and f.startswith(base_name):
            return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


@dataclass
class OpenNeuroDS001810Kernel:
    """Stage1 kernel for OpenNeuro ds001810 (attentional blink + tDCS)."""

    KERNEL_ID: str = "openneuro-ds001810-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # =====================================================================
        # 1. Channel renaming to standard 10-20
        # =====================================================================
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in _BIOSEMI_64_RENAME:
                new_name = _BIOSEMI_64_RENAME[old_name]
                if new_name != old_name:
                    rename_map[old_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)

        # =====================================================================
        # 2. Set channel types
        # =====================================================================
        ch_type_map = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_TYPE_OVERRIDES:
                ch_type_map[ch_name] = _CHANNEL_TYPE_OVERRIDES[ch_name]
            elif ch_name.startswith("EX"):
                ch_type_map[ch_name] = "misc"
        
        if ch_type_map:
            raw.set_channel_types(ch_type_map)

        # =====================================================================
        # 3. Set montage (before any operations that need channel positions)
        # =====================================================================
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            # If standard_1020 fails, try with relaxed matching
            try:
                raw.set_montage("biosemi64", match_case=False, on_missing="warn")
            except Exception:
                pass  # Montage not critical for analysis

        # =====================================================================
        # 4. Load events from BIDS events.tsv — BrainVision .eeg files do NOT
        #    carry annotations natively (the .vmrk marker file may be missing
        #    or empty). We MUST populate raw.annotations from the sibling
        #    events.tsv.  Use the literal 'type' column as the annotation label;
        #    the 'value' column carries the numeric STATUS codes and is kept as
        #    description.  Onset is in seconds; duration 'n/a' → 0.
        # =====================================================================
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            try:
                df = pd.read_csv(events_tsv_path, sep="\t", dtype=str)

                onsets = []
                durations = []
                descriptions = []

                for _, ev_row in df.iterrows():
                    # onset (seconds)
                    onset_str = str(ev_row.get("onset", "")).strip()
                    if onset_str == "" or onset_str.lower() == "n/a":
                        continue
                    try:
                        onset = float(onset_str)
                    except ValueError:
                        continue

                    # duration
                    dur_str = str(ev_row.get("duration", "")).strip()
                    if dur_str == "" or dur_str.lower() == "n/a":
                        duration = 0.0
                    else:
                        try:
                            duration = float(dur_str)
                        except ValueError:
                            duration = 0.0

                    # label: use 'type' column (STATUS, Epoch, CM_in_range, etc.)
                    # This is the column that carries distinguishable event labels.
                    label = ""
                    if "type" in ev_row and pd.notna(ev_row["type"]):
                        label = str(ev_row["type"]).strip()
                        if label.lower() == "n/a":
                            label = ""

                    # value column: numeric STATUS codes, kept as description
                    value = ""
                    if "value" in ev_row and pd.notna(ev_row["value"]):
                        v = str(ev_row["value"]).strip()
                        if v and v.lower() != "n/a":
                            value = v

                    # Build description: use label; append value if distinct
                    if label and value and label != value:
                        description = f"{label}/{value}"
                    elif label:
                        description = label
                    elif value:
                        description = value
                    else:
                        description = "unknown"

                    onsets.append(onset)
                    durations.append(duration)
                    descriptions.append(description)

                if onsets:
                    annot = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                        orig_time=None,
                    )
                    raw.set_annotations(annot)
            except Exception:
                pass  # If events.tsv parsing fails, leave whatever annotations exist

        # =====================================================================
        # 5. Extract subject metadata from participants.tsv
        # =====================================================================
        subject_id = _get_subject_id_from_path(file_path)
        
        # Default metadata
        age = "unknown"
        sex = "unknown"
        tDCS_on_first_day = "unknown"
        amplifier = "BioSemi ActiveTwo"  # Known from dataset documentation
        cap = "BioSemi 64-channel cap"   # Known from dataset documentation
        handedness = "unknown"

        participants_path = _find_participants_tsv(file_path)
        if participants_path and subject_id:
            try:
                participants_df = pd.read_csv(participants_path, sep="\t", dtype=str)
                # Find matching row
                subj_row = participants_df[participants_df["participant_id"] == subject_id]
                if not subj_row.empty:
                    if "age" in subj_row.columns:
                        age_val = subj_row["age"].values[0]
                        if pd.notna(age_val):
                            age = str(age_val)
                    if "gender" in subj_row.columns:
                        sex_val = subj_row["gender"].values[0]
                        if pd.notna(sex_val):
                            sex = str(sex_val)
                    if "tDCS_on_first_day" in subj_row.columns:
                        tdc_val = subj_row["tDCS_on_first_day"].values[0]
                        if pd.notna(tdc_val):
                            tDCS_on_first_day = str(tdc_val)
            except Exception:
                pass  # If participants.tsv parsing fails, use defaults

        # =====================================================================
        # 6. Build eegunity_description
        # =====================================================================
        description = {
            "dataset": "ds001810",
            "dataset_name": "Attentional blink and tDCS",
            "paradigm": "RSVP attentional blink",
            "task": "attentionalblink",
            "stimulation": "tDCS",
            "subject_id": subject_id,
            "age": age,
            "sex": sex,
            "handedness": handedness,
            "tDCS_on_first_day": tDCS_on_first_day,
            "amplifier": amplifier,
            "cap": cap,
            "sampling_rate": raw.info["sfreq"],
            "n_channels": len(raw.ch_names),
            "n_samples": raw.n_times,
            "duration_sec": raw.n_times / raw.info["sfreq"] if raw.info["sfreq"] > 0 else None,
            "channel_names": raw.ch_names,
            "reference": "CMS/DRL (BioSemi default)",
            "has_annotations": raw.annotations is not None and len(raw.annotations) > 0,
            "n_annotations": len(raw.annotations) if raw.annotations is not None else 0,
        }

        # Store description in raw.info['description'] as JSON string
        raw.info["description"] = json.dumps(description)

        return raw


KERNEL = OpenNeuroDS001810Kernel()