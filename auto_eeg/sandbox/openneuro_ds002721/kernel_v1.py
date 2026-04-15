"""Dataset-specific kernel for openneuro ds002721.

EEG dataset recorded during affective music listening.
Participants listened to 40 music clips from film scores while their EEG was recorded.

Source: https://openneuro.org/datasets/ds002721
Source: DOI 10.1038/s41597-020-0507-6 (Film Clips dataset)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np


# Music clip onset event mapping (26 unique tracks)
# Source: analysis.md / paradigm description
# Annotator: Human, 2026-04-08
_EVENT_MAP = {
    800: "music_onset_track_800",
    801: "music_onset_track_801",
    802: "music_onset_track_802",
    803: "music_onset_track_803",
    804: "music_onset_track_804",
    805: "music_onset_track_805",
    806: "music_onset_track_806",
    807: "music_onset_track_807",
    808: "music_onset_track_808",
    786: "music_onset_track_786",
    788: "music_onset_track_788",
    833: "music_onset_track_833",
    834: "music_onset_track_834",
    835: "music_onset_track_835",
    836: "music_onset_track_836",
    837: "music_onset_track_837",
    838: "music_onset_track_838",
    839: "music_onset_track_839",
    840: "music_onset_track_840",
    902: "music_onset_track_902",
    903: "music_onset_track_903",
    904: "music_onset_track_904",
    905: "music_onset_track_905",
    906: "music_onset_track_906",
    907: "music_onset_track_907",
    908: "music_onset_track_908",
    32768: "system_marker_32768",
    257: "system_marker_257",
    1092: "system_marker_1092",
    33575: "system_marker_33575",
}

# Admin/system markers to exclude from target events
_ADMIN_EVENTS = {32768, 257, 1092, 33575}

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
        ("EOG-left", ["EOG-left", "EOGL", "HEOG-left"]),
        ("EOG-right", ["EOG-right", "EOGR", "HEOG-right"]),
        ("EOG-up", ["EOG-up", "EOGU", "VEOG-up"]),
        ("EOG-down", ["EOG-down", "EOGD", "VEOG-down"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _remap_annotations_to_events(raw: mne.io.BaseRaw) -> None:
    """Remap annotation descriptions to standardized event labels."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return

    new_descriptions = []
    for desc in raw.annotations.description:
        try:
            code = int(float(desc))
            new_desc = _EVENT_MAP.get(code, f"event_{code}")
        except (ValueError, TypeError):
            new_desc = str(desc)
        new_descriptions.append(new_desc)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)


class OpenNeuroDS002721Kernel:
    """Stage1 kernel for the OpenNeuro ds002721 dataset.

    This kernel handles the BIDS-formatted OpenNeuro ds002721 dataset,
    which contains EEG recordings during affective music listening.
    """

    KERNEL_ID: str = "openneuro-ds002721-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least file path info.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object.
        """
        # Extract subject information from locator row
        subject_id = str(row.get("participant_id", row.get("subject_id", "unknown")))

        # Get age and sex from participants.tsv if available via udataset
        age = "unknown"
        sex = "unknown"
        if hasattr(udataset, "participants_df") and udataset.participants_df is not None:
            participants_df = udataset.participants_df
            if subject_id in participants_df.index or subject_id in participants_df["participant_id"].values:
                if "age" in participants_df.columns:
                    age = str(participants_df.loc[subject_id, "age"])
                if "sex" in participants_df.columns:
                    sex = str(participants_df.loc[subject_id, "sex"]).lower()
                    if sex not in ("male", "female"):
                        sex = "unknown"

        # Update description with metadata
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # First, rename channels
            channel_types_to_set = {}
            eog_channels = {"EOG-left", "EOG-right", "EOG-up", "EOG-down"}
            
            for old_name, new_name in rename_map.items():
                if new_name in eog_channels:
                    channel_types_to_set[new_name] = "eog"
            
            raw.rename_channels(rename_map)
            
            # Set channel types for EOG
            if channel_types_to_set:
                eog_to_set = {ch: ch_type for ch, ch_type in channel_types_to_set.items() if ch in raw.ch_names}
                if eog_to_set:
                    raw.set_channel_types(eog_to_set)

            # Set montage if all channels are standard 10-20
            standard_chs = set(raw.ch_names) & _STANDARD_19_CHANNELS
            if len(standard_chs) >= 16:
                try:
                    montage = mne.channels.make_standard_montage("standard_1020")
                    raw.set_montage(montage, on_missing="warn")
                except Exception:
                    pass

        # Remap annotations to standardized event labels
        _remap_annotations_to_events(raw)

        return raw


KERNEL = OpenNeuroDS002721Kernel()