"""Ear-EEG Sleep Monitoring 2023 (EESM23) stage1 kernel for EEGUnity.

Dataset: openneuro_ds005178
Source: https://openneuro.org/datasets/ds005178
DOI: 10.3389/fnins.2023.987578, 10.1038/s41597-025-04579-8

Ear-EEG sleep monitoring dataset with 5 in-ear EEG channels at 250 Hz.
Sleep stage annotations (W/N1/N2/N3/REM) are stored in BIDS events.tsv files.
The kernel reads scoring annotations from BIDS *_events.tsv sidecars and maps
them to canonical sleep stage event IDs for 30-second epoching.

Channel names are non-standard ear-EEG labels and are kept as-is since they
do not map to standard 10-20 positions. No montage is set.
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


# BIDS scoring index to canonical event ID mapping.
# Source: task-sleep_acq-scoring_events.json in dataset
# scoring_idx values: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact
# Annotator: LLM, 2026-04-08
_SCORING_MAP = {
    1: "Sleep stage W",
    2: "Sleep stage R",
    3: "Sleep stage N1",
    4: "Sleep stage N2",
    5: "Sleep stage N3",
    6: "artefact",
}

# Required info fields from participants.tsv to include in eegunity_description
# LLM 推断，需人类复核
_REQUIRED_INFO_FIELDS: List[str] = []


def _detect_subject(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-(\w+)", file_path)
    return match.group(1) if match else "unknown"


def _find_bids_root(file_path: str) -> str:
    """Find BIDS root directory from a file path."""
    parts = file_path.split(os.sep)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].startswith("sub-"):
            return os.sep.join(parts[:i])
    # Fallback: search upward for participants.tsv
    for i in range(len(parts) - 1, -1, -1):
        candidate = os.sep.join(parts[:i])
        if candidate and os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    return os.path.dirname(file_path)


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root directory."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return None


def _load_subject_info(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    df = _read_participants_tsv(bids_root)
    if df is None:
        return info
    
    subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
    if subject_col not in df.columns:
        return info
    
    subject_row = df[df[subject_col] == f"sub-{subject_id}"]
    if subject_row.empty:
        # Try without sub- prefix
        subject_row = df[df[subject_col] == subject_id]
    
    if subject_row.empty:
        return info
    
    row = subject_row.iloc[0]
    
    # Age
    if "age" in row and pd.notna(row["age"]):
        info["age"] = str(int(float(row["age"])))
    
    # Sex
    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).lower().strip()
        if sex_val in ("m", "male"):
            info["sex"] = "male"
        elif sex_val in ("f", "female"):
            info["sex"] = "female"
    
    # Handedness
    if "handedness" in row and pd.notna(row["handedness"]):
        hand_val = str(row["handedness"]).lower().strip()
        if hand_val in ("r", "right"):
            info["handedness"] = "right"
        elif hand_val in ("l", "left"):
            info["handedness"] = "left"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # For BIDS, events.tsv is in the same directory with matching entities
    base_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    
    # Remove extension
    name_no_ext = re.sub(r"\.(edf|bdf|set|fif|vhdr|eeg|cnt)$", "", base_name, flags=re.IGNORECASE)
    
    # Try exact match first
    events_path = os.path.join(base_dir, f"{name_no_ext}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try without _eeg suffix
    name_no_eeg = re.sub(r"_eeg$", "", name_no_ext)
    events_path = os.path.join(base_dir, f"{name_no_eeg}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Search for any events.tsv in same directory that matches subject/task
    if os.path.exists(base_dir):
        for f in os.listdir(base_dir):
            if f.endswith("_events.tsv"):
                # Check if subject and task match
                if re.search(r"sub-" + _detect_subject(file_path), f):
                    return os.path.join(base_dir, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or events_df.empty:
        return None
    
    required_cols = ["onset"]
    for col in required_cols:
        if col not in events_df.columns:
            return None
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Description: prefer trial_type, then value, then stim_type
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        # Map numeric scoring values if present
        descriptions = []
        for val in events_df["value"].values:
            if pd.isna(val):
                descriptions.append("unknown")
            else:
                try:
                    int_val = int(float(val))
                    desc = _SCORING_MAP.get(int_val, str(val))
                    descriptions.append(desc)
                except (ValueError, TypeError):
                    descriptions.append(str(val))
        descriptions = np.array(descriptions)
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Filter out empty/NaN descriptions
    valid_mask = [d is not None and str(d).strip() != "" and str(d).lower() != "nan" for d in descriptions]
    if not any(valid_mask):
        return None
    
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    # Ensure non-negative onsets
    onsets = np.maximum(onsets, 0)
    
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions.tolist(),
    )
    return annotations


@dataclass
class EESM23Kernel:
    """Stage1 kernel for the Ear-EEG Sleep Monitoring 2023 (EESM23) dataset."""

    KERNEL_ID: str = "openneuro-ds005178-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _detect_subject(file_path)
        bids_root = _find_bids_root(file_path)
        
        # Load subject info from participants.tsv
        subject_info = _load_subject_info(bids_root, subject_id)
        
        # Build eegunity_description
        eegunity_desc = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": "unknown",  # LLM 推断，需人类复核
            "cap": "unknown",  # LLM 推断，需人类复核 - ear-EEG in-ear electrodes, non-standard cap
            "handedness": subject_info["handedness"],
        }
        
        # Add any required info fields from participants.tsv
        df = _read_participants_tsv(bids_root)
        if df is not None and _REQUIRED_INFO_FIELDS:
            subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
            if subject_col in df.columns:
                subject_row = df[df[subject_col] == f"sub-{subject_id}"]
                if subject_row.empty:
                    subject_row = df[df[subject_col] == subject_id]
                if not subject_row.empty:
                    row_data = subject_row.iloc[0]
                    for field in _REQUIRED_INFO_FIELDS:
                        if field in row_data and pd.notna(row_data[field]):
                            eegunity_desc[field] = str(row_data[field])
                        else:
                            eegunity_desc[field] = "unknown"
        
        # Set description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })
        
        # Channel handling: ear-EEG channels are non-standard, keep as-is
        # No renaming or montage for in-ear electrodes (not standard 10-20)
        # Source: dataset documentation - 5 in-ear EEG channels
        # Annotator: LLM, 2026-04-08
        
        # Ensure all channels are typed as EEG (they should be already)
        # Check for any mislabeled channels
        current_types = raw.get_channel_types()
        type_map = {}
        for ch_name, ch_type in zip(raw.ch_names, current_types):
            if ch_type not in ("eeg", "misc", "stim", "eog", "ecg", "emg"):
                type_map[ch_name] = "eeg"
        
        if type_map:
            raw.set_channel_types(type_map)
        
        # Handle events from events.tsv sidecar
        # The dataset uses BIDS events.tsv for sleep stage annotations and triggers
        events_path = _find_events_tsv(file_path)
        
        if events_path is not None:
            events_df = _read_events_tsv(events_path)
            if events_df is not None and not events_df.empty:
                # Check if this is a scoring events file or trigger events file
                is_scoring = "scoring" in os.path.basename(events_path).lower()
                is_trigger = "trigger" in os.path.basename(events_path).lower()
                
                # For trigger events, ensure trigger events are preserved
                if is_trigger or (not is_scoring):
                    # This contains trigger events - ensure they are in annotations
                    annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    if annotations is not None:
                        # Merge with existing annotations if any
                        existing_annotations = raw.annotations
                        if existing_annotations is not None and len(existing_annotations) > 0:
                            all_onsets = np.concatenate([existing_annotations.onset, annotations.onset])
                            all_durations = np.concatenate([existing_annotations.duration, annotations.duration])
                            all_descriptions = list(existing_annotations.description) + list(annotations.description)
                            
                            # Sort by onset
                            sort_idx = np.argsort(all_onsets)
                            all_onsets = all_onsets[sort_idx]
                            all_durations = all_durations[sort_idx]
                            all_descriptions = [all_descriptions[i] for i in sort_idx]
                            
                            merged_annotations = mne.Annotations(
                                onset=all_onsets,
                                duration=all_durations,
                                description=all_descriptions,
                            )
                            raw.set_annotations(merged_annotations)
                        else:
                            raw.set_annotations(annotations)
                else:
                    # Scoring events - add as annotations
                    annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    if annotations is not None:
                        existing_annotations = raw.annotations
                        if existing_annotations is not None and len(existing_annotations) > 0:
                            all_onsets = np.concatenate([existing_annotations.onset, annotations.onset])
                            all_durations = np.concatenate([existing_annotations.duration, annotations.duration])
                            all_descriptions = list(existing_annotations.description) + list(annotations.description)
                            
                            sort_idx = np.argsort(all_onsets)
                            all_onsets = all_onsets[sort_idx]
                            all_durations = all_durations[sort_idx]
                            all_descriptions = [all_descriptions[i] for i in sort_idx]
                            
                            merged_annotations = mne.Annotations(
                                onset=all_onsets,
                                duration=all_durations,
                                description=all_descriptions,
                            )
                            raw.set_annotations(merged_annotations)
                        else:
                            raw.set_annotations(annotations)
        
        # Also check for sibling scoring events file if current is trigger file
        if events_path is not None and "trigger" in os.path.basename(events_path).lower():
            base_dir = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name_no_ext = re.sub(r"\.(edf|bdf|set|fif|vhdr|eeg|cnt)$", "", base_name, flags=re.IGNORECASE)
            name_no_eeg = re.sub(r"_eeg$", "", name_no_ext)
            name_no_trigger = re.sub(r"_trigger$", "", name_no_eeg)
            
            # Try to find scoring events
            scoring_patterns = [
                f"{name_no_trigger}_scoring_events.tsv",
                f"{name_no_trigger}_acq-scoring_events.tsv",
            ]
            
            for pattern in scoring_patterns:
                scoring_path = os.path.join(base_dir, pattern)
                if os.path.exists(scoring_path):
                    scoring_df = _read_events_tsv(scoring_path)
                    if scoring_df is not None and not scoring_df.empty:
                        scoring_annotations = _events_to_annotations(scoring_df, raw.info["sfreq"])
                        if scoring_annotations is not None:
                            existing_annotations = raw.annotations
                            if existing_annotations is not None and len(existing_annotations) > 0:
                                all_onsets = np.concatenate([existing_annotations.onset, scoring_annotations.onset])
                                all_durations = np.concatenate([existing_annotations.duration, scoring_annotations.duration])
                                all_descriptions = list(existing_annotations.description) + list(scoring_annotations.description)
                                
                                sort_idx = np.argsort(all_onsets)
                                all_onsets = all_onsets[sort_idx]
                                all_durations = all_durations[sort_idx]
                                all_descriptions = [all_descriptions[i] for i in sort_idx]
                                
                                merged_annotations = mne.Annotations(
                                    onset=all_onsets,
                                    duration=all_durations,
                                    description=all_descriptions,
                                )
                                raw.set_annotations(merged_annotations)
                            else:
                                raw.set_annotations(scoring_annotations)
                    break
        
        # Ensure trigger events are present for downstream tasks
        # Verify annotations contain trigger events
        if raw.annotations is not None:
            has_trigger = any("trigger" in str(desc).lower() for desc in raw.annotations.description)
            # If no trigger found in annotations but file is a trigger file, we may need to add from events
            if not has_trigger and events_path is not None and "trigger" in os.path.basename(events_path).lower():
                events_df = _read_events_tsv(events_path)
                if events_df is not None and "value" in events_df.columns:
                    # Add trigger annotations explicitly
                    trigger_mask = events_df["value"].astype(str).str.lower() == "trigger"
                    if not trigger_mask.any():
                        # Try trial_type column
                        if "trial_type" in events_df.columns:
                            trigger_mask = events_df["trial_type"].astype(str).str.lower() == "trigger"
                    
                    if trigger_mask.any():
                        trigger_df = events_df[trigger_mask]
                        trigger_annotations = _events_to_annotations(trigger_df, raw.info["sfreq"])
                        if trigger_annotations is not None:
                            existing_annotations = raw.annotations
                            if existing_annotations is not None and len(existing_annotations) > 0:
                                all_onsets = np.concatenate([existing_annotations.onset, trigger_annotations.onset])
                                all_durations = np.concatenate([existing_annotations.duration, trigger_annotations.duration])
                                all_descriptions = list(existing_annotations.description) + list(trigger_annotations.description)
                                
                                sort_idx = np.argsort(all_onsets)
                                all_onsets = all_onsets[sort_idx]
                                all_durations = all_durations[sort_idx]
                                all_descriptions = [all_descriptions[i] for i in sort_idx]
                                
                                merged_annotations = mne.Annotations(
                                    onset=all_onsets,
                                    duration=all_durations,
                                    description=all_descriptions,
                                )
                                raw.set_annotations(merged_annotations)
                            else:
                                raw.set_annotations(trigger_annotations)
        
        return raw


KERNEL = EESM23Kernel()