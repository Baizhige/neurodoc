"""Dataset-specific kernel for openneuro ds002721.

EEG dataset recorded during affective music listening.
Participants listened to music clips from film scores while their EEG was recorded.

Source: https://openneuro.org/datasets/ds002721
Source: DOI 10.1038/s41597-020-0507-6 (Film Clips dataset)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne
import numpy as np


# Admin/system markers to exclude from target events
_ADMIN_EVENTS = {32768, 257, 1092, 33575, 901}

# Standard 10-20 montage for 19 channels (typical for music EEG studies)
# Source: DOI 10.1038/s41597-020-0507-6 - confirms 19-channel EEG
# Annotator: LLM, 2026-04-08
_STANDARD_19_CHANNELS = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T3", "C3", "Cz", "C4", "T4",
    "T5", "P3", "Pz", "P4", "T6",
    "O1", "O2"
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names.

    Source: Standard 10-20 system
    Annotator: LLM, 2026-04-08
    """
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "Fp 1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "Fp 2"]),
        ("F7", ["F7", "EEG-F7", "F 7"]),
        ("F3", ["F3", "EEG-F3", "F 3"]),
        ("Fz", ["Fz", "EEG-Fz", "F z"]),
        ("F4", ["F4", "EEG-F4", "F 4"]),
        ("F8", ["F8", "EEG-F8", "F 8"]),
        ("T3", ["T3", "EEG-T3", "T 3", "T7"]),
        ("C3", ["C3", "EEG-C3", "C 3"]),
        ("Cz", ["Cz", "EEG-Cz", "C z"]),
        ("C4", ["C4", "EEG-C4", "C 4"]),
        ("T4", ["T4", "EEG-T4", "T 4", "T8"]),
        ("T5", ["T5", "EEG-T5", "T 5", "P7"]),
        ("P3", ["P3", "EEG-P3", "P 3"]),
        ("Pz", ["Pz", "EEG-Pz", "P z"]),
        ("P4", ["P4", "EEG-P4", "P 4"]),
        ("T6", ["T6", "EEG-T6", "T 6", "P8"]),
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
        durations = df.get("duration", [0.0] * len(df)).values.tolist() if "duration" in df.columns else [0.0] * len(df)

        # Build descriptions from trial_type column (literal strings, no remapping per HC-5)
        descriptions = []
        for idx, row in df.iterrows():
            if "trial_type" in df.columns and pd.notna(row.get("trial_type")):
                # Use literal string from trial_type column
                descriptions.append(str(row["trial_type"]))
            elif "value" in df.columns and pd.notna(row.get("value")):
                descriptions.append(str(row["value"]))
            else:
                descriptions.append("unknown")

        return {
            "onset": onsets,
            "duration": durations,
            "description": descriptions,
        }
    except Exception:
        return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Path to the BIDS dataset root.
    subject_id : str
        Subject identifier (e.g., "sub-01").

    Returns
    -------
    dict
        Dictionary with age, sex, and any other fields.
    """
    import pandas as pd

    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {"age": "unknown", "sex": "unknown", "amplifier": "unknown", "cap": "unknown", "handedness": "unknown"}

    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id
        subj_row = df[df["participant_id"] == subject_id]
        if len(subj_row) == 0:
            return {"age": "unknown", "sex": "unknown", "amplifier": "unknown", "cap": "unknown", "handedness": "unknown"}

        row = subj_row.iloc[0]

        # Extract age
        age = "unknown"
        if "age" in row and pd.notna(row["age"]):
            age = str(int(float(row["age"])))

        # Extract sex
        sex = "unknown"
        if "sex" in row and pd.notna(row["sex"]):
            sex = str(row["sex"])

        # Extract amplifier
        amplifier = "unknown"
        if "amplifier" in row and pd.notna(row["amplifier"]):
            amplifier = str(row["amplifier"])

        # Extract cap
        cap = "unknown"
        if "cap" in row and pd.notna(row["cap"]):
            cap = str(row["cap"])

        # Extract handedness
        handedness = "unknown"
        if "handedness" in row and pd.notna(row["handedness"]):
            handedness = str(row["handedness"])

        return {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
    except Exception:
        return {"age": "unknown", "sex": "unknown", "amplifier": "unknown", "cap": "unknown", "handedness": "unknown"}


@dataclass
class OpenneuroDs002721Kernel:
    """Kernel for OpenNeuro ds002721 - Affective Music Listening EEG."""

    KERNEL_ID: str = "openneuro_ds002721"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get dataset path and subject info
        dataset_path = getattr(udataset, "dataset_path", "")
        subject_id = str(row.get("sub_id", "unknown"))

        # Read participants info
        participant_info = _read_participants_info(dataset_path, subject_id)

        # Build description
        original_description = raw.info.get("description", "") or ""
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": participant_info,
        })

        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw = raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass

        # Load events from BIDS events.tsv sidecar file
        # EDF files in this dataset have no native triggers; events must come from events.tsv
        file_path = str(row.get("file_path", ""))
        if file_path:
            # Try multiple strategies to find the events.tsv sidecar
            events_tsv_path = None
            
            # Strategy 1: Standard BIDS sidecar in same directory
            edf_dir = os.path.dirname(file_path)
            edf_basename = os.path.basename(file_path)
            
            # BIDS naming: sub-XX_task-YY_run-Z_eeg.edf -> sub-XX_task-YY_run-Z_events.tsv
            if "_eeg.edf" in edf_basename:
                bids_events_name = edf_basename.replace("_eeg.edf", "_events.tsv")
            else:
                bids_events_name = edf_basename.replace(".edf", "_events.tsv")
            
            candidate_path = os.path.join(edf_dir, bids_events_name)
            if os.path.exists(candidate_path):
                events_tsv_path = candidate_path
            
            # Strategy 2: Look in parent directory (some BIDS layouts put events one level up)
            if events_tsv_path is None:
                parent_dir = os.path.dirname(edf_dir)
                if parent_dir:
                    candidate_path = os.path.join(parent_dir, bids_events_name)
                    if os.path.exists(candidate_path):
                        events_tsv_path = candidate_path
            
            # Strategy 3: Direct replacement on full path
            if events_tsv_path is None:
                base_path = file_path.replace("_eeg.edf", "").replace(".edf", "")
                candidate_path = base_path + "_events.tsv"
                if os.path.exists(candidate_path):
                    events_tsv_path = candidate_path
            
            # Strategy 4: Search for any _events.tsv in the same directory with matching subject/task
            if events_tsv_path is None:
                import re
                # Extract subject and task from filename
                sub_match = re.search(r'(sub-[^_]+)', edf_basename)
                task_match = re.search(r'(task-[^_]+)', edf_basename)
                run_match = re.search(r'(run-[^_]+)', edf_basename)
                
                if os.path.exists(edf_dir):
                    for fname in os.listdir(edf_dir):
                        if fname.endswith('_events.tsv'):
                            # Check if subject and task match
                            sub_ok = (sub_match is None) or (sub_match.group(1) in fname)
                            task_ok = (task_match is None) or (task_match.group(1) in fname)
                            run_ok = (run_match is None) or (run_match.group(1) in fname)
                            if sub_ok and task_ok and run_ok:
                                candidate_path = os.path.join(edf_dir, fname)
                                if os.path.exists(candidate_path):
                                    events_tsv_path = candidate_path
                                    break
            
            # Read and apply events if found
            if events_tsv_path is not None:
                events_data = _read_events_tsv(events_tsv_path)
                
                if events_data is not None:
                    # Create MNE Annotations from events.tsv data
                    # onset is in seconds per BIDS spec
                    annotations = mne.Annotations(
                        onset=events_data["onset"],
                        duration=events_data["duration"],
                        description=events_data["description"],
                    )
                    raw = raw.set_annotations(annotations)

        return raw


KERNEL = OpenneuroDs002721Kernel()