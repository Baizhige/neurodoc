"""openneuro_ds004279 stage1 kernel for EEGUnity.

Large Spanish EEG dataset with 56 subjects performing speech perception
and silent production tasks with 30 Spanish sentences.

Source: https://openneuro.org/datasets/ds004279
Paper: DOI 10.1088/1741-2552/ad88a3
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne


# Standard 10-20 montage for 64+ channel systems
_STANDARD_MONTAGE = "standard_1020"

# Device metadata - likely Brain Products based on Spanish EEG studies
# Source: General inference from paradigm and Spanish research conventions
# LLM 推断，需人类复核
_DEVICE_AMPLIFIER = "unknown"  # Likely Brain Products amplifier
_DEVICE_CAP = "unknown"        # Likely Ag/AgCl wet electrode cap

# Event prefix for multi-paradigm disambiguation
_PARADIGM_PREFIX = "LARGE_SPANISH_EEG"


def _detect_paradigm(file_path: str) -> Optional[str]:
    """Detect paradigm from file path components.
    
    Returns paradigm identifier: 'perception', 'production', or None.
    """
    basename = os.path.basename(file_path).lower()
    if "perception" in basename:
        return "perception"
    elif "production" in basename:
        return "production"
    return None


def _prefix_event_description(desc: str, paradigm: Optional[str]) -> str:
    """Add paradigm prefix to event description for disambiguation.
    
    Parameters
    ----------
    desc : str
        Original event description
    paradigm : str or None
        Detected paradigm identifier
        
    Returns
    -------
    str
        Prefixed event description
    """
    if paradigm and desc not in (
        "bad_artifact",
        "Impedance_test",
        "bad_before_experiment",
        "bad_after_experiment",
    ):
        return f"{_PARADIGM_PREFIX}: {desc}"
    return desc


def _build_perception_event_map() -> Dict[int, str]:
    """Build event ID map for perception paradigm.
    
    Maps numeric event IDs (1-30) to semantic perception_N labels.
    """
    return {i: f"perception_{i}" for i in range(1, 31)}


def _build_production_event_map() -> Dict[int, str]:
    """Build event ID map for production paradigm.
    
    Maps numeric event IDs to semantic production_N labels.
    """
    return {i: f"production_{i}" for i in range(1, 31)}


class OpenNeuroDS004279Kernel:
    """Stage1 kernel for openneuro_ds004279 dataset."""

    KERNEL_ID: str = "openneuro-ds004279-stage1"

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
            The modified Raw object with updated description and annotations.
        """
        file_path = row.get("File Path", "")
        paradigm = _detect_paradigm(file_path)

        # Update description with eegunity metadata
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": _DEVICE_AMPLIFIER,
                "cap": _DEVICE_CAP,
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Process events: prefix with paradigm for disambiguation
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            # No annotations available
            return raw

        # Build prefix mapping based on paradigm
        if paradigm == "perception":
            event_map = _build_perception_event_map()
        elif paradigm == "production":
            event_map = _build_production_event_map()
        else:
            event_map = {}

        # Remap event annotations with paradigm prefix
        new_annotations = []
        for onset, duration, orig_desc in zip(
            events[:, 0] / raw.info["sfreq"],
            [0.0] * len(events),
            events[:, 2],
        ):
            orig_str = str(orig_desc)
            # Check if numeric and in our map
            if orig_str.isdigit():
                int_id = int(orig_str)
                if int_id in event_map:
                    desc = _prefix_event_description(event_map[int_id], paradigm)
                else:
                    desc = _prefix_event_description(orig_str, paradigm)
            else:
                desc = _prefix_event_description(orig_str, paradigm)
            new_annotations.append((onset, duration, desc))

        # Create new annotations
        if new_annotations:
            onsets = [a[0] for a in new_annotations]
            durations = [a[1] for a in new_annotations]
            descriptions = [a[2] for a in new_annotations]
            new_mne_annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
                sfreq=raw.info["sfreq"],
            )
            raw.set_annotations(new_mne_annotations)

        # Rename channels to standard names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard montage if channels are standard 10-20 names
        _try_set_montage(raw)

        # Downsample to 250 Hz for Classical Task 1 (handled by downstream)
        # raw.resample(250)  # Optional: uncomment if always needed

        return raw


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for non-standard channel names.

    Handles common variations in BrainVision/BrainAmp channel naming.
    """
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "EEG Fp1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "EEG Fp2"]),
        ("Fz", ["Fz", "EEG-Fz", "EEG Fz"]),
        ("F3", ["F3", "EEG-F3", "EEG F3"]),
        ("F4", ["F4", "EEG-F4", "EEG F4"]),
        ("F7", ["F7", "EEG-F7", "EEG F7"]),
        ("F8", ["F8", "EEG-F8", "EEG F8"]),
        ("FC5", ["FC5", "EEG-FC5", "EEG FC5"]),
        ("FC1", ["FC1", "EEG-FC1", "EEG FC1"]),
        ("FC2", ["FC2", "EEG-FC2", "EEG FC2"]),
        ("FC6", ["FC6", "EEG-FC6", "EEG FC6"]),
        ("Cz", ["Cz", "EEG-Cz", "EEG Cz"]),
        ("C3", ["C3", "EEG-C3", "EEG C3"]),
        ("C4", ["C4", "EEG-C4", "EEG C4"]),
        ("T7", ["T7", "T3", "EEG-T7", "EEG T7"]),
        ("T8", ["T8", "T4", "EEG-T8", "EEG T8"]),
        ("CP5", ["CP5", "EEG-CP5", "EEG CP5"]),
        ("CP1", ["CP1", "EEG-CP1", "EEG CP1"]),
        ("CP2", ["CP2", "EEG-CP2", "EEG CP2"]),
        ("CP6", ["CP6", "EEG-CP6", "EEG CP6"]),
        ("Pz", ["Pz", "EEG-Pz", "EEG Pz"]),
        ("P3", ["P3", "EEG-P3", "EEG P3"]),
        ("P4", ["P4", "EEG-P4", "EEG P4"]),
        ("P7", ["P7", "P7", "EEG-P7", "EEG P7"]),
        ("P8", ["P8", "P8", "EEG-P8", "EEG P8"]),
        ("POz", ["POz", "POz", "EEG-POz", "EEG POz"]),
        ("O1", ["O1", "EEG-O1", "EEG O1"]),
        ("O2", ["O2", "EEG-O2", "EEG O2"]),
        ("Oz", ["Oz", "EEG-Oz", "EEG Oz"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 10-20 montage.

    Silently skips if montage cannot be applied.
    """
    try:
        montage = mne.channels.make_standard_montage(_STANDARD_MONTAGE)
        # Only set if most channels match
        ch_set = set(mne.channels.read_ch_connectivity(montage)[0])
        raw_ch_eeg = {
            ch for ch, kind in zip(raw.ch_names, raw.get_channel_types())
            if kind == "eeg"
        }
        if len(raw_ch_eeg & ch_set) >= len(ch_set) * 0.7:
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass


KERNEL = OpenNeuroDS004279Kernel()