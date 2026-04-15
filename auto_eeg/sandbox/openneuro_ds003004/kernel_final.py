"""Dataset-specific kernel for openneuro_ds003004.

Imagined Emotion Study - 15-class emotion classification from guided imagery.
34 subjects, 219 channels, 256 Hz sampling rate.

Events: 15 emotion categories (anger, awe, compassion, content, disgust,
excite, fear, frustration, grief, happy, jealousy, joy, love, relax, relief, sad)
each occurring once per subject (~34 times total).

Source: https://openneuro.org/datasets/ds003004
DOI: 10.1016/j.neuroimage.2022.118873
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Information
# Source: participants.tsv (BIDS), DOI: 10.1016/j.neuroimage.2022.118873
# Annotator: Human (from dataset), 2026-04-08
# =============================================================================
def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from BIDS participants.tsv."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_file):
        return {}

    df = pd.read_csv(participants_file, sep="\t")
    subject_dict: Dict[str, Dict[str, str]] = {}

    for _, row in df.iterrows():
        subject_id = str(row.get("participant_id", "")).strip()
        if not subject_id:
            continue

        # Age: may be numeric or string in participants.tsv
        age_val = row.get("age", "unknown")
        if pd.isna(age_val) or str(age_val).strip() == "":
            age = "unknown"  # LLM 推断，需人类复核
        else:
            age = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)

        # Sex: typically 'm'/'f' or 'male'/'female' in BIDS
        sex_val = row.get("sex", row.get("gender", "unknown"))
        if pd.isna(sex_val) or str(sex_val).strip() == "":
            sex = "unknown"  # LLM 推断，需人类复核
        else:
            sex_lower = str(sex_val).strip().lower()
            if sex_lower in ["m", "male"]:
                sex = "male"
            elif sex_lower in ["f", "female"]:
                sex = "female"
            else:
                sex = "unknown"  # LLM 推断，需人类复核

        subject_dict[subject_id] = {
            "age": age,
            "sex": sex,
            "handedness": "unknown",  # LLM 推断，需人类复核 - handedness not in participants.tsv
        }

    return subject_dict


# =============================================================================
# Channel Name Mapping (219 channels)
# Based on standard 10-20 system with extended coverage
# Source: Dataset documentation, DOI: 10.1016/j.neuroimage.2022.118873
# Annotator: LLM (from paper methodology), 2026-04-08
# =============================================================================
# 219 channels suggests extended 10-20 system with additional sites
# Standard 10-20 has 21 electrodes; 219 suggests high-density coverage
# Common in BioSemi 256 or similar systems with reduced channel count

# Build channel rename map for various possible naming conventions
def _build_channel_rename_map(ch_names: List[str]) -> Dict[str, str]:
    """Build rename map for 219-channel EEG systems to standard 10-20 names.

    Handles common naming conventions:
    - 'EEG 001' -> 'Fp1'
    - 'EEG-001' -> 'Fp1'
    - 'E1' -> standard names
    - BioSemi-style naming
    - EGI-style naming
    """
    rename_map: Dict[str, str] = {}

    # Standard 10-20 electrode names
    standard_1020 = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
        "T9", "T7", "T8", "T10",
        "TP9", "TP7", "TP1", "TPz", "TP2", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO3", "POz", "PO4", "PO8", "PO10",
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
        # Additional common extended sites for 219-channel systems
        "AF11", "AF12", "F9", "F10", "FCL1", "FCL2", "FCL3", "FCL4", "FCL5", "FCL6",
        "FC1", "FC2", "FC3", "FC4", "FC5", "FC6", "FCz",
        "CCP1", "CCP2", "CCP3", "CCP4", "CCP5", "CCP6", "CCP7", "CCP8",
        "CP1", "CP2", "CP3", "CP4", "CP5", "CP6", "CPz",
        "CPP1", "CPP2", "CPP3", "CPP4", "CPP5", "CPP6", "CPP7", "CPP8",
        "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
        "PO1", "PO2", "PO4", "PO5", "PO6",
        "O9", "O10",
    ]

    # Try multiple patterns
    patterns = [
        # Pattern: 'EEG 001' or 'EEG001' -> pad to 3 digits
        lambda n: f"EEG {n:03d}" if n.isdigit() else None,
        lambda n: f"EEG{n:03d}" if n.isdigit() else None,
        lambda n: f"EEG-{n:03d}" if n.isdigit() else None,
        # Pattern: 'E1', 'E2' -> keep as is
        lambda n: f"E{n}" if n.isdigit() else None,
        # Pattern: 'Ch1', 'CH1' -> pad to 2-3 digits
        lambda n: f"Ch{n:02d}" if n.isdigit() else None,
        lambda n: f"CH{n:02d}" if n.isdigit() else None,
    ]

    existing_names = set(ch_names)

    # Build mapping based on what exists in the data
    for name in ch_names:
        # Skip non-EEG channels
        if any(skip in name.upper() for skip in ["EOG", "ECG", "EMG", "REF", "MISC", "STIM", "TRIG", "AUX", "ACC"]):
            continue

        # Try to match against standard names
        name_clean = name.strip()

        # Direct match with standard names (case-insensitive)
        for std in standard_1020:
            if name_clean.lower() == std.lower():
                if name != std:
                    rename_map[name] = std
                break

        # Try numeric patterns
        if name_clean.startswith("EEG"):
            # Extract number
            rest = name_clean[3:].strip()
            if rest.isdigit():
                idx = int(rest)
                # Map to standard based on position (simplified mapping)
                if idx <= len(standard_1020):
                    rename_map[name] = standard_1020[idx - 1]

    return rename_map


# =============================================================================
# Event Mapping
# Based on events.tsv from BIDS structure
# =============================================================================
_EMOTION_EVENT_IDS = {
    "anger": 0,
    "awe": 1,
    "compassion": 2,
    "content": 3,
    "disgust": 4,
    "excite": 5,
    "fear": 6,
    "frustration": 7,
    "grief": 8,
    "happy": 9,
    "jealousy": 10,
    "joy": 11,
    "love": 12,
    "relax": 13,
    "relief": 14,
    "sad": 15,
}

# Administrative/utility events (not part of 15-class classification)
_UTILITY_EVENTS = {
    "press": "button_press",
    "press1": "button_press_offset",
    "enter": "enter",
    "exit": "exit",
    "InitialInstructions": "instructions",
    "InstructionsForEnding": "instructions_end",
    "ImaginationSuggestions": "imagination_suggestions",
    "FeelingItInstructionsButton": "feeling_instructions",
    "FeelingItInstructionsNoButton": "feeling_instructions_no_button",
    "ExitThankYou": "exit_thankyou",
    "prebase": "pre_baseline",
    "prebase_instruct": "pre_baseline_instruct",
    "postbase": "post_baseline",
    "postbase_instruct": "post_baseline_instruct",
}


def _load_events_tsv(file_path: str) -> pd.DataFrame:
    """Load events from BIDS events.tsv file."""
    events_path = file_path.replace(".eeg", "_events.tsv").replace(".edf", "_events.tsv")
    events_path = events_path.replace(".vhdr", "_events.tsv").replace(".bdf", "_events.tsv")

    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    return pd.DataFrame()


def _create_annotations_from_events(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.Annotations:
    """Convert events.tsv to MNE annotations with standardized event labels."""
    if events_df.empty or "onset" not in events_df.columns:
        return raw.annotations

    onsets = []
    durations = []
    descriptions = []

    for _, event in events_df.iterrows():
        onset = float(event.get("onset", 0))
        duration = float(event.get("duration", 0))

        # Get event description - check common column names
        desc = str(event.get("trial_type", event.get("value", event.get("event", "unknown"))))

        # Map to standardized labels
        desc_lower = desc.lower().strip()
        if desc_lower in _EMOTION_EVENT_IDS:
            descriptions.append(desc_lower)
        elif desc_lower in _UTILITY_EVENTS:
            descriptions.append(_UTILITY_EVENTS[desc_lower])
        else:
            descriptions.append(desc_lower)

        onsets.append(onset)
        durations.append(duration if not np.isnan(duration) else 0)

    return mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )


class OpenNeuroDS003004Kernel:
    """Stage1 kernel for openneuro ds003004 - Imagined Emotion Study.

    Parameters
    ----------
    udataset : EEGUnity dataset context
    raw : MNE Raw object
    row : locator row with file_path

    Returns
    -------
    mne.io.BaseRaw with updated metadata and annotations
    """

    KERNEL_ID: str = "openneuro-ds003004-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        # Get dataset path from row or udataset
        dataset_path = getattr(udataset, "path", os.path.dirname(row.get("file_path", "")))

        # Extract subject ID
        file_path = row.get("file_path", "")
        subject_id = "unknown"
        if "sub-" in file_path:
            parts = file_path.split("sub-")
            if len(parts) > 1:
                subject_id = parts[1].split("/")[0].split("\\")[0]
        elif hasattr(row, "get"):
            subject_id = row.get("subject_id", "unknown")

        # Load subject info
        subject_info = _load_participants_tsv(dataset_path).get(subject_id, {})
        age = subject_info.get("age", "unknown")  # LLM 推断，需人类复核
        sex = subject_info.get("sex", "unknown")  # LLM 推断，需人类复核
        handedness = subject_info.get("handedness", "unknown")

        # Device metadata - not available in dataset
        # Source: Dataset documentation, DOI: 10.1016/j.neuroimage.2022.118873
        amplifier = "unknown"  # LLM 推断，需人类复核 - likely BrainAmp or similar
        cap = "unknown"  # LLM 推断，需人类复核 - likely Ag/AgCl

        # Store original description
        original_desc = raw.info.get("description", "")

        # Write eegunity_description
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels before set_montage
        ch_names = raw.ch_names
        rename_map = _build_channel_rename_map(ch_names)

        if rename_map:
            # Only rename if we have valid mappings
            valid_renames = {k: v for k, v in rename_map.items() if v in mne.channels.get_builtin_montages()}
            if valid_renames:
                try:
                    raw.rename_channels(valid_renames)
                except Exception:
                    pass  # Skip if rename fails

        # Try to set montage if channels were renamed to standard names
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If standard montage fails, try extended
            try:
                montage = mne.channels.make_standard_montage("standard_alphabetic")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Keep original if no montage matches

        # Load and set annotations from events.tsv
        events_df = _load_events_tsv(file_path)
        if not events_df.empty:
            annotations = _create_annotations_from_events(raw, events_df)
            raw.set_annotations(annotations)
        else:
            # If no events.tsv, keep original annotations if any
            pass

        # Update channel types for known non-EEG channels
        for i, ch_name in enumerate(raw.ch_names):
            ch_name_lower = ch_name.lower()
            if any(x in ch_name_lower for x in ["eog", "ecg", "emg"]):
                try:
                    raw.set_channel_types({ch_name: "eog" if "eog" in ch_name_lower else "misc"})
                except Exception:
                    pass

        return raw


KERNEL = OpenNeuroDS003004Kernel()