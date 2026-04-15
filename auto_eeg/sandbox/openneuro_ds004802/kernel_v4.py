"""Dataset-specific kernel for openneuro_ds004802.

Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot).
Roving oddball EEG paradigm investigating social hypersensitivity and hyperalertness.

Source: https://openneuro.org/datasets/ds004802
Events.tsv provides human-readable `event` column. Rebuild annotations from that column
so the locator reflects task semantics instead of opaque numeric codes.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne
import pandas as pd

from kernels.openneuro_specific._base import OpenNeuroBaseKernel


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find events.tsv file for a given EEG file path."""
    base_dir = os.path.dirname(file_path)
    candidates = [
        os.path.join(base_dir, "events.tsv"),
        os.path.join(base_dir, os.path.pardir, "events.tsv"),
        os.path.join(base_dir, os.path.pardir, os.path.pardir, "events.tsv"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _find_participants_tsv(dataset_root: str) -> Optional[str]:
    """Find participants.tsv file in the dataset root directory."""
    candidates = [
        os.path.join(dataset_root, "participants.tsv"),
        os.path.join(dataset_root, os.path.pardir, "participants.tsv"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _normalize_event_label(label: str) -> str:
    """Normalize event label to a clean string."""
    text = str(label).strip()
    if not text:
        return "unknown_event"
    return text.replace("/", "_").replace(" ", "_")


def _summarize_annotations(raw: mne.io.BaseRaw) -> str:
    """Summarize annotation counts for logging."""
    counts = Counter(str(desc) for desc in raw.annotations.description if str(desc).strip())
    if not counts:
        return "no_events"
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{label}: {count}" for label, count in ordered)


_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
_AMPLIFIER = "unknown"
_CAP = "Ag/AgCl"


@dataclass
class OpenNeuroDS004802Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for openneuro_ds004802 - Loneliness EEG study."""

    KERNEL_ID: str = "openneuro-ds004802"
    _description: Optional[Dict[str, str]] = None

    def _get_dataset_root(self, file_path: str) -> str:
        """Find the dataset root directory."""
        current = os.path.dirname(file_path)
        parent = os.path.dirname(current)
        while current and current != parent:
            if os.path.exists(os.path.join(current, "participants.tsv")) or \
               os.path.exists(os.path.join(current, "dataset_description.json")):
                return current
            parent = current
            current = os.path.dirname(current)
        return os.path.dirname(file_path)

    def _load_subject_info(self, file_path: str, row) -> Dict[str, str]:
        """Load subject information from participants.tsv or infer from row."""
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        dataset_root = self._get_dataset_root(file_path)
        participants_path = _find_participants_tsv(dataset_root)

        if participants_path and os.path.exists(participants_path):
            try:
                participants_df = pd.read_csv(participants_path, sep="\t")
                subject_id = row.get("subject_id", "")
                if not subject_id:
                    subject_id = row.get("participant_id", "")
                if not subject_id:
                    subject_id = row.get("subject", "")

                if subject_id:
                    subject_row = participants_df[
                        participants_df["participant_id"] == subject_id
                    ]
                    if len(subject_row) == 0:
                        key = subject_id.split("-")[-1] if "-" in subject_id else subject_id
                        subject_row = participants_df[
                            participants_df["participant_id"].str.contains(key, na=False)
                        ]

                    if len(subject_row) > 0:
                        row_data = subject_row.iloc[0]
                        if "age" in participants_df.columns:
                            age_val = row_data.get("age")
                            if pd.notna(age_val):
                                subject_info["age"] = str(int(float(age_val)))
                        if "sex" in participants_df.columns:
                            sex_val = row_data.get("sex")
                            if pd.notna(sex_val):
                                sex_str = str(sex_val).strip().lower()
                                if sex_str in ["m", "male", "f", "female"]:
                                    subject_info["sex"] = "male" if sex_str.startswith("m") else "female"
                        if "handedness" in participants_df.columns:
                            handed_val = row_data.get("handedness")
                            if pd.notna(handed_val):
                                handed_str = str(handed_val).strip().lower()
                                if handed_str in ["r", "right"]:
                                    subject_info["handedness"] = "right"
                                elif handed_str in ["l", "left"]:
                                    subject_info["handedness"] = "left"
            except Exception:
                pass

        return subject_info

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename non-standard channel names to standard 10-20 names if needed."""
        rename_map: Dict[str, str] = {}
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper()
            if ch_name.startswith("EEG-") and len(ch_name) > 4 and ch_name[4:].isdigit():
                continue
            if ch_name in ["Fp1", "Fp2", "Fpz", "F7", "F8", "F3", "F4", "Fz",
                          "T7", "T8", "C3", "C4", "Cz", "P7", "P8", "P3", "P4", "Pz",
                          "O1", "O2", "Oz"]:
                continue
            if ch_upper in [
                "FP1", "FP2", "FPZ", "F7", "F8", "F3", "F4", "FZ",
                "T7", "T8", "C3", "C4", "CZ", "P7", "P8", "P3", "P4", "PZ",
                "O1", "O2", "OZ", "AF3", "AF4", "AF7", "AF8", "AFZ",
                "FC5", "FC6", "FC3", "FC4", "FC1", "FC2", "FCZ",
                "CP5", "CP6", "CP3", "CP4", "CP1", "CP2", "CPZ",
                "PO7", "PO8", "PO3", "PO4", "POZ",
                "F1", "F2", "F5", "F6", "C1", "C2", "C5", "C6",
                "P1", "P2", "P5", "P6", "PO1", "PO2", "PO5", "PO6",
                "FT7", "FT8", "TP7", "TP8",
                "M1", "M2", "A1", "A2", "TP9", "TP10"]:
                continue

        if rename_map:
            raw.rename_channels(rename_map)

        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        return raw

    @property
    def description(self) -> Optional[Dict[str, str]]:
        """Return the eegunity_description dict set during apply."""
        return self._description

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record."""
        file_path = row.get("file_path", "")
        subject_info = self._load_subject_info(file_path, row)
        raw = super().apply(udataset, raw, row)
        if file_path:
            events_tsv = _find_events_tsv(file_path)
            if events_tsv and os.path.exists(events_tsv):
                try:
                    events_df = pd.read_csv(events_tsv, sep="\t")
                    if "onset" in events_df.columns and "event" in events_df.columns:
                        onsets = []
                        durations = []
                        descriptions = []
                        for _, ev_row in events_df.iterrows():
                            try:
                                onset_sec = float(ev_row["onset"])
                                description = _normalize_event_label(ev_row["event"])
                                duration = 0.0
                                if "duration" in events_df.columns:
                                    try:
                                        duration = float(ev_row["duration"])
                                    except (ValueError, TypeError):
                                        duration = 0.0
                                onsets.append(onset_sec)
                                durations.append(duration)
                                descriptions.append(description)
                            except (ValueError, TypeError, KeyError):
                                continue
                        if onsets:
                            new_annotations = mne.Annotations(
                                onset=onsets,
                                duration=durations,
                                description=descriptions,
                                orig_time=raw.annotations.orig_time,
                            )
                            raw.set_annotations(raw.annotations + new_annotations, on_missing="warn")
                except Exception:
                    pass
        raw = self._rename_channels(raw)
        self._description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": subject_info.get("handedness", "unknown"),
        }
        return raw


KERNEL = OpenNeuroDS004802Kernel()