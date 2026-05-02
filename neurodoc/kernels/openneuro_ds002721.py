"""Dataset-specific kernel for openneuro ds002721.

EEG dataset recorded during affective music listening.
Participants listened to music clips from film scores while their EEG was recorded,
to investigate the neural correlates of music-induced emotional states.

Source: https://openneuro.org/datasets/ds002721
Source: DOI 10.1038/s41597-020-0507-6 (Film Clips dataset)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 10-20 montage for 19 channels
# Source: DOI 10.1038/s41597-020-0507-6 - confirms 19-channel EEG with standard 10-20 layout
# Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
_STANDARD_19_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "O2"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names.

    Source: Standard 10-20 system, common variants in EDF/BIDS exports
    Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
    """
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "Fp 1", "FP1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "Fp 2", "FP2"]),
        ("F7", ["F7", "EEG-F7", "F 7"]),
        ("F3", ["F3", "EEG-F3", "F 3"]),
        ("Fz", ["Fz", "EEG-Fz", "F z", "FZ"]),
        ("F4", ["F4", "EEG-F4", "F 4"]),
        ("F8", ["F8", "EEG-F8", "F 8"]),
        ("T7", ["T7", "EEG-T7", "T 7", "T3", "EEG-T3", "T 3"]),
        ("C3", ["C3", "EEG-C3", "C 3"]),
        ("Cz", ["Cz", "EEG-Cz", "C z", "CZ"]),
        ("C4", ["C4", "EEG-C4", "C 4"]),
        ("T8", ["T8", "EEG-T8", "T 8", "T4", "EEG-T4", "T 4"]),
        ("P7", ["P7", "EEG-P7", "P 7", "T5", "EEG-T5", "T 5"]),
        ("P3", ["P3", "EEG-P3", "P 3"]),
        ("Pz", ["Pz", "EEG-Pz", "P z", "PZ"]),
        ("P4", ["P4", "EEG-P4", "P 4"]),
        ("P8", ["P8", "EEG-P8", "P 8", "T6", "EEG-T6", "T 6"]),
        ("O1", ["O1", "EEG-O1", "O 1"]),
        ("O2", ["O2", "EEG-O2", "O 2"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _read_events_tsv(file_path: str) -> Optional[Dict[str, Any]]:
    """Read events from BIDS events.tsv sidecar file.
    
    Parameters
    ----------
    file_path : str
        Path to the events.tsv file.
        
    Returns
    -------
    dict or None
        Dictionary with 'onset', 'duration', 'description' lists, or None if file not found.
    """
    import pandas as pd

    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path, sep="\t")
        if len(df) == 0:
            return None

        onsets = df["onset"].values.tolist()
        
        # duration column
        if "duration" in df.columns:
            durations = df["duration"].values.tolist()
        else:
            durations = [0.0] * len(df)

        # description: prefer 'trial_type', then 'value', then 'stim_type'
        if "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values.tolist()
        elif "value" in df.columns:
            descriptions = df["value"].astype(str).values.tolist()
        elif "stim_type" in df.columns:
            descriptions = df["stim_type"].astype(str).values.tolist()
        else:
            # fallback: use first non-onset/duration column
            desc_col = None
            for col in df.columns:
                if col not in ("onset", "duration", "sample", "HED"):
                    desc_col = col
                    break
            if desc_col is not None:
                descriptions = df[desc_col].astype(str).values.tolist()
            else:
                descriptions = ["unknown"] * len(df)

        return {
            "onset": onsets,
            "duration": durations,
            "description": descriptions,
        }
    except Exception:
        return None


def _find_events_tsv(eeg_file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for an EEG file.
    
    BIDS convention: same directory, same base name with _events.tsv suffix.
    """
    base = eeg_file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    # Try standard BIDS naming
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try in same directory with matching subject/task
    dir_name = os.path.dirname(eeg_file_path)
    base_name = os.path.basename(eeg_file_path)
    
    # Extract sub-XX and task-YY if present
    import re
    sub_match = re.search(r'(sub-[a-zA-Z0-9]+)', base_name)
    task_match = re.search(r'(task-[a-zA-Z0-9]+)', base_name)
    run_match = re.search(r'(run-[0-9]+)', base_name)
    
    if sub_match and task_match:
        sub = sub_match.group(1)
        task = task_match.group(1)
        run = run_match.group(1) if run_match else None
        
        for fname in os.listdir(dir_name):
            if not fname.endswith("_events.tsv"):
                continue
            if sub in fname and task in fname:
                if run is None or run in fname:
                    return os.path.join(dir_name, fname)
    
    return None


@dataclass
class OpenNeuroDS002721Kernel:
    """Stage1 kernel for OpenNeuro ds002721 (affective music listening)."""

    KERNEL_ID: str = "openneuro-ds002721-stage1"
    kernel_requirements: Dict[str, Any] = None

    def __post_init__(self):
        self.kernel_requirements = {
            "required_event_ids": ['259', '260', '325', '445', '477', '496', '497', '552', '613', '786', '788', '800', '801', '802', '803', '804', '805', '806', '807'],
            "required_info_fields": ["age", "sex"],
            "required_native_misc": [],
            "derived_misc_channels": [],
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- 1. Channel rename to standard 10-20 BEFORE set_montage() ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Set standard 10-20 montage if channels match
        current_ch_names = set(raw.ch_names)
        standard_set = set(_STANDARD_19_CHANNELS)
        if current_ch_names == standard_set or len(current_ch_names.intersection(standard_set)) >= 17:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Pick only channels that exist in both raw and montage
                montage_chs = [ch for ch in raw.ch_names if ch in montage.ch_names]
                if montage_chs:
                    raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # inferred by LLM, needs human review: montage may fail, continue without

        # --- 2. Read participants.tsv for subject info ---
        # Find participants.tsv by walking up from file_path
        participants_path = None
        search_dir = os.path.dirname(file_path)
        for _ in range(5):  # Search up to 5 levels up
            candidate = os.path.join(search_dir, "participants.tsv")
            if os.path.exists(candidate):
                participants_path = candidate
                break
            parent = os.path.dirname(search_dir)
            if parent == search_dir:
                break
            search_dir = parent

        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
        extra_fields: Dict[str, str] = {}

        # Extract subject ID from file path
        import re
        sub_match = re.search(r'(sub-[a-zA-Z0-9]+)', file_path)
        subject_id = sub_match.group(1) if sub_match else None

        if participants_path and subject_id:
            import pandas as pd
            try:
                df_participants = pd.read_csv(participants_path, sep="\t")
                # Find row for this subject
                sub_row = None
                if "participant_id" in df_participants.columns:
                    sub_row = df_participants[df_participants["participant_id"] == subject_id]
                elif "subject_id" in df_participants.columns:
                    sub_row = df_participants[df_participants["subject_id"] == subject_id]
                
                if sub_row is not None and len(sub_row) > 0:
                    sub_row = sub_row.iloc[0]
                    
                    # age
                    if "age" in sub_row:
                        age_val = sub_row["age"]
                        if pd.notna(age_val):
                            subject_info["age"] = str(int(float(age_val)))
                    
                    # sex
                    if "sex" in sub_row:
                        sex_val = sub_row["sex"]
                        if pd.notna(sex_val):
                            sex_str = str(sex_val).strip().lower()
                            if sex_str in ("m", "male"):
                                subject_info["sex"] = "male"
                            elif sex_str in ("f", "female"):
                                subject_info["sex"] = "female"
                            else:
                                subject_info["sex"] = "unknown"
                    
                    # handedness if available
                    if "handedness" in sub_row:
                        hand_val = sub_row["handedness"]
                        if pd.notna(hand_val):
                            hand_str = str(hand_val).strip().lower()
                            if hand_str in ("r", "right"):
                                subject_info["handedness"] = "right"
                            elif hand_str in ("l", "left"):
                                subject_info["handedness"] = "left"
                    
                    # required_info_fields: collect all listed columns as strings
                    for field in self.kernel_requirements.get("required_info_fields", []):
                        if field in sub_row and field not in ("age", "sex", "handedness"):
                            val = sub_row[field]
                            if pd.notna(val):
                                extra_fields[field] = str(val)
                            else:
                                extra_fields[field] = "unknown"
            except Exception:
                pass  # inferred by LLM, needs human review: participants.tsv read failed

        # --- 3. Handle events from events.tsv ---
        # Always load events from events.tsv for this dataset; EDF files do not carry triggers
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_data = _read_events_tsv(events_tsv_path)
            if events_data is not None:
                # Create annotations from events.tsv data
                # onset is in seconds, which is what mne.Annotations expects
                annotations = mne.Annotations(
                    onset=events_data["onset"],
                    duration=events_data["duration"],
                    description=events_data["description"],
                    orig_time=raw.annotations.orig_time if raw.annotations else None,
                )
                raw.set_annotations(annotations)

        # --- 4. Build eegunity_description ---
        description = {
            "dataset_name": "ds002721",
            "task": "affective music listening",
            "sampling_frequency": raw.info["sfreq"],
            "n_channels": len(raw.ch_names),
            "n_samples": raw.n_times,
            "channel_names": raw.ch_names,
            "duration_sec": raw.n_times / raw.info["sfreq"],
            "subject_info": subject_info,
            "extra_fields": extra_fields,
            "events_source": "events.tsv" if (events_tsv_path and events_data is not None) else "raw",
            "n_events": len(raw.annotations) if raw.annotations else 0,
        }

        # Store description in raw.info['description'] as JSON
        raw.info["description"] = json.dumps(description)

        return raw


KERNEL = OpenNeuroDS002721Kernel()