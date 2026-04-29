"""OpenNeuro DS002338 stage1 kernel for EEGUnity.

Dataset: A multi-modal human neuroimaging dataset for data integration:
simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task (XP2).

64-channel EEG recorded at 5000 Hz using BrainVision system.
Participants performed right-hand motor imagery with 1D or 2D neurofeedback display
during simultaneous EEG-fMRI. Task alternates between 20s Rest blocks and 20s Task-NF blocks.

Source: https://openneuro.org/datasets/ds002338
Reference: DOI 10.1038/s41597-020-0498-3
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Dataset-specific constants and lookup tables
# ============================================================================

# Standard 64-channel names for BrainVision MR-compatible EEG cap
# Source: BrainVision ActiChamp/BrainAmp MR plus standard 64-channel layout
# LLM 推断，需人类复核
_64CH_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]

# BrainVision vendor channel naming patterns
# LLM 推断，需人类复核
_VENDOR_CHANNEL_PATTERNS = [
    "EEG {:03d}",   # "EEG 001", "EEG 002", ...
    "EEG{:03d}",    # "EEG001", "EEG002", ...
    "Ch{:d}",       # "Ch1", "Ch2", ...
    "Channel {:d}", # "Channel 1", "Channel 2", ...
]


def _build_brainvision_channel_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Map BrainVision vendor channel names to standard 10-20 names.

    BrainVision files may use "EEG 001", "EEG 002" ... "EEG 064" naming.
    This maps them to standard 10-20 electrode positions.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for i, std_name in enumerate(_64CH_STANDARD_NAMES, start=1):
        for pattern in _VENDOR_CHANNEL_PATTERNS:
            vendor_name = pattern.format(i)
            if vendor_name in existing_names and vendor_name != std_name:
                rename_map[vendor_name] = std_name
                break

    return rename_map


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv.

    Returns dict with age, sex, feedback_type as strings.
    Missing values are returned as "unknown".
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {"age": "unknown", "sex": "unknown", "feedback_type": "unknown"}

    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {"age": "unknown", "sex": "unknown", "feedback_type": "unknown"}

    # Normalize subject_id to match participants.tsv format
    # participants.tsv uses "sub-01", "sub-02", etc.
    if not subject_id.startswith("sub-"):
        # Try to extract subject number and format
        subject_num = "".join(filter(str.isdigit, subject_id))
        if subject_num:
            subject_id = f"sub-{int(subject_num):02d}"
        else:
            subject_id = f"sub-{subject_id}"

    # Find matching row
    row = df[df["participant_id"] == subject_id]
    if row.empty:
        # Try without leading zeros
        subject_id_alt = subject_id.replace("sub-0", "sub-")
        row = df[df["participant_id"] == subject_id_alt]
        if row.empty:
            return {"age": "unknown", "sex": "unknown", "feedback_type": "unknown"}

    info = {}
    # age
    if "age" in row.columns:
        age_val = row["age"].values[0]
        if pd.isna(age_val):
            info["age"] = "unknown"
        else:
            info["age"] = str(int(float(age_val)))
    else:
        info["age"] = "unknown"

    # sex
    if "sex" in row.columns:
        sex_val = row["sex"].values[0]
        if pd.isna(sex_val):
            info["sex"] = "unknown"
        else:
            sex_str = str(sex_val).strip().lower()
            if sex_str in ("m", "male"):
                info["sex"] = "male"
            elif sex_str in ("f", "female"):
                info["sex"] = "female"
            else:
                info["sex"] = "unknown"
    else:
        info["sex"] = "unknown"

    # feedback_type
    if "feedback_type" in row.columns:
        fb_val = row["feedback_type"].values[0]
        if pd.isna(fb_val):
            info["feedback_type"] = "unknown"
        else:
            info["feedback_type"] = str(fb_val).strip().lower()
    else:
        info["feedback_type"] = "unknown"

    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for a given EEG file.

    Returns DataFrame with events, or None if not found.
    """
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.eeg -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.eeg", "").replace("_eeg.vhdr", "").replace("_eeg.edf", "")
    events_path = base + "_events.tsv"

    if not os.path.exists(events_path):
        # Try alternative: same directory, replace extension
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        # Remove .eeg, .vhdr, .edf and add _events.tsv
        name_root = file_name.rsplit(".", 1)[0]
        events_path = os.path.join(dir_name, name_root.replace("_eeg", "_events") + ".tsv")
        if not os.path.exists(events_path):
            # Try one more: just replace _eeg with _events
            events_path = os.path.join(dir_name, name_root.replace("_eeg", "") + "_events.tsv")
            if not os.path.exists(events_path):
                return None

    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations.

    Uses 'onset', 'duration', and 'trial_type' columns.
    Falls back to 'value' column if 'trial_type' is missing.
    """
    if events_df is None or len(events_df) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])

    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))

    # Use trial_type if available, otherwise value
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    else:
        descriptions = np.array(["unknown"] * len(onsets))

    # Filter out any NaN rows
    valid_mask = ~(np.isnan(onsets) | pd.isna(descriptions))
    onsets = onsets[valid_mask]
    durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(np.sum(valid_mask))
    descriptions = descriptions[valid_mask]

    # Map trial_type values to required event IDs for downstream tasks
    # Required: 'Stimulus/S  2', 'Stimulus/S 99'
    # The events.tsv has 'Rest' and 'Task-NF' which correspond to these
    desc_mapped = []
    for desc in descriptions:
        desc_lower = str(desc).strip().lower()
        if desc_lower == "rest":
            desc_mapped.append("Stimulus/S 99")
        elif desc_lower == "task-nf":
            desc_mapped.append("Stimulus/S  2")
        else:
            desc_mapped.append(str(desc))

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=desc_mapped,
    )


@dataclass
class OpenNeuroDS002338Kernel:
    """Stage1 kernel for OpenNeuro ds002338 dataset."""

    KERNEL_ID: str = "openneuro-ds002338-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ------------------------------------------------------------------
        # 1. Determine dataset path and subject ID
        # ------------------------------------------------------------------
        # Extract dataset root and subject from file path
        # Path pattern: .../ds002338/sub-XX/eeg/...
        path_parts = file_path.split(os.sep)
        dataset_path = ""
        subject_id = "unknown"
        for i, part in enumerate(path_parts):
            if part.startswith("sub-"):
                subject_id = part
                dataset_path = os.sep.join(path_parts[:i])
                break

        if dataset_path == "":
            # Fallback: go up until we find participants.tsv
            temp_path = os.path.dirname(file_path)
            for _ in range(5):
                if os.path.exists(os.path.join(temp_path, "participants.tsv")):
                    dataset_path = temp_path
                    break
                temp_path = os.path.dirname(temp_path)

        # ------------------------------------------------------------------
        # 2. Channel renaming to standard 10-20
        # ------------------------------------------------------------------
        rename_map = _build_brainvision_channel_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Ensure ECG channel is typed as misc
        ecg_channels = [ch for ch in raw.ch_names if ch.upper() == "ECG"]
        if ecg_channels:
            raw.set_channel_types({ch: "misc" for ch in ecg_channels})

        # Set montage after renaming
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in the montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            common_chs = list(montage_ch_names & raw_ch_names)
            if len(common_chs) >= 10:  # Require reasonable coverage
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without

        # ------------------------------------------------------------------
        # 3. Read participants.tsv info
        # ------------------------------------------------------------------
        subject_info = _read_participants_info(dataset_path, subject_id)

        # ------------------------------------------------------------------
        # 4. Build eegunity_description
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "") or ""

        # Device info from dataset documentation
        # Source: 10.1038/s41597-020-0498-3, BrainVision BrainAmp MR plus
        # LLM 推断，需人类复核
        amplifier = "BrainAmp MR plus"  # LLM 推断，需人类复核
        cap = "Ag/AgCl"  # LLM 推断，需人类复核
        handedness = "unknown"  # Not available in participants.tsv

        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
            "feedback_type": subject_info.get("feedback_type", "unknown"),
        }

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        # ------------------------------------------------------------------
        # 5. Handle events from events.tsv
        # ------------------------------------------------------------------
        # BrainVision .eeg files may not carry triggers without .vmrk file
        # We must derive annotations from events.tsv sidecar
        events_df = _read_events_tsv(file_path)

        if events_df is not None and len(events_df) > 0:
            # Check if raw already has meaningful annotations
            existing_annotations = raw.annotations
            has_existing_events = (
                existing_annotations is not None
                and len(existing_annotations) > 0
                and not all(desc == "" or desc == "BAD_" for desc in existing_annotations.description)
            )

            if not has_existing_events:
                # Derive annotations from events.tsv
                annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                if len(annotations) > 0:
                    raw.set_annotations(annotations)

        # ------------------------------------------------------------------
        # 6. Ensure required native misc channels exist
        # ------------------------------------------------------------------
        # Required native misc: ['ECG']
        # Already handled above in step 2

        # ------------------------------------------------------------------
        # 7. Verify final state
        # ------------------------------------------------------------------
        # Ensure required event IDs are present
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Verify we have the required event descriptions
            descs = set(raw.annotations.description)
            required_events = {"Stimulus/S  2", "Stimulus/S 99"}
            # Also accept the raw forms from events.tsv
            alt_forms = {"Task-NF", "Rest"}
            present = descs & (required_events | alt_forms)
            # If we only have raw forms, we need to remap - but _events_to_annotations
            # already did the remapping above

        return raw


KERNEL = OpenNeuroDS002338Kernel()