"""Physionet EEG-MAT stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import pandas as pd


@dataclass
class PhysionetEegmatKernel:
    """Stage1 kernel for the physionet-eegmat dataset."""

    KERNEL_ID: str = "physionet-eegmat-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Locate subject-info.csv.
        data_dir = os.path.dirname(file_path)
        subject_info_path = os.path.join(data_dir, "subject-info.csv")

        filename = os.path.basename(file_path)
        subject_id = filename.split("_")[0]

        age = "Unknown"
        gender = "Unknown"
        count_quality_description = "Unknown"

        if os.path.exists(subject_info_path):
            subject_info = pd.read_csv(subject_info_path)
            subject_data = subject_info[subject_info["Subject"] == subject_id]

            if not subject_data.empty:
                age = subject_data["Age"].values[0] if "Age" in subject_data.columns else "Unknown"
                gender = subject_data["Gender"].values[0] if "Gender" in subject_data.columns else "Unknown"
                count_quality = (
                    subject_data["Count quality"].values[0]
                    if "Count quality" in subject_data.columns
                    else "Unknown"
                )
                if count_quality == 1:
                    count_quality_description = "Good"
                elif count_quality == 0:
                    count_quality_description = "Bad"

        # Determine task from filename suffix.
        if filename.endswith("_1.edf"):
            task_description = "Background EEG"
        elif filename.endswith("_2.edf"):
            task_description = "Mental Arithmetic Task EEG"
        else:
            task_description = "Unknown Task"

        annotation_description = f"{task_description};Count Quality: {count_quality_description}"

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "Neurocom EEG 23-channel system  (Ukraine, XAI-MEDICA)",
                "cap": "silver/silver chloride electrodes",
                "age": str(age),
                "sex": str(gender).replace("F", "Female").replace("M", "Male"),
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Set annotation spanning entire recording.
        annotations = mne.Annotations(
            onset=0,
            duration=raw.times[-1],
            description=annotation_description,
        )
        raw.set_annotations(annotations)

        return raw


KERNEL = PhysionetEegmatKernel()
