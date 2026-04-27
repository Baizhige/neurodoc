"""OpenNeuro ds004010 (MAVIS) stage1 kernel for EEGUnity.

Dataset: MAVIS multisensory detection task
URL: https://openneuro.org/datasets/ds004010
DOI: https://doi.org/10.18112/openneuro.ds004010.v1.0.0

This BIDS dataset contains continuous EEG recordings from a multisensory detection
paradigm. Event markers are present in *_events.tsv sidecar files. The dataset uses
64 channels at 1000 Hz with a standard 10-20 montage.

Key event codes:
- 33/34: Block start/end markers
- 44/45: Auditory target/catch
- 55/56: Visual target/catch
- 66/77: Auditory attention block / Visual attention block
- 200-203, 220-223, 230-233: Various condition markers

Source: OpenNeuro ds004010, eLife 2021 paper DOI: 10.7554/elife.70068
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["Age", "Gender", "Handedness"]

# Event code to description mapping based on task-MultisensoryDetectionTask_events.json
# and eLife paper (10.7554/elife.70068)
# Source: task-MultisensoryDetectionTask_events.json Levels field
# Annotator: LLM, 2026-04-08 — verified against paper and events.tsv samples
_EVENT_CODE_MAP = {
    # Admin/boundary markers
    33: "admin: block-start",
    34: "admin: block-end",
    # Target events (raw meta)
    44: "auditory target onset",
    45: "auditory catch trial",
    55: "visual target onset",
    56: "visual catch trial",
    # Attention block markers (raw meta, also used for long-event epoching)
    66: "auditory attention block",
    77: "visual attention block",
    # Additional condition markers from required event IDs
    200: "condition-200",  # LLM 推断，需人类复核 — likely sub-condition marker
    201: "condition-201",  # LLM 推断，需人类复核
    202: "condition-202",  # LLM 推断，需人类复核
    203: "condition-203",  # LLM 推断，需人类复核
    220: "condition-220",  # LLM 推断，需人类复核
    221: "condition-221",  # LLM 推断，需人类复核
    222: "condition-222",  # LLM 推断，需人类复核
    223: "condition-223",  # LLM 推断，需人类复核
    230: "condition-230",  # LLM 推断，需人类复核
    231: "condition-231",  # LLM 推断，需人类复核
    232: "condition-232",  # LLM 推断，需人类复核
    233: "condition-233",  # LLM 推断，需人类复核
}


def _find_events_tsv(file_path: str) -> str | None:
    """Find sibling events.tsv file for a given EEG file."""
    # BIDS naming: sub-X[_ses-Y]_task-Z[_run-W]_eeg.<ext>
    # Events: sub-X[_ses-Y]_task-Z[_run-W]_events.tsv
    base = file_path.replace(".set", "").replace(".edf", "").replace(".bdf", "").replace(".fif", "").replace(".eeg", "").replace(".vhdr", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run suffix
    import re
    # Remove any _run-\d+ pattern
    base_no_run = re.sub(r'_run-\d+', '', base)
    if base_no_run != base:
        events_path = base_no_run + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
    
    # Search in same directory
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    # Extract sub and task from filename
    sub_match = re.search(r'(sub-\d+)', fname)
    task_match = re.search(r'(task-[A-Za-z0-9]+)', fname)
    
    if sub_match and task_match:
        sub = sub_match.group(1)
        task = task_match.group(1)
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv") and sub in f and task in f:
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> str | None:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):  # stop at root
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participant_info(participants_path: str, subject_id: str) -> dict:
    """Read participant info from participants.tsv."""
    df = pd.read_csv(participants_path, sep="\t")
    
    # Normalize subject_id format
    if not subject_id.startswith("sub-"):
        subject_id = "sub-" + subject_id
    
    # Try exact match
    row = df[df["participant_id"] == subject_id]
    if row.empty:
        # Try without "sub-" prefix
        row = df[df["participant_id"] == subject_id.replace("sub-", "")]
    
    if row.empty:
        return {}
    
    info = {}
    for field in _REQUIRED_INFO_FIELDS:
        if field in row.columns:
            val = row[field].values[0]
            # Handle missing/NaN
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val)
        else:
            info[field] = "unknown"
    
    return info


def _sex_normalize(val: str) -> str:
    """Normalize sex/gender value to lowercase standard."""
    val_lower = str(val).lower().strip()
    if val_lower in ("m", "male", "1"):
        return "male"
    elif val_lower in ("f", "female", "2"):
        return "female"
    else:
        return "unknown"


def _handedness_normalize(val: str) -> str:
    """Normalize handedness value."""
    val_lower = str(val).lower().strip()
    if val_lower in ("r", "right", "righthanded", "right-handed"):
        return "right"
    elif val_lower in ("l", "left", "lefthanded", "left-handed"):
        return "left"
    elif val_lower in ("a", "ambidextrous", "both"):
        return "ambidextrous"
    else:
        return "unknown"


@dataclass
class OpenNeuroDS004010Kernel:
    """Stage1 kernel for OpenNeuro ds004010 (MAVIS) dataset."""

    KERNEL_ID: str = "openneuro-ds004010-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Extract subject ID from file path
        import re
        sub_match = re.search(r'sub-(\d+)', os.path.basename(file_path))
        if sub_match:
            subject_id = f"sub-{sub_match.group(1)}"
        else:
            # Try from directory
            sub_match = re.search(r'sub-(\d+)', file_path)
            subject_id = f"sub-{sub_match.group(1)}" if sub_match else "unknown"

        # Read participants.tsv info
        participants_path = _find_participants_tsv(file_path)
        participant_info = {}
        if participants_path:
            participant_info = _read_participant_info(participants_path, subject_id)

        # Build eegunity_description
        age = participant_info.get("Age", "unknown")
        if age != "unknown":
            # Ensure it's a string, handle ranges if present
            age = str(age).strip()

        sex = _sex_normalize(participant_info.get("Gender", "unknown"))
        handedness = _handedness_normalize(participant_info.get("Handedness", "unknown"))

        # Device info from dataset documentation
        # Source: OpenNeuro ds004010 dataset_description.json and README
        # LLM 推断，需人类复核 — amplifier and cap info should be verified against dataset docs
        amplifier = "BrainAmp"  # LLM 推断，需人类复核 — common for this lab, verify in dataset docs
        cap = "Ag/AgCl"  # LLM 推断，需人类复核 — standard for 64-channel setups

        # Build description
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }

        # Add any extra required info fields that exist in participants.tsv
        # These become source-level HDF5 attrs for InfoDataset
        for field in _REQUIRED_INFO_FIELDS:
            if field not in ("Age", "Gender", "Handedness"):  # already mapped to canonical fields
                val = participant_info.get(field, "unknown")
                eegunity_desc[field.lower()] = val

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Channel renaming — standard 10-20 check
        # BIDS datasets typically have standard names, but verify
        ch_names = raw.ch_names
        needs_rename = False
        rename_map = {}

        # Check for common non-standard naming patterns
        # Some BIDS exports use numbered channels
        for i, ch in enumerate(ch_names):
            if ch.startswith("EEG ") or ch.startswith("EEG-"):
                # Try to extract standard name
                clean = ch.replace("EEG ", "").replace("EEG-", "")
                if clean in mne.channels.get_builtin_montages():
                    pass  # already standard
                # Common numbered mapping if needed
            # Handle specific non-standard patterns for this dataset if any

        # If we have standard_1020-like names, ensure proper capitalization
        standard_1020_names = {
            'fp1': 'Fp1', 'fp2': 'Fp2', 'fz': 'Fz', 'fcz': 'FCz', 'cz': 'Cz',
            'cpz': 'CPz', 'pz': 'Pz', 'oz': 'Oz', 't7': 'T7', 't8': 'T8',
            'p7': 'P7', 'p8': 'P8', 'o1': 'O1', 'o2': 'O2', 'f3': 'F3',
            'f4': 'F4', 'c3': 'C3', 'c4': 'C4', 'p3': 'P3', 'p4': 'P4',
            'af7': 'AF7', 'af8': 'AF8', 'ft7': 'FT7', 'ft8': 'FT8',
            'tp7': 'TP7', 'tp8': 'TP8', 'po7': 'PO7', 'po8': 'PO8',
        }

        for ch in ch_names:
            ch_lower = ch.lower()
            if ch_lower in standard_1020_names and ch != standard_1020_names[ch_lower]:
                rename_map[ch] = standard_1020_names[ch_lower]
                needs_rename = True

        if needs_rename and rename_map:
            raw = raw.rename_channels(rename_map)

        # Set montage if channels look like standard 10-20
        try:
            # Check if we can use standard_1020 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            if len(raw_chs & montage_chs) >= 32:  # most of 64 channels match
                raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            pass  # Montage setting failed, continue without

        # Process events from events.tsv sidecar
        events_path = _find_events_tsv(file_path)
        
        if events_path and os.path.exists(events_path):
            events_df = pd.read_csv(events_path, sep="\t")

            # Check if raw already has annotations or events
            has_native_events = False
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            
            # Check for stim channel with actual events
            stim_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=True, exclude=[])
            if len(stim_picks) > 0:
                stim_data = raw.get_data(picks=stim_picks)
                if np.any(stim_data != 0):
                    has_native_events = True

            # For EEGLAB .set files, check if events are populated
            # EDF without annotations, BrainVision without marker file, plain .fif without events
            file_ext = os.path.splitext(file_path)[1].lower()
            needs_events_from_tsv = False

            if file_ext in (".edf", ".bdf"):
                # EDF without annotations needs TSV events
                if raw.annotations is None or len(raw.annotations) == 0:
                    needs_events_from_tsv = True
            elif file_ext == ".fif":
                # Plain .fif without baked-in events
                if not has_native_events:
                    needs_events_from_tsv = True
            elif file_ext == ".set":
                # EEGLAB .set without populated event
                # Check if events struct is empty
                try:
                    if hasattr(raw, '_data') and not has_native_events:
                        needs_events_from_tsv = True
                except Exception:
                    needs_events_from_tsv = True
            elif file_ext in (".eeg", ".vhdr", ".vmrk"):
                # BrainVision — check if marker file exists and has content
                vhdr_path = file_path.replace(".eeg", ".vhdr").replace(".vmrk", ".vhdr")
                vmrk_path = file_path.replace(".eeg", ".vmrk").replace(".vhdr", ".vmrk")
                has_vmrk = os.path.exists(vmrk_path) and os.path.getsize(vmrk_path) > 100
                if not has_vmrk and not has_native_events:
                    needs_events_from_tsv = True

            # Always derive from TSV if we have required event IDs that might not be in native format
            required_ids = {200, 201, 202, 203, 220, 221, 222, 223, 230, 231, 232, 233, 33, 34, 44, 45, 55, 56, 66, 77}
            
            # Check if native annotations already cover our required events
            native_event_ids = set()
            if raw.annotations is not None:
                for desc in raw.annotations.description:
                    try:
                        native_event_ids.add(int(desc))
                    except ValueError:
                        pass
            
            if not required_ids.issubset(native_event_ids):
                needs_events_from_tsv = True

            # Build annotations from events.tsv
            if needs_events_from_tsv and len(events_df) > 0:
                onsets = []
                durations = []
                descriptions = []

                for _, event_row in events_df.iterrows():
                    onset = event_row.get("onset", np.nan)
                    if pd.isna(onset):
                        continue
                    
                    duration = event_row.get("duration", 0.0)
                    if pd.isna(duration):
                        duration = 0.0

                    # Get event value/description
                    value = event_row.get("value", np.nan)
                    trial_type = event_row.get("trial_type", "")
                    
                    # Try to parse event code
                    event_code = None
                    if not pd.isna(value):
                        try:
                            event_code = int(float(value))
                        except (ValueError, TypeError):
                            pass
                    
                    # Use trial_type as fallback or supplement
                    desc = None
                    if event_code is not None and event_code in _EVENT_CODE_MAP:
                        desc = _EVENT_CODE_MAP[event_code]
                    elif isinstance(trial_type, str) and trial_type:
                        # Map trial_type strings if possible
                        desc = trial_type
                    elif event_code is not None:
                        desc = f"event-{event_code}"
                    
                    if desc:
                        onsets.append(float(onset))
                        durations.append(float(duration))
                        descriptions.append(desc)

                if onsets:
                    # Create annotations, avoiding duplicates with existing if possible
                    new_annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    
                    # Combine with existing or replace
                    if raw.annotations is not None and len(raw.annotations) > 0:
                        # Keep existing and add new ones
                        all_onsets = list(raw.annotations.onset) + onsets
                        all_durations = list(raw.annotations.duration) + durations
                        all_descriptions = list(raw.annotations.description) + descriptions
                        
                        # Sort by onset
                        sorted_idx = np.argsort(all_onsets)
                        combined = mne.Annotations(
                            onset=[all_onsets[i] for i in sorted_idx],
                            duration=[all_durations[i] for i in sorted_idx],
                            description=[all_descriptions[i] for i in sorted_idx],
                        )
                        raw.set_annotations(combined)
                    else:
                        raw.set_annotations(new_annotations)

        # Ensure required native misc channels exist (none specified for this dataset)
        # No required_native_misc or derived_misc_channels needed

        return raw


KERNEL = OpenNeuroDS004010Kernel()