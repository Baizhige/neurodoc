"""zenodo_dtu stage1 kernel for EEGUnity (HANDLES_UNAVAILABLE).

Dataset: DTU Auditory Attention Decoding Dataset
Format: MATLAB .mat files (BioSemi ActiveTwo, 64 EEG + 9 auxiliary = 73 channels)
Source: https://zenodo.org/records/1199011
Paper: Fuglsang et al., 2018, NeuroImage (10.1016/j.neuroimage.2017.04.026)

The .mat files contain:
- data.EEG: EEG data matrix (n_channels x n_samples)
- data.stimu: stimulus onset times (in samples)
- data.attended: attended speaker labels per trial (1 or 2)
- data.sampFreq: sampling frequency (512 Hz)
- data.chnames: channel names

This kernel reads .mat files directly because EEGUnity cannot parse
the proprietary MATLAB structure with standard MNE routines.

Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass

import mne
import numpy as np
import scipy.io as sio


# Standard BioSemi 64-channel layout based on 10-20 system
# Source: BioSemi ActiveTwo documentation; standard 10-20 layout
# Annotator: LLM 推断，需人类复核
_BIOSEMI_64_CH_NAMES = [
    'Fp1', 'AF7', 'AF3', 'F1', 'F3', 'F5', 'F7', 'FT7',
    'FC5', 'FC3', 'FC1', 'C1', 'C3', 'C5', 'T7', 'TP7',
    'CP5', 'CP3', 'CP1', 'P1', 'P3', 'P5', 'P7', 'P9',
    'PO7', 'PO3', 'O1', 'Iz', 'Oz', 'POz', 'Pz', 'CPz',
    'Fpz', 'Fp2', 'AF8', 'AF4', 'AFz', 'Fz', 'F2', 'F4',
    'F6', 'F8', 'FT8', 'FC6', 'FC4', 'FC2', 'FCz', 'Cz',
    'C2', 'C4', 'C6', 'T8', 'TP8', 'CP6', 'CP4', 'CP2',
    'P2', 'P4', 'P6', 'P8', 'P10', 'PO8', 'PO4', 'O2',
]

# Auxiliary channel names (9 channels: 8 external + 1 status)
# Source: analysis.md notes "64 channels plus additional auxiliary channels (total 73)"
# The exact auxiliary channel names are not specified in the dataset documentation.
# Common BioSemi auxiliary channels include EXG1-8 and GSR/ERG/etc.
# Annotator: LLM 推断，需人类复核
_AUX_CH_NAMES = [
    'EXG1', 'EXG2', 'EXG3', 'EXG4', 'EXG5', 'EXG6', 'EXG7', 'EXG8', 'Status'
]


def _load_mat_struct(mat_path: str) -> dict:
    """Load MATLAB .mat file and extract the data structure."""
    mat = sio.loadmat(mat_path, simplify_cells=True)
    
    # The .mat file typically has a 'data' variable containing the structure
    if 'data' in mat:
        data = mat['data']
    else:
        # Try to find the data structure directly
        data_keys = [k for k in mat.keys() if not k.startswith('__')]
        if len(data_keys) == 1:
            data = mat[data_keys[0]]
        else:
            raise ValueError(f"Cannot identify data structure in {mat_path}. Keys: {data_keys}")
    
    # Handle nested structure (data might be a numpy array of object dtype)
    if isinstance(data, np.ndarray) and data.dtype == object:
        data = data.item()
    
    return data


def _extract_field(data: dict, field_name: str, default=None):
    """Safely extract a field from the MATLAB struct, handling nested arrays."""
    if field_name not in data:
        return default
    
    val = data[field_name]
    
    # Unwrap numpy scalar arrays
    if isinstance(val, np.ndarray):
        if val.size == 1:
            val = val.item()
        elif val.ndim == 2 and val.shape[0] == 1:
            val = val.flatten()
        elif val.ndim == 2 and val.shape[1] == 1:
            val = val.flatten()
    
    return val


@dataclass
class ZenodoDTUKernel:
    """Stage1 kernel for the DTU Auditory Attention Decoding Dataset."""

    KERNEL_ID: str = "zenodo-dtu-stage1"
    HANDLES_UNAVAILABLE: bool = True

    def load(self, udataset, row) -> mne.io.BaseRaw:
        """Load a .mat file directly into an MNE Raw object."""
        file_path = row["File Path"]
        data = _load_mat_struct(file_path)
        
        # Extract EEG data
        eeg_data = _extract_field(data, 'EEG')
        if eeg_data is None:
            raise ValueError(f"No 'EEG' field found in {file_path}")
        
        # Determine data shape: should be (n_channels, n_samples)
        if eeg_data.ndim == 2:
            if eeg_data.shape[0] > eeg_data.shape[1]:
                # Might be (samples, channels), transpose
                if eeg_data.shape[1] == 73 or eeg_data.shape[1] == 64:
                    eeg_data = eeg_data.T
        elif eeg_data.ndim == 3:
            # Sometimes MATLAB saves as (1, n_channels, n_samples)
            eeg_data = eeg_data.squeeze()
            if eeg_data.ndim == 2 and eeg_data.shape[0] > eeg_data.shape[1]:
                if eeg_data.shape[1] == 73 or eeg_data.shape[1] == 64:
                    eeg_data = eeg_data.T
        
        n_channels, n_samples = eeg_data.shape
        
        # Extract sampling frequency
        sfreq = _extract_field(data, 'sampFreq')
        if sfreq is None:
            sfreq = 512.0  # Known from dataset documentation
        else:
            sfreq = float(sfreq)
        
        # Extract channel names
        chnames = _extract_field(data, 'chnames')
        if chnames is None:
            # Use default BioSemi 64 + auxiliary names
            if n_channels == 73:
                ch_names = _BIOSEMI_64_CH_NAMES + _AUX_CH_NAMES
            elif n_channels == 64:
                ch_names = _BIOSEMI_64_CH_NAMES
            else:
                ch_names = [f'CH{i+1}' for i in range(n_channels)]
        else:
            # Process channel names from file
            if isinstance(chnames, np.ndarray):
                if chnames.dtype == object:
                    ch_names = [str(c).strip() for c in chnames.flatten()]
                else:
                    ch_names = [str(c).strip() for c in chnames.flatten()]
            else:
                ch_names = [str(chnames).strip()]
            
            # Ensure correct length
            if len(ch_names) != n_channels:
                if n_channels == 73 and len(ch_names) == 64:
                    ch_names = ch_names + _AUX_CH_NAMES
                elif len(ch_names) < n_channels:
                    ch_names = ch_names + [f'CH{i+1}' for i in range(len(ch_names), n_channels)]
        
        # Create channel types
        ch_types = []
        for i, ch in enumerate(ch_names):
            ch_upper = ch.upper()
            if ch_upper in ['STATUS', 'TRIGGER', 'STI', 'STIM']:
                ch_types.append('stim')
            elif ch_upper.startswith('EXG') or ch_upper.startswith('AUX') or ch_upper in ['HEOG', 'VEOG', 'EOG']:
                ch_types.append('eog')
            elif i < 64 or ch_upper in [c.upper() for c in _BIOSEMI_64_CH_NAMES]:
                ch_types.append('eeg')
            else:
                ch_types.append('misc')
        
        # Create MNE info
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        
        # Create RawArray
        raw = mne.io.RawArray(eeg_data, info, verbose=False)
        
        # Set original description
        raw.info["description"] = json.dumps({
            "original_description": "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "BioSemi ActiveTwo",  # From analysis.md
                "cap": "BioSemi",  # LLM 推断，需人类复核
                "handedness": "unknown",
            }
        })
        
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # Load the original .mat data for event extraction
        try:
            data = _load_mat_struct(file_path)
        except Exception as e:
            warnings.warn(f"Could not load {file_path} for event extraction: {e}")
            data = None
        
        # Update description with eegunity_description
        original_desc = raw.info.get("description", "")
        try:
            original_desc_dict = json.loads(original_desc)
            original_desc_str = original_desc_dict.get("original_description", original_desc)
        except (json.JSONDecodeError, TypeError):
            original_desc_str = str(original_desc) if original_desc else ""
        
        # Subject info from filename if possible
        # Files are typically named like S1.mat, S2.mat, etc.
        basename = os.path.basename(file_path)
        subject_id = os.path.splitext(basename)[0]  # e.g., "S1"
        
        # No participants.tsv available for this dataset
        # All demographic info is unknown
        # Source: analysis.md notes subject_age, subject_sex, device are all missing
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc_str,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "BioSemi ActiveTwo",
                "cap": "BioSemi",  # LLM 推断，需人类复核
                "handedness": "unknown",
            }
        })
        
        # Channel renaming to standard 10-20 names if needed
        # The BioSemi 64 channels should already be in standard names, but check
        rename_map = {}
        for i, ch_name in enumerate(raw.ch_names):
            # Handle common variations
            upper_name = ch_name.upper()
            # Check if already standard
            if ch_name in _BIOSEMI_64_CH_NAMES:
                continue
            # Try to match case-insensitively
            for std_name in _BIOSEMI_64_CH_NAMES:
                if upper_name == std_name.upper():
                    if ch_name != std_name:
                        rename_map[ch_name] = std_name
                    break
        
        # Apply rename if any
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage for EEG channels
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) == 64:
            try:
                montage = mne.channels.make_standard_montage('biosemi64')
                raw.set_montage(montage, match_case=False, on_missing='warn')
            except Exception as e:
                warnings.warn(f"Could not set montage: {e}")
        elif len(eeg_picks) > 0:
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, match_case=False, on_missing='warn')
            except Exception as e:
                warnings.warn(f"Could not set standard_1020 montage: {e}")
        
        # Extract events from .mat file
        stimu = None
        attended = None
        
        if data is not None:
            stimu = _extract_field(data, 'stimu')
            attended = _extract_field(data, 'attended')
        
        # Create annotations from trial information
        annotations = []
        
        if stimu is not None and attended is not None:
            # Ensure they are 1D arrays of the same length
            if isinstance(stimu, (list, tuple, np.ndarray)):
                stimu = np.asarray(stimu).flatten()
            else:
                stimu = np.array([stimu])
            
            if isinstance(attended, (list, tuple, np.ndarray)):
                attended = np.asarray(attended).flatten()
            else:
                attended = np.array([attended])
            
            # Ensure same length
            min_len = min(len(stimu), len(attended))
            stimu = stimu[:min_len]
            attended = attended[:min_len]
            
            sfreq = raw.info['sfreq']
            
            # Calculate trial durations (onset to next onset, or to end of recording)
            onsets = stimu / sfreq  # Convert samples to seconds
            durations = np.zeros(min_len)
            
            for i in range(min_len):
                if i < min_len - 1:
                    durations[i] = onsets[i + 1] - onsets[i]
                else:
                    durations[i] = raw.times[-1] - onsets[i]
            
            # Create descriptions based on attended speaker
            descriptions = []
            for att in attended:
                att_val = int(att) if not np.isnan(att) else 0
                if att_val == 1:
                    descriptions.append('attend_speaker_1')
                elif att_val == 2:
                    descriptions.append('attend_speaker_2')
                else:
                    descriptions.append('unknown')
            
            # Create MNE Annotations
            raw_annotations = mne.Annotations(
                onset=onsets.tolist(),
                duration=durations.tolist(),
                description=descriptions
            )
            raw.set_annotations(raw_annotations)
            
            # Create derived misc channel: attended_speaker_label
            # This creates a continuous channel with the attended speaker label
            # for each time point, useful for epoch-level analysis
            
            # Initialize with zeros (unknown/no trial)
            attended_label_data = np.zeros((1, len(raw.times)))
            
            for i in range(min_len):
                onset_sample = int(stimu[i])
                if i < min_len - 1:
                    offset_sample = int(stimu[i + 1])
                else:
                    offset_sample = len(raw.times)
                
                # Clamp to valid range
                onset_sample = max(0, min(onset_sample, len(raw.times) - 1))
                offset_sample = max(onset_sample, min(offset_sample, len(raw.times)))
                
                # Set label value (1 or 2) for trial duration
                att_val = int(attended[i]) if not np.isnan(attended[i]) else 0
                if att_val in [1, 2]:
                    attended_label_data[0, onset_sample:offset_sample] = att_val
            
            # Create as a new channel
            misc_info = mne.create_info(
                ['attended_speaker_label'],
                sfreq=raw.info['sfreq'],
                ch_types=['misc']
            )
            misc_raw = mne.io.RawArray(attended_label_data, misc_info, verbose=False)
            
            # Add to existing raw
            raw.add_channels([misc_raw], force_update_info=True)
            
        else:
            # Missing stimu or attended fields - create unknown annotations
            # Source: analysis.md notes "stimu and attended fields may be missing in some versions"
            warnings.warn(f"Missing stimu or attended field in {file_path}. Creating 'unknown' annotations.")
            
            # Create a single long unknown annotation for the whole recording
            raw_annotations = mne.Annotations(
                onset=[0.0],
                duration=[raw.times[-1]],
                description=['unknown']
            )
            raw.set_annotations(raw_annotations)
            
            # Create derived misc channel with zeros (unknown)
            attended_label_data = np.zeros((1, len(raw.times)))
            misc_info = mne.create_info(
                ['attended_speaker_label'],
                sfreq=raw.info['sfreq'],
                ch_types=['misc']
            )
            misc_raw = mne.io.RawArray(attended_label_data, misc_info, verbose=False)
            raw.add_channels([misc_raw], force_update_info=True)
        
        # Ensure all misc channels are properly typed
        misc_channels = [ch for ch in raw.ch_names if ch in ['attended_speaker_label', 'Status', 'EXG1', 'EXG2', 'EXG3', 'EXG4', 'EXG5', 'EXG6', 'EXG7', 'EXG8']]
        if misc_channels:
            ch_type_map = {ch: 'misc' for ch in misc_channels}
            # Only set for channels that aren't already correctly typed
            current_types = raw.get_channel_types(picks=misc_channels)
            to_update = {}
            for ch, current_type in zip(misc_channels, current_types):
                if current_type != 'misc':
                    to_update[ch] = 'misc'
            if to_update:
                raw.set_channel_types(to_update)
        
        return raw


KERNEL = ZenodoDTUKernel()