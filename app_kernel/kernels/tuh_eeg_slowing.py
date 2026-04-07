"""TUH EEG Slowing stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
from dataclasses import dataclass

import mne
import pandas as pd


@dataclass
class TuhEegSlowingKernel:
    """Stage1 kernel for the tuh-eeg-slowing dataset."""

    KERNEL_ID: str = "tuh-eeg-slowing-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        sex_mapping = {0: "unknown", 1: "male", 2: "female"}
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap": "unknown",
                "age": "unknown",
                "sex": sex_mapping.get(raw.info.get("sex", 0), "unknown"),
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Read .csv annotation file alongside EEG data.
        csv_path = raw.filenames[0][:-3] + "csv"
        annotations_df = pd.read_csv(csv_path, comment="#")

        required_columns = ["channel", "start_time", "stop_time", "label"]
        missing_columns = [col for col in required_columns if col not in annotations_df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        start_time = annotations_df["start_time"].values
        stop_time = annotations_df["stop_time"].values
        label = annotations_df["label"].values
        duration = stop_time - start_time

        annotations = mne.Annotations(onset=start_time, duration=duration, description=label)
        raw.set_annotations(annotations)

        return raw


KERNEL = TuhEegSlowingKernel()
