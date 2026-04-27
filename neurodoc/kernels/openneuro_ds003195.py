"""OpenNeuro ds003195 stage1 kernel for EEGUnity.

Parkinson's disease placebo control group resting-state EEG dataset.
19 channels, 200 Hz sampling rate. BIDS-compliant with EDF files.

Source: https://openneuro.org/datasets/ds003195
Paper: DOI 10.3389/fnins.2022.841428

This kernel handles:
- BIDS participants.tsv metadata extraction (sex required)
- Standard 10-20 channel renaming for 19-channel montage
- Event annotation from sibling events.tsv (EDF files have no native annotations)
- Spanish/English event label normalization
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Required info fields from participants.tsv
# ---------------------------------------------------------------------------
_REQUIRED_INFO_FIELDS = ["sex"]

# ---------------------------------------------------------------------------
# Channel rename map for standard 19-channel 10-20 montage
# Source: Standard 10-20 system for 19 EEG channels
# Annotator: LLM, 2026-04-08 — needs human verification against actual data
# ---------------------------------------------------------------------------
_STANDARD_19_CHANNEL_MAP: Dict[str, str] = {
    # Handle common variants
    "FP1": "Fp1",
    "FP2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "FZ": "Fz",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "CZ": "Cz",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "PZ": "Pz",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    # Handle numbered variants if present
    "EEG-FP1": "Fp1",
    "EEG-FP2": "Fp2",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-FZ": "Fz",
    "EEG-Fz": "Fz",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-T7": "T7",
    "EEG-C3": "C3",
    "EEG-CZ": "Cz",
    "EEG-Cz": "Cz",
    "EEG-C4": "C4",
    "EEG-T8": "T8",
    "EEG-P7": "P7",
    "EEG-P3": "P3",
    "EEG-PZ": "Pz",
    "EEG-Pz": "Pz",
    "EEG-P4": "P4",
    "EEG-P8": "P8",
    "EEG-O1": "O1",
    "EEG-O2": "O2",
    # Handle 0-indexed variants
    "0": "Fp1",
    "1": "Fp2",
    "2": "F7",
    "3": "F3",
    "4": "Fz",
    "5": "F4",
    "6": "F8",
    "7": "T7",
    "8": "C3",
    "9": "Cz",
    "10": "C4",
    "11": "T8",
    "12": "P7",
    "13": "P3",
    "14": "Pz",
    "15": "P4",
    "16": "P8",
    "17": "O1",
    "18": "O2",
}

# ---------------------------------------------------------------------------
# Event label normalization map
# Maps raw event descriptions to canonical event IDs for downstream tasks.
# Source: analysis.md event structure + events.tsv inspection
# Annotator: LLM, 2026-04-08
# ---------------------------------------------------------------------------
_EVENT_LABEL_MAP: Dict[str, str] = {
    # Eyes closed
    "ojos cerrados": "65",
    "eyes closed": "65",
    "65": "65",
    # Eyes open
    "ojos abiertos": "66",
    "eyes open": "66",
    "66": "66",
    # Hyperventilation periods
    "hiperventilacion 1": "67",
    "hyperventilation 1": "67",
    "67": "67",
    "hiperventilacion 2": "68",
    "hyperventilation 2": "68",
    "68": "68",
    "hiperventilacion 3": "69",
    "hyperventilation 3": "69",
    "69": "69",
    # Hyperventilation 4 (with typo variant)
    "hiperventilacion 4": "74",
    "hipervantilacion 4": "74",  # typo variant
    "hyperventilation 4": "74",
    "74": "74",
    # Recovery
    "recuperacion": "70",
    "recovery": "70",
    "70": "70",
    # Photic stimulation (Spanish and English)
    "fotoestimulacion": "71",
    "photic stimulation": "5",
    "71": "71",
    "5": "5",
    # Eyes open during hyperventilation
    "HPVOJOS ABIERTOS": "HPVOJOS_ABIERTOS",
    # Discontinuity marker (admin event, excluded from tasks)
    "discontinuity": "discontinuity",
    "2": "discontinuity",
}


def _get_subject_id(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    match = re.search(r"sub-([a-zA-Z0-9]+)", file_path)
    return match.group(1) if match else "unknown"


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for i in range(len(parts), 0, -1):
        candidate = os.sep.join(parts[:i])
        if os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    return None


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read subject metadata from participants.tsv."""
    result: Dict[str, str] = {}
    p_tsv = os.path.join(bids_root, "participants.tsv")
    if not os.path.exists(p_tsv):
        return result
    
    try:
        df = pd.read_csv(p_tsv, sep="\t")
        # Find subject row
        subj_col = "participant_id"
        if subj_col not in df.columns:
            return result
        
        # BIDS subject IDs may have 'sub-' prefix
        for _, row in df.iterrows():
            pid = str(row[subj_col])
            if pid == subject_id or pid == f"sub-{subject_id}":
                for field in _REQUIRED_INFO_FIELDS:
                    if field in df.columns:
                        val = str(row[field]) if pd.notna(row[field]) else "unknown"
                        result[field] = val
                    else:
                        result[field] = "unknown"
                break
    except Exception:
        pass
    
    # Fill missing required fields with unknown
    for field in _REQUIRED_INFO_FIELDS:
        if field not in result:
            result[field] = "unknown"
    
    return result


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given data file."""
    # BIDS pattern: sub-XX[_ses-YY]_task-ZZ_eeg.edf -> sub-XX[_ses-YY]_task-ZZ_events.tsv
    base = file_path.replace("_eeg.edf", "_events.tsv").replace("_eeg.set", "_events.tsv").replace("_eeg.fif", "_events.tsv")
    if os.path.exists(base):
        return base
    
    # Try other patterns
    for ext in [".edf", ".set", ".fif", ".eeg"]:
        if file_path.endswith(ext):
            base = file_path[:-len(ext)]
            candidate = base + "_events.tsv"
            if os.path.exists(candidate):
                return candidate
    
    # Search in same directory
    data_dir = os.path.dirname(file_path)
    if os.path.isdir(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith("_events.tsv"):
                return os.path.join(data_dir, f)
    
    return None


def _read_events_tsv(events_tsv_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
        return df
    except Exception:
        return None


def _events_tsv_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    required_cols = ["onset"]
    if not all(c in events_df.columns for c in required_cols):
        return None
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        if pd.isna(row["onset"]):
            continue
        
        onset = float(row["onset"])
        duration = float(row["duration"]) if "duration" in row and pd.notna(row["duration"]) else 0.0
        
        # Determine description from value or trial_type
        # Prefer 'value' column as it contains the numeric trigger codes needed
        desc = None
        if "value" in row and pd.notna(row["value"]):
            val = str(row["value"]).strip()
            # Normalize through label map
            desc = _EVENT_LABEL_MAP.get(val.lower(), val)
        elif "trial_type" in row and pd.notna(row["trial_type"]):
            tt = str(row["trial_type"]).strip()
            desc = _EVENT_LABEL_MAP.get(tt.lower(), tt)
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    if len(onsets) == 0:
        return None
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _has_native_events(raw: mne.io.BaseRaw) -> bool:
    """Check if raw file already has meaningful events/annotations."""
    # Check annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Filter out empty/startup annotations
        non_empty = [d for d in raw.annotations.description if d and d not in ("BAD boundary", "EDGE boundary", "")]
        if len(non_empty) > 0:
            return True
    
    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=True, exclude=[])
    if len(stim_picks) > 0:
        return True
    
    return False


@dataclass
class OpenNeuroDS003195Kernel:
    """Stage1 kernel for OpenNeuro ds003195 (Placebo Neuroepo multisession)."""

    KERNEL_ID: str = "openneuro-ds003195-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _get_subject_id(file_path)
        bids_root = _find_bids_root(file_path)
        
        # -------------------------------------------------------------------
        # 1. Read participants.tsv metadata
        # -------------------------------------------------------------------
        participant_info: Dict[str, str] = {}
        if bids_root:
            participant_info = _read_participants_tsv(bids_root, subject_id)
        
        # Normalize sex to lowercase
        sex = participant_info.get("sex", "unknown").lower()
        if sex not in ("male", "female"):
            sex = "unknown"
        
        # -------------------------------------------------------------------
        # 2. Build eegunity_description
        # -------------------------------------------------------------------
        # Age is missing in this dataset per analysis.md
        # Device info missing in accessible metadata
        # LLM 推断，需人类复核
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_desc: Dict[str, str] = {
            "age": "unknown",  # subject_age missing in dataset
            "sex": sex,
            "amplifier": "unknown",  # device missing in dataset
            "cap": "unknown",  # not specified in accessible metadata
            "handedness": "unknown",  # not specified in accessible metadata
        }
        
        # Add required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field != "sex":  # sex already handled above
                val = participant_info.get(field, "unknown")
                eegunity_desc[field] = val
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # -------------------------------------------------------------------
        # 3. Channel renaming (BEFORE set_montage)
        # -------------------------------------------------------------------
        rename_map: Dict[str, str] = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            # Try exact match first, then case-insensitive
            if ch_name in _STANDARD_19_CHANNEL_MAP:
                rename_map[ch_name] = _STANDARD_19_CHANNEL_MAP[ch_name]
            elif upper in _STANDARD_19_CHANNEL_MAP:
                rename_map[ch_name] = _STANDARD_19_CHANNEL_MAP[upper]
            elif ch_name.lower() in {k.lower(): v for k, v in _STANDARD_19_CHANNEL_MAP.items()}:
                # Try lowercase match
                lower_map = {k.lower(): v for k, v in _STANDARD_19_CHANNEL_MAP.items()}
                rename_map[ch_name] = lower_map[ch_name.lower()]
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # -------------------------------------------------------------------
        # 4. Set standard 10-20 montage
        # -------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            pass
        
        # -------------------------------------------------------------------
        # 5. Event annotations — EDF files have no native triggers, MUST load from events.tsv
        # -------------------------------------------------------------------
        # Always load from events.tsv; EDF files do not carry embedded annotations
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_df = _read_events_tsv(events_tsv_path)
            if events_df is not None and len(events_df) > 0:
                annotations = _events_tsv_to_annotations(events_df, raw.info["sfreq"])
                if annotations is not None:
                    # Set annotations on raw — this is the critical step that was missing
                    raw.set_annotations(annotations)
        
        # -------------------------------------------------------------------
        # 6. Final metadata
        # -------------------------------------------------------------------
        raw.info["subject_info"] = raw.info.get("subject_info") or {}
        raw.info["subject_info"]["his_id"] = subject_id
        
        return raw


KERNEL = OpenNeuroDS003195Kernel()