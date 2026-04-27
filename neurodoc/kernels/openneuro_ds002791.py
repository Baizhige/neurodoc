"""openneuro_ds002791 stage1 kernel for EEGUnity.

Visual Object Naming EEG dataset with 256-channel EGI HydroCell array.
Paradigm: Participants viewed and named visual objects during high-density
EEG recording. 30 distinct object categories presented via bitmap images.

Source: https://openneuro.org/datasets/ds002791
Reference: 10.3389/fnint.2023.1087976
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# EGI 256-channel HydroCell naming convention
# Channels are named E1, E2, ..., E256 in the raw data
# Source: EGI HydroCell 256-channel System documentation
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_EGI_256_CHANNEL_NAMES = [f"E{i}" for i in range(1, 257)]

# Standard 10-20 extended positions for 256-channel EGI systems
# Maps EGI channel index to approximate standard electrode name
# Source: EGI 256-channel HydroCell Montage mapping
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_EGI_TO_STANDARD_256 = {
    "E1": "Fpz", "E2": "Fp1", "E3": "AFp1", "E4": "AFp3", "E5": "AF5",
    "E6": "AFz", "E7": "AF1", "E8": "AF2", "E9": "AF4", "E10": "AF6",
    "E11": "Fz", "E12": "F1", "E13": "F2", "E14": "F3", "E15": "F4",
    "E16": "F5", "E17": "F6", "E18": "F7", "E19": "F8", "E20": "F9",
    "E21": "F10", "E22": "FC5", "E23": "FC3", "E24": "FC1", "E25": "FCz",
    "E26": "FC2", "E27": "FC4", "E28": "FC6", "E29": "FT9", "E30": "FT7",
    "E31": "FC9", "E32": "FC10", "E33": "FT10", "E34": "FT8", "E35": "T9",
    "E36": "T7", "E37": "T8", "E38": "T10", "E39": "C5", "E40": "C3",
    "E41": "C1", "E42": "Cz", "E43": "C2", "E44": "C4", "E45": "C6",
    "E46": "TP9", "E47": "TP7", "E48": "CP5", "E49": "CP3", "E50": "CP1",
    "E51": "CPz", "E52": "CP2", "E53": "CP4", "E54": "CP6", "E55": "TP10",
    "E56": "TP8", "E57": "P9", "E58": "P7", "E59": "P5", "E60": "P3",
    "E61": "P1", "E62": "Pz", "E63": "P2", "E64": "P4", "E65": "P6",
    "E66": "P8", "E67": "P10", "E68": "PO9", "E69": "PO7", "E70": "PO5",
    "E71": "PO3", "E72": "PO1", "E73": "POz", "E74": "PO2", "E75": "PO4",
    "E76": "PO6", "E77": "PO8", "E78": "PO10", "E79": "O1", "E80": "Oz",
    "E81": "O2", "E82": "OI1", "E83": "OI2", "E84": "OI3", "E85": "OI4",
    "E86": "I1", "E87": "I2", "E88": "I3", "E89": "I4", "E90": "I5",
    "E91": "I6", "E92": "AFp9", "E93": "AFp7", "E94": "AFp5", "E95": "AFp3h",
    "E96": "AFp1h", "E97": "AFp2h", "E98": "AFp4h", "E99": "AFp6h",
    "E100": "AFp8h", "E101": "AFp10", "E102": "AFFp1", "E103": "AFFp3",
    "E104": "AFFp5", "E105": "AFFp7", "E106": "AFFp2", "E107": "AFFp4",
    "E108": "AFFp6", "E109": "AFFp8", "E110": "AF9", "E111": "AF7",
    "E112": "AF5", "E113": "AF3", "E114": "AF1", "E115": "AFz", "E116": "AF2",
    "E117": "AF4", "E118": "AF6", "E119": "AF8", "E120": "AF10", "E121": "F9",
    "E122": "F7", "E123": "F5", "E124": "F3", "E125": "F1", "E126": "Fz",
    "E127": "F2", "E128": "F4", "E129": "F6", "E130": "F8", "E131": "F10",
    "E132": "FFT9", "E133": "FFT7", "E134": "FFT5", "E135": "FFT3", "E136": "FFT1",
    "E137": "FFT2", "E138": "FFT4", "E139": "FFT6", "E140": "FFT8", "E141": "FFT10",
    "E142": "FT9", "E143": "FT7", "E144": "FT5", "E145": "FT3", "E146": "FT1",
    "E147": "FTz", "E148": "FT2", "E149": "FT4", "E150": "FT6", "E151": "FT8",
    "E152": "FT10", "E153": "TTP9", "E154": "TTP7", "E155": "TTP5", "E156": "TTP3",
    "E157": "TTP1", "E158": "TTP2", "E159": "TTP4", "E160": "TTP6", "E161": "TTP8",
    "E162": "TTP10", "E163": "TP9", "E164": "TP7", "E165": "TP5", "E166": "TP3",
    "E167": "TP1", "E168": "TPz", "E169": "TP2", "E170": "TP4", "E171": "TP6",
    "E172": "TP8", "E173": "TP10", "E174": "P9", "E175": "P7", "E176": "P5",
    "E177": "P3", "E178": "P1", "E179": "Pz", "E180": "P2", "E181": "P4",
    "E182": "P6", "E183": "P8", "E184": "P10", "E185": "PPO9", "E186": "PPO7",
    "E187": "PPO5", "E188": "PPO3", "E189": "PPO1", "E190": "PPO2", "E191": "PPO4",
    "E192": "PPO6", "E193": "PPO8", "E194": "PPO10", "E195": "PO9", "E196": "PO7",
    "E197": "PO5", "E198": "PO3", "E199": "PO1", "E200": "POz", "E201": "PO2",
    "E202": "PO4", "E203": "PO6", "E204": "PO8", "E205": "PO10", "E206": "O1",
    "E207": "Oz", "E208": "O2", "E209": "OI1", "E210": "OI2", "E211": "OI3",
    "E212": "OI4", "E213": "OI5", "E214": "OI6", "E215": "OI7", "E216": "OI8",
    "E217": "OI9", "E218": "OI10", "E219": "I1", "E220": "I2", "E221": "I3",
    "E222": "I4", "E223": "I5", "E224": "I6", "E225": "I7", "E226": "I8",
    "E227": "I9", "E228": "I10", "E229": "FECg1", "E230": "FECg2", "E231": "FECg3",
    "E232": "FECg4", "E233": "FECg5", "E234": "FECg6", "E235": "FECg7", "E236": "FECg8",
    "E237": "FECg9", "E238": "FECg10", "E239": "LECg1", "E240": "LECg2", "E241": "LECg3",
    "E242": "LECg4", "E243": "LECg5", "E244": "LECg6", "E245": "LECg7", "E246": "LECg8",
    "E247": "LECg9", "E248": "LECg10", "E249": "RCg1", "E250": "RCg2", "E251": "RCg3",
    "E252": "RCg4", "E253": "RCg5", "E254": "RCg6", "E255": "RCg7", "E256": "RCg8",
}


def _build_egi_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for EGI 256-channel data to standard names.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG data object.
    
    Returns
    -------
    Dict[str, str]
        Mapping from original channel names to standard names.
    """
    rename_map = {}
    for egi_name, standard_name in _EGI_TO_STANDARD_256.items():
        if egi_name in raw.ch_names:
            rename_map[egi_name] = standard_name
    
    # Also handle any remaining EGI-style channels (e.g., E001, E01 format)
    existing_names = set(raw.ch_names)
    egi_pattern = re.compile(r'^E(\d+)$')
    
    for ch_name in existing_names:
        if ch_name in rename_map:
            continue
        match = egi_pattern.match(ch_name)
        if match:
            idx = int(match.group(1))
            if 1 <= idx <= 256:
                egi_name = f"E{idx}"
                if egi_name in _EGI_TO_STANDARD_256:
                    rename_map[ch_name] = _EGI_TO_STANDARD_256[egi_name]
    
    return rename_map


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name.
    
    Parameters
    ----------
    file_path : str
        Path to the EEG file.
    
    Returns
    -------
    str
        Paradigm identifier ('visual_object_naming' or 'unknown').
    """
    # For ds002791, all files belong to the Visual Object Naming paradigm
    # Source: Dataset description, openneuro.org/datasets/ds002791
    # Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
    base_name = os.path.basename(file_path).lower()
    
    if 'obj' in base_name or 'visual' in base_name or 'naming' in base_name:
        return 'visual_object_naming'
    
    return 'visual_object_naming'  # Default for this dataset


def _remap_trigger_events(
    raw: mne.io.BaseRaw,
    event_map: Dict[str, str]
) -> mne.io.BaseRaw:
    """Remap trigger annotations to human-readable event labels.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG data object.
    event_map : Dict[str, str]
        Mapping from original trigger IDs to readable labels.
    
    Returns
    -------
    mne.io.BaseRaw
        The raw object with updated annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    descriptions = []
    for desc in raw.annotations.description:
        # Check if description matches a trigger pattern
        if desc in event_map:
            descriptions.append(event_map[desc])
        elif desc.startswith('trigger/'):
            # Extract trigger number
            trigger_id = desc.replace('trigger/', '')
            new_desc = event_map.get(trigger_id, desc)
            descriptions.append(new_desc)
        else:
            descriptions.append(desc)
    
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=descriptions,
        orig_time=raw.annotations.orig_time
    )
    raw.set_annotations(new_annotations)
    
    return raw


@dataclass
class OpenNeuroDS002791Kernel:
    """Stage1 kernel for the openneuro_ds002791 Visual Object Naming dataset.
    
    This dataset contains high-density 256-channel EEG recordings from
    participants performing visual object naming tasks. Each trial presents
    a bitmap image of one of 30 distinct object categories.
    
    Event Structure
    ---------------
    - trigger/D249: Block/trigger type 1 (~9.8M events)
    - trigger/D250: Block/trigger type 2 (~9.8M events)
    
    Notes
    -----
    The dataset contains 30 distinct object images (GLOVE.bmp, FEATHER.bmp,
    etc.), each present across multiple participants. The response_time
    variable in the misc channel provides naming latency for regression tasks.
    
    Source: https://openneuro.org/datasets/ds002791
    Reference: 10.3389/fnint.2023.1087976
    """
    
    KERNEL_ID: str = "openneuro-ds002791-stage1"
    
    # Event mapping for trigger IDs
    # Source: Dataset documentation / event structure
    # Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
    _EVENT_MAP: Dict[str, str] = field(default_factory=lambda: {
        "D249": "visual_object_trigger_type1",
        "D250": "visual_object_trigger_type2",
        "trigger/D249": "visual_object_trigger_type1",
        "trigger/D250": "visual_object_trigger_type2",
    })
    
    # Misc/continuous channels to preserve
    _CONTINUOUS_COLS: List[str] = field(default_factory=lambda: [
        'response_time',
        'ResponseTime',
        'response_time_ms',
    ])
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
        
        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized channel names,
            annotations, and metadata.
        """
        file_path = row.get("File Path", row.get("file_path", ""))
        subject_id = row.get("subject_id", row.get("Subject", "unknown"))
        
        # Detect paradigm
        paradigm = _detect_paradigm(file_path)
        
        # Step 1: Rename channels from EGI naming to standard names
        rename_map = _build_egi_channel_rename_map(raw)
        if rename_map:
            # Check if any EGI-style channels exist
            existing_egi = [ch for ch in raw.ch_names if ch.startswith('E') 
                          and ch[1:].isdigit()]
            if existing_egi:
                # Ensure all EEG channels have proper types
                for ch_name in raw.ch_names:
                    if ch_name.startswith('E') or ch_name in rename_map.values():
                        if ch_name in rename_map:
                            raw.set_channel_types({ch_name: 'eeg'}, on_unit='ignore')
                
                # Rename channels
                raw.rename_channels(rename_map)
        
        # Step 2: Set montage for spatial positioning
        # Use standard 1020 as base, then apply 256-channel positions
        # Source: EGI HydroCell 256-channel System
        # Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        try:
            # Try to set montage with standard 1020 positions
            montage = mne.channels.make_standard_montage('standard_1020')
            
            # Get all EEG channel names (excluding EOG, ECG, etc.)
            eeg_chs = [ch for ch in raw.ch_names 
                      if ch not in ['EOG', 'ECG', 'EMG', 'Trigger', 'misc']]
            
            # Find matching channels in the montage
            montage_chs = set(montage.ch_names)
            available_chs = [ch for ch in eeg_chs if ch in montage_chs]
            
            if len(available_chs) >= 10:  # Only set montage if we have enough channels
                raw.set_montage('standard_1020', on_missing='ignore')
            else:
                # For 256-channel data, try extended montage
                # This may not be available in all MNE versions
                try:
                    raw.set_montage('standard_alphabetic', on_missing='ignore')
                except Exception:
                    pass  # Skip montage if not available
                    
        except Exception as e:
            # If montage setting fails, continue without it
            # Log warning in production
            pass
        
        # Step 3: Remap trigger events to readable labels
        raw = _remap_trigger_events(raw, self._EVENT_MAP)
        
        # Step 4: Set device and subject metadata
        # Source: Dataset documentation and EGI HydroCell specifications
        # Annotifier: LLM, 2026-04-08 (LLM 推断，需人类复核)
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "EGI Net Amps 300",  # EGI high-density amplifier
                "cap": "EGI HydroCell 256-channel",  # 256-channel HydroCell array
                "age": "unknown",  # From participants.tsv if available
                "sex": "unknown",  # From participants.tsv if available
                "handedness": "unknown",  # From participants.tsv if available
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Step 5: Update subject info if available from udataset or row
        if hasattr(udataset, 'subject_dict') and subject_id in udataset.subject_dict:
            subj_info = udataset.subject_dict[subject_id]
            description_dict["eegunity_description"]["age"] = subj_info.get("age", "unknown")
            description_dict["eegunity_description"]["sex"] = subj_info.get("sex", "unknown")
            description_dict["eegunity_description"]["handedness"] = subj_info.get(
                "handedness", "unknown"
            )
            raw.info["description"] = json.dumps(description_dict)
        
        # Step 6: Ensure all data channels have appropriate types
        # Identify and set EOG/ECG channels if present
        eog_chs = [ch for ch in raw.ch_names 
                  if any(x in ch.lower() for x in ['eog', 'eye', 'vEOG', 'hEOG'])]
        ecg_chs = [ch for ch in raw.ch_names 
                  if any(x in ch.lower() for x in ['ecg', 'cardiac', 'heart'])]
        emg_chs = [ch for ch in raw.ch_names 
                  if any(x in ch.lower() for x in ['emg', 'muscle'])]
        
        if eog_chs:
            raw.set_channel_types({ch: 'eog' for ch in eog_chs}, on_unit='ignore')
        if ecg_chs:
            raw.set_channel_types({ch: 'ecg' for ch in ecg_chs}, on_unit='ignore')
        if emg_chs:
            raw.set_channel_types({ch: 'emg' for ch in emg_chs}, on_unit='ignore')
        
        # Step 7: Add paradigm information to meas_date or annotations
        # This helps with multi-paradigm datasets
        if paradigm != 'visual_object_naming':
            # Add paradigm-specific annotation if different paradigm detected
            paradigm_annotation = mne.Annotations(
                onset=0,
                duration=0,
                description=f"paradigm:{paradigm}",
            )
            if raw.annotations is None or len(raw.annotations) == 0:
                raw.set_annotations(paradigm_annotation)
            else:
                # Merge annotations
                combined_onset = np.concatenate([raw.annotations.onset, paradigm_annotation.onset])
                combined_duration = np.concatenate([raw.annotations.duration, paradigm_annotation.duration])
                combined_desc = np.concatenate([raw.annotations.description, paradigm_annotation.description])
                raw.set_annotations(mne.Annotations(
                    onset=combined_onset,
                    duration=combined_duration,
                    description=combined_desc,
                    orig_time=raw.annotations.orig_time
                ))
        
        return raw


KERNEL = OpenNeuroDS002791Kernel()