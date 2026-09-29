"""OpenNeuro ds004147 stage1 kernel for EEGUnity.

BIDS-compliant dataset: Casinos reinforcement learning task.
- 12 subjects, EEG recorded during cue-response learning with feedback
- Events stored in *_events.tsv sidecars; raw BrainVision .eeg files may not carry annotations
- Required event IDs include Stimulus/S codes for cues and feedback
- Derived misc channel: trial_onset_time from events.tsv:onset

Source: https://openneuro.org/datasets/ds004147
DOI: https://doi.org/10.18112/openneuro.ds004147.v1.0.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "handedness", "order", "sex", "stimuli"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["trial_onset_time"]


def _find_events_tsv(file_path: str) -> str | None:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX[_ses-YY]_task-ZZ[_run-WW]_eeg.<ext>
    # events: sub-XX[_ses-YY]_task-ZZ[_run-WW]_events.tsv
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".vmrk", "").replace(".edf", "").replace(".bdf", "").replace(".set", "").replace(".fif", "")
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try without run entity
    import re
    # Remove _run-XX from path
    base_no_run = re.sub(r'_run-\d+', '', base)
    events_tsv_no_run = base_no_run + "_events.tsv"
    if os.path.exists(events_tsv_no_run):
        return events_tsv_no_run
    
    # Search in same directory
    dir_path = os.path.dirname(file_path)
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> str | None:
    """Find participants.tsv going up from file directory."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id(file_path: str) -> str | None:
    """Extract subject ID from BIDS filename."""
    import re
    match = re.search(r'(sub-[a-zA-Z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


@dataclass
class OpenNeuroDS004147Kernel:
    """Stage1 kernel for OpenNeuro ds004147 (Casinos task)."""

    KERNEL_ID: str = "openneuro-ds004147-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- Channel renaming to standard 10-20 ---
        # BrainVision files may have numbered or non-standard names
        # Standard 10-20 channel names for this dataset
        # Source: BrainVision standard cap, 64 channels
        _STANDARD_1020_CHANNELS = [
            "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
            "T7", "C3", "Cz", "C4", "T8", "TP9", "CP5", "CP1", "CP2", "CP6", "TP10",
            "P7", "P3", "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
            "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6", "FT9", "FT7", "FC3",
            "FC4", "FT8", "FT10", "C5", "C1", "C2", "C6", "TP7", "CP3", "CPz", "CP4",
            "TP8", "P5", "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
        ]
        rename_map = {}
        for i, ch_name in enumerate(raw.ch_names):
            # Skip non-EEG channels
            if ch_name.upper() in ["EOG1", "EOG2", "ECG", "EMG", "STIM", "STATUS", "TRIGGER"]:
                continue
            # Try to match to standard names
            if ch_name in _STANDARD_1020_CHANNELS:
                continue  # Already standard
            # Common BrainVision patterns: EEG 0, EEG_0, 0, etc.
            clean_name = ch_name.replace("EEG", "").replace("_", "").replace(" ", "").strip()
            try:
                idx = int(clean_name)
                if 0 <= idx < len(_STANDARD_1020_CHANNELS):
                    rename_map[ch_name] = _STANDARD_1020_CHANNELS[idx]
            except ValueError:
                # Try direct match with case variations
                for std_name in _STANDARD_1020_CHANNELS:
                    if ch_name.upper() == std_name.upper() and ch_name != std_name:
                        rename_map[ch_name] = std_name
                        break
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if we have standard channel names now
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            pass  # Non-standard cap or missing positions, skip per rulebook

        # --- Read participants.tsv for subject info ---
        subject_id = _extract_subject_id(file_path)
        participants_tsv = _find_participants_tsv(file_path)
        
        info_fields = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
        
        if participants_tsv and subject_id:
            try:
                participants_df = pd.read_csv(participants_tsv, sep="\t")
                # Find row for this subject
                sub_row = participants_df[participants_df["participant_id"] == subject_id]
                if len(sub_row) == 0:
                    # Try without "sub-" prefix
                    sub_id_clean = subject_id.replace("sub-", "")
                    sub_row = participants_df[participants_df["participant_id"] == sub_id_clean]
                if len(sub_row) == 0:
                    # Try with "sub-" prefix
                    sub_row = participants_df[participants_df["participant_id"] == f"sub-{sub_id_clean}"]
                
                if len(sub_row) > 0:
                    for field in _REQUIRED_INFO_FIELDS:
                        if field in sub_row.columns:
                            val = sub_row[field].values[0]
                            if pd.notna(val):
                                info_fields[field] = str(val).strip()
                            else:
                                info_fields[field] = "unknown"
                        else:
                            info_fields[field] = "unknown"
            except Exception:
                pass  # Keep defaults
        
        # Normalize sex to lowercase
        sex_val = info_fields.get("sex", "unknown").lower()
        if sex_val in ["m", "male"]:
            info_fields["sex"] = "male"
        elif sex_val in ["f", "female"]:
            info_fields["sex"] = "female"
        else:
            info_fields["sex"] = "unknown"
        
        # Normalize age to string
        age_val = info_fields.get("age", "unknown")
        try:
            # Try to extract numeric age
            age_float = float(age_val)
            if age_float > 0:
                info_fields["age"] = str(int(age_float))
            else:
                info_fields["age"] = "unknown"
        except ValueError:
            # Keep as-is if it's a range or already string
            if age_val == "unknown":
                info_fields["age"] = "unknown"
            # else keep the string value (e.g., "22-45")
        
        # --- Write eegunity_description ---
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_desc = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": info_fields.get("age", "unknown"),
                "sex": info_fields.get("sex", "unknown"),
                "amplifier": "BrainAmp",  # inferred by LLM, needs human review - typical for this dataset
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review - standard BrainVision cap
                "handedness": info_fields.get("handedness", "unknown"),
            }
        }
        
        # Add extra required info fields
        for field in _REQUIRED_INFO_FIELDS:
            if field not in ["age", "sex", "handedness"]:
                eegunity_desc["eegunity_description"][field] = info_fields.get(field, "unknown")
        
        raw.info["description"] = json.dumps(eegunity_desc)

        # --- Read events.tsv and create annotations ---
        # CRITICAL FIX: BrainVision .eeg files in this dataset do NOT carry their own
        # annotations/triggers. Events MUST come from the sibling *_events.tsv files.
        # The events.tsv contains onset (seconds), duration, sample, trial_type, and value.
        # We use the 'value' column as the annotation description since it carries the
        # distinguishable trigger labels (e.g., "S 31", "S 32", etc.).
        events_tsv = _find_events_tsv(file_path)
        events_df = None
        
        if events_tsv and os.path.exists(events_tsv):
            try:
                events_df = pd.read_csv(events_tsv, sep="\t")
            except Exception:
                events_df = None
        
        # Create annotations from events.tsv if available
        if events_df is not None and len(events_df) > 0:
            # Build annotations from events.tsv
            onsets = []
            durations = []
            descriptions = []
            
            for _, ev_row in events_df.iterrows():
                # Handle BOM in column names
                onset_col = '\ufeffonset' if '\ufeffonset' in ev_row.index else 'onset'
                duration_col = 'duration'
                value_col = 'value'
                trial_type_col = 'trial_type'
                
                # Get onset in seconds
                try:
                    onset = float(ev_row[onset_col])
                except (KeyError, ValueError):
                    continue
                
                # Get duration in seconds
                try:
                    duration = float(ev_row[duration_col])
                except (KeyError, ValueError):
                    duration = 0.0
                
                # Get description from 'value' column (contains actual trigger codes like "S 31")
                # Fall back to 'trial_type' only if 'value' is missing or n/a
                description = None
                if value_col in ev_row.index:
                    val = ev_row[value_col]
                    if pd.notna(val) and str(val).strip() != 'n/a':
                        description = str(val).strip()
                
                if description is None and trial_type_col in ev_row.index:
                    val = ev_row[trial_type_col]
                    if pd.notna(val) and str(val).strip() != 'n/a':
                        description = str(val).strip()
                
                if description is None:
                    description = "unknown"
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(description)
            
            # Create and set annotations on the raw object
            if len(onsets) > 0:
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=None
                )
                raw.set_annotations(annotations)
        
        # --- Create derived misc channel: trial_onset_time from events.tsv ---
        # This channel contains the onset times of all events for this recording
        if events_df is not None and len(events_df) > 0:
            try:
                onset_col = '\ufeffonset' if '\ufeffonset' in events_df.columns else 'onset'
                trial_onset_times = events_df[onset_col].astype(float).values
                
                # Create a misc channel with trial onset times
                # Pad or truncate to match data length
                n_samples = raw.n_times
                trial_onset_channel = np.full(n_samples, np.nan)
                
                # Place onset times at corresponding sample indices
                sfreq = raw.info['sfreq']
                for onset_time in trial_onset_times:
                    sample_idx = int(round(onset_time * sfreq))
                    if 0 <= sample_idx < n_samples:
                        trial_onset_channel[sample_idx] = onset_time
                
                # Create info for misc channel
                info_misc = mne.create_info(
                    ch_names=['trial_onset_time'],
                    sfreq=sfreq,
                    ch_types=['misc']
                )
                
                # Create RawArray for the misc channel
                raw_misc = mne.io.RawArray(trial_onset_channel.reshape(1, -1), info_misc)
                
                # Add to raw
                raw.add_channels([raw_misc], force_update_info=True)
            except Exception:
                pass  # If derived channel creation fails, continue without it
        
        return raw


KERNEL = OpenNeuroDS004147Kernel()