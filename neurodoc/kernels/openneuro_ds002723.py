"""OpenNeuro ds002723 stage1 kernel for EEGUnity.

Brain-Computer Music Interface (BCMI) testing session dataset.
8 subjects, 44 files, 37 channels, 1000 Hz.
Affective music conditions 1-9 (condition 8 excluded).

Source: https://openneuro.org/datasets/ds002723
DOI: 10.1038/s41597-020-0507-6
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Daly et al. 2018 (Scientific Data) - 10.1038/s41597-020-0507-6
# BCMI system electrode placement follows standard 10-20 system
# 37-channel array: 32 EEG + EOG + ECG + GSR channels
# Annotator: LLM, 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "AF3": "AF3",
    "AF4": "AF4",
    "F1": "F1",
    "F2": "F2",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC5": "FC5",
    "FC6": "FC6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP5": "CP5",
    "CP6": "CP6",
    "PO3": "PO3",
    "PO4": "PO4",
    "EOG": "EOG",
    "ECG": "ECG",
    "GSR": "GSR",
}


# Event mapping for affective music conditions
# Source: Paper 10.1038/s41597-020-0507-6 Table 1
_EVENT_MAP: Dict[int, str] = {
    1: "music_condition_1",
    2: "music_condition_2",
    3: "music_condition_3",
    4: "music_condition_4",
    5: "music_condition_5",
    6: "music_condition_6",
    7: "music_condition_7",
    9: "music_condition_9",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path."""
    basename = os.path.basename(file_path).lower()
    if "test" in basename:
        return "testing"
    elif "calibration" in basename:
        return "calibration"
    elif "training" in basename:
        return "training"
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common alternative naming patterns in EEG data
    alias_patterns = {
        "Fp1": ["EEG-Fp1", "Fp1", "fp1", "FP1"],
        "Fp2": ["EEG-Fp2", "Fp2", "fp2", "FP2"],
        "F7": ["EEG-F7", "F7", "f7", "F7"],
        "F3": ["EEG-F3", "F3", "f3", "F3"],
        "Fz": ["EEG-Fz", "Fz", "fz", "FZ"],
        "F4": ["EEG-F4", "F4", "f4", "F4"],
        "F8": ["EEG-F8", "F8", "f8", "F8"],
        "T7": ["EEG-T7", "T7", "t7", "T7", "T3"],
        "C3": ["EEG-C3", "C3", "c3", "C3"],
        "Cz": ["EEG-Cz", "Cz", "cz", "CZ"],
        "C4": ["EEG-C4", "C4", "c4", "C4"],
        "T8": ["EEG-T8", "T8", "t8", "T8", "T4"],
        "P7": ["EEG-P7", "P7", "p7", "P7", "T5"],
        "P3": ["EEG-P3", "P3", "p3", "P3"],
        "Pz": ["EEG-Pz", "Pz", "pz", "PZ"],
        "P4": ["EEG-P4", "P4", "p4", "P4"],
        "P8": ["EEG-P8", "P8", "p8", "P8", "T6"],
        "O1": ["EEG-O1", "O1", "o1", "O1"],
        "Oz": ["EEG-Oz", "Oz", "oz", "OZ"],
        "O2": ["EEG-O2", "O2", "o2", "O2"],
        "AF3": ["EEG-AF3", "AF3", "af3"],
        "AF4": ["EEG-AF4", "AF4", "af4"],
        "F1": ["EEG-F1", "F1", "f1"],
        "F2": ["EEG-F2", "F2", "f2"],
        "FC1": ["EEG-FC1", "FC1", "fc1"],
        "FC2": ["EEG-FC2", "FC2", "fc2"],
        "FC5": ["EEG-FC5", "FC5", "fc5"],
        "FC6": ["EEG-FC6", "FC6", "fc6"],
        "CP1": ["EEG-CP1", "CP1", "cp1"],
        "CP2": ["EEG-CP2", "CP2", "cp2"],
        "CP5": ["EEG-CP5", "CP5", "cp5"],
        "CP6": ["EEG-CP6", "CP6", "cp6"],
        "PO3": ["EEG-PO3", "PO3", "po3"],
        "PO4": ["EEG-PO4", "PO4", "po4"],
        "EOG": ["EOG", "eog", "EOG-left", "EOG-right"],
        "ECG": ["ECG", "ecg"],
        "GSR": ["GSR", "gsr", "EDA", "eda"],
    }

    for target_name, aliases in alias_patterns.items():
        if target_name in existing_names:
            continue
        for alias in aliases:
            if alias in existing_names and alias != target_name:
                rename_map[alias] = target_name
                break

    return rename_map


def _extract_subject_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv."""
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Find row matching subject_id
            subject_col = "participant_id" if "participant_id" in df.columns else df.columns[0]
            subject_row = df[df[subject_col].str.contains(subject_id, case=False, na=False)]

            if not subject_row.empty:
                info = {}
                # Extract age
                if "age" in df.columns:
                    age_val = subject_row["age"].values[0]
                    info["age"] = str(int(age_val)) if pd.notna(age_val) else "unknown"
                else:
                    info["age"] = "unknown"

                # Extract sex
                if "sex" in df.columns:
                    sex_val = str(subject_row["sex"].values[0]).lower()
                    if sex_val in ["m", "male", "f", "female"]:
                        info["sex"] = "male" if sex_val in ["m", "male"] else "female"
                    else:
                        info["sex"] = "unknown"
                else:
                    info["sex"] = "unknown"

                return info
        except Exception:
            pass

    # Default if not found
    return {"age": "unknown", "sex": "unknown"}


@dataclass
class OpenNeuroDS002723Kernel:
    """Stage1 kernel for OpenNeuro ds002723 (BCMI testing session)."""

    KERNEL_ID: str = "openneuro-ds002723-stage1"

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
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(file_path))

        # Extract subject ID from file path
        subject_id = ""
        path_parts = file_path.split(os.sep)
        for part in path_parts:
            if part.startswith("sub-"):
                subject_id = part.replace("sub-", "")
                break

        # Detect paradigm
        paradigm = _detect_paradigm(file_path)

        # Get original description
        original_description = raw.info.get("description", "")

        # Extract subject metadata
        subject_info = _extract_subject_info(dataset_path, subject_id)

        # Build eegunity_description
        # Device info from dataset documentation - inferred by LLM, needs human review
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # inferred by LLM, needs human review
                "cap": "unknown",  # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Get new channel names after rename
            ch_names_mapping = {}
            for old_name, new_name in rename_map.items():
                ch_names_mapping[old_name] = new_name

            raw.rename_channels(ch_names_mapping)

        # Set montage for EEG channels (standard 10-20 system)
        try:
            # Get standard 10-20 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            # Apply only to channels that exist in both raw and montage
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional

        # Process events/annotations
        # For BIDS format, events are typically in *_events.tsv sidecar
        # or encoded as stim channels
        events_file = file_path.replace(".vhdr", "_events.tsv").replace(
            ".eeg", "_events.tsv"
        ).replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv")

        annotations_added = False

        # Try to read events from events.tsv if it exists
        if os.path.exists(events_file):
            try:
                events_df = pd.read_csv(events_file, sep="\t")
                if "onset" in events_df.columns and "duration" in events_df.columns:
                    onset = events_df["onset"].values
                    duration = events_df["duration"].values

                    # Get event description
                    if "trial_type" in events_df.columns:
                        descriptions = events_df["trial_type"].astype(str).values
                    elif "value" in events_df.columns:
                        # Map numeric values to music condition labels
                        descriptions = []
                        for val in events_df["value"].values:
                            try:
                                int_val = int(float(val))
                                descriptions.append(_EVENT_MAP.get(int_val, str(val)))
                            except (ValueError, TypeError):
                                descriptions.append(str(val))
                    else:
                        descriptions = [str(i) for i in range(len(onset))]

                    # Filter to only include target events
                    filtered_onsets = []
                    filtered_durations = []
                    filtered_descriptions = []

                    for i, desc in enumerate(descriptions):
                        if desc in _EVENT_MAP.values():
                            filtered_onsets.append(onset[i])
                            filtered_durations.append(duration[i])
                            filtered_descriptions.append(desc)

                    if filtered_onsets:
                        annotations = mne.Annotations(
                            onset=np.array(filtered_onsets),
                            duration=np.array(filtered_durations),
                            description=filtered_descriptions,
                        )
                        raw.set_annotations(annotations)
                        annotations_added = True
            except Exception:
                pass

        # If no events from file, try to use existing annotations or stim channel
        if not annotations_added:
            try:
                # Check if there are existing annotations
                if raw.annotations:
                    # Remap existing annotations to music condition labels
                    new_descriptions = []
                    for desc in raw.annotations.description:
                        try:
                            int_desc = int(float(desc))
                            new_desc = _EVENT_MAP.get(int_desc, desc)
                            new_descriptions.append(new_desc)
                        except (ValueError, TypeError):
                            new_descriptions.append(desc)

                    new_annotations = mne.Annotations(
                        onset=raw.annotations.onset,
                        duration=raw.annotations.duration,
                        description=new_descriptions,
                    )
                    raw.set_annotations(new_annotations)
                    annotations_added = True
            except Exception:
                pass

        # Add paradigm prefix if multiple paradigms detected
        if paradigm != "testing":
            try:
                current_annotations = raw.annotations
                new_descriptions = [
                    f"{paradigm.upper()}: {desc}" for desc in current_annotations.description
                ]
                new_annotations = mne.Annotations(
                    onset=current_annotations.onset,
                    duration=current_annotations.duration,
                    description=new_descriptions,
                )
                raw.set_annotations(new_annotations)
            except Exception:
                pass

        return raw


KERNEL = OpenNeuroDS002723Kernel()