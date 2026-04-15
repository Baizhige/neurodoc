"""OpenNeuro DS005087 (Robinson et al., 2025) stage1 kernel for EEGUnity.

RSVP Visual Hemifield Presentation dataset: 80 subjects, 63 channels, 1000 Hz.
Rapid serial visual presentation at 5 Hz to left/right/center hemifield.

Source: https://openneuro.org/datasets/ds005087
DOI: https://doi.org/10.1126/sciadv.adq0889
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# Default amplifier/cap if not found in dataset metadata.
# Source: Inferred from typical EEG lab equipment for Robinson et al. (2025),
# likely standard 64-channel system. LLM 推断，需人类复核
_DEFAULT_AMPLIFIER = "unknown"
_DEFAULT_CAP = "unknown"


def _extract_subject_info(
    participants_tsv: Optional[str],
) -> Dict[str, Dict[str, str]]:
    """Extract subject metadata from participants.tsv if available.

    Returns a dict mapping subject_id -> {"age": str, "sex": str}.
    """
    if participants_tsv is None or not os.path.exists(participants_tsv):
        return {}

    try:
        df = pd.read_csv(participants_tsv, sep="\t")
    except Exception:
        return {}

    subject_info: Dict[str, Dict[str, str]] = {}
    for _, row in df.iterrows():
        sid = str(row.get("participant_id", ""))
        if not sid:
            continue

        age_val = row.get("age", "unknown")
        sex_val = str(row.get("sex", "unknown")).lower()

        if isinstance(age_val, (int, float)) and not np.isnan(age_val):
            age_str = str(int(age_val))
        elif isinstance(age_val, str) and age_val.strip():
            age_str = age_val.strip()
        else:
            age_str = "unknown"

        if sex_val not in ("male", "female"):
            sex_str = "unknown"
        else:
            sex_str = sex_val

        subject_info[sid] = {"age": age_str, "sex": sex_str}

    return subject_info


def _build_eegunity_description(
    raw: mne.io.BaseRaw,
    subject_id: str,
    subject_info: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    """Build the EEGUnity description dict for a single raw file."""
    original_desc = raw.info.get("description", "")

    info = subject_info.get(subject_id, {})
    age = info.get("age", "unknown")
    sex = info.get("sex", "unknown")

    return {
        "original_description": original_desc,
        "eegunity_description": {
            "age": age,
            "sex": sex,
            "amplifier": _DEFAULT_AMPLIFIER,
            "cap": _DEFAULT_CAP,
            "handedness": "unknown",
        },
    }


def _create_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create annotations from raw events (BrainVision markers or stim channel).

    The dataset uses BrainVision format with markers E 1, E 2, E 3 for
    hemifield conditions and numeric codes 1, 2, 3 for stimulus categories.
    """
    original_event_id: Dict[str, int] = {}
    original_events: np.ndarray = np.zeros((0, 3), dtype=int)

    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        original_events = events
        original_event_id = event_id
    except Exception:
        pass

    if original_events.size == 0:
        return mne.Annotations(onset=[], duration=[], description=[])

    onset_times = original_events[:, 0] / raw.info["sfreq"]
    descriptions: list[str] = []

    for event_id_val in original_events[:, 2]:
        desc = str(event_id_val)
        for orig_desc, orig_id in original_event_id.items():
            if orig_id == event_id_val:
                desc = orig_desc
                break
        descriptions.append(desc)

    annotations = mne.Annotations(
        onset=onset_times,
        duration=np.zeros(len(onset_times)),
        description=descriptions,
    )

    return annotations


def _rename_channels_standard1020(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed.

    Check for common non-standard channel naming patterns in BrainVision data
    (e.g., 'EEG 001', 'EOG-left', etc.) and map to standard names.

    Source: Standard 10-20 channel naming convention. LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    for ch in ch_names:
        if ch.startswith("EEG "):
            parts = ch.split()
            if len(parts) >= 2:
                num_str = parts[1].lstrip("0")
                if num_str.isdigit():
                    new_name = f"EEG-{int(num_str)}"
                    if ch != new_name:
                        rename_map[ch] = new_name
        elif ch.startswith("EOG-") or ch.startswith("EOG "):
            eye_pos = ch.replace("EOG-", "").replace("EOG ", "").lower()
            if eye_pos in ("left", "l", "lo"):
                rename_map[ch] = "EOG-left"
            elif eye_pos in ("right", "r", "ro"):
                rename_map[ch] = "EOG-right"
            elif eye_pos in ("up", "u", "uo"):
                rename_map[ch] = "EOG-up"
            elif eye_pos in ("down", "d", "do"):
                rename_map[ch] = "EOG-down"
        elif ch.startswith("SC ") or ch.startswith("Status"):
            if ch.startswith("SC "):
                rename_map[ch] = "stim"

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage if all EEG channels are standard names."""
    try:
        eeg_channels = [
            ch for ch in raw.ch_names
            if ch not in ("stim", "misc", "EOG-left", "EOG-right", "EOG-up", "EOG-down")
            and not ch.startswith("EOG-")
        ]

        if not eeg_channels:
            return raw

        montage = mne.channels.make_standard_montage("standard_1020")
        known_channels = set(montage.ch_names)

        if all(ch in known_channels for ch in eeg_channels):
            raw.set_montage("standard_1020", on_missing="ignore")
    except Exception:
        pass

    return raw


class OpenNeuroDS005087Kernel:
    """Stage1 kernel for OpenNeuro DS005087 (Robinson et al., 2025)."""

    KERNEL_ID: str = "openneuro-ds005087-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least File Path and participant_id.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with annotations and metadata.
        """
        file_path = str(row.get("File Path", ""))
        participant_id = str(row.get("participant_id", row.get("subject_id", "")))

        dataset_dir = os.path.dirname(os.path.dirname(file_path))
        participants_tsv = os.path.join(dataset_dir, "participants.tsv")
        subject_info = _extract_subject_info(participants_tsv)

        raw = _rename_channels_standard1020(raw)

        raw = _set_montage_if_possible(raw)

        annotations = _create_annotations(raw)
        raw.set_annotations(annotations)

        description_dict = _build_eegunity_description(
            raw, participant_id, subject_info
        )
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS005087Kernel()