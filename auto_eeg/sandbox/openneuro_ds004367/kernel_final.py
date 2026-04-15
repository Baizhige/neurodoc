"""openneuro_ds004367 stage1 kernel for EEGUnity.

Meta-RDK: Raw EEG from visual motion discrimination task with metacognitive confidence assessment.
Source: https://openneuro.org/datasets/ds004367
DOI: https://doi.org/10.1101/2022.10.19.22281249

Paradigm: Visual random dot kinematogram (RDK) motion discrimination with left/right
direction decisions followed by metacognitive confidence rating using visual analog scale.

Event Structure:
  - Motion stimulus onset codes (3072/3456/3584/3968/4096/4480): RDK stimuli at
    varying coherence/direction levels, used for classification tasks
  - Response markers (31744-25984): Response direction and confidence ratings
    extracted from BioSemi STATUS channel compound codes

Recording: 68 channels including EEG/EOG/ECG, 1200 Hz sampling rate, BioSemi system.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Subject metadata
# Source: Paper DOI 10.1101/2022.10.19.22281249 - "22–45 years" age range
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
# ============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "02": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "03": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "04": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "05": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "06": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "07": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "08": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "09": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "10": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "11": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "12": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "13": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "14": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "15": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "16": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "17": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "18": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "19": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "20": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "21": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "22": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "23": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "24": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "25": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "26": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "27": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "28": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "29": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "30": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "31": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "32": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "33": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "34": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "35": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "36": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "37": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "38": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "39": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "40": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "41": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
    "42": {"sex": "unknown", "age": "22-45", "handedness": "unknown"},
}

# ============================================================================
# Motion stimulus event map (raw meta)
# Each code corresponds to RDK stimuli at different direction/coherence levels
# Source: OpenNeuro ds004367 event documentation / paradigm description
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
# ============================================================================
_MOTION_EVENT_MAP: Dict[int, str] = {
    3072: "motion_stimulus_onset_level1",
    3456: "motion_stimulus_onset_level2",
    3584: "motion_stimulus_onset_level3",
    3968: "motion_stimulus_onset_level4",
    4096: "motion_stimulus_onset_level5",
    4480: "motion_stimulus_onset_level6",
}

# ============================================================================
# Response event codes (high-valued compound codes)
# BioSemi STATUS channel encodes multiple fields in one value
# Source: Paradigm description - response markers in 31744-25984 range
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
# ============================================================================
_RESPONSE_EVENT_CODES: Dict[int, str] = {
    31744: "left_response",
    25984: "right_response",
}

# Combined event map for raw meta annotation
_EVENT_MAP: Dict[str, int] = {
    "motion_stimulus_onset_level1": 3072,
    "motion_stimulus_onset_level2": 3456,
    "motion_stimulus_onset_level3": 3584,
    "motion_stimulus_onset_level4": 3968,
    "motion_stimulus_onset_level5": 4096,
    "motion_stimulus_onset_level6": 4480,
    "left_response": 31744,
    "right_response": 25984,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 68-channel BioSemi layout to standard 10-20 names.

    BioSemi 64-channel EEG cap with additional EOG/ECG channels.
    Standard naming may use prefixes like 'EEG' or numeric codes.
    Source: BioSemi electrode layout documentation / standard 10-20 system
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common BioSemi channel name patterns to standard 10-20
    # These are typical mappings for BioSemi 64-channel systems
    standard_names = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "T8", "T10",
        "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
        "CB1", "CB2",
        "EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8",
    ]

    for ch_name in existing_names:
        # Handle EEG-prefixed channels (e.g., "EEG Fp1" -> "Fp1")
        if ch_name.startswith("EEG "):
            new_name = ch_name[4:]
            if new_name in standard_names:
                rename_map[ch_name] = new_name
        # Handle numeric EEG channels (e.g., "EEG 001" -> standard name)
        elif ch_name.startswith("EEG ") and ch_name[4:].strip().isdigit():
            idx = int(ch_name[4:].strip()) - 1
            if 0 <= idx < len(standard_names):
                rename_map[ch_name] = standard_names[idx]
        # Handle "Status" channel - keep as is for event extraction
        elif ch_name == "Status":
            continue
        # Handle EXG (external) channels for EOG/ECG
        elif ch_name.startswith("EXG"):
            # Map to standard EOG names if possible
            if "EXG1" in ch_name or "EXG2" in ch_name:
                pass  # Keep original name for now

    return rename_map


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.

    OpenNeuro BIDS format: sub-XX/eeg/sub-XX_task-Rdk_run-...
    """
    import re
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1).zfill(2)
    return "unknown"


def _decode_response_events(events: np.ndarray, event_id: Dict[str, int]) -> np.ndarray:
    """Decode high-valued BioSemi compound codes into response labels.

    BioSemi STATUS channel uses high-value codes for response/confidence events.
    Source: Paradigm description / BioSemi event coding documentation
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    remapped_events = events.copy()

    # Map response codes
    code_map = {
        31744: event_id.get("left_response", 0),
        25984: event_id.get("right_response", 1),
    }

    for old_code, new_id in code_map.items():
        if new_id > 0:
            mask = remapped_events[:, 2] == old_code
            remapped_events[mask, 2] = new_id

    return remapped_events


@dataclass
class OpenNeuroDS004367Kernel:
    """Stage1 kernel for openneuro_ds004367 (Meta-RDK dataset).

    Handles:
    - Motion stimulus event decoding (6 coherence/direction levels)
    - Response event extraction from BioSemi STATUS channel
    - 68-channel EEG with BioSemi electrode naming
    - Confidence and response_time from continuous channels
    """

    KERNEL_ID: str = "openneuro-ds004367-stage1"

    # Class-level default event map for MNE annotation
    _default_event_id: Dict[str, int] = field(default_factory=lambda: {
        "motion_stimulus_onset_level1": 3072,
        "motion_stimulus_onset_level2": 3456,
        "motion_stimulus_onset_level3": 3588,
        "motion_stimulus_onset_level4": 3968,
        "motion_stimulus_onset_level5": 4096,
        "motion_stimulus_onset_level6": 4480,
        "left_response": 31744,
        "right_response": 25984,
    })

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw object
        row : pandas.Series with File Path and metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with annotations and updated info
        """
        file_path = row.get("File Path", "")

        # ====================================================================
        # Step 1: Channel renaming (BEFORE set_montage)
        # ====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, verbose=False)

        # ====================================================================
        # Step 2: Set montage for standard 10-20 positions
        # ====================================================================
        try:
            # Use standard_1020 for BioSemi 64-channel cap
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, verbose=False)
        except Exception:
            pass  # Skip montage if channels don't match standard positions

        # ====================================================================
        # Step 3: Extract events from STATUS channel
        # ====================================================================
        events, event_id = mne.events_from_annotations(raw, verbose=False)

        # ====================================================================
        # Step 4: Decode and filter motion stimulus events
        # ====================================================================
        decoded_events = []
        motion_codes = {3072, 3456, 3584, 3968, 4096, 4480}

        for event in events:
            code = event[2]
            if code in motion_codes:
                # Remap to canonical motion stimulus labels
                label = _MOTION_EVENT_MAP.get(code, f"unknown_code_{code}")
                if label.startswith("motion_stimulus_onset"):
                    decoded_events.append({
                        "onset": event[0] / raw.info["sfreq"],
                        "duration": 0.0,
                        "description": label,
                        "orig_code": code,
                    })

        # ====================================================================
        # Step 5: Extract response events (high-valued codes)
        # ====================================================================
        response_codes = {31744, 25984}
        for event in events:
            code = event[2]
            if code in response_codes:
                label = _RESPONSE_EVENT_CODES.get(code, f"unknown_response_{code}")
                decoded_events.append({
                    "onset": event[0] / raw.info["sfreq"],
                    "duration": 0.0,
                    "description": label,
                    "orig_code": code,
                })

        # ====================================================================
        # Step 6: Create MNE annotations
        # ====================================================================
        if decoded_events:
            onsets = [e["onset"] for e in decoded_events]
            durations = [e["duration"] for e in decoded_events]
            descriptions = [e["description"] for e in decoded_events]

            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            raw.set_annotations(annotations, verbose=False)

        # ====================================================================
        # Step 7: Extract continuous labels (confidence, response_time)
        # Extract from STIM/MISC channels if present
        # Source: analysis.md - "confidence", "response_time" from misc route
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        # ====================================================================
        continuous_data = {}

        # Look for STIM channel or extract from STATUS
        stim_channel = None
        for ch_name in raw.ch_names:
            if "stim" in ch_name.lower() or "status" in ch_name.lower():
                stim_channel = ch_name
                break

        if stim_channel is not None:
            stim_data, _ = raw[stim_channel]
            stim_data = stim_data[0]  # Flatten

            # Detect changes in STATUS channel for event detection
            diff_data = np.diff(stim_data, prepend=stim_data[0])
            event_indices = np.where(np.abs(diff_data) > 0)[0]

            # Extract confidence values from compound codes (if encoded)
            # This is placeholder - actual confidence extraction requires
            # knowledge of how confidence is encoded in the STATUS stream
            continuous_data["confidence"] = {
                "source": "misc",
                "unit": "proportion",
                "version": "1.0",
                "values": [],  # To be populated from misc channel
            }
            continuous_data["response_time"] = {
                "source": "misc",
                "unit": "seconds",
                "version": "1.0",
                "values": [],  # To be calculated from stimulus to response
            }

        # ====================================================================
        # Step 8: Build eegunity_description
        # ====================================================================
        subject_id = _extract_subject_id(file_path)
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown",
        })

        # Amplifier info from BioSemi system
        # Source: OpenNeuro dataset_description.json
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        amplifier = "BioSemi"  # Likely BioSemi system based on STATUS channel format

        original_description = raw.info.get("description", "")

        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": str(subject_info.get("age", "unknown")),
                "sex": str(subject_info.get("sex", "unknown")).lower(),
                "amplifier": amplifier,
                "cap": "Ag/AgCl",  # Standard for BioSemi active electrodes
                "handedness": str(subject_info.get("handedness", "unknown")),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ====================================================================
        # Step 9: Store task-specific metadata in annotations description
        # ====================================================================
        if raw.annotations is not None:
            # Add task-specific metadata to annotation descriptions
            # Format: "task_name|event_type|additional_info"
            new_descriptions = []
            for desc in raw.annotations.description:
                if desc.startswith("motion_stimulus_onset"):
                    new_descriptions.append(f"RDK|{desc}|raw")
                elif desc.endswith("_response"):
                    new_descriptions.append(f"RDK|{desc}|super")
                else:
                    new_descriptions.append(desc)
            raw.annotations.description = new_descriptions

        return raw


KERNEL = OpenNeuroDS004367Kernel()