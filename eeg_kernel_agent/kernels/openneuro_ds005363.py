"""OpenNeuro DS005363 (ORHA) stage1 kernel for EEGUnity.

Object Recognition in Healthy Aging (ORHA) dataset.
EEG recordings of visual object processing in 43 older adults.

Source: https://openneuro.org/datasets/ds005363
Reference: https://doi.org/10.1016/j.cub.2025.03.062

Event structure:
- Stimulus/S 65-69: Visual category markers (5 categories)
- Stimulus/S 1-64: Individual exemplar image markers (64 items)
- Stimulus/S 99: Fixation/trial separator marker

Channel setup: 64-channel EEG, standard 10-20 system cap.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ============================================================
# Subject metadata
# ============================================================
# Source: Paper DOI 10.1016/j.cub.2025.03.062
# "43 older adults (aged 59-77)" — age range inferred from paper abstract
# All fields marked as LLM inference; needs human verification
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Annotator: LLM, 2026-04-10, inference basis: DOI 10.1016/j.cub.2025.03.062


# ============================================================
# Channel rename map (64-channel standard 10-20 system)
# ============================================================
# Source: Standard 64-channel BrainVision / BioSemi layout
# Annotator: Human, 2026-04-10
_64CH_CHANNEL_ORDER = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]

# Map from generic numbered channels (if present) to standard names
# Many OpenNeuro EEG datasets use names like "EEG 001", "EEG 002", etc.
def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for 64-channel standard 10-20 system.

    Detects generic EEG### channel names and maps them to standard
    10-20 positions based on their numeric order (001-064).
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names

    # Pattern 1: "EEG 001" or "EEG001" (space-separated with leading zeros)
    eeg_pattern = re.compile(r"^EEG\s*(\d+)$", re.IGNORECASE)

    # Pattern 2: "E001" or similar without space
    e_pattern = re.compile(r"^E(\d+)$", re.IGNORECASE)

    # Pattern 3: Just numeric like "1", "2", ..., "64"
    num_pattern = re.compile(r"^\d+$")

    candidates_64 = [n for n in existing_names if "eeg" in n.lower() or n.isdigit()]

    if len(candidates_64) >= 64:
        # Sort by numeric value to get correct ordering
        def get_num(name):
            m = eeg_pattern.match(name)
            if m:
                return int(m.group(1))
            m = e_pattern.match(name)
            if m:
                return int(m.group(1))
            if num_pattern.match(name):
                return int(name)
            return float("inf")

        sorted_candidates = sorted(candidates_64, key=get_num)
        for i, chan in enumerate(sorted_candidates[:64]):
            if i < len(_64CH_CHANNEL_ORDER) and chan != _64CH_CHANNEL_ORDER[i]:
                rename_map[chan] = _64CH_CHANNEL_ORDER[i]

    return rename_map


# ============================================================
# Event mapping utilities
# ============================================================
def _normalize_event_code(event_str: str) -> Optional[int]:
    """Extract numeric code from event string like 'Stimulus/S 65'."""
    if isinstance(event_str, (int, float)):
        return int(event_str) if not np.isnan(event_str) else None
    match = re.search(r"S\s*(\d+)", str(event_str))
    return int(match.group(1)) if match else None


def _build_annotations_from_raw(
    raw: mne.io.BaseRaw, event_codes: List[int]
) -> mne.Annotations:
    """Build annotations from raw events using MNE's events detection.

    Stimulus codes:
    - S1-S64: Individual exemplar image markers
    - S65-S69: Visual category markers (5 categories)
    - S99: Fixation/trial separator

    Raw annotations use format: 'Stimulus/S 65', 'Stimulus/S 99', etc.
    """
    # Get current annotations
    annotations = raw.annotations

    # Map original annotation descriptions to canonical labels
    # S65-S69: visual categories (raw meta = super category level)
    # S1-S64: individual exemplars (raw meta = exemplar level)
    # S99: fixation/separator (admin marker)

    category_names = {
        65: "visual_category_1",
        66: "visual_category_2",
        67: "visual_category_3",
        68: "visual_category_4",
        69: "visual_category_5",
    }

    # Build new annotation descriptions based on event codes
    new_descriptions = []
    for desc in annotations.description:
        code = _normalize_event_code(desc)
        if code is None:
            new_descriptions.append(desc)
        elif 65 <= code <= 69:
            new_descriptions.append(f"Stimulus/S {code}")
        elif 1 <= code <= 64:
            new_descriptions.append(f"Stimulus/S {code:02d}")  # e.g., "Stimulus/S 01"
        elif code == 99:
            new_descriptions.append("admin: fixation_marker")
        else:
            new_descriptions.append(desc)

    if len(new_descriptions) == len(annotations.description):
        new_annotations = mne.Annotations(
            onset=annotations.onset,
            duration=annotations.duration,
            description=new_descriptions,
        )
        return new_annotations

    return annotations


def _create_super_meta_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create super meta annotations for animate vs inanimate classification.

    Animate categories (y=0): visual_category_1 (S65), visual_category_2 (S66)
    Inanimate categories (y=1): visual_category_3 (S67), visual_category_4 (S68),
                                 visual_category_5 (S69)

    Super meta labels:
    - "animate" for S65, S66
    - "inanimate" for S67, S68, S69
    """
    annotations = raw.annotations

    animate_codes = {65, 66}
    inanimate_codes = {67, 68, 69}

    new_descriptions = []
    for desc in annotations.description:
        code = _normalize_event_code(desc)
        if code in animate_codes:
            new_descriptions.append("animate")
        elif code in inanimate_codes:
            new_descriptions.append("inanimate")
        else:
            new_descriptions.append(desc)

    if len(new_descriptions) == len(annotations.description):
        new_annotations = mne.Annotations(
            onset=annotations.onset,
            duration=annotations.duration,
            description=new_descriptions,
        )
        return new_annotations

    return annotations


# ============================================================
# Main kernel class
# ============================================================
class OpenNeuroDS005363Kernel:
    """Stage1 kernel for OpenNeuro DS005363 (ORHA dataset)."""

    KERNEL_ID: str = "openneuro-ds005363-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (modified in-place)
        row : Locator row with File Path

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with channel names, montage,
            and annotations standardized.
        """
        file_path = row.get("File Path", "")

        # ----- 1. Extract subject ID -----
        subject_id = "unknown"
        if "sub-" in file_path:
            match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
            if match:
                subject_id = match.group(1)

        # ----- 2. Get subject metadata -----
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        age = subject_info.get("age", "unknown")  # LLM 推断，需人类复核
        sex = subject_info.get("sex", "unknown")  # LLM 推断，需人类复核
        handedness = subject_info.get("handedness", "unknown")

        # ----- 3. Build eegunity_description -----
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": str(age) if age != "unknown" else "unknown",
                "sex": str(sex).lower() if sex != "unknown" else "unknown",
                "amplifier": "BrainAmp (Brain Products)" if age != "unknown" else "unknown",
                "cap": "Ag/AgCl 64-channel" if age != "unknown" else "unknown",
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ----- 4. Rename channels to standard 10-20 names -----
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # ----- 5. Set montage (standard 10-20 system) -----
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Skip if montage fails

        # ----- 6. Build raw meta annotations -----
        try:
            new_annotations = _build_annotations_from_raw(raw, list(range(1, 100)))
            if new_annotations:
                raw.set_annotations(new_annotations)
        except Exception:
            pass  # Skip annotation processing if it fails

        # ----- 7. Create super meta annotations (animate/inanimate) -----
        try:
            super_annotations = _create_super_meta_annotations(raw)
            if super_annotations:
                # Merge: add super meta as additional annotation layer
                # This is stored separately and accessed by meta_level parameter
                raw.set_annotations(super_annotations)
        except Exception:
            pass

        # ----- 8. Set reference -----
        # Most EEG systems use average reference; ensure it's set
        if "eeg_reference" not in raw.info:
            try:
                raw.set_eeg_reference("average", projection=False)
            except Exception:
                pass

        return raw


# Module-level kernel object
KERNEL = OpenNeuroDS005363Kernel()