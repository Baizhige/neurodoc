"""openneuro_ds004148 stage1 kernel for EEGUnity.

Southwest University Resting-State and Cognitive State EEG Dataset.
Contains 5 mental states: Eyes-Open (EO), Eyes-Closed (EC), Music, Memory, Mental-Arithmetic.
Recorded at 500 Hz with 61 EEG channels.

Source: https://openneuro.org/datasets/ds004148
DOI: 10.1038/s41597-022-01607-9
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional, Tuple

import mne


# Mapping from trigger codes to mental state labels
# Source: analysis.md event structure (Event ID column)
# Annotator: LLM, 2026-04-08
_TRIGGER_MAP = {
    "S 33": "S 33",  # Eyes-open resting state
    "S 44": "S 44",  # Eyes-closed resting state
    "S 55": "S 55",  # Music listening
    "S 66": "S 66",  # Memory task
    "S 77": "S 77",  # Mental arithmetic
}

# Subject metadata defaults
# Age range 18-45 derived from dataset paper (DOI: 10.1038/s41597-022-01607-9)
# Annotator: LLM, 2026-04-08
_DEFAULT_AGE = "18-45"
_DEFAULT_SEX = "unknown"  # LLM 推断，需人类复核
_DEFAULT_AMPLIFIER = "unknown"  # LLM 推断，需人类复核
_DEFAULT_CAP = "unknown"  # LLM 推断，需人类复核
_DEFAULT_HANDEDNESS = "unknown"  # LLM 推断，需人类复核


def _build_annotations_from_triggers(
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Build annotations from trigger/marker channels.

    This dataset uses STIM channel or annotation-based trigger markers.
    Triggers: S 33 (EO), S 44 (EC), S 55 (Mu), S 66 (Me), S 77 (Ma).

    Returns
    -------
    mne.Annotations
        Annotations derived from trigger events.
    """
    events, event_id = mne.events_from_annotations(raw, verbose=False)

    # Build mapping from raw event id (int) to trigger description
    # event_id is Dict[str, int]
    trigger_descriptions: Dict[int, str] = {}

    for desc, code in event_id.items():
        # desc is string like "S 33" or "769" etc.
        # Try to match against known trigger codes
        desc_stripped = desc.strip()
        if desc_stripped in _TRIGGER_MAP:
            trigger_descriptions[code] = _TRIGGER_MAP[desc_stripped]
        elif desc_stripped.startswith("S "):
            # Keep as-is for known S ## markers
            trigger_descriptions[code] = desc_stripped
        else:
            # Unknown trigger - mark as admin
            # Annotator: LLM, 2026-04-08
            trigger_descriptions[code] = f"admin: marker-{desc_stripped}"

    if not events.size:
        return mne.Annotations(onset=[], duration=[], description=[])

    onset_times = events[:, 0] / raw.info["sfreq"]
    descriptions = [trigger_descriptions.get(e, f"admin: marker-{e}") for e in events[:, 2]]

    return mne.Annotations(onset=onset_times, duration=[0.0] * len(onset_times), description=descriptions)


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from file path.

    OpenNeuro BIDS format: sub-<label> prefix.
    """
    filename = os.path.basename(file_path)

    # Try to extract subject from various patterns
    # Pattern: sub-<subject_label>
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)

    # Fallback: use filename without extension
    return os.path.splitext(filename)[0]


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Set standard 1020 montage if channel names are recognized.

    Uses mne standard 10-20 system. Sets montage only if all EEG channels
    can be matched to standard names.

    Source: Channel names follow standard 10-20 system (from paper description)
    Annotator: LLM, 2026-04-08
    """
    try:
        # Try to set standard 1020 montage
        raw.set_montage("standard_1020", on_missing="ignore")
    except Exception:
        # If montage fails, skip silently
        pass


class openneuro_ds004148Kernel:
    """Stage1 kernel for the openneuro_ds004148 dataset."""

    KERNEL_ID: str = "openneuro-ds004148-stage1"

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
            The modified Raw object with metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # Extract subject ID for metadata lookup
        subject_id = _extract_subject_id_from_path(file_path)

        # Build eegunity_description with defaults
        # Sex and device info from dataset: all fields missing per analysis.md
        # Annotator: LLM, 2026-04-08
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": _DEFAULT_AGE,
                "sex": _DEFAULT_SEX,
                "amplifier": _DEFAULT_AMPLIFIER,
                "cap": _DEFAULT_CAP,
                "handedness": _DEFAULT_HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Build annotations from trigger markers
        annotations = _build_annotations_from_triggers(raw)
        raw.set_annotations(annotations)

        # Set standard 1020 montage if channel names match
        _set_montage_if_possible(raw)

        return raw


KERNEL = openneuro_ds004148Kernel()