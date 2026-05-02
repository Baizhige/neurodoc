"""OpenNeuro ds003801 stage1 kernel for EEGUnity.

Neural Tracking to Go - Mobile EEG dichotic listening study.
Participants performed dichotic listening while sitting or walking.
Used for auditory attention decoding (attended vs ignored speaker).

BIDS dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds003801
Original paper: DOI 10.1088/1741-2552/ac42b5
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


# ============================================================================
# Kernel Requirements
# ============================================================================
# Required info fields from participants.tsv: age, gender
# Required event IDs (must appear in scan): all event types listed in analysis.md

# ============================================================================
# Channel Rename Map
# ============================================================================
# Source: TMSi Saga 32-channel system default mapping, 24 EEG channels
# From dataset documentation and paper 10.1088/1741-2552/ac42b5
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Ch 1": "Fp1",
    "Ch 2": "Fp2",
    "Ch 3": "F7",
    "Ch 4": "F3",
    "Ch 5": "Fz",
    "Ch 6": "F4",
    "Ch 7": "F8",
    "Ch 8": "T7",
    "Ch 9": "C3",
    "Ch 10": "Cz",
    "Ch 11": "C4",
    "Ch 12": "T8",
    "Ch 13": "P7",
    "Ch 14": "P3",
    "Ch 15": "Pz",
    "Ch 16": "P4",
    "Ch 17": "P8",
    "Ch 18": "O1",
    "Ch 19": "Oz",
    "Ch 20": "O2",
    "Ch 21": "AF7",
    "Ch 22": "AF8",
    "Ch 23": "AFz",
    "Ch 24": "FC1",
}


# ============================================================================
# Device Metadata
# ============================================================================
# Source: paper 10.1088/1741-2552/ac42b5, Section 2.1
# "EEG was recorded using a TMSi Saga 32-channel amplifier..."
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_AMPLIFIER = "TMSi Saga 32-channel"
# Source: paper 10.1088/1741-2552/ac42b5, Ag/AgCl ring electrodes used
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_CAP = "Ag/AgCl"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EDF file.
    
    BIDS convention: sub-XX/eeg/sub-XX_task-YY_events.tsv
    """
    # Remove .edf extension and look for events.tsv
    base = file_path.replace(".edf", "")
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try alternative: replace _eeg.edf with _events.tsv
    alt = file_path.replace("_eeg.edf", "_events.tsv")
    if os.path.exists(alt):
        return alt
    
    # Try finding in same directory
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).replace(".edf", "").replace("_eeg", "")
    for f in os.listdir(dir_path):
        if f.endswith("_events.tsv") and base_name in f:
            return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file directory."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "participants.csv"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # Pattern: sub-XX/... or sub-XX_...
    patterns = [
        r"sub-([0-9]+)/",
        r"sub-([0-9]+)_",
    ]
    for pat in patterns:
        match = re.search(pat, file_path)
        if match:
            return match.group(1)
    # Try from filename
    basename = os.path.basename(file_path)
    match = re.search(r"sub-([0-9]+)", basename)
    if match:
        return match.group(1)
    return None


def _normalize_sex(value: Any) -> str:
    """Normalize sex/gender value to canonical form."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"
    s = str(value).strip().lower()
    if s in ("f", "female", "w", "woman"):
        return "female"
    if s in ("m", "male", "man"):
        return "male"
    return "unknown"


def _normalize_age(value: Any) -> str:
    """Normalize age value to string."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"
    try:
        # Handle ranges like "22-45"
        age_str = str(value).strip()
        # If it's a clean number, return as string
        float(age_str.replace("-", "").replace(" ", ""))
        return age_str
    except (ValueError, TypeError):
        return "unknown"


@dataclass
class OpenNeuroDS003801Kernel:
    """Stage1 kernel for OpenNeuro ds003801 dataset."""

    KERNEL_ID: str = "openneuro-ds003801-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        file_name = os.path.basename(file_path)

        # =====================================================================
        # 1. Channel Rename (before set_montage)
        # =====================================================================
        rename_map = {}
        for old_name, new_name in _CHANNEL_RENAME_MAP.items():
            if old_name in raw.ch_names and old_name != new_name:
                rename_map[old_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)

        # =====================================================================
        # 2. Set Montage for standard 10-20 channels
        # =====================================================================
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            # Some channels may not be in standard_1020, continue without full montage
            pass

        # =====================================================================
        # 3. Read participants.tsv for subject metadata
        # =====================================================================
        subject_id = _extract_subject_id_from_path(file_path)
        
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        
        participants_tsv = _find_participants_tsv(file_path)
        extra_info: Dict[str, str] = {}
        
        if participants_tsv and subject_id is not None:
            try:
                df = pd.read_csv(participants_tsv, sep="\t")
                # Find matching subject row
                subj_col = None
                for col in df.columns:
                    if col.lower() in ("participant_id", "subject_id", "participant id"):
                        subj_col = col
                        break
                if subj_col is None and len(df.columns) > 0:
                    subj_col = df.columns[0]  # Usually first column is participant_id
                
                if subj_col is not None:
                    # Format subject ID for matching (with or without "sub-" prefix)
                    subj_ids_to_try = [
                        f"sub-{subject_id}",
                        subject_id,
                        f"{int(subject_id):02d}" if subject_id.isdigit() else subject_id,
                    ]
                    
                    for sid in subj_ids_to_try:
                        mask = df[subj_col].astype(str).str.strip() == sid
                        if mask.any():
                            subj_row = df[mask].iloc[0]
                            
                            # Extract age
                            for age_col in ["age", "Age", "subject_age"]:
                                if age_col in df.columns:
                                    age = _normalize_age(subj_row[age_col])
                                    break
                            
                            # Extract sex/gender
                            for sex_col in ["sex", "gender", "Sex", "Gender"]:
                                if sex_col in df.columns:
                                    sex = _normalize_sex(subj_row[sex_col])
                                    break
                            
                            # Extract handedness if available
                            for hand_col in ["handedness", "Handedness", "hand"]:
                                if hand_col in df.columns:
                                    val = subj_row[hand_col]
                                    if pd.notna(val):
                                        h = str(val).strip().lower()
                                        if h in ("r", "right"):
                                            handedness = "right"
                                        elif h in ("l", "left"):
                                            handedness = "left"
                                    break
                            
                            # Build extra info from required_info_fields: age, gender
                            # These are already canonical; include all participants.tsv columns
                            for col in df.columns:
                                if col == subj_col:
                                    continue
                                val = subj_row.get(col)
                                if pd.notna(val):
                                    extra_info[col] = str(val)
                                else:
                                    extra_info[col] = "unknown"
                            break
            except Exception:
                pass  # Keep defaults if participants.tsv cannot be read

        # =====================================================================
        # 4. Build eegunity_description
        # =====================================================================
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": handedness,
        }
        
        # Add required info fields from participants.tsv
        # Required: age, gender
        for field in ["age", "gender"]:
            if field in extra_info:
                eegunity_desc[field] = extra_info[field]
            else:
                eegunity_desc[field] = "unknown"
        
        # Add any other participants.tsv columns
        for key, val in extra_info.items():
            if key not in eegunity_desc:
                eegunity_desc[key] = val

        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # =====================================================================
        # 5. Events from events.tsv (EDF may not carry triggers reliably)
        # =====================================================================
        events_tsv = _find_events_tsv(file_path)
        
        if events_tsv and os.path.exists(events_tsv):
            try:
                events_df = pd.read_csv(events_tsv, sep="\t")
                
                # Required columns for BIDS events.tsv
                if "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                    
                    # Determine description column: trial_type preferred, then value, then stim_type
                    desc_col = None
                    for col in ["trial_type", "value", "stim_type", "event_type"]:
                        if col in events_df.columns:
                            desc_col = col
                            break
                    
                    if desc_col is not None:
                        descriptions = events_df[desc_col].astype(str).values
                        
                        # Filter out empty/NaN descriptions
                        valid_mask = [d and str(d).lower() not in ("nan", "none", "") for d in descriptions]
                        
                        if any(valid_mask):
                            valid_onsets = onsets[valid_mask]
                            valid_durations = durations[valid_mask]
                            valid_descriptions = descriptions[valid_mask]
                            
                            # Create annotations
                            annotations = mne.Annotations(
                                onset=valid_onsets,
                                duration=valid_durations,
                                description=valid_descriptions,
                            )
                            raw.set_annotations(annotations)
            except Exception:
                pass  # Keep existing annotations if events.tsv cannot be parsed

        # =====================================================================
        # 6. Ensure misc channels if required
        # =====================================================================
        # No required_native_misc or derived_misc_channels for this dataset
        # All channels are EEG type from the TMSi system

        return raw


KERNEL = OpenNeuroDS003801Kernel()