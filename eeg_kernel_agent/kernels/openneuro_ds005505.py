"""OpenNeuro DS005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

This kernel processes the Healthy Brain Network (HBN) EEG Release 1 dataset,
a large-scale developmental battery with 129-channel EEG recordings at 500 Hz
collected from children and adolescents (ages 5.2–21.7).

The dataset contains six experimental paradigms: naturalistic movie watching,
eyes-open/closed resting state, sensory contrast detection, surrounding
suppression, sequence learning, and symbol search tasks.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1101/2024.10.03.615261

Channel naming: The HBN dataset uses standard 10-20 extended montage with
129 channels. Original channel names may have prefixes like "EEG" that need
standardization.

Required info fields: age, attention, externalizing, internalizing, p_factor, sex
Required derived misc: accuracy (from user_answer vs correct_answer), response_time
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# HBN 129-channel standard montage channel names (10-20 extended system)
# Source: HBN dataset documentation and BrainVision channel files
_HBN_129_CHANNELS = {
    # Standard 10-20 channels
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # Extra channels for 129-channel system
    "F9", "F10",
    "FT9", "FT10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "PO1", "PO2",
    "F6", "F2",
    "CP6", "CP2",
    "P6", "P2",
    "PO6", "PO4",
    # Reference/misc channels
    "M1", "M2",
    "VEO", "HEO",
    "CB1", "CB2",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for HBN 129-channel standard montage.
    
    The HBN EEG data may have channel names with various prefixes
    (e.g., 'EEG 001', 'CH01', 'Fp1') that need standardization.
    
    Returns
    -------
    Dict[str, str]
        Dictionary mapping original names to standard names.
    """
    rename_map = {}
    existing_names = raw.ch_names
    
    for ch in existing_names:
        cleaned = ch.strip()
        
        # Strip common prefixes: "EEG ", "EEG-", "eeg_", "CH", "Ch "
        for prefix in ["EEG ", "EEG-", "eeg_", "CH", "Ch "]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        
        # Handle numeric-only channels (keep as-is if can't map)
        if cleaned.isdigit():
            continue
        
        # Direct match check (case-sensitive first)
        if cleaned in _HBN_129_CHANNELS:
            if cleaned != ch:
                rename_map[ch] = cleaned
        else:
            # Case-insensitive check
            cleaned_lower = cleaned.lower()
            for std_ch in _HBN_129_CHANNELS:
                if std_ch.lower() == cleaned_lower:
                    rename_map[ch] = std_ch
                    break
    
    return rename_map


def _create_misc_annotations(
    raw: mne.io.BaseRaw, 
    events_df: Optional[pd.DataFrame]
) -> Tuple[mne.Annotations, Dict[str, np.ndarray]]:
    """Create derived misc channels (accuracy and response_time).
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG object.
    events_df : Optional[pd.DataFrame]
        Events dataframe from events.tsv if available.
        
    Returns
    -------
    Tuple[mne.Annotations, Dict[str, np.ndarray]]
        Updated annotations and misc channel data dict.
    """
    misc_data = {}
    
    if events_df is None or events_df.empty:
        return raw.annotations, misc_data
    
    # Get trialResponse events
    if 'trial_type' in events_df.columns:
        trial_resp = events_df[events_df['trial_type'] == 'trialResponse'].copy()
    elif 'value' in events_df.columns:
        trial_resp = events_df[events_df['value'] == 'trialResponse'].copy()
    else:
        return raw.annotations, misc_data
    
    if trial_resp.empty:
        return raw.annotations, misc_data
    
    # Get newPage events for response time calculation
    if 'trial_type' in events_df.columns:
        new_pages = events_df[events_df['trial_type'] == 'newPage'].copy()
    elif 'value' in events_df.columns:
        new_pages = events_df[events_df['value'] == 'newPage'].copy()
    else:
        new_pages = pd.DataFrame()
    
    # Create accuracy misc channel
    accuracy_values = []
    accuracy_onsets = []
    
    for _, row in trial_resp.iterrows():
        user_answer = row.get('user_answer', None)
        correct_answer = row.get('correct_answer', None)
        
        if user_answer is not None and correct_answer is not None:
            try:
                is_correct = int(user_answer) == int(correct_answer)
                accuracy_values.append(1.0 if is_correct else 0.0)
                accuracy_onsets.append(row['onset'])
            except (ValueError, TypeError):
                pass
    
    # Create response_time misc channel
    rt_values = []
    rt_onsets = []
    
    if not new_pages.empty:
        new_page_onsets = new_pages['onset'].values
        for _, row in trial_resp.iterrows():
            trial_onset = row['onset']
            # Find most recent newPage before this trialResponse
            preceding = new_page_onsets[new_page_onsets < trial_onset]
            if len(preceding) > 0:
                rt = trial_onset - preceding[-1]
                rt_values.append(rt)
                rt_onsets.append(trial_onset)
    
    # Store misc channel data for later extraction
    misc_data['accuracy'] = {
        'onsets': np.array(accuracy_onsets) if accuracy_onsets else np.array([]),
        'values': np.array(accuracy_values) if accuracy_values else np.array([])
    }
    misc_data['response_time'] = {
        'onsets': np.array(rt_onsets) if rt_onsets else np.array([]),
        'values': np.array(rt_values) if rt_values else np.array([])
    }
    
    return raw.annotations, misc_data


@dataclass
class HBNKernel:
    """Stage1 kernel for the HBN EEG Release 1 dataset (OpenNeuro DS005505)."""

    KERNEL_ID: str = "hbn-eeg-release1-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``,
            ``Subject ID``, and optional ``Paradigm``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized channels, events,
            and metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "")

        # 1. Rename channels to standard 10-20 montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[HBNKernel] Renaming {len(rename_map)} channels for {subject_id}")
            raw.rename_channels(rename_map)

        # 2. Try to set standard montage (1020 system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[HBNKernel] Montage setup warning for {subject_id}: {e}")

        # 3. Build eegunity_description from participants.tsv
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",
                # Additional required info fields
                "attention": "unknown",
                "externalizing": "unknown",
                "internalizing": "unknown",
                "p_factor": "unknown",
            },
        }

        # Read participants.tsv for subject-specific metadata
        dataset_root = getattr(udataset, 'root_path', None)
        if dataset_root is None and file_path:
            dataset_root = os.path.dirname(file_path)
            # Navigate up to find dataset root
            while dataset_root and not os.path.exists(os.path.join(dataset_root, "participants.tsv")):
                parent = os.path.dirname(dataset_root)
                if parent == dataset_root:
                    break
                dataset_root = parent

        if dataset_root:
            participants_path = os.path.join(dataset_root, "participants.tsv")
            if os.path.exists(participants_path):
                try:
                    participants_df = pd.read_csv(participants_path, sep="\t")
                    # Match subject ID format (e.g., "sub-01" or "NDARXX...")
                    subject_col = None
                    for col in ['participant_id', 'subject_id', 'Subject ID']:
                        if col in participants_df.columns:
                            subject_col = col
                            break
                    
                    if subject_col:
                        # Try different subject ID formats
                        subject_patterns = [
                            subject_id,
                            subject_id.replace("sub-", ""),
                            subject_id.replace("NDAR", ""),
                        ]
                        
                        for pattern in subject_patterns:
                            matches = participants_df[participants_df[subject_col].str.contains(pattern, na=False)]
                            if not matches.empty:
                                row_p = matches.iloc[0]
                                if 'age' in participants_df.columns:
                                    age_val = row_p.get('age', 'unknown')
                                    if pd.notna(age_val):
                                        description_dict["eegunity_description"]["age"] = str(int(float(age_val)))
                                if 'sex' in participants_df.columns:
                                    sex_val = row_p.get('sex', 'unknown')
                                    if pd.notna(sex_val):
                                        sex_str = str(sex_val).lower()
                                        if sex_str in ['m', 'male']:
                                            description_dict["eegunity_description"]["sex"] = "male"
                                        elif sex_str in ['f', 'female']:
                                            description_dict["eegunity_description"]["sex"] = "female"
                                        else:
                                            description_dict["eegunity_description"]["sex"] = "unknown"
                                if 'handedness' in participants_df.columns:
                                    handed_val = row_p.get('handedness', 'unknown')
                                    if pd.notna(handed_val):
                                        handed_str = str(handed_val).lower()
                                        if 'left' in handed_str:
                                            description_dict["eegunity_description"]["handedness"] = "left"
                                        elif 'right' in handed_str:
                                            description_dict["eegunity_description"]["handedness"] = "right"
                                # Additional required fields
                                for field in ['attention', 'externalizing', 'internalizing', 'p_factor']:
                                    if field in participants_df.columns:
                                        val = row_p.get(field, 'unknown')
                                        if pd.notna(val):
                                            description_dict["eegunity_description"][field] = str(val)
                                break
                except Exception as e:
                    print(f"[HBNKernel] Warning reading participants.tsv: {e}")

        raw.info["description"] = json.dumps(description_dict)

        # 4. Process events.tsv for accurate events and derived misc channels
        events_path = None
        if dataset_root:
            # Find events.tsv in the same directory or subdirectory
            file_dir = os.path.dirname(file_path)
            candidates = [
                os.path.join(file_dir, "events.tsv"),
                os.path.join(file_dir, os.path.basename(file_path).split('.')[0] + "_events.tsv"),
            ]
            for candidate in candidates:
                if os.path.exists(candidate):
                    events_path = candidate
                    break
        
        events_df = None
        if events_path:
            try:
                events_df = pd.read_csv(events_path, sep="\t")
            except Exception as e:
                print(f"[HBNKernel] Warning reading events.tsv: {e}")

        # 5. Add events as annotations if events.tsv exists
        if events_df is not None and not events_df.empty:
            onset_list = []
            duration_list = []
            description_list = []
            
            # Get event column (trial_type or value)
            event_col = 'trial_type' if 'trial_type' in events_df.columns else 'value'
            
            for _, event_row in events_df.iterrows():
                if event_col in event_row:
                    onset_list.append(float(event_row['onset']))
                    duration_list.append(float(event_row.get('duration', 0)))
                    description_list.append(str(event_row[event_col]))
            
            if onset_list:
                annotations = mne.Annotations(
                    onset=np.array(onset_list),
                    duration=np.array(duration_list),
                    description=description_list,
                )
                raw.set_annotations(annotations)
            
            # 6. Create derived misc channels (accuracy and response_time)
            _, misc_data = _create_misc_annotations(raw, events_df)
            
            # Store misc data as attributes for downstream epoch writer
            raw._misc_channel_data = misc_data
        else:
            raw._misc_channel_data = {}

        # 7. Ensure required events are properly represented in annotations
        # Map event IDs to MNE-readable format
        required_events = [
            'dot_no1_ON', 'dot_no2_ON', 'dot_no3_ON', 'dot_no4_ON',
            'dot_no5_ON', 'dot_no6_ON', 'dot_no7_ON', 'dot_no8_ON',
            'fixpoint_ON', 'instructed_toCloseEyes', 'instructed_toOpenEyes',
            'left_target', 'newPage', 'right_target', 'stim_ON',
            'trialResponse', 'video_start'
        ]
        
        # Verify events are present in annotations
        current_annotations = raw.annotations
        if current_annotations is not None and len(current_annotations) > 0:
            current_descs = set(current_annotations.description)
            missing = [e for e in required_events if e not in current_descs]
            if missing:
                print(f"[HBNKernel] Warning: Some required events not found in {subject_id}: {missing}")

        return raw


KERNEL = HBNKernel()