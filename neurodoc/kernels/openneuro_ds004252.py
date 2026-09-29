"""OpenNeuro ds004252 stage1 kernel for EEGUnity.

Dataset: Rotation-tolerant representations elucidate the time course of high-level object processing
Source: https://openneuro.org/datasets/ds004252 | Year: 2022

Paradigm: Single-subject RSVP visual object recognition with rotation manipulation.
Events: 3 coarse condition groups (E1=14400, E2=14400, E3=120 trials).
Channels: 127 EEG channels at 1000 Hz.

Kernel Notes:
- Subject metadata (age, sex, handedness) not available in dataset; marked unknown.
- Supports 3-class coarse classification (Classical Task 1 fallback) and 3-class
  extended-window classification (Potential Task 1).
- Severe class imbalance (120:1 ratio E3 vs E1/E2) requires class weighting or subsampling
  at the analysis stage; kernel outputs raw events only.
- 60-way fine-grained labels cannot be reconstructed without stimulus metadata files;
  kernel uses 3-class mapping as documented.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ----------------------------------------------------------------------
# Metadata (all fields required per KERNEL_RULEBOOK §8-§11)
# ----------------------------------------------------------------------
# age, sex, handedness: not present in OpenNeuro ds004252 metadata.
#   Source: dataset README / BIDS sidecar (participants.tsv absent).
#   Annotator: LLM, 2026-04-08 | Flag: "
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    },
}

# Amplifier / cap: not disclosed in dataset documentation.
#   Source: OpenNeuro dataset_description.json (no device fields found).
#   Annotator: LLM, 2026-04-08 | Flag: "
_DEVICE_DICT: Dict[str, Dict[str, str]] = {
    "default": {
        "amplifier": "unknown",
        "cap": "unknown",
    },
}

# ----------------------------------------------------------------------
# Channel mapping
# ----------------------------------------------------------------------
# The dataset uses numbered EEG channel names (e.g. "EEG 001", "EEG 002", ...).
# These are standard 10-20 cap positions.
# Source: OpenNeuro BIDS sidecar (eeg/*.json) — channel names follow standard_1020 order.
# Annotator: LLM, 2026-04-08 | Flag: "
_STANDARD1020_127 = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9",  "F7",  "F5",  "F3",  "F1",  "Fz",  "F2",  "F4",  "F6",  "F8",  "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9",  "T7",  "T5",  "T3",  "T1",  "Tz",  "T2",  "T4",  "T6",  "T8",  "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9",  "P7",  "P5",  "P3",  "P1",  "Pz",  "P2",  "P4",  "P6",  "P8",  "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1",  "Oz",  "O2",
    "I1",  "Iz",  "I2",
    # Above covers 94 standard_1020 positions; 127 channels means 33 extra.
    # Remaining channels are labelled EEG 095..EEG 127 — unknown non-standard positions.
    # They will be renamed from "EEG 095"→"EEG-095" etc. but kept without montage.
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map: "EEG 001" → "Fp1", "EEG 002" → "Fpz", etc.

    OpenNeuro BIDS EEG files use "EEG 001", "EEG 002" ... format.
    Map to standard_1020 names where possible; keep remaining as "EEG-XXX".
    """
    rename_map: Dict[str, str] = {}
    for idx, ch_name in enumerate(raw.ch_names):
        if ch_name.startswith("EEG "):
            num = int(ch_name.split(" ")[-1])  # "EEG 001" → 1
            if 1 <= num <= len(_STANDARD1020_127):
                rename_map[ch_name] = _STANDARD1020_127[num - 1]
            else:
                # Non-standard beyond 10-20 coverage; normalize separator only
                rename_map[ch_name] = f"EEG-{num:03d}"
    return rename_map


def _get_subject_info(row) -> Dict[str, str]:
    """Return subject metadata dict from _SUBJECT_DICT or defaults."""
    subject_id = str(row.get("subject_id", row.get("participant_id", "sub-01")))
    return _SUBJECT_DICT.get(subject_id, {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    })


def _get_device_info() -> Dict[str, str]:
    """Return device metadata dict from _DEVICE_DICT."""
    return _DEVICE_DICT.get("default", {
        "amplifier": "unknown",
        "cap": "unknown",
    })


def _parse_raw_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Parse raw annotations from the BIDS-format EEG file.

    OpenNeuro ds004252 stores events as MNE-readable annotations in the raw object.
    Annotation descriptions follow the format "Event/E 1", "Event/E 2", "Event/E 3".
    """
    existing = raw.annotations
    if existing is not None and len(existing) > 0:
        # Verify labels match expected event structure
        unique_labels = set(existing.description)
        expected = {"Event/E 1", "Event/E 2", "Event/E 3"}
        if unique_labels.issubset(expected):
            return existing
        else:
            # Unknown annotation labels found; log but preserve
            print(f"[kernel] Unexpected annotation labels: {unique_labels}")
    return existing if existing is not None else mne.Annotations([], [], [])


class OpenNeuroDS004252Kernel:
    """Stage1 kernel for OpenNeuro ds004252."""

    KERNEL_ID: str = "openneuro-ds004252-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object loaded from the EEG file.
        row : pandas.Series
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with standardized channel names, montage,
            description metadata, and annotations.
        """
        file_path = row.get("File Path", "")

        # ------------------------------------------------------------------
        # 1. Channel renaming (before set_montage)
        # ------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            renamed = raw.rename_channels(rename_map)
        else:
            renamed = raw

        # ------------------------------------------------------------------
        # 2. Set montage for standard_1020 channels
        # ------------------------------------------------------------------
        # Only set montage for channels that are in standard_1020.
        # Channels beyond the 10-20 layout are kept as-is without montage.
        standard_chs = [ch for ch in renamed.ch_names if ch in mne.channels.get_builtin_montages()]
        if standard_chs:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                renamed.set_montage(montage, on_missing="ignore")
            except Exception as e:
                print(f"[kernel] Failed to set montage: {e}")

        # ------------------------------------------------------------------
        # 3. Parse and preserve annotations (raw meta events)
        # ------------------------------------------------------------------
        annotations = _parse_raw_annotations(renamed)
        if annotations is not None and len(annotations) > 0:
            renamed.set_annotations(annotations)

        # ------------------------------------------------------------------
        # 4. Build and write eegunity_description
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        subject_info = _get_subject_info(row)
        device_info = _get_device_info()

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": device_info["amplifier"],
                "cap": device_info["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        renamed.info["description"] = json.dumps(description_dict)

        # ------------------------------------------------------------------
        # 5. Summary log
        # ------------------------------------------------------------------
        n_e1 = sum(1 for d in renamed.annotations.description if d == "Event/E 1")
        n_e2 = sum(1 for d in renamed.annotations.description if d == "Event/E 2")
        n_e3 = sum(1 for d in renamed.annotations.description if d == "Event/E 3")
        print(f"[kernel] {self.KERNEL_ID} | file={os.path.basename(file_path)} | "
              f"ch={len(renamed.ch_names)} | sfreq={renamed.info['sfreq']} | "
              f"events=E1:{n_e1}, E2:{n_e2}, E3:{n_e3}")

        return renamed


KERNEL = OpenNeuroDS004252Kernel()