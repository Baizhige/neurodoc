"""OpenNeuro ds002724 stage1 kernel for EEGUnity.

Affective brain-computer music interface training sessions.
37-channel EEG + physiological recordings (ECG, GSR, etc.).
Sampling rate: 1000 Hz. 9 music conditions coded as events 1-9.

Source: https://openneuro.org/datasets/ds002724
DOI: https://doi.org/10.1038/s41597-020-0507-6
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import pandas as pd


# Event mapping: codes 1-9 → human-readable labels
# Source: analysis.md, Daly et al. 2020, Scientific Data
_EVENT_ID_MAP = {
    1: "Music condition 1",
    2: "Music condition 2",
    3: "Music condition 3",
    4: "Music condition 4",
    5: "Music condition 5",
    6: "Music condition 6",
    7: "Music condition 7",
    8: "Music condition 8",
    9: "Music condition 9",
}


def _extract_subject_info_from_bids(raw: mne.io.BaseRaw, row) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv.
    
    Source: BIDS participants.tsv file
    """
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    file_path = row.get("File Path", "")
    if not file_path:
        return subject_info
    
    # Navigate to dataset root to find participants.tsv
    parts = file_path.split(os.sep)
    dataset_root = None
    for i, part in enumerate(parts):
        if part.startswith("sub-"):
            dataset_root = os.path.join(os.sep.join(parts[:i]), "")
            break
    
    if dataset_root and os.path.exists(dataset_root):
        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        if os.path.exists(participants_tsv):
            try:
                df = pd.read_csv(participants_tsv, sep="\t")
                # Extract subject ID from file path
                for part in parts:
                    if part.startswith("sub-"):
                        subject_id = part
                        break
                else:
                    return subject_info
                
                # Match participant row
                if "participant_id" in df.columns:
                    match = df[df["participant_id"] == subject_id]
                    if len(match) > 0:
                        row_data = match.iloc[0]
                        
                        # Age
                        if "age" in df.columns:
                            age_val = row_data.get("age")
                            if pd.notna(age_val):
                                subject_info["age"] = str(int(age_val))
                        
                        # Sex
                        if "sex" in df.columns:
                            sex_val = row_data.get("sex", "")
                            if pd.notna(sex_val):
                                sex_lower = str(sex_val).lower().strip()
                                if sex_lower in ("m", "male", "man"):
                                    subject_info["sex"] = "male"
                                elif sex_lower in ("f", "female", "woman"):
                                    subject_info["sex"] = "female"
                                else:
                                    subject_info["sex"] = "unknown"
                        
                        # Handedness
                        if "handedness" in df.columns:
                            handed_val = row_data.get("handedness", "")
                            if pd.notna(handed_val):
                                handed_lower = str(handed_val).lower().strip()
                                if handed_lower in ("r", "right"):
                                    subject_info["handedness"] = "right"
                                elif handed_lower in ("l", "left"):
                                    subject_info["handedness"] = "left"
                                else:
                                    subject_info["handedness"] = "unknown"
            except Exception:
                pass
    
    return subject_info


class DS002724Kernel:
    """Stage1 kernel for OpenNeuro ds002724.

    Processes training session EEG data from the affective brain-computer
    music interface study. The dataset contains 37-channel recordings with
    physiological channels (ECG, GSR, respiration), and 9 music condition
    events encoded as stimulus codes 1-9.

    Device info (amplifier, cap):
    Source: Daly et al. 2020, Scientific Data paper
    - Amplifier: "BrainAmp" (inferred from Brain Products hardware common in EEG studies)
    - Cap: "Ag/AgCl" (standard for EEG caps)
    """

    KERNEL_ID: str = "openneuro-ds002724-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # Extract subject info from BIDS participants.tsv
        subject_info = _extract_subject_info_from_bids(raw, row)

        # Update description with eegunity_description
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "BrainAmp",  # Source: Daly et al. 2020 - inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # Source: Daly et al. 2020 - inferred by LLM, needs human review
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Extract events and remap to human-readable labels
        events, event_id_map = mne.events_from_annotations(raw, verbose=False)

        if events.size > 0:
            new_onset = []
            new_duration = []
            new_description = []

            for idx in range(len(events)):
                event_id = events[idx, 2]
                # Handle both int and string event IDs
                event_key = event_id if isinstance(event_id, int) else int(event_id) if str(event_id).isdigit() else event_id
                
                if event_key in _EVENT_ID_MAP:
                    new_description.append(_EVENT_ID_MAP[event_key])
                    new_onset.append(events[idx, 0] / raw.info["sfreq"])
                    new_duration.append(0.0)

            if new_onset:
                annotations = mne.Annotations(
                    onset=new_onset,
                    duration=new_duration,
                    description=new_description,
                )
                raw.set_annotations(annotations)

        return raw


KERNEL = DS002724Kernel()