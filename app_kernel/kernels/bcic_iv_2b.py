"""BCIC IV 2b stage1 kernel for EEGUnity."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from typing import Any, Dict

import mne
import numpy as np
import scipy.io as scio


_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "B01": {"sex": "female", "age": "20"},
    "B02": {"sex": "male", "age": "24"},
    "B03": {"sex": "male", "age": "21"},
    "B04": {"sex": "female", "age": "23"},
    "B05": {"sex": "male", "age": "24"},
    "B06": {"sex": "female", "age": "21"},
    "B07": {"sex": "male", "age": "27"},
    "B08": {"sex": "female", "age": "32"},
    "B09": {"sex": "male", "age": "26"},
}


def _update_events(original_events, original_event_id, new_event_id):
    """Map original event IDs to new event IDs based on label matching."""
    original_to_new_mapping = {}
    for original_key, original_value in original_event_id.items():
        for new_key, new_value in new_event_id.items():
            if original_key in new_key:
                original_to_new_mapping[original_value] = new_value

    new_events = copy.deepcopy(original_events)
    for event in new_events:
        if event[2] in original_to_new_mapping:
            event[2] = original_to_new_mapping[event[2]]

    return new_events


@dataclass
class BCICIV2bKernel:
    """Stage1 kernel for the BCIC IV 2b dataset."""

    KERNEL_ID: str = "bcic-iv-2b-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = os.path.basename(file_path)[:3]

        # Update description.
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap": "Ag/AgCl",
                "age": _SUBJECT_DICT[subject_id]["age"],
                "sex": _SUBJECT_DICT[subject_id]["sex"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Set montage and EOG channel types.
        # Use case-insensitive prefix matching to handle both eegunity <=0.5.4
        # (uppercase 'EOG:ch01') and >=0.7.4 (lowercase 'eog:ch01').
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.info.set_montage(montage, on_missing="ignore")
        _eog_keys = {"EOG:CH01", "EOG:CH02", "EOG:CH03"}
        ch_type_updates = {
            ch: "eog" for ch in raw.ch_names if ch.upper() in _eog_keys
        }
        if ch_type_updates:
            raw.set_channel_types(ch_type_updates)

        # Event mapping.
        new_event_id = {
            "Rejected trial": 1,
            "Horizontal eye movement": 2,
            "Vertical eye movement": 3,
            "Eye rotation": 4,
            "Eye blinks": 5,
            "Idling EEG (eyes open)": 6,
            "Idling EEG (eyes closed)": 7,
            "Start of a new run": 8,
            "Start of a trial": 9,
            "Cue onset left (class 1)": 10,
            "Cue onset right (class 2)": 11,
            "BCI feedback (continuous)": 12,
            "Cue unknown": 13,
        }

        original_events, original_event_id = mne.events_from_annotations(raw)
        new_events = _update_events(original_events, original_event_id, new_event_id)

        # If file ends with 'E.gdf', use .mat classlabel to refine events.
        file_base, file_ext = os.path.splitext(file_path)
        if file_base.endswith("E") and file_ext == ".gdf":
            unknown_id = new_event_id["Cue unknown"]
            mat_filepath = f"{file_base}.mat"
            if os.path.exists(mat_filepath):
                mat_data = scio.loadmat(mat_filepath)
                values_from_mat = mat_data["classlabel"].flatten() + 9
                replacement_indices = np.where(new_events[:, -1] == unknown_id)[0]
                if len(replacement_indices) == len(values_from_mat):
                    new_events[
                        replacement_indices[: len(values_from_mat)], 2
                    ] = values_from_mat

        # Convert events back to annotations.
        event_desc = {v: k for k, v in new_event_id.items()}
        annotations = mne.annotations_from_events(
            events=new_events,
            sfreq=raw.info["sfreq"],
            event_desc=event_desc,
        )
        raw.set_annotations(annotations)

        return raw


KERNEL = BCICIV2bKernel()
