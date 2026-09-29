"""OpenNeuro ds005406 stage1 kernel for EEGUnity.

EEG frequency-tagging SSVEP study with 29 subjects, 64 channels, 1000 Hz.
Paradigm: Action observation with frequency tagging (2.5 Hz, 3.16 Hz fundamentals
and 5.66 Hz intermodulation product). Four action conditions from 2x2 factorial
design (movement type: same/different × agent number: 1P/2P).

Source: https://openneuro.org/datasets/ds005406
DOI: 10.1101/2024.05.10.593473
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# 64-channel standard layout mapping from BrainVision numbered channels.
# Source: BrainVision recorder default 64-channel layout (ActiCap/ActiCHamp).
# The standard 64-channel cap uses positions: FP1, FP2, F7, F3, Fz, F4, F8,
# FC5, FC3, FC1, FCz, FC2, FC4, FC6, T7, C5, C3, C1, Cz, C2, C4, C6, T8,
# CP5, CP3, CP1, CPz, CP2, CP4, CP6, P7, P5, P3, P1, Pz, P2, P4, P6, P8,
# PO9, PO7, PO3, POz, PO4, PO8, PO10, O1, Oz, O2, plus special channels.
# Annotator: LLM, 2026-04-08; inferred by LLM, needs human review
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "1": "FP1",
    "2": "FP2",
    "3": "F7",
    "4": "F3",
    "5": "Fz",
    "6": "F4",
    "7": "F8",
    "8": "FC5",
    "9": "FC3",
    "10": "FC1",
    "11": "FCz",
    "12": "FC2",
    "13": "FC4",
    "14": "FC6",
    "15": "T7",
    "16": "C5",
    "17": "C3",
    "18": "C1",
    "19": "Cz",
    "20": "C2",
    "21": "C4",
    "22": "C6",
    "23": "T8",
    "24": "CP5",
    "25": "CP3",
    "26": "CP1",
    "27": "CPz",
    "28": "CP2",
    "29": "CP4",
    "30": "CP6",
    "31": "P7",
    "32": "P5",
    "33": "P3",
    "34": "P1",
    "35": "Pz",
    "36": "P2",
    "37": "P4",
    "38": "P6",
    "39": "P8",
    "40": "PO9",
    "41": "PO7",
    "42": "PO3",
    "43": "POz",
    "44": "PO4",
    "45": "PO8",
    "46": "PO10",
    "47": "O1",
    "48": "Oz",
    "49": "O2",
    "50": "I",  # Iz (Inion)
    "51": "AF9",
    "52": "AF7",
    "53": "AF3",
    "54": "AFz",
    "55": "AF4",
    "56": "AF8",
    "57": "AF10",
    "58": "F9",
    "59": "F10",
    "60": "M1",
    "61": "M2",
    "62": "TP9",
    "63": "TP10",
    "64": "AUX",
}

# Subject metadata: all fields unknown since participants.tsv not confirmed.
# Annotator: LLM, 2026-04-08; inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Raw event annotation mapping (Stimulus/S XX codes).
# Keys are numeric strings since mne.events_from_annotations returns numeric codes.
_RAW_EVENT_MAP: Dict[str, str] = {
    "11": "Stimulus/S 11",
    "12": "Stimulus/S 12",
    "21": "Stimulus/S 21",
    "22": "Stimulus/S 22",
    "31": "Stimulus/S 31",
    "32": "Stimulus/S 32",
    "41": "Stimulus/S 41",
    "42": "Stimulus/S 42",
    "255": "admin: marker-255",
}

# Admin event codes to exclude from raw meta.
_ADMIN_EVENTS: set = {"admin: marker-255", "admin: segment_boundary"}


@dataclass
class OpenNeuroDS005406Kernel:
    """Stage1 kernel for OpenNeuro ds005406 SSVEP action observation dataset."""

    KERNEL_ID: str = "openneuro-ds005406-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context.
        raw : MNE Raw object loaded from BrainVision files.
        row : Locator row with File Path and Subject ID.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw with channel renaming, montage, and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = str(row.get("Subject ID", "unknown"))

        # 1. Rename numbered channels to standard 10-20 names.
        raw = self._rename_channels(raw)

        # 2. Set standard 10-20 montage.
        raw = self._set_montage(raw)

        # 3. Extract and set annotations from events.
        raw = self._set_annotations(raw)

        # 4. Build and write eegunity_description.
        raw = self._write_description(raw, subject_id)

        return raw

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename numbered channels to standard 10-20 names."""
        rename_map: Dict[str, str] = {}
        for ch_name in raw.ch_names:
            # Match pure numeric channel names or EEG-NN format.
            match = re.match(r"^(?:EEG-)?(\d+)$", ch_name, re.IGNORECASE)
            if match:
                num_str = match.group(1)
                if num_str in _CHANNEL_RENAME_MAP:
                    rename_map[ch_name] = _CHANNEL_RENAME_MAP[num_str]

        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage for renamed channels."""
        try:
            # Try standard 1020 system first.
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # Fallback: try to set only those channels that exist in montage.
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass

        return raw

    def _set_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Extract events from raw and convert to annotations."""
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            return raw

        # Build annotation onset/duration/description lists.
        onsets: List[float] = []
        durations: List[float] = []
        descriptions: List[str] = []

        for event in events:
            onset_sample = event[0]
            onset_sec = onset_sample / raw.info["sfreq"]
            event_code = event[2]

            # Map numeric code to annotation description.
            desc = self._map_event_code(event_code)
            if desc is None:
                continue

            # Skip admin events.
            if desc in _ADMIN_EVENTS:
                continue

            onsets.append(onset_sec)
            durations.append(0.0)
            descriptions.append(desc)

        if onsets:
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            raw.set_annotations(annotations)

        return raw

    def _map_event_code(self, code: int) -> Optional[str]:
        """Map numeric event code to canonical event label."""
        # BrainVision stores events as integer codes like 11, 12, 21, etc.
        code_str = str(code)
        return _RAW_EVENT_MAP.get(code_str)

    def _write_description(
        self, raw: mne.io.BaseRaw, subject_id: str
    ) -> mne.io.BaseRaw:
        """Write eegunity_description to raw.info['description']."""
        # Get subject metadata from dictionary if available.
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # Fill in fields from subject dict or mark as unknown.
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        # Amplifier and cap: inferred from paradigm documentation.
        # Source: Paper DOI 10.1101/2024.05.10.593473 suggests standard
        # EEG lab equipment; exact model not specified in available materials.
        # Annotator: LLM, 2026-04-08; inferred by LLM, needs human review
        amplifier = "unknown"
        cap = "unknown"

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex),
                "amplifier": str(amplifier),
                "cap": str(cap),
                "handedness": str(handedness),
            },
        }

        raw.info["description"] = json.dumps(description_dict)
        return raw


KERNEL = OpenNeuroDS005406Kernel()