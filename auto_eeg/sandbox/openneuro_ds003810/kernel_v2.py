"""OpenNeuro DS003810 stage1 kernel for EEGUnity.

Motor imagery EEG dataset using low-cost consumer-grade EEG system.
Participants performed kinesthetic motor imagery of grasping movements.
Data recorded with OpenViBE (OVTK) event triggers.

Source: https://openneuro.org/datasets/ds003810
References:
  - DOI: 10.1016/j.dib.2022.108225 (Data in Brief paper)
  - DOI: 10.1016/j.heliyon.2020.e03425 (Original MI-BCI feasibility study)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# =============================================================================
# Channel Mapping for Low-Cost 15-Channel EEG System
# =============================================================================
# Source: Inferred from dataset description (low-cost consumer-grade EEG with 15 channels)
# The original dataset uses non-standard channel names (EEG-0, EEG-1, ...).
# Standard 10-20 layout with 15 channels typical for motor imagery BCI:
# Frontopolar: Fp1, Fp2
# Frontal: F7, F3, Fz, F4, F8
# Temporal: T3, T4
# Central: C3, Cz, C4
# Parietal: P3, Pz, P4
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-0": "Fp1",
    "EEG-1": "Fp2",
    "EEG-2": "F7",
    "EEG-3": "F3",
    "EEG-4": "Fz",
    "EEG-5": "F4",
    "EEG-6": "F8",
    "EEG-7": "T3",
    "EEG-8": "C3",
    "EEG-9": "Cz",
    "EEG-10": "C4",
    "EEG-11": "T4",
    "EEG-12": "P3",
    "EEG-13": "Pz",
    "EEG-14": "P4",
}

# Standard 10-20 montage channels (15-channel subset)
_STANDARD_MONTAGE_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T3", "C3", "Cz", "C4", "T4", "P3", "Pz", "P4"
]

# =============================================================================
# Subject Information (Inferred from dataset papers)
# =============================================================================
# Source: DOI: 10.1016/j.heliyon.2020.e03425 - "healthy participants, aged
# between 22 and 45 years, all right-handed" # LLM 推断，需人类复核
# Source: DOI: 10.1016/j.dib.2022.108225 - demographic info in dataset
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
_SUBJECT_AGE: str = "22-45"  # Range as per papers
_SUBJECT_SEX: str = "unknown"  # Not explicitly stated in provided docs
_SUBJECT_HANDEDNESS: str = "right"  # Per original study description

# Device info from dataset description
_AMPLIFIER: str = "low-cost consumer-grade EEG"  # LLM 推断，需人类复核
_CAP: str = "unknown"  # Not specified in available docs


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from actual channel names to standard names."""
    rename_map: Dict[str, str] = {}
    for source_name, target_name in _CHANNEL_RENAME_MAP.items():
        if source_name in raw.ch_names:
            rename_map[source_name] = target_name
    return rename_map


def _get_available_montage_channels(raw: mne.io.BaseRaw) -> List[str]:
    """Return list of channels that have valid positions in standard_1020."""
    montage = mne.channels.make_standard_montage("standard_1020")
    available = []
    for ch in raw.ch_names:
        if ch in montage.ch_names:
            available.append(ch)
    return available


@dataclass
class OpenNeuroDS003810Kernel:
    """Stage1 kernel for OpenNeuro DS003810 motor imagery dataset."""

    KERNEL_ID: str = "openneuro-ds003810-stage1"

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
            Preprocessed Raw object with updated metadata and annotations.
        """
        # -------------------------------------------------------------------------
        # Step 1: Channel renaming (BEFORE set_montage)
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_renamed = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if existing_renamed:
                print(f"[Kernel] Renaming {len(existing_renamed)} channels: {existing_renamed}")
                raw.rename_channels(existing_renamed)

        # -------------------------------------------------------------------------
        # Step 2: Set montage (standard 10-20 system)
        # -------------------------------------------------------------------------
        available_channels = _get_available_montage_channels(raw)
        if available_channels:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="warn")
                print(f"[Kernel] Montage set for {len(available_channels)} channels")
            except Exception as e:
                print(f"[Kernel] Warning: Could not set montage: {e}")
        else:
            print("[Kernel] Warning: No standard channels found for montage")

        # -------------------------------------------------------------------------
        # Step 3: Update description with eegunity_description
        # -------------------------------------------------------------------------
        original_description = raw.info.get("description", "")
        if isinstance(original_description, dict):
            original_description = json.dumps(original_description)

        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": _SUBJECT_AGE,
                "sex": _SUBJECT_SEX,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _SUBJECT_HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # Step 4: Process events and create annotations
        # -------------------------------------------------------------------------
        # Read existing annotations from raw
        original_annotations = raw.annotations
        
        if len(original_annotations) > 0:
            # Map numeric event codes to descriptive strings based on OpenViBE OVTK standards
            # OVTK_GDF_* events are standard OpenViBE stimulation codes for BCI paradigms
            event_description_map = {
                "769": "OVTK_GDF_Right",
                "770": "OVTK_GDF_Tongue",
                "32773": "OVTK_GDF_Start_Of_Trial",
                "32774": "OVTK_GDF_Cross_On_Screen",
                "32775": "OVTK_GDF_Feedback_Continuous",
                "32776": "OVTK_GDF_End_Of_Trial",
                "32781": "OVTK_GDF_Correct",
                "32782": "OVTK_GDF_Incorrect",
                "32786": "OVTK_StimulationId_BaselineStart",
                "32787": "OVTK_StimulationId_BaselineStop",
                "32791": "OVTK_StimulationId_Beep",
                "32792": "OVTK_StimulationId_Train",
                "1": "OVTK_StimulationId_ExperimentStart",
                "2": "OVTK_StimulationId_ExperimentStop",
                "3": "OVTK_GDF_End_Of_Session",
            }
            
            # Also handle string descriptions from GDF files
            string_event_map = {
                "769": "OVTK_GDF_Right",
                "770": "OVTK_GDF_Tongue",
                "32773": "OVTK_GDF_Start_Of_Trial",
                "32774": "OVTK_GDF_Cross_On_Screen",
                "32775": "OVTK_GDF_Feedback_Continuous",
                "32776": "OVTK_GDF_End_Of_Trial",
                "32781": "OVTK_GDF_Correct",
                "32782": "OVTK_GDF_Incorrect",
                "32786": "OVTK_StimulationId_BaselineStart",
                "32787": "OVTK_StimulationId_BaselineStop",
                "32791": "OVTK_StimulationId_Beep",
                "32792": "OVTK_StimulationId_Train",
                "1": "OVTK_StimulationId_ExperimentStart",
                "2": "OVTK_StimulationId_ExperimentStop",
                "3": "OVTK_GDF_End_Of_Session",
            }
            
            # Update annotation descriptions
            new_descriptions = []
            for desc in original_annotations.description:
                desc_str = str(desc)
                if desc_str in event_description_map:
                    new_descriptions.append(event_description_map[desc_str])
                elif desc_str in string_event_map:
                    new_descriptions.append(string_event_map[desc_str])
                else:
                    new_descriptions.append(desc_str)
            
            # Create new annotations with updated descriptions
            new_onset = original_annotations.onset.tolist()
            new_duration = original_annotations.duration.tolist()
            
            raw.set_annotations(
                mne.Annotations(
                    onset=new_onset,
                    duration=new_duration,
                    description=new_descriptions,
                    ch_names=None
                )
            )
            
            print(f"[Kernel] Processed {len(original_annotations)} events")
        else:
            print("[Kernel] No events found in raw annotations")

        # -------------------------------------------------------------------------
        # Step 5: Store eegunity_description in temp (not dataset_info)
        # -------------------------------------------------------------------------
        # Use info['temp'] instead of info['dataset_info'] as后者 is not allowed
        raw.info["temp"] = {
            "eegunity_description": {
                "age": _SUBJECT_AGE,
                "sex": _SUBJECT_SEX,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _SUBJECT_HANDEDNESS,
            },
        }

        return raw


KERNEL = OpenNeuroDS003810Kernel()