"""Dataset-specific kernel for openneuro_ds003458.

Three Armed Bandit Gambling Task EEG dataset from OpenNeuro.
- 23 subjects, 66 channels, 500 Hz sampling rate
- BioSemi amplifier system
- Events: stimulus choices (Left/Right/Up), button responses, feedback outcomes (Win/Loss/Null)

Source: https://openneuro.org/datasets/ds003458 DOI: 10.18112/openneuro.ds003458.v1.1.0
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Subject metadata from participants.tsv
# Source: participants.tsv in dataset root
# Annotator: LLM, 2026-04-08, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Event code to human-readable label mapping for feedback outcomes
# Based on analysis.md Event Structure table
# S100 = Feedback Win (reward received)
# S 23 = Feedback Loss (no reward)
# S 32 = Feedback Null (neutral feedback)
# Source: dataset events.tsv analysis, DOI: 10.18112/openneuro.ds003458.v1.1.0
# Annotator: Human, 2026-04-08
_FEEDBACK_EVENT_MAP: Dict[str, str] = {
    "S100": "Feedback Win",
    "S 23": "Feedback Loss",
    "S 32": "Feedback Null",
    "S113": "Feedback Win",
    "S131": "Feedback Loss",
    "S212": "Feedback Win",
    "S221": "Feedback Loss",
}

# Stimulus choice event mapping
# Source: dataset events.tsv analysis, DOI: 10.18112/openneuro.ds003458.v1.1.0
# Annotator: Human, 2026-04-08
_STIMULUS_EVENT_MAP: Dict[str, str] = {
    "S  1": "Stimulus Left",
    "S  2": "Stimulus Right",
    "S  3": "Stimulus Up",
}

# Response event mapping
# Source: dataset events.tsv analysis, DOI: 10.18112/openneuro.ds003458.v1.1.0
# Annotator: Human, 2026-04-08
_RESPONSE_EVENT_MAP: Dict[str, str] = {
    "S  5": "Response",
}

# BioSemi default channel naming may include non-standard names
# Standard 1020 cap has 64 EEG channels + 2 EOG
# Source: BioSemi electrode layout documentation
# Annotator: LLM, 2026-04-08, needs human review
_STANDARD_EEG_CHANNELS = {
    "Fp1", "Fp2", "Fz", "F3", "F4", "F7", "F8",
    "FCz", "FC3", "FC4", "FC1", "FC2", "FC5", "FC6",
    "Cz", "C3", "C4", "C1", "C2", "C5", "C6",
    "CPz", "CP3", "CP4", "CP1", "CP2", "CP5", "CP6",
    "Pz", "P3", "P4", "P7", "P8", "P1", "P2",
    "POz", "PO3", "PO4", "PO7", "PO8", "PO1", "PO2",
    "O1", "O2", "Oz",
    "AFz", "AF3", "AF4", "AF7", "AF8",
    "F1", "F2", "F5", "F6",
    "FT7", "FT8", "TP7", "TP8",
    "T7", "T8", "T9", "T10",
    "P5", "P6",
    "PO5", "PO6",
}


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_id(row) -> str:
    """Extract subject ID from row file path."""
    file_path = row.get("File Path", "")
    match = re.search(r"sub-(\w+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _get_subject_info(row, dataset_root: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or defaults."""
    subject_id = _extract_subject_id(row)

    # Load participants if not already cached
    if not _SUBJECT_DICT:
        df = _load_participants_tsv(dataset_root)
        for _, participant_row in df.iterrows():
            pid = str(participant_row.get("participant_id", ""))
            if pid.startswith("sub-"):
                pid = pid[4:]  # Remove 'sub-' prefix
            age = str(participant_row.get("age", "unknown"))
            sex = str(participant_row.get("sex", "unknown")).lower()
            if sex not in ["male", "female"]:
                sex = "unknown"
            _SUBJECT_DICT[pid] = {"age": age, "sex": sex}

    subject_data = _SUBJECT_DICT.get(subject_id, {})
    return {
        "age": subject_data.get("age", "unknown"),
        "sex": subject_data.get("sex", "unknown"),
    }


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard names if needed."""
    existing = set(raw.ch_names)

    # Build rename map for non-standard BioSemi channel names
    rename_map: Dict[str, str] = {}

    for ch in existing:
        ch_upper = ch.upper()
        # Handle common BioSemi naming patterns
        # e.g., "EEG 001" -> "Fp1" or similar standard names
        if ch.startswith("EEG"):
            # Try to map based on position in the list
            idx = existing.index(ch) if ch in list(existing) else -1
            # BioSemi typically uses sequential naming
            # This is an approximation - actual mapping needs dataset documentation
            pass  # Keep original names unless documentation confirms mapping

    if rename_map:
        # Only rename if we have valid mappings
        valid_renames = {k: v for k, v in rename_map.items() if k in existing and v in _STANDARD_EEG_CHANNELS}
        if valid_renames:
            raw.rename_channels(valid_renames)

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 1020 montage for EEG channels."""
    try:
        # Try to set standard 1020 montage
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        # If montage setting fails, continue without it
        pass
    return raw


def _parse_events_tsv(row) -> Optional[pd.DataFrame]:
    """Parse events from events.tsv if available."""
    file_path = row.get("File Path", "")
    if not file_path:
        return None

    # Derive events.tsv path from EEG file path
    base_dir = os.path.dirname(file_path)
    eeg_file = os.path.basename(file_path)
    subject_match = re.search(r"(sub-\w+)", eeg_file)
    if not subject_match:
        return None

    subject_id = subject_match.group(1)
    events_path = os.path.join(base_dir, f"{subject_id}_events.tsv")

    # Also check in parent directories
    if not os.path.exists(events_path):
        events_path = os.path.join(os.path.dirname(base_dir), f"{subject_id}_events.tsv")

    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    return None


def _create_annotations_from_events(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Create MNE annotations from events.tsv data."""
    if events_df is None or events_df.empty:
        return raw

    sfreq = raw.info["sfreq"]

    # Standard BIDS events.tsv columns: onset, duration, trial_type, value, etc.
    onset_col = "onset" if "onset" in events_df.columns else events_df.columns[0]
    duration_col = "duration" if "duration" in events_df.columns else None
    value_col = "value" if "value" in events_df.columns else None
    trial_type_col = "trial_type" if "trial_type" in events_df.columns else None

    onsets = []
    durations = []
    descriptions = []

    for _, event_row in events_df.iterrows():
        try:
            onset = float(event_row[onset_col])
            onsets.append(onset)

            if duration_col and duration_col in event_row:
                dur = float(event_row[duration_col])
            else:
                dur = 0.0
            durations.append(dur)

            # Get event label - prefer trial_type, then value
            label = ""
            if trial_type_col and trial_type_col in event_row:
                label = str(event_row[trial_type_col])
            elif value_col and value_col in event_row:
                label = str(event_row[value_col])
            else:
                label = "unknown"

            # Map numeric codes to readable labels
            label_stripped = label.strip()
            if label_stripped in _FEEDBACK_EVENT_MAP:
                label = _FEEDBACK_EVENT_MAP[label_stripped]
            elif label_stripped in _STIMULUS_EVENT_MAP:
                label = _STIMULUS_EVENT_MAP[label_stripped]
            elif label_stripped in _RESPONSE_EVENT_MAP:
                label = _RESPONSE_EVENT_MAP[label_stripped]

            descriptions.append(label)
        except (ValueError, TypeError):
            continue

    if onsets:
        annotations = mne.Annotations(
            onset=np.array(onsets),
            duration=np.array(durations),
            description=descriptions,
        )
        raw.set_annotations(annotations)

    return raw


class OpenNeuroDS003458Kernel:
    """Stage1 kernel for OpenNeuro ds003458 Three Armed Bandit dataset."""

    KERNEL_ID: str = "openneuro-ds003458-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", os.path.dirname(os.path.dirname(file_path)))

        # Get subject metadata
        subject_info = _get_subject_info(row, dataset_root)

        # Get original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description
        # Amplifier: BioSemi system (from dataset documentation)
        # Cap: Ag/AgCl (BioSemi standard)
        # Source: OpenNeuro ds003458 dataset description
        # Annotator: LLM, 2026-04-08, needs human review
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BioSemi",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        raw = _rename_channels(raw)

        # Set standard 1020 montage
        raw = _set_montage_if_possible(raw)

        # Parse events from events.tsv and create annotations
        events_df = _parse_events_tsv(row)
        raw = _create_annotations_from_events(raw, events_df)

        return raw


KERNEL = OpenNeuroDS003458Kernel()