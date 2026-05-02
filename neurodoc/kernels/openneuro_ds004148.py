"""openneuro_ds004148 stage1 kernel for EEGUnity.

Southwest University Resting-State and Cognitive State EEG Dataset.
Contains 5 mental states: Eyes-Open (EO), Eyes-Closed (EC), Music, Memory, Mental-Arithmetic.
Recorded at 500 Hz with 61 EEG channels.

Source: https://openneuro.org/datasets/ds004148
DOI: 10.1038/s41597-022-01607-9
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


# Mapping from trigger codes to mental state labels
# Source: analysis.md event structure (Event ID column)
# Annotator: LLM, 2026-04-08
_TRIGGER_MAP = {
    "S 33": "S 33",  # Eyes-open resting state
    "S 44": "S 44",  # Eyes-closed resting state
    "S 55": "S 55",  # Music listening
    "S 66": "S 66",  # Memory task
    "S 77": "S 77",  # Mental arithmetic
}

# Required info fields from participants.tsv
# Annotator: LLM, 2026-04-08
_REQUIRED_INFO_FIELDS = [
    "(1)Discontinuity of Mind_session1",
    "(2)Theory of Mind_session1",
    "ESS_2ndVisit",
    "KSS_session1",
    "PANAS-N_session1",
    "PANAS-P_session1",
    "SAS_1stVisit",
    "SDS_2ndVisit",
    "Subtraction_Correct/Not correct_session3",
    "age",
    "sex",
]

# Default values for required eegunity_description fields
# Age range 18-45 derived from dataset paper (DOI: 10.1038/s41597-022-01607-9)
# Annotator: LLM, 2026-04-08
_DEFAULT_AGE = "18-45"
_DEFAULT_SEX = "unknown"  # inferred by LLM, needs human review
_DEFAULT_AMPLIFIER = "unknown"  # inferred by LLM, needs human review
_DEFAULT_CAP = "unknown"  # inferred by LLM, needs human review
_DEFAULT_HANDEDNESS = "unknown"  # inferred by LLM, needs human review


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from file path.

    OpenNeuro BIDS format: sub-<label> prefix.
    """
    filename = os.path.basename(file_path)
    
    # Try to extract subject from various patterns
    match = re.search(r'sub-([a-zA-Z0-9]+)', filename)
    if match:
        return match.group(1)
    
    # Try directory path
    dirname = os.path.dirname(file_path)
    match = re.search(r'sub-([a-zA-Z0-9]+)', dirname)
    if match:
        return match.group(1)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file starting from the file's directory and going up."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for the given EEG file."""
    # BIDS convention: same directory, same base name with _events.tsv suffix
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative extensions
    for ext in [".edf", ".set", ".vhdr", ".eeg"]:
        base_alt = file_path.replace(ext, "")
        events_path = base_alt + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}
    
    # Find subject row - participant_id format could be "sub-01" or "01"
    subject_col = "participant_id"
    if subject_col not in df.columns:
        return {}
    
    # Try exact match first
    mask = df[subject_col] == f"sub-{subject_id}"
    if not mask.any():
        mask = df[subject_col] == subject_id
    
    if not mask.any():
        return {}
    
    row = df[mask].iloc[0]
    info = {}
    
    for field in _REQUIRED_INFO_FIELDS:
        if field in row.index:
            val = row[field]
            # Convert to string, handle NaN
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val)
        else:
            info[field] = "unknown"
    
    return info


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _build_annotations_from_events_tsv(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Build MNE Annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Standard BIDS events columns: onset, duration, trial_type, value
    onsets = events_df["onset"].values if "onset" in events_df.columns else []
    durations = events_df["duration"].values if "duration" in events_df.columns else [0.0] * len(onsets)
    
    # Use trial_type or value as description
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    else:
        descriptions = ["unknown"] * len(onsets)
    
    # Handle NaN durations
    durations = [0.0 if pd.isna(d) else float(d) for d in durations]
    
    return mne.Annotations(onset=list(onsets), duration=list(durations), description=list(descriptions))


def _create_derived_misc_channel(raw: mne.io.BaseRaw, name: str, value: float) -> mne.io.RawArray:
    """Create a constant misc channel with the given value."""
    n_times = len(raw.times)
    data = np.full((1, n_times), float(value), dtype=np.float64)
    
    info = mne.create_info(
        ch_names=[name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    
    raw_misc = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    return raw_misc


def _compute_bmi(height_cm: Optional[float], weight_kg: Optional[float]) -> Optional[float]:
    """Compute BMI from height (cm) and weight (kg)."""
    if height_cm is None or weight_kg is None:
        return None
    if pd.isna(height_cm) or pd.isna(weight_kg):
        return None
    if height_cm <= 0 or weight_kg <= 0:
        return None
    
    height_m = float(height_cm) / 100.0
    bmi = float(weight_kg) / (height_m ** 2)
    return bmi


def _compute_mental_health_composite(
    sas: Optional[float],
    sds: Optional[float],
    ess: Optional[float],
    all_sas: List[float],
    all_sds: List[float],
    all_ess: List[float],
) -> Optional[float]:
    """Compute z-score averaged mental health composite."""
    # Collect available measures and their reference distributions
    measures = []
    refs = []
    
    if sas is not None and not pd.isna(sas):
        measures.append(float(sas))
        refs.append(all_sas)
    if sds is not None and not pd.isna(sds):
        measures.append(float(sds))
        refs.append(all_sds)
    if ess is not None and not pd.isna(ess):
        measures.append(float(ess))
        refs.append(all_ess)
    
    if not measures:
        return None
    
    # Compute z-scores for available measures
    z_scores = []
    for m, ref in zip(measures, refs):
        ref_clean = [float(x) for x in ref if not pd.isna(x)]
        if len(ref_clean) < 2:
            z_scores.append(0.0)  # Can't compute z-score, use 0
            continue
        mean = np.mean(ref_clean)
        std = np.std(ref_clean, ddof=1)
        if std == 0:
            z_scores.append(0.0)
        else:
            z_scores.append((m - mean) / std)
    
    return float(np.mean(z_scores))


@dataclass
class OpenNeuroDS004148Kernel:
    """Stage1 kernel for the Southwest University Resting-State and Cognitive State EEG Dataset (ds004148)."""

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"]
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participants.tsv for required info fields
        participants_path = _find_participants_tsv(file_path)
        participants_info = {}
        if participants_path is not None and subject_id is not None:
            participants_info = _read_participants_info(participants_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participants_info.get("age", _DEFAULT_AGE),
            "sex": participants_info.get("sex", _DEFAULT_SEX),
            "amplifier": _DEFAULT_AMPLIFIER,
            "cap": _DEFAULT_CAP,
            "handedness": _DEFAULT_HANDEDNESS,
        }
        
        # Add required_info_fields to eegunity_description
        for field in _REQUIRED_INFO_FIELDS:
            eegunity_description[field] = participants_info.get(field, "unknown")
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Read events.tsv and set annotations if available
        events_path = _find_events_tsv(file_path)
        if events_path is not None:
            events_df = _read_events_tsv(events_path)
            if events_df is not None and not events_df.empty:
                annotations = _build_annotations_from_events_tsv(events_df, raw.info["sfreq"])
                if len(annotations) > 0:
                    raw.set_annotations(annotations)
        
        # Create derived misc channels
        # subtraction_final_number: use Subtraction_Correct/Not correct_session3 value
        subtraction_value_str = participants_info.get("Subtraction_Correct/Not correct_session3", "unknown")
        try:
            subtraction_value = float(subtraction_value_str)
        except (ValueError, TypeError):
            subtraction_value = 0.0
        
        raw_subtraction = _create_derived_misc_channel(raw, "subtraction_final_number", subtraction_value)
        
        # mental_health_composite: compute from SAS, SDS, ESS
        sas_val = None
        sds_val = None
        ess_val = None
        try:
            sas_str = participants_info.get("SAS_1stVisit", "unknown")
            if sas_str != "unknown":
                sas_val = float(sas_str)
        except (ValueError, TypeError):
            pass
        try:
            sds_str = participants_info.get("SDS_2ndVisit", "unknown")
            if sds_str != "unknown":
                sds_val = float(sds_str)
        except (ValueError, TypeError):
            pass
        try:
            ess_str = participants_info.get("ESS_2ndVisit", "unknown")
            if ess_str != "unknown":
                ess_val = float(ess_str)
        except (ValueError, TypeError):
            pass
        
        # Read all participants for reference distributions
        all_sas = []
        all_sds = []
        all_ess = []
        if participants_path is not None:
            try:
                df_all = pd.read_csv(participants_path, sep="\t")
                if "SAS_1stVisit" in df_all.columns:
                    all_sas = [float(x) for x in df_all["SAS_1stVisit"].dropna() if pd.notna(x)]
                if "SDS_2ndVisit" in df_all.columns:
                    all_sds = [float(x) for x in df_all["SDS_2ndVisit"].dropna() if pd.notna(x)]
                if "ESS_2ndVisit" in df_all.columns:
                    all_ess = [float(x) for x in df_all["ESS_2ndVisit"].dropna() if pd.notna(x)]
            except Exception:
                pass
        
        mental_health_value = _compute_mental_health_composite(
            sas_val, sds_val, ess_val, all_sas, all_sds, all_ess
        )
        if mental_health_value is None:
            mental_health_value = 0.0
        
        raw_mental_health = _create_derived_misc_channel(raw, "mental_health_composite", mental_health_value)
        
        # Add misc channels to raw
        raw = raw.add_channels([raw_subtraction, raw_mental_health], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004148Kernel()