"""OpenNeuro ds004784 stage1 kernel for EEGUnity.

Dataset: Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts.
264-channel phantom EEG recorded at 512 Hz.
Event codes: 65471 (artifact-on) and 65343 (artifact-off/clean).

This is a BIDS-compliant dataset with participants.tsv and events.tsv sidecars.
The generic BIDS kernel is extended here to handle:
- 264-channel extended montage (non-standard_1020, no montage set)
- Events from BrainVision .eeg + .vmrk or from events.tsv sidecar
- Hardcoded device metadata from dataset documentation

Source: https://openneuro.org/datasets/ds004784
References:
- Kappenman et al. (2021), 10.1109/TNSRE.2020.3000971 (original phantom design)
- Dataset papers in references/

Channel naming: The dataset uses 1-based numbered channels Ch1-Ch264 from the
BrainVision recorder. These are NOT standard 10-20 positions; they represent
a custom high-density montage on the phantom head. No renaming is performed
as standard names are not applicable.

Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# Hardcoded device metadata from dataset documentation and papers
# Source: Kappenman et al. (2021), 10.1109/TNSRE.2020.3000971
# Annotator: LLM 推断，需人类复核
_DEVICE_INFO = {
    "amplifier": "BrainAmp DC",
    "cap": "Ag/AgCl custom phantom cap (264-channel)",
    "handedness": "unknown",  # phantom has no handedness
}


@dataclass
class OpenNeuroDS004784Kernel:
    """Stage1 kernel for OpenNeuro ds004784 (Phantom EEG)."""

    KERNEL_ID: str = "openneuro-ds004784-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- 1. Extract subject info from participants.tsv ---
        # BIDS standard: participants.tsv at dataset root
        dataset_root = self._find_dataset_root(file_path)
        subject_id = self._extract_subject_id(file_path)

        # Default values
        age = "unknown"
        sex = "unknown"

        if dataset_root and subject_id:
            participants_path = os.path.join(dataset_root, "participants.tsv")
            if os.path.exists(participants_path):
                try:
                    participants_df = pd.read_csv(participants_path, sep="\t")
                    # Match subject_id (handle "sub-01" vs "01" variations)
                    sub_match = participants_df[
                        participants_df["participant_id"].str.contains(
                            subject_id.replace("sub-", ""), case=False, na=False
                        ) | participants_df["participant_id"].str.contains(
                            subject_id, case=False, na=False
                        )
                    ]
                    if len(sub_match) == 1:
                        sub_row = sub_match.iloc[0]
                        # Age
                        if "age" in sub_row and pd.notna(sub_row["age"]):
                            age = str(int(sub_row["age"]))
                        # Sex - normalize to lowercase
                        if "sex" in sub_row and pd.notna(sub_row["sex"]):
                            sex_val = str(sub_row["sex"]).strip().lower()
                            if sex_val in ("m", "male"):
                                sex = "male"
                            elif sex_val in ("f", "female"):
                                sex = "female"
                            else:
                                sex = "unknown"
                        elif "gender" in sub_row and pd.notna(sub_row["gender"]):
                            gender_val = str(sub_row["gender"]).strip().lower()
                            if gender_val in ("m", "male"):
                                sex = "male"
                            elif gender_val in ("f", "female"):
                                sex = "female"
                            else:
                                sex = "unknown"
                except Exception:
                    pass  # Keep defaults if parsing fails

        # --- 2. Build eegunity_description ---
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _DEVICE_INFO["amplifier"],
                "cap": _DEVICE_INFO["cap"],
                "handedness": _DEVICE_INFO["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # --- 3. Channel handling ---
        # The dataset uses Ch1-Ch264 naming from BrainVision.
        # These are NOT standard 10-20 positions; no renaming or montage is applied.
        # Verify channel types are correctly set (should be eeg by default from BV)
        # Ensure no channels are mislabeled as stim/misc that should be eeg
        ch_types = raw.get_channel_types()
        for i, (ch_name, ch_type) in enumerate(zip(raw.ch_names, ch_types)):
            # Keep EEG channels as EEG
            if ch_name.startswith("Ch") and ch_type != "eeg":
                raw.set_channel_types({ch_name: "eeg"})

        # --- 4. Event handling: derive from events.tsv if annotations are missing ---
        # BrainVision .eeg files should have events in the .vmrk marker file,
        # which MNE reads automatically. However, if annotations are empty or
        # the marker file is missing, fall back to the events.tsv sidecar.
        has_annotations = (
            raw.annotations is not None and len(raw.annotations) > 0
        )

        if not has_annotations:
            # Try to read events from sidecar events.tsv
            events_tsv_path = self._find_events_tsv(file_path)
            if events_tsv_path and os.path.exists(events_tsv_path):
                try:
                    events_df = pd.read_csv(events_tsv_path, sep="\t")
                    # BIDS events.tsv columns: onset, duration, trial_type, value, ...
                    if len(events_df) > 0 and "onset" in events_df.columns:
                        onsets = events_df["onset"].values.astype(float)
                        # Duration: default to 0 if missing or empty
                        if "duration" in events_df.columns:
                            durations = events_df["duration"].fillna(0).values.astype(float)
                        else:
                            durations = np.zeros(len(events_df))
                        # Description: prefer trial_type, then value, then fallback
                        descriptions = []
                        for _, ev_row in events_df.iterrows():
                            if "trial_type" in ev_row and pd.notna(ev_row["trial_type"]):
                                desc = str(ev_row["trial_type"])
                            elif "value" in ev_row and pd.notna(ev_row["value"]):
                                desc = str(ev_row["value"])
                            else:
                                desc = "event"
                            descriptions.append(desc)

                        annotations = mne.Annotations(
                            onset=onsets,
                            duration=durations.tolist() if hasattr(durations, 'tolist') else list(durations),
                            description=descriptions,
                        )
                        raw.set_annotations(annotations)
                except Exception:
                    pass  # If events.tsv parsing fails, leave as-is

        # --- 5. Final verification of events ---
        # Ensure events are accessible via events_from_annotations
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            # If still no events, try to find a stim channel as last resort
            stim_candidates = [ch for ch in raw.ch_names if "stim" in ch.lower()]
            if stim_candidates:
                try:
                    events = mne.find_events(raw, stim_channel=stim_candidates[0], verbose=False)
                    onsets = events[:, 0] / raw.info["sfreq"]
                    durations = [0.0] * len(events)
                    descriptions = events[:, 2].astype(str)
                    raw.set_annotations(mne.Annotations(onsets, durations, descriptions))
                except Exception:
                    pass  # No events available

        return raw

    def _find_dataset_root(self, file_path: str) -> str | None:
        """Find BIDS dataset root by looking for participants.tsv."""
        current_dir = os.path.dirname(os.path.abspath(file_path))
        # Walk up to find participants.tsv
        for _ in range(10):  # Limit search depth
            if os.path.exists(os.path.join(current_dir, "participants.tsv")):
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                break
            current_dir = parent
        return None

    def _extract_subject_id(self, file_path: str) -> str | None:
        """Extract subject ID from BIDS file path."""
        # Typical pattern: sub-01/eeg/sub-01_task-rest_eeg.eeg
        basename = os.path.basename(file_path)
        parts = basename.split("_")
        if parts and parts[0].startswith("sub-"):
            return parts[0]
        # Try from directory structure
        for part in os.path.normpath(file_path).split(os.sep):
            if part.startswith("sub-"):
                return part
        return None

    def _find_events_tsv(self, file_path: str) -> str | None:
        """Find corresponding events.tsv sidecar for a given EEG file."""
        # BIDS naming: sub-XX_task-YY_eeg.eeg -> sub-XX_task-YY_events.tsv
        base = os.path.splitext(file_path)[0]  # Remove .eeg
        # Handle common BIDS suffixes
        for suffix in ["_eeg", "_meg", "_ieeg"]:
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        events_tsv = base + "_events.tsv"
        if os.path.exists(events_tsv):
            return events_tsv

        # Also check in same directory with pattern matching
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        # Extract subject and task for pattern matching
        parts = base_name.split("_")
        if len(parts) >= 2:
            sub_task = "_".join(parts[:2])  # e.g., "sub-01_task-rest"
            for f in os.listdir(dir_name) if os.path.isdir(dir_name) else []:
                if f.startswith(sub_task) and f.endswith("_events.tsv"):
                    return os.path.join(dir_name, f)

        return None


KERNEL = OpenNeuroDS004784Kernel()