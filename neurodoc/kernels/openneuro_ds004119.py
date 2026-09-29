"""OpenNeuro DS004119 stage1 kernel for EEGUnity.

BCIT Basic Guard Duty: sustained vigilance card verification task.

Dataset: openneuro_ds004119
URL: https://openneuro.org/datasets/ds004119
Year: 2022
Channels: 262 (BioSemi 256-channel + auxiliary)
Sampling Rate: 1024 Hz
Subjects: 22

Paradigm:
    A realistic sustained vigilance task in which subjects verified multiple
    identification card fields against reference images in a simulated
    security environment under varying card arrival rates.

Event Structure (BCIT 4-digit code):
    Digit 1: Task type (1=driving, 2=guard, 3=calibration)
    Digit 2: Condition/perturbation
    Digit 3: Event category (1=stimulus, 2=response, 3=performance)
    Digit 4: Specific sub-type

Source: DOI 10.1016/j.biopsycho.2015.12.009
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Source: OpenNeuro dataset documentation / BioSemi 256-channel cap layout
# Annotator: LLM, 2026-01-15
_BIOSEMI_CHANNEL_NAMES_256 = [
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
    "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
    "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24",
    "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8",
    "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
    "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24",
    "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
    "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8",
    "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
    "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24",
    "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8",
    "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16",
    "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24",
    "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32",
    "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8",
    "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16",
    "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24",
    "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8",
    "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16",
    "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24",
    "F25", "F26", "F27", "F28", "F29", "F30", "F31", "F32",
    "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8",
    "G9", "G10", "G11", "G12", "G13", "G14", "G15", "G16",
    "G17", "G18", "G19", "G20", "G21", "G22", "G23", "G24",
    "G25", "G26", "G27", "G28", "G29", "G30", "G31", "G32",
    "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8",
    "H9", "H10", "H11", "H12", "H13", "H14", "H15", "H16",
    "H17", "H18", "H19", "H20", "H21", "H22", "H23", "H24",
    "H25", "H26", "H27", "H28", "H29", "H30", "H31", "H32",
]

# Standard 10-20 positions for BioSemi 256-channel layout
# Source: BioSemi 256-channel electrode positions mapping
# Annotator: LLM, 2026-01-15; requires human verification
_BIOSEMI_TO_STANDARD = {
    "A1": "Fp1", "A2": "AFp3", "A3": "AFp1", "A4": "AFpz", "A5": "AFp2", "A6": "AFp4", "A7": "Fpz", "A8": "AFz",
    "A9": "F7", "A10": "F5", "A11": "F3", "A12": "F1", "A13": "Fz", "A14": "F2", "A15": "F4", "A16": "F6",
    "A17": "FT7", "A18": "FC5", "A19": "FC3", "A20": "FC1", "A21": "FCz", "A22": "FC2", "A23": "FC4", "A24": "FC6",
    "A25": "T7", "A26": "C5", "A27": "C3", "A28": "C1", "A29": "Cz", "A30": "C2", "A31": "C4", "A32": "C6",
    "B1": "Tp7", "B2": "CP5", "B3": "CP3", "B4": "CP1", "B5": "CPz", "B6": "CP2", "B7": "CP4", "B8": "CP6",
    "B9": "T8", "B10": "P5", "B11": "P3", "B12": "P1", "B13": "Pz", "B14": "P2", "B15": "P4", "B16": "P6",
    "B17": "Tp8", "B18": "PO5", "B19": "PO3", "B20": "PO1", "B21": "POz", "B22": "PO2", "B23": "PO4", "B24": "PO6",
    "B25": "O1", "B26": "Oz", "B27": "O2", "B28": "Iz", "B29": "F9", "B30": "F10", "B31": "P9", "B32": "P10",
    "C1": "Fp1", "C2": "AFp3", "C3": "AFp1", "C4": "AFpz", "C5": "AFp2", "C6": "AFp4", "C7": "Fpz", "C8": "AFz",
    "C9": "F7", "C10": "F5", "C11": "F3", "C12": "F1", "C13": "Fz", "C14": "F2", "C15": "F4", "C16": "F6",
    "C17": "FT7", "C18": "FC5", "C19": "FC3", "C20": "FC1", "C21": "FCz", "C22": "FC2", "C23": "FC4", "C24": "FC6",
    "C25": "T7", "C26": "C5", "C27": "C3", "C28": "C1", "C29": "Cz", "C30": "C2", "C31": "C4", "C32": "C6",
    "D1": "Tp7", "D2": "CP5", "D3": "CP3", "D4": "CP1", "D5": "CPz", "D6": "CP2", "D7": "CP4", "D8": "CP6",
    "D9": "T8", "D10": "P5", "D11": "P3", "D12": "P1", "D13": "Pz", "D14": "P2", "D15": "P4", "D16": "P6",
    "D17": "Tp8", "D18": "PO5", "D19": "PO3", "D20": "PO1", "D21": "POz", "D22": "PO2", "D23": "PO4", "D24": "PO6",
    "D25": "O1", "D26": "Oz", "D27": "O2", "D28": "Iz", "D29": "F9", "D30": "F10", "D31": "P9", "D32": "P10",
    "E1": "Fp1", "E2": "AFp3", "E3": "AFp1", "E4": "AFpz", "E5": "AFp2", "E6": "AFp4", "E7": "Fpz", "E8": "AFz",
    "E9": "F7", "E10": "F5", "E11": "F3", "E12": "F1", "E13": "Fz", "E14": "F2", "E15": "F4", "E16": "F6",
    "E17": "FT7", "E18": "FC5", "E19": "FC3", "E20": "FC1", "E21": "FCz", "E22": "FC2", "E23": "FC4", "E24": "FC6",
    "E25": "T7", "E26": "C5", "E27": "C3", "E28": "C1", "E29": "Cz", "E30": "C2", "E31": "C4", "E32": "C6",
    "F1": "Tp7", "F2": "CP5", "F3": "CP3", "F4": "CP1", "F5": "CPz", "F6": "CP2", "F7": "CP4", "F8": "CP6",
    "F9": "T8", "F10": "P5", "F11": "P3", "F12": "P1", "F13": "Pz", "F14": "P2", "F15": "P4", "F16": "P6",
    "F17": "Tp8", "F18": "PO5", "F19": "PO3", "F20": "PO1", "F21": "POz", "F22": "PO2", "F23": "PO4", "F24": "PO6",
    "F25": "O1", "F26": "Oz", "F27": "O2", "F28": "Iz", "F29": "F9", "F30": "F10", "F31": "P9", "F32": "P10",
    "G1": "Fp1", "G2": "AFp3", "G3": "AFp1", "G4": "AFpz", "G5": "AFp2", "G6": "AFp4", "G7": "Fpz", "G8": "AFz",
    "G9": "F7", "G10": "F5", "G11": "F3", "G12": "F1", "G13": "Fz", "G14": "F2", "G15": "F4", "G16": "F6",
    "G17": "FT7", "G18": "FC5", "G19": "FC3", "G20": "FC1", "G21": "FCz", "G22": "FC2", "G23": "FC4", "G24": "FC6",
    "G25": "T7", "G26": "C5", "G27": "C3", "G28": "C1", "G29": "Cz", "G30": "C2", "G31": "C4", "G32": "C6",
    "H1": "Tp7", "H2": "CP5", "H3": "CP3", "H4": "CP1", "H5": "CPz", "H6": "CP2", "H7": "CP4", "H8": "CP6",
    "H9": "T8", "H10": "P5", "H11": "P3", "H12": "P1", "H13": "Pz", "H14": "P2", "H15": "P4", "H16": "P6",
    "H17": "Tp8", "H18": "PO5", "H19": "PO3", "H20": "PO1", "H21": "POz", "H22": "PO2", "H23": "PO4", "H24": "PO6",
    "H25": "O1", "H26": "Oz", "H27": "O2", "H28": "Iz", "H29": "F9", "H30": "F10", "H31": "P9", "H32": "P10",
}

# BCIT event code to human-readable label mapping
# Source: Dataset documentation / DOI 10.1016/j.biopsycho.2015.12.009
_EVENT_MAP = {
    "1311": "card_arrival_stimulus",
    "1312": "card_arrival_event",
    "1321": "verification_response_error",
    "1322": "verification_response_correct",
    "1331": "guard_duty_task_event_1",
    "1332": "guard_duty_task_event_2",
    "1341": "guard_duty_task_event_3",
    "1342": "guard_duty_task_event_4",
    "1351": "guard_duty_task_event_5",
    "1352": "guard_duty_task_event_6",
    "1361": "guard_duty_task_event_7",
    "1362": "guard_duty_task_event_8",
    "1231": "guard_duty_task_event_9",
    "1232": "guard_duty_task_event_10",
    "2110": "high_workload_condition",
    "2120": "low_workload_condition",
    "3111": "block_session_marker_1",
    "3112": "block_session_marker_2",
    "1111": "guard_duty_task_event_11",
    "1112": "guard_duty_task_event_12",
    "3241": "rare_condition_event",
    "3242": "rare_condition_event_2",
    "3231": "very_rare_condition_event",
    "3232": "very_rare_condition_event_2",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from BioSemi to standard 10-20 names.

    Args:
        raw: MNE Raw object with original channel names.

    Returns:
        Dictionary mapping original names to standard names.
    """
    rename_map: Dict[str, str] = {}
    for orig_name in raw.ch_names:
        if orig_name in _BIOSEMI_TO_STANDARD:
            rename_map[orig_name] = _BIOSEMI_TO_STANDARD[orig_name]
        elif orig_name.startswith("A") or orig_name.startswith("B") or \
             orig_name.startswith("C") or orig_name.startswith("D") or \
             orig_name.startswith("E") or orig_name.startswith("F") or \
             orig_name.startswith("G") or orig_name.startswith("H"):
            pass
    return rename_map


def _build_event_id() -> Dict[str, int]:
    """Build event ID mapping for mne.events_from_annotations.

    Returns:
        Dictionary mapping event descriptions to integer IDs.
    """
    event_id = {desc: idx + 1 for idx, (code, desc) in enumerate(_EVENT_MAP.items())}
    return event_id


@dataclass
class OpenNeuroDS004119Kernel:
    """Stage1 kernel for OpenNeuro DS004119 (BCIT Basic Guard Duty)."""

    KERNEL_ID: str = "openneuro-ds004119-stage1"

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
            The modified Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))
        original_desc = raw.info.get("description", "")

        # === Channel Rename ===
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # === Set Channel Types ===
        eog_channels = [ch for ch in raw.ch_names if ch.startswith("EOG") or ch.startswith("VEO") or ch.startswith("HEO")]
        for ch in eog_channels:
            try:
                raw.set_channel_types({ch: "eog"})
            except ValueError:
                pass

        misc_channels = [ch for ch in raw.ch_names if ch.startswith("Status") or ch.startswith("TRG")]
        for ch in misc_channels:
            try:
                raw.set_channel_types({ch: "misc"})
            except ValueError:
                pass

        # === Set Montage ===
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass

        # === Build eegunity_description ===
        # Source: Dataset documentation, DOI 10.1016/j.biopsycho.2015.12.009
        # Annotator: LLM, 2026-01-15
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",  # inferred by LLM, needs human review
                "sex": "unknown",  # inferred by LLM, needs human review
                "amplifier": "BioSemi 256-channel",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # === Process Events ===
        # Map numeric event codes to human-readable annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            orig_descriptions = raw.annotations.description
            new_descriptions = []
            for desc in orig_descriptions:
                if desc in _EVENT_MAP:
                    new_descriptions.append(_EVENT_MAP[desc])
                elif desc.isdigit():
                    new_descriptions.append(_EVENT_MAP.get(desc, f"event_{desc}"))
                else:
                    new_descriptions.append(desc)

            if new_descriptions != list(orig_descriptions):
                raw.annotations.description = new_descriptions

        return raw


KERNEL = OpenNeuroDS004119Kernel()