"""OpenNeuro DS004577 stage1 kernel for EEGUnity.

Infant resting-state EEG dataset: 103 healthy infants (1-12 months),
128-channel high-density EEG, 500 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004577
Reference: 10.1038/s41597-024-03606-4
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 128-channel layout for infant high-density EEG caps.
# Source: BrainVision "Infant" montage (actiCAP 128ch infant layout)
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_INFANT_128_CHANNEL_LIST = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2", "Iz",
    "AFp9", "AFp7", "AFp5", "AFp3", "AFp1", "AFpz", "AFp2", "AFp4", "AFp6", "AFp8", "AFp10",
    "Fp1", "Fpz", "Fp2",  # duplicate check needed
    "I1", "I2",
    # Extended positions for 128ch layout
    "FFC1", "FFC2", "FFC3", "FFC4", "FFC5", "FFC6", "FFC7", "FFC8",
    "FCC1", "FCC2", "FCC3", "FCC4", "FCC5", "FCC6", "FCC7", "FCC8",
    "CCP1", "CCP2", "CCP3", "CCP4", "CCP5", "CCP6", "CCP7", "CCP8",
    "CPP1", "CPP2", "CPP3", "CPP4", "CPP5", "CPP6", "CPP7", "CPP8",
    "PPO1", "PPO2", "PPO3", "PPO4", "PPO5", "PPO6", "PPO7", "PPO8",
    "POO1", "POO2", "POO3", "POO4", "POO5", "POO6", "POO7", "POO8",
    "OI1", "OI2",
]

# Actually use a cleaner 128-channel list based on standard 10-10 extended
# Source: 10-5 system 128 channel layout (modified for infant caps)
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_STANDARD_128CH = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2", "Iz",
    "AFp9", "AFp7", "AFp5", "AFp3", "AFp1", "AFpz", "AFp2", "AFp4", "AFp6", "AFp8", "AFp10",
    "FFC1", "FFC2", "FFC3", "FFC4", "FFC5", "FFC6",
    "FCC1", "FCC2", "FCC3", "FCC4", "FCC5", "FCC6",
    "CCP1", "CCP2", "CCP3", "CCP4", "CCP5", "CCP6",
    "CPP1", "CPP2", "CPP3", "CPP4", "CPP5", "CPP6",
    "PPO1", "PPO2", "PPO3", "PPO4", "PPO5", "PPO6",
    "POO1", "POO2", "POO3", "POO4", "POO5", "POO6",
    "OI1", "OI2",
    "I1", "I2",
]


def _build_channel_rename_map(raw_ch_names: list) -> Dict[str, str]:
    """Build rename map for infant 128-channel EEG.

    Handles common alias patterns:
    - BrainVision: "Ch 001" -> standard name
    - EGI/GES: "E1", "E2" -> standard name
    - Numeric: "1", "2" -> standard name
    - BIDS: "EEG 001", "EEG-001" -> standard name

    Source: BrainVision actiCAP 128ch infant electrode layout documentation
    Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
    """
    rename_map: Dict[str, str] = {}
    used_targets = set()

    for ch in raw_ch_names:
        ch_stripped = ch.strip()
        target = None

        # Already standard name
        if ch_stripped in _STANDARD_128CH:
            continue

        # Pattern: "Ch 001" / "CH 001" / "Ch001"
        if ch_stripped.upper().startswith("CH"):
            suffix = ch_stripped[2:].strip()
            if suffix.isdigit():
                num = int(suffix)
                if 1 <= num <= 128:
                    target = _STANDARD_128CH[num - 1]

        # Pattern: "EEG 001" / "EEG-001" / "EEG001"
        elif ch_stripped.upper().startswith("EEG"):
            suffix = ch_stripped[3:].strip().lstrip("- ")
            if suffix.isdigit():
                num = int(suffix)
                if 1 <= num <= 128:
                    target = _STANDARD_128CH[num - 1]

        # Pattern: "E1", "E2" (EGI/GES format)
        elif ch_stripped.upper().startswith("E") and ch_stripped[1:].isdigit():
            num = int(ch_stripped[1:])
            if 1 <= num <= 128:
                target = _STANDARD_128CH[num - 1]

        # Pattern: plain "001", "002"
        elif ch_stripped.isdigit():
            num = int(ch_stripped)
            if 1 <= num <= 128:
                target = _STANDARD_128CH[num - 1]

        # Avoid duplicate target assignments
        if target is not None and target not in used_targets and target != ch_stripped:
            rename_map[ch] = target
            used_targets.add(target)

    return rename_map


def _read_participants_tsv(dataset_path: str, participant_id: str) -> Dict[str, str]:
    """Read participants.tsv and return info for given participant."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}

    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match participant_id format (e.g., "sub-01" or "01")
        mask = df["participant_id"] == participant_id
        if not mask.any():
            # Try without "sub-" prefix
            mask = df["participant_id"] == participant_id.replace("sub-", "")
        if not mask.any():
            # Try with "sub-" prefix
            mask = df["participant_id"] == "sub-" + participant_id.replace("sub-", "")

        if mask.any():
            row = df[mask].iloc[0]
            return {str(k): str(v) if pd.notna(v) else "unknown" for k, v in row.items()}
    except Exception:
        pass

    return {}


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read sibling events.tsv for given EEG file."""
    # Try multiple patterns to find the events.tsv file
    # Pattern 1: Direct replacement of _eeg.<ext> with _events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    
    if not os.path.exists(events_path):
        # Pattern 2: BIDS pattern in same directory
        dir_path = os.path.dirname(file_path)
        fname = os.path.basename(file_path)
        # Replace extension with _events.tsv
        name_part = fname.split("_eeg")[0] if "_eeg" in fname else fname.rsplit(".", 1)[0]
        events_path = os.path.join(dir_path, name_part + "_events.tsv")
    
    if not os.path.exists(events_path):
        # Pattern 3: Look for any _events.tsv in the same directory with matching subject/session
        dir_path = os.path.dirname(file_path)
        fname = os.path.basename(file_path)
        # Extract subject and session from filename
        parts = fname.split("_")
        sub_part = None
        ses_part = None
        for part in parts:
            if part.startswith("sub-"):
                sub_part = part
            elif part.startswith("ses-"):
                ses_part = part
        
        if sub_part:
            for f in os.listdir(dir_path):
                if f.endswith("_events.tsv"):
                    f_parts = f.split("_")
                    f_sub = None
                    f_ses = None
                    for fp in f_parts:
                        if fp.startswith("sub-"):
                            f_sub = fp
                        elif fp.startswith("ses-"):
                            f_ses = fp
                    
                    # Match by subject and optionally session
                    if f_sub == sub_part:
                        if ses_part is None or f_ses == ses_part:
                            events_path = os.path.join(dir_path, f)
                            break
    
    if not os.path.exists(events_path):
        # Pattern 4: Check parent directory (some BIDS layouts put events in parent)
        dir_path = os.path.dirname(file_path)
        parent_dir = os.path.dirname(dir_path)
        fname = os.path.basename(file_path)
        name_part = fname.split("_eeg")[0] if "_eeg" in fname else fname.rsplit(".", 1)[0]
        events_path = os.path.join(parent_dir, name_part + "_events.tsv")
        
        if not os.path.exists(events_path):
            # Try matching by subject in parent directory
            parts = fname.split("_")
            sub_part = None
            for part in parts:
                if part.startswith("sub-"):
                    sub_part = part
                    break
            
            if sub_part:
                for f in os.listdir(parent_dir) if os.path.isdir(parent_dir) else []:
                    if f.endswith("_events.tsv") and sub_part in f:
                        events_path = os.path.join(parent_dir, f)
                        break

    if os.path.exists(events_path):
        try:
            return pd.read_csv(events_path, sep="\t")
        except Exception:
            pass

    return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])

    onsets = events_df["onset"].values.astype(float)
    durations = events_df.get("duration", pd.Series([0.0] * len(events_df))).values.astype(float)
    
    # CRITICAL FIX: Use 'value' column for event descriptions, not 'trial_type'.
    # The 'value' column contains the actual trigger codes ('65', '66') that 
    # downstream tasks require. The 'trial_type' column contains descriptive 
    # strings like 'eyes_closed', 'discontinuity' which are NOT the required event IDs.
    # Per HC-5: do NOT remap or rename event IDs — pass literal tsv labels through.
    if "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = ["unknown"] * len(events_df)

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


@dataclass
class OpenNeuroDS004577Kernel:
    """Stage-1 kernel for OpenNeuro ds004577 infant resting-state EEG."""

    KERNEL_ID = "openneuro_ds004577"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract subject ID from file path or row
        file_path = str(row.get("file_path", ""))
        dataset_path = str(udataset.dataset_path) if hasattr(udataset, "dataset_path") else os.path.dirname(file_path)

        # Parse participant_id from file path (BIDS pattern: sub-XX/...)
        participant_id = ""
        parts = file_path.replace("\\", "/").split("/")
        for part in parts:
            if part.startswith("sub-"):
                participant_id = part
                break

        # Read participants.tsv info
        participant_info = _read_participants_tsv(dataset_path, participant_id)

        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": participant_info.get("amplifier", "unknown"),
            "cap": participant_info.get("cap", "unknown"),
            "handedness": participant_info.get("handedness", "unknown"),
        }

        # Store original description and set new description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        # Rename channels to standard 128ch names
        rename_map = _build_channel_rename_map(raw.ch_names)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Set montage if not already set
        if raw.get_montage() is None:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Pick only channels that exist in both raw and montage
                montage_ch_names = set(montage.ch_names)
                raw_ch_names = set(raw.ch_names)
                common_ch_names = list(raw_ch_names.intersection(montage_ch_names))
                if common_ch_names:
                    montage = montage.copy().pick_channels(common_ch_names)
                    raw = raw.set_montage(montage, match_case=False, on_missing="ignore")
            except Exception:
                pass

        # CRITICAL FIX: EDF files in this dataset have no native annotations/events.
        # Events MUST come from the sibling events.tsv files.
        # Read events.tsv and set annotations on the raw object.
        events_df = _read_events_tsv(file_path)
        if events_df is not None and not events_df.empty:
            annotations = _events_to_annotations(events_df, sfreq=raw.info["sfreq"])
            # Use set_annotations to properly attach annotations to raw
            # This ensures mne.events_from_annotations(raw) will work
            raw = raw.set_annotations(annotations)
        else:
            # If no events.tsv found, ensure annotations are at least initialized empty
            if raw.annotations is None:
                raw = raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))

        return raw


KERNEL = OpenNeuroDS004577Kernel()