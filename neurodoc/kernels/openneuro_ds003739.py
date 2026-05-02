"""OpenNeuro DS003739 stage1 kernel for EEGUnity.

Perturbed beam-walking task: EEG recorded during walking on a treadmill-mounted
balance beam with sensorimotor perturbations (visual rotations and physical waist pulls).

Source: https://openneuro.org/datasets/ds003739
Paper: 10.1016/j.neuroimage.2019.05.038 / 10.1016/j.dib.2021.107635 / 10.1523/ENEURO.0207-18.2018
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-09 — needs human review
# Source: Dataset README and paper 10.1523/ENEURO.0207-18.2018
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # 30 participants, 18–45 years, right-handed
    # Exact individual data not publicly released; values inferred from paper
}

# Annotator: LLM, 2026-04-09 — needs human review
# Source: 10.1016/j.dib.2021.107635 — Dataset paper
_DEVICE_INFO = {
    "amplifier": "BrainAmp MR plus",  # From dataset description
    "cap": "Ag/AgCl",                 # Standard EEG cap
}


# Event parsing: extract perturbation type, posture, and direction from event labels
# Pattern:
#   Pull:    L_pull_Stn, R_pull_Stn, L_pull_Wlk, R_pull_Wlk
#   Rotate:  M_on_CCW_SVZ, M_on_CW_SVZ, M_on_CCW_WVZ, M_on_CW_WVZ
def _parse_event_label(label: str) -> Dict[str, Any]:
    """Parse event label into perturbation components.

    Pull events: L/R_pull_Stn/Wlk
    Rotation events: M_on_CCW/CW_SVZ/WVZ
    """
    label = str(label).strip()
    result = {
        "original": label,
        "perturbation": "unknown",  # pull | rotate
        "posture": "unknown",       # stand | walk
        "direction": "unknown",     # left | right | cw | ccw
        "4class_label": -1,         # 0-3 for 4-class task
        "8class_label": -1,         # 0-7 for 8-class task
    }

    # Parse pull events: L_pull_Stn, R_pull_Stn, L_pull_Wlk, R_pull_Wlk
    pull_match = re.match(r"^(L|R)_pull_(Stn|Wlk)$", label)
    if pull_match:
        direction = pull_match.group(1)
        posture = pull_match.group(2)

        result["perturbation"] = "pull"
        result["posture"] = "stand" if posture == "Stn" else "walk"
        result["direction"] = "left" if direction == "L" else "right"

        # 4-class: collapse direction
        if posture == "Stn":
            result["4class_label"] = 0
        else:
            result["4class_label"] = 1

        # 8-class
        if posture == "Stn":
            result["8class_label"] = 0 if direction == "L" else 1
        else:
            result["8class_label"] = 2 if direction == "L" else 3
        return result

    # Parse rotation events: M_on_CCW_SVZ, M_on_CW_SVZ, M_on_CCW_WVZ, M_on_CW_WVZ
    rot_match = re.match(r"^M_on_(CCW|CW)_(SVZ|WVZ)$", label)
    if rot_match:
        rot_dir = rot_match.group(1)
        posture_env = rot_match.group(2)

        result["perturbation"] = "rotate"
        result["posture"] = "stand" if posture_env == "SVZ" else "walk"
        result["direction"] = "ccw" if rot_dir == "CCW" else "cw"

        # 4-class: collapse rotation direction
        if posture_env == "SVZ":
            result["4class_label"] = 2
        else:
            result["4class_label"] = 3

        # 8-class
        if posture_env == "SVZ":
            result["8class_label"] = 4 if rot_dir == "CCW" else 5
        else:
            result["8class_label"] = 6 if rot_dir == "CCW" else 7
        return result

    return result


# 4-class label mapping (for super meta)
_4CLASS_MAP = {
    "stand_pull": 0,
    "walk_pull": 1,
    "stand_rotate": 2,
    "walk_rotate": 3,
}

# 8-class label mapping (for super meta)
_8CLASS_MAP = {
    "L_pull_Stn": 0,
    "R_pull_Stn": 1,
    "L_pull_Wlk": 2,
    "R_pull_Wlk": 3,
    "M_on_CCW_SVZ": 4,
    "M_on_CW_SVZ": 5,
    "M_on_CCW_WVZ": 6,
    "M_on_CW_WVZ": 7,
}


def _build_4class_label(parsed: Dict[str, Any]) -> str:
    """Convert parsed event to 4-class label string."""
    pert = parsed["perturbation"]
    posture = parsed["posture"]
    if pert == "unknown" or posture == "unknown":
        return "unknown"
    return f"{posture}_{pert}"


@dataclass
class OpenNeuroDS003739Kernel:
    """Stage1 kernel for the OpenNeuro DS003739 dataset."""

    KERNEL_ID: str = "openneuro-ds003739-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        base_dir = os.path.dirname(file_path)

        # Build eegunity_description
        subject_id = row.get("subject_id", "unknown")

        # Try to load participants.tsv for age/sex
        age_val = "unknown"
        sex_val = "unknown"
        handedness_val = "unknown"

        participants_tsv = os.path.join(base_dir, "..", "..", "participants.tsv")
        if os.path.exists(participants_tsv):
            try:
                p_df = pd.read_csv(participants_tsv, sep="\t")
                subj_row = p_df[p_df.get("participant_id", pd.Series()) == subject_id]
                if len(subj_row) > 0:
                    row_data = subj_row.iloc[0]
                    if "age" in p_df.columns:
                        age_raw = row_data.get("age", "unknown")
                        if age_raw and str(age_raw).lower() != "n/a":
                            age_val = str(age_raw)
                    if "sex" in p_df.columns or "gender" in p_df.columns:
                        sex_col = "sex" if "sex" in p_df.columns else "gender"
                        sex_raw = row_data.get(sex_col, "unknown")
                        if sex_raw and str(sex_raw).lower() not in ("n/a", ""):
                            sex_lower = str(sex_raw).lower()
                            if sex_lower in ("m", "male"):
                                sex_val = "male"
                            elif sex_lower in ("f", "female"):
                                sex_val = "female"
                            else:
                                sex_val = "unknown"
            except Exception:
                pass

        # Apply device metadata
        # Annotator: LLM, 2026-04-09 — needs human review
        amplifier = _DEVICE_INFO.get("amplifier", "unknown")
        cap = _DEVICE_INFO.get("cap", "unknown")

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age_val,
                "sex": sex_val,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness_val,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Load events.tsv if present
        events_tsv = None
        for fname in os.listdir(base_dir):
            if fname.endswith("_events.tsv"):
                events_tsv = os.path.join(base_dir, fname)
                break

        annotations_list = []
        onset_list = []
        duration_list = []
        description_list = []

        if events_tsv and os.path.exists(events_tsv):
            try:
                ev_df = pd.read_csv(events_tsv, sep="\t")
                if {"onset", "duration", "trial_type"}.issubset(ev_df.columns):
                    for _, ev_row in ev_df.iterrows():
                        onset_val = float(ev_row["onset"])
                        duration_val = float(ev_row.get("duration", 0))
                        trial_type = str(ev_row["trial_type"])

                        onset_list.append(onset_val)
                        duration_list.append(duration_val)
                        description_list.append(trial_type)

                        annotations_list.append(
                            {
                                "original": trial_type,
                                "onset": onset_val,
                                "duration": duration_val,
                            }
                        )
            except Exception:
                pass

        # If no events.tsv, look for annotations already on raw
        if not onset_list:
            existing_annots = raw.annotations
            if len(existing_annots) > 0:
                for i in range(len(existing_annots)):
                    onset_list.append(existing_annots.onset[i])
                    duration_list.append(existing_annots.duration[i])
                    description_list.append(existing_annots.description[i])

        # Set raw annotations
        if onset_list:
            raw.set_annotations(
                mne.Annotations(
                    onset=np.array(onset_list),
                    duration=np.array(duration_list),
                    description=description_list,
                )
            )
        else:
            # No events detected; raw meta stays empty
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))

        # Super meta: create 4-class and 8-class labels as separate annotations
        # These are stored as annotations with description = "4class:<label>" etc.
        super4_onsets = []
        super4_durations = []
        super4_descriptions = []

        super8_onsets = []
        super8_durations = []
        super8_descriptions = []

        for ann_data in annotations_list:
            parsed = _parse_event_label(ann_data["original"])
            if parsed["4class_label"] >= 0:
                label_4class = _build_4class_label(parsed)
                super4_onsets.append(ann_data["onset"])
                super4_durations.append(ann_data["duration"])
                super4_descriptions.append(f"4class:{label_4class}")

            if parsed["8class_label"] >= 0:
                super8_onsets.append(ann_data["onset"])
                super8_durations.append(ann_data["duration"])
                super8_descriptions.append(f"8class:{ann_data['original']}")

        # Append super meta annotations
        all_onset = list(raw.annotations.onset)
        all_duration = list(raw.annotations.duration)
        all_desc = list(raw.annotations.description)

        if super4_onsets:
            all_onset.extend(super4_onsets)
            all_duration.extend(super4_durations)
            all_desc.extend(super4_descriptions)

        if super8_onsets:
            all_onset.extend(super8_onsets)
            all_duration.extend(super8_durations)
            all_desc.extend(super8_descriptions)

        if all_onset:
            raw.set_annotations(
                mne.Annotations(
                    onset=np.array(all_onset),
                    duration=np.array(all_duration),
                    description=all_desc,
                )
            )

        # Set montage if standard 10-20 channels detected
        # Annotator: LLM, 2026-04-09 — needs human review
        # Source: Paper indicates standard EEG cap; 149 channels suggests high-density
        try:
            standard_chs = [ch for ch in raw.ch_names if ch in mne.channels.make_standard_montage("standard_1020").ch_names]
            if len(standard_chs) >= 20:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS003739Kernel()