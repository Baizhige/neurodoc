"""OpenNeuro DS004381 stage1 kernel for EEGUnity.

Intraoperative SEP dataset during medianus-tibialis stimulation with 8 different rates.
4 channels, 20 kHz sampling rate, 18 subjects.

Source: https://openneuro.org/datasets/ds004381
Reference DOI: 10.1016/j.clinph.2023.03.008
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Stimulation rate patterns for super meta extraction
# Source: Derived from filename pattern (paper DOI: 10.1016/j.clinph.2023.03.008)
# Annotator: LLM, 2026-04-08
_STIM_RATE_PATTERN = re.compile(r"(\d+\.?\d*)\s*Hz", re.IGNORECASE)

# Known stimulation rates for this dataset
# Source: Paper analysis (DOI: 10.1016/j.clinph.2023.03.008)
# Annotator: LLM, 2026-04-08
_VALID_STIM_RATES: List[str] = [
    "stimulation_rate_2.7Hz",
    "stimulation_rate_4.7Hz",
    "stimulation_rate_8.7Hz",
    "stimulation_rate_12.7Hz",
    "stimulation_rate_16.7Hz",
    "stimulation_rate_20.7Hz",
    "stimulation_rate_24.7Hz",
    "stimulation_rate_28.7Hz",
]


def _extract_stimulation_rate(file_path: str) -> str:
    """Extract stimulation rate from file path or filename.

    Parameters
    ----------
    file_path : str
        Full file path or filename containing rate information.

    Returns
    -------
    str
        Stimulation rate label (e.g., "stimulation_rate_2.7Hz") or "unknown_rate".
    """
    filename = os.path.basename(file_path)
    match = _STIM_RATE_PATTERN.search(filename)
    if match:
        rate = float(match.group(1))
        return f"stimulation_rate_{rate}Hz"
    return "unknown_rate"


def _build_default_channel_names(n_channels: int) -> List[str]:
    """Build default channel names based on channel count.

    For intraoperative SEP with 4 channels, typical layout:
    - 2 channels for medianus (left/right C3/C4 area)
    - 2 channels for tibial (Cz area or referenced)

    Source: Clinical SEP convention (LLM inferred, need human复核)
    # LLM 推断，需人类复核
    """
    if n_channels == 4:
        return ["C3", "C4", "Cz", "REF"]
    elif n_channels == 3:
        return ["C3", "C4", "Cz"]
    elif n_channels == 2:
        return ["C3", "Cz"]
    else:
        return [f"EEG-{i}" for i in range(n_channels)]


def _rename_channels_if_needed(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channels to standard 10-20 names.

    Attempts to detect and rename channels based on common patterns:
    - Numeric EEG-0, EEG-1, etc.
    - Other non-standard naming

    Source: Kernel inference (LLM 推断，需人类复核)
    # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    for ch_name in raw.ch_names:
        ch_upper = ch_name.upper()
        # Pattern: EEG-0, EEG-1, etc.
        if re.match(r"^EEG-\d+$", ch_name):
            # Keep as-is or map based on position if known
            # For SEP, typically C3/C4/Cz related
            continue
        # Pattern: just numbers
        if re.match(r"^\d+$", ch_name):
            idx = int(ch_name)
            default_names = _build_default_channel_names(raw.info["nchan"])
            if idx < len(default_names):
                rename_map[ch_name] = default_names[idx]

    if rename_map:
        mne.rename_channels(raw.info, rename_map)
    return raw


def _load_participants_tsv(dataset_path: str) -> Optional[pd.DataFrame]:
    """Load participants.tsv if it exists.

    Returns
    -------
    pd.DataFrame or None
        Participants dataframe or None if not found.
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            return df
        except Exception:
            pass
    return None


def _get_subject_info_from_participants(
    dataset_path: str, subject_id: str
) -> Dict[str, str]:
    """Extract subject info from participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Root dataset path.
    subject_id : str
        Subject identifier (e.g., "sub-01").

    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, etc.
    """
    df = _load_participants_tsv(dataset_path)
    if df is None:
        return {}

    # Normalize subject_id for matching
    if "participant_id" in df.columns:
        # Try exact match first
        match = df[df["participant_id"] == subject_id]
        if match.empty:
            # Try without 'sub-' prefix
            clean_id = subject_id.replace("sub-", "")
            match = df[df["participant_id"].str.contains(clean_id, na=False)]

        if not match.empty:
            row = match.iloc[0]
            info = {}
            for col in ["age", "sex", "handedness"]:
                if col in row and pd.notna(row[col]):
                    info[col] = str(row[col]).lower() if col == "sex" else str(row[col])
            return info

    return {}


class OpenNeuroDS004381Kernel:
    """Stage1 kernel for OpenNeuro DS004381 dataset.

    Intraoperative SEP recordings with 8 stimulation rates (2.7-28.7 Hz).
    No discrete events in raw data; stimulation rate encoded in filenames.
    """

    KERNEL_ID: str = "openneuro-ds004381-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", row.get("subject_id", "unknown"))

        # Extract original description
        original_description = raw.info.get("description", "")

        # Try to get subject info from participants.tsv
        # Source: BIDS participants.tsv (if available)
        # Annotator: LLM, 2026-04-08
        dataset_path = row.get("Dataset Path", "")
        subject_info = _get_subject_info_from_participants(dataset_path, subject_id)

        # Infer device info from sampling rate
        # Source: Dataset documentation (20kHz indicates specialized amplifier)
        # Annotator: LLM, 2026-04-08
        sfreq = raw.info["sfreq"]
        if sfreq >= 10000:
            amplifier = "high-resolution intraoperative amplifier (20kHz)"  # LLM 推断，需人类复核
        else:
            amplifier = "unknown"

        # Build eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower()
                if subject_info.get("sex") else "unknown",
                "amplifier": amplifier,
                "cap": "invasive / sterile surgical setup",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        raw = _rename_channels_if_needed(raw)

        # Try to set montage if channels are recognizable
        # Only for standard 10-20 channels that MNE can locate
        standard_channels = {"C3", "C4", "Cz", "FC3", "FC4", "FCz",
                             "CP3", "CP4", "CPz", "Fz", "Pz"}
        ch_names_set = set(raw.ch_names)
        if ch_names_set & standard_channels:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Find channels that match standard names
                common_channels = ch_names_set & set(monteage.ch_names for monteage in [montage])  # type: ignore
                if common_channels:
                    raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # If montage fails, continue without it
                pass

        # Extract stimulation rate from filename for super meta
        stim_rate = _extract_stimulation_rate(file_path)

        # Create annotation for stimulation rate (super meta)
        # This enables epoch_by_segmentation_hdf5 to segment by rate
        if stim_rate != "unknown_rate" and raw.n_times > 0:
            # Create a single annotation at the start indicating the stimulation rate
            annotations = mne.Annotations(
                onset=[0.0],
                duration=[raw.n_times / raw.info["sfreq"]],
                description=[stim_rate],
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004381Kernel()