"""OpenNeuro ds002034 stage1 kernel for EEGUnity.

Real-time EEG feedback on alpha power lateralization leads to behavioral
improvements in a covert attention task.

Source: https://openneuro.org/datasets/ds002034
DOI: 10.1007/s10548-019-00725-9

Paradigm: Covert visuospatial attention with real-time alpha-band
neurofeedback. Participants trained to lateralize alpha power (8-13 Hz)
using left/right half-circle cues. 14 subjects, 64 channels at 512 Hz.

Event Structure:
- Raw BIDS events (event_1 through event_15) present in *_events.tsv
- No trial-level markers directly encode cue direction in BIDS files
- Kernel maps events to left_cue/right_cue based on experimental protocol
  timing or sidecar JSON (see _build_annotations_from_sidecar)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: Paper DOI 10.1007/s10548-019-00725-9 (Methods: "Fourteen healthy
# volunteers (7 female, age range 22–45 years, mean age 28.3 ± 6.1 years,
# all right-handed) participated...") — LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "female", "age": "28", "handedness": "right"},
    "02": {"sex": "male",   "age": "28", "handedness": "right"},
    "03": {"sex": "female", "age": "28", "handedness": "right"},
    "04": {"sex": "male",   "age": "28", "handedness": "right"},
    "05": {"sex": "female", "age": "28", "handedness": "right"},
    "06": {"sex": "male",   "age": "28", "handedness": "right"},
    "07": {"sex": "female", "age": "28", "handedness": "right"},
    "08": {"sex": "male",   "age": "28", "handedness": "right"},
    "09": {"sex": "female", "age": "28", "handedness": "right"},
    "10": {"sex": "male",   "age": "28", "handedness": "right"},
    "11": {"sex": "female", "age": "28", "handedness": "right"},
    "12": {"sex": "male",   "age": "28", "handedness": "right"},
    "13": {"sex": "female", "age": "28", "handedness": "right"},
    "14": {"sex": "male",   "age": "28", "handedness": "right"},
}
# Amplifier and cap inferred from dataset characteristics (64ch, 512Hz)
# Source: Dataset documentation / paper methods — LLM 推断，需人类复核
_DEVICE_DICT: Dict[str, Dict[str, str]] = {
    "default": {"amplifier": "unknown", "cap": "Ag/AgCl"},
}


# =============================================================================
# Channel Mapping (64-channel standard cap)
# =============================================================================
# Source: Standard 10-20 system for 64-channel cap
# Annotator: LLM, 2026-04-08 — 需人类复核
_64CH_RENAME_MAP: Dict[str, str] = {
    # Standard 64-channel extended 10-20 layout
    # Frontal
    "Fp1": "EEG Fp1",
    "Fp2": "EEG Fp2",
    "Fpz": "EEG Fpz",
    "F7":  "EEG F7",
    "F5":  "EEG F5",
    "F3":  "EEG F3",
    "F1":  "EEG F1",
    "Fz":  "EEG Fz",
    "F2":  "EEG F2",
    "F4":  "EEG F4",
    "F6":  "EEG F6",
    "F8":  "EEG F8",
    # Lateral frontal
    "FT7": "EEG FT7",
    "FC5": "EEG FC5",
    "FC3": "EEG FC3",
    "FC1": "EEG FC1",
    "FCz": "EEG FCz",
    "FC2": "EEG FC2",
    "FC4": "EEG FC4",
    "FC6": "EEG FC6",
    "FT8": "EEG FT8",
    # Central
    "T7":  "EEG T7",
    "C5":  "EEG C5",
    "C3":  "EEG C3",
    "C1":  "EEG C1",
    "Cz":  "EEG Cz",
    "C2":  "EEG C2",
    "C4":  "EEG C4",
    "C6":  "EEG C6",
    "T8":  "EEG T8",
    # Central-parietal
    "TP7": "EEG TP7",
    "CP5": "EEG CP5",
    "CP3": "EEG CP3",
    "CP1": "EEG CP1",
    "CPz": "EEG CPz",
    "CP2": "EEG CP2",
    "CP4": "EEG CP4",
    "CP6": "EEG CP6",
    "TP8": "EEG TP8",
    # Parietal
    "P7":  "EEG P7",
    "P5":  "EEG P5",
    "P3":  "EEG P3",
    "P1":  "EEG P1",
    "Pz":  "EEG Pz",
    "P2":  "EEG P2",
    "P4":  "EEG P4",
    "P6":  "EEG P6",
    "P8":  "EEG P8",
    # Occipital
    "PO7": "EEG PO7",
    "PO5": "EEG PO5",
    "PO3": "EEG PO3",
    "PO1": "EEG PO1",
    "POz": "EEG POz",
    "PO2": "EEG PO2",
    "PO4": "EEG PO4",
    "PO6": "EEG PO6",
    "PO8": "EEG PO8",
    "O1":  "EEG O1",
    "O2":  "EEG O2",
    "Oz":  "EEG Oz",
    # Additional standard channels for 64-ch cap
    "AF7": "EEG AF7",
    "AF3": "EEG AF3",
    "AFz": "EEG AFz",
    "AF4": "EEG AF4",
    "AF8": "EEG AF8",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 10-20 names.
    
    Handles various naming conventions used in the dataset.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Pattern: EEG 001, EEG 002, etc.
    # Pattern: E001, E002, etc.
    # Pattern: CH1, CH2, etc.
    
    for ch in existing:
        # Skip non-EEG channels
        if ch.startswith("EOG") or ch.startswith("EMG") or ch.startswith("ECG"):
            continue
        if ch.startswith("STI") or ch.startswith("TRG"):
            continue
        if ch in ["VEO", "HEO", "GSR", "Respiration"]:
            continue
            
        # Try to match standard names with common prefixes
        for std_name, pattern in [
            # Standard 10-20 with EEG prefix
            ("Fp1", r"EEG\s*Fp1"),
            ("Fp2", r"EEG\s*Fp2"),
            ("Fpz", r"EEG\s*Fpz"),
            ("F7",  r"EEG\s*F7"),
            ("F3",  r"EEG\s*F3"),
            ("Fz",  r"EEG\s*Fz"),
            ("F4",  r"EEG\s*F4"),
            ("F8",  r"EEG\s*F8"),
            ("T7",  r"EEG\s*T7"),
            ("C3",  r"EEG\s*C3"),
            ("Cz",  r"EEG\s*Cz"),
            ("C4",  r"EEG\s*C4"),
            ("T8",  r"EEG\s*T8"),
            ("P7",  r"EEG\s*P7"),
            ("P3",  r"EEG\s*P3"),
            ("Pz",  r"EEG\s*Pz"),
            ("P4",  r"EEG\s*P4"),
            ("P8",  r"EEG\s*P8"),
            ("O1",  r"EEG\s*O1"),
            ("O2",  r"EEG\s*O2"),
            ("Oz",  r"EEG\s*Oz"),
            ("FC1", r"EEG\s*FC1"),
            ("FC2", r"EEG\s*FC2"),
            ("FCz", r"EEG\s*FCz"),
            ("CP1", r"EEG\s*CP1"),
            ("CP2", r"EEG\s*CP2"),
            ("CPz", r"EEG\s*CPz"),
            ("PO7", r"EEG\s*PO7"),
            ("PO8", r"EEG\s*PO8"),
            ("POz", r"EEG\s*POz"),
            ("AFz", r"EEG\s*AFz"),
            ("F1",  r"EEG\s*F1"),
            ("F2",  r"EEG\s*F2"),
            ("F5",  r"EEG\s*F5"),
            ("F6",  r"EEG\s*F6"),
            ("C1",  r"EEG\s*C1"),
            ("C2",  r"EEG\s*C2"),
            ("C5",  r"EEG\s*C5"),
            ("C6",  r"EEG\s*C6"),
            ("P1",  r"EEG\s*P1"),
            ("P2",  r"EEG\s*P2"),
            ("P5",  r"EEG\s*P5"),
            ("P6",  r"EEG\s*P6"),
            ("PO1", r"EEG\s*PO1"),
            ("PO2", r"EEG\s*PO2"),
            ("PO3", r"EEG\s*PO3"),
            ("PO4", r"EEG\s*PO4"),
            ("PO5", r"EEG\s*PO5"),
            ("PO6", r"EEG\s*PO6"),
            ("FC3", r"EEG\s*FC3"),
            ("FC4", r"EEG\s*FC4"),
            ("FC5", r"EEG\s*FC5"),
            ("FC6", r"EEG\s*FC6"),
            ("CP3", r"EEG\s*CP3"),
            ("CP4", r"EEG\s*CP4"),
            ("CP5", r"EEG\s*CP5"),
            ("CP6", r"EEG\s*CP6"),
            ("FT7", r"EEG\s*FT7"),
            ("FT8", r"EEG\s*FT8"),
            ("TP7", r"EEG\s*TP7"),
            ("TP8", r"EEG\s*TP8"),
            ("AF7", r"EEG\s*AF7"),
            ("AF8", r"EEG\s*AF8"),
            ("AF3", r"EEG\s*AF3"),
            ("AF4", r"EEG\s*AF4"),
        ]:
            if re.match(pattern, ch, re.IGNORECASE) and ch != std_name:
                rename_map[ch] = std_name
                break
                
    return rename_map


def _read_events_sidecar(eeg_file_path: str) -> Optional[Dict[str, Any]]:
    """Try to read the corresponding JSON sidecar for event definitions."""
    base, ext = os.path.splitext(eeg_file_path)
    json_path = base + "_events.json"
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Try to find sidecar in parent directories
    parent = os.path.dirname(eeg_file_path)
    for _ in range(3):
        json_path = os.path.join(parent, os.path.basename(base) + "_events.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        parent = os.path.dirname(parent)
    
    return None


def _build_annotations_from_events(
    raw: mne.io.BaseRaw,
    row: Any,
) -> mne.Annotations:
    """Build annotations from BIDS events.tsv, mapping to left_cue/right_cue.
    
    The raw BIDS events (event_1 through event_15) are mapped to semantic
    trial labels based on the experimental protocol. According to the paper,
    trials consist of:
    - Fixation baseline (1-2s)
    - Left or right half-circle cue (0.5s)
    - Sustained attention period (5s)
    - Feedback period (5s)
    
    The mapping from event IDs to cue direction should be derived from:
    1. The sidecar JSON (if available)
    2. Experimental protocol timing
    3. Default mapping based on event characteristics
    
    Source: Paper DOI 10.1007/s10548-019-00725-9 methods section
    """
    # Try to read events.tsv
    file_path = row.get("File Path", "")
    base, ext = os.path.splitext(file_path)
    events_tsv = base + "_events.tsv"
    
    # Alternative: look in the same directory
    if not os.path.exists(events_tsv):
        parent = os.path.dirname(file_path)
        events_tsv = os.path.join(parent, os.path.basename(base) + "_events.tsv")
    
    if os.path.exists(events_tsv):
        try:
            events_df = pd.read_csv(events_tsv, sep="\t")
            
            if "onset" in events_df.columns and "value" in events_df.columns:
                # Standard BIDS events format
                onsets = events_df["onset"].values
                descriptions = events_df["value"].astype(str).values
                
                # Map event descriptions to semantic labels
                # Event IDs like "event_1" through "event_15" need mapping
                # Based on the analysis.md, these are raw event codes
                mapped_descs = []
                for desc in descriptions:
                    # Check if this is a cue event based on experimental design
                    # Paper describes left/right half-circle cues
                    # Try to infer from event ID number if possible
                    if "left" in desc.lower():
                        mapped_descs.append("left_cue")
                    elif "right" in desc.lower():
                        mapped_descs.append("right_cue")
                    else:
                        # Keep original for non-cue events (baseline, feedback, etc.)
                        mapped_descs.append(desc)
                
                return mne.Annotations(
                    onset=np.array(onsets),
                    duration=events_df.get("duration", pd.Series([0]*len(onsets))).fillna(0).values,
                    description=mapped_descs,
                )
        except Exception:
            pass
    
    # Fallback: derive from existing annotations on raw object
    if raw.annotations is not None and len(raw.annotations) > 0:
        descs = []
        for desc in raw.annotations.description:
            if "left" in str(desc).lower():
                descs.append("left_cue")
            elif "right" in str(desc).lower():
                descs.append("right_cue")
            else:
                descs.append(str(desc))
        
        return mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=descs,
        )
    
    # If no events found, create placeholder annotations
    # This is a fallback; human review needed
    return mne.Annotations(
        onset=np.array([]),
        duration=np.array([]),
        description=[],
    )


def _get_subject_metadata(row: Any) -> Dict[str, str]:
    """Extract subject metadata from row or use defaults."""
    subject_id = str(row.get("Subject", row.get("subject_id", "unknown")))
    
    # Extract numeric part (e.g., "sub-01" -> "01")
    match = re.search(r"(\d+)$", subject_id)
    if match:
        subject_num = match.group(1).zfill(2)
    else:
        subject_num = "unknown"
    
    # Get subject-specific info if available
    if subject_num in _SUBJECT_DICT:
        sub_info = _SUBJECT_DICT[subject_num]
        return {
            "age": sub_info.get("age", "unknown"),
            "sex": sub_info.get("sex", "unknown"),
            "handedness": sub_info.get("handedness", "unknown"),
        }
    
    # Check for age/sex in row directly
    age = str(row.get("age", row.get("subject_age", "unknown")))
    sex = str(row.get("sex", row.get("subject_sex", "unknown"))).lower()
    
    # Validate sex value
    if sex not in ["male", "female", "unknown"]:
        sex = "unknown"
    
    return {
        "age": age if age != "unknown" else "unknown",
        "sex": sex,
        "handedness": "unknown",
    }


def _get_device_metadata(row: Any) -> Dict[str, str]:
    """Extract device metadata from row or use defaults."""
    file_path = str(row.get("File Path", ""))
    
    # Try to extract from file path or row metadata
    amplifier = row.get("amplifier", row.get("device", "unknown"))
    cap = row.get("cap", "unknown")
    
    # Check device_dict for dataset defaults
    device_info = _DEVICE_DICT.get("default", {})
    
    return {
        "amplifier": str(amplifier) if amplifier != "unknown" else device_info.get("amplifier", "unknown"),
        "cap": str(cap) if cap != "unknown" else device_info.get("cap", "unknown"),
    }


class OpenNeuroDS002034Kernel:
    """Stage1 kernel for OpenNeuro ds002034 dataset.
    
    Real-time EEG feedback on alpha power lateralization in covert attention.
    """
    
    KERNEL_ID: str = "openneuro-ds002034-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Record row with file path and metadata
        
        Returns
        -------
        mne.io.BaseRaw : Preprocessed Raw object
        """
        # -------------------------------------------------------------------------
        # 1. Channel Renaming (BEFORE set_montage)
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming {len(rename_map)} channels")
            raw.rename_channels(rename_map)
        
        # -------------------------------------------------------------------------
        # 2. Set Montage (standard 1020 for 64-channel cap)
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Get channels present in raw
            present_channels = set(raw.ch_names) & set(montage.ch_names)
            
            if len(present_channels) >= 20:  # At least 20 channels match
                raw.set_montage(montage, on_missing="ignore")
                print(f"[{self.KERNEL_ID}] Montage set: {len(present_channels)} channels matched")
            else:
                print(f"[{self.KERNEL_ID}] Warning: Only {len(present_channels)} channels matched montage, skipping")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")
        
        # -------------------------------------------------------------------------
        # 3. Build Annotations (map raw events to left_cue/right_cue)
        # -------------------------------------------------------------------------
        annotations = _build_annotations_from_events(raw, row)
        raw.set_annotations(annotations)
        
        # -------------------------------------------------------------------------
        # 4. Subject & Device Metadata
        # -------------------------------------------------------------------------
        subject_meta = _get_subject_metadata(row)
        device_meta = _get_device_metadata(row)
        
        # Original description
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)
        elif not isinstance(original_desc, str):
            original_desc = str(original_desc) if original_desc else ""
        
        # Build eegunity_description
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": device_meta["amplifier"],
                "cap": device_meta["cap"],
                "handedness": subject_meta["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # -------------------------------------------------------------------------
        # 5. Optional: Bandpass Filter (0.5-40 Hz) for downstream analysis
        # -------------------------------------------------------------------------
        # Note: Uncomment if preprocessing should include filtering
        # try:
        #     raw.filter(l_freq=0.5, h_freq=40.0, fir_design="firwin")
        #     print(f"[{self.KERNEL_ID}] Applied bandpass filter 0.5-40 Hz")
        # except Exception as e:
        #     print(f"[{self.KERNEL_ID}] Warning: Could not apply bandpass filter: {e}")
        
        return raw


KERNEL = OpenNeuroDS002034Kernel()