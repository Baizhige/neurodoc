"""Stage1 kernel for OpenNeuro ds002691 - Internal attention study.

Dataset: https://openneuro.org/datasets/ds002691
Paradigm: Sustained internal attention (concentrate vs relax) with 15-second blocks.
Subjects: 20 | Channels: 32 | Sampling Rate: 250 Hz

Primary Events:
- D100: Relax condition (y=0)
- D101: Concentrate condition (y=1)

Source: Ceh et al. (2020) Neurophysiological indicators of internal attention.
        DOI: 10.3389/fnins.2021.664490
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: Dataset README / participants.tsv (if available)
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-10": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-11": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-12": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-13": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-14": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-15": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-16": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-17": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-18": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-19": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-20": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# =============================================================================
# Event Mapping (raw meta level)
# =============================================================================
# Primary condition events (D100/D101 are the main experimental markers)
# D100: Relax condition (baseline)
# D101: Concentrate condition (internal attention)
# DI* codes: Internal markers for timing (dense ~40ms resolution within blocks)
# Other D* codes: Block progression markers (varying resolution)
# Source: Dataset event structure from analysis.md
# Annotator: Human, 2026-04-08
_RAW_EVENT_MAP: Dict[str, str] = {
    "D100": "relax",
    "D101": "concentrate",
    "D102": "relax_progress",
    "D103": "concentrate_progress",
    "D104": "relax_progress",
    "D105": "concentrate_progress",
    "D106": "relax_progress",
    "D107": "concentrate_progress",
    "D108": "relax_progress",
    "D109": "concentrate_progress",
    "D110": "relax_progress",
    "D111": "concentrate_progress",
    "D112": "relax_progress",
    "D113": "concentrate_progress",
    "D114": "relax_progress",
    "D115": "concentrate_progress",
    "D116": "relax_progress",
    "D117": "concentrate_progress",
    "D118": "relax_progress",
    "D119": "concentrate_progress",
    "D120": "relax_progress",
    "D121": "concentrate_progress",
    "D122": "relax_progress",
    "D124": "relax_progress",
    "D125": "concentrate_progress",
    "D127": "relax_progress",
    "D139": "transition",
    "D140": "transition",
    "D141": "transition",
    "D142": "transition",
    "D143": "transition",
    "D144": "transition",
    "D145": "transition",
    "D146": "transition",
    "D147": "transition",
    "D148": "transition",
    "D149": "transition",
    "D150": "transition",
    "D151": "transition",
    "D152": "transition",
    "D153": "transition",
    "D154": "transition",
    "D155": "transition",
    "D156": "transition",
    "D157": "transition",
    "D158": "transition",
    "D159": "transition",
    "D160": "transition",
    "D161": "transition",
    "D162": "transition",
    "D163": "transition",
    "D164": "transition",
    "D165": "transition",
    "D166": "transition",
    "D167": "transition",
    "D168": "transition",
    "D169": "transition",
    "D170": "transition",
    "D171": "transition",
    "D172": "transition",
    "D173": "transition",
    "D174": "transition",
    "D175": "transition",
    "D176": "transition",
    "D177": "transition",
    "D178": "transition",
    "D179": "transition",
    "D180": "transition",
    "D181": "transition",
    "D182": "transition",
    "D183": "transition",
    "D184": "transition",
    "D185": "transition",
    "D186": "transition",
    "D187": "transition",
    "D188": "transition",
    "D192": "admin_marker",
    "D194": "admin_marker",
    "D201": "admin_marker",
    "D203": "admin_marker",
    "D204": "admin_marker",
    "D205": "admin_marker",
    "D206": "admin_marker",
    "D207": "admin_marker",
    "D208": "admin_marker",
    "D209": "admin_marker",
    "D210": "admin_marker",
    "D211": "admin_marker",
    "D212": "admin_marker",
    "D213": "admin_marker",
    "D214": "admin_marker",
    "D215": "admin_marker",
}

# =============================================================================
# Channel Name Mapping
# =============================================================================
# Based on BrainVision / standard 32-channel EEG cap (BrainCap 32Ch)
# Source: Dataset documentation and standard electrode naming
# Annotator: Human, 2026-04-08
_EEG_CHANNEL_ALIASES: List[Tuple[str, List[str]]] = [
    ("Fp1", ["Fp1", "EEG-Fp1", "EEG Fp1", "FP1", "EEG-FP1"]),
    ("Fp2", ["Fp2", "EEG-Fp2", "EEG Fp2", "FP2", "EEG-FP2"]),
    ("F7", ["F7", "EEG-F7", "EEG F7", "F07"]),
    ("F3", ["F3", "EEG-F3", "EEG F3"]),
    ("Fz", ["Fz", "EEG-Fz", "EEG Fz", "Fz"]),
    ("F4", ["F4", "EEG-F4", "EEG F4"]),
    ("F8", ["F8", "EEG-F8", "EEG F8", "F08"]),
    ("T7", ["T7", "EEG-T7", "EEG T7", "T7", "EEG-T3", "T3"]),
    ("C3", ["C3", "EEG-C3", "EEG C3"]),
    ("Cz", ["Cz", "EEG-Cz", "EEG Cz", "Cz"]),
    ("C4", ["C4", "EEG-C4", "EEG C4"]),
    ("T8", ["T8", "EEG-T8", "EEG T8", "T8", "EEG-T4", "T4"]),
    ("P7", ["P7", "EEG-P7", "EEG P7", "P7", "EEG-T5", "T5"]),
    ("P3", ["P3", "EEG-P3", "EEG P3"]),
    ("Pz", ["Pz", "EEG-Pz", "EEG Pz", "Pz"]),
    ("P4", ["P4", "EEG-P4", "EEG P4"]),
    ("P8", ["P8", "EEG-P8", "EEG P8", "P8", "EEG-T6", "T6"]),
    ("O1", ["O1", "EEG-O1", "EEG O1"]),
    ("Oz", ["Oz", "EEG-Oz", "EEG Oz"]),
    ("O2", ["O2", "EEG-O2", "EEG O2"]),
    ("AF7", ["AF7", "EEG-AF7", "EEG AF7"]),
    ("AF3", ["AF3", "EEG-AF3", "EEG AF3"]),
    ("AF4", ["AF4", "EEG-AF4", "EEG AF4"]),
    ("AF8", ["AF8", "EEG-AF8", "EEG AF8"]),
    ("F1", ["F1", "EEG-F1", "EEG F1"]),
    ("F2", ["F2", "EEG-F2", "EEG F2"]),
    ("FC5", ["FC5", "EEG-FC5", "EEG FC5"]),
    ("FC1", ["FC1", "EEG-FC1", "EEG FC1"]),
    ("FC2", ["FC2", "EEG-FC2", "EEG FC2"]),
    ("FC6", ["FC6", "EEG-FC6", "EEG FC6"]),
    ("C1", ["C1", "EEG-C1", "EEG C1"]),
    ("C2", ["C2", "EEG-C2", "EEG C2"]),
    ("CP5", ["CP5", "EEG-CP5", "EEG CP5"]),
    ("CP1", ["CP1", "EEG-CP1", "EEG CP1"]),
    ("CP2", ["CP2", "EEG-CP2", "EEG CP2"]),
    ("CP6", ["CP6", "EEG-CP6", "EEG CP6"]),
    ("P1", ["P1", "EEG-P1", "EEG P1"]),
    ("P2", ["P2", "EEG-P2", "EEG P2"]),
    ("PO3", ["PO3", "EEG-PO3", "EEG PO3"]),
    ("PO4", ["PO4", "EEG-PO4", "EEG PO4"]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map from raw channel names to standard names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data.

    Returns
    -------
    Dict[str, str]
        Mapping from original channel names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in _EEG_CHANNEL_ALIASES:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _detect_subject_id(row) -> str:
    """Detect subject ID from row data.

    Parameters
    ----------
    row : pandas.Series
        Dataset locator row.

    Returns
    -------
    str
        Subject ID (e.g., 'sub-01').
    """
    if "Subject ID" in row:
        return str(row["Subject ID"])
    if "File Path" in row:
        file_path = row["File Path"]
        match = re.search(r"(sub-\d+)", str(file_path))
        if match:
            return match.group(1)
    return "unknown"


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap annotation descriptions using raw event map.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data.

    Returns
    -------
    mne.io.BaseRaw
        Raw with remapped annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    new_descriptions = []
    for desc in raw.annotations.description:
        mapped = _RAW_EVENT_MAP.get(str(desc), str(desc))
        new_descriptions.append(mapped)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    return raw


def _try_set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard montage if channels are recognized.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data.

    Returns
    -------
    mne.io.BaseRaw
        Raw with montage set if successful.
    """
    eeg_channels = [ch for ch in raw.ch_names
                    if raw.get_channel_types()[raw.ch_names.index(ch)] == "eeg"]

    recognized = []
    for ch in eeg_channels:
        try:
            pos = mne.channels.make_standard_montage("standard_1020").get_positions()[ch]
            if pos is not None:
                recognized.append(ch)
        except Exception:
            continue

    if len(recognized) >= 20:
        try:
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass

    return raw


@dataclass
class OpenNeuroDS002691Kernel:
    """Stage1 kernel for OpenNeuro ds002691 dataset.

    Internal attention study with concentrate vs relax conditions.
    """

    KERNEL_ID: str = "openneuro-ds002691-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            Raw EEG data loaded by EEGUnity.
        row : pandas.Series
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw EEG data.
        """
        original_description = raw.info.get("description", "")

        subject_id = _detect_subject_id(row)
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        if age == "unknown":
            age = "unknown"  # LLM 推断，需人类复核
        if sex == "unknown":
            sex = "unknown"  # LLM 推断，需人类复核
        if handedness == "unknown":
            handedness = "unknown"  # LLM 推断，需人类复核

        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        raw = _try_set_montage(raw)

        raw = _remap_annotations(raw)

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex).lower(),
                "amplifier": "BrainAmp",  # LLM 推断，需人类复核 - typical for this paradigm
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核 - standard EEG cap
                "handedness": str(handedness),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS002691Kernel()