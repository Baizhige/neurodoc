"""openneuro_ds004517 stage1 kernel for EEGUnity.

Semantic decoding of imagined animals and tools during auditory imagery task.
32-channel EEG, 500 Hz, 20 subjects.

Events:
- animal_auditory_imagery_task / tool_auditory_imagery_task (long events)
- audio_animal / audio_tool (short cue events)
- rest

Source: https://openneuro.org/datasets/ds004517
       DOI: https://doi.org/10.18112/openneuro.ds004517.v1.0.2
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Dataset description and paper DOI: 10.1038/s41597-025-04967-0
# amplifier information not explicitly stated in public documentation
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 21)
}

# Annotator: Human, 2026-04-08
# Source: Standard 32-channel EEG cap (typically 10-20 system)
# Common channel naming in auditory EEG studies
_EEG_CHANNEL_NAMES_STANDARD = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "T5", "T6",
    "M1", "M2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.

    Annotator: Human, 2026-04-08
    Source: OpenNeuro ds004517 channel naming convention review
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    # Common EEG channel aliases for 32-channel caps
    alias_groups = [
        # Standard 10-20 positions
        ("Fp1", ["EEG Fp1", "Fp1", "EEG-Fp1"]),
        ("Fp2", ["EEG Fp2", "Fp2", "EEG-Fp2"]),
        ("Fpz", ["EEG Fpz", "Fpz", "EEG-Fpz"]),
        ("F7", ["EEG F7", "F7", "EEG-F7"]),
        ("F3", ["EEG F3", "F3", "EEG-F3"]),
        ("Fz", ["EEG Fz", "Fz", "EEG-Fz"]),
        ("F4", ["EEG F4", "F4", "EEG-F4"]),
        ("F8", ["EEG F8", "F8", "EEG-F8"]),
        ("T7", ["EEG T7", "T7", "EEG-T7", "T7 left"]),
        ("C3", ["EEG C3", "C3", "EEG-C3"]),
        ("Cz", ["EEG Cz", "Cz", "EEG-Cz"]),
        ("C4", ["EEG C4", "C4", "EEG-C4"]),
        ("T8", ["EEG T8", "T8", "EEG-T8", "T8 right"]),
        ("P7", ["EEG P7", "P7", "EEG-P7"]),
        ("P3", ["EEG P3", "P3", "EEG-P3"]),
        ("Pz", ["EEG Pz", "Pz", "EEG-Pz"]),
        ("P4", ["EEG P4", "P4", "EEG-P4"]),
        ("P8", ["EEG P8", "P8", "EEG-P8"]),
        ("O1", ["EEG O1", "O1", "EEG-O1"]),
        ("Oz", ["EEG Oz", "Oz", "EEG-Oz"]),
        ("O2", ["EEG O2", "O2", "EEG-O2"]),
        ("T5", ["EEG T5", "T5", "EEG-T5"]),
        ("T6", ["EEG T6", "T6", "EEG-T6"]),
        # Mastoide references
        ("M1", ["EEG M1", "M1", "EEG-M1", "Mastoid left", "left mastoid"]),
        ("M2", ["EEG M2", "M2", "EEG-M2", "Mastoid right", "right mastoid"]),
        # Common EOG channels
        ("EOG-left", ["EOG left", "EOG-L", "EOG-L1", "VEOG1"]),
        ("EOG-right", ["EOG right", "EOG-R", "EOG-R1"]),
        ("EOG-up", ["EOG up", "EOG-U", "HEOG"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in ch_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _extract_subject_info(
    dataset_path: str, subject_id: str
) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv.

    Annotator: Human, 2026-04-08
    Source: BIDS format participants.tsv file
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")

    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            row = df[df["participant_id"] == subject_id]
            if not row.empty:
                age = row.iloc[0].get("age", "unknown")
                sex = row.iloc[0].get("sex", row.iloc[0].get("gender", "unknown"))
                handedness = row.iloc[0].get("handedness", "unknown")

                # Normalize sex to lowercase
                if pd.notna(sex):
                    sex = str(sex).lower()
                    if sex not in ("male", "female"):
                        sex = "unknown"
                else:
                    sex = "unknown"

                return {
                    "age": str(age) if pd.notna(age) else "unknown",
                    "sex": sex,
                    "handedness": str(handedness).lower() if pd.notna(handedness) else "unknown",
                }
        except Exception:
            pass

    # Fallback to hardcoded dict
    return _SUBJECT_DICT.get(subject_id, {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    })


def _build_event_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract and normalize events from raw annotations.

    Annotator: Human, 2026-04-08
    Source: OpenNeuro ds004517 events.tsv structure
    Events: animal_auditory_imagery_task, tool_auditory_imagery_task,
            audio_animal, audio_tool, rest
    """
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)

        # Map existing event descriptions to canonical names
        canonical_map = {
            "animal_auditory_imagery_task": "animal_auditory_imagery_task",
            "tool_auditory_imagery_task": "tool_auditory_imagery_task",
            "audio_animal": "audio_animal",
            "audio_tool": "audio_tool",
            "rest": "rest",
        }

        # Build new annotations with canonical event names
        onsets = events[:, 0] / raw.info["sfreq"]
        descriptions = []
        for event_idx in events[:, 2]:
            for orig_desc, orig_id in event_id.items():
                if orig_id == event_idx:
                    canonical_desc = canonical_map.get(orig_desc, orig_desc)
                    descriptions.append(canonical_desc)
                    break
            else:
                descriptions.append(f"event_{event_idx}")

        return mne.Annotations(
            onset=onsets.tolist(),
            duration=[0.0] * len(onsets),
            description=descriptions,
        )
    except Exception:
        # If no annotations, return empty
        return mne.Annotations(onset=[], duration=[], description=[])


class openneuro_ds004517_Kernel:
    """Stage1 kernel for openneuro_ds004517 dataset."""

    KERNEL_ID: str = "openneuro-ds004517-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset: EEGUnity dataset context
        raw: MNE Raw object (modified in-place and returned)
        row: Locator row with File Path and other metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        original_description = raw.info.get("description", "")

        # Step 1: Channel rename (before set_montage)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
            raw.set_channel_types({
                name: "eeg" for name in raw.ch_names
                if name not in ("M1", "M2", "EOG-left", "EOG-right", "EOG-up")
            })

        # Step 2: Set montage if standard
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if not applicable

        # Step 3: Extract subject info
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))
        dataset_path = row.get("Dataset Path", "")

        if dataset_path and os.path.exists(dataset_path):
            subject_info = _extract_subject_info(dataset_path, subject_id)
        else:
            subject_info = _SUBJECT_DICT.get(subject_id, {
                "age": "unknown",
                "sex": "unknown",
                "handedness": "unknown",
            })

        # Step 4: Build event annotations
        annotations = _build_event_annotations(raw)
        raw.set_annotations(annotations)

        # Step 5: Write eegunity_description
        # Annotator: LLM, 2026-04-08
        # Source: Paper DOI 10.1038/s41597-025-04967-0 + OpenNeuro documentation
        # amplifier/cap inferred from typical auditory EEG paradigm setup
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = openneuro_ds004517_Kernel()