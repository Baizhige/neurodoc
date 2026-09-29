"""OpenNeuro DS005403 Delayed Auditory Feedback EEG/EGG stage1 kernel for EEGUnity.

Dataset: Delayed Auditory Feedback EEG/EGG
Source: https://openneuro.org/datasets/ds005403
Paradigm: Speech production with DAF (Delayed Auditory Feedback)
Channels: EEG + EGG (electroglottography) + audio/misc channels
Sampling Rate: 1000 Hz
Subjects: 66

Event Structure:
- baseline: Baseline (no delay) speech block
- adaption: Adaptation DAF condition block
- random1: Random delay condition 1 block
- random2: Random delay condition 2 block

Native misc channels: audio, audio_envelope, audio_onsets, egg, egg_envelope
Derived misc channels: delay, detected_delay (from events.tsv)

Required info fields from participants.tsv: hand, sex

Source: DOI 10.1523/jneurosci.2294.24.2025
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Native misc channels that should be present in raw data
_NATIVE_MISC_CHANNELS = ["audio", "audio_envelope", "audio_onsets", "egg", "egg_envelope"]


def _get_dataset_root(file_path: str) -> str:
    """Traverse upward to find BIDS dataset root (contains participants.tsv)."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at filesystem root
        if os.path.exists(os.path.join(current_dir, "participants.tsv")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return current_dir


def _load_participant_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Load participant info from participants.tsv."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
    }

    if not os.path.exists(participants_path):
        return info

    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Normalize subject_id for matching
        search_id = subject_id
        if not search_id.startswith("sub-"):
            search_id = f"sub-{search_id}"

        # Try to find matching row
        mask = df["participant_id"] == search_id
        if not mask.any():
            # Try without sub- prefix
            mask = df["participant_id"] == subject_id

        if mask.any():
            row = df[mask].iloc[0]

            # Age: not present in this dataset
            if "age" in row and pd.notna(row["age"]):
                info["age"] = str(int(float(row["age"])))
            # Age is missing in this dataset per analysis.md

            # Sex
            if "sex" in row and pd.notna(row["sex"]):
                sex_val = str(row["sex"]).strip().lower()
                if sex_val in ("m", "male"):
                    info["sex"] = "male"
                elif sex_val in ("f", "female"):
                    info["sex"] = "female"
                else:
                    info["sex"] = "unknown"

            # Handedness from 'hand' column
            if "hand" in row and pd.notna(row["hand"]):
                hand_val = str(row["hand"]).strip().lower()
                if hand_val in ("r", "right"):
                    info["handedness"] = "right"
                elif hand_val in ("l", "left"):
                    info["handedness"] = "left"
                else:
                    info["handedness"] = "unknown"
    except Exception:
        pass

    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    base = os.path.splitext(file_path)[0]
    # Try standard BIDS naming
    events_path = base.replace("_eeg", "_events").replace(".set", "_events.tsv")
    if not events_path.endswith("_events.tsv"):
        events_path = base + "_events.tsv"

    if os.path.exists(events_path):
        return events_path

    # Also try without replacement for edge cases
    alt_path = base.rsplit("_", 1)[0] + "_events.tsv"
    if os.path.exists(alt_path):
        return alt_path

    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    fname_base = os.path.basename(base)
    # Extract subject and task info
    for f in os.listdir(eeg_dir):
        if f.endswith("_events.tsv"):
            return os.path.join(eeg_dir, f)

    return None


def _load_events_df(events_path: str) -> Optional[pd.DataFrame]:
    """Load events.tsv file."""
    if not events_path or not os.path.exists(events_path):
        return None
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _create_step_function_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame,
                                  column: str, channel_name: str) -> mne.io.BaseRaw:
    """Create a derived misc channel from events.tsv column as step function.

    For each trial interval [onset, onset+duration), set value to the column value.
    Between trials use 0.
    """
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    data = np.zeros((1, n_samples))

    if column not in events_df.columns:
        # Skip creating this channel if source column is not available
        return raw

    for _, evt_row in events_df.iterrows():
        onset = float(evt_row["onset"])
        duration = float(evt_row.get("duration", 0))
        value = evt_row[column]

        # Convert to sample indices
        start_idx = int(onset * sfreq)
        if start_idx < 0:
            start_idx = 0
        end_idx = int((onset + duration) * sfreq) if duration > 0 else n_samples
        if end_idx > n_samples:
            end_idx = n_samples

        # Handle numeric conversion
        try:
            if pd.isna(value):
                val = 0.0
            else:
                val = float(value)
        except (ValueError, TypeError):
            val = 0.0

        if start_idx < n_samples:
            data[0, start_idx:end_idx] = val

    info = mne.create_info([channel_name], sfreq, ch_types=["misc"])
    new_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    raw.add_channels([new_raw], force_update_info=True)
    return raw


def _events_to_annotations(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Convert events.tsv to MNE Annotations.

    Uses trial_type or value column for description, onset and duration for timing.
    HC-5: No remapping or renaming of event IDs — pass literal tsv labels through.
    """
    if events_df is None or len(events_df) == 0:
        return raw

    # Determine description column — use trial_type if available (carries meaningful labels)
    desc_col = None
    for col in ["trial_type", "value", "stim_type"]:
        if col in events_df.columns:
            desc_col = col
            break

    if desc_col is None:
        return raw

    onsets = []
    durations = []
    descriptions = []

    for _, evt_row in events_df.iterrows():
        onset = float(evt_row["onset"])
        duration = float(evt_row.get("duration", 0))
        desc = str(evt_row[desc_col])

        # Pass literal strings through without remapping (HC-5 compliant)
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)

    # Remove existing annotations and add new ones
    annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
    raw.set_annotations(annotations)

    return raw


@dataclass
class OpenNeuroDS005403Kernel:
    """Stage1 kernel for OpenNeuro DS005403 (Delayed Auditory Feedback EEG/EGG)."""

    KERNEL_ID: str = "openneuro-ds005403-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path`` and ``Subject ID``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object.
        """
        file_path = row["File Path"]
        subject_id = row.get("Subject ID", "")

        # Load participant info from participants.tsv
        dataset_root = _get_dataset_root(file_path)
        subject_info = _load_participant_info(dataset_root, subject_id)

        # Load events.tsv for this file
        events_path = _find_events_tsv(file_path)
        events_df = _load_events_df(events_path)

        # Update description with metadata
        # inferred by LLM, needs human review: amplifier and cap values inferred from dataset documentation
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": subject_info.get("handedness", "unknown"),
                "dataset": "openneuro-ds005403",
                "paradigm": "delayed_auditory_feedback",
                "task": "daf",
            },
        }

        # Set description
        raw.info["description"] = json.dumps(description_dict)

        # Add derived misc channels from events.tsv numeric columns
        if events_df is not None:
            # Add delay channel (from events.tsv:delay)
            raw = _create_step_function_channel(raw, events_df, "delay", "delay")
            # Add detected_delay channel (from events.tsv:detected_delay)
            raw = _create_step_function_channel(raw, events_df, "detected_delay", "detected_delay")

        # Convert events.tsv to annotations — BrainVision .eeg files may not carry
        # their own triggers if the .vmrk marker file is missing or empty, so we
        # always populate from the companion events.tsv to ensure events are present.
        if events_df is not None:
            raw = _events_to_annotations(raw, events_df)

        return raw


KERNEL = OpenNeuroDS005403Kernel()