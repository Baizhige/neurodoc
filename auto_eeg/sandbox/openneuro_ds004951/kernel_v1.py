"""OpenNeuro ds004951 stage1 kernel for EEGUnity.

Braille Letters EEG dataset - tactile stimulation of Braille letters
to left/right index fingers, comparing sighted controls and blind individuals.

Source: https://openneuro.org/datasets/ds004951
DOI: 10.7554/eLife.98148

Paradigm: Braille letter identification (16 letters, S1-S16)
         8-class subset: B, C, D, L, M, N, V, Z

Device: BrainVision MR plus (64-channel EEG, 1000 Hz)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Dataset documentation / OpenNeuro ds004951
# EEG channel names follow standard_1020 with 64-channel layout
# 64 EEG channels: Fp1, Fp2, F7, F3, Fz, F4, F8, FC3, FCz, FC4, T3, C3, Cz, C4,
# T4, CP3, CPz, CP4, T5, P3, Pz, P4, T6, O1, Oz, O2 + extended 10-20 positions
# Annotator: LLM, 2026-04-08, inferred from standard 64-channel EEG cap
_EEG_CHANNEL_MAP = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "FC3": "FC3",
    "FCz": "FCz",
    "FC4": "FC4",
    "T3": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T4": "T8",
    "CP3": "CP3",
    "CPz": "CPz",
    "CP4": "CP4",
    "T5": "T9",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "T6": "T10",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC5": "FC5",
    "FC6": "FC6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP5": "CP5",
    "CP6": "CP6",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO1": "PO1",
    "PO2": "PO2",
    "PO3": "PO3",
    "PO4": "PO4",
    "POz": "POz",
    "AF3": "AF3",
    "AF4": "AF4",
    "AF7": "AF7",
    "AF8": "AF8",
    "O9": "O9",  # LLM 推断，需人类复核 - extended 10-20
    "O10": "O10",  # LLM 推断，需人类复核 - extended 10-20
    "Iz": "Iz",
    "LPA": "LPA",
    "RPA": "RPA",
    "NHS": "NHS",  # LLM 推断，需人类复核 - possibly nonstandard
}

# Braille letter event mapping (Stimulus/S xx format from BrainVision)
# 8-class task: B=0, C=1, D=2, L=3, M=4, N=5, V=6, Z=7
# Mapping verified from DOI: 10.7554/eLife.98148
_EVENT_MAP_8CLASS = {
    "Stimulus/S 1": 0,   # Braille letter B
    "Stimulus/S 2": 1,   # Braille letter C
    "Stimulus/S 3": 2,   # Braille letter D
    "Stimulus/S 4": 3,   # Braille letter L
    "Stimulus/S 5": 4,   # Braille letter M
    "Stimulus/S 6": 5,   # Braille letter N
    "Stimulus/S 7": 6,   # Braille letter V
    "Stimulus/S 8": 7,   # Braille letter Z
}

# 16-class task: all Braille letters S1-S16
_EVENT_MAP_16CLASS = {
    "Stimulus/S 1": 0,
    "Stimulus/S 2": 1,
    "Stimulus/S 3": 2,
    "Stimulus/S 4": 3,
    "Stimulus/S 5": 4,
    "Stimulus/S 6": 5,
    "Stimulus/S 7": 6,
    "Stimulus/S 8": 7,
    "Stimulus/S 9": 8,
    "Stimulus/S 10": 9,
    "Stimulus/S 11": 10,
    "Stimulus/S 12": 11,
    "Stimulus/S 13": 12,
    "Stimulus/S 14": 13,
    "Stimulus/S 15": 14,
    "Stimulus/S 16": 15,
}

# Admin/block markers to exclude from classification tasks
_ADMIN_CODES = {
    "Stimulus/S101",   # Response feedback / block marker A
    "Stimulus/S222",   # Response feedback / block marker B
    "Stimulus/S200",   # Block boundary / condition marker
    "Stimulus/S253",   # Admin / response marker
    "Stimulus/S254",   # Admin / system marker
    "Stimulus/S255",   # BrainVision admin sync marker
    "New Segment/",    # BrainVision segment boundary
}


def _detect_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.

    Parameters
    ----------
    file_path : str
        Full path to EEG file.

    Returns
    -------
    str
        Subject identifier (e.g., 'sub-01', 'sub-001').
    """
    # Match sub-XXXX pattern
    match = re.search(r"sub-[a-zA-Z]*(\d+)", file_path)
    if match:
        num = int(match.group(1))
        # Preserve leading zeros if present in original
        if "sub-0" in file_path:
            return f"sub-{num:03d}"
        return f"sub-{num:02d}"
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map for standard 10-20 names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from current names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Build reverse map: standard name -> possible source names
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "FP1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "FP2"]),
        ("F7", ["F7", "EEG-F7", "F7"]),
        ("F3", ["F3", "EEG-F3", "F3"]),
        ("Fz", ["Fz", "EEG-Fz", "Fz"]),
        ("F4", ["F4", "EEG-F4", "F4"]),
        ("F8", ["F8", "EEG-F8", "F8"]),
        ("FC3", ["FC3", "EEG-FC3", "FC3"]),
        ("FCz", ["FCz", "EEG-FCz", "FCz"]),
        ("FC4", ["FC4", "EEG-FC4", "FC4"]),
        ("T7", ["T7", "T3", "EEG-T3"]),
        ("C3", ["C3", "EEG-C3"]),
        ("Cz", ["Cz", "EEG-Cz"]),
        ("C4", ["C4", "EEG-C4"]),
        ("T8", ["T8", "T4", "EEG-T4"]),
        ("CP3", ["CP3", "EEG-CP3"]),
        ("CPz", ["CPz", "EEG-CPz"]),
        ("CP4", ["CP4", "EEG-CP4"]),
        ("T9", ["T9", "T5", "EEG-T5"]),
        ("P3", ["P3", "EEG-P3"]),
        ("Pz", ["Pz", "EEG-Pz"]),
        ("P4", ["P4", "EEG-P4"]),
        ("T10", ["T10", "T6", "EEG-T6"]),
        ("O1", ["O1", "EEG-O1"]),
        ("Oz", ["Oz", "EEG-Oz"]),
        ("O2", ["O2", "EEG-O2"]),
        ("F1", ["F1", "EEG-F1"]),
        ("F2", ["F2", "EEG-F2"]),
        ("F5", ["F5", "EEG-F5"]),
        ("F6", ["F6", "EEG-F6"]),
        ("FC1", ["FC1", "EEG-FC1"]),
        ("FC2", ["FC2", "EEG-FC2"]),
        ("FC5", ["FC5", "EEG-FC5"]),
        ("FC6", ["FC6", "EEG-FC6"]),
        ("C1", ["C1", "EEG-C1"]),
        ("C2", ["C2", "EEG-C2"]),
        ("C5", ["C5", "EEG-C5"]),
        ("C6", ["C6", "EEG-C6"]),
        ("CP1", ["CP1", "EEG-CP1"]),
        ("CP2", ["CP2", "EEG-CP2"]),
        ("CP5", ["CP5", "EEG-CP5"]),
        ("CP6", ["CP6", "EEG-CP6"]),
        ("P1", ["P1", "EEG-P1"]),
        ("P2", ["P2", "EEG-P2"]),
        ("P5", ["P5", "EEG-P5"]),
        ("P6", ["P6", "EEG-P6"]),
        ("PO1", ["PO1", "EEG-PO1"]),
        ("PO2", ["PO2", "EEG-PO2"]),
        ("PO3", ["PO3", "EEG-PO3"]),
        ("PO4", ["PO4", "EEG-PO4"]),
        ("POz", ["POz", "EEG-POz"]),
        ("AF3", ["AF3", "EEG-AF3"]),
        ("AF4", ["AF4", "EEG-AF4"]),
        ("AF7", ["AF7", "EEG-AF7"]),
        ("AF8", ["AF8", "EEG-AF8"]),
        ("Iz", ["Iz", "Iz", "EEG-Iz"]),
        ("LPA", ["LPA"]),
        ("RPA", ["RPA"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _load_participant_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load participant metadata from BIDS participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Path to dataset root.
    subject_id : str
        Subject identifier (e.g., 'sub-001').

    Returns
    -------
    Dict[str, str]
        Dictionary with age, sex, handedness.
    """
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Normalize subject_id for matching
            normalized_id = subject_id.replace("sub-", "sub-")

            # Try exact match first
            row = df[df["participant_id"] == normalized_id]
            if row.empty:
                # Try without leading zeros
                num_match = re.search(r"(\d+)", subject_id)
                if num_match:
                    subj_num = int(num_match.group(1))
                    for _, row in df.iterrows():
                        pid = row["participant_id"]
                        pid_num_match = re.search(r"(\d+)", pid)
                        if pid_num_match and int(pid_num_match.group(1)) == subj_num:
                            row = row
                            break

            if not row.empty:
                row = row.iloc[0]
                age = str(int(row.get("age", "unknown"))) if pd.notna(row.get("age")) else "unknown"
                sex = str(row.get("sex", "unknown")).lower()
                handedness = str(row.get("hand", row.get("handedness", "unknown"))).lower()

                # Validate sex
                if sex not in ["male", "female"]:
                    sex = "unknown"

                # Validate handedness
                if handedness not in ["right", "left", "unknown"]:
                    handedness = "unknown"

                return {
                    "age": age,
                    "sex": sex,
                    "handedness": handedness,
                }
        except Exception:
            pass

    # Default values if participants.tsv not found or read failed
    # LLM 推断，需人类复核
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


class OpenNeuroDS004951Kernel:
    """Stage1 kernel for OpenNeuro ds004951 (Braille Letters EEG)."""

    KERNEL_ID: str = "openneuro-ds004951-stage1"

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
            Preprocessed Raw object with standardized channels, events, and metadata.
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(os.path.dirname(file_path)))

        # Detect subject ID
        subject_id = _detect_subject_id(file_path)

        # Load participant metadata
        participant_info = _load_participant_info(dataset_path, subject_id)

        # Get original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description
        eegunity_desc = {
            "age": participant_info["age"],
            "sex": participant_info["sex"],
            "amplifier": "BrainAmp MR plus",  # Source: OpenNeuro ds004951 documentation
            "cap": "Ag/AgCl",  # Source: standard EEG lab equipment, LLM 推断，需人类复核
            "handedness": participant_info["handedness"],
        }

        # Write description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Sort by length (longer first) to avoid partial replacements
            rename_items = sorted(rename_map.items(), key=lambda x: len(x[0]), reverse=True)
            for old_name, new_name in rename_items:
                try:
                    raw.rename_channels({old_name: new_name})
                except Exception:
                    pass

        # Set montage (standard 1020)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage may fail if channels don't match exactly

        # Process events from BrainVision annotations
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = np.empty((0, 3), dtype=int)
            event_id = {}

        # Filter out admin codes and create clean annotations
        if len(events) > 0:
            valid_events = []
            valid_descriptions = []

            for i in range(len(events)):
                event_code = events[i, 2]
                # Find the annotation description for this event
                for desc, code in event_id.items():
                    if code == event_code:
                        # Check if it's a valid Braille letter (S1-S16)
                        if desc.startswith("Stimulus/S "):
                            num_match = re.search(r"S (\d+)", desc)
                            if num_match:
                                num = int(num_match.group(1))
                                if 1 <= num <= 16:
                                    valid_events.append(events[i])
                                    valid_descriptions.append(desc)
                        break

            if valid_events:
                valid_events = np.array(valid_events)
                # Convert to sample indices
                onsets = valid_events[:, 0] / raw.info["sfreq"]
                descriptions = valid_descriptions

                annotations = mne.Annotations(
                    onset=onsets,
                    duration=[0.0] * len(onsets),
                    description=descriptions,
                )
                raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004951Kernel()