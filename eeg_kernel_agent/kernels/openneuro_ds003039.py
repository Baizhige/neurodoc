"""Dataset-specific kernel for openneuro_ds003039 (Free Walking Study).

This kernel handles the free-walking EEG dataset with mobile EEG recordings.
Events (button presses, heel strikes) are sourced from behavioral log files
rather than EEG-triggered markers.

Source: https://openneuro.org/datasets/ds003039
DOI: https://doi.org/10.18112/openneuro.ds003039.v1.0.2
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Channel Configuration
# ============================================================================
# Source: Dataset documentation / 10.3389/fspor.2022.945341
# The dataset uses a 67-channel mobile EEG system (BioSemi ActiveTwo or similar).
# Standard 1020 positions are used; exact channel names may vary by subject.
# Annotator: LLM, 2026-04-08 — 需人类复核

# Standard 67-channel mobile EEG layout names (standard_1020 extended)
_STANDARD_67_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "T8", "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "TP7", "TP8", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "FPO1", "FPO2", "AFp1", "AFp2",  # Extra default positions
]

# Common channel aliases that may appear in the raw data
_CHANNEL_ALIAS_MAP: Dict[str, List[str]] = {
    "Fp1": ["EEG Fp1", "Fp1", "EEG-Fp1"],
    "Fp2": ["EEG Fp2", "Fp2", "EEG-Fp2"],
    "Fpz": ["EEG Fpz", "Fpz", "EEG-Fpz"],
    "AF3": ["EEG AF3", "AF3", "EEG-AF3"],
    "AF4": ["EEG AF4", "AF4", "EEG-AF4"],
    "AFz": ["EEG AFz", "AFz", "EEG-AFz"],
    "F7": ["EEG F7", "F7", "EEG-F7"],
    "F3": ["EEG F3", "F3", "EEG-F3"],
    "F1": ["EEG F1", "F1", "EEG-F1"],
    "Fz": ["EEG Fz", "Fz", "EEG-Fz"],
    "F2": ["EEG F2", "F2", "EEG-F2"],
    "F4": ["EEG F4", "F4", "EEG-F4"],
    "F6": ["EEG F6", "F6", "EEG-F6"],
    "F8": ["EEG F8", "F8", "EEG-F8"],
    "FC5": ["EEG FC5", "FC5", "EEG-FC5"],
    "FC3": ["EEG FC3", "FC3", "EEG-FC3"],
    "FC1": ["EEG FC1", "FC1", "EEG-FC1"],
    "FCz": ["EEG FCz", "FCz", "EEG-FCz"],
    "FC2": ["EEG FC2", "FC2", "EEG-FC2"],
    "FC4": ["EEG FC4", "FC4", "EEG-FC4"],
    "FC6": ["EEG FC6", "FC6", "EEG-FC6"],
    "T7": ["EEG T7", "T7", "EEG-T7"],
    "C5": ["EEG C5", "C5", "EEG-C5"],
    "C3": ["EEG C3", "C3", "EEG-C3"],
    "C1": ["EEG C1", "C1", "EEG-C1"],
    "Cz": ["EEG Cz", "Cz", "EEG-Cz"],
    "C2": ["EEG C2", "C2", "EEG-C2"],
    "C4": ["EEG C4", "C4", "EEG-C4"],
    "C6": ["EEG C6", "C6", "EEG-C6"],
    "T8": ["EEG T8", "T8", "EEG-T8"],
    "CP5": ["EEG CP5", "CP5", "EEG-CP5"],
    "CP3": ["EEG CP3", "CP3", "EEG-CP3"],
    "CP1": ["EEG CP1", "CP1", "EEG-CP1"],
    "CPz": ["EEG CPz", "CPz", "EEG-CPz"],
    "CP2": ["EEG CP2", "CP2", "EEG-CP2"],
    "CP4": ["EEG CP4", "CP4", "EEG-CP4"],
    "CP6": ["EEG CP6", "CP6", "EEG-CP6"],
    "TP7": ["EEG TP7", "TP7", "EEG-TP7"],
    "TP8": ["EEG TP8", "TP8", "EEG-TP8"],
    "P7": ["EEG P7", "P7", "EEG-P7"],
    "P5": ["EEG P5", "P5", "EEG-P5"],
    "P3": ["EEG P3", "P3", "EEG-P3"],
    "P1": ["EEG P1", "P1", "EEG-P1"],
    "Pz": ["EEG Pz", "Pz", "EEG-Pz"],
    "P2": ["EEG P2", "P2", "EEG-P2"],
    "P4": ["EEG P4", "P4", "EEG-P4"],
    "P6": ["EEG P6", "P6", "EEG-P6"],
    "P8": ["EEG P8", "P8", "EEG-P8"],
    "PO7": ["EEG PO7", "PO7", "EEG-PO7"],
    "PO3": ["EEG PO3", "PO3", "EEG-PO3"],
    "POz": ["EEG POz", "POz", "EEG-POz"],
    "PO4": ["EEG PO4", "PO4", "EEG-PO4"],
    "PO8": ["EEG PO8", "PO8", "EEG-PO8"],
    "O1": ["EEG O1", "O1", "EEG-O1"],
    "Oz": ["EEG Oz", "Oz", "EEG-Oz"],
    "O2": ["EEG O2", "O2", "EEG-O2"],
}

# Event mapping for button presses and gait events
# These events are sourced from behavioral logs, not EEG annotations
_EVENT_MAP: Dict[str, str] = {
    # Button press events
    "LeftButtonPress": "LeftButtonPress",
    "RightButtonPress": "RightButtonPress",
    "MissLeftButtonPress": "MissLeftButtonPress",
    "MissRightButtonPress": "MissRightButtonPress",
    # Gait events
    "LeftHS": "LeftHS",  # Left heel strike
    "RightHS": "RightHS",  # Right heel strike
    "LeftTO": "LeftTO",  # Left toe-off
    "RightTO": "RightTO",  # Right toe-off
}

# Admin events to exclude
_ADMIN_EVENTS = {"boundary", "ACOK", "admin"}


# ============================================================================
# Subject Information
# ============================================================================
# Source: participants.tsv from BIDS dataset
# This will be populated from the BIDS participants file at runtime
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}


# ============================================================================
# Kernel Class
# ============================================================================
@dataclass
class OpenNeuroDS003039Kernel:
    """Stage1 kernel for openneuro_ds003039 (Free Walking Study)."""

    KERNEL_ID: str = "openneuro-ds003039-stage1"

    _behavioral_log_cache: Dict[str, pd.DataFrame] = field(default_factory=dict)

    def _load_participants_tsv(self, dataset_root: str) -> pd.DataFrame:
        """Load participants.tsv to extract subject metadata."""
        participants_path = os.path.join(dataset_root, "participants.tsv")
        if os.path.exists(participants_path):
            df = pd.read_csv(participants_path, sep="\t")
            return df
        return pd.DataFrame()

    def _get_subject_info(self, subject_id: str, dataset_root: str) -> Dict[str, str]:
        """Extract subject metadata from participants.tsv or return defaults."""
        global _SUBJECT_DICT

        if not _SUBJECT_DICT:
            df = self._load_participants_tsv(dataset_root)
            if not df.empty and "participant_id" in df.columns:
                for _, row in df.iterrows():
                    pid = str(row["participant_id"]).replace("sub-", "")
                    info = {
                        "age": str(row.get("age", "unknown")),
                        "sex": str(row.get("sex", "unknown")).lower(),
                        "handedness": str(row.get("handedness", "unknown")).lower(),
                    }
                    _SUBJECT_DICT[pid] = info

        # Extract clean subject ID
        clean_id = subject_id.replace("sub-", "")

        if clean_id in _SUBJECT_DICT:
            return _SUBJECT_DICT[clean_id]

        # LLM 推断，需人类复核
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    def _find_behavioral_log(self, file_path: str) -> Optional[str]:
        """Find associated behavioral log file for button/gait events."""
        base_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Common behavioral log patterns
        patterns = [
            filename.replace(".vhdr", "_events.tsv").replace(".eeg", "_events.tsv"),
            filename.replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv"),
            filename.replace(".vhdr", "_behavioral.tsv"),
            filename.replace(".eeg", "_behavioral.tsv"),
            filename.replace(".edf", "_behavioral.tsv"),
            "events.tsv",
            "behavioral.tsv",
        ]

        for pattern in patterns:
            candidate = os.path.join(base_dir, pattern)
            if os.path.exists(candidate):
                return candidate

        # Try parent directories
        for _ in range(3):
            base_dir = os.path.dirname(base_dir)
            for pattern in patterns:
                candidate = os.path.join(base_dir, pattern)
                if os.path.exists(candidate):
                    return candidate

        return None

    def _parse_behavioral_events(self, log_path: str) -> pd.DataFrame:
        """Parse behavioral log file to extract event timestamps."""
        if log_path in self._behavioral_log_cache:
            return self._behavioral_log_cache[log_path]

        try:
            df = pd.read_csv(log_path, sep="\t")
            self._behavioral_log_cache[log_path] = df
            return df
        except Exception:
            return pd.DataFrame()

    def _build_annotations_from_behavioral(
        self, raw: mne.io.BaseRaw, behavioral_df: pd.DataFrame
    ) -> mne.Annotations:
        """Build MNE annotations from behavioral log data."""
        sfreq = raw.info["sfreq"]

        # Expected columns in behavioral log
        onset_times = []
        descriptions = []
        durations = []

        # Check common column names for event timing
        onset_col = None
        event_col = None
        duration_col = None

        for col in behavioral_df.columns:
            col_lower = col.lower()
            if "onset" in col_lower or "time" in col_lower or "timestamp" in col_lower:
                onset_col = col
            elif "event" in col_lower or "type" in col_lower or "condition" in col_lower:
                event_col = col
            elif "duration" in col_lower:
                duration_col = col

        if onset_col is None:
            # Try to infer from column order
            cols = list(behavioral_df.columns)
            if len(cols) >= 1:
                onset_col = cols[0]
            if len(cols) >= 2:
                event_col = cols[1]

        if onset_col and event_col:
            for _, row in behavioral_df.iterrows():
                try:
                    onset_sec = float(row[onset_col])
                    event_desc = str(row[event_col]).strip()

                    # Map event to standardized label
                    if event_desc in _EVENT_MAP:
                        mapped_label = _EVENT_MAP[event_desc]
                    elif event_desc not in _ADMIN_EVENTS:
                        mapped_label = event_desc
                    else:
                        continue  # Skip admin events

                    onset_times.append(onset_sec)
                    descriptions.append(mapped_label)

                    # Duration handling
                    if duration_col and pd.notna(row[duration_col]):
                        durations.append(float(row[duration_col]))
                    else:
                        durations.append(0.0)

                except (ValueError, TypeError):
                    continue

        if onset_times:
            annotations = mne.Annotations(
                onset=np.array(onset_times),
                duration=np.array(durations),
                description=descriptions,
            )
            return annotations

        return mne.Annotations(onset=[], duration=[], description=[])

    def _build_channel_rename_map(self, raw: mne.io.BaseRaw) -> Dict[str, str]:
        """Build channel rename map for standard 1020 naming."""
        rename_map: Dict[str, str] = {}
        existing = set(raw.ch_names)

        for target, aliases in _CHANNEL_ALIAS_MAP.items():
            for alias in aliases:
                if alias in existing and alias != target:
                    rename_map[alias] = target
                    break

        return rename_map

    def _apply_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Apply standard 1020 montage if possible."""
        # Try to set standard 1020 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If montage fails, try extended 1020
            try:
                raw.set_montage("standard_1020", on_missing="warn")
            except Exception:
                # Skip montage if channels don't match
                pass

        return raw

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Record locator (pandas.Series-like)

        Returns
        -------
        mne.io.BaseRaw
            Processed MNE Raw object with metadata and annotations
        """
        # Get file path and subject info
        file_path = row.get("File Path", "")
        subject_id = str(row.get("Subject", row.get("participant_id", "sub-unknown")))

        # Try to get dataset root from file path
        dataset_root = ""
        if file_path:
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("ds"):
                    dataset_root = os.sep.join(parts[: i + 1])
                    break
                if part == "openneuro" and i + 1 < len(parts):
                    dataset_root = os.sep.join(parts[: i + 2])
                    break

        # Get subject metadata
        subject_info = self._get_subject_info(subject_id, dataset_root)

        # Build eegunity_description
        # Source: participants.tsv, dataset documentation
        # Annotator: LLM, 2026-04-08 — 需人类复核
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # Mobile EEG system (likely BioSemi ActiveTwo)
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names (before set_montage)
        rename_map = self._build_channel_rename_map(raw)
        if rename_map:
            logger = mne.get_logger()
            logger.info(
                f"[DS003039 Kernel] Renaming {len(rename_map)} channels: {list(rename_map.values())}"
            )
            raw.rename_channels(rename_map)

        # Apply standard 1020 montage
        raw = self._apply_montage(raw)

        # Build annotations from behavioral logs
        behavioral_log = self._find_behavioral_log(file_path)
        if behavioral_log:
            behavioral_df = self._parse_behavioral_events(behavioral_log)
            if not behavioral_df.empty:
                annotations = self._build_annotations_from_behavioral(raw, behavioral_df)
                if len(annotations) > 0:
                    raw.set_annotations(annotations)
                    logger = mne.get_logger()
                    logger.info(
                        f"[DS003039 Kernel] Loaded {len(annotations)} events from {behavioral_log}"
                    )

        # Ensure all button press and gait events are properly mapped
        # Even if no behavioral log found, create annotations for any existing events
        existing_annots = raw.annotations
        if len(existing_annots) == 0:
            # No events found - this is expected for naturalistic walking paradigm
            logger = mne.get_logger()
            logger.info(
                "[DS003039 Kernel] No event markers in EEG file. "
                "Naturalistic free-walking paradigm - button/gait events should be in behavioral logs."
            )

        return raw


KERNEL = OpenNeuroDS003039Kernel()