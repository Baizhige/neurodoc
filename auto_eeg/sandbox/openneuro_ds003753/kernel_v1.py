"""OpenNeuro DS003753 stage1 kernel for EEGUnity.

Probabilistic Learning with Affective Feedback dataset.
66-channel EEG, 500 Hz sampling rate, 25 subjects.
BIDS format with events.tsv containing trial_type for FB subtype decoding.

Source: https://openneuro.org/datasets/ds003753
Paper: https://doi.org/10.3758/s13415-021-00950-5
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.3758/s13415-021-00950-5, Methods section
# 64-channel BrainVision system with FCz reference
# LLM 推断，需人类复核
_AMPLIFIER = "BrainVision Recorder"

# Source: Dataset documentation
# LLM 推断，需人类复核
_CAP = "Ag/AgCl"

# Source: Dataset README / participants.tsv
_PARTICIPANTS_DICT: Dict[str, Dict[str, str]] = {}
# Populated dynamically from participants.tsv in apply()


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    participants_dict: Dict[str, Dict[str, str]] = {}

    if os.path.exists(participants_file):
        df = pd.read_csv(participants_file, sep="\t")
        for _, row in df.iterrows():
            subj_id = str(row.get("participant_id", ""))
            if not subj_id:
                continue
            participants_dict[subj_id] = {
                "age": str(row.get("age", "unknown")),
                "sex": str(row.get("sex", "unknown")).lower(),
                "handedness": str(row.get("handedness", "unknown")).lower(),
            }

    return participants_dict


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    base_dir = os.path.dirname(file_path)
    sub_dir = os.path.dirname(base_dir)
    eeg_dir = os.path.dirname(sub_dir)
    sub_id = os.path.basename(sub_dir)

    possible_paths = [
        os.path.join(base_dir, f"{sub_id}_events.tsv"),
        os.path.join(base_dir, f"*{sub_id}*_events.tsv"),
        os.path.join(sub_dir, f"{sub_id}_events.tsv"),
    ]

    for pattern in possible_paths:
        if "*" in pattern:
            import glob

            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        elif os.path.exists(pattern):
            return pattern

    return None


def _decode_fb_valence(events_tsv: str) -> Dict[int, str]:
    """Decode FB event valence (liked/disliked) from events.tsv trial_type column.

    Returns dict mapping event index to valence label.
    Source: events.tsv trial_type column decoding
    """
    valence_map: Dict[int, str] = {}

    if events_tsv and os.path.exists(events_tsv):
        df = pd.read_csv(events_tsv, sep="\t")
        if "trial_type" in df.columns and "value" in df.columns:
            for idx, row in df.iterrows():
                value = str(row.get("value", ""))
                trial_type = str(row.get("trial_type", ""))

                if value in ["FB", "S  2", "S  3", "S  4"]:
                    if "liked" in trial_type.lower() or "puppy" in trial_type.lower():
                        valence_map[idx] = "liked"
                    elif "disliked" in trial_type.lower() or "chair" in trial_type.lower():
                        valence_map[idx] = "disliked"

    return valence_map


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for non-standard names.

    Dataset uses BrainVision format with potential non-standard naming.
    Source: Dataset channel listing
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    standard_channels = {
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "AF7", "AF3", "AF4", "AF8",
        "F1", "F2", "F5", "F6",
        "FC5", "FC3", "FC1", "FC2", "FC4", "FC6",
        "C5", "C6",
        "CP5", "CP3", "CP1", "CP2", "CP4", "CP6",
        "P1", "P2", "P5", "P6",
        "PO7", "PO3", "PO4", "PO8",
        "EOG-left", "EOG-right", "EOG-central",
    }

    for ch in ch_names:
        if ch.startswith("EEG"):
            suffix = ch[3:].strip()
            if suffix in standard_channels:
                rename_map[ch] = suffix
            elif suffix.isdigit():
                pass
        elif ch in ["EOG", "EOG-left", "EOG-right"]:
            if "left" in ch.lower():
                rename_map[ch] = "EOG-left"
            elif "right" in ch.lower():
                rename_map[ch] = "EOG-right"
            else:
                rename_map[ch] = "EOG-central"

    return rename_map


def _detect_subj_id(file_path: str) -> Optional[str]:
    """Extract subject ID from file path."""
    match = re.search(r"sub-[A-Za-z0-9]+", file_path)
    if match:
        return match.group(0).replace("sub-", "")
    return None


class OpenNeuroDS003753Kernel:
    """Stage1 kernel for OpenNeuro DS003753 dataset."""

    KERNEL_ID: str = "openneuro-ds003753-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        dataset_path = udataset.path if hasattr(udataset, "path") else os.path.dirname(os.path.dirname(file_path))

        subj_id = _detect_subj_id(file_path)

        participants_dict = _load_participants_tsv(dataset_path)
        subj_info = participants_dict.get(subj_id, {})

        age = subj_info.get("age", "unknown")
        sex = subj_info.get("sex", "unknown")
        handedness = subj_info.get("handedness", "unknown")

        original_description = raw.info.get("description", "")

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            renamed = raw.rename_channels(rename_map)
            raw = renamed if renamed is not None else raw

        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass

        events_tsv = _find_events_tsv(file_path)
        fb_valence_map = _decode_fb_valence(events_tsv)

        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = np.array([]).reshape(0, 3)
            event_id = {}

        if len(events) > 0:
            onset_times = events[:, 0] / raw.info["sfreq"]
            descriptions = []

            for i, ev in enumerate(events):
                orig_desc = list(event_id.keys())[list(event_id.values()).index(ev[2])] if ev[2] in event_id.values() else str(ev[2])
                descriptions.append(orig_desc)

            annotations = mne.Annotations(
                onset=onset_times,
                duration=[0.0] * len(events),
                description=descriptions,
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS003753Kernel()