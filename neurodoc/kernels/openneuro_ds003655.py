"""OpenNeuro DS003655 VerbalWorkingMemory stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds003655
Verbal working memory task with retention vs manipulation conditions.
21 channels, 500 Hz sampling rate, 26 subjects.

Event ID parity encoding:
  - Even IDs (160, 260, 360): Retention condition (y=0)
  - Odd IDs (161, 261, 361): Manipulation condition (y=1)
  - Middle digit encodes load level (5, 6, 7)

Source: DOI 10.1111/ejn.15457 — Verbal working memory with alphabetization
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}
# Populated from dataset participants.tsv; fallback is "unknown"


# =============================================================================
# Channel Mapping
# =============================================================================
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    "POz": "POz",
}


# =============================================================================
# Event ID Mapping
# =============================================================================
_EVENT_ID_MAP: Dict[int, str] = {
    160: "encoding_R_load5",
    161: "encoding_M_load5",
    260: "encoding_R_load6",
    261: "encoding_M_load6",
    360: "encoding_R_load7",
    361: "encoding_M_load7",
    250: "probe_R_load5",
    251: "probe_M_load5",
    350: "probe_R_load6",
    351: "probe_M_load6",
    450: "probe_R_load7",
    451: "probe_M_load7",
}

event_id_inv: Dict[str, int] = {v: k for k, v in _EVENT_ID_MAP.items()}


@dataclass
class OpenNeuroDS003655Kernel:
    KERNEL_ID: str = "openneuro-ds003655-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))

        # -------------------------------------------------------------------------
        # Step 1: Load subject metadata from participants.tsv
        # -------------------------------------------------------------------------
        dataset_root = udataset.root_path if hasattr(udataset, "root_path") else ""
        participants_tsv = os.path.join(dataset_root, "participants.tsv")

        if os.path.exists(participants_tsv):
            try:
                participants_df = pd.read_csv(participants_tsv, sep="\t")
                subj_row = None
                for _, p_row in participants_df.iterrows():
                    pid = str(p_row.get("participant_id", ""))
                    if pid.endswith(subject_id) or pid == subject_id:
                        subj_row = p_row
                        break

                if subj_row is not None:
                    age_val = subj_row.get("age", "unknown")
                    sex_val = str(subj_row.get("sex", "unknown")).lower()
                    if isinstance(age_val, (int, float)) and not np.isnan(age_val):
                        age_str = str(int(age_val))
                    else:
                        age_str = str(age_val) if age_val else "unknown"

                    if sex_val in ["m", "male"]:
                        sex_str = "male"
                    elif sex_val in ["f", "female"]:
                        sex_str = "female"
                    else:
                        sex_str = "unknown"
                else:
                    age_str = "unknown"
                    sex_str = "unknown"
            except Exception:
                age_str = "unknown"
                sex_str = "unknown"
        else:
            age_str = "unknown"
            sex_str = "unknown"

        if subject_id in _SUBJECT_DICT:
            age_str = _SUBJECT_DICT[subject_id].get("age", age_str)
            sex_str = _SUBJECT_DICT[subject_id].get("sex", sex_str)

        # -------------------------------------------------------------------------
        # Step 2: Update raw.info description
        # -------------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age_str,
                "sex": sex_str,
                "amplifier": "BrainAmp" if raw.info.get("meas_date") else "unknown",
                "cap": "Ag/AgCl" if raw.info.get("meas_date") else "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # Step 3: Rename channels to standard 10-20 names
        # -------------------------------------------------------------------------
        rename_map: Dict[str, str] = {}
        existing_chs = set(raw.ch_names)

        for std_name, alias in _CHANNEL_RENAME_MAP.items():
            if alias in existing_chs and alias != std_name:
                rename_map[alias] = std_name

        if rename_map:
            raw.rename_channels(rename_map, verbose=False)

        # -------------------------------------------------------------------------
        # Step 4: Set montage for standard 10-20 positions
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn", verbose=False)
        except Exception:
            pass

        # -------------------------------------------------------------------------
        # Step 5: Process events from annotations or raw events
        # -------------------------------------------------------------------------
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = np.empty((0, 3), dtype=int)
            event_id = {}

        sfreq = raw.info["sfreq"]
        onsets = []
        durations = []
        descriptions = []
        y_labels = []

        for ev in events:
            if len(ev) >= 3:
                event_desc = str(ev[2])
                if event_desc in _EVENT_ID_MAP:
                    desc = _EVENT_ID_MAP[event_desc]
                else:
                    try:
                        ev_id = int(float(event_desc))
                        desc = _EVENT_ID_MAP.get(ev_id, event_desc)
                    except (ValueError, TypeError):
                        desc = event_desc

                onset_sec = ev[0] / sfreq
                onsets.append(onset_sec)
                durations.append(0.0)
                descriptions.append(desc)

                try:
                    ev_id_num = int(float(event_desc))
                    if ev_id_num % 2 == 0:
                        y_labels.append(0)
                    else:
                        y_labels.append(1)
                except (ValueError, TypeError):
                    y_labels.append(0)

        if onsets:
            annotated_descs = [f"{desc}_y{y}" for desc, y in zip(descriptions, y_labels)]
            new_annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=annotated_descs,
                ch_names=None,
            )
            raw.set_annotations(new_annotations, verbose=False)

        return raw


KERNEL = OpenNeuroDS003655Kernel()