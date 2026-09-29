"""OpenNeuro DS003670 stage1 kernel for EEGUnity.

Dataset: Concurrent EEG, ECG, and Behavior with Multiple Doses of Transcranial
Electrical Stimulation during Continuous Tracking Task.

Source: https://openneuro.org/datasets/ds003670 (DOI: 10.1038/s41597-021-01046-y)
        https://doi.org/10.1016/j.brs.2024.05.009

35 channels, 2000 Hz sampling rate.
Events: Stimulation Start, Stimulation Stop, Block Start, STATUS
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Source: paper_10.1038_s41597-021-01046-y.pdf - 30-channel EEG with 2 EKG leads
# + 3 auxiliary channels for stimulation markers
# Annotator: LLM, 2026-01-15
_STANDARD_35_CHANNEL_MAP = {
    "EEG-Fz": "Fz",
    "EEG-F1": "F1",
    "EEG-F3": "F3",
    "EEG-F5": "F5",
    "EEG-F7": "F7",
    "EEG-F2": "F2",
    "EEG-F4": "F4",
    "EEG-F6": "F6",
    "EEG-F8": "F8",
    "EEG-Cz": "Cz",
    "EEG-C1": "C1",
    "EEG-C3": "C3",
    "EEG-C5": "C5",
    "EEG-C7": "C7",
    "EEG-C2": "C2",
    "EEG-C4": "C4",
    "EEG-C6": "C6",
    "EEG-C8": "C8",
    "EEG-Pz": "Pz",
    "EEG-P1": "P1",
    "EEG-P3": "P3",
    "EEG-P5": "P5",
    "EEG-P7": "P7",
    "EEG-P2": "P2",
    "EEG-P4": "P4",
    "EEG-P6": "P6",
    "EEG-P8": "P8",
    "EEG-Oz": "Oz",
    "EEG-O1": "O1",
    "EEG-O2": "O2",
    "EKG": "ECG",  # ECG/EKG channel
    "stim1": "STI 101",  # Stimulus channel 1
    "stim2": "STI 102",  # Stimulus channel 2
    "stim3": "STI 103",  # Stimulus channel 3
}


# Default device info from dataset documentation
# Source: openneuro dataset description
# Annotator: LLM, 2026-01-15
_DEFAULT_AMPLIFIER = "BrainAmp DC"  # inferred by LLM, needs human review
_DEFAULT_CAP = "Ag/AgCl"  # inferred by LLM, needs human review


def _detect_stimulation_dose(events_df: pd.DataFrame) -> Dict[str, Any]:
    """Detect stimulation dose condition from events.

    Dose codes: F0/F5/F30 (Frontal), M0/M5/M30 (Motor), S0/S5 (Sham)
    """
    if "trial_type" not in events_df.columns and "stim_type" not in events_df.columns:
        return {"dose": "unknown", "site": "unknown"}

    col = "trial_type" if "trial_type" in events_df.columns else "stim_type"
    unique_values = events_df[col].dropna().unique()

    dose = "unknown"
    site = "unknown"

    for val in unique_values:
        if isinstance(val, str):
            if "F30" in val:
                dose = "F30"
                site = "frontal"
                break
            elif "M30" in val:
                dose = "M30"
                site = "motor"
                break
            elif "F5" in val:
                dose = "F5"
                site = "frontal"
            elif "M5" in val:
                dose = "M5"
                site = "motor"
            elif "S5" in val or "sham" in val.lower():
                dose = "sham"
                site = "sham"

    return {"dose": dose, "site": site}


def _build_subject_info(
    dataset_root: str, subject_id: str
) -> Dict[str, str]:
    """Load subject metadata from participants.tsv.

    Returns dict with age, sex, handedness keys.
    """
    participants_tsv = os.path.join(dataset_root, "participants.tsv")

    age = "unknown"
    sex = "unknown"
    handedness = "unknown"

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            row = df[df["participant_id"] == subject_id]
            if len(row) > 0:
                if "age" in row.columns and pd.notna(row["age"].iloc[0]):
                    age = str(row["age"].iloc[0])
                if "sex" in row.columns and pd.notna(row["sex"].iloc[0]):
                    sex_val = str(row["sex"].iloc[0]).lower()
                    if sex_val in ["m", "male"]:
                        sex = "male"
                    elif sex_val in ["f", "female"]:
                        sex = "female"
                    else:
                        sex = "unknown"
                if "handedness" in row.columns and pd.notna(row["handedness"].iloc[0]):
                    hand_val = str(row["handedness"].iloc[0]).lower()
                    if "right" in hand_val:
                        handedness = "right"
                    elif "left" in hand_val:
                        handedness = "left"
        except Exception:
            pass

    # inferred by LLM, needs human review
    if age == "unknown":
        age = "unknown"  # inferred by LLM, needs human review

    return {"age": age, "sex": sex, "handedness": handedness}


def _load_events_tsv(eeg_file_path: str) -> pd.DataFrame:
    """Load corresponding events.tsv file for an EEG file."""
    base_dir = os.path.dirname(eeg_file_path)
    eeg_dir = os.path.dirname(base_dir)

    # Look for events.tsv in same directory or parent
    events_paths = [
        os.path.join(eeg_dir, "events.tsv"),
        os.path.join(base_dir, "events.tsv"),
    ]

    for events_path in events_paths:
        if os.path.exists(events_path):
            try:
                return pd.read_csv(events_path, sep="\t")
            except Exception:
                pass

    return pd.DataFrame()


@dataclass
class OpenNeuroDS003670Kernel:
    """Stage1 kernel for OpenNeuro DS003670 dataset.

    Handles BIDS-format EEG data with transcranial electrical stimulation events.
    """

    KERNEL_ID: str = "openneuro-ds003670-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw object
        row : pandas Series with File Path and other metadata

        Returns
        -------
        mne.io.BaseRaw
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))

        # Determine dataset root from file path
        dataset_root = self._find_dataset_root(file_path)

        # Load subject info
        subject_info = _build_subject_info(dataset_root, subject_id)

        # Update description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEFAULT_AMPLIFIER,
                "cap": _DEFAULT_CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels before setting montage
        self._rename_channels(raw)

        # Set montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        # Process events
        self._process_events(raw, file_path, dataset_root)

        return raw

    def _find_dataset_root(self, file_path: str) -> str:
        """Find dataset root directory from file path."""
        if not file_path:
            return ""

        # Navigate up to find dataset root (contains participants.tsv)
        current = os.path.dirname(file_path)
        while current and current != os.path.dirname(current):
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)

        # Fallback: go up 3 levels from sub-XX/eeg/ structure
        parts = file_path.split(os.sep)
        if "sub-" in file_path:
            for i, part in enumerate(parts):
                if part.startswith("sub-"):
                    return os.sep.join(parts[:i])
        return os.path.dirname(file_path)

    def _rename_channels(self, raw: mne.io.BaseRaw) -> None:
        """Rename channels to standard 10-20 nomenclature."""
        ch_names = raw.ch_names

        # Build rename map for existing channels
        rename_map = {}
        for old_name, new_name in _STANDARD_35_CHANNEL_MAP.items():
            if old_name in ch_names:
                rename_map[old_name] = new_name

        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for non-EEG channels
        ecg_chs = [ch for ch in raw.ch_names if ch.upper() in ["ECG", "EKG"]]
        for ch in ecg_chs:
            try:
                raw.set_channel_types({ch: "ecg"})
            except Exception:
                pass

        stim_chs = [ch for ch in raw.ch_names if "STI" in ch.upper()]
        for ch in stim_chs:
            try:
                raw.set_channel_types({ch: "stim"})
            except Exception:
                pass

    def _process_events(
        self, raw: mne.io.BaseRaw, file_path: str, dataset_root: str
    ) -> None:
        """Process events from annotations and events.tsv."""
        # Load events.tsv if available
        events_df = _load_events_tsv(file_path)

        if not events_df.empty and "onset" in events_df.columns:
            self._apply_events_from_tsv(raw, events_df)
        else:
            # Fallback: use existing annotations or extract from stim channels
            self._extract_from_stim_channels(raw)

    def _apply_events_from_tsv(
        self, raw: mne.io.BaseRaw, events_df: pd.DataFrame
    ) -> None:
        """Apply events from BIDS events.tsv file."""
        # Standard BIDS columns: onset, duration, trial_type
        if "trial_type" in events_df.columns:
            event_col = "trial_type"
        elif "value" in events_df.columns:
            event_col = "value"
        else:
            event_col = None

        if event_col is None:
            return

        # Filter valid rows
        valid_mask = events_df[event_col].notna()
        valid_events = events_df[valid_mask].copy()

        if len(valid_events) == 0:
            return

        # Map event descriptions to canonical names
        onset_times = valid_events["onset"].values
        descriptions = valid_events[event_col].values
        durations = (
            valid_events["duration"].values
            if "duration" in valid_events.columns
            else [0.0] * len(valid_events)
        )

        # Convert to canonical event names
        canonical_descs = []
        for desc in descriptions:
            desc_str = str(desc).strip()
            # Map common variations
            if "start" in desc_str.lower() or "stim on" in desc_str.lower():
                canonical_descs.append("Stimulation Start")
            elif "stop" in desc_str.lower() or "stim off" in desc_str.lower():
                canonical_descs.append("Stimulation Stop")
            elif "block" in desc_str.lower() or "task" in desc_str.lower():
                canonical_descs.append("Block Start")
            elif "status" in desc_str.lower() or "code" in desc_str.lower():
                canonical_descs.append("STATUS")
            else:
                canonical_descs.append(desc_str)

        # Create MNE annotations
        annotations = mne.Annotations(
            onset=onset_times,
            duration=durations.tolist() if hasattr(durations, "tolist") else list(durations),
            description=canonical_descs,
        )

        raw.set_annotations(annotations)

    def _extract_from_stim_channels(self, raw: mne.io.BaseRaw) -> None:
        """Extract events from stimulation trigger channels."""
        stim_channels = [ch for ch in raw.ch_names if "STI" in ch.upper()]

        if not stim_channels:
            return

        # Find events from stim channel
        stim_data, stim_times = raw[stim_channels[0], :]

        # Detect threshold crossings (stimulation markers typically have
        # distinct amplitude values)
        threshold = stim_data.max() * 0.5
        crossings = []
        current_val = 0

        for i in range(len(stim_data[0])):
            val = stim_data[0, i]
            if val != current_val and val > threshold:
                crossings.append(i)
                current_val = val

        if crossings:
            onset_times = [stim_times[c] for c in crossings]
            descriptions = ["STATUS"] * len(crossings)

            annotations = mne.Annotations(
                onset=onset_times,
                duration=[0.0] * len(onset_times),
                description=descriptions,
            )

            raw.set_annotations(annotations)


KERNEL = OpenNeuroDS003670Kernel()