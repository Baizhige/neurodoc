"""OpenNeuro DS006040 (gradCPT) stage1 kernel for EEGUnity.

Sustained Attention Task dataset using simultaneous EEG-fMRI.
64-channel EEG, 5000 Hz sampling rate.
Events: S155 (mountain standard), S245 (city target), S254 (button press).

Source: https://openneuro.org/datasets/ds006040
Reference: https://doi.org/10.1038/s41597-026-06616-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ============================================================================
# Channel Mapping for 64-channel EEG cap (standard 10-20 layout)
# ============================================================================
# Source: Standard 64-channel EEG cap electrode positions following extended
# 10-20 system. Channel names follow Brain Products / BrainAmp convention.
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核

_64CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz",
    # Extra channels if present (EOG, ECG, etc.)
    "EOG-left", "EOG-right", "EOG-up", "EOG-down",
    "ECG", "EMG-mentalis", "EMG-orbicularis",
]


def _build_64ch_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 64-channel standard montage."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common patterns for BrainAmp 64-channel data
    alias_groups = [
        # StandardFp/Fz naming
        ("Fp1", ["Fp1", "Fp 1", "EEG Fp1", "Fp_1"]),
        ("Fp2", ["Fp2", "Fp 2", "EEG Fp2", "Fp_2"]),
        ("Fpz", ["Fpz", "Fpz", "EEG Fpz"]),
        # AF row
        ("AF7", ["AF7", "AF 7", "EEG AF7"]),
        ("AF3", ["AF3", "AF 3", "EEG AF3"]),
        ("AFz", ["AFz", "AFz", "EEG AFz"]),
        ("AF4", ["AF4", "AF 4", "EEG AF4"]),
        ("AF8", ["AF8", "AF 8", "EEG AF8"]),
        # F row
        ("F7", ["F7", "F 7", "EEG F7"]),
        ("F5", ["F5", "F 5", "EEG F5"]),
        ("F3", ["F3", "F 3", "EEG F3"]),
        ("F1", ["F1", "F 1", "EEG F1"]),
        ("Fz", ["Fz", "Fz", "EEG Fz"]),
        ("F2", ["F2", "F 2", "EEG F2"]),
        ("F4", ["F4", "F 4", "EEG F4"]),
        ("F6", ["F6", "F 6", "EEG F6"]),
        ("F8", ["F8", "F 8", "EEG F8"]),
        # FC row
        ("FT7", ["FT7", "FT 7", "EEG FT7"]),
        ("FC5", ["FC5", "FC 5", "EEG FC5"]),
        ("FC3", ["FC3", "FC 3", "EEG FC3"]),
        ("FC1", ["FC1", "FC 1", "EEG FC1"]),
        ("FCz", ["FCz", "FCz", "EEG FCz"]),
        ("FC2", ["FC2", "FC 2", "EEG FC2"]),
        ("FC4", ["FC4", "FC 4", "EEG FC4"]),
        ("FC6", ["FC6", "FC 6", "EEG FC6"]),
        ("FT8", ["FT8", "FT 8", "EEG FT8"]),
        # C row
        ("T7", ["T7", "T 7", "EEG T7", "T3"]),
        ("C5", ["C5", "C 5", "EEG C5"]),
        ("C3", ["C3", "C 3", "EEG C3"]),
        ("C1", ["C1", "C 1", "EEG C1"]),
        ("Cz", ["Cz", "Cz", "EEG Cz"]),
        ("C2", ["C2", "C 2", "EEG C2"]),
        ("C4", ["C4", "C 4", "EEG C4"]),
        ("C6", ["C6", "C 6", "EEG C6"]),
        ("T8", ["T8", "T 8", "EEG T8", "T4"]),
        # CP row
        ("TP7", ["TP7", "TP 7", "EEG TP7"]),
        ("CP5", ["CP5", "CP 5", "EEG CP5"]),
        ("CP3", ["CP3", "CP 3", "EEG CP3"]),
        ("CP1", ["CP1", "CP 1", "EEG CP1"]),
        ("CPz", ["CPz", "CPz", "EEG CPz"]),
        ("CP2", ["CP2", "CP 2", "EEG CP2"]),
        ("CP4", ["CP4", "CP 4", "EEG CP4"]),
        ("CP6", ["CP6", "CP 6", "EEG CP6"]),
        ("TP8", ["TP8", "TP 8", "EEG TP8"]),
        # P row
        ("P7", ["P7", "P 7", "EEG P7"]),
        ("P5", ["P5", "P 5", "EEG P5"]),
        ("P3", ["P3", "P 3", "EEG P3"]),
        ("P1", ["P1", "P 1", "EEG P1"]),
        ("Pz", ["Pz", "Pz", "EEG Pz"]),
        ("P2", ["P2", "P 2", "EEG P2"]),
        ("P4", ["P4", "P 4", "EEG P4"]),
        ("P6", ["P6", "P 6", "EEG P6"]),
        ("P8", ["P8", "P 8", "EEG P8"]),
        # PO row
        ("PO7", ["PO7", "PO 7", "EEG PO7"]),
        ("PO3", ["PO3", "PO 3", "EEG PO3"]),
        ("POz", ["POz", "POz", "EEG POz"]),
        ("PO4", ["PO4", "PO 4", "EEG PO4"]),
        ("PO8", ["PO8", "PO 8", "EEG PO8"]),
        # O row
        ("O1", ["O1", "O 1", "EEG O1"]),
        ("Oz", ["Oz", "Oz", "EEG Oz"]),
        ("O2", ["O2", "O 2", "EEG O2"]),
        ("Iz", ["Iz", "Iz", "EEG Iz"]),
        # Auxiliary channels
        ("EOG-left", ["EOG-left", "EOG L", "EOGL", "Veog-left"]),
        ("EOG-right", ["EOG-right", "EOG R", "EOGR", "Veog-right"]),
        ("EOG-up", ["EOG-up", "EOG U", "EOGU"]),
        ("ECG", ["ECG", "ecg", "Cardiac"]),
        ("EMG-mentalis", ["EMG-mentalis", "EMG1", "EMG-mental"]),
        ("EMG-orbicularis", ["EMG-orbicularis", "EMG2", "EMG-orb"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


# ============================================================================
# Event Mapping
# ============================================================================
_EVENT_DESCRIPTION_MAP = {
    "155": "S155",
    "245": "S245",
    "254": "S254",
    "sync": "Sync On",
    "qrs": "qrs",
    "tr": "TR",
    "t1": "T 1",
    "[]": "[]",
}


def _parse_event_description(desc: str) -> str:
    """Parse event description to canonical form."""
    if not desc or desc == "":
        return "[]"

    desc_clean = str(desc).strip()
    desc_lower = desc_clean.lower()

    # Direct numeric codes
    if desc_clean in ("155", "S155"):
        return "S155"
    if desc_clean in ("245", "S245"):
        return "S245"
    if desc_clean in ("254", "S254"):
        return "S254"

    # Admin events
    if "sync" in desc_lower:
        return "Sync On"
    if desc_lower in ("qrs", "q r s", "cardiac"):
        return "qrs"
    if desc_lower in ("tr", "trigger", "repetition"):
        return "TR"
    if desc_lower in ("t1", "t 1", "marker t1"):
        return "T 1"

    # Empty
    if desc_clean in ("[]", "empty", "null", ""):
        return "[]"

    return desc_clean


# ============================================================================
# gradCPT Trial Logic (Super Meta)
# ============================================================================
def _build_trial_correctness_annotations(
    events: np.ndarray,
    event_id: Dict[str, int],
    sfreq: float,
) -> Tuple[List[float], List[float], List[str]]:
    """Build trial correctness labels for gradCPT.

    For each S155/S245 stimulus event, check if S254 occurred within
    the trial window (0-2s).

    Returns:
        Tuple of (onset_times, durations, descriptions)
    """
    onset_list: List[float] = []
    duration_list: List[float] = []
    desc_list: List[str] = []

    stimulus_id = event_id.get("S155") or event_id.get("245")
    target_id = event_id.get("S245") or event_id.get("245")
    response_id = event_id.get("S254") or event_id.get("254")

    if stimulus_id is None or response_id is None:
        return [], [], []

    # Get all stimulus events (S155 and S245)
    stimulus_mask = (events[:, 2] == stimulus_id) | (events[:, 2] == target_id)
    stimulus_events = events[stimulus_mask]

    # Get all response events
    response_mask = events[:, 2] == response_id
    response_times = events[response_mask, 0] / sfreq

    trial_window = 2.0  # seconds

    for stim_event in stimulus_events:
        stim_time = stim_event[0] / sfreq
        stim_type = "S155" if stim_event[2] == stimulus_id else "S245"

        # Check for response within window
        response_in_window = np.any(
            (response_times >= stim_time) & (response_times <= stim_time + trial_window)
        )

        if stim_type == "S155":
            # Mountain scene: correct if NO response (correct omission)
            if response_in_window:
                label = "commission_error"
            else:
                label = "correct_omission"
        else:  # S245
            # City scene: correct if response (correct commission)
            if response_in_window:
                label = "correct_commission"
            else:
                label = "omission_error"

        onset_list.append(stim_time)
        duration_list.append(0.0)
        desc_list.append(label)

    return onset_list, duration_list, desc_list


# ============================================================================
# Kernel Class
# ============================================================================
class OpenNeuroDS006040Kernel:
    """Stage1 kernel for OpenNeuro DS006040 (gradCPT) dataset."""

    KERNEL_ID: str = "openneuro-ds006040-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object.
        """
        file_path = row.get("File Path", "")

        # =====================================================================
        # 1. Update description with eegunity_description
        # =====================================================================
        # age/sex from OpenNeuro: not provided in BIDS metadata
        # Source: dataset analysis.md, 2026-04-08
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": "BrainAmp MR plus",  # LLM 推断，需人类复核 (typical for fMRI-compatible EEG)
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # =====================================================================
        # 2. Rename channels to standard names (BEFORE set_montage)
        # =====================================================================
        rename_map = _build_64ch_rename_map(raw)
        if rename_map:
            # fmt: off
            raw.rename_channels(rename_map, allow_duplicates=False)
            # fmt: on

        # =====================================================================
        # 3. Set standard 10-20 montage
        # =====================================================================
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage is optional if channel names don't match

        # =====================================================================
        # 4. Parse and set annotations from events
        # =====================================================================
        try:
            # Try to get events from raw annotations first
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = np.empty((0, 3))
            event_id = {}

        if len(events) > 0:
            # Map event descriptions to canonical form
            canonical_event_id: Dict[str, int] = {}
            max_id = 0

            for desc, orig_id in event_id.items():
                canonical = _parse_event_description(desc)
                if canonical not in canonical_event_id.values():
                    max_id += 1
                    canonical_event_id[canonical] = max_id

            # Rebuild events with canonical IDs
            new_events = events.copy()
            desc_to_new_id = {
                _parse_event_description(
                    list(event_id.keys())[
                        list(event_id.values()).index(orig_id)
                    ]
                ): new_id
                for desc, orig_id in event_id.items()
                for new_id in [canonical_event_id.get(
                    _parse_event_description(desc)
                )]
                if new_id is not None
            }

            for i, event_row in enumerate(new_events):
                orig_desc = None
                for desc, orig_id in event_id.items():
                    if orig_id == event_row[2]:
                        orig_desc = desc
                        break
                if orig_desc is not None:
                    canonical = _parse_event_description(orig_desc)
                    if canonical in canonical_event_id:
                        new_events[i, 2] = canonical_event_id[canonical]

            events = new_events

        # Convert to annotations
        if len(events) > 0:
            sfreq = raw.info["sfreq"]
            onsets = events[:, 0] / sfreq
            durations = np.zeros(len(events))

            # Map event IDs to descriptions
            reverse_map = {v: k for k, v in canonical_event_id.items()}
            descriptions = [
                reverse_map.get(eid, f"event_{eid}")
                for eid in events[:, 2]
            ]

            annotations = mne.Annotations(
                onset=onsets.tolist(),
                duration=durations.tolist(),
                description=descriptions,
            )
            raw.set_annotations(annotations)

        # =====================================================================
        # 5. Downsample from 5000 Hz to 500 Hz for processing
        # =====================================================================
        if raw.info["sfreq"] > 500:
            # Calculate decimation factor
            current_sfreq = raw.info["sfreq"]
            target_sfreq = 500
            decim = max(1, int(round(current_sfreq / target_sfreq)))

            # Don't exceed factor of 10 to avoid MNE issues
            if decim > 10:
                decim = 10

            if decim > 1:
                raw = raw.copy()
                raw.decimate(decim, verbose=False)

        return raw


KERNEL = OpenNeuroDS006040Kernel()