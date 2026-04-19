"""OpenNeuro ds005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 1 - Large-scale multi-task developmental
battery collected from children and adolescents (ages 5.2-21.7). Contains resting-state,
movie watching, contrast detection, surrounding suppression, sequence learning, and
symbol search paradigms. Uses BioSemi 128-channel system at 500 Hz.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1016/j.neuroimage.2020.117001
          https://doi.org/10.1101/2024.10.03.615261
          https://www.nature.com/articles/sdata201740

Channel naming: BioSemi standard 128-channel layout (EEG001-EEG128)
Events: BIDS events.tsv format with HED annotations
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
# CHANNEL RENAME MAP - BioSemi 128-channel to standard naming
# Source: HBN dataset documentation, BioSemi standard layout
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
# ============================================================================
_BIOSEMI_CHANNEL_MAP: Dict[str, str] = {}
for i in range(1, 129):
    _BIOSEMI_CHANNEL_MAP[f"EEG{i:03d}"] = f"EEG{i:03d}"


# ============================================================================
# SUBJECT INFO - From participants.tsv (BIDS standard)
# Source: participants.tsv in dataset root
# Annotator: Human, 2026-04-08
# ============================================================================
_SUBJECT_INFO_CACHE: Dict[str, Dict[str, str]] = {}
_DATASET_ROOT_CACHE: Optional[str] = None


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv for subject metadata."""
    pth = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(pth):
        return pd.read_csv(pth, sep="\t")
    return pd.DataFrame()


def _get_subject_info(udataset, row) -> Dict[str, str]:
    """Get subject metadata from participants.tsv.

    Returns
    -------
    dict with keys: age, sex, handedness
    """
    global _DATASET_ROOT_CACHE

    subject_id = row.get("subject_id", "")
    if not subject_id:
        file_path = row.get("file_path", row.get("File Path", ""))
        match = re.search(r"sub-([A-Z0-9]+)", file_path)
        if match:
            subject_id = match.group(1)

    if subject_id in _SUBJECT_INFO_CACHE:
        return _SUBJECT_INFO_CACHE[subject_id]

    if udataset is not None:
        dataset_root = str(udataset.get("dataset_root", ""))
    else:
        dataset_root = ""

    if not dataset_root and _DATASET_ROOT_CACHE:
        dataset_root = _DATASET_ROOT_CACHE

    if dataset_root:
        _DATASET_ROOT_CACHE = dataset_root

    df = _load_participants_tsv(dataset_root)

    info = {"age": "unknown", "sex": "unknown", "handedness": "unknown", "amplifier": "BioSemi", "cap": "Ag/AgCl"}

    if not df.empty and "participant_id" in df.columns:
        df["participant_id_norm"] = df["participant_id"].str.replace("sub-", "", regex=False)
        match_row = df[df["participant_id_norm"] == subject_id]
        if not match_row.empty:
            row_data = match_row.iloc[0]

            if "age" in row_data and pd.notna(row_data["age"]):
                age_val = row_data["age"]
                if isinstance(age_val, (int, float)):
                    info["age"] = str(int(age_val))
                elif isinstance(age_val, str):
                    info["age"] = age_val.strip()

            if "sex" in row_data and pd.notna(row_data["sex"]):
                sex_val = str(row_data["sex"]).lower().strip()
                if sex_val in ["m", "male"]:
                    info["sex"] = "male"
                elif sex_val in ["f", "female"]:
                    info["sex"] = "female"
                else:
                    info["sex"] = "unknown"

            if "handedness" in row_data and pd.notna(row_data["handedness"]):
                handed_val = str(row_data["handedness"]).lower().strip()
                if handed_val in ["r", "right", "right-handed"]:
                    info["handedness"] = "right"
                elif handed_val in ["l", "left", "left-handed"]:
                    info["handedness"] = "left"
                else:
                    info["handedness"] = "unknown"

    _SUBJECT_INFO_CACHE[subject_id] = info
    return info


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename BioSemi channels to standard names if needed."""
    existing_names = raw.ch_names
    rename_map = {}

    for ch in existing_names:
        if ch.startswith("EEG") and len(ch) == 6:
            rename_map[ch] = ch
        elif ch in _BIOSEMI_CHANNEL_MAP:
            rename_map[ch] = _BIOSEMI_CHANNEL_MAP[ch]

    if rename_map:
        rename_list = [(old, new) for old, new in rename_map.items() if old != new]
        if rename_list:
            raw.rename_channels(dict(rename_list))

    return raw


def _set_montage_if_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage if BioSemi 128-channel layout."""
    try:
        montage = mne.channels.make_standard_montage("biosemi128")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass
    return raw


def _get_events_file_path(raw, row) -> Optional[str]:
    """Find corresponding events.tsv file for the EEG file."""
    file_path = row.get("file_path", row.get("File Path", ""))
    if not file_path:
        return None

    base_dir = os.path.dirname(file_path)
    eeg_file = os.path.basename(file_path)

    events_file = eeg_file.replace("_eeg.fif", "_events.tsv")
    events_path = os.path.join(base_dir, events_file)

    if os.path.exists(events_path):
        return events_path

    events_file = eeg_file.replace("_eeg.edf", "_events.tsv")
    events_path = os.path.join(base_dir, events_file)

    if os.path.exists(events_path):
        return events_path

    for fname in os.listdir(base_dir):
        if fname.endswith("_events.tsv"):
            return os.path.join(base_dir, fname)

    return None


def _derive_trial_accuracy_from_events(events_path: str) -> Dict[int, float]:
    """Derive trial accuracy from events.tsv correct_answer column.

    For contrast detection trials, match user_answer to correct_answer.
    Returns dict mapping onset sample index to accuracy (1.0 or 0.0).
    """
    trial_accuracy = {}

    if not events_path or not os.path.exists(events_path):
        return trial_accuracy

    try:
        events_df = pd.read_csv(events_path, sep="\t")

        if "trial_type" not in events_df.columns:
            return trial_accuracy

        contrast_trials = events_df[events_df["trial_type"] == "contrastTrial_start"]

        for idx, trial_row in contrast_trials.iterrows():
            trial_onset = trial_row.get("onset")
            if pd.isna(trial_onset):
                continue

            correct_answer = trial_row.get("correct_answer")
            user_answer = trial_row.get("user_answer")

            if pd.isna(correct_answer) or pd.isna(user_answer):
                accuracy = 0.0
            elif int(correct_answer) == int(user_answer):
                accuracy = 1.0
            else:
                accuracy = 0.0

            trial_accuracy[idx] = accuracy

    except Exception:
        pass

    return trial_accuracy


def _create_accuracy_channel(raw: mne.io.BaseRaw, trial_accuracy: Dict[int, float]) -> mne.io.BaseRaw:
    """Create a misc channel for trial accuracy if derived data available."""
    if not trial_accuracy:
        return raw

    n_samples = raw.n_times
    accuracy_data = np.zeros(n_samples)

    sfreq = raw.info["sfreq"]

    for idx, accuracy in trial_accuracy.items():
        accuracy_data[int(idx)] = accuracy

    info = mne.create_info(
        ch_names=["trial_accuracy"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    accuracy_raw = mne.io.RawArray(accuracy_data.reshape(1, -1), info)
    raw.add_channels([accuracy_raw], force_equal_channels=False)

    return raw


def _process_raw_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Ensure raw annotations use canonical event names."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    current_desc = set(raw.annotations.description)

    event_rename_map = {
        "contrastChangeB1_start": "contrastChangeB1_start",
        "contrastChangeB2_start": "contrastChangeB2_start",
        "contrastChangeB3_start": "contrastChangeB3_start",
        "contrastTrial_start": "contrastTrial_start",
        "dot_no1_OFF": "dot_no1_OFF",
        "dot_no1_ON": "dot_no1_ON",
        "dot_no2_OFF": "dot_no2_OFF",
        "dot_no2_ON": "dot_no2_ON",
        "dot_no3_OFF": "dot_no3_OFF",
        "dot_no3_ON": "dot_no3_ON",
        "dot_no4_OFF": "dot_no4_OFF",
        "dot_no4_ON": "dot_no4_ON",
        "dot_no5_OFF": "dot_no5_OFF",
        "dot_no5_ON": "dot_no5_ON",
        "dot_no6_OFF": "dot_no6_OFF",
        "dot_no6_ON": "dot_no6_ON",
        "dot_no7_OFF": "dot_no7_OFF",
        "dot_no7_ON": "dot_no7_ON",
        "dot_no8_OFF": "dot_no8_OFF",
        "dot_no8_ON": "dot_no8_ON",
        "fixpoint_ON": "fixpoint_ON",
        "instructed_toCloseEyes": "instructed_toCloseEyes",
        "instructed_toOpenEyes": "instructed_toOpenEyes",
        "learningBlock_1": "learningBlock_1",
        "learningBlock_2": "learningBlock_2",
        "learningBlock_3": "learningBlock_3",
        "learningBlock_4": "learningBlock_4",
        "learningBlock_5": "learningBlock_5",
        "left_buttonPress": "left_buttonPress",
        "left_target": "left_target",
        "newPage": "newPage",
        "resting_start": "resting_start",
        "right_buttonPress": "right_buttonPress",
        "right_target": "right_target",
        "seqLearning_start": "seqLearning_start",
        "seqLearning_stop": "seqLearning_stop",
        "stim_ON": "stim_ON",
    }

    new_descriptions = []
    for desc in raw.annotations.description:
        new_desc = event_rename_map.get(desc, desc)
        new_descriptions.append(new_desc)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time
    )
    raw.set_annotations(new_annotations)

    return raw


@dataclass
class HBNKernel:
    """Stage1 kernel for the Healthy Brain Network (HBN) EEG dataset."""

    KERNEL_ID: str = "hbn-eeg-release1-stage1"

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
            The modified Raw object with updated metadata and annotations.
        """
        subject_info = _get_subject_info(udataset, row)

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": subject_info.get("amplifier", "unknown"),
                "cap": subject_info.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        raw = _rename_channels(raw)

        raw = _set_montage_if_standard(raw)

        raw = _process_raw_annotations(raw)

        events_path = _get_events_file_path(raw, row)
        if events_path:
            trial_accuracy = _derive_trial_accuracy_from_events(events_path)
            if trial_accuracy:
                raw = _create_accuracy_channel(raw, trial_accuracy)

        return raw


KERNEL = HBNKernel()