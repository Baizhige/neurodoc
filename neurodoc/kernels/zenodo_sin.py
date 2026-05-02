"""zenodo_sin stage1 kernel for EEGUnity.

Dataset: Speech-in-Noise (SiN) Auditory Attention Decoding Dataset (Zenodo Mirror)
Format: .mat files with pre-epoched 3D arrays (896 time points x 66 channels x 100 trials)
Subjects: 26 (NH_subject01-NH_subject26)
Channels: 64 EEG + 2 mastoid references = 66 total
Sampling Rate: 256 Hz

The .mat files contain pre-epoched data for two conditions (7 and 13).
This kernel reconstructs continuous raw by concatenating trials and annotating
each trial with its condition label.

Source: https://zenodo.org/ (mirror of Mendeley SiN dataset)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import mne
import numpy as np
import scipy.io as sio


# No age/sex information available in this dataset.
# All subjects are described as "normal-hearing" adults.
# Annotator: LLM, 2026-04-08

# Channel layout: 64 channels + 2 mastoid references
# Standard 10-20 system with mastoids (M1, M2)
# Source: Dataset documentation and typical SiN AAD setups
# Annotator: LLM, 2026-04-08
_CHANNEL_NAMES = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8", "TP9", "CP5", "CP1", "CP2", "CP6", "TP10",
    "P7", "P3", "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
    "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6", "FT9", "FT7", "FC3",
    "FC4", "FT8", "FT10", "C5", "C1", "C2", "C6", "TP7", "CP3", "CPz", "CP4",
    "TP8", "P5", "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
    "M1", "M2"  # Mastoid references
]


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from filename like 'NH_subject01_condition7.mat'."""
    basename = os.path.basename(file_path)
    match = re.search(r'(NH_subject\d+)', basename)
    if match:
        return match.group(1)
    return "unknown"


def _load_mat_data(file_path: str) -> tuple[np.ndarray, list[str], float]:
    """Load .mat file and return EEG data, channel names, and sampling rate.
    
    The .mat file contains pre-epoched 3D array: (n_times, n_channels, n_trials)
    for a single condition. We need to find the data variable.
    """
    mat = sio.loadmat(file_path, simplify_cells=True)
    
    # Find the data variable (should be a 3D array)
    data_var = None
    for key in mat.keys():
        if key.startswith('__'):
            continue
        val = mat[key]
        if isinstance(val, np.ndarray) and val.ndim == 3:
            data_var = key
            break
    
    if data_var is None:
        raise ValueError(f"No 3D array found in {file_path}")
    
    data = mat[data_var]  # shape: (n_times, n_channels, n_trials)
    
    # Check if we need to transpose
    # Expected: (n_times, n_channels, n_trials) = (896, 66, 100)
    # MNE expects (n_channels, n_times) for RawArray
    
    # Verify dimensions match expected structure
    if data.shape[1] == len(_CHANNEL_NAMES):
        # shape is (n_times, n_channels, n_trials)
        n_times, n_channels, n_trials = data.shape
    elif data.shape[0] == len(_CHANNEL_NAMES):
        # shape might be (n_channels, n_times, n_trials)
        data = data.transpose(1, 0, 2)
        n_times, n_channels, n_trials = data.shape
    else:
        # Try other permutations
        if data.shape[2] == len(_CHANNEL_NAMES):
            data = data.transpose(0, 2, 1)
            n_times, n_channels, n_trials = data.shape
        else:
            raise ValueError(
                f"Cannot match channel count {len(_CHANNEL_NAMES)} to data shape {data.shape}"
            )
    
    # Reshape to continuous: (n_channels, n_times * n_trials)
    n_samples_total = n_times * n_trials
    data_continuous = data.transpose(1, 0, 2).reshape(n_channels, n_samples_total)
    
    # Determine condition from filename
    condition = _extract_condition(file_path)
    
    # Create annotations for each trial
    sfreq = 256.0  # Known from dataset documentation
    
    return data_continuous, _CHANNEL_NAMES, sfreq, condition, n_times, n_trials


def _extract_condition(file_path: str) -> str:
    """Extract condition label from filename."""
    basename = os.path.basename(file_path).lower()
    if 'condition7' in basename or 'condition_7' in basename or '_7' in basename:
        return "SiN_condition_7"
    elif 'condition13' in basename or 'condition_13' in basename or '_13' in basename:
        return "SiN_condition_13"
    # Try generic pattern
    match = re.search(r'condition[_]?(\d+)', basename)
    if match:
        return f"SiN_condition_{match.group(1)}"
    return "SiN_unknown"


def _find_sibling_condition_file(file_path: str) -> str | None:
    """Find the other condition file for the same subject."""
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    
    # Extract subject and current condition
    subject_match = re.search(r'(NH_subject\d+)', basename)
    if not subject_match:
        return None
    
    subject = subject_match.group(1)
    
    # Check if we have condition 7 or 13
    if '7' in basename and '13' not in basename:
        other_pattern = subject + '.*condition.*13'
    elif '13' in basename:
        other_pattern = subject + '.*condition.*7'
    else:
        return None
    
    # Look for sibling file
    for f in os.listdir(dirname):
        if re.search(other_pattern, f, re.IGNORECASE):
            return os.path.join(dirname, f)
    
    return None


@dataclass
class ZenodoSiNKernel:
    """Stage1 kernel for the Zenodo SiN dataset."""

    KERNEL_ID: str = "zenodo-sin-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # This dataset uses .mat files that MNE cannot directly read.
        # We need to reconstruct the raw from the pre-epoched data.
        # The file_path may point to one condition; we need to handle both.
        
        # Load current file
        data, ch_names, sfreq, condition, n_times, n_trials = _load_mat_data(file_path)
        
        # Try to find and load sibling condition file
        sibling_path = _find_sibling_condition_file(file_path)
        all_data = [data]
        all_conditions = [(condition, n_times, n_trials)]
        
        if sibling_path and os.path.exists(sibling_path):
            sib_data, sib_ch_names, sib_sfreq, sib_condition, sib_n_times, sib_n_trials = _load_mat_data(sibling_path)
            all_data.append(sib_data)
            all_conditions.append((sib_condition, sib_n_times, sib_n_trials))
            # Verify consistency
            assert sfreq == sib_sfreq, "Sampling rates must match"
            assert ch_names == sib_ch_names, "Channel names must match"
            assert n_times == sib_n_times, "Trial lengths must match"
        
        # Concatenate all conditions
        if len(all_data) > 1:
            full_data = np.concatenate(all_data, axis=1)
        else:
            full_data = all_data[0]
        
        # Create MNE Info
        info = mne.create_info(
            ch_names=ch_names,
            sfreq=sfreq,
            ch_types=['eeg'] * 64 + ['misc'] * 2  # 64 EEG + 2 mastoid as misc
        )
        
        # Create RawArray
        raw_new = mne.io.RawArray(full_data, info)
        
        # Set channel types for mastoids to misc (already set, but ensure)
        mastoid_types = {ch: 'misc' for ch in ch_names if ch in ['M1', 'M2']}
        if mastoid_types:
            raw_new.set_channel_types(mastoid_types)
        
        # Rename channels to standard names before montage
        # (already standard, but ensure consistency)
        
        # Set montage for EEG channels
        eeg_chs = [ch for ch in ch_names if ch not in ['M1', 'M2']]
        montage = mne.channels.make_standard_montage('standard_1020')
        # Only set montage for channels that exist in the montage
        raw_new.set_montage(montage, on_missing='ignore')
        
        # Create annotations for each trial
        onset_list = []
        duration_list = []
        description_list = []
        
        sample_offset = 0
        for cond, trial_len, n_trial in all_conditions:
            for trial_idx in range(n_trial):
                onset = sample_offset / sfreq
                duration = trial_len / sfreq
                onset_list.append(onset)
                duration_list.append(duration)
                description_list.append(cond)
                sample_offset += trial_len
        
        annotations = mne.Annotations(
            onset=onset_list,
            duration=duration_list,
            description=description_list
        )
        raw_new.set_annotations(annotations)
        
        # Read required info fields from participants.tsv if available
        # Default values since this dataset has no demographic information
        age = "n/a"
        sex = "n/a"
        amplifier = "n/a"
        cap = "n/a"
        handedness = "n/a"
        
        # Try to read from participants.tsv
        dataset_path = row.get("Dataset Path", "")
        participants_path = os.path.join(dataset_path, "participants.tsv") if dataset_path else ""
        if participants_path and os.path.exists(participants_path):
            try:
                import pandas as pd
                participants_df = pd.read_csv(participants_path, sep='\t')
                subject_id = _extract_subject_id(file_path)
                # Try to match subject
                for _, p_row in participants_df.iterrows():
                    p_id = str(p_row.get('participant_id', ''))
                    if subject_id in p_id or p_id in subject_id:
                        age = str(p_row.get('age', 'n/a'))
                        sex = str(p_row.get('sex', 'n/a'))
                        amplifier = str(p_row.get('amplifier', 'n/a'))
                        cap = str(p_row.get('cap', 'n/a'))
                        handedness = str(p_row.get('handedness', 'n/a'))
                        break
            except Exception:
                pass
        
        # Build description with exact required format
        original_desc = raw_new.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        })
        
        # Copy over the description to raw_new
        raw_new.info["description"] = raw.info["description"]
        
        return raw_new


KERNEL = ZenodoSiNKernel()