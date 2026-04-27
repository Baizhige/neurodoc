"""openneuro_ds003947 stage1 kernel for EEGUnity.

Dataset: First Episode Psychosis vs. Control Resting-State EEG (Task 2)
Source: https://openneuro.org/datasets/ds003947
Paper: 10.1038/s41598-024-66110-0, 10.48550/arxiv.2411.18392

This kernel handles a BIDS-format resting-state EEG dataset with:
- 61 subjects, 64 channels, 3000 Hz sampling rate
- 5-minute recording per subject
- Diagnosis labels from participants.tsv (type column: Control/Psychosis)

The dataset uses standard_1020 64-channel montage. Events are not present
in raw files; resting-state segmentation is handled at epoching stage.

Required info fields from participants.tsv: age, ethnicity, gender, race, type
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 64-channel layout used in this dataset
# Source: OpenNeuro ds003947 dataset documentation, 64-channel BrainVision actiChamp
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
_CHANNEL_NAMES_64 = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
    "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
    "TP9", "CP5", "CP1", "CP2", "CP6", "TP10", "P7", "P3",
    "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
    "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6",
    "FT9", "FT7", "FC3", "FC4", "FT8", "FT10", "C5", "C1",
    "C2", "C6", "TP7", "CP3", "CPz", "CP4", "TP8", "P5",
    "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
]


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from BIDS dataset root."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info_from_tsv(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv row."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "gender": "unknown",
        "ethnicity": "unknown",
        "race": "unknown",
        "type": "unknown",
        "handedness": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
    }

    if participants_df.empty:
        return info

    # Match subject ID (handle sub- prefix variations)
    clean_id = subject_id.replace("sub-", "")
    match_col = None
    for col in ["participant_id", "subject_id"]:
        if col in participants_df.columns:
            # Try exact match first, then with/without prefix
            mask = participants_df[col].astype(str).str.replace("sub-", "", regex=False) == clean_id
            if mask.any():
                match_col = col
                break

    if match_col is None:
        return info

    row = participants_df[mask].iloc[0]

    # age
    if "age" in row.index and pd.notna(row["age"]):
        try:
            info["age"] = str(int(float(row["age"])))
        except (ValueError, TypeError):
            info["age"] = str(row["age"])

    # sex / gender (normalize to lowercase)
    for col in ["sex", "gender"]:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip().lower()
            if val in ("m", "male"):
                info["sex"] = "male"
                info["gender"] = "M"
            elif val in ("f", "female"):
                info["sex"] = "female"
                info["gender"] = "F"
            else:
                info["sex"] = val
                info["gender"] = str(row[col]).strip()

    # ethnicity
    if "ethnicity" in row.index and pd.notna(row["ethnicity"]):
        info["ethnicity"] = str(row["ethnicity"]).strip()

    # race
    if "race" in row.index and pd.notna(row["race"]):
        info["race"] = str(row["race"]).strip()

    # type (clinical status: Control/Psychosis)
    if "type" in row.index and pd.notna(row["type"]):
        info["type"] = str(row["type"]).strip()

    # handedness
    if "handedness" in row.index and pd.notna(row["handedness"]):
        val = str(row["handedness"]).strip().lower()
        if val in ("r", "right"):
            info["handedness"] = "right"
        elif val in ("l", "left"):
            info["handedness"] = "left"
        else:
            info["handedness"] = val

    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".edf", "").replace(".set", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try BIDS directory structure
    dirname = os.path.dirname(file_path)
    for f in os.listdir(dirname):
        if f.endswith("_events.tsv"):
            return os.path.join(dirname, f)
    
    return None


class OpenNeuroDS003947Kernel:
    """Stage1 kernel for OpenNeuro ds003947 (FEP vs Control Resting-State EEG)."""

    KERNEL_ID: str = "openneuro-ds003947-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))

        # Get subject metadata from participants.tsv
        subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
        participants_df = _load_participants_tsv(dataset_path)
        subject_info = _get_subject_info_from_tsv(participants_df, subject_id)

        # Determine amplifier and cap from dataset documentation
        # Source: 10.1038/s41598-024-66110-0 — BrainVision actiChamp, Ag/AgCl electrodes
        # Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
        amplifier = "BrainProducts actiChamp"  # LLM 推断，需人类复核
        cap = "Ag/AgCl"  # LLM 推断，需人类复核

        # Build eegunity_description with required info fields
        eegunity_desc = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": amplifier,
            "cap": cap,
            "handedness": subject_info["handedness"],
            "ethnicity": subject_info["ethnicity"],
            "gender": subject_info["gender"],
            "race": subject_info["race"],
            "type": subject_info["type"],
        }

        # Update description
        original_desc = raw.info.get("description", "") or ""
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # Rename channels to standard 10-20 names if needed
        # The dataset uses standard names but may have prefix variations
        rename_map = {}
        existing_names = list(raw.ch_names)
        
        # Handle common prefix patterns (EEG, A, etc.)
        for i, ch_name in enumerate(existing_names):
            clean_name = ch_name.replace("EEG ", "").replace("EEG", "").replace("A", "").strip()
            # Try to match with standard names
            if clean_name in _CHANNEL_NAMES_64 and clean_name != ch_name:
                rename_map[ch_name] = clean_name
            elif ch_name.startswith("A") and len(ch_name) > 1:
                # Handle A1, A2, ... An notation -> match by position
                try:
                    idx = int(ch_name[1:]) - 1  # 1-based to 0-based
                    if 0 <= idx < len(_CHANNEL_NAMES_64):
                        rename_map[ch_name] = _CHANNEL_NAMES_64[idx]
                except ValueError:
                    pass

        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Ensure all channel names are in standard set
        # Reorder to standard montage if possible
        current_names = set(raw.ch_names)
        standard_names = [n for n in _CHANNEL_NAMES_64 if n in current_names]
        if len(standard_names) == len(raw.ch_names):
            # All channels match standard names, set standard_1020 montage
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Pick only the channels we have
                montage_ch_names = [n for n in montage.ch_names if n in current_names]
                if len(montage_ch_names) == len(raw.ch_names):
                    raw.set_montage(montage, match_case=False, on_missing="ignore")
            except Exception:
                pass  # Montage setting failed, continue without

        # Check for events.tsv and create annotations if needed
        # This dataset has no meaningful events (resting-state), but we check
        # for completeness per kernel requirements
        events_path = _find_events_tsv(file_path)
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                if not events_df.empty and len(events_df) > 0:
                    # Check if there are actual event entries (not just header/empty)
                    has_events = False
                    for col in ["trial_type", "value", "stim_type"]:
                        if col in events_df.columns:
                            if events_df[col].notna().any():
                                has_events = True
                                break
                    
                    if has_events:
                        # Create annotations from events.tsv
                        onsets = []
                        durations = []
                        descriptions = []
                        
                        for _, ev_row in events_df.iterrows():
                            onset = ev_row.get("onset", np.nan)
                            if pd.isna(onset):
                                continue
                            
                            duration = ev_row.get("duration", 0.0)
                            if pd.isna(duration):
                                duration = 0.0
                            
                            # Use trial_type or value as description
                            desc = "unknown"
                            if "trial_type" in ev_row.index and pd.notna(ev_row["trial_type"]):
                                desc = str(ev_row["trial_type"])
                            elif "value" in ev_row.index and pd.notna(ev_row["value"]):
                                desc = str(ev_row["value"])
                            elif "stim_type" in ev_row.index and pd.notna(ev_row["stim_type"]):
                                desc = str(ev_row["stim_type"])
                            
                            onsets.append(float(onset))
                            durations.append(float(duration))
                            descriptions.append(desc)
                        
                        if onsets:
                            annotations = mne.Annotations(
                                onset=onsets,
                                duration=durations,
                                description=descriptions,
                            )
                            raw.set_annotations(annotations)
            except Exception:
                pass  # Failed to read events, continue

        # Ensure no required native/derived misc channels are missing
        # This dataset has no required misc channels per requirements

        return raw


KERNEL = OpenNeuroDS003947Kernel()