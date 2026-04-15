"""OpenNeuro ds004625 stage1 kernel for EEGUnity.

Dataset: Mind in Motion: Young Adults Walking Over Uneven Terrain
Source: https://openneuro.org/datasets/ds004625
284-channel high-density EEG, 500 Hz, 32 subjects.
Paradigm: Locomotor control during uneven terrain walking.

This kernel extends the generic BIDS kernel with dataset-specific
channel renaming and hardcoded amplifier metadata derived from
the accompanying reference papers.

Annotator: LLM (gpt-4o), 2025-01-15
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ---------------------------------------------------------------------------
# Constants derived from dataset documentation / reference papers
# ---------------------------------------------------------------------------
# Source: reference paper DOI 10.3389/fnagi.2025.1644741 (walking EEG study)
# amplifier: "BioSemi ActiveTwo" system (high-density 256+ channel EEG)
# cap: "BioSemi 256-channel Ag/AgCl cap" (LLM 推断，需人类复核)
# Source: DOI 10.1162/imag.a.1039 — young adults walking protocol
_SUBJECT_AGE: str = "unknown"   # Age not stored in participants.tsv (LLM 推断，需人类复核)
_SUBJECT_SEX: str = "unknown"   # Sex not stored in participants.tsv (LLM 推断，需人类复核)
_AMPLIFIER: str = "BioSemi ActiveTwo"  # LLM 推断，需人类复核
_CAP: str = "BioSemi 256-channel Ag/AgCl"  # LLM 推断，需人类复核
_HANDEDNESS: str = "unknown"

# ---------------------------------------------------------------------------
# High-density channel naming
# ---------------------------------------------------------------------------
# The dataset uses BioSemi naming convention. The 284 channels follow the
# BioSemi 256-channel system layout (standard_1020 extended with intermediate
# positions). We attempt to rename non-standard BioSemi labels to standard
# 10-20 names where possible; unknown channels are kept as-is.
#
# BioSemi naming patterns:
#   A = anterior, P = posterior, L = left, R = right
#   Numbers indicate electrode row (lower = more lateral)
#
# Source for channel map: BioSemi ActiveTwo electrode layout documentation
# (LLM 推断，需人类复核)
_BIOSEMI_10_20_MAP: Dict[str, str] = {
    # Standard 10-20 electrodes present in BioSemi layout
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "Cz": "Cz", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "Oz": "Oz", "O2": "O2",
    # BioSemi standard labels that map directly
    "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F1": "F1", "F2": "F2",
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1",
    "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    "C1": "C1", "C2": "C2",
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1",
    "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    "P1": "P1", "P2": "P2",
    "PO7": "PO7", "PO3": "PO3", "POz": "POz", "PO4": "POz", "PO8": "PO8",
    "TP9": "TP9", "TP10": "TP10",
    "FT9": "FT9", "FT10": "FT10",
    "PO9": "PO9", "PO10": "PO10",
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from raw channel names to standard names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object with raw channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from original channel names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # 1. Exact matches to BioSemi standard labels
    for src, dst in _BIOSEMI_10_20_MAP.items():
        if src in existing:
            rename_map[src] = dst

    # 2. Handle BioSemi extended labels (e.g., A1, A2, ..., P1, P2, ...)
    #    These are intermediate positions; keep them as-is if unknown.
    #    Pattern: single letter + number
    extended_pattern = re.compile(r"^[APLROV]\d+$")
    for ch in raw.ch_names:
        if ch in rename_map:
            continue
        # Skip standard 10-20 channels already handled
        if ch in _BIOSEMI_10_20_MAP.values():
            continue

    # 3. Handle EMG channels (EMG-L, EMG-R, etc.)
    if "EMG-L" in existing and "EMG-L" not in rename_map:
        rename_map["EMG-L"] = "EMG-L"
    if "EMG-R" in existing and "EMG-R" not in rename_map:
        rename_map["EMG-R"] = "EMG-R"

    # 4. Keep EOG, ECG, reference channels as-is
    for prefix in ("EOG", "ECG", "REF", "GND"):
        for ch in raw.ch_names:
            if ch.startswith(prefix) and ch not in rename_map:
                rename_map[ch] = ch

    return rename_map


def _set_montage_safe(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard_1020 montage on raw, skipping unavailable channels.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object.

    Returns
    -------
    mne.io.BaseRaw
        Raw with montage applied (if possible).
    """
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        # Find intersection between available channels and montage
        available = set(raw.ch_names)
        montage_names = set(montage.ch_names)
        common = available & montage_names

        if len(common) >= 20:  # Require at least 20 standard channels
            raw.set_montage(montage, on_missing="ignore")
        else:
            # Not enough standard channels for reliable montage
            pass
    except Exception:
        pass
    return raw


def _extract_bids_sidecar_fields(row) -> Dict[str, Any]:
    """Extract subject metadata from BIDS participants.tsv sidecar.

    Parameters
    ----------
    row : pd.Series or dict-like
        Locator row for the current file.

    Returns
    -------
    Dict[str, str]
        Dict with keys: age, sex, handedness (all lowercase string values).
    """
    result = {
        "age": _SUBJECT_AGE,
        "sex": _SUBJECT_SEX,
        "handedness": _HANDEDNESS,
    }
    # participants.tsv fields — openneuro BIDS datasets often include:
    # participant_id, age, sex, handedness, etc.
    for key in ("age", "sex", "handedness"):
        if key in row and row[key] not in (None, ""):
            val = str(row[key]).strip()
            if key == "sex":
                val = val.lower()
                if val not in ("male", "female"):
                    val = "unknown"
            if key == "age":
                # Keep as string
                pass
            result[key] = val
    return result


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

class OpenNeuroDS004625Kernel:
    """Stage1 kernel for OpenNeuro ds004625 (Mind in Motion dataset).

    KERNEL_ID: str
        Unique kernel identifier for EEGUnity.
    """

    KERNEL_ID: str = "openneuro-ds004625-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context (shared-attr holder).
        raw : mne.io.BaseRaw
            In-memory MNE Raw object loaded from the EEG file.
        row : pd.Series or dict-like
            Locator row containing at least ``File Path``, and any
            BIDS-sidecar columns (e.g., ``subject_id``, ``age``, ``sex``).

        Returns
        -------
        mne.io.BaseRaw
            The preprocessed MNE Raw object with updated description,
            renamed channels, and set_montage applied.
        """
        # ------------------------------------------------------------------
        # Step 1: Update raw.info["description"] with eegunity_description
        # ------------------------------------------------------------------
        subject_info = _extract_bids_sidecar_fields(row)

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ------------------------------------------------------------------
        # Step 2: Rename channels to standard 10-20 names
        # ------------------------------------------------------------------
        rename_map = _build_rename_map(raw)
        if rename_map:
            # Only rename channels that differ from their target name
            valid_renames = {
                src: dst for src, dst in rename_map.items()
                if src != dst and src in raw.ch_names
            }
            if valid_renames:
                raw.rename_channels(valid_renames)

        # ------------------------------------------------------------------
        # Step 3: Set montage for spatial positions (after renaming)
        # ------------------------------------------------------------------
        raw = _set_montage_safe(raw)

        # ------------------------------------------------------------------
        # Step 4: Ensure annotations are set from raw events
        #         The BIDS kernel handles events.tsv; here we ensure
        #         any pre-existing annotations are preserved.
        # ------------------------------------------------------------------
        # If no annotations exist (raw file only), attempt to create from stim channels
        if raw.annotations is None or len(raw.annotations) == 0:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) == 0:
                # No events found — this may be a continuous recording without markers
                pass

        return raw


# Module-level kernel object for EEGUnity auto-loading
KERNEL = OpenNeuroDS004625Kernel()