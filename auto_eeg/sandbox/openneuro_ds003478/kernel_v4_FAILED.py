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
    "sub-089": {"bdi": 0,  "sex": "female", "age": "30", "handedness": "right"},
}

# -------------------------------------------------------------------
# Stage-0: Dataset description (populated by apply)
# -------------------------------------------------------------------
_EEGUNITY_DESCRIPTION: Dict[str, Any] = {}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _safe_filename(raw_or_path) -> str:
    if isinstance(raw_or_path, mne.io.BaseRaw):
        return raw_or_path.filenames[0] if raw_or_path.filenames else "unknown"
    return str(raw_or_path)


def _validate_raw(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Ensure raw is preloaded."""
    if not raw.preload:
        raw = raw.load_data()
        raw.preload = True
    return raw


def _build_description(row: pd.Series) -> Dict[str, Any]:
    subject_id = row.get("subject_id", "unknown")
    meta = _SUBJECT_BDI_DICT.get(subject_id, {})
    return {
        "age": str(meta.get("age", "N/A")),
        "sex": meta.get("sex", "N/A"),
        "handedness": meta.get("handedness", "N/A"),
        "amplifier": "N/A",
        "cap": "N/A",
        "bdi": meta.get("bdi", -1),
        "dataset": "openneuro_ds003478",
        "subject_id": subject_id,
    }


def _extract_runs(task_str: str) -> List[str]:
    """Extract run identifiers from task name."""
    if not isinstance(task_str, str):
        return []
    runs = re.findall(r"run-\d+", task_str)
    return runs


def _detect_eyes(task_str: str) -> str:
    """Detect eyes condition from task descriptor."""
    task_lower = task_str.lower() if isinstance(task_str, str) else ""
    if "eyesopen" in task_lower or "eyeopen" in task_lower or "eopen" in task_lower:
        return "EO"
    elif "eyesclosed" in task_lower or "eyeclosed" in task_lower or "eclosed" in task_lower:
        return "EC"
    return "EC"  # default to eyes closed for resting state


# -------------------------------------------------------------------
# Kernel
# -------------------------------------------------------------------

class openneuro_ds003478_Kernel:
    VERSION = "1.0.0"

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Handle case where raw is already a Raw object
        if isinstance(raw, mne.io.BaseRaw):
            return _validate_raw(raw)

        # Otherwise treat as file path
        if not isinstance(raw, (str, os.PathLike)):
            raise TypeError(f"raw must be a file path or BaseRaw, got {type(raw)}")

        raw_obj = mne.io.read_raw(raw, preload=True, verbose=False)
        return raw_obj

    def describe(self, udataset, row) -> Dict[str, Any]:
        """Populate EEGUnity dataset description metadata."""
        global _EEGUNITY_DESCRIPTION
        desc = _build_description(row)
        subject_id = row.get("subject_id", "unknown")
        task = row.get("task", "unknown")
        run_list = _extract_runs(task)
        eyes_cond = _detect_eyes(task)
        desc.update({
            "eyes_condition": eyes_cond,
            "runs": run_list,
            "task": task,
        })
        _EEGUNITY_DESCRIPTION.update(desc)
        return _EEGUNITY_DESCRIPTION


# -------------------------------------------------------------------
# Module-level kernel instance
# -------------------------------------------------------------------
KERNEL = openneuro_ds003478_Kernel()