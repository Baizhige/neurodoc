"""THINGS-EEG (openneuro_ds003825) stage1 kernel for EEGUnity.

Dataset: Human electroencephalography recordings from 50 subjects for 22,248 images
from 1,854 object concepts. RSVP paradigm at 10 Hz.

Source: https://openneuro.org/datasets/ds003825
DOI: 10.1038/s41597-021-01102-7

Note: Subject metadata (age, sex, handedness) and device info (amplifier, cap)
are not available in the dataset. All fields set to "unknown".
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Event mapping: raw numeric codes to human-readable labels
# Source: analysis.md - Event Structure table
_EVENT_MAP: Dict[int, str] = {
    1: "E 1",   # RSVP image onset (primary stimulus stream)
    2: "E 2",   # Secondary condition marker
    3: "E 3",   # Block/sequence boundary or target event
}


class THINGSEEGKernel:
    """Stage1 kernel for the THINGS-EEG dataset (openneuro_ds003825)."""

    KERNEL_ID: str = "openneuro-ds003825-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single THINGS-EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with annotations and metadata.
        """
        file_path = row.get("File Path", "")

        # --- Channel renaming (before set_montage) ---
        raw = self._rename_channels(raw)

        # --- Set montage ---
        raw = self._set_montage(raw)

        # --- Remap events to annotations ---
        raw = self._remap_events_to_annotations(raw)

        # --- Write eegunity_description ---
        raw = self._write_description(raw)

        return raw

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 1020 names if needed.

        The dataset uses EEGLAB preprocessing which may have non-standard
        channel names. This attempts to rename common patterns to standard
        10-20 system names.

        Source: Standard 10-20 system electrode naming convention.
        Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
        """
        ch_names = raw.ch_names
        n_channels = len(ch_names)

        # Common EEGLAB channel naming patterns to standard names
        # 64-channel setup is typical for this dataset
        rename_map: Dict[str, str] = {}

        # Standard 64-channel layout names (international 10-20 system extended)
        standard_64 = [
            "Fp1", "Fpz", "Fp2",
            "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
            "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
            "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
            "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
            "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
            "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
            "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
            "O1", "Oz", "O2",
            "I1", "Iz", "I2",
        ]

        # Try to match and rename based on common patterns
        for i, ch in enumerate(ch_names):
            # Skip if already a standard name
            if ch in standard_64:
                continue

            # Pattern: EEG-XX or EEG-XXpz etc.
            match = re.match(r"EEG[-_]?(\d+)", ch, re.IGNORECASE)
            if match and i < len(standard_64):
                rename_map[ch] = standard_64[i]

            # Pattern: E followed by number (EEGLAB convention)
            match = re.match(r"E(\d+)", ch, re.IGNORECASE)
            if match and ch not in rename_map and i < len(standard_64):
                rename_map[ch] = standard_64[i]

        if rename_map:
            # Only rename channels that exist
            valid_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if valid_renames:
                raw.rename_channels(valid_renames)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set electrode montage for standardized spatial positions.

        Attempts to set standard 1020 montage. Falls back gracefully if
        channel names don't match the standard montage.

        Source: mne.channels.standard_montage
        Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
        """
        try:
            # Try standard 1020 montage first
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If standard_1020 fails, try a less strict approach
            try:
                # Try to set whatever channels match
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # Skip montage if channels are too non-standard
                pass

        return raw

    def _remap_events_to_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Convert events to MNE annotations with standardized labels.

        Reads events from the raw object and creates annotations using
        the standardized event mapping.

        Source: analysis.md - Event Structure table
        Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
        """
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            # No events found or cannot parse
            return raw

        # Build new annotation descriptions
        onset_times = events[:, 0] / raw.info["sfreq"]
        durations = [0.0] * len(events)
        descriptions = []

        # Get the original annotation map
        orig_desc_map = event_id

        for event in events:
            orig_id = event[2]
            # Find the original description for this ID
            orig_desc = None
            for desc, code in orig_desc_map.items():
                if code == orig_id:
                    orig_desc = desc
                    break

            if orig_desc is not None:
                # Check if it's a numeric code we can map
                try:
                    code = int(orig_desc)
                    if code in _EVENT_MAP:
                        descriptions.append(_EVENT_MAP[code])
                    else:
                        descriptions.append(f"E {code}")
                except (ValueError, TypeError):
                    # Keep original description if not a simple number
                    descriptions.append(str(orig_desc))
            else:
                descriptions.append(str(orig_id))

        # Create and set annotations
        annotations = mne.Annotations(
            onset=onset_times,
            duration=durations,
            description=descriptions,
        )
        raw.set_annotations(annotations)

        return raw

    def _write_description(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Write standardized eegunity_description to raw.info.

        Subject metadata (age, sex, handedness) and device info
        (amplifier, cap) are not available in this dataset.

        Source: Dataset documentation (missing fields noted)
        Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
        """
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",       # Not available in dataset
                "sex": "unknown",       # Not available in dataset
                "amplifier": "unknown", # Not specified in dataset
                "cap": "unknown",       # Not specified in dataset
                "handedness": "unknown", # Not available in dataset
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = THINGSEEGKernel()