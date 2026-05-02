"""OpenNeuro DS004350 stage1 kernel for EEGUnity.

Executive Functioning Study for Assessing the Effect of Neurofeedback.
Contains N-back (NB1/NB2/NB3), Local-Global (LG), and SART paradigms.

Source: https://openneuro.org/datasets/ds004350
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


# Annotator: LLM, 2026-04-08
# Source: Dataset README / paper descriptions
# Amplifier inferred from common EEG labs using 64-channel systems at 256 Hz
_DEVICE_AMPLIFIER = "unknown"  # inferred by LLM, needs human review

# Annotator: LLM, 2026-04-08
# Source: Standard EEG research practice for cognitive paradigms
_CAP_MATERIAL = "unknown"  # inferred by LLM, needs human review


def _load_subject_info(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from BIDS participants.tsv.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping from subject_id (e.g., "sub-001") to metadata dict with
        keys: age, sex, handedness, group.
    """
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    subject_info: Dict[str, Dict[str, str]] = {}

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", ""))
                if not subj_id.startswith("sub-"):
                    subj_id = f"sub-{subj_id}"

                # Normalize sex to lowercase
                raw_sex = str(row.get("sex", "unknown")).strip().lower()
                if raw_sex not in ("male", "female"):
                    raw_sex = "unknown"

                # Age handling
                raw_age = str(row.get("age", "unknown")).strip()
                if raw_age in ("nan", "", "NA", "None"):
                    raw_age = "unknown"

                # Handedness
                raw_handed = str(row.get("handedness", "unknown")).strip().lower()
                if raw_handed not in ("right", "left", "ambidextrous"):
                    raw_handed = "unknown"

                # Group (required info field)
                raw_group = str(row.get("group", "unknown")).strip()
                if raw_group in ("nan", "", "NA", "None"):
                    raw_group = "unknown"

                subject_info[subj_id] = {
                    "age": raw_age,
                    "sex": raw_sex,
                    "handedness": raw_handed,
                    "group": raw_group,
                }
        except Exception:
            pass

    return subject_info


def _detect_task_from_filename(file_path: str) -> Optional[str]:
    """Detect BIDS task from filename.

    Returns
    -------
    str or None
        Task name: "NB1", "NB2", "NB3", "LG", "SART", or None.
    """
    basename = os.path.basename(file_path)
    match = re.search(r"task-([A-Za-z0-9]+)", basename)
    if match:
        return match.group(1).upper()
    return None


def _build_channel_rename_map_64(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 64-channel EEG caps.

    Common 64-channel layouts use names like EEG-0..EEG-63 or 1..64.
    Maps to standard 10-20 naming where possible.
    """
    rename_map: Dict[str, str] = {}

    # Standard 64-channel extended 10-20 layout
    # Source: BrainCap 64 channel layout (common in neurofeedback studies)
    # Annotator: LLM, 2026-04-08; inferred by LLM, needs human review
    _STANDARD_64_NAMES = [
        "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AF4", "AF8", "F7",
        "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
        "FT8", "T7", "C5", "C3", "C1", "Cz", "C2", "C4",
        "C6", "T8", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2",
        "CP4", "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz",
        "P2", "P4", "P6", "P8", "PO7", "PO3", "POz", "PO4",
        "PO8", "O1", "Oz", "O2", "Iz"
    ]

    existing = set(raw.ch_names)

    # Try numbered EEG channels (EEG-0..EEG-63 or 0..63)
    for i in range(64):
        for prefix in [f"EEG-{i}", str(i), f"Ch{i+1}", f"CH{i+1}"]:
            if prefix in existing and i < len(_STANDARD_64_NAMES):
                rename_map[prefix] = _STANDARD_64_NAMES[i]
                break

    # Also handle common named patterns
    name_patterns = {
        "Fp1": ["Fp1", "FP1"],
        "Fpz": ["Fpz", "FPz"],
        "Fp2": ["Fp2", "FP2"],
        "AF7": ["AF7"],
        "AF3": ["AF3"],
        "AF4": ["AF4"],
        "AF8": ["AF8"],
        "F7": ["F7"],
        "F5": ["F5"],
        "F3": ["F3"],
        "F1": ["F1"],
        "Fz": ["Fz", "FZ"],
        "F2": ["F2"],
        "F4": ["F4"],
        "F6": ["F6"],
        "F8": ["F8"],
        "FT7": ["FT7"],
        "FC5": ["FC5"],
        "FC3": ["FC3"],
        "FC1": ["FC1"],
        "FCz": ["FCz", "FCZ"],
        "FC2": ["FC2"],
        "FC4": ["FC4"],
        "FC6": ["FC6"],
        "FT8": ["FT8"],
        "T7": ["T7"],
        "C5": ["C5"],
        "C3": ["C3"],
        "C1": ["C1"],
        "Cz": ["Cz", "CZ"],
        "C2": ["C2"],
        "C4": ["C4"],
        "C6": ["C6"],
        "T8": ["T8"],
        "TP7": ["TP7"],
        "CP5": ["CP5"],
        "CP3": ["CP3"],
        "CP1": ["CP1"],
        "CPz": ["CPz", "CPZ"],
        "CP2": ["CP2"],
        "CP4": ["CP4"],
        "CP6": ["CP6"],
        "TP8": ["TP8"],
        "P7": ["P7"],
        "P5": ["P5"],
        "P3": ["P3"],
        "P1": ["P1"],
        "Pz": ["Pz", "PZ"],
        "P2": ["P2"],
        "P4": ["P4"],
        "P6": ["P6"],
        "P8": ["P8"],
        "PO7": ["PO7"],
        "PO3": ["PO3"],
        "POz": ["POz", "POZ"],
        "PO4": ["PO4"],
        "PO8": ["PO8"],
        "O1": ["O1"],
        "Oz": ["Oz", "OZ"],
        "O2": ["O2"],
        "Iz": ["Iz", "IZ"],
    }

    for target, variants in name_patterns.items():
        for v in variants:
            if v in existing and v != target and v not in rename_map:
                rename_map[v] = target
                break

    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = file_path.replace(".vhdr", "").replace(".eeg", "").replace(".edf", "").replace(".set", "").replace(".fif", "")
    # BIDS naming: sub-XXX[_ses-YYY]_task-ZZZ[_run-RR]_eeg.<ext>
    # events.tsv: sub-XXX[_ses-YYY]_task-ZZZ[_run-RR]_events.tsv
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv

    # Try without run suffix
    base_no_run = re.sub(r"_run-\d+", "", base)
    events_tsv = base_no_run + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv

    return None


def _load_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Load events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, task: Optional[str]) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations.

    Uses paradigm prefix for event descriptions to disambiguate across tasks.
    """
    onsets = []
    durations = []
    descriptions = []

    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0))
        if pd.isna(duration):
            duration = 0.0

        # Build description with paradigm prefix
        trial_type = str(row.get("trial_type", "")) if "trial_type" in row else ""
        value = str(row.get("value", "")) if "value" in row else ""

        if task and value:
            desc = f"{task}: {value}"
        elif task and trial_type:
            desc = f"{task}: {trial_type}"
        elif value:
            desc = value
        elif trial_type:
            desc = trial_type
        else:
            desc = "unknown"

        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _find_response_time_columns(events_df: pd.DataFrame) -> List[str]:
    """Find response time columns in events dataframe."""
    rt_cols = []
    for col in events_df.columns:
        if "response_time" in col.lower():
            rt_cols.append(col)
    return rt_cols


def _add_derived_misc_channel(raw: mne.io.BaseRaw, name: str, data: np.ndarray) -> None:
    """Add a derived misc channel to the raw object."""
    info = mne.create_info([name], raw.info["sfreq"], ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, info)
    raw.add_channels([raw_misc], force_update_info=True)


@dataclass
class OpenNeuroDS004350:
    """Stage-1 kernel for OpenNeuro ds004350.

    Executive Functioning Study for Assessing the Effect of Neurofeedback.
    """

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_root = row.get("dataset_root", udataset.dataset_path if hasattr(udataset, "dataset_path") else "")
        file_path = row.get("file_path", "")

        # Get subject ID from row or file path
        subject_id = row.get("subject_id", "")
        if not subject_id and file_path:
            match = re.search(r"(sub-\d+)", file_path)
            if match:
                subject_id = match.group(1)

        # Load subject info from participants.tsv
        subject_info = _load_subject_info(dataset_root)
        subj_meta = subject_info.get(subject_id, {})

        # Detect task
        task = _detect_task_from_filename(file_path)

        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map_64(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass

        # Load events from events.tsv
        events_tsv_path = _find_events_tsv(file_path)
        events_df = None
        if events_tsv_path:
            events_df = _load_events_tsv(events_tsv_path)
            if events_df is not None:
                # Add annotations from events.tsv
                annotations = _events_to_annotations(events_df, task)
                raw.set_annotations(annotations)

                # Create derived misc channels for response times from events.tsv
                rt_cols = _find_response_time_columns(events_df)
                for col in rt_cols:
                    # Create a trial-locked step function for response time
                    data = np.zeros((1, len(raw.times)))
                    if "onset" in events_df.columns and col in events_df.columns:
                        for _, ev_row in events_df.iterrows():
                            onset = float(ev_row.get("onset", 0))
                            rt_val = ev_row.get(col, np.nan)
                            if pd.isna(rt_val):
                                continue
                            rt_val = float(rt_val)
                            # Find sample index for onset
                            onset_idx = int(onset * raw.info["sfreq"])
                            if 0 <= onset_idx < len(raw.times):
                                # Fill from onset to onset + response_time
                                end_idx = int((onset + rt_val) * raw.info["sfreq"])
                                end_idx = min(end_idx, len(raw.times))
                                if end_idx > onset_idx:
                                    data[0, onset_idx:end_idx] = rt_val
                                else:
                                    # If RT is 0 or negative, just mark the onset
                                    data[0, onset_idx] = rt_val

                    # Add as misc channel
                    _add_derived_misc_channel(raw, col, data)

        # Create required derived misc channels based on task
        # Map task to derived channel name and check for response_time in events.tsv
        task_to_channel = {
            "NB1": "response_time_nb1",
            "NB2": "response_time_nb2",
            "LG": "response_time_lg",
        }

        current_task = task.upper() if task else None
        if current_task in task_to_channel and events_df is not None and "response_time" in events_df.columns:
            channel_name = task_to_channel[current_task]
            
            # Create trial-locked step function for response_time
            data = np.zeros((1, len(raw.times)))
            for _, ev_row in events_df.iterrows():
                onset = float(ev_row.get("onset", 0))
                rt_val = ev_row.get("response_time", np.nan)
                if pd.isna(rt_val):
                    continue
                rt_val = float(rt_val)
                onset_idx = int(onset * raw.info["sfreq"])
                if 0 <= onset_idx < len(raw.times):
                    end_idx = int((onset + rt_val) * raw.info["sfreq"])
                    end_idx = min(end_idx, len(raw.times))
                    if end_idx > onset_idx:
                        data[0, onset_idx:end_idx] = rt_val
                    else:
                        data[0, onset_idx] = rt_val
            
            # Only add if we found valid response time data
            if np.any(data != 0) or np.any(~np.isnan(events_df["response_time"].values)):
                _add_derived_misc_channel(raw, channel_name, data)

        # Set eegunity_description
        eegunity_description = {
            "age": subj_meta.get("age", "unknown"),
            "sex": subj_meta.get("sex", "unknown"),
            "amplifier": _DEVICE_AMPLIFIER,
            "cap": _CAP_MATERIAL,
            "handedness": subj_meta.get("handedness", "unknown"),
        }

        # Store description in raw.info as a custom field
        raw.info["eegunity_description"] = eegunity_description

        return raw


KERNEL = OpenNeuroDS004350()