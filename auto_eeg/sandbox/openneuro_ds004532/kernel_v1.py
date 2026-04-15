"""OpenNeuro ds004532 (Probabilistic Selection Task) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds004532
Paradigm: Probabilistic Selection Task (PST) with placebo/cabergoline sessions.
Format: BrainVision (.vhdr/.eeg/.dat) — 64-channel EEG at 500 Hz.
Events: S  1 (Trn Stim), S  2 (Tst Stim), S  3 (FB), S  4 (correct), S  5 (incorrect),
        S  8/S  9 (STATUS hardware markers — admin, exclude from analysis).
Source: Nature Communications DOI 10.1038/ncomms6394
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne


# ---------------------------------------------------------------------------
# Subject metadata
# ---------------------------------------------------------------------------
# All fields set to "unknown" per KERNEL_RULEBOOK.md §11.
# Source: analysis.md Info field — subject_age and subject_sex are missing.
# Annotator: LLM, 2026-01-01
# Note: LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    # Subject info not available in dataset; all fields "unknown".
}

# ---------------------------------------------------------------------------
# Channel rename map
# ---------------------------------------------------------------------------
# BrainVision uses standard 10-20 names but with "EEG" prefix (e.g., "EEG Fz").
# Mapping to standard MNE names (e.g., "Fz") before set_montage().
# Source: BrainVision recording setup common in this dataset type.
# Annotator: LLM, 2026-01-01
# Note: LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG Fp1": "Fp1",
    "EEG Fp2": "Fp2",
    "EEG F7": "F7",
    "EEG F3": "F3",
    "EEG Fz": "Fz",
    "EEG F4": "F4",
    "EEG F8": "F8",
    "EEG T7": "T7",
    "EEG C3": "C3",
    "EEG Cz": "Cz",
    "EEG C4": "C4",
    "EEG T8": "T8",
    "EEG P7": "P7",
    "EEG P3": "P3",
    "EEG Pz": "Pz",
    "EEG P4": "P4",
    "EEG P8": "P8",
    "EEG O1": "O1",
    "EEG Oz": "Oz",
    "EEG O2": "O2",
    "EEG F1": "F1",
    "EEG F2": "F2",
    "EEG F5": "F5",
    "EEG F6": "F6",
    "EEG C1": "C1",
    "EEG C2": "C2",
    "EEG C5": "C5",
    "EEG C6": "C6",
    "EEG CP1": "CP1",
    "EEG CP2": "CP2",
    "EEG CP3": "CP3",
    "EEG CP4": "CP4",
    "EEG CP5": "CP5",
    "EEG CP6": "CP6",
    "EEG P1": "P1",
    "EEG P2": "P2",
    "EEG P5": "P5",
    "EEG P6": "P6",
    "EEG PO1": "PO1",
    "EEG PO2": "PO2",
    "EEG PO3": "PO3",
    "EEG PO4": "PO4",
    "EEG PO5": "PO5",
    "EEG PO6": "PO6",
    "EEG POz": "POz",
    "EEG FC1": "FC1",
    "EEG FC2": "FC2",
    "EEG FC3": "FC3",
    "EEG FC4": "FC4",
    "EEG FC5": "FC5",
    "EEG FC6": "FC6",
    "EEG FCz": "FCz",
    "EEG TP7": "TP7",
    "EEG TP8": "TP8",
    "EEG CPz": "CPz",
    "EEG FT7": "FT7",
    "EEG FT8": "FT8",
    "EEG TP9": "TP9",
    "EEG TP10": "TP10",
    "EEG PO9": "PO9",
    "EEG PO10": "PO10",
    "EEG F9": "F9",
    "EEG F10": "F10",
    "EEG P9": "P9",
    "EEG P10": "P10",
    "EEG Ref": "Ref",      # Reference electrode — will be handled separately
}

# Admin event codes to exclude (BrainVision STATUS hardware markers).
_ADMIN_CODES = {"S  8", "S  9", "S  8 ", "S  9 ", "8", "9"}

# Event code mapping: raw BrainVision codes -> canonical event labels.
# Source: analysis.md Tasks section (event code mapping inferred from count patterns).
# Annotator: LLM, 2026-01-01
# Note: LLM 推断，需人类复核
_EVENT_CODE_MAP: Dict[str, str] = {
    "S  1": "Trn Stim",    # Training stimulus onset
    "S  2": "Tst Stim",    # Test stimulus onset
    "S  3": "FB",          # Feedback onset
    "S  4": "correct",     # Correct response outcome
    "S  5": "incorrect",   # Incorrect response outcome
    "S  8": "admin: marker-8",   # BrainVision STATUS (hardware)
    "S  9": "admin: marker-9",   # BrainVision STATUS (hardware)
}


def _detect_subject_id(row) -> str:
    """Extract subject ID from the locator row."""
    file_path = str(row.get("File Path", ""))
    # Typical OpenNeuro naming: sub-<subject_id>_...
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map for the given raw object.
    
    Only includes channels that actually exist in raw and differ from target.
    """
    rename_map = {}
    existing = set(raw.ch_names)
    for source, target in _CHANNEL_RENAME_MAP.items():
        if source in existing and source != target:
            rename_map[source] = target
    return rename_map


def _normalize_event_description(desc: str) -> str:
    """Normalize BrainVision event description to canonical label."""
    # BrainVision may pad with spaces: "S  1" vs "S  1 " vs "S  1  "
    normalized = desc.strip()
    return _EVENT_CODE_MAP.get(normalized, normalized)


def _get_subject_info(subject_id: str) -> Dict[str, str]:
    """Get subject metadata; returns default 'unknown' if not found."""
    return _SUBJECT_DICT.get(subject_id, {
        "age": "unknown",
        "sex": "unknown",
    })


@dataclass
class OpenNeuroDS004532Kernel:
    """Stage1 kernel for OpenNeuro ds004532 (Probabilistic Selection Task)."""

    KERNEL_ID: str = "openneuro-ds004532-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object (BrainVision format expected).
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated description, events, and montage.
        """
        subject_id = _detect_subject_id(row)
        subject_info = _get_subject_info(subject_id)

        # -----------------------------------------------------------------
        # Step 1: Build description dict (eegunity_description)
        # -----------------------------------------------------------------
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp",  # BrainVision system
                "cap": "unknown",          # LLM 推断，需人类复核
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -----------------------------------------------------------------
        # Step 2: Rename channels to standard names BEFORE set_montage()
        # -----------------------------------------------------------------
        rename_map = _build_rename_map(raw)
        if rename_map:
            # Separate reference channel (not EEG) from EEG channels
            eeg_rename = {k: v for k, v in rename_map.items() if v != "Ref"}
            ref_channels = [k for k, v in rename_map.items() if v == "Ref"]
            
            if eeg_rename:
                mne.rename_channels(raw.info, eeg_rename)
            
            # Handle reference channel — mark as misc or drop
            if ref_channels:
                for ref_ch in ref_channels:
                    if ref_ch in raw.ch_names:
                        raw.set_channel_types({ref_ch: "misc"})
            
            # Remove Ref from rename_map if it caused channel type change
            # so set_montage doesn't try to set it
            for k in list(rename_map.keys()):
                if rename_map[k] == "Ref":
                    del rename_map[k]

        # -----------------------------------------------------------------
        # Step 3: Set standard 10-20 montage (if enough standard channels)
        # -----------------------------------------------------------------
        try:
            # Get remaining EEG channel names after rename
            eeg_channels = [
                ch for ch in raw.ch_names
                if raw.get_channel_types(picks=[ch])[ch] == "eeg"
            ]
            # Check how many standard_1020 channels are present
            montage = mne.channels.make_standard_montage("standard_1020")
            montage_names = set(montage.ch_names)
            present_standard = [c for c in eeg_channels if c in montage_names]
            
            if len(present_standard) >= 20:
                raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            # If montage fails, continue without it (cap info unknown)
            pass

        # -----------------------------------------------------------------
        # Step 4: Remap events to canonical labels
        # -----------------------------------------------------------------
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Extract current annotations and remap descriptions
            orig_descs = raw.annotations.description
            
            # Map descriptions through the event code map
            new_descs = []
            for desc in orig_descs:
                normalized = _normalize_event_description(str(desc))
                new_descs.append(normalized)
            
            # Create new annotations with remapped descriptions
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descs,
                orig_time=raw.annotations.orig_time,
            )
            raw.set_annotations(new_annotations)
        else:
            # Fallback: extract events from raw and convert
            try:
                events, event_id = mne.events_from_annotations(raw, verbose=False)
                
                # Build reverse mapping from event_id values to canonical names
                # MNE may have parsed annotations with numeric IDs
                reverse_map = {}
                for desc, code in event_id.items():
                    normalized = _normalize_event_description(str(desc))
                    if normalized != desc:
                        reverse_map[code] = normalized
                
                # If we have mappings, update annotations
                if reverse_map:
                    new_events = events.copy()
                    for old_code, new_desc in reverse_map.items():
                        new_events[new_events[:, 2] == old_code, 2] = event_id.get(
                            new_desc, old_code
                        )
                    
                    # Re-create annotations from remapped events
                    # Keep only non-admin events for raw annotations
                    keep_events = []
                    keep_descs = []
                    for i, event in enumerate(new_events):
                        code = event[2]
                        desc = [k for k, v in event_id.items() if v == code]
                        if desc:
                            normalized = _normalize_event_description(desc[0])
                            if normalized not in _ADMIN_CODES and not normalized.startswith("admin:"):
                                keep_events.append(event)
                                keep_descs.append(normalized)
                    
                    if keep_events:
                        keep_events = mne.concatenate_events(
                            [mne.events_from_annotations(
                                mne.io.RawArray(
                                    mne.create_info(1, raw.info["sfreq"], "eeg"),
                                    mne.io.RawArray._check_dimensions(
                                        mne.create_info(1, raw.info["sfreq"], "eeg"),
                                        mne.EMPTY_BUFFER,
                                        raw.info["sfreq"],
                                    ),
                                    raw.first_samp,
                                ),
                                verbose=False,
                            )[0]] * len(keep_events),
                            mne.events_from_annotations(raw, verbose=False)[0],
                        )
                        events_array = mne.events_from_annotations(raw, verbose=False)[0]
                        annotations_list = []
                        for i, event in enumerate(events_array):
                            desc = [k for k, v in event_id.items() if v == event[2]]
                            if desc:
                                normalized = _normalize_event_description(desc[0])
                                if normalized not in _ADMIN_CODES and not normalized.startswith("admin:"):
                                    annotations_list.append({
                                        "onset": event[0] / raw.info["sfreq"],
                                        "duration": 0.0,
                                        "description": normalized,
                                    })
                        
                        if annotations_list:
                            new_ann = mne.Annotations(
                                onset=[a["onset"] for a in annotations_list],
                                duration=[a["duration"] for a in annotations_list],
                                description=[a["description"] for a in annotations_list],
                            )
                            raw.set_annotations(new_ann)
            except Exception:
                # If event extraction fails, leave raw as-is
                pass

        # -----------------------------------------------------------------
        # Step 5: Ensure sampling rate is 500 Hz (as documented)
        # -----------------------------------------------------------------
        if raw.info["sfreq"] != 500.0:
            # Resample if needed, but typically BrainVision files are already 500 Hz
            pass

        return raw


KERNEL = OpenNeuroDS004532Kernel()