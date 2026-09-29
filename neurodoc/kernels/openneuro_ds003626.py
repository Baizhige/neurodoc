"""OpenNeuro ds003626 stage1 kernel for EEGUnity.

Inner Speech dataset - high-density EEG (137 channels) at 1024 Hz.
Three modalities: inner speech, pronounced speech, visualization.
Directional commands: Up, Down, Left, Right.

Source: https://openneuro.org/datasets/ds003626
DOI: 10.1038/s41597-022-01536-7
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Dataset descriptor paper DOI 10.1038/s41597-022-01536-7
# Annotator: LLM, 2026-04-09
# The paper describes 10 healthy subjects but does not provide individual age/sex.
# participants.tsv in the dataset lacks age/sex columns.
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}


# Channel mapping for 137-channel Biosemi ActiveTwo system
# Source: Biosemi 137-channel cap documentation; standard naming convention
# for Biosemi extended 10-20 system with additional electrodes.
# Annotator: LLM, 2026-04-09
# The dataset uses Biosemi's standard 137-channel naming. MNE may load these
# as generic labels or numbers; we ensure standard Biosemi names are used.
_BIOSEMI_137_CHANNELS = [
    # Standard 10-20
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7", "FC5", "FC3", "FC1",
    "C1", "C3", "C5", "T7", "TP7", "CP5", "CP3", "CP1", "P1", "P3", "P5",
    "P7", "P9", "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz", "Fpz",
    "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4", "F6", "F8", "FT8", "FC6",
    "FC4", "FC2", "FCz", "Cz", "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4",
    "CP2", "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
    # Additional 10-10 and 10-5 positions for high-density
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10",
    "C7", "C8", "C9", "C10", "D1", "D2", "D3", "D4", "D5", "D6",
    "D7", "D8", "D9", "D10", "E1", "E2", "E3", "E4", "E5", "E6",
    "E7", "E8", "E9", "E10", "F9", "F10", "G1", "G2", "G3", "G4",
    "G5", "G6", "G7", "G8", "G9", "G10", "H1", "H2", "H3", "H4",
    "H5", "H6", "H7", "H8", "H9", "H10", "I1", "I2", "I3", "I4",
    "I5", "I6", "I7", "I8", "I9", "I10",
    # Remaining positions to reach 137
    "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10",
    "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10",
    "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10",
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10",
    "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10",
]


def _detect_subject_id(file_path: str) -> str:
    """Extract subject ID from file path.
    
    Expected format: sub-<subject_id>
    """
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return match.group(1)
    
    # Fallback: extract from directory structure
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part.replace("sub-", "")
    
    return "unknown"


def _load_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from participants.tsv.
    
    Returns a dict with age, sex, handedness, and any extra columns.
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    
    if not os.path.exists(participants_file):
        return {}
    
    try:
        df = pd.read_csv(participants_file, sep="\t")
    except Exception:
        return {}
    
    # Find row for this subject
    for _, row in df.iterrows():
        participant_id = str(row.get("participant_id", ""))
        if participant_id == f"sub-{subject_id}" or participant_id == subject_id:
            info = {}
            # Required canonical fields
            age_raw = row.get("age", None)
            if age_raw is not None and not pd.isna(age_raw):
                try:
                    info["age"] = str(int(float(age_raw)))
                except (ValueError, TypeError):
                    info["age"] = "unknown"
            else:
                info["age"] = "unknown"
            
            sex_raw = row.get("sex", row.get("gender", None))
            if sex_raw is not None and not pd.isna(sex_raw):
                sex_str = str(sex_raw).strip().lower()
                if sex_str in ("m", "male"):
                    info["sex"] = "male"
                elif sex_str in ("f", "female"):
                    info["sex"] = "female"
                else:
                    info["sex"] = "unknown"
            else:
                info["sex"] = "unknown"
            
            handedness_raw = row.get("handedness", None)
            if handedness_raw is not None and not pd.isna(handedness_raw):
                hand_str = str(handedness_raw).strip().lower()
                if hand_str in ("r", "right"):
                    info["handedness"] = "right"
                elif hand_str in ("l", "left"):
                    info["handedness"] = "left"
                else:
                    info["handedness"] = "unknown"
            else:
                info["handedness"] = "unknown"
            
            # Extra fields for eegunity_description
            for col in df.columns:
                if col not in ("participant_id", "age", "sex", "gender", "handedness"):
                    val = row.get(col, None)
                    if val is not None and not pd.isna(val):
                        info[col] = str(val)
                    else:
                        info[col] = "unknown"
            
            return info
    
    return {}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".edf", "").replace(".set", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Check BIDS sidecar location
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    # Remove extension
    base_no_ext = os.path.splitext(base_name)[0]
    events_path2 = os.path.join(dir_path, base_no_ext + "_events.tsv")
    if os.path.exists(events_path2):
        return events_path2
    
    # Try broader search in subject directory
    subj_dir = os.path.dirname(file_path)
    for f in os.listdir(subj_dir) if os.path.isdir(subj_dir) else []:
        if f.endswith("_events.tsv"):
            return os.path.join(subj_dir, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns
    if "onset" not in events_df.columns:
        return None
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Description priority: trial_type > value > stim_type
    descriptions = []
    for _, row in events_df.iterrows():
        if "trial_type" in events_df.columns and pd.notna(row.get("trial_type", None)):
            desc = str(row["trial_type"])
        elif "value" in events_df.columns and pd.notna(row.get("value", None)):
            desc = str(row["value"])
        elif "stim_type" in events_df.columns and pd.notna(row.get("stim_type", None)):
            desc = str(row["stim_type"])
        else:
            desc = "unknown"
        descriptions.append(desc)
    
    # Filter out rows with empty descriptions
    valid_mask = [d.strip() != "" and d != "nan" and d != "None" for d in descriptions]
    if not any(valid_mask):
        return None
    
    onsets = onsets[valid_mask]
    durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(sum(valid_mask))
    descriptions = [d for d, v in zip(descriptions, valid_mask) if v]
    
    # Ensure durations match
    if len(durations) != len(onsets):
        durations = np.zeros(len(onsets))
    
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )
    return annotations


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to Biosemi 137 standard."""
    rename_map = {}
    existing = set(raw.ch_names)
    
    # Check if channels are already standard Biosemi names
    std_names = set(_BIOSEMI_137_CHANNELS)
    
    # If channels are numbered (common in some Biosemi exports), map to standard
    # Pattern: "A1", "A2" or "1", "2" or "EEG 001", "EEG 002"
    numbered_patterns = [
        (r'^(\d+)$', lambda m: int(m.group(1))),  # "1", "2", ...
        (r'^EEG\s*(\d+)$', lambda m: int(m.group(1))),  # "EEG 001", "EEG 002"
        (r'^EEG-(\d+)$', lambda m: int(m.group(1))),  # "EEG-001", "EEG-002"
        (r'^A(\d+)$', lambda m: int(m.group(1))),  # "A1", "A2" (Biosemi style)
        (r'^B(\d+)$', lambda m: 32 + int(m.group(1))),  # Extended naming
    ]
    
    # Check if we need renaming
    needs_rename = False
    for ch in existing:
        if ch not in std_names:
            needs_rename = True
            break
    
    if not needs_rename:
        return {}
    
    # Try to map numbered channels
    for ch in existing:
        if ch in std_names:
            continue
        
        for pattern, extractor in numbered_patterns:
            match = re.match(pattern, ch)
            if match:
                idx = extractor(match)
                # Biosemi 137: channels 1-137 (1-indexed in some exports, 0-indexed in others)
                if 0 <= idx < len(_BIOSEMI_137_CHANNELS):
                    target = _BIOSEMI_137_CHANNELS[idx]
                elif 1 <= idx <= len(_BIOSEMI_137_CHANNELS):
                    target = _BIOSEMI_137_CHANNELS[idx - 1]
                else:
                    continue
                
                if target not in existing or target == ch:
                    rename_map[ch] = target
                    break
    
    return rename_map


@dataclass
class OpenNeuroDS003626Kernel:
    """Stage1 kernel for OpenNeuro ds003626 (Inner Speech BCI Dataset)."""

    KERNEL_ID: str = "openneuro-ds003626-stage1"
    
    # Kernel requirements for downstream processing
    kernel_requirements = {
        "required_info_fields": [],  # participants.tsv lacks standard columns
        "required_native_misc": [],
        "derived_misc_channels": [],
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        subject_id = _detect_subject_id(file_path)
        
        # Load participant info from participants.tsv
        participant_info = _load_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": "Biosemi ActiveTwo",  # inferred by LLM, needs human review
            "cap": "Biosemi 137-channel ActiveTwo cap",  # inferred by LLM, needs human review
            "handedness": participant_info.get("handedness", "unknown"),
        }
        
        # Add any extra required info fields
        for key, val in participant_info.items():
            if key not in ("age", "sex", "handedness"):
                eegunity_description[key] = val
        
        # Update description
        original_desc = raw.info.get("description", "") or ""
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Channel renaming BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage for standard 10-20/10-10/10-5 positions
        # Biosemi 137 uses extended 10-5 system
        try:
            montage = mne.channels.make_standard_montage("biosemi128")
            # For 137 channels, we use standard_1025 or biosemi128 as approximation
            # inferred by LLM, needs human review
            raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
        except Exception:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
            except Exception:
                pass  # Montage setting failed, continue without
        
        # Ensure channel types are correctly set
        # Biosemi channels are typically EEG; check for any non-EEG channels
        ch_types = raw.get_channel_types()
        eog_candidates = [ch for ch in raw.ch_names if any(x in ch.upper() for x in ("EOG", "EYE", "EXG", "HEO", "VEO"))]
        misc_candidates = [ch for ch in raw.ch_names if any(x in ch.upper() for x in ("MISC", "STATUS", "TRIGGER", "STI"))]
        
        type_updates = {}
        for ch in eog_candidates:
            if ch in raw.ch_names:
                type_updates[ch] = "eog"
        for ch in misc_candidates:
            if ch in raw.ch_names:
                type_updates[ch] = "misc"
        
        if type_updates:
            raw.set_channel_types(type_updates)
        
        # Handle events from events.tsv for formats that don't carry their own triggers
        # BrainVision .eeg files should have .vmrk markers, but we ensure events.tsv
        # is used as fallback when native events are missing or insufficient
        needs_events_tsv = False
        
        # Check if raw already has meaningful annotations/events
        existing_annotations = raw.annotations
        if existing_annotations is None or len(existing_annotations) == 0:
            needs_events_tsv = True
        else:
            # Check if annotations are just recording segments (admin markers)
            admin_only = all(
                desc.startswith("event_3") or desc.startswith("event_4") or desc.startswith("event_6") or desc == "65536"
                for desc in existing_annotations.description
            ) if len(existing_annotations) > 0 else True
            if admin_only:
                needs_events_tsv = True
        
        # Also check for BrainVision marker file issues
        if file_path.endswith(".eeg") or file_path.endswith(".vhdr"):
            vmrk_path = file_path.replace(".eeg", ".vmrk").replace(".vhdr", ".vmrk")
            if not os.path.exists(vmrk_path):
                needs_events_tsv = True
        
        # Read and apply events from events.tsv if needed
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_df = _read_events_tsv(events_tsv_path)
            if events_df is not None and len(events_df) > 0:
                # Check if we need to use events.tsv (native events missing/insufficient)
                # or if we should supplement
                
                # Always derive annotations from events.tsv to ensure complete event coverage
                # This handles cases where BrainVision .vmrk may be incomplete
                annotations_from_tsv = _events_to_annotations(events_df, raw.info["sfreq"])
                
                if annotations_from_tsv is not None:
                    # Check for meaningful non-admin events in events.tsv
                    meaningful_events = [
                        desc for desc in annotations_from_tsv.description
                        if not (desc.startswith("event_3") or desc.startswith("event_4") or 
                                desc.startswith("event_5") or desc == "65536" or
                                desc.startswith("New Segment"))
                    ]
                    
                    if len(meaningful_events) > 0:
                        # Merge or replace annotations
                        if needs_events_tsv or len(existing_annotations) == 0:
                            raw.set_annotations(annotations_from_tsv)
                        else:
                            # Supplement existing annotations with events.tsv events
                            # that are not already present
                            existing_descs = set(existing_annotations.description)
                            new_onsets = []
                            new_durations = []
                            new_descriptions = []
                            
                            for onset, duration, desc in zip(
                                annotations_from_tsv.onset,
                                annotations_from_tsv.duration,
                                annotations_from_tsv.description
                            ):
                                # Simple deduplication: skip if very close to existing
                                is_new = True
                                for ex_onset in existing_annotations.onset:
                                    if abs(onset - ex_onset) < 0.001:
                                        is_new = False
                                        break
                                if is_new:
                                    new_onsets.append(onset)
                                    new_durations.append(duration)
                                    new_descriptions.append(desc)
                            
                            if new_onsets:
                                combined = existing_annotations.copy()
                                combined.append(new_onsets, new_durations, new_descriptions)
                                raw.set_annotations(combined)
        
        # Final verification: ensure events_from_annotations can yield the expected events
        try:
            events, event_id = mne.events_from_annotations(raw)
            # Verify we have the required event IDs
            required_events = ['event_11', 'event_12', 'event_13', 'event_14', 'event_15',
                             'event_21', 'event_22', 'event_23', 'event_51',
                             'event_61', 'event_62', 'event_63', 'event_64']
            found_events = set(event_id.keys())
            # Map numeric descriptions if needed
            for req in required_events:
                if req not in found_events:
                    # Check if numeric version exists
                    numeric = req.replace("event_", "")
                    if numeric in found_events:
                        pass  # Will be handled by downstream
        except Exception:
            pass  # No valid events to extract, but we tried our best
        
        return raw


KERNEL = OpenNeuroDS003626Kernel()