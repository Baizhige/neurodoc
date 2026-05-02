"""openneuro_ds003620 stage1 kernel for EEGUnity.

Runabout: A Mobile EEG Study of Auditory Oddball Processing in Laboratory
and Real-World Conditions.

Source: https://openneuro.org/datasets/ds003620
DOI: 10.1038/s41598-021-01772-8

This kernel handles the OpenNeuro ds003620 BIDS dataset which contains
auditory oddball EEG recordings across three environments (lab, oval, campus)
with mobile EEG hardware.

Annotations/Events:
    - t_count_lab / t_count_oval / t_count_campus: Target tone, count condition
    - t_Count_lab / t_Count_oval / t_Count_campus: Target tone, Count (capital) condition
    - t_Dontcount_lab / t_Dontcount_oval / t_Dontcount_campus: Target tone, don't-count condition
    - ntcount_lab / ntcount_oval / ntcount_campus: Non-target tone, count condition
    - ntCount_lab / ntCount_oval / ntCount_campus: Non-target tone, Count condition
    - ntDontcount_lab / ntDontcount_oval / ntDontcount_campus: Non-target tone, don't-count condition
    - Stimulus-prefixed variants (e.g., Stimulus/t_count_lab)
    - empty: Admin/padding events (excluded from epoching)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Target event IDs for classification (both raw and Stimulus-prefixed)
_TARGET_EVENTS = [
    "t_count_lab", "t_count_oval", "t_count_campus",
    "t_Count_lab", "t_Count_oval", "t_Count_campus",
    "t_Dontcount_lab", "t_Dontcount_oval", "t_Dontcount_campus",
    "ntcount_lab", "ntcount_oval", "ntcount_campus",
    "ntCount_lab", "ntCount_oval", "ntCount_campus",
    "ntDontcount_lab", "ntDontcount_oval", "ntDontcount_campus",
    "Stimulus/t_count_lab", "Stimulus/t_count_oval", "Stimulus/t_count_campus",
    "Stimulus/t_Count_lab", "Stimulus/t_Count_oval", "Stimulus/t_Count_campus",
    "Stimulus/t_Dontcount_lab", "Stimulus/t_Dontcount_oval", "Stimulus/t_Dontcount_campus",
    "Stimulus/ntcount_lab", "Stimulus/ntcount_oval", "Stimulus/ntcount_campus",
    "Stimulus/ntCount_lab", "Stimulus/ntCount_oval", "Stimulus/ntCount_campus",
    "Stimulus/ntDontcount_lab", "Stimulus/ntDontcount_oval", "Stimulus/ntDontcount_campus",
]

# Label mapping for binary classification
_EVENT_TO_LABEL: Dict[str, int] = {}
for ev in _TARGET_EVENTS:
    if ev.startswith("t_") or ev.startswith("Stimulus/t_"):
        _EVENT_TO_LABEL[ev] = 1  # Target (deviant) tone
    else:
        _EVENT_TO_LABEL[ev] = 0  # Non-target (standard) tone

# Admin events to exclude
_ADMIN_EVENTS = {"empty", "boundary", "S  1"}

# Amplifier information - Source: DOI 10.1038/s41598-021-01772-8 indicates
# "BioSemi ActiveTwo" system used for mobile EEG recording
# inferred by LLM, needs human review
_AMPLIFIER = "BioSemi ActiveTwo"
_CAP = "Ag/AgCl"  # Active electrodes typically use Ag/AgCl


def _detect_subject_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv.
    
    Returns:
        Dict with 'age', 'sex', 'handedness' keys.
    
    Source: participants.tsv in BIDS dataset root
    """
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Find row matching this subject
            subj_col = "participant_id" if "participant_id" in df.columns else "subject_id"
            if subj_col in df.columns:
                row = df[df[subj_col] == subject_id]
                if len(row) > 0:
                    info = {}
                    # Extract age
                    if "age" in df.columns:
                        age_val = row["age"].values[0]
                        if pd.notna(age_val):
                            info["age"] = str(int(float(age_val)))  # inferred by LLM, needs human review
                        else:
                            info["age"] = "unknown"
                    else:
                        info["age"] = "unknown"
                    
                    # Extract sex
                    if "sex" in df.columns:
                        sex_val = row["sex"].values[0]
                        if pd.notna(sex_val):
                            sex_lower = str(sex_val).lower()
                            if sex_lower in ["m", "male"]:
                                info["sex"] = "male"
                            elif sex_lower in ["f", "female"]:
                                info["sex"] = "female"
                            else:
                                info["sex"] = "unknown"
                        else:
                            info["sex"] = "unknown"
                    else:
                        info["sex"] = "unknown"
                    
                    # Extract handedness
                    if "handedness" in df.columns:
                        hand_val = row["handedness"].values[0]
                        if pd.notna(hand_val):
                            hand_lower = str(hand_val).lower()
                            if hand_lower in ["r", "right", "right-handed"]:
                                info["handedness"] = "right"
                            elif hand_lower in ["l", "left", "left-handed"]:
                                info["handedness"] = "left"
                            else:
                                info["handedness"] = "unknown"
                        else:
                            info["handedness"] = "unknown"
                    else:
                        info["handedness"] = "unknown"
                    
                    return info
        except Exception:
            pass
    
    # Default values if not found - inferred by LLM, needs human review
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _rename_channels_bids(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed.
    
    The Runabout dataset uses BioSemi ActiveTwo with standard 10-20 layout.
    Source: DOI 10.1038/s41598-021-01772-8 - standard electrode positions used
    
    This function attempts to normalize channel names that may appear as
    numeric codes (e.g., "EEG-001") to standard names based on the BioSemi
    32-channel + 3 EOG setup.
    
    inferred by LLM, needs human review - channel naming convention
    """
    ch_names = raw.ch_names
    rename_map = {}
    
    # Standard BioSemi 32-channel layout for Runabout study
    # BioSemi uses naming like A1-A32 for electrode positions
    # inferred by LLM, needs human review
    biosemi_standard = [
        "Fp1", "AFp3", "AFp1", "AFp2", "AFp4", "AFp5", "AFp6", "AFz",
        "Fpz", "Fp2", "AF7", "AF3", "AF4", "AF8", "F9", "F7", "F5", "F3",
        "F1", "Fz", "F2", "F4", "F6", "F8", "F10", "FT9", "FT7", "FC5",
        "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10", "T9", "T7",
        "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10", "TP9", "TP7",
        "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO7", "PO3", "POz", "PO4", "PO8", "O9", "O7", "O3", "O1", "Oz",
        "O2", "O4", "O8", "O10", "I1", "Iz", "I2", "AFp9", "AFp10",
        "AF9", "AF10", "Fp9", "Fp10", "AFF9", "AFF5", "AFF1", "AFF2",
        "AFF6", "AFF10", "FTT9", "FTT7", "FTT5", "FTT3", "FTT1", "FTTz",
        "FTT2", "FTT4", "FTT6", "FTT8", "FTT10", "TT9", "TT7", "TP9", "TP7",
        "CPP9", "CPP5", "CPP3", "CPP1", "CPPz", "CPP2", "CPP4", "CPP6",
        "CPP10", "PTT9", "PTT7", "PTT5", "PTT3", "PTT1", "PTTz", "PTT2",
        "PTT4", "PTT6", "PTT8", "PTT10", "T9", "T7", "T10", "T8", "O9", "O10",
        # EOG channels
        "EOG-left", "EOG-right", "EOG-central"
    ]
    
    # Check for BioSemi naming pattern (e.g., "A1", "A2", etc.)
    # Or numeric naming (e.g., "EEG-001", "EEG-002")
    # Or "BioSemi" prefixed names
    
    for ch in ch_names:
        ch_upper = ch.upper()
        # Handle numeric EEG channel names
        if ch_upper.startswith("EEG-") or ch_upper.startswith("EEG_"):
            try:
                # Try to extract numeric suffix
                num_part = chUpper = ch_upper.replace("EEG-", "").replace("EEG_", "")
                idx = int(num_part) - 1  # 0-indexed
                if 0 <= idx < len(biosemi_standard):
                    rename_map[ch] = biosemi_standard[idx]
            except (ValueError, IndexError):
                pass
        # Handle simple numeric names
        elif ch.isdigit():
            try:
                idx = int(ch) - 1
                if 0 <= idx < len(biosemi_standard):
                    rename_map[ch] = biosemi_standard[idx]
            except (ValueError, IndexError):
                pass
        # Handle BioSemi A1, A2 naming
        elif ch_upper.startswith("A") and len(ch) <= 3:
            try:
                idx = int(ch[1:]) - 1
                if 0 <= idx < len(biosemi_standard):
                    rename_map[ch] = biosemi_standard[idx]
            except ValueError:
                pass
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _clean_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Clean and standardize annotations for the dataset.
    
    Remove admin events, standardize Stimulus-prefixed event names,
    and ensure consistent naming.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    descriptions = list(raw.annotations.description)
    new_descriptions = []
    
    for desc in descriptions:
        # Normalize Stimulus/ prefix (some files may have Stimulus/t_count_lab)
        if desc.startswith("Stimulus/"):
            # Remove Stimulus/ prefix to match standard naming
            new_desc = desc.replace("Stimulus/", "")
        else:
            new_desc = desc
        
        # Filter out admin events
        if new_desc in _ADMIN_EVENTS:
            new_descriptions.append("admin: exclude")
        else:
            new_descriptions.append(new_desc)
    
    # Update annotations with cleaned descriptions
    new_onset = []
    new_duration = []
    new_desc_filtered = []
    
    for i, desc in enumerate(new_descriptions):
        if desc != "admin: exclude":
            new_onset.append(raw.annotations.onset[i])
            new_duration.append(raw.annotations.duration[i])
            new_desc_filtered.append(desc)
    
    if new_desc_filtered:
        new_annotations = mne.Annotations(
            onset=new_onset,
            duration=new_duration,
            description=new_desc_filtered,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)
    
    return raw


class OpenNeuroDs003620Kernel:
    """Stage1 kernel for openneuro_ds003620 (Runabout dataset)."""

    KERNEL_ID: str = "openneuro-ds003620-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

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
            Preprocessed raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", row.get("participant_id", "unknown"))
        
        # Determine dataset path from file path
        if file_path:
            dataset_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
            if not os.path.exists(os.path.join(dataset_path, "participants.tsv")):
                # Try to find dataset root differently
                parent = os.path.dirname(file_path)
                while parent and not parent.endswith(os.sep):
                    if os.path.exists(os.path.join(parent, "participants.tsv")):
                        dataset_path = parent
                        break
                    parent = os.path.dirname(parent)
        else:
            dataset_path = ""
        
        # Get subject information
        subject_info = _detect_subject_info(dataset_path, subject_id)
        
        # Get original description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        # Build description dict for EEGUnity
        description_dict = {
            "original_description": str(original_description),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard names BEFORE set_montage
        raw = _rename_channels_bids(raw)
        
        # Set standard 10-20 montage
        try:
            # Try standard_1020 first (most common for this type of study)
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If standard_1020 fails, try extended_1020 or ignore
            try:
                montage = mne.channels.make_standard_montage("extended_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # Skip montage if electrodes don't match
                pass
        
        # Clean annotations - standardize event names and remove admin events
        raw = _clean_annotations(raw)
        
        # Update channel types for EOG if present
        ch_names = raw.ch_names
        for ch in ch_names:
            ch_lower = ch.lower()
            if "eog" in ch_lower or "eye" in ch_lower:
                try:
                    raw.set_channel_types({ch: "eog"})
                except Exception:
                    pass
            elif "emg" in ch_lower or "muscle" in ch_lower:
                try:
                    raw.set_channel_types({ch: "emg"})
                except Exception:
                    pass
        
        return raw


KERNEL = OpenNeuroDs003620Kernel()