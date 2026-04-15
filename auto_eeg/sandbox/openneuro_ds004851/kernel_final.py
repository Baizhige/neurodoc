"""HID (High-Density EEG Operational Dataset) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004851
65 subjects | 72 channels | 2048 Hz | High-density EEG operational paradigm

Event Structure:
  - 1xxx: Primary stimulus classes (10xx: onset markers, 11xx: response markers)
  - 7xxx: Operational block markers
  - 8xxx: Secondary stimulus categories

Source: https://openneuro.org/datasets/ds004851
Reference DOI: 10.18112/openneuro.ds004851.v2.1.0

Kernel Notes:
  - 72-channel HD-EEG follows standard_1020 layout
  - Even/odd paired events (e.g., 1010/1011) indicate onset/response semantics
  - Multi-class structure supports fine-grained stimulus discrimination analysis
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False

# ============================================================================
# Subject Metadata
# ============================================================================
# Source: OpenNeuro ds004851 participants.tsv
# LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(3)}": {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
    for i in range(1, 66)
}

# ============================================================================
# Channel Configuration
# ============================================================================
# Source: 72-channel HD-EEG standard_1020 layout (inferred from dataset description)
# LLM 推断，需人类复核
_STANDARD_72_CHANNELS = [
    "FP1", "FPZ", "FP2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POZ", "PO4", "PO6", "PO8",
    "O1", "OZ", "O2",
    "F9", "F10",
    "T9", "T10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "O9", "O10",
    "CB1", "CB2"
]

# ============================================================================
# Event Mapping
# ============================================================================
# Raw event codes from dataset analysis
# Mapping to human-readable labels based on analysis.md event structure
_EVENT_MAP: Dict[str, str] = {
    # Primary stimulus class A (even: onset, odd: response)
    "1010": "HID: stimulus_A_onset",
    "1011": "HID: stimulus_A_response",
    # Primary stimulus class B
    "1020": "HID: stimulus_B_onset",
    "1021": "HID: stimulus_B_response",
    # Primary stimulus class C
    "1030": "HID: stimulus_C_onset",
    "1031": "HID: stimulus_C_response",
    # Primary stimulus class D
    "1040": "HID: stimulus_D_onset",
    "1041": "HID: stimulus_D_response",
    # Primary stimulus class E
    "1050": "HID: stimulus_E_onset",
    "1051": "HID: stimulus_E_response",
    # Primary stimulus class F
    "1060": "HID: stimulus_F_onset",
    "1061": "HID: stimulus_F_response",
    # Secondary stimulus 81
    "8100": "HID: secondary_81_onset",
    "8101": "HID: secondary_81_response",
    # Secondary stimulus 80 subtypes
    "8010": "HID: secondary_80A_onset",
    "8011": "HID: secondary_80A_response",
    "8020": "HID: secondary_80B_onset",
    "8021": "HID: secondary_80B_response",
    # Operational block markers
    "7001": "HID: block_marker_01",
    "7002": "HID: block_marker_02",
    "7003": "HID: block_marker_03",
    "7004": "HID: block_marker_04",
    "7005": "HID: block_marker_05",
    "7006": "HID: block_marker_06",
    "7007": "HID: block_marker_07",
    "7008": "HID: block_marker_08",
    "7009": "HID: block_marker_09",
    "7010": "HID: block_marker_10",
    "7011": "HID: block_marker_11",
    "7012": "HID: block_marker_12",
    "7013": "HID: block_marker_13",
    "7014": "HID: block_marker_14",
    "7015": "HID: block_marker_15",
    "7016": "HID: block_marker_16",
    "7017": "HID: block_marker_17",
    "7018": "HID: block_marker_18",
    "7019": "HID: block_marker_19",
    "8000": "HID: secondary_80_onset",
    "8001": "HID: secondary_80_response",
}

# ============================================================================
# Kernel Implementation
# ============================================================================

class HIDKernel:
    """Stage1 kernel for OpenNeuro ds004851 (High-Density EEG Operational Dataset)."""

    KERNEL_ID: str = "openneuro-ds004851"
    HANDLES_UNAVAILABLE: bool = False

    def __init__(self):
        """Initialize the HID kernel."""
        self._event_map = _EVENT_MAP

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HID recording.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : dict-like
            Locator row with at least 'File Path' and 'Subject ID'.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with metadata and annotations.
        """
        # Extract subject information
        subject_id = str(row.get("Subject ID", "unknown"))
        subject_key = subject_id if subject_id.startswith("sub-") else f"sub-{subject_id}"
        subject_info = _SUBJECT_DICT.get(subject_key, {})

        # Build eegunity_description
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Handle channel names and montage for 72-channel HD-EEG
        self._process_channels(raw)

        # Process events from annotations or stim channels
        self._process_events(raw)

        return raw

    def _process_channels(self, raw: mne.io.BaseRaw) -> None:
        """Process channel names and set montage for HD-EEG."""
        ch_names = raw.ch_names

        # Check if channels need renaming for standard_1020 compatibility
        rename_map = self._build_channel_rename_map(ch_names)

        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip renaming if it fails

        # Try to set standard 1020 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            existing_chs = set(raw.ch_names) & set(montage.ch_names)
            if len(existing_chs) >= 64:  # At least 64 channels match
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if it fails

    def _build_channel_rename_map(self, ch_names: list) -> Dict[str, str]:
        """Build a channel rename map for standard_1020 naming."""
        rename_map: Dict[str, str] = {}

        # Common non-standard naming patterns in EEG data
        alias_groups = [
            # FP electrodes
            ("Fp1", ["FP1", "fp1", "fpz", "Fpz", "fpz"]),
            ("Fp2", ["FP2", "fp2"]),
            ("Fpz", ["Fpz", "fpz"]),
            # F electrodes
            ("F7", ["F7", "f7"]),
            ("F3", ["F3", "f3"]),
            ("Fz", ["Fz", "fz"]),
            ("F4", ["F4", "f4"]),
            ("F8", ["F8", "f8"]),
            # T electrodes
            ("T7", ["T7", "t7", "T3", "t3"]),
            ("T8", ["T8", "t8", "T4", "t4"]),
            # C electrodes
            ("C3", ["C3", "c3"]),
            ("Cz", ["Cz", "cz"]),
            ("C4", ["C4", "c4"]),
            # P electrodes
            ("P7", ["P7", "p7", "P3", "p3"]),
            ("P3", ["P3", "p3"]),
            ("Pz", ["Pz", "pz"]),
            ("P4", ["P4", "p4"]),
            ("P8", ["P8", "p8"]),
            # O electrodes
            ("O1", ["O1", "o1"]),
            ("Oz", ["Oz", "oz"]),
            ("O2", ["O2", "o2"]),
        ]

        existing_names = set(ch_names)
        for target_name, aliases in alias_groups:
            for source_name in aliases:
                if source_name in existing_names and source_name != target_name:
                    rename_map[source_name] = target_name
                    break

        return rename_map

    def _process_events(self, raw: mne.io.BaseRaw) -> None:
        """Process events from raw annotations and create standardized labels."""
        # Get existing annotations
        annotations = raw.annotations

        if len(annotations) == 0:
            # No annotations - check for stim channels
            stim_channels = [ch for ch in raw.ch_names if ch.upper().startswith("STIM") or ch.upper() == "TRIGGER"]
            if stim_channels:
                # Extract events from stim channel data
                self._extract_stim_events(raw)
        else:
            # Remap existing annotations to standardized labels
            self._remap_annotations(raw)

    def _extract_stim_events(self, raw: mne.io.BaseRaw) -> None:
        """Extract events from stim/trigger channels."""
        sfreq = raw.info["sfreq"]
        stim_data = None

        # Try to find stim channel
        for ch_name in raw.ch_names:
            if "STIM" in ch_name.upper() or "TRIGGER" in ch_name.upper():
                stim_idx = raw.ch_names.index(ch_name)
                stim_data, _ = raw[stim_idx]
                break

        if stim_data is None:
            return

        # Find event onsets (non-zero transitions)
        stim_data = stim_data.flatten()
        threshold = 0.5 * np.max(stim_data) if np.max(stim_data) > 0 else 100

        # Detect rising edges
        above = stim_data > threshold
        transitions = np.diff(above.astype(int))
        onset_indices = np.where(transitions > 0)[0]

        if len(onset_indices) == 0:
            return

        # Get event values
        event_values = stim_data[onset_indices].astype(int).tolist()

        # Create annotations
        onsets = onset_indices / sfreq
        descriptions = [self._event_map.get(str(v), f"HID: event_{v}") for v in event_values]

        new_annotations = mne.Annotations(
            onset=onsets.tolist(),
            duration=[0.0] * len(onsets),
            description=descriptions,
        )

        raw.set_annotations(new_annotations)

    def _remap_annotations(self, raw: mne.io.BaseRaw) -> None:
        """Remap annotation descriptions to standardized labels."""
        current_annotations = raw.annotations
        new_descriptions = []

        for desc in current_annotations.description:
            # Try to match numeric event code
            try:
                # Handle numeric annotations
                if isinstance(desc, (int, float)) or (isinstance(desc, str) and desc.isdigit()):
                    event_code = str(int(float(desc)))
                    mapped_desc = self._event_map.get(event_code, f"HID: event_{event_code}")
                else:
                    # Try to extract numeric code from description
                    import re
                    match = re.search(r'\d+', str(desc))
                    if match:
                        event_code = match.group()
                        mapped_desc = self._event_map.get(event_code, str(desc))
                    else:
                        mapped_desc = str(desc)
            except (ValueError, TypeError):
                mapped_desc = str(desc)

            new_descriptions.append(mapped_desc)

        # Create new annotations with remapped descriptions
        remapped_annotations = mne.Annotations(
            onset=current_annotations.onset,
            duration=current_annotations.duration,
            description=new_descriptions,
        )

        raw.set_annotations(remapped_annotations)


# Module-level kernel instance
KERNEL = HIDKernel()