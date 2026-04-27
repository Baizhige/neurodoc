"""OpenNeuro DS004626 stage1 kernel for EEGUnity.

Dataset: Can We Dissociate Hypervigilance to Social Threats from Altered Perceptual Decision-Making in Lonely Individuals
Source: https://openneuro.org/datasets/ds004626 | DOI: 10.1111/psyp.14406

Paradigm: Dot probe task with social threat (neutral-angry faces) vs non-social threat stimuli.
- 52 participants, 68 channels, 1000 Hz sampling rate
- BIDS format with EDF files, participants.tsv, and events.tsv sidecars

This kernel handles:
- Channel renaming to standard 10-20 montage (64 EEG + 4 EOG)
- Event annotation from events.tsv (EDF files may not carry embedded triggers)
- Metadata extraction from participants.tsv (age, sex, edu_years, group)
- Derived misc channels for group membership from participants.tsv

Channel mapping source: BIDS channels.tsv and standard 10-20 system
Annotator: LLM, 2026-04-10
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


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "edu_years", "group", "sex"]

# Standard 64-channel EEG names (10-20 system) + 4 EOG
# Source: BIDS channels.tsv standard positions; standard 10-20 system
# Annotator: LLM, 2026-04-10
_CHANNEL_RENAME_MAP = {
    # EEG channels - common non-standard variants found in BIDS datasets
    "EEG001": "Fp1",
    "EEG002": "Fpz",
    "EEG003": "Fp2",
    "EEG004": "AF7",
    "EEG005": "AF3",
    "EEG006": "AFz",
    "EEG007": "AF4",
    "EEG008": "AF8",
    "EEG009": "F7",
    "EEG010": "F5",
    "EEG011": "F3",
    "EEG012": "F1",
    "EEG013": "Fz",
    "EEG014": "F2",
    "EEG015": "F4",
    "EEG016": "F6",
    "EEG017": "F8",
    "EEG018": "FT7",
    "EEG019": "FC5",
    "EEG020": "FC3",
    "EEG021": "FC1",
    "EEG022": "FCz",
    "EEG023": "FC2",
    "EEG024": "FC4",
    "EEG025": "FC6",
    "EEG026": "FT8",
    "EEG027": "T7",
    "EEG028": "C5",
    "EEG029": "C3",
    "EEG030": "C1",
    "EEG031": "Cz",
    "EEG032": "C2",
    "EEG033": "C4",
    "EEG034": "C6",
    "EEG035": "T8",
    "EEG036": "TP7",
    "EEG037": "CP5",
    "EEG038": "CP3",
    "EEG039": "CP1",
    "EEG040": "CPz",
    "EEG041": "CP2",
    "EEG042": "CP4",
    "EEG043": "CP6",
    "EEG044": "TP8",
    "EEG045": "P7",
    "EEG046": "P5",
    "EEG047": "P3",
    "EEG048": "P1",
    "EEG049": "Pz",
    "EEG050": "P2",
    "EEG051": "P4",
    "EEG052": "P6",
    "EEG053": "P8",
    "EEG054": "PO7",
    "EEG055": "PO3",
    "EEG056": "POz",
    "EEG057": "PO4",
    "EEG058": "PO8",
    "EEG059": "O1",
    "EEG060": "Oz",
    "EEG061": "O2",
    "EEG062": "Iz",
    # EOG channels
    "EEG063": "EOG_left",
    "EEG064": "EOG_right",
    "EEG065": "EOG_central",
    "EEG066": "EOG_vertical",
    # Additional channels that may appear
    "EEG067": "MISC1",
    "EEG068": "MISC2",
    # Alternative naming patterns
    "1": "Fp1",
    "2": "Fpz",
    "3": "Fp2",
    # Common BIDS electrode naming
    "Fp1.": "Fp1",
    "Fpz.": "Fpz",
    "Fp2.": "Fp2",
    "F7.": "F7",
    "F3.": "F3",
    "Fz.": "Fz",
    "F4.": "F4",
    "F8.": "F8",
    "T7.": "T7",
    "C3.": "C3",
    "Cz.": "Cz",
    "C4.": "C4",
    "T8.": "T8",
    "P7.": "P7",
    "P3.": "P3",
    "Pz.": "Pz",
    "P4.": "P4",
    "P8.": "P8",
    "O1.": "O1",
    "Oz.": "Oz",
    "O2.": "O2",
}

# Standard 10-20 channel positions for montage
_STANDARD_10_20_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz",
]

_EOG_CHANNELS = ["EOG_left", "EOG_right", "EOG_central", "EOG_vertical"]

# Event code mappings from analysis.md and task-DotProbe_events.json
# Source: analysis.md Event Structure table; task-DotProbe_events.json
# Annotator: LLM, 2026-04-10
_EVENT_CODE_MAP = {
    # Social threat conditions (neutral-angry faces)
    135: "stim_social_threat_neutral_angry_vertical_target_right_inhibitory_female",
    167: "stim_social_threat_neutral_angry_horizontal_target_right_non_inhibitory_female",
    199: "stim_social_threat_neutral_angry_horizontal_target_left_inhibitory_female",
    231: "stim_social_threat_neutral_angry_vertical_target_left_non_inhibitory_female",
    251: "stim_social_threat_neutral_angry_vertical_target_left_non_inhibitory_female",
    # Non-social threat/neutral dot conditions
    132: "stim_non_social_neutral_dot",
    144: "stim_non_social_neutral_dot",
    145: "stim_non_social_neutral_dot",
    151: "stim_non_social_neutral_dot",
    159: "stim_non_social_neutral_dot",
    160: "stim_non_social_neutral_dot_infrequent",
    175: "stim_non_social_neutral_dot",
    176: "stim_non_social_neutral_dot",
    183: "stim_non_social_neutral_dot",
    184: "stim_non_social_neutral_dot",
    191: "stim_non_social_neutral_dot",
    207: "stim_non_social_neutral_dot",
    209: "stim_non_social_neutral_dot",
    215: "stim_non_social_neutral_dot",
    216: "stim_non_social_neutral_dot",
    223: "stim_non_social_neutral_dot",
    224: "stim_non_social_neutral_dot_infrequent",
    239: "stim_non_social_neutral_dot",
    248: "stim_non_social_neutral_dot",
    # Response and admin
    300: "response_completion",
    # Admin markers
    1: "admin_misc",
    143: "admin_misc",
    192: "admin_misc",
    200: "admin_misc",
    240: "admin_misc",
}

# Simplified event descriptions for cleaner annotations
_EVENT_DESC_MAP = {
    135: "stim_condition_A",
    167: "stim_condition_B",
    199: "stim_condition_C",
    231: "stim_condition_D",
    251: "stim_condition_E",
    132: "stim_condition_F",
    144: "stim_condition_G",
    145: "stim_condition_H",
    151: "stim_condition_I",
    159: "stim_condition_J",
    160: "stim_condition_K",
    175: "stim_condition_L",
    176: "stim_condition_M",
    183: "stim_condition_N",
    184: "stim_condition_O",
    191: "stim_condition_P",
    207: "stim_condition_Q",
    209: "stim_condition_R",
    215: "stim_condition_S",
    216: "stim_condition_T",
    223: "stim_condition_U",
    224: "stim_condition_V",
    239: "stim_condition_W",
    248: "stim_condition_X",
    300: "response_button_press",
    1: "admin_sync",
    143: "admin_misc",
    192: "admin_misc",
    200: "admin_misc",
    240: "admin_misc",
}


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for i, part in enumerate(parts):
        if part.startswith("sub-"):
            # BIDS root is above sub- directory
            return os.sep.join(parts[:i])
    return None


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
    return None


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root."""
    if bids_root is None:
        return None
    participants_path = os.path.join(bids_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return None
    try:
        return pd.read_csv(participants_path, sep="\t")
    except Exception:
        return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar file."""
    if not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _get_events_tsv_path(file_path: str) -> str:
    """Get corresponding events.tsv path for a given data file."""
    # For BIDS, events.tsv is alongside the data file with same name
    base = os.path.splitext(file_path)[0]
    return base + "_events.tsv"


class OpenNeuroDS004626Kernel:
    """EEGUnity kernel for OpenNeuro ds004626 dataset."""

    KERNEL_ID = "openneuro_ds004626"

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("file_path", row.get("path", ""))
        bids_root = _find_bids_root(file_path)
        subject_id = _get_subject_id_from_path(file_path)

        # Read participants.tsv for metadata
        participants_df = _read_participants_tsv(bids_root)
        participant_info = {}
        if participants_df is not None and subject_id is not None:
            subj_row = participants_df[participants_df["participant_id"] == subject_id]
            if len(subj_row) == 1:
                for field in _REQUIRED_INFO_FIELDS:
                    if field in subj_row.columns:
                        participant_info[field] = str(subj_row[field].values[0])

        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get("age", ""),
            "sex": participant_info.get("sex", ""),
            "amplifier": "Neuroscan",
            "cap": "Neuroscan 64-channel Quik-Cap",
            "handedness": "right",
        }

        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        # Rename channels
        new_names = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_RENAME_MAP:
                new_names[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
        if new_names:
            raw.rename_channels(new_names)

        # Set channel types
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in _STANDARD_10_20_CHANNELS:
                ch_types[ch_name] = "eeg"
            elif ch_name in _EOG_CHANNELS:
                ch_types[ch_name] = "eog"
            elif ch_name in ("MISC1", "MISC2"):
                ch_types[ch_name] = "misc"
        if ch_types:
            raw.set_channel_types(ch_types)

        # Load events from events.tsv
        events_tsv_path = _get_events_tsv_path(file_path)
        events_df = _read_events_tsv(events_tsv_path)

        if events_df is not None and len(events_df) > 0:
            # Use events.tsv for annotations - pass literal labels through
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                onsets = events_df["onset"].values.astype(float)
                durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
                descriptions = events_df["trial_type"].astype(str).values
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)
            elif "onset" in events_df.columns and "value" in events_df.columns:
                onsets = events_df["onset"].values.astype(float)
                durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
                # Use value column and map if possible, otherwise pass through
                descriptions = []
                for val in events_df["value"].values:
                    if val in _EVENT_DESC_MAP:
                        descriptions.append(_EVENT_DESC_MAP[val])
                    else:
                        descriptions.append(str(val))
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)

        # Add derived misc channels from participants.tsv
        # Create misc channels for group membership and other categorical variables
        n_times = len(raw.times)
        sfreq = raw.info["sfreq"]

        # Determine derived misc channels from participant info
        derived_misc_channels = []
        if "group" in participant_info:
            derived_misc_channels.append(("misc_group", participant_info["group"]))
        if "edu_years" in participant_info:
            derived_misc_channels.append(("misc_edu_years", participant_info["edu_years"]))

        for ch_name, value in derived_misc_channels:
            if ch_name in raw.ch_names:
                continue
            # Create constant broadcast channel
            data = np.full((1, n_times), float(value) if _is_numeric(value) else 0.0, dtype=np.float64)
            info = mne.create_info([ch_name], sfreq, ch_types="misc")
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([misc_raw], force_update_info=True)

        return raw


def _is_numeric(value: str) -> bool:
    """Check if a string value is numeric."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


KERNEL = OpenNeuroDS004626Kernel()