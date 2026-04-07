"""Kaggle INRIA stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


@dataclass
class KaggleInriaKernel:
    """Stage1 kernel for the kaggle-inria (BCI Challenge) dataset."""

    KERNEL_ID: str = "kaggle-inria-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = udataset.get_shared_attr()["dataset_path"]

        # Update description.
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap": "Ag/AgCl",
                "age": "20-37",
                "sex": "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Load TrainLabels.csv from dataset root.
        train_labels_path = os.path.join(dataset_path, "TrainLabels.csv")
        train_labels_df = pd.read_csv(train_labels_path)

        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]  # e.g. "Data_S02_Sess01"

        # Extract event positions from FeedBackEvent channel.
        feedback_channel = raw.get_data(picks="FeedBackEvent")[0]
        event_indices = np.where(feedback_channel == 1)[0]
        event_times = event_indices / raw.info["sfreq"]
        event_durations = np.ones_like(event_times) * 1

        # Match labels.
        file_events = train_labels_df[
            train_labels_df["IdFeedBack"].str.startswith(base_name[5:])
        ]

        descriptions = []
        for i, event_time in enumerate(event_times):
            feedback_id = f"{base_name[5:]}_FB{str(i + 1).zfill(3)}"
            label_row = file_events[file_events["IdFeedBack"] == feedback_id]

            if not label_row.empty:
                prediction = label_row["Prediction"].values[0]
                description = (
                    "good feedback to P300"
                    if prediction == 1
                    else "wrong feedback to P300"
                )
            else:
                description = "unknown feedback to P300"
            descriptions.append(description)

        annotations = mne.Annotations(
            onset=event_times, duration=event_durations, description=descriptions
        )
        raw.set_annotations(annotations)

        return raw


KERNEL = KaggleInriaKernel()
