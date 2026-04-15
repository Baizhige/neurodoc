"""OpenNeuro ds004660 (TNO Military Cognitive Workload) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds004660
DOI: https://doi.org/10.18112/openneuro.ds004660.v1.0.2

A military-relevant cognitive workload study conducted at TNO research institute,
involving hierarchically encoded task conditions with 5-digit numeric trigger codes.

Paradigm structure:
- Primary task (14xxx): Target detection / oddball-like condition
- Secondary task (21xxx): Supporting task condition
- Codes: first 2 digits = task type, middle digit = difficulty, last 2 digits = variant

Tasks supported:
- P300/Oddball Target Detection: tmin=-0.2s, tmax=0.8s, baseline=(-0.2,0.0)s
- Multiclass Hierarchical Condition Classification: tmin=-0.2s, tmax=1.0s

Source: TNO research institute, Netherlands
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Channel rename map
# Based on: OpenNeuro ds004660 channel naming convention (EEG-01..EEG-38)
# Standard 1020 positions. Annotated by LLM, 2026-04-08
# LLM 推断，需人类复核
# ---------------------------------------------------------------------------
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-01": "Fp1",
    "EEG-02": "Fp2",
    "EEG-03": "F7",
    "EEG-04": "F3",
    "EEG-05": "Fz",
    "EEG-06": "F4",
    "EEG-07": "F8",
    "EEG-08": "T7",
    "EEG-09": "C3",
    "EEG-10": "Cz",
    "EEG-11": "C4",
    "EEG-12": "T8",
    "EEG-13": "P7",
    "EEG-14": "P3",
    "EEG-15": "Pz",
    "EEG-16": "P4",
    "EEG-17": "P8",
    "EEG-18": "O1",
    "EEG-19": "Oz",
    "EEG-20": "O2",
    "EEG-21": "Fpz",
    "EEG-22": "AF3",
    "EEG-23": "AF4",
    "EEG-24": "FC5",
    "EEG-25": "FC1",
    "EEG-26": "FC2",
    "EEG-27": "FC6",
    "EEG-28": "CP5",
    "EEG-29": "CP1",
    "EEG-30": "CP2",
    "EEG-31": "CP6",
    "EEG-32": "PO3",
    "EEG-33": "PO4",
    "EEG-34": "F1",
    "EEG-35": "F2",
    "EEG-36": "C1",
    "EEG-37": "C2",
    "EEG-38": "P1",
}

# EOG channels (if present)
_EOG_RENAME_MAP: Dict[str, str] = {
    "EOG-left": "EOG-left",
    "EOG-right": "EOG-right",
    "EOG-up": "EOG-up",
    "EOG-down": "EOG-down",
}

# System/trigger channel to preserve (if present)
_MISC_CHANNEL_NAMES = {"stim", "trigger", "marker", "status"}


# ---------------------------------------------------------------------------
# Event code mapping tables
# Source: analysis.md + TNO paradigm structure inference
# LLM 推断，需人类复核
# ---------------------------------------------------------------------------

# P300/Oddball Target Detection mapping
# High-frequency non-target codes: 14211, 14212, 13001, 13002 (y=1)
# Target candidate codes: 21111, 14111, 14112, 21201 (y=0)
_P300_EVENT_MAP: Dict[int, str] = {
    14211: "frequent_non_target_A",
    14212: "frequent_non_target_B",
    13001: "frequent_non_target_C",
    13002: "frequent_non_target_D",
    21111: "target_secondary_task",
    14111: "target_primary_task_A",
    14112: "target_primary_task_B",
    21201: "target_secondary_variant",
}

# Multiclass Hierarchical Condition Classification mapping
_MULTICLASS_EVENT_MAP: Dict[int, str] = {
    11001: "system_marker_A",
    11002: "system_marker_B",
    12101: "task_phase_1_A",
    12102: "task_phase_1_B",
    12201: "task_phase_2_A",
    12202: "task_phase_2_B",
    13001: "primary_condition_A",
    13002: "primary_condition_B",
    14111: "primary_condition_C",
    14112: "primary_condition_D",
    14121: "primary_condition_E",
    14122: "primary_condition_F",
    14211: "primary_task_core_A",
    14212: "primary_task_core_B",
    14231: "primary_task_extended_A",
    14232: "primary_task_extended_B",
    15111: "secondary_task_1A",
    15121: "secondary_task_1B",
    15211: "secondary_task_2A",
    15221: "secondary_task_2B",
    15311: "secondary_task_3A",
    15321: "secondary_task_3B",
    15411: "secondary_task_4A",
    15421: "secondary_task_4B",
    15511: "secondary_task_5A",
    15521: "secondary_task_5B",
    15611: "secondary_task_6A",
    15621: "secondary_task_6B",
}

# All known event codes for validation
_ALL_EVENT_CODES: set = set(_P300_EVENT_MAP.keys()) | set(_MULTICLASS_EVENT_MAP.keys())


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map compatible with actual channel names in raw."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Standard EEG channels
    for source_name, target_name in _CHANNEL_RENAME_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name

    # EOG channels
    for source_name, target_name in _EOG_RENAME_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name

    return rename_map


def _detect_trigger_channel(raw: mne.io.BaseRaw) -> Optional[str]:
    """Detect the trigger/stimulus channel name."""
    for ch_name in raw.ch_names:
        ch_lower = ch_name.lower()
        if ch_lower in _MISC_CHANNEL_NAMES:
            return ch_name
        if "stim" in ch_lower or "trigger" in ch_lower:
            return ch_name
    return None


def _extract_events_from_stim_channel(
    raw: mne.io.BaseRaw, stim_channel: str
) -> Tuple[np.ndarray, np.ndarray]:
    """Extract events from stimulus/stim channel as annotations."""
    stim_data, times = raw[stim_channel]
    stim_data = stim_data.flatten()

    # Find transitions (rising edges) - event onsets
    diff_data = np.diff(stim_data.astype(np.int32))
    transition_indices = np.where(diff_data != 0)[0]

    if len(transition_indices) == 0:
        return np.empty((0, 3), dtype=np.int32), np.array([], dtype=np.int32)

    onsets = times[transition_indices]
    event_ids = stim_data[transition_indices + 1].astype(np.int32)

    # Filter for known event codes only
    valid_mask = np.isin(event_ids, list(_ALL_EVENT_CODES))
    onsets = onsets[valid_mask]
    event_ids = event_ids[valid_mask]

    # Convert to MNE events format: [sample, prev_id, event_id]
    sample_indices = (onsets * raw.info["sfreq"]).astype(np.int32)
    events = np.column_stack([sample_indices, np.zeros(len(sample_indices), dtype=np.int32), event_ids])

    return events, event_ids


def _create_annotations(
    raw: mne.io.BaseRaw, events: np.ndarray, event_id_map: Dict[int, str]
) -> mne.Annotations:
    """Create MNE annotations from events array."""
    if len(events) == 0:
        return mne.Annotations(onset=[], duration=[], description=[], sfreq=raw.info["sfreq"])

    onsets = events[:, 0] / raw.info["sfreq"]
    durations = np.zeros(len(onsets))
    descriptions = [event_id_map.get(eid, f"unknown_{eid}") for eid in events[:, 2]]

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions, sfreq=raw.info["sfreq"])


def _load_subject_info(dataset_root: str) -> Dict[str, Dict[str, Any]]:
    """Load subject information from BIDS participants.tsv if available."""
    participants_file = os.path.join(dataset_root, "participants.tsv")
    subject_info: Dict[str, Dict[str, Any]] = {}

    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).strip()
                if not subj_id:
                    continue
                # Extract subject number from format like "sub-001" -> "001"
                subj_num = re.sub(r"[^0-9]", "", subj_id)
                subject_info[subj_num] = {
                    "age": str(row.get("age", "unknown")),
                    "sex": str(row.get("sex", row.get("gender", "unknown"))).lower(),
                    "handedness": str(row.get("handedness", "unknown")),
                }
        except Exception:
            pass

    return subject_info


def _build_eegunity_description(
    raw: mne.io.BaseRaw,
    subject_info: Dict[str, Dict[str, Any]],
    row: Any,
) -> Dict[str, Any]:
    """Build the eegunity_description dictionary."""
    original_desc = raw.info.get("description", "")

    # Try to extract subject ID from row
    subject_id = "unknown"
    if hasattr(row, "get") and "File Path" in row:
        file_path = row["File Path"]
        # Extract subject number from filename pattern: sub-001_ses-XX_...
        match = re.search(r"sub-(\d+)", str(file_path))
        if match:
            subject_id = match.group(1)
    elif hasattr(row, "Subject"):
        subject_id = str(row["Subject"])

    # Get subject-specific info if available
    subj_data = subject_info.get(subject_id, {})

    # Infer amplifier info from dataset characteristics
    # Source: TNO research institute standard equipment inference
    # LLM 推断，需人类复核
    amplifier = "unknown"
    if raw.info["sfreq"] == 512:
        amplifier = "unknown"  # Common EEG amplifiers support 512 Hz

    return {
        "original_description": original_desc,
        "eegunity_description": {
            "age": subj_data.get("age", "unknown"),
            "sex": subj_data.get("sex", "unknown"),
            "amplifier": amplifier,
            "cap": "unknown",  # LLM 推断，需人类复核
            "handedness": subj_data.get("handedness", "unknown"),
        },
    }


class TNOmilitaryKernel:
    """Stage1 kernel for OpenNeuro ds004660 (TNO Military Cognitive Workload)."""

    KERNEL_ID: str = "openneuro-ds004660-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with channel names, montage, annotations,
            and description metadata.
        """
        # Get dataset root path from udataset or row
        dataset_root = ""
        if hasattr(udataset, "dataset_root"):
            dataset_root = udataset.dataset_root
        elif hasattr(row, "get") and "Dataset" in row:
            dataset_root = row.get("Dataset", "")

        # -------------------------------------------------------------------------
        # Step 1: Load subject information from BIDS
        # -------------------------------------------------------------------------
        subject_info = _load_subject_info(dataset_root)

        # -------------------------------------------------------------------------
        # Step 2: Rename channels to standard names
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Use explicit renaming to avoid conflicts
            for old_name, new_name in rename_map.items():
                if old_name != new_name and old_name in raw.ch_names:
                    try:
                        raw.rename_channels({old_name: new_name})
                    except Exception:
                        pass

        # -------------------------------------------------------------------------
        # Step 3: Set standard 1020 montage
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setup optional, continue if fails

        # -------------------------------------------------------------------------
        # Step 4: Detect trigger channel and extract events
        # -------------------------------------------------------------------------
        stim_channel = _detect_trigger_channel(raw)
        if stim_channel:
            events, event_ids = _extract_events_from_stim_channel(raw, stim_channel)

            if len(events) > 0:
                # Combine P300 and Multiclass event maps for annotation
                combined_event_map = {**_P300_EVENT_MAP, **_MULTICLASS_EVENT_MAP}
                annotations = _create_annotations(raw, events, combined_event_map)
                raw.set_annotations(annotations)
        else:
            # Fallback: try to use existing annotations or events
            if raw.annotations is not None and len(raw.annotations) > 0:
                # Annotations already exist, pass through
                pass
            else:
                # Try standard MNE event detection
                try:
                    events, event_id = mne.events_from_annotations(raw)
                    # Map numeric annotations to human-readable labels
                    combined_event_map = {**_P300_EVENT_MAP, **_MULTICLASS_EVENT_MAP}
                    # Keep only events we recognize
                    valid_events = []
                    for ev in events:
                        eid = ev[2]
                        if eid in combined_event_map:
                            valid_events.append(ev)
                    if valid_events:
                        valid_events = np.array(valid_events)
                        annotations = _create_annotations(raw, valid_events, combined_event_map)
                        raw.set_annotations(annotations)
                except Exception:
                    pass

        # -------------------------------------------------------------------------
        # Step 5: Set description metadata
        # -------------------------------------------------------------------------
        eegunity_desc = _build_eegunity_description(raw, subject_info, row)
        raw.info["description"] = json.dumps(eegunity_desc)

        return raw


KERNEL = TNOmilitaryKernel()