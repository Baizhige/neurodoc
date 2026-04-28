"""openneuro_ds004022 stage1 kernel for EEGUnity.

Dataset: Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks
         in Patients with Orthopedic Impairment
Source: https://openneuro.org/datasets/ds004022 (doi:10.18112/openneuro.ds004022.v1.0.0)
Paper: 10.1371/journal.pone.0335364, 10.1016/j.bspc.2025.108597, 10.3389/fnhum.2025.1583342

18 EEG channels, 500 Hz, 7 subjects with orthopedic impairment + healthy controls
performing Reach/Twist/Lift/Grasp motor imagery tasks (events S 7-S 10).

BIDS-compliant dataset with EEGLAB .set files, participants.tsv, and events.tsv sidecars.
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


# ============================================================================
# CONSTANTS
# ============================================================================

# 18 active EEG channels as reported in dataset documentation
# Source: dataset README, paper 10.1371/journal.pone.0335364
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_ACTIVE_EEG_CHANNELS_18 = [
    "F3", "F4", "Fz",
    "FC3", "FCz", "FC4",
    "C3", "C4", "Cz",
    "CP3", "CPz", "CP4",
    "P3", "P4", "Pz",
    "O1", "O2", "Oz",
]

# Event ID mapping from raw numeric codes to descriptive strings
# Source: analysis.md Event Structure table, dataset events.tsv
# Annotator: LLM, 2026-04-08
_EVENT_MAP: Dict[int, str] = {
    1: "S 1",
    2: "S 2",
    3: "S 3",
    4: "S 4",
    5: "S 5",
    6: "S 6",
    7: "S 7",
    8: "S 8",
    9: "S 9",
    10: "S 10",
    12: "condition 12",
}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["Hand Dominance", "Years Since Diagnosis", "age", "sex"]

# Required native misc channels (none for this dataset)
_REQUIRED_NATIVE_MISC: List[str] = []

# Required derived misc channels (none for this dataset)
_REQUIRED_DERIVED_MISC: List[str] = []


# ============================================================================
# HELPERS
# ============================================================================

def _extract_subject_id(row) -> str:
    """Extract subject ID from BIDS file path."""
    file_path = row.get("File Path", "")
    
    # BIDS format: sub-01, sub-02, etc.
    match = re.search(r'sub-(\d+)', file_path, re.IGNORECASE)
    if match:
        return match.group(1).zfill(2)
    
    return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given data file."""
    # BIDS structure: sub-XX/[ses-YY/]eeg/sub-XX_task-YY_run-ZZ_eeg.set
    # events.tsv should be: sub-XX/[ses-YY/]eeg/sub-XX_task-YY_run-ZZ_events.tsv
    # or at the subject/session level
    
    base_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Try run-specific events.tsv first
    events_tsv = os.path.join(base_dir, base_name.replace("_eeg", "_events") + ".tsv")
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try without _eeg suffix replacement
    events_tsv = os.path.join(base_dir, base_name + "_events.tsv")
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try subject-level events.tsv
    subject_match = re.search(r'(sub-\d+)', base_name, re.IGNORECASE)
    if subject_match:
        sub_id = subject_match.group(1)
        subject_dir = os.path.join(base_dir, "..")
        subject_events = os.path.join(os.path.normpath(subject_dir), f"{sub_id}_events.tsv")
        if os.path.exists(subject_events):
            return subject_events
    
    # Try task-level pattern
    task_match = re.search(r'(sub-\d+_task-[^_]+(?:_run-\d+)?)', base_name, re.IGNORECASE)
    if task_match:
        events_tsv = os.path.join(base_dir, task_match.group(1) + "_events.tsv")
        if os.path.exists(events_tsv):
            return events_tsv
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv starting from file path and going up."""
    current_dir = os.path.dirname(file_path)
    
    # Search up to 3 levels up
    for _ in range(4):
        participants_tsv = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_tsv):
            return participants_tsv
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    
    return None


def _read_participants_info(participants_tsv: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info: Dict[str, str] = {}
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        
        # Find subject row
        sub_col = None
        for col in df.columns:
            if col.lower() in ["participant_id", "subject_id", "participant id"]:
                sub_col = col
                break
        
        if sub_col is None:
            # Use first column as subject ID
            sub_col = df.columns[0]
        
        # Format subject ID for matching (handle sub-01 vs 01)
        search_ids = [f"sub-{subject_id}", subject_id, subject_id.lstrip("0") or "0"]
        
        subject_row = None
        for search_id in search_ids:
            mask = df[sub_col].astype(str).str.strip() == search_id
            if mask.any():
                subject_row = df[mask].iloc[0]
                break
        
        if subject_row is not None:
            for field in _REQUIRED_INFO_FIELDS:
                if field in df.columns:
                    val = subject_row[field]
                    # Handle missing/NaN values
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val).strip()
                else:
                    info[field] = "unknown"
        else:
            # Subject not found, all unknown
            for field in _REQUIRED_INFO_FIELDS:
                info[field] = "unknown"
                
    except Exception:
        # File read error, all unknown
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    
    return info


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events from events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _events_tsv_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns: onset, (duration), and either trial_type or value
    if "onset" not in events_df.columns:
        return None
    
    # Get durations
    if "duration" in events_df.columns:
        durations = events_df["duration"].fillna(0).values
    else:
        durations = np.zeros(len(events_df))
    
    # Get descriptions
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    else:
        # Try to find any descriptive column
        desc_col = None
        for col in events_df.columns:
            if col not in ["onset", "duration", "sample", "channel"]:
                desc_col = col
                break
        if desc_col is None:
            return None
        descriptions = events_df[desc_col].astype(str).values
    
    # Convert numeric descriptions through event map if needed
    mapped_descriptions = []
    for desc in descriptions:
        desc_str = str(desc).strip()
        # Try to map numeric codes
        try:
            desc_int = int(float(desc_str))
            if desc_int in _EVENT_MAP:
                mapped_descriptions.append(_EVENT_MAP[desc_int])
            else:
                mapped_descriptions.append(desc_str)
        except (ValueError, TypeError):
            # Already a string, keep as-is but ensure S-style format
            mapped_descriptions.append(desc_str)
    
    # Filter out empty descriptions
    valid_mask = [d and str(d).lower() != "nan" for d in mapped_descriptions]
    if not any(valid_mask):
        return None
    
    onsets = events_df["onset"].values[valid_mask]
    durations = durations[valid_mask] if len(durations) == len(valid_mask) else durations[np.array(valid_mask)]
    mapped_descriptions = [d for d, v in zip(mapped_descriptions, valid_mask) if v]
    
    # Ensure durations array matches
    if len(durations) != len(onsets):
        durations = np.zeros(len(onsets))
    
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations.tolist() if hasattr(durations, 'tolist') else list(durations),
        description=mapped_descriptions,
    )
    
    return annotations


def _has_native_events(raw: mne.io.BaseRaw) -> bool:
    """Check if raw file already has meaningful events/annotations."""
    # Check annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Check if annotations are meaningful (not just boundary)
        non_boundary = [d for d in raw.annotations.description if d.lower() != "boundary"]
        if len(non_boundary) > 0:
            return True
    
    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
    if len(stim_picks) > 0:
        return True
    
    return False


@dataclass
class OpenNeuroDS004022Kernel:
    """Stage1 kernel for OpenNeuro ds004022 dataset."""

    KERNEL_ID: str = "openneuro-ds004022-stage1"
    kernel_requirements: Dict[str, Any] = None

    def __post_init__(self):
        self.kernel_requirements = {
            "required_event_ids": ["S 10", "S 2", "S 3", "S 4", "S 5", "S 6", "S 7", "S 8", "S 9"],
            "required_info_fields": _REQUIRED_INFO_FIELDS,
            "required_native_misc": _REQUIRED_NATIVE_MISC,
            "derived_misc_channels": _REQUIRED_DERIVED_MISC,
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _extract_subject_id(row)
        
        # =====================================================================
        # 1. CHANNEL RENAMING (before set_montage)
        # =====================================================================
        
        # EEGLAB .set files may have channel names that need standardization
        rename_map: Dict[str, str] = {}
        
        # Map common non-standard names to standard 10-20
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper().strip()
            
            # Handle EGI/numbered channel formats
            if ch_name.startswith("E") and ch_name[1:].isdigit():
                # EGI HydroCel Geodesic Sensor Net mapping for 18 channels
                # Source: dataset documentation, standard EGI 32-channel layout
                # Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
                egi_map = {
                    "E2": "Fz", "E3": "F3", "E4": "F4",
                    "E5": "FC3", "E6": "FCz", "E7": "FC4",
                    "E8": "C3", "E9": "Cz", "E10": "C4",
                    "E11": "CP3", "E12": "CPz", "E13": "CP4",
                    "E14": "P3", "E15": "Pz", "E16": "P4",
                    "E17": "O1", "E18": "Oz", "E19": "O2",
                }
                if ch_name in egi_map:
                    rename_map[ch_name] = egi_map[ch_name]
            
            # Handle generic EEG-XX format
            elif re.match(r'^EEG[-_]?\d+$', ch_name, re.IGNORECASE):
                num_match = re.search(r'\d+', ch_name)
                if num_match:
                    idx = int(num_match.group())
                    if 0 <= idx < len(_ACTIVE_EEG_CHANNELS_18):
                        rename_map[ch_name] = _ACTIVE_EEG_CHANNELS_18[idx]
            
            # Handle lowercase variants
            elif ch_name.lower() in [c.lower() for c in _ACTIVE_EEG_CHANNELS_18]:
                std_name = next(c for c in _ACTIVE_EEG_CHANNELS_18 if c.lower() == ch_name.lower())
                if ch_name != std_name:
                    rename_map[ch_name] = std_name
        
        # Apply rename if any mappings found
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Ensure we have the expected 18 channels; if more, select subset
        current_ch_names = set(raw.ch_names)
        expected_ch_names = set(_ACTIVE_EEG_CHANNELS_18)
        
        if expected_ch_names.issubset(current_ch_names):
            # Pick only the 18 expected channels
            picks = [raw.ch_names.index(ch) for ch in _ACTIVE_EEG_CHANNELS_18 if ch in raw.ch_names]
            if len(picks) == 18:
                raw = raw.pick(picks)
        
        # =====================================================================
        # 2. SET MONTAGE
        # =====================================================================
        
        # Set standard 10-20 montage for renamed channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage if channels are in the montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            if raw_ch_names.issubset(montage_ch_names) or len(raw_ch_names & montage_ch_names) >= 10:
                raw.set_montage(montage, match_case=False, match_alias=True, on_missing="warn")
        except Exception:
            # Montage setting failed, continue without
            pass
        
        # =====================================================================
        # 3. READ PARTICIPANTS.TSV AND BUILD DESCRIPTION
        # =====================================================================
        
        participants_tsv = _find_participants_tsv(file_path)
        subject_info = _read_participants_info(participants_tsv, subject_id) if participants_tsv else {}
        
        # Default unknowns for missing fields
        for field in _REQUIRED_INFO_FIELDS:
            if field not in subject_info:
                subject_info[field] = "unknown"
        
        # Extract canonical fields
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown").lower()
        if sex not in ["male", "female"]:
            sex = "unknown"
        
        # Hand dominance -> handedness
        handedness = subject_info.get("Hand Dominance", "unknown").lower()
        if handedness in ["right", "r", "right-handed", "right handed"]:
            handedness = "right"
        elif handedness in ["left", "l", "left-handed", "left handed"]:
            handedness = "left"
        elif handedness == "unknown":
            pass  # keep as unknown
        else:
            handedness = "unknown"  # LLM 推断，需人类复核
        
        # Device info from dataset documentation
        # Source: paper 10.1371/journal.pone.0335364, dataset README
        # Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
        amplifier = "unknown"  # Not specified in available documentation
        cap = "unknown"  # Not specified; likely standard Ag/AgCl cap
        
        # Build eegunity_description with required info fields
        eegunity_description = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add required info fields as strings
        for field in _REQUIRED_INFO_FIELDS:
            val = subject_info.get(field, "unknown")
            if field not in eegunity_description:
                eegunity_description[field] = str(val) if val != "unknown" else "unknown"
        
        # Ensure Years Since Diagnosis is included
        if "Years Since Diagnosis" in subject_info:
            eegunity_description["Years Since Diagnosis"] = str(subject_info["Years Since Diagnosis"])
        
        original_desc = raw.info.get("description", "") or ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # =====================================================================
        # 4. EVENTS FROM EVENTS.TSV (if raw lacks meaningful events)
        # =====================================================================
        
        # EEGLAB .set files may have events in the file, but check if meaningful
        needs_events_from_tsv = False
        
        if not _has_native_events(raw):
            needs_events_from_tsv = True
        else:
            # Check if annotations are just boundary markers
            if raw.annotations is not None:
                descs = list(raw.annotations.description)
                non_boundary = [d for d in descs if d.lower() not in ["boundary", ""]]
                if len(non_boundary) == 0:
                    needs_events_from_tsv = True
        
        if needs_events_from_tsv:
            events_tsv = _find_events_tsv(file_path)
            if events_tsv:
                events_df = _read_events_tsv(events_tsv)
                if events_df is not None and len(events_df) > 0:
                    annotations = _events_tsv_to_annotations(events_df, raw.info["sfreq"])
                    if annotations is not None:
                        raw.set_annotations(annotations)
        
        # =====================================================================
        # 5. REMAP ANY NUMERIC ANNOTATIONS TO DESCRIPTIVE STRINGS
        # =====================================================================
        
        if raw.annotations is not None and len(raw.annotations) > 0:
            new_descriptions = []
            needs_update = False
            
            for desc in raw.annotations.description:
                desc_str = str(desc).strip()
                
                # Try numeric mapping
                try:
                    desc_int = int(float(desc_str))
                    if desc_int in _EVENT_MAP:
                        new_descriptions.append(_EVENT_MAP[desc_int])
                        needs_update = True
                    else:
                        new_descriptions.append(desc_str)
                except (ValueError, TypeError):
                    # Already string, check if needs S-prefix formatting
                    if re.match(r'^\d+$', desc_str):
                        # Pure number without S prefix
                        try:
                            desc_int = int(desc_str)
                            if desc_int in _EVENT_MAP:
                                new_descriptions.append(_EVENT_MAP[desc_int])
                                needs_update = True
                            else:
                                new_descriptions.append(desc_str)
                        except ValueError:
                            new_descriptions.append(desc_str)
                    else:
                        new_descriptions.append(desc_str)
            
            if needs_update:
                # Rebuild annotations with mapped descriptions
                raw.set_annotations(mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                ))
        
        # =====================================================================
        # 6. HANDLE MISC CHANNELS (native and derived)
        # =====================================================================
        
        # No required native or derived misc channels for this dataset
        # But ensure any existing misc channels are properly typed
        
        # Check for channels that should be misc
        current_types = raw.get_channel_types()
        misc_fixes = {}
        for ch_name, ch_type in zip(raw.ch_names, current_types):
            # Mark non-EEG channels as misc if they aren't already
            if ch_type not in ["eeg", "misc", "stim"] and not ch_name.upper().startswith("EEG"):
                misc_fixes[ch_name] = "misc"
        
        if misc_fixes:
            raw.set_channel_types(misc_fixes)
        
        # =====================================================================
        # 7. FINAL VALIDATION
        # =====================================================================
        
        # Ensure all channel types are set
        unknown_types = [ch_name for ch_name, ch_type in zip(raw.ch_names, raw.get_channel_types()) 
                        if ch_type == "misc" and ch_name in _ACTIVE_EEG_CHANNELS_18]
        
        # Fix any EEG channels mislabeled as misc
        if unknown_types:
            fix_map = {ch: "eeg" for ch in unknown_types}
            raw.set_channel_types(fix_map)
        
        return raw


KERNEL = OpenNeuroDS004022Kernel()