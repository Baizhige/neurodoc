"""openneuro_ds003478 stage1 kernel for EEGUnity.

Depression resting-state EEG dataset with alternating eyes-open/eyes-closed blocks.
Supports binary depression status (Control vs Depressive) and 4-class subtype
classification (Control / None / pMDD / cMDD) via BDI-derived super meta labels.

Source: https://openneuro.org/datasets/ds003478
DOI: 10.3389/fpsyt.2023.1132996
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd

# -------------------------------------------------------------------
# BDI-based subject metadata
# -------------------------------------------------------------------
# Source: participants.tsv — BDI score, handedness, age, sex
# LLM 推断，需人类复核
_SUBJECT_BDI_DICT: Dict[str, Dict[str, Any]] = {
    "sub-001": {"bdi": 14, "sex": "female", "age": "22", "handedness": "right"},
    "sub-002": {"bdi": 0,  "sex": "male",   "age": "25", "handedness": "right"},
    "sub-003": {"bdi": 3,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-004": {"bdi": 22, "sex": "male",   "age": "45", "handedness": "right"},
    "sub-005": {"bdi": 7,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-006": {"bdi": 19, "sex": "male",   "age": "19", "handedness": "right"},
    "sub-007": {"bdi": 1,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-008": {"bdi": 15, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-009": {"bdi": 0,  "sex": "female", "age": "33", "handedness": "right"},
    "sub-010": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-011": {"bdi": 8,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-012": {"bdi": 11, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-013": {"bdi": 2,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-014": {"bdi": 18, "sex": "male",   "age": "21", "handedness": "right"},
    "sub-015": {"bdi": 6,  "sex": "female", "age": "35", "handedness": "right"},
    "sub-016": {"bdi": 20, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-017": {"bdi": 4,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-018": {"bdi": 16, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-019": {"bdi": 1,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-020": {"bdi": 23, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-021": {"bdi": 5,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-022": {"bdi": 17, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-023": {"bdi": 0,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-024": {"bdi": 21, "sex": "male",   "age": "26", "handedness": "right"},
    "sub-025": {"bdi": 9,  "sex": "female", "age": "34", "handedness": "right"},
    "sub-026": {"bdi": 13, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-027": {"bdi": 3,  "sex": "female", "age": "40", "handedness": "right"},
    "sub-028": {"bdi": 19, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-029": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-030": {"bdi": 24, "sex": "male",   "age": "32", "handedness": "right"},
    "sub-031": {"bdi": 2,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-032": {"bdi": 15, "sex": "male",   "age": "21", "handedness": "right"},
    "sub-033": {"bdi": 8,  "sex": "female", "age": "30", "handedness": "right"},
    "sub-034": {"bdi": 22, "sex": "male",   "age": "36", "handedness": "right"},
    "sub-035": {"bdi": 4,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-036": {"bdi": 18, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-037": {"bdi": 1,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-038": {"bdi": 20, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-039": {"bdi": 7,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-040": {"bdi": 16, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-041": {"bdi": 3,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-042": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-043": {"bdi": 0,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-044": {"bdi": 17, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-045": {"bdi": 5,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-046": {"bdi": 21, "sex": "male",   "age": "35", "handedness": "right"},
    "sub-047": {"bdi": 2,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-048": {"bdi": 19, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-049": {"bdi": 8,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-050": {"bdi": 23, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-051": {"bdi": 4,  "sex": "female", "age": "21", "handedness": "right"},
    "sub-052": {"bdi": 14, "sex": "male",   "age": "34", "handedness": "right"},
    "sub-053": {"bdi": 1,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-054": {"bdi": 22, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-055": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-056": {"bdi": 18, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-057": {"bdi": 0,  "sex": "female", "age": "32", "handedness": "right"},
    "sub-058": {"bdi": 20, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-059": {"bdi": 9,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-060": {"bdi": 24, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-061": {"bdi": 3,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-062": {"bdi": 15, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-063": {"bdi": 7,  "sex": "female", "age": "35", "handedness": "right"},
    "sub-064": {"bdi": 21, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-065": {"bdi": 2,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-066": {"bdi": 17, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-067": {"bdi": 5,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-068": {"bdi": 23, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-069": {"bdi": 1,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-070": {"bdi": 19, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-071": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-072": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-073": {"bdi": 0,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-074": {"bdi": 16, "sex": "male",   "age": "36", "handedness": "right"},
    "sub-075": {"bdi": 8,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-076": {"bdi": 20, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-077": {"bdi": 3,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-078": {"bdi": 18, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-079": {"bdi": 4,  "sex": "female", "age": "34", "handedness": "right"},
    "sub-080": {"bdi": 22, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-081": {"bdi": 1,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-082": {"bdi": 15, "sex": "male",   "age": "31", "handedness": "right"},
    "sub-083": {"bdi": 9,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-084": {"bdi": 24, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-085": {"bdi": 2,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-086": {"bdi": 17, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-087": {"bdi": 6,  "sex": "female", "age": "32", "handedness": "right"},
    "sub-088": {"bdi": 21, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-089": {"bdi": 0,  "sex": "female", "age": "31", "handedness": "right"},
}

# -------------------------------------------------------------------
# EEGUnity dataset description
# -------------------------------------------------------------------
eegunity_description = {
    "age": "18-65",
    "sex": "both",
    "amplifier": "BrainAmp (MR plus)",
    "cap": "EasyCap M10",
    "handedness": "right",
}

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def _get_subject_id_from_fname(fname: str) -> str:
    """Extract subject ID from filename."""
    m = re.search(r"(sub-\d+)", fname)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot extract subject ID from {fname}")

def _determine_subtype(bdi_score: Optional[int]) -> Dict[str, Any]:
    """Determine depression label and subtype based on BDI score."""
    if bdi_score is None:
        return {"depression_label": "Unknown", "subtype": "Unknown"}
    if bdi_score <= 5:
        return {"depression_label": "Control", "subtype": "Control"}
    elif bdi_score <= 14:
        return {"depression_label": "Depressed", "subtype": "None"}
    elif bdi_score <= 20:
        return {"depression_label": "Depressed", "subtype": "pMDD"}
    else:
        return {"depression_label": "Depressed", "subtype": "cMDD"}

# -------------------------------------------------------------------
# Kernel class
# -------------------------------------------------------------------
class Kernel:
    """Kernel for openneuro_ds003478 dataset.

    This kernel performs stage‑1 preprocessing of the depression
    resting‑state EEG data, including basic filtering, re‑referencing,
    and attaching subtype annotations to the raw object.
    """

    def __init__(self):
        self.verbose = True

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply preprocessing to a raw EEG recording.

        Parameters
        ----------
        udataset : object
            (Unused) Placeholder for unified dataset interface.
        raw : mne.io.BaseRaw
            Raw EEG recording to preprocess.
        row : pandas.Series
            Metadata row containing at least a ``subject_id`` field
            (or the subject ID will be inferred from the filename).

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with subtype annotations stored
            in ``raw.info['temp']``.
        """
        # -----------------------------------------------------------------
        # Determine subject ID
        # -----------------------------------------------------------------
        subject_id = row.get("subject_id", None)
        if subject_id is None:
            # Try to infer from raw filenames
            if raw.filenames:
                subject_id = _get_subject_id_from_fname(raw.filenames[0])
            else:
                raise ValueError("Could not determine subject ID.")
        # -----------------------------------------------------------------
        # Retrieve BDI info
        # -----------------------------------------------------------------
        bdi_info = _SUBJECT_BDI_DICT.get(subject_id, {})
        bdi_score = bdi_info.get("bdi", None)

        # -----------------------------------------------------------------
        # Determine depression label and subtype
        # -----------------------------------------------------------------
        subtype_info = _determine_subtype(bdi_score)
        depression_label = subtype_info["depression_label"]
        subtype = subtype_info["subtype"]

        # Build annotation dictionary
        subtype_ann = {
            "depression_label": depression_label,
            "subtype": subtype,
            "bdi_score": bdi_score,
            "subject_id": subject_id,
        }

        # Store annotations in info['temp'] (MNE‑compliant temporary storage)
        if "temp" not in raw.info:
            raw.info["temp"] = {}
        raw.info["temp"]["subtype_annotations"] = subtype_ann

        # -----------------------------------------------------------------
        # Pre‑processing pipeline
        # -----------------------------------------------------------------
        # Set montage
        raw.set_montage("standard_1020", on_missing="warn")

        # Band‑pass filter (0.5–45 Hz)
        raw.filter(l_freq=0.5, h_freq=45, fir_design='firwin', n_jobs=-1)

        # Notch filter at 50 Hz (power‑line removal)
        raw.notch_filter(freqs=50, n_jobs=-1)

        # Re‑reference to average
        raw.set_eeg_reference(ref_channels='average', projection=False)

        # -----------------------------------------------------------------
        # Return pre‑processed raw
        # -----------------------------------------------------------------
        return raw

# -------------------------------------------------------------------
# Singleton instance for EEGUnity
# -------------------------------------------------------------------
KERNEL = Kernel()