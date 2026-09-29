"""Dataset-specific kernel for openneuro ds003522.

Three-Stimulus Auditory Oddball and Rest in Acute and Chronic TBI.
64-channel EEG + 1 trigger channel, 500 Hz sampling.

Source: https://openneuro.org/datasets/ds003522
DOI: 10.1016/j.neuropsychologia.2019.107125
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: Dataset does not include participants.tsv with demographic info.
# All values inferred from general study description (mTBI patients, healthy controls).
# Age range from paper: 18-65 years (majority in 20s-40s).
# inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Subject IDs are sub-001 through sub-062
    # Specific demographic data not available in BIDS sidecar
}


# =============================================================================
# Channel Configuration
# =============================================================================
# Source: BrainVision format with 64-channel setup.
# Standard 64-channel layout with Cz as reference.
# inferred by LLM, needs human review
_EEG_CHANNEL_RENAMES: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fpz": "Fpz",
    "Fz": "Fz",
    "F3": "F3",
    "F4": "F4",
    "F7": "F7",
    "F8": "F8",
    "FC5": "FC5",
    "FC6": "FC6",
    "FC1": "FC1",
    "FC2": "FC2",
    "FCz": "FCz",
    "Cz": "Cz",
    "C3": "C3",
    "C4": "C4",
    "T7": "T7",
    "T8": "T8",
    "CP5": "CP5",
    "CP6": "CP6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CPz": "CPz",
    "P7": "P7",
    "P8": "P8",
    "P3": "P3",
    "P4": "P4",
    "Pz": "Pz",
    "PO7": "PO7",
    "PO8": "PO8",
    "POz": "POz",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    # Extended 64-channel names
    "AF7": "AF7",
    "AF8": "AF8",
    "AF3": "AF3",
    "AF4": "AF4",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FT7": "FT7",
    "FT8": "FT8",
    "FC3": "FC3",
    "FC4": "FC4",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "TP7": "TP7",
    "TP8": "TP8",
    "CP3": "CP3",
    "CP4": "CP4",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO3": "PO3",
    "PO4": "PO4",
    "O9": "O9",
    "O10": "O10",
}


# =============================================================================
# Event Mapping (numeric to human-readable)
# =============================================================================
# Source: events.tsv in BIDS structure shows human-readable event descriptions.
# Numeric trigger codes from STATUS channel:
# S  1 = Standard Tone (~80% probability)
# S  2 = Novel Tone (rare distractor, P3a)
# S  3 = Target Tone (rare target, P3b)
# S200 = Eyes Open resting block marker
# S201 = Rest/baseline block marker
# S202 = Eyes Closed resting block marker
# STATUS / R12 = system status / response events
_EVENT_MAP: Dict[str, str] = {
    "S  1": "Standard Tone",
    "S  2": "Novel Tone",
    "S  3": "Target Tone",
    "S200": "Eyes Open",
    "S201": "Eyes Closed",
    "S202": "Eyes Open",
    "STATUS": "admin: STATUS",
    "R 12": "admin: response",
}


# =============================================================================
# Kernel Class
# =============================================================================
class OpenNeuroDS003522Kernel:
    """Stage1 kernel for openneuro_ds003522 (Three-Stimulus Auditory Oddball TBI Study)."""

    KERNEL_ID: str = "openneuro-ds003522-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded from BIDS
        row : Locator row with file path information

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with standardized events and metadata
        """
        # -------------------------------------------------------------------------
        # 1. Extract subject ID and load subject metadata
        # -------------------------------------------------------------------------
        file_path = row.get("File Path", "")
        subject_id = self._extract_subject_id(file_path)
        subject_info = _SUBJECT_DICT.get(subject_id, {})

        # -------------------------------------------------------------------------
        # 2. Channel renaming (before set_montage)
        # -------------------------------------------------------------------------
        raw = self._rename_channels(raw)

        # -------------------------------------------------------------------------
        # 3. Set standard 10-20 montage
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setup is optional if channels don't match

        # -------------------------------------------------------------------------
        # 4. Process annotations/events
        # -------------------------------------------------------------------------
        raw = self._process_events(raw)

        # -------------------------------------------------------------------------
        # 5. Write eegunity_description
        # -------------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)

        # Infer subject info from study context if not in subject dict
        # inferred by LLM, needs human review
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        # Amplifier info from BrainVision system
        # inferred by LLM, needs human review
        amplifier = "BrainVision"
        cap = "Ag/AgCl"  # Standard for EEG studies

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex).lower() if sex != "unknown" else "unknown",
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _extract_subject_id(self, file_path: str) -> str:
        """Extract subject ID from file path."""
        match = re.search(r"sub-(\d+)", file_path)
        if match:
            return f"sub-{match.group(1)}"
        return "unknown"

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names if needed."""
        ch_names = raw.ch_names
        rename_map = {}

        for ch_name in ch_names:
            # Skip trigger/status channels
            if ch_name.upper() in ["STATUS", "TRIGGER", "R 12", "R12"]:
                continue

            # Check for standard 10-20 names already
            if ch_name in _EEG_CHANNEL_RENAMES.values():
                continue

            # Try to match via rename dict
            if ch_name in _EEG_CHANNEL_RENAMES:
                rename_map[ch_name] = _EEG_CHANNEL_RENAMES[ch_name]
            else:
                # Try with spaces normalized (BrainVision format: "Fp 1" -> "Fp1")
                normalized = ch_name.replace(" ", "")
                if normalized in _EEG_CHANNEL_RENAMES:
                    rename_map[ch_name] = _EEG_CHANNEL_RENAMES[normalized]
                elif ch_name.startswith("EEG-"):
                    # Handle EEG-001 style naming
                    continue  # Keep as-is if can't map

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _process_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process and standardize event annotations."""
        # Get existing annotations
        orig_annotations = raw.annotations

        if len(orig_annotations) > 0:
            # Map existing annotations to standardized names
            new_descriptions = []
            for desc in orig_annotations.description:
                # Try exact match first
                mapped = _EVENT_MAP.get(desc)
                if mapped:
                    new_descriptions.append(mapped)
                else:
                    # Try stripped version (remove extra spaces)
                    stripped = re.sub(r"\s+", " ", desc.strip())
                    mapped = _EVENT_MAP.get(stripped)
                    if mapped:
                        new_descriptions.append(mapped)
                    else:
                        # Keep original if no mapping found
                        new_descriptions.append(desc)

            # Create new annotations with mapped descriptions
            new_annotations = mne.Annotations(
                onset=orig_annotations.onset,
                duration=orig_annotations.duration,
                description=new_descriptions,
                orig_time=orig_annotations.orig_time,
            )
            raw.set_annotations(new_annotations)
        else:
            # No annotations - extract events from STATUS channel if present
            raw = self._extract_status_events(raw)

        return raw

    def _extract_status_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Extract events from STATUS channel if no annotations exist."""
        ch_names = raw.ch_names

        # Look for status/trigger channel
        status_ch = None
        for ch in ch_names:
            if ch.upper() in ["STATUS", "TRIGGER", "STIM", "MISC"]:
                status_ch = ch
                break

        if status_ch is None:
            return raw

        # Find event channel index
        status_idx = ch_names.index(status_ch)

        # Get data and find events (changes in trigger channel)
        data, times = raw[status_idx, :]
        trigger_data = data[0]

        # Find sample points where trigger changes
        diff = np.diff(trigger_data)
        event_indices = np.where(diff != 0)[0] + 1  # +1 because diff shifts by 1

        if len(event_indices) == 0:
            return raw

        # Get event codes
        event_codes = trigger_data[event_indices]

        # Create onset times
        sfreq = raw.info["sfreq"]
        onsets = event_indices / sfreq

        # Map event codes to descriptions
        descriptions = []
        for code in event_codes:
            code_str = str(int(code)).strip()
            # Try to match in event map
            mapped = None
            for key, val in _EVENT_MAP.items():
                if key.replace(" ", "") == code_str or key == f"S{code_str}":
                    mapped = val
                    break
            if mapped:
                descriptions.append(mapped)
            else:
                descriptions.append(f"event-{int(code)}")

        # Create annotations
        annotations = mne.Annotations(
            onset=onsets,
            duration=np.zeros(len(onsets)),
            description=descriptions,
        )
        raw.set_annotations(annotations)

        return raw


# Module-level kernel instance
KERNEL = OpenNeuroDS003522Kernel()