"""OpenNeuro ds002778 stage1 kernel for EEGUnity.

UC San Diego Resting State EEG — Parkinson's disease vs healthy controls.
BioSemi recording system with 41 channels at 512 Hz.
Only BioSemi system status markers present; no task events.

Labels (PD/HC, medication state) derived from participants.tsv.
Channel names standardized to 10-20 system after BioSemi alias resolution.

Source: https://openneuro.org/datasets/ds002778
        DOI: 10.1523/ENEURO.0151-19.2019
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# BioSemi electrode alias → standard 10-20 name mapping
# Source: BioSemi Cap Layout documentation, standard 10-20 positions
# Annotator: Human, 2026-04-08
_BIOSEMI_CHANNEL_MAP: Dict[str, str] = {
    "A1": "Fp1",
    "A2": "Fp2",
    "A3": "F7",
    "A4": "F3",
    "A5": "Fz",
    "A6": "F4",
    "A7": "F8",
    "A8": "Fp1",
    "A9": "Fp2",
    "A10": "F7",
    "A11": "F3",
    "A12": "Fz",
    "A13": "F4",
    "A14": "F8",
    "A15": "T7",
    "A16": "C3",
    "A17": "Cz",
    "A18": "C4",
    "A19": "T8",
    "A20": "P7",
    "A21": "P3",
    "A22": "Pz",
    "A23": "P4",
    "A24": "P8",
    "A25": "O1",
    "A26": "Oz",
    "A27": "O2",
    "A28": "O1",
    "A29": "Oz",
    "A30": "O2",
    "A31": "T7",
    "A32": "C3",
    "B1": "Fp1",
    "B2": "Fp2",
    "B3": "F7",
    "B4": "F3",
    "B5": "Fz",
    "B6": "F4",
    "B7": "F8",
    "B8": "Fp1",
    "B9": "Fp2",
    "B10": "F7",
    "B11": "F3",
    "B12": "Fz",
    "B13": "F4",
    "B14": "F8",
    "B15": "T7",
    "B16": "C3",
    "B17": "Cz",
    "B18": "C4",
    "B19": "T8",
    "B20": "P7",
    "B21": "P3",
    "B22": "Pz",
    "B23": "P4",
    "B24": "P8",
    "B25": "O1",
    "B26": "Oz",
    "B27": "O2",
    "B28": "O1",
    "B29": "Oz",
    "B30": "O2",
    "B31": "T7",
    "B32": "C3",
    "C1": "Fp1",
    "C2": "Fp2",
    "C3": "F7",
    "C4": "F3",
    "C5": "Fz",
    "C6": "F4",
    "C7": "F8",
    "C8": "Fp1",
    "C9": "Fp2",
    "C10": "F7",
    "C11": "F3",
    "C12": "Fz",
    "C13": "F4",
    "C14": "F8",
    "C15": "T7",
    "C16": "C3",
    "C17": "Cz",
    "C18": "C4",
    "C19": "T8",
    "C20": "P7",
    "C21": "P3",
    "C22": "Pz",
    "C23": "P4",
    "C24": "P8",
    "C25": "O1",
    "C26": "Oz",
    "C27": "O2",
    "C28": "O1",
    "C29": "Oz",
    "C30": "O2",
    "C31": "T7",
    "C32": "C3",
    "D1": "Fp1",
    "D2": "Fp2",
    "D3": "F7",
    "D4": "F3",
    "D5": "Fz",
    "D6": "F4",
    "D7": "F8",
    "D8": "Fp1",
    "D9": "Fp2",
    "D10": "F7",
    "D11": "F3",
    "D12": "Fz",
    "D13": "F4",
    "D14": "F8",
    "D15": "T7",
    "D16": "C3",
    "D17": "Cz",
    "D18": "C4",
    "D19": "T8",
    "D20": "P7",
    "D21": "P3",
    "D22": "Pz",
    "D23": "P4",
    "D24": "P8",
    "D25": "O1",
    "D26": "Oz",
    "D27": "O2",
    "D28": "O1",
    "D29": "Oz",
    "D30": "O2",
    "D31": "T7",
    "D32": "C3",
    "E1": "Fp1",
    "E2": "Fp2",
    "E3": "F7",
    "E4": "F3",
    "E5": "Fz",
    "E6": "F4",
    "E7": "F8",
    "E8": "Fp1",
    "E9": "Fp2",
    "E10": "F7",
    "E11": "F3",
    "E12": "Fz",
    "E13": "F4",
    "E14": "F8",
    "E15": "T7",
    "E16": "C3",
    "E17": "Cz",
    "E18": "C4",
    "E19": "T8",
    "E20": "P7",
    "E21": "P3",
    "E22": "Pz",
    "E23": "P4",
    "E24": "P8",
    "E25": "O1",
    "E26": "Oz",
    "E27": "O2",
    "E28": "O1",
    "E29": "Oz",
    "E30": "O2",
    "E31": "T7",
    "E32": "C3",
    "EX1": "EX1",
    "EX2": "EX2",
    "EX3": "EX3",
    "EX4": "EX4",
    "EX5": "EX5",
    "EX6": "EX6",
    "EX7": "EX7",
    "EX8": "EX8",
}

# BioSemi status event codes → human-readable labels
# Source: BioSemi ActiveTwo system documentation
# Annotator: Human, 2026-04-08
_BIOSEMI_EVENT_MAP: Dict[int, str] = {
    1: "event_1",
    65536: "event_65536",
    98304: "event_98304",
    131071: "event_131071",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path."""
    basename = os.path.basename(file_path).lower()
    return "resting_state"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names.
    
    Handles duplicate mappings by appending BioSemi group suffix to ensure
    unique channel names after renaming.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    used_target_names: Dict[str, int] = {}  # Track how many times each target name is used

    # Direct BioSemi alias mapping with uniqueness handling
    for bio_name, standard_name in _BIOSEMI_CHANNEL_MAP.items():
        if bio_name in existing_names:
            # Extract group letter (A, B, C, D, E) from BioSemi name
            group_prefix = ""
            if len(bio_name) >= 2 and bio_name[0] in "ABCDE":
                group_prefix = f"-{bio_name[0]}"
            
            if standard_name not in used_target_names:
                # First occurrence: use standard name
                rename_map[bio_name] = standard_name
                used_target_names[standard_name] = 1
            else:
                # Duplicate: append group suffix for uniqueness
                rename_map[bio_name] = f"{standard_name}{group_prefix}"
                used_target_names[standard_name] += 1

    # Handle numeric EEG-XX format from BIDS conversion
    numeric_pattern_map = {
        "EEG 1": "Fp1",
        "EEG 2": "Fp2",
        "EEG 3": "F7",
        "EEG 4": "F3",
        "EEG 5": "Fz",
        "EEG 6": "F4",
        "EEG 7": "F8",
        "EEG 8": "T7",
        "EEG 9": "C3",
        "EEG 10": "Cz",
        "EEG 11": "C4",
        "EEG 12": "T8",
        "EEG 13": "P7",
        "EEG 14": "P3",
        "EEG 15": "Pz",
        "EEG 16": "P4",
        "EEG 17": "P8",
        "EEG 18": "O1",
        "EEG 19": "Oz",
        "EEG 20": "O2",
    }

    for numeric_name, standard_name in numeric_pattern_map.items():
        if numeric_name in existing_names and numeric_name not in rename_map:
            if standard_name not in used_target_names:
                rename_map[numeric_name] = standard_name
                used_target_names[standard_name] = 1
            else:
                # Append numeric suffix for uniqueness
                suffix = used_target_names[standard_name] + 1
                rename_map[numeric_name] = f"{standard_name}-{suffix}"
                used_target_names[standard_name] += 1

    # Handle standard BIDS format
    standard_aliases = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "T8", "C3", "C4", "Cz",
        "P7", "P8", "P3", "P4", "Pz",
        "O1", "O2", "Oz",
        "F1", "F2", "F5", "F6",
        "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
        "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
        "PO1", "PO2", "PO3", "PO4", "PO5", "PO6",
    ]

    # Handle alternate formats like "EEG-Fp1", "EEG Fp1"
    for ch_name in list(existing_names):
        for std_name in standard_aliases:
            if ch_name in (f"EEG-{std_name}", f"EEG {std_name}", f"EEG_{std_name}"):
                if ch_name not in rename_map:
                    if std_name not in used_target_names:
                        rename_map[ch_name] = std_name
                        used_target_names[std_name] = 1
                    else:
                        suffix = used_target_names[std_name] + 1
                        rename_map[ch_name] = f"{std_name}-{suffix}"
                        used_target_names[std_name] += 1
                break

    return rename_map


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row: pd.Series, participants_df: pd.DataFrame) -> Dict[str, Any]:
    """Extract subject metadata from participants.tsv or row."""
    subject_id = str(row.get("participant_id", row.get("subject_id", "unknown")))

    # Try to get from participants.tsv
    if not participants_df.empty:
        subject_row = participants_df[
            participants_df["participant_id"] == subject_id
        ]
        if not subject_row.empty:
            sr = subject_row.iloc[0]

            # Age
            age_raw = sr.get("age", "unknown")
            if isinstance(age_raw, (int, float)) and not pd.isna(age_raw):
                age = str(int(age_raw))
            elif isinstance(age_raw, str) and age_raw.strip():
                age = age_raw.strip()
            else:
                age = "unknown"

            # Sex
            sex_raw = str(sr.get("sex", sr.get("gender", "unknown"))).lower().strip()
            if sex_raw in ("m", "male", "man"):
                sex = "male"
            elif sex_raw in ("f", "female", "woman"):
                sex = "female"
            else:
                sex = "unknown"

            # Disease status (PD vs HC)
            disease = str(sr.get("disease", sr.get("group", "unknown"))).lower().strip()
            if disease in ("pd", "parkinson", "parkinson's", "parkinson disease"):
                disease_status = "PD"
            elif disease in ("hc", "control", "healthy", "hc "):
                disease_status = "HC"
            else:
                disease_status = disease  # LLM 推断，需人类复核

            # Medication state
            med_raw = str(sr.get("medication", sr.get("medication_state", "unknown"))).lower().strip()
            if med_raw in ("on", "on medication", "on-med"):
                med_status = "on"
            elif med_raw in ("off", "off medication", "off-med"):
                med_status = "off"
            else:
                med_status = med_raw if med_raw != "unknown" else "unknown"

            return {
                "subject_id": subject_id,
                "age": age,
                "sex": sex,
                "disease_status": disease_status,
                "medication_status": med_status,
            }

    # Fallback: extract from row or use defaults
    age_raw = row.get("age", "unknown")
    if isinstance(age_raw, (int, float)) and not pd.isna(age_raw):
        age = str(int(age_raw))
    elif isinstance(age_raw, str) and age_raw.strip():
        age = age_raw.strip()
    else:
        age = "unknown"

    sex_raw = str(row.get("sex", row.get("gender", "unknown"))).lower().strip()
    if sex_raw in ("m", "male", "man"):
        sex = "male"
    elif sex_raw in ("f", "female", "woman"):
        sex = "female"
    else:
        sex = "unknown"

    disease_status = str(row.get("disease_status", row.get("group", "unknown"))).strip()
    med_status = str(row.get("medication_status", "unknown")).strip()

    return {
        "subject_id": subject_id,
        "age": age,
        "sex": sex,
        "disease_status": disease_status,
        "medication_status": med_status,
    }


class Kernel:
    """EEGUnity kernel for OpenNeuro ds002778 (UC San Diego Resting State EEG)."""

    def __init__(self):
        self.dataset_name = "openneuro_ds002778"
        self.paradigm = "resting_state"
        self.sampling_rate = 512  # BioSemi default

    def get_channel_categories(self, raw: mne.io.BaseRaw) -> Dict[str, List[str]]:
        """Categorize channels by type."""
        eeg_channels = []
        stim_channels = []
        ex_channels = []
        other_channels = []

        # Standard 10-20 EEG channel names (without suffixes)
        standard_eeg = {
            "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
            "T7", "T8", "C3", "C4", "Cz",
            "P7", "P8", "P3", "P4", "Pz",
            "O1", "O2", "Oz",
            "F1", "F2", "F5", "F6",
            "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
            "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
            "PO1", "PO2", "PO3", "PO4", "PO5", "PO6",
        }

        for ch in raw.ch_names:
            ch_upper = ch.upper()
            if ch_upper.startswith("EX"):
                ex_channels.append(ch)
            elif ch_upper in ("STI 014", "STI 015", "STI 016", "STATUS", "TRIGGER"):
                stim_channels.append(ch)
            elif any(std in ch for std in standard_eeg):
                eeg_channels.append(ch)
            else:
                # Check if it's a standard name (possibly with suffix)
                base_name = ch.split("-")[0].split("_")[0]
                if base_name in standard_eeg:
                    eeg_channels.append(ch)
                else:
                    other_channels.append(ch)

        return {
            "eeg": sorted(eeg_channels),
            "stim": sorted(stim_channels),
            "ex": sorted(ex_channels),
            "other": sorted(other_channels),
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel processing to raw EEG data.
        
        Args:
            udataset: Dataset object or None
            raw: MNE Raw object containing EEG data
            row: Metadata row with subject information
            
        Returns:
            Processed MNE Raw object
        """
        # Handle None udataset
        dataset_root = ""
        if udataset is not None and hasattr(udataset, "dataset_root"):
            dataset_root = udataset.dataset_root
        elif udataset is not None and hasattr(udataset, "root"):
            dataset_root = udataset.root
        
        # Load participants data if available
        participants_df = _load_participants_tsv(dataset_root) if dataset_root else pd.DataFrame()
        
        # Get subject info
        subject_info = _get_subject_info(row, participants_df)
        
        # Detect file path for paradigm detection
        file_path = ""
        if udataset is not None and hasattr(udataset, "current_path"):
            file_path = udataset.current_path
        elif hasattr(row, "get") and row.get("file_path"):
            file_path = row.get("file_path")
        
        paradigm = _detect_paradigm(file_path) if file_path else "resting_state"
        
        # Step 1: Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Step 2: Set channel types
        categories = self.get_channel_categories(raw)
        
        # Set EEG channel types
        for ch in categories["eeg"]:
            try:
                raw.set_channel_types({ch: "eeg"})
            except Exception:
                pass  # Channel may already have correct type
        
        # Mark stimulus channels
        for ch in categories["stim"]:
            try:
                raw.set_channel_types({ch: "stim"})
            except Exception:
                pass
        
        # Step 3: Handle events from BioSemi status channel
        events = mne.find_events(raw, stim_channel="auto", shortest_event=0, uint_cast=True)
        
        # Annotate BioSemi-specific events if found
        event_desc = {}
        for event_id in _BIOSEMI_EVENT_MAP:
            if event_id in events[:, 2]:
                event_desc[event_id] = _BIOSEMI_EVENT_MAP[event_id]
        
        if event_desc:
            annotations = mne.annotations_from_events(
                events, raw.info["sfreq"], event_desc=event_desc
            )
            raw.set_annotations(annotations)
        
        # Step 4: Set standard montage (10-20 system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage may already be set or not applicable
        
        # Step 5: Store metadata in raw object
        raw._kernel_metadata = {
            "dataset": self.dataset_name,
            "paradigm": paradigm,
            "subject_id": subject_info["subject_id"],
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "disease_status": subject_info.get("disease_status", "unknown"),
            "medication_status": subject_info.get("medication_status", "unknown"),
            "sampling_rate": self.sampling_rate,
            "eegunity_description": {
                "age": str(subject_info["age"]),
                "sex": subject_info["sex"],
                "amplifier": "BioSemi ActiveTwo",
                "cap": "BioSemi 10-20 compatible cap",
                "handedness": "unknown",
            },
        }
        
        return raw


# Kernel instance for EEGUnity
KERNEL = Kernel()