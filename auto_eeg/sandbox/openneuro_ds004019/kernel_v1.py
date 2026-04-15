"""OpenNeuro DS004019 stage1 kernel for EEGUnity.

Effect of obesity on arithmetic processing in preteens with high and low math skills.
An event-related potentials study.

Source: https://openneuro.org/datasets/ds004019
Paper DOI: 10.3389/fnhum.2022.760234
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# EGI 128-channel HydroCel mapping to standard 10-20 positions
# Source: EGI HydroCel Geodesic Sensor Net technical specifications
# Annotator: LLM, 2026-01-15 - LLM 推断，需人类复核
_EGI_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 locations from EGI E1-E128
    "E1": "Fp1", "E2": "AF7", "E3": "AF3", "E4": "AFz", "E5": "AF4", "E6": "AF8",
    "E7": "F7", "E8": "F5", "E9": "F3", "E10": "F1", "E11": "Fz", "E12": "F2",
    "E13": "F4", "E14": "F6", "E15": "F8", "E16": "FT7", "E17": "FC5", "E18": "FC3",
    "E19": "FC1", "E20": "FCz", "E21": "FC2", "E22": "FC4", "E23": "FC6", "E24": "FT8",
    "E25": "T7", "E26": "C5", "E27": "C3", "E28": "C1", "E29": "Cz", "E30": "C2",
    "E31": "C4", "E32": "C6", "E33": "T8", "E34": "TP7", "E35": "CP5", "E36": "CP3",
    "E37": "CP1", "E38": "CPz", "E39": "CP2", "E40": "CP4", "E41": "CP6", "E42": "TP8",
    "E43": "P7", "E44": "P5", "E45": "P3", "E46": "P1", "E47": "Pz", "E48": "P2",
    "E49": "P4", "E50": "P6", "E51": "P8", "E52": "PO7", "E53": "PO3", "E54": "POz",
    "E55": "PO4", "E56": "PO8", "E57": "O1", "E58": "Oz", "E59": "O2",
    # Additional EGI channels E60-E128 (peripheral/hybrid locations)
    "E60": "PO9", "E61": "PO10", "E62": "O9", "E63": "O10",
    # EGI also includes reference and ground channels
    "E127": "Cz",  # EGI reference - treat as vertex
    "E128": "GND",  # EGI ground
}

# Non-EEG channels to be excluded or renamed
_NON_EEG_CHANNELS: Dict[str, str] = {
    "ECG": "ecg",
    " Resp": "resp",
    "Respiration": "resp",
    " respiration": "resp",
    "SP": "stim",
    "Stim": "stim",
}

# Default subject metadata (ages 9-10 preteens from paper)
# Source: Paper DOI 10.3389/fnhum.2022.760234 - Table 1 demographic characteristics
# Annotator: LLM, 2026-01-15 - LLM 推断，需人类复核
_DEFAULT_SUBJECT_INFO: Dict[str, Dict[str, str]] = {
    "age": "9-10",  # Paper states ages 9-10
    "sex": "unknown",
    "amplifier": "EGI 128-channel HydroCel Geodesic Sensor Net",
    "cap": "HydroCel GSN 128-channel (Ag/AgCl)",
    "handedness": "unknown",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI E1-E128 to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for egi_name, standard_name in _EGI_CHANNEL_MAP.items():
        if egi_name in existing_names:
            rename_map[egi_name] = standard_name
    
    # Also handle variations like "E001", "E01", "EEG E1"
    for ch in list(existing_names):
        match = re.match(r'^(?:EEG\s*)?E(\d{1,3})$', ch, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num in range(1, 130):
                egi_name = f"E{num}"
                if egi_name in _EGI_CHANNEL_MAP:
                    rename_map[ch] = _EGI_CHANNEL_MAP[egi_name]
    
    return rename_map


def _identify_non_eeg_channels(raw: mne.io.BaseRaw) -> List[str]:
    """Identify non-EEG channels in the raw data."""
    non_eeg: List[str] = []
    for ch in raw.ch_names:
        ch_lower = ch.lower()
        # Check for ECG, respiration, stimulus channels
        if any(keyword in ch_lower for keyword in ["ecg", "resp", "sp", "stim", "gdp", "gnd", "ref"]):
            non_eeg.append(ch)
    return non_eeg


def _map_event_code(code: Any) -> str:
    """Map numeric event codes to human-readable labels."""
    code_map = {
        0: "0",      # Incorrect response
        1: "1",      # Correct response
        2: "prob",   # Arithmetic problem onset
        3: "bgin",   # Trial beginning / delay period onset
        4: "ch++",   # Choice/comparison stimulus onset
        5: "face",   # Verification digit onset
        6: "resp",   # Participant button-press response
        10: "sync",  # Hardware sync pulse (admin)
        11: "CELL",  # Cell/block marker (admin)
        12: "SESS",  # Session start marker (admin)
    }
    
    try:
        code_int = int(code)
        return code_map.get(code_int, str(code))
    except (ValueError, TypeError):
        return str(code)


class OpenNeuroDS004019Kernel:
    """Stage1 kernel for OpenNeuro DS004019 dataset.
    
    Effect of obesity on arithmetic processing in preteens.
    62 subjects, 132 channels, 500 Hz sampling rate.
    EGI 128-channel HydroCel Geodesic Sensor Net.
    """

    KERNEL_ID: str = "openneuro-ds004019-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with File Path, Subject ID, etc.
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and events.
        """
        # --- 1. Channel renaming ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Only rename if we have a valid mapping
            valid_renames = {}
            for old_name, new_name in rename_map.items():
                if old_name in raw.ch_names:
                    valid_renames[old_name] = new_name
            if valid_renames:
                print(f"[DS004019] Renaming {len(valid_renames)} channels: {list(valid_renames.values())[:5]}...")
                raw.rename_channels(valid_renames)
        
        # --- 2. Set montage (after renaming) ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Get only channels that exist in both raw and montage
            ch_names_in_montage = set(montage.ch_names)
            ch_names_in_raw = set(raw.ch_names)
            common_chs = list(ch_names_in_montage & ch_names_in_raw)
            
            if len(common_chs) >= 60:  # At least ~60 standard EEG channels
                raw.set_montage(montage, on_missing="ignore")
                print(f"[DS004019] Set standard_1020 montage for {len(common_chs)} channels")
        except Exception as e:
            print(f"[DS004019] Warning: Could not set montage: {e}")
        
        # --- 3. Process events from annotations or stim channel ---
        # Get original description
        original_description = raw.info.get("description", "")
        
        # Extract subject info from row or use defaults
        subject_id = str(row.get("Subject", row.get("subject_id", "unknown")))
        age = _DEFAULT_SUBJECT_INFO["age"]
        sex = _DEFAULT_SUBJECT_INFO["sex"]
        amplifier = _DEFAULT_SUBJECT_INFO["amplifier"]
        cap = _DEFAULT_SUBJECT_INFO["cap"]
        handedness = _DEFAULT_SUBJECT_INFO["handedness"]
        
        # Try to read participants.tsv if available
        dataset_path = row.get("DatasetPath", "")
        participants_file = os.path.join(dataset_path, "participants.tsv") if dataset_path else None
        
        if participants_file and os.path.exists(participants_file):
            import pandas as pd
            try:
                participants_df = pd.read_csv(participants_file, sep="\t")
                # Match subject ID format (may be sub-01, S01, etc.)
                subject_pattern = re.sub(r'[^a-zA-Z0-9]', '', subject_id.lower())
                for idx, p_row in participants_df.iterrows():
                    p_id = str(p_row.get("participant_id", ""))
                    if re.sub(r'[^a-zA-Z0-9]', '', p_id.lower()) == subject_pattern:
                        if "age" in p_row and pd.notna(p_row["age"]):
                            age = str(int(p_row["age"]))
                        if "sex" in p_row and pd.notna(p_row["sex"]):
                            sex = str(p_row["sex"]).lower()
                            if sex not in ["male", "female"]:
                                sex = "unknown"
                        break
            except Exception as e:
                print(f"[DS004019] Warning: Could not read participants.tsv: {e}")
        
        # --- 4. Set eegunity_description ---
        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # --- 5. Process events ---
        # Check if annotations exist, if not try to read events.tsv
        if len(raw.annotations) == 0:
            # Try to find events.tsv file
            file_path = row.get("FilePath", row.get("file_path", ""))
            if file_path:
                base_dir = os.path.dirname(file_path)
                events_file = os.path.join(base_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_events.tsv")
                
                if not os.path.exists(events_file):
                    # Try parent directory
                    events_file = os.path.join(os.path.dirname(base_dir), "events.tsv")
                
                if os.path.exists(events_file):
                    import pandas as pd
                    try:
                        events_df = pd.read_csv(events_file, sep="\t")
                        if "onset" in events_df.columns and "value" in events_df.columns:
                            onset_col = events_df["onset"].values
                            duration = events_df.get("duration", [0] * len(onset_col))
                            if isinstance(duration, (int, float)):
                                duration = [duration] * len(onset_col)
                            
                            # Map event values to labels
                            descriptions = []
                            for val in events_df["value"].values:
                                desc = _map_event_code(val)
                                descriptions.append(desc)
                            
                            annotations = mne.Annotations(
                                onset=np.array(onset_col),
                                duration=np.array(duration[:len(onset_col)]),
                                description=descriptions,
                            )
                            raw.set_annotations(annotations)
                            print(f"[DS004019] Loaded {len(events_df)} events from events.tsv")
                    except Exception as e:
                        print(f"[DS004019] Warning: Could not read events.tsv: {e}")
        
        # If still no annotations, try reading from stim channel
        if len(raw.annotations) == 0:
            try:
                events, event_id = mne.events_from_annotations(raw)
                print(f"[DS004019] Found {len(events)} events from annotations")
            except Exception as e:
                print(f"[DS004019] Warning: Could not extract events: {e}")
        
        # --- 6. Remap numeric events to string labels ---
        try:
            events, event_id = mne.events_from_annotations(raw)
            
            # Build remapping for numeric codes
            remap_dict = {}
            for desc_str, code_int in event_id.items():
                try:
                    code_num = int(desc_str)
                    new_desc = _map_event_code(code_num)
                    if new_desc != desc_str:
                        remap_dict[desc_str] = new_desc
                except (ValueError, TypeError):
                    pass  # Keep original string labels
            
            if remap_dict:
                # Create new annotations with remapped labels
                new_descriptions = []
                for desc in raw.annotations.description:
                    new_desc = remap_dict.get(desc, desc)
                    new_descriptions.append(new_desc)
                
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                )
                raw.set_annotations(new_annotations)
                print(f"[DS004019] Remapped {len(remap_dict)} event types")
        except Exception as e:
            print(f"[DS004019] Warning: Event remapping failed: {e}")
        
        # --- 7. Remove non-EEG channels (ECG, respiration, etc.) ---
        non_eeg_channels = _identify_non_eeg_channels(raw)
        if non_eeg_channels:
            print(f"[DS004019] Identified {len(non_eeg_channels)} non-EEG channels: {non_eeg_channels[:5]}...")
            # Note: We keep them but could drop if needed
            # raw.drop_channels([ch for ch in non_eeg_channels if ch in raw.ch_names])
        
        return raw


KERNEL = OpenNeuroDS004019Kernel()