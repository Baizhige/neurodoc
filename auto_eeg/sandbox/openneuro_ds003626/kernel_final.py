"""OpenNeuro ds003626 stage1 kernel for EEGUnity.

Inner Speech dataset - high-density EEG (137 channels) at 1024 Hz.
Three modalities: inner speech, pronounced speech, visualization.
Directional commands: Up, Down, Left, Right.

Source: https://openneuro.org/datasets/ds003626
DOI: 10.1038/s41597-022-01536-7
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


# Source: Dataset descriptor paper DOI 10.1038/s41597-022-01536-7
# Annotator: LLM, 2026-04-09 — 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# All subject info requires verification from participants.tsv


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm type from file path or name.
    
    The dataset contains three modalities:
    - inner speech (InnerSpeech)
    - pronounced speech (Pronounced)
    - visualization (Visualization)
    """
    file_name = os.path.basename(file_path).lower()
    
    if "inner" in file_name and "speech" in file_name:
        return "InnerSpeech"
    elif "pronounced" in file_name or "pronounce" in file_name:
        return "Pronounced"
    elif "visualization" in file_name or "visualization" in file_name:
        return "Visualization"
    elif "visualization" in file_name:
        return "Visualization"
    
    return "Unknown"


def _detect_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.
    
    Expected format: sub-<subject_id>
    """
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return match.group(1)
    
    # Fallback: extract from directory structure
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part.replace("sub-", "")
    
    return "unknown"


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv.
    
    Returns a dict mapping subject_id -> {age, sex, handedness}
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    
    if not os.path.exists(participants_file):
        return {}
    
    try:
        df = pd.read_csv(participants_file, sep="\t")
    except Exception:
        return {}
    
    subject_dict = {}
    for _, row in df.iterrows():
        participant_id = str(row.get("participant_id", ""))
        if not participant_id.startswith("sub-"):
            continue
        
        subject_id = participant_id.replace("sub-", "")
        
        # Extract age
        age_raw = row.get("age", None)
        if age_raw is not None and not pd.isna(age_raw):
            try:
                age = str(int(float(age_raw)))
            except (ValueError, TypeError):
                age = "unknown"
        else:
            age = "unknown"
        
        # Extract sex
        sex_raw = row.get("sex", row.get("gender", None))
        if sex_raw is not None and not pd.isna(sex_raw):
            sex_str = str(sex_raw).lower().strip()
            if sex_str in ["m", "male"]:
                sex = "male"
            elif sex_str in ["f", "female"]:
                sex = "female"
            else:
                sex = "unknown"
        else:
            sex = "unknown"
        
        # Extract handedness
        handedness_raw = row.get("handedness", row.get("hand", None))
        if handedness_raw is not None and not pd.isna(handedness_raw):
            hand_str = str(handedness_raw).lower().strip()
            if hand_str in ["r", "right", "right-handed"]:
                handedness = "right"
            elif hand_str in ["l", "left", "left-handed"]:
                handedness = "left"
            else:
                handedness = "unknown"
        else:
            handedness = "unknown"
        
        subject_dict[subject_id] = {
            "age": age,
            "sex": sex,
            "handedness": handedness,
        }
    
    return subject_dict


def _load_events_tsv(file_path: str) -> pd.DataFrame:
    """Load events from events.tsv file.
    
    The events.tsv contains timing information for the paradigm.
    No EEG trigger markers are present - timing is encoded externally.
    """
    # Get the events file path - same directory as the EEG file
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    # Try to find matching events.tsv
    # Pattern: <eeg_filename>_events.tsv or <base>_events.tsv
    base_name = file_name.rsplit(".", 1)[0]
    
    events_candidates = [
        os.path.join(dir_path, f"{base_name}_events.tsv"),
        os.path.join(dir_path, file_name.replace(".vhdr", "_events.tsv").replace(".eeg", "_events.tsv")),
    ]
    
    for events_path in events_candidates:
        if os.path.exists(events_path):
            try:
                df = pd.read_csv(events_path, sep="\t")
                return df
            except Exception:
                pass
    
    return pd.DataFrame()


def _build_annotations_from_events(
    events_df: pd.DataFrame,
    sfreq: float,
) -> mne.Annotations:
    """Build MNE annotations from events.tsv data.
    
    Events.tsv columns typically include:
    - onset: time in seconds
    - duration: event duration
    - value/trial_type: event identifier
    """
    if events_df.empty:
        return mne.Annotations(
            onset=np.array([], dtype=float),
            duration=np.array([], dtype=float),
            description=np.array([], dtype=object),
        )
    
    # Normalize column names
    onset_col = None
    duration_col = None
    value_col = None
    
    for col in ["onset", "onset_sec", "start_time"]:
        if col in events_df.columns:
            onset_col = col
            break
    
    for col in ["duration", "dur", "duration_sec"]:
        if col in events_df.columns:
            duration_col = col
            break
    
    for col in ["value", "trial_type", "event_label", "event_type", "event_id"]:
        if col in events_df.columns:
            value_col = col
            break
    
    if onset_col is None:
        # Fallback: try first numeric column as onset
        for col in events_df.columns:
            if events_df[col].dtype in [np.float64, np.float32, np.int64]:
                onset_col = col
                break
    
    if onset_col is None:
        return mne.Annotations(
            onset=np.array([], dtype=float),
            duration=np.array([], dtype=float),
            description=np.array([], dtype=object),
        )
    
    # Extract onset times
    onset = events_df[onset_col].values
    if not np.issubdtype(onset.dtype, np.floating):
        onset = onset.astype(float)
    
    # Extract durations (default to 0 if not available)
    if duration_col is not None:
        duration = events_df[duration_col].values
        if not np.issubdtype(duration.dtype, np.floating):
            duration = duration.astype(float)
    else:
        duration = np.zeros(len(onset))
    
    # Extract event descriptions
    if value_col is not None:
        descriptions = events_df[value_col].astype(str).values
    else:
        descriptions = np.array([f"event_{i}" for i in range(len(onset))])
    
    return mne.Annotations(
        onset=onset,
        duration=duration,
        description=descriptions,
    )


def _build_event_rename_map() -> Dict[str, Dict[str, str]]:
    """Build event renaming map based on paradigm understanding.
    
    Source: Dataset descriptor DOI 10.1038/s41597-022-01536-7
    Events 11-14: Directional commands (Up, Down, Left, Right)
    Events 15-16: Word categories (social/numerical words)
    Events 21-23: Modality markers or repeats
    """
    # Directional commands mapping
    directional_map = {
        "11": "Up",
        "12": "Down",
        "13": "Left",
        "14": "Right",
    }
    
    # Word categories (social vs numerical)
    word_map = {
        "15": "Social_words",
        "16": "Numerical_words",
    }
    
    # Additional events
    additional_map = {
        "21": "event_21",
        "22": "event_22",
        "23": "event_23",
        "31": "event_31",
        "32": "event_32",
        "33": "event_33",
        "34": "event_34",
        "42": "event_42",
        "44": "event_44",
        "45": "event_45",
        "46": "event_46",
    }
    
    return {**directional_map, **word_map, **additional_map}


@dataclass
class OpenNeuroDS003626Kernel:
    """Stage1 kernel for the OpenNeuro ds003626 Inner Speech dataset.
    
    High-density EEG (137 channels) at 1024 Hz.
    Three modalities: inner speech, pronounced speech, visualization.
    No EEG trigger markers - timing reconstructed from events.tsv.
    """

    KERNEL_ID: str = "openneuro-ds003626-stage1"

    def load(self, file_path: str, udataset=None) -> mne.io.BaseRaw:
        """Load BrainVision EEG file and return MNE Raw object.
        
        Parameters
        ----------
        file_path : str
            Path to the .vhdr file
        udataset : optional
            EEGUnity dataset context
            
        Returns
        -------
        mne.io.BaseRaw
            Loaded raw EEG data
        """
        # MNE can read BrainVision files directly
        raw = mne.io.read_raw_brainvision(
            file_path,
            preload=False,
            verbose=False,
        )
        
        return raw

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw EEG data with metadata and annotations.
        """
        file_path = row.get("File Path", row.get("file_path", ""))
        dataset_path = row.get("Dataset Path", "")
        
        # Detect paradigm and subject
        paradigm = _detect_paradigm(file_path)
        subject_id = _detect_subject_id(file_path)
        
        # Get subject info from participants.tsv
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        if not subject_info and dataset_path:
            all_subjects = _load_participants_tsv(dataset_path)
            subject_info = all_subjects.get(subject_id, {})
        
        # Build eegunity_description
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")
        
        # Amplifier info from dataset descriptor
        # Source: Dataset descriptor DOI 10.1038/s41597-022-01536-7
        amplifier = "unknown"  # LLM 推断，需人类复核
        cap = "unknown"       # LLM 推断，需人类复核
        
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Handle channel renaming for 137-channel high-density EEG
        # Standard 10-20 system extended montage
        raw = _rename_channels_standard(raw)
        
        # Try to set standard 1020 montage for high-density EEG
        try:
            # Use standard_1020 as base, may not cover all 137 channels
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        
        # Load events from events.tsv
        events_df = _load_events_tsv(file_path)
        sfreq = raw.info["sfreq"]
        
        # Build annotations with paradigm prefix if applicable
        annotations = _build_annotations_from_events(events_df, sfreq)
        
        # Add paradigm prefix to descriptions if paradigm detected
        if paradigm != "Unknown" and len(annotations.description) > 0:
            new_descriptions = np.array([
                f"{paradigm}: {desc}" for desc in annotations.description
            ])
            annotations = mne.Annotations(
                onset=annotations.onset,
                duration=annotations.duration,
                description=new_descriptions,
            )
        
        raw.set_annotations(annotations)
        
        return raw


def _rename_channels_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard names if they use non-standard naming.
    
    Source: Dataset descriptor DOI 10.1038/s41597-022-01536-7
    The dataset uses BrainVision format with standard channel naming.
    This function handles common non-standard naming patterns.
    """
    ch_names = raw.ch_names
    rename_map = {}
    
    for ch in ch_names:
        ch_lower = ch.lower()
        
        # Skip non-EEG channels
        if ch_lower in ["eog", "emg", "ecg", "trigger", "stim"]:
            continue
        
        # Handle EEG-0, EEG-1, ... naming
        eeg_match = re.match(r'eeg[-_]?(\d+)', ch_lower)
        if eeg_match:
            continue  # Keep as is for now, will use montage
        
        # Handle common variations of standard names
        if ch == ch.upper() and len(ch) <= 4:
            # Likely a standard channel name already
            continue
    
    # Apply any renames found
    if rename_map:
        existing_renames = {k: v for k, v in rename_map.items() if k in ch_names}
        if existing_renames:
            raw.rename_channels(existing_renames)
    
    return raw


def _infer_amplifier_from_info(raw: mne.io.BaseRaw) -> str:
    """Infer amplifier type from raw info if possible.
    
    Source: LLM, 2026-04-09 — 推断，需人类复核
    """
    # Check for common device indicators in raw info
    description = raw.info.get("description", "")
    
    if "brainamp" in description.lower():
        return "BrainAmp"
    elif "egi" in description.lower():
        return "EGI"
    elif "biosemi" in description.lower():
        return "BioSemi"
    elif "neuroscan" in description.lower():
        return "NeuroScan"
    
    return "unknown"


KERNEL = OpenNeuroDS003626Kernel()