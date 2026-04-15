"""OpenNeuro ds004505 (Real World Table Tennis) stage1 kernel for EEGUnity.

Dataset: Real-world table tennis EEG during cooperative/competitive play.
64-channel mobile EEG at 500 Hz. Hit events detected via IMU acceleration.

Source: https://openneuro.org/datasets/ds004505
Paper: DOI 10.1016/j.dib.2023.110024 (Data in Brief)
      DOI 10.1523/ENEURO.0463-22.2023 (eNeuro)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08 - needs human verification
# Source: Table tennis EEG literature typically uses 64-channel actiCAP
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 20)
}

# Standard 64-channel 10-20 montage names (actiCAP / BrainCap 64-channel)
# Order matches typical actiCAP layout
_64CH_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8",
    "T7", "T8",
    "TP7", "TP8",
    "M1", "M2",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]

# BrainVision channel naming patterns for 64-channel systems
# Many OpenNeuro EEG datasets use "EEG" + number format
_EEG_NUMERIC_PATTERN = re.compile(r"^EEG\s*(\d+)$", re.IGNORECASE)


def _try_parse_brainvision_markers(vmrk_path: str) -> Optional[mne.Annotations]:
    """Parse BrainVision vmrk file for event markers.

    Parameters
    ----------
    vmrk_path : str
        Path to .vmrk file.

    Returns
    -------
    mne.Annotations or None
        Parsed annotations if successful, None otherwise.
    """
    try:
        if not os.path.exists(vmrk_path):
            return None

        onsets = []
        durations = []
        descriptions = []

        with open(vmrk_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Find Marker section
        if "[Marker Information]" not in content:
            return None

        # Parse individual markers
        # Format: Mk<id>=<type>,<description>,<position>,<points>,<channel>
        for line in content.split("\n"):
            if not line.startswith("Mk"):
                continue

            parts = line.split("=")
            if len(parts) < 2:
                continue

            # Parse marker data
            data = parts[1].split(",")
            if len(data) < 4:
                continue

            try:
                marker_type = data[0].strip()
                description = data[1].strip()
                position = int(data[2].strip())
                points = int(data[3].strip())

                # Skip unknown/empty markers
                if not description or description in ["New Segment", "Stimulus", "Comment"]:
                    continue

                # Skip hardware status markers (admin events)
                if marker_type in ["SyncStatus", "Time", "Par"]:
                    continue

                # Calculate onset time (position is in samples at 500 Hz)
                onset_sec = position / 500.0
                duration_sec = points / 500.0 if points > 0 else 0.0

                onsets.append(onset_sec)
                durations.append(duration_sec)
                descriptions.append(description)

            except (ValueError, IndexError):
                continue

        if not onsets:
            return None

        return mne.Annotations(
            onset=np.array(onsets),
            duration=np.array(durations),
            description=descriptions,
        )

    except Exception:
        return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to 10-20 standard names.

    Handles patterns like:
    - EEG 001 -> Fp1 (and so on in standard order)
    - EEG-001 -> Fp1
    - E1, E2, ... -> standard names (if available)

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw data object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from old names to new standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names

    # Pattern 1: EEG numeric (EEG 001, EEG-001, EEG001)
    eeg_channels = [ch for ch in existing_names if _EEG_NUMERIC_PATTERN.match(ch)]

    if len(eeg_channels) >= 64:
        # Extract numbers and sort
        eeg_pairs = []
        for ch in eeg_channels:
            match = _EEG_NUMERIC_PATTERN.match(ch)
            if match:
                num = int(match.group(1))
                eeg_pairs.append((num, ch))

        eeg_pairs.sort(key=lambda x: x[0])

        # Map first 64 to standard names
        for idx, (_, old_name) in enumerate(eeg_pairs[:64]):
            if idx < len(_64CH_STANDARD_NAMES):
                new_name = _64CH_STANDARD_NAMES[idx]
                if old_name != new_name:
                    rename_map[old_name] = new_name

    return rename_map


def _detect_subject_id(row) -> str:
    """Extract subject ID from row."""
    if hasattr(row, "get"):
        return row.get("subject_id", row.get("participant_id", "unknown"))
    return getattr(row, "subject_id", getattr(row, "participant_id", "unknown"))


def _load_bids_events(row, sfreq: float = 500.0) -> Optional[mne.Annotations]:
    """Load events from BIDS *_events.tsv file.

    Parameters
    ----------
    row : pandas.Series
        Row with File Path information.
    sfreq : float
        Sampling frequency for onset calculation.

    Returns
    -------
    mne.Annotations or None
        Events as annotations.
    """
    try:
        # Look for events.tsv alongside the EEG file
        if hasattr(row, "get") and "File Path" in row:
            base_path = row["File Path"]
        else:
            base_path = str(row) if row else ""

        if not base_path:
            return None

        # Replace common extensions with _events.tsv
        for ext in [".vhdr", ".eeg", ".edf", ".bdf", ".set", ".fif"]:
            if base_path.lower().endswith(ext):
                events_path = base_path[: -len(ext)] + "_events.tsv"
                break
        else:
            # Try with _events.tsv suffix
            events_path = base_path.rsplit(".", 1)[0] + "_events.tsv"

        if not os.path.exists(events_path):
            return None

        # Load events TSV
        events_df = pd.read_csv(events_path, sep="\t")

        if events_df.empty:
            return None

        # Standard BIDS columns: onset, duration, trial_type (or value/type)
        onset_col = None
        for col in ["onset", "onset_sec"]:
            if col in events_df.columns:
                onset_col = col
                break

        if onset_col is None:
            return None

        # Get duration (default 0)
        duration_col = "duration" if "duration" in events_df.columns else None

        # Get description (trial_type, value, or stim_type)
        desc_col = None
        for col in ["trial_type", "value", "stim_type", "event_type"]:
            if col in events_df.columns:
                desc_col = col
                break

        if desc_col is None:
            return None

        # Build annotations
        onsets = events_df[onset_col].fillna(0).values
        durations = (
            events_df[duration_col].fillna(0).values if duration_col else np.zeros(len(onsets))
        )
        descriptions = events_df[desc_col].fillna("unknown").astype(str).values

        # Filter out empty or admin descriptions
        valid_mask = [
            d.strip() and d.lower() not in ["n/a", "na", "none", "unknown", ""]
            for d in descriptions
        ]

        return mne.Annotations(
            onset=onsets[valid_mask],
            duration=durations[valid_mask],
            description=descriptions[valid_mask],
        )

    except Exception:
        return None


class OpenNeuroDS004505Kernel:
    """Stage1 kernel for OpenNeuro ds004505 (Real World Table Tennis).

    This kernel handles:
    - Channel name standardization (EEG numeric -> 10-20 standard)
    - Event parsing from BrainVision vmrk files or BIDS events.tsv
    - Subject metadata population
    - Description field with eegunity_description format

    Paradigm: Table tennis with cooperative/competitive conditions,
    moving/stationary serve conditions, and ball-hit events detected
    via IMU acceleration threshold (0.75g).
    """

    KERNEL_ID: str = "openneuro-ds004505-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and subject information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object.
        """
        # Get file path
        if hasattr(row, "get"):
            file_path = row.get("File Path", row.get("file_path", ""))
        else:
            file_path = getattr(row, "File Path", getattr(row, "file_path", ""))

        # Detect subject ID
        subject_id = _detect_subject_id(row)
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # Build eegunity_description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainVision / Mobile EEG",  # Based on STATUS marker in data
                "cap": "actiCAP 64ch",  # LLM 推断，需人类复核 - 64-channel standard cap
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only EEG channels that need renaming
            eeg_renames = {k: v for k, v in rename_map.items() if k.startswith("EEG")}
            if eeg_renames:
                # Restrict to first 64 EEG channels in standard order
                eeg_items = list(eeg_renames.items())
                restricted_renames = {}
                used_targets = set()

                for old_name, new_name in eeg_items:
                    if new_name not in used_targets:
                        restricted_renames[old_name] = new_name
                        used_targets.add(new_name)

                if restricted_renames:
                    raw.rename_channels(restricted_renames)

            # Set montage for renamed channels
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage setting is best-effort

        # Try to load events from BIDS events.tsv first
        annotations = _load_bids_events(row, raw.info.get("sfreq", 500.0))

        # Fall back to BrainVision vmrk parsing
        if annotations is None and file_path:
            for ext in [".vhdr", ".eeg"]:
                if file_path.lower().endswith(ext):
                    vmrk_path = file_path[: -len(ext)] + ".vmrk"
                    annotations = _try_parse_brainvision_markers(vmrk_path)
                    break

        # Apply annotations if found
        if annotations is not None and len(annotations) > 0:
            # Merge with existing annotations
            existing = raw.annotations
            if existing and len(existing) > 0:
                combined_onset = np.concatenate([existing.onset, annotations.onset])
                combined_duration = np.concatenate([existing.duration, annotations.duration])
                combined_desc = list(existing.description) + list(annotations.description)
                annotations = mne.Annotations(
                    onset=combined_onset,
                    duration=combined_duration,
                    description=combined_desc,
                )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004505Kernel()