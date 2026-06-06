"""Dataset-specific kernel for openneuro ds004448 (BMI-HDEEG dataset 4).

High-density EEG motor imagery dataset with 130 channels, 1000 Hz sampling rate.
Participants performed sensorimotor rhythm-based BCI with two-class motor imagery
(left hand vs right hand) and relaxation/rest periods.

BIDS-compliant dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds004448 | DOI: 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv (must be exposed in eegunity_description)
_REQUIRED_INFO_FIELDS = ["age", "sex", "handedness", "amplifier", "cap"]

# Required native misc channels (already in raw data, ensure type is 'misc')
_REQUIRED_NATIVE_MISC = []

# Required derived misc channels (kernel must create)
_REQUIRED_DERIVED_MISC = ["trial_index"]


# Source: dataset_document/openneuro_ds004448/analysis.md and public BIDS
# events.tsv sidecars. Sidecar onsets are stored in milliseconds.
# Annotator: human, 2026-06-04
_RAW_META = {
    "event_1": "Trial phase onset: Trial start",
}

_EVENT_HINTS = {
    event_id: {
        "type": "event",
        "meta_level": "raw",
        "meaning": meaning,
    }
    for event_id, meaning in _RAW_META.items()
}


def _get_file_path(row) -> str:
    if hasattr(row, "get"):
        for key in ("File Path", "file_path", "path"):
            value = row.get(key)
            if value:
                return str(value)
    return str(row)


def _event_onset_seconds(value) -> float:
    onset = float(value)
    return onset / 1000.0 if onset > 1000.0 else onset


def _event_description(value) -> str:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return ""
    if not np.isfinite(numeric_value) or not numeric_value.is_integer():
        return ""
    event_id = f"event_{int(numeric_value)}"
    return event_id if event_id in _RAW_META else ""


class OpenNeuroDS004448Kernel:
    """Stage1 kernel for OpenNeuro ds004448 (BMI-HDEEG dataset 4)."""

    KERNEL_ID: str = "openneuro-ds004448-stage1"
    required_info_fields = list(_REQUIRED_INFO_FIELDS)
    raw_meta = dict(_RAW_META)
    super_meta = {}

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)

        # Ensure data is preloaded before adding channels
        if not raw.preload:
            raw.load_data()

        # ------------------------------------------------------------------
        # 1. Extract subject ID from file path for participants.tsv lookup
        # ------------------------------------------------------------------
        subject_match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
        if subject_match:
            subject_id = f"sub-{subject_match.group(1)}"
        else:
            subject_id = None

        # ------------------------------------------------------------------
        # 2. Read participants.tsv for subject metadata
        # ------------------------------------------------------------------
        dataset_root = os.path.dirname(os.path.dirname(file_path))  # Go up from sub-XX/eeg/
        # Handle case where file is deeper in BIDS hierarchy
        temp_path = file_path
        for _ in range(5):  # Search up to 5 levels
            potential_root = os.path.dirname(temp_path)
            participants_path = os.path.join(potential_root, "participants.tsv")
            if os.path.exists(participants_path):
                dataset_root = potential_root
                break
            temp_path = potential_root

        participants_path = os.path.join(dataset_root, "participants.tsv")
        participant_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
        }

        if os.path.exists(participants_path) and subject_id:
            try:
                participants_df = pd.read_csv(participants_path, sep="\t")
                # Find matching row
                if "participant_id" in participants_df.columns:
                    subj_row = participants_df[participants_df["participant_id"] == subject_id]
                    if len(subj_row) == 0:
                        # Try without 'sub-' prefix
                        subj_row = participants_df[participants_df["participant_id"] == subject_match.group(1) if subject_match else ""]

                    if len(subj_row) > 0:
                        subj_data = subj_row.iloc[0]

                        # Age
                        if "age" in subj_data:
                            age_val = subj_data["age"]
                            if pd.notna(age_val):
                                participant_info["age"] = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)

                        # Sex (prefer 'sex', fallback to 'gender')
                        sex_val = None
                        if "sex" in subj_data and pd.notna(subj_data["sex"]):
                            sex_val = str(subj_data["sex"]).strip().lower()
                        elif "gender" in subj_data and pd.notna(subj_data["gender"]):
                            sex_val = str(subj_data["gender"]).strip().lower()

                        if sex_val:
                            if sex_val in ["m", "male"]:
                                participant_info["sex"] = "male"
                            elif sex_val in ["f", "female"]:
                                participant_info["sex"] = "female"
                            else:
                                participant_info["sex"] = sex_val

                        # Handedness
                        if "handedness" in subj_data and pd.notna(subj_data["handedness"]):
                            hand_val = str(subj_data["handedness"]).strip().lower()
                            if hand_val in ["r", "right"]:
                                participant_info["handedness"] = "right"
                            elif hand_val in ["l", "left"]:
                                participant_info["handedness"] = "left"
                            else:
                                participant_info["handedness"] = hand_val

                        # Amplifier
                        if "amplifier" in subj_data and pd.notna(subj_data["amplifier"]):
                            participant_info["amplifier"] = str(subj_data["amplifier"])
                        elif "amplifier_type" in subj_data and pd.notna(subj_data["amplifier_type"]):
                            participant_info["amplifier"] = str(subj_data["amplifier_type"])

                        # Cap
                        if "cap" in subj_data and pd.notna(subj_data["cap"]):
                            participant_info["cap"] = str(subj_data["cap"])
                        elif "cap_type" in subj_data and pd.notna(subj_data["cap_type"]):
                            participant_info["cap"] = str(subj_data["cap_type"])
                        elif "cap_model" in subj_data and pd.notna(subj_data["cap_model"]):
                            participant_info["cap"] = str(subj_data["cap_model"])
            except Exception:
                pass  # Keep defaults if reading fails

        # ------------------------------------------------------------------
        # 3. Load events from BIDS events.tsv sidecar
        # ------------------------------------------------------------------
        # EDF files in this dataset have no native annotations/triggers.
        # Events MUST come from the sibling events.tsv file.
        events_tsv_path = file_path.replace("_eeg.edf", "_events.tsv")
        if not os.path.exists(events_tsv_path):
            # Try alternative naming patterns
            base = file_path.replace("_eeg.edf", "")
            for suffix in ["_events.tsv", "_eeg_events.tsv"]:
                alt_path = base + suffix
                if os.path.exists(alt_path):
                    events_tsv_path = alt_path
                    break

        # Build annotations from events.tsv and create trial_index misc channel
        onsets = []
        durations = []
        descriptions = []
        trial_index_data = np.zeros((1, len(raw.times)))
        trial_index_available = False
        
        if os.path.exists(events_tsv_path):
            try:
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                sfreq = raw.info["sfreq"]

                # Check if 'trial' column exists for trial_index derived misc channel
                has_trial_col = "trial" in events_df.columns

                for idx, ev in events_df.iterrows():
                    onset_sec = _event_onset_seconds(ev["onset"])
                    duration_sec = float(ev["duration"]) if "duration" in ev and pd.notna(ev["duration"]) else 0.0
                    
                    desc = _event_description(ev.get("value"))
                    if not desc:
                        continue
                    
                    onsets.append(onset_sec)
                    durations.append(duration_sec)
                    descriptions.append(desc)
                    
                    # Fill trial_index channel from 'trial' column if available
                    if has_trial_col and "trial" in ev and pd.notna(ev["trial"]):
                        trial_index_available = True
                        trial_val = float(ev["trial"])
                        start_sample = int(round(onset_sec * sfreq))
                        if start_sample < len(raw.times):
                            end_sample = min(int(round((onset_sec + duration_sec) * sfreq)), len(raw.times))
                            trial_index_data[0, start_sample:end_sample] = trial_val

                # If no 'trial' column found, leave trial_index_data as zeros and don't add channel
                if not has_trial_col:
                    trial_index_available = False
            except Exception:
                trial_index_available = False

        # Set annotations on raw (replace any existing, since EDF has none useful)
        if len(onsets) > 0:
            # Filter out annotations outside data range to avoid MNE warnings
            max_time = raw.times[-1] + 1.0 / raw.info["sfreq"]
            valid_idx = [i for i, o in enumerate(onsets) if o < max_time]
            if valid_idx:
                valid_onsets = [onsets[i] for i in valid_idx]
                valid_durations = [durations[i] for i in valid_idx]
                valid_descriptions = [descriptions[i] for i in valid_idx]
                raw.set_annotations(mne.Annotations(onset=valid_onsets, duration=valid_durations, description=valid_descriptions))

        # ------------------------------------------------------------------
        # 4. Add derived misc channels
        # ------------------------------------------------------------------
        # Add trial_index as misc channel only if 'trial' column was actually available
        if trial_index_available and "trial_index" not in raw.ch_names:
            trial_info = mne.create_info(
                ch_names=["trial_index"],
                sfreq=raw.info["sfreq"],
                ch_types=["misc"],
            )
            trial_raw = mne.io.RawArray(trial_index_data, trial_info, verbose=False)
            raw.add_channels([trial_raw], force_update_info=True)

        # ------------------------------------------------------------------
        # 5. Update description with metadata
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": participant_info,
            "eegunity_scan_hints": {
                "events": _EVENT_HINTS,
            },
        })

        return raw


KERNEL = OpenNeuroDS004448Kernel()
