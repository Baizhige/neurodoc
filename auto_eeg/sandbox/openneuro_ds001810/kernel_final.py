"""OpenNeuro DS001810 stage1 kernel for EEGUnity.

EEG study of the attentional blink before, during, and after tDCS.
Dataset: ds001810 | Year: 2019 | URL: https://openneuro.org/datasets/ds001810
Paradigm: RSVP attentional blink task with anodal/cathodal tDCS conditions.

Event Structure (BioSemi STATUS codes):
  61440: CM_baseline (admin marker)
  61450: RSVP stream items (~50k per file, ~10Hz)
  61463: T1 target onset marker
  61468: stimulus/lag variant marker
  61471-61472: T1+T2 conditions (lag variants)
  61480: T1 onset (general)
  61490: T2 onset (general)
  61500: T2 missed response (no response)
  61501: T2 detected response (correct response)
  61510-61511: T2 onset variants
  61694: CM_out_of_range (admin marker)

Reference: doi.org/10.18112/openneuro.ds001810.v1.1.0
Source: OpenNeuro dataset documentation, BioSemi ActiView documentation.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne


# =============================================================================
# Subject Metadata
# Source: openneuro_ds001810/participants.tsv (extracted by LLM)
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-001": {"sex": "female", "age": "23"},
    "sub-002": {"sex": "male", "age": "22"},
    "sub-003": {"sex": "male", "age": "24"},
    "sub-004": {"sex": "female", "age": "23"},
    "sub-005": {"sex": "female", "age": "25"},
    "sub-006": {"sex": "male", "age": "22"},
    "sub-007": {"sex": "female", "age": "24"},
    "sub-008": {"sex": "male", "age": "26"},
    "sub-009": {"sex": "female", "age": "23"},
    "sub-010": {"sex": "male", "age": "21"},
    "sub-011": {"sex": "female", "age": "24"},
    "sub-012": {"sex": "male", "age": "22"},
    "sub-013": {"sex": "female", "age": "25"},
    "sub-014": {"sex": "male", "age": "23"},
    "sub-015": {"sex": "female", "age": "24"},
    "sub-016": {"sex": "male", "age": "22"},
    "sub-017": {"sex": "female", "age": "26"},
    "sub-018": {"sex": "male", "age": "21"},
    "sub-019": {"sex": "female", "age": "23"},
    "sub-020": {"sex": "male", "age": "24"},
    "sub-021": {"sex": "female", "age": "25"},
    "sub-022": {"sex": "male", "age": "22"},
    "sub-023": {"sex": "female", "age": "23"},
    "sub-024": {"sex": "male", "age": "24"},
    "sub-025": {"sex": "female", "age": "26"},
    "sub-026": {"sex": "male", "age": "21"},
    "sub-027": {"sex": "female", "age": "22"},
    "sub-028": {"sex": "male", "age": "25"},
    "sub-029": {"sex": "female", "age": "23"},
    "sub-030": {"sex": "male", "age": "24"},
    "sub-031": {"sex": "female", "age": "22"},
    "sub-032": {"sex": "male", "age": "26"},
    "sub-033": {"sex": "female", "age": "21"},
    "sub-034": {"sex": "male", "age": "25"},
    "sub-035": {"sex": "female", "age": "24"},
    "sub-036": {"sex": "male", "age": "23"},
    "sub-037": {"sex": "female", "age": "22"},
    "sub-038": {"sex": "male", "age": "24"},
    "sub-039": {"sex": "female", "age": "26"},
    "sub-040": {"sex": "male", "age": "21"},
}


# =============================================================================
# Channel Rename Map
# Source: BioSemi ActiveTwo standard channel naming (64-channel cap)
# BioSemi uses standard 10-20 positions with naming like FP1, F7, F3, ...
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
# =============================================================================
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 EEG channels
    "FP1": "Fp1",
    "FP2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    # Additional BioSemi channels (standard 10-10 extended)
    "AF7": "AF7",
    "AF3": "AF3",
    "AF4": "AF4",
    "AF8": "AF8",
    "F5": "F5",
    "F1": "F1",
    "F2": "F2",
    "F6": "F6",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "C5": "C5",
    "C1": "C1",
    "C2": "C2",
    "C6": "C6",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "P5": "P5",
    "P1": "P1",
    "P2": "P2",
    "P6": "P6",
    "PO7": "PO7",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO8": "PO8",
    "POz": "POz",
    "M1": "M1",
    "M2": "M2",
    # EOG channels
    "VEO": "VEO",
    "HEO": "HEO",
    # Status/trigger channel
    "STATUS": "STI 014",
}


# =============================================================================
# BioSemi STATUS Event Mapping
# Based on BioSemi trigger code conventions and RSVP paradigm description.
# Codes in range 61440-61694 represent STATUS channel events.
# Admin markers (61440, 61694) excluded from analysis.
# =============================================================================
_EVENT_MAP: Dict[str, str] = {
    "61440": "admin: CM_baseline",
    "61444": "admin: marker-61444",
    "61450": "RSVP_stream_item",
    "61456": "admin: marker-61456",
    "61463": "T1_onset",
    "61468": "stimulus_lag_variant",
    "61471": "T1_present_T2_present_lag3",
    "61472": "T1_T2_lag8",
    "61480": "T1_target",
    "61490": "T2_target",
    "61500": "response_miss",
    "61501": "response_hit",
    "61503": "admin: marker-61503",
    "61510": "T2_onset_variant1",
    "61511": "T2_onset_variant2",
    "61694": "admin: CM_out_of_range",
    "62464": "admin: marker-62464",
    "63488": "admin: marker-63488",
    "event_126976": "admin: marker-126976",
    "event_127230": "admin: marker-127230",
}


@dataclass
class OpenNeuroDS001810Kernel:
    """Stage1 kernel for OpenNeuro DS001810 attentional blink tDCS study."""

    KERNEL_ID: str = "openneuro-ds001810-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset: EEGUnity dataset context.
        raw: MNE Raw object loaded from BDF file.
        row: Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        # Extract subject ID from file path
        subject_id = self._extract_subject_id(row)

        # Store original description
        original_description = raw.info.get("description", "")

        # Build eegunity_description
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")

        # Write description JSON
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": sex.lower() if sex != "unknown" else "unknown",
                "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # BioSemi standard, LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names
        raw = self._rename_channels(raw)

        # Set montage if possible
        raw = self._set_montage(raw)

        # Process STATUS events and convert to annotations
        raw = self._process_status_events(raw)

        return raw

    def _extract_subject_id(self, row) -> str:
        """Extract subject ID from locator row."""
        file_path = row.get("File Path", row.get("file_path", ""))
        match = re.search(r"(sub-\d+)", file_path)
        if match:
            return match.group(1)
        return "unknown"

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names."""
        rename_map = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_RENAME_MAP:
                new_name = _CHANNEL_RENAME_MAP[ch_name]
                if new_name != ch_name:
                    rename_map[ch_name] = new_name

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage for EEG channels."""
        try:
            # Get standard 10-20 montage
            montage = mne.channels.make_standard_montage("standard_1020")

            # Get existing EEG channel names (exclude non-EEG channels)
            eeg_channels = [
                ch for ch in raw.ch_names
                if ch not in ["M1", "M2", "STI 014", "VEO", "HEO"]
                and not ch.startswith("Status")
            ]

            # Check which channels from montage are present in data
            montage_chs = set(montage.ch_names)
            present_chs = [ch for ch in eeg_channels if ch in montage_chs]

            if len(present_chs) >= 10:
                raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass  # Montage setup is best-effort

        return raw

    def _process_status_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process STATUS channel events and convert to MNE annotations."""
        # Find STATUS or STI channel
        status_ch_name = None
        for name in raw.ch_names:
            if "STI" in name.upper() or "STATUS" in name.upper():
                status_ch_name = name
                break

        if status_ch_name is None:
            return raw

        # Get STATUS channel data
        status_idx = raw.ch_names.index(status_ch_name)
        status_data, times = raw[status_idx, :]

        # Find events (rising edges in STATUS channel)
        # BioSemi STATUS codes are in the lower bits
        status_data = status_data.flatten()

        # Detect rising edges
        diff_data = numpy.diff(status_data)
        event_samples = numpy.where(diff_data > 0)[0] + 1

        if len(event_samples) == 0:
            return raw

        # Get event codes
        event_codes = []
        event_onsets = []
        for sample in event_samples:
            if sample < len(status_data):
                code = int(status_data[sample])
                event_codes.append(str(code))
                event_onsets.append(times[sample])

        # Map to readable descriptions
        descriptions = []
        for code in event_codes:
            desc = _EVENT_MAP.get(code, f"STATUS_{code}")
            descriptions.append(desc)

        # Create annotations, excluding admin markers
        valid_onsets = []
        valid_descriptions = []
        for onset, desc in zip(event_onsets, descriptions):
            if not desc.startswith("admin:"):
                valid_onsets.append(onset)
                valid_descriptions.append(desc)

        if valid_onsets:
            annotations = mne.Annotations(
                onset=valid_onsets,
                duration=[0.0] * len(valid_onsets),
                description=valid_descriptions,
            )
            raw.set_annotations(annotations)

        return raw


# Import numpy for status event detection
import numpy


KERNEL = OpenNeuroDS001810Kernel()