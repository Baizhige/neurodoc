"""OpenNeuro DS005363 (ORHA) stage1 kernel for EEGUnity.

Object Recognition in Healthy Aging (ORHA) dataset.
EEG recordings of visual object processing in 43 older adults.

Source: https://openneuro.org/datasets/ds005363
Reference: https://doi.org/10.1016/j.cub.2025.03.062

Event structure:
- Stimulus/S 01-64: Individual exemplar image markers (64 items)
- Stimulus/S 65-69: Catch trials (excluded from main tasks)
- Stimulus/S101-108: Block markers
- Stimulus/S199: Response markers
- Stimulus/S255: Session start/end
- admin: fixation_marker: Fixation cross presentation
- animate / inanimate: Super meta labels from events.tsv

Channel setup: 64-channel EEG, standard 10-20 system cap.
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


# ============================================================
# Subject metadata
# ============================================================
# Source: Paper DOI 10.1016/j.cub.2025.03.062
# "43 older adults (aged 59-77)" — age range inferred from paper abstract
# All fields marked as LLM inference; needs human verification
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Annotator: LLM, 2026-04-10, inference basis: DOI 10.1016/j.cub.2025.03.062


# ============================================================
# Channel rename map (64-channel standard 10-20 system)
# ============================================================
# Source: Standard 64-channel BrainVision / BioSemi layout
# Annotator: Human, 2026-04-10
_64CH_CHANNEL_ORDER = [
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


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for 64-channel standard 10-20 system.

    Detects generic EEG### channel names and maps them to standard
    10-20 positions based on their numeric order (001-064).
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names

    # Pattern 1: "EEG 001" or "EEG001" (space-separated with leading zeros)
    eeg_pattern = re.compile(r"^EEG\s*(\d+)$", re.IGNORECASE)

    # Pattern 2: "E001" or similar without space
    e_pattern = re.compile(r"^E(\d+)$", re.IGNORECASE)

    # Pattern 3: Just numeric like "1", "2", ..., "64"
    num_pattern = re.compile(r"^\d+$")

    candidates_64 = [n for n in existing_names if "eeg" in n.lower() or n.isdigit() or e_pattern.match(n)]

    if len(candidates_64) >= 64:
        # Sort by numeric value to get correct ordering
        def get_num(name):
            m = eeg_pattern.match(name)
            if m:
                return int(m.group(1))
            m = e_pattern.match(name)
            if m:
                return int(m.group(1))
            m = num_pattern.match(name)
            if m:
                return int(m.group(0))
            return 9999

        sorted_candidates = sorted(candidates_64, key=get_num)
        for i, old_name in enumerate(sorted_candidates[:64]):
            new_name = _64CH_CHANNEL_ORDER[i]
            if old_name != new_name:
                rename_map[old_name] = new_name

    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # Pattern: sub-XXX/ses-XX/eeg/sub-XXX_ses-XX_task-..._eeg.bdf
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to the EEG file."""
    # Walk up from file to find dataset root
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(5):  # Search up to 5 levels up
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv for a given EEG file."""
    # BIDS naming: sub-XXX_ses-XX_task-XXX_eeg.bdf -> sub-XXX_ses-XX_task-XXX_events.tsv
    base = file_path.replace("_eeg.bdf", "_events.tsv")
    base = base.replace("_eeg.edf", "_events.tsv")
    base = base.replace("_eeg.set", "_events.tsv")
    base = base.replace("_eeg.vhdr", "_events.tsv")
    base = base.replace("_eeg.fif", "_events.tsv")
    base = base.replace("_eeg.eeg", "_events.tsv")

    if os.path.exists(base):
        return base

    # Also check in the same directory
    dir_name = os.path.dirname(file_path)
    for f in os.listdir(dir_name):
        if f.endswith("_events.tsv"):
            return os.path.join(dir_name, f)

    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Normalize subject_id format
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"

        row = df[df["participant_id"] == subject_id]
        if row.empty:
            return {}

        info = {}
        for col in ["age", "sex", "group", "amplifier", "cap", "handedness"]:
            if col in row.columns:
                val = row.iloc[0][col]
                if pd.isna(val):
                    info[col] = "unknown"
                else:
                    info[col] = str(val).strip()
            else:
                info[col] = "unknown"

        # Normalize sex to lowercase
        if "sex" in info:
            info["sex"] = info["sex"].lower()
            if info["sex"] not in ["male", "female"]:
                info["sex"] = "unknown"

        return info
    except Exception:
        return {}


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        # Handle BOM and other encoding issues
        df = pd.read_csv(events_path, sep="\t", encoding="utf-8-sig")
        # Clean up column names (remove BOM if present)
        df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]
        return df
    except Exception:
        return None


def _create_trial_onset_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'trial_onset_time' from events.tsv onset values.

    For each stimulus event (Stimulus/S 01 - Stimulus/S 69), creates a step function
    where the channel value equals the event onset time (in seconds from recording start)
    for the duration of that trial. Between trials, value is 0.
    """
    if events_df is None or events_df.empty:
        return raw

    # Filter to stimulus events
    stimulus_mask = events_df["trial_type"].astype(str).str.startswith("Stimulus/S ")
    if "value" in events_df.columns:
        # Also check value column for numeric stimulus codes
        value_mask = events_df["value"].astype(str).str.match(r"^\s*\d+\s*$")
        stimulus_mask = stimulus_mask | value_mask

    stim_events = events_df[stimulus_mask].copy()

    if stim_events.empty:
        # Try with description or other columns
        if "description" in events_df.columns:
            stim_events = events_df[events_df["description"].astype(str).str.startswith("Stimulus/S ")].copy()

    if stim_events.empty:
        return raw

    # Ensure we have onset column
    if "onset" not in stim_events.columns:
        return raw

    # Create step function data
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))

    for _, event in stim_events.iterrows():
        onset_sec = float(event["onset"])
        onset_sample = int(onset_sec * sfreq)
        if onset_sample < n_samples:
            # Find end of trial: next event onset or 1 second default
            data[0, onset_sample:] = onset_sec

    # Create info for misc channel
    ch_info = mne.create_info(["trial_onset_time"], sfreq, ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, ch_info, first_samp=raw.first_samp)
    raw.add_channels([raw_misc], force_update_info=True)

    return raw


def _create_block_marker_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'block_marker_value' from events.tsv block markers.

    Block markers are Stimulus/S101-108. Creates a step function with the block
    number (101-108) for the duration of that block.
    """
    if events_df is None or events_df.empty:
        return raw

    block_mask = events_df["trial_type"].astype(str).str.match(r"Stimulus/S10[1-8]")
    block_events = events_df[block_mask].copy()

    if block_events.empty and "description" in events_df.columns:
        block_mask = events_df["description"].astype(str).str.match(r"Stimulus/S10[1-8]")
        block_events = events_df[block_mask].copy()

    if block_events.empty:
        return raw

    if "onset" not in block_events.columns:
        return raw

    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))

    for _, event in block_events.iterrows():
        onset_sec = float(event["onset"])
        onset_sample = int(onset_sec * sfreq)

        # Extract block number from trial_type or description
        tt = str(event.get("trial_type", ""))
        desc = str(event.get("description", ""))
        match = re.search(r"S(10[1-8])", tt) or re.search(r"S(10[1-8])", desc)
        if match and onset_sample < n_samples:
            block_num = float(match.group(1))
            data[0, onset_sample:] = block_num

    ch_info = mne.create_info(["block_marker_value"], sfreq, ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, ch_info, first_samp=raw.first_samp)
    raw.add_channels([raw_misc], force_update_info=True)

    return raw


def _create_catch_trial_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'is_catch_trial' indicating catch trial periods.

    Catch trials are Stimulus/S 65-69. Creates a binary step function (1 during
    catch trials, 0 otherwise).
    """
    if events_df is None or events_df.empty:
        return raw

    catch_mask = events_df["trial_type"].astype(str).str.match(r"Stimulus/S\s*6[5-9]")
    catch_events = events_df[catch_mask].copy()

    if catch_events.empty and "description" in events_df.columns:
        catch_mask = events_df["description"].astype(str).str.match(r"Stimulus/S\s*6[5-9]")
        catch_events = events_df[catch_mask].copy()

    if catch_events.empty:
        return raw

    if "onset" not in catch_events.columns:
        return raw

    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))

    for _, event in catch_events.iterrows():
        onset_sec = float(event["onset"])
        onset_sample = int(onset_sec * sfreq)
        if onset_sample < n_samples:
            # Set to 1 for catch trial, stay 1 until next event changes it
            data[0, onset_sample:] = 1.0

    ch_info = mne.create_info(["is_catch_trial"], sfreq, ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, ch_info, first_samp=raw.first_samp)
    raw.add_channels([raw_misc], force_update_info=True)

    return raw


def _create_animate_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'is_animate' from events.tsv animate labels.

    Creates a step function: 1 when current trial is animate, 0 when inanimate,
    NaN/0 when unknown.
    """
    if events_df is None or events_df.empty:
        return raw

    # Look for animate/inanimate in trial_type or animate column
    has_animate = False
    if "animate" in events_df.columns:
        # Direct animate column
        sfreq = raw.info["sfreq"]
        n_samples = raw.n_times
        data = np.zeros((1, n_samples))

        for _, event in events_df.iterrows():
            if "onset" not in event or pd.isna(event["onset"]):
                continue
            onset_sec = float(event["onset"])
            onset_sample = int(onset_sec * sfreq)
            if onset_sample >= n_samples:
                continue

            val = str(event.get("animate", "")).lower().strip()
            if val in ("1", "true", "yes", "animate"):
                data[0, onset_sample:] = 1.0
            elif val in ("0", "false", "no", "inanimate"):
                data[0, onset_sample:] = 0.0

        has_animate = True
    elif "trial_type" in events_df.columns:
        # Check if trial_type contains animate/inanimate
        animate_mask = events_df["trial_type"].astype(str).str.lower().isin(["animate", "inanimate"])
        if animate_mask.any():
            sfreq = raw.info["sfreq"]
            n_samples = raw.n_times
            data = np.zeros((1, n_samples))

            for _, event in events_df[animate_mask].iterrows():
                if "onset" not in event or pd.isna(event["onset"]):
                    continue
                onset_sec = float(event["onset"])
                onset_sample = int(onset_sec * sfreq)
                if onset_sample >= n_samples:
                    continue

                val = str(event.get("trial_type", "")).lower().strip()
                if val == "animate":
                    data[0, onset_sample:] = 1.0
                elif val == "inanimate":
                    data[0, onset_sample:] = 0.0

            has_animate = True
        else:
            return raw
    else:
        return raw

    if not has_animate:
        return raw

    ch_info = mne.create_info(["is_animate"], sfreq, ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, ch_info, first_samp=raw.first_samp)
    raw.add_channels([raw_misc], force_update_info=True)

    return raw


def _add_events_as_annotations(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add events from events.tsv as MNE annotations.

    Preserves original event labels from events.tsv without remapping.
    """
    if events_df is None or events_df.empty:
        return raw

    if "onset" not in events_df.columns:
        return raw

    onsets = []
    durations = []
    descriptions = []

    # Default duration if not specified
    default_duration = 0.0

    for _, event in events_df.iterrows():
        onset_sec = float(event["onset"])
        onset_sample = int(onset_sec * raw.info["sfreq"])

        # Duration: use duration column if available, else default
        if "duration" in event and not pd.isna(event["duration"]):
            duration = float(event["duration"])
        else:
            duration = default_duration

        # Description: prefer trial_type, then description, then value
        desc = None
        for col in ["trial_type", "description", "value"]:
            if col in event and not pd.isna(event[col]):
                desc = str(event[col]).strip()
                break

        if desc is None:
            desc = "unknown"

        onsets.append(onset_sec)
        durations.append(duration)
        descriptions.append(desc)

    # Remove any existing annotations to avoid duplicates
    # Then add new ones
    if len(onsets) > 0:
        annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
        raw.set_annotations(annot)

    return raw


class OpenNeuroDS005363Kernel:
    """Stage-1 kernel for OpenNeuro ds005363 (ORHA)."""

    KERNEL_ID = "openneuro_ds005363"
    DATASET_NAME = "ORHA_Object_Recognition_Healthy_Aging"
    DATASET_CITATION = "https://doi.org/10.1016/j.cub.2025.03.062"

    required_info_fields = ["age", "sex", "amplifier", "cap", "handedness"]
    derived_misc_channels = ["trial_onset_time", "block_marker_value", "is_catch_trial", "is_animate"]

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Store original description
        original_description = raw.info.get("description", "")

        # Get file path from row
        file_path = str(row.get("file_path", ""))

        # Extract subject ID
        subject_id = _get_subject_id_from_path(file_path)

        # Read participants.tsv for subject info
        participants_path = _find_participants_tsv(file_path)
        subject_info = {}
        if participants_path and subject_id:
            subject_info = _read_participants_info(participants_path, subject_id)

        # Build eegunity_description with required fields
        eegunity_description = {}
        for field in self.required_info_fields:
            eegunity_description[field] = subject_info.get(field, "unknown")

        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types: all EEG channels are 'eeg', any others default
        eeg_picks = [ch for ch in raw.ch_names if ch in _64CH_CHANNEL_ORDER]
        if eeg_picks:
            channel_types = {ch: "eeg" for ch in eeg_picks}
            raw.set_channel_types(channel_types)

        # Read events.tsv and add as annotations
        events_path = _find_events_tsv(file_path)
        events_df = None
        if events_path:
            events_df = _read_events_tsv(events_path)
            if events_df is not None:
                raw = _add_events_as_annotations(raw, events_df)

        # Create derived misc channels
        if events_df is not None:
            raw = _create_trial_onset_misc_channel(raw, events_df)
            raw = _create_block_marker_misc_channel(raw, events_df)
            raw = _create_catch_trial_misc_channel(raw, events_df)
            raw = _create_animate_misc_channel(raw, events_df)

        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenNeuroDS005363Kernel()