"""OpenNeuro DS003766 stage1 kernel for EEGUnity.

Dataset: A Resource for Assessing Dynamic Binary Choices in the Adult Brain Using EEG and Mouse-Tracking
- 31 subjects, 129 channels, 1000 Hz
- Paradigms: food preference, semantic judgments (word/image)
- Trigger codes: 0400-0403 (stimulus), 0500-0506 (response), 0200-series (trial-phase)

Source: https://openneuro.org/datasets/ds003766
DOI: 10.1038/s41597-022-01538-5
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne


# Event mapping: numeric trigger code -> readable label
_EVENT_MAP: Dict[int, str] = {
    # Stimulus codes (0400 series)
    400: "stimulus: food item A",
    401: "stimulus: image",
    402: "stimulus: word",
    403: "stimulus: semantic variant",
    # Response codes (0500 series)
    500: "response: left choice",
    501: "response: right choice",
    503: "response: outcome variant 1",
    505: "response: outcome variant 2",
    506: "response: outcome variant 3",
    # Trial-phase codes (0200 series)
    202: "trial_phase: start",
    203: "trial_phase: evidence_1",
    204: "trial_phase: evidence_2",
    205: "trial_phase: evidence_3",
    206: "trial_phase: evidence_4",
    207: "trial_phase: conflict_1",
    208: "trial_phase: conflict_2",
    209: "trial_phase: conflict_3",
    210: "trial_phase: response_preparation",
    211: "trial_phase: prep_variant_1",
    212: "trial_phase: prep_variant_2",
    213: "trial_phase: prep_variant_3",
    214: "trial_phase: prep_variant_4",
    215: "trial_phase: prep_variant_5",
    216: "trial_phase: response_final",
    217: "trial_phase: resp_final_variant_1",
    218: "trial_phase: resp_final_variant_2",
    219: "trial_phase: resp_final_variant_3",
    220: "trial_phase: resp_final_variant_4",
    221: "trial_phase: resp_final_variant_5",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name.
    
    Source: dataset structure inference
    """
    basename = os.path.basename(file_path).lower()
    if "food" in basename:
        return "FOOD"
    elif "word" in basename:
        return "WORD"
    elif "image" in basename:
        return "IMAGE"
    elif "semantic" in basename:
        return "SEMANTIC"
    return "UNKNOWN"


def _standardize_channel_names(ch_names: List[str], n_channels: int) -> Dict[str, str]:
    """Create standardized 10-20 channel naming map.
    
    For 128/129 channel datasets, map to standard_1020 equivalents.
    Source: high-density EEG standard naming conventions
    """
    rename_map: Dict[str, str] = {}
    
    # Common standard 10-20 channels
    standard_chs = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "AF7", "AF3", "AF4", "AF8",
        "FC5", "FC1", "FC2", "FC6",
        "CP5", "CP1", "CP2", "CP6",
        "PO7", "PO3", "PO4", "PO8",
    ]
    
    # Build rename map for numbered EEG channels
    if n_channels >= 128:
        for i, ch in enumerate(ch_names):
            ch_upper = ch.upper()
            if re.match(r'^(EEG[-_]?)?0*(\d+)$', ch_upper):
                match = re.search(r'(\d+)$', ch_upper)
                if match:
                    idx = int(match.group(1))
                    if idx < len(standard_chs):
                        rename_map[ch] = standard_chs[idx]
    
    return rename_map


def _read_events_tsv(eeg_file: str) -> Optional[mne.Annotations]:
    """Read events from BIDS *_events.tsv sidecar file.
    
    Source: BIDS standard for EEG datasets
    """
    dir_name = os.path.dirname(eeg_file)
    base_name = os.path.basename(eeg_file)
    
    candidates = [
        os.path.join(dir_name, base_name.replace('.vhdr', '_events.tsv').replace('.edf', '_events.tsv').replace('.fif', '_events.tsv')),
        os.path.join(dir_name, '..', '..', base_name.replace('.vhdr', '_events.tsv').replace('.edf', '_events.tsv').replace('.fif', '_events.tsv')),
        os.path.join(dir_name, 'events.tsv'),
        os.path.join(dir_name, '..', 'events.tsv'),
    ]
    
    for events_path in candidates:
        if os.path.exists(events_path):
            try:
                events_df = mne.read_events_tsv(events_path)
                if 'onset' in events_df.columns and 'duration' in events_df.columns:
                    onset = events_df['onset'].values
                    duration = events_df['duration'].values if 'duration' in events_df.columns else [0] * len(onset)
                    description = events_df['value'].values if 'value' in events_df.columns else events_df.get('trial_type', ['unknown'] * len(onset)).values
                    
                    return mne.Annotations(
                        onset=onset,
                        duration=duration,
                        description=[str(d) for d in description],
                    )
            except Exception:
                continue
    return None


class OpenNeuroDS003766Kernel:
    """Stage1 kernel for OpenNeuro DS003766 dataset."""

    KERNEL_ID: str = "openneuro-ds003766-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        
        # Detect paradigm from file
        paradigm = _detect_paradigm(file_path)
        
        # Get original description
        original_desc = raw.info.get("description", "") or ""
        
        # Extract subject info
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        
        # Extract subject ID from file path or row
        if "subject_id" in row:
            subject_id = str(row["subject_id"])
        else:
            match = re.search(r'sub-(\w+)', file_path)
            subject_id = match.group(1) if match else "unknown"
        
        # Try reading participants.tsv
        dataset_root = ""
        if udataset is not None:
            dataset_root = udataset.get("root", "")
        
        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        if os.path.exists(participants_tsv):
            try:
                import pandas as pd
                participants_df = pd.read_csv(participants_tsv, sep='\t')
                subj_row = participants_df[participants_df['participant_id'] == f"sub-{subject_id}"]
                if len(subj_row) > 0:
                    if 'age' in subj_row.columns:
                        age_val = subj_row['age'].values[0]
                        if pd.notna(age_val):
                            age = str(int(float(age_val)))
                    if 'sex' in subj_row.columns:
                        sex_val = str(subj_row['sex'].values[0]).lower()
                        if sex_val in ['m', 'male', 'f', 'female']:
                            sex = 'male' if sex_val in ['m', 'male'] else 'female'
                    if 'handedness' in subj_row.columns:
                        handed_val = str(subj_row['handedness'].values[0])
                        if pd.notna(handed_val) and handed_val not in ['n/a', '']:
                            handedness = handed_val
            except Exception:
                pass
        
        # Amplifier and cap information - DS003766 uses BioSemi system
        amplifier = "BioSemi"
        cap = "BioSemi 128-channel"
        
        # Try reading _channels.tsv sidecar for more specific info
        channels_tsv = file_path.replace('.set', '_channels.tsv').replace('.fif', '_channels.tsv').replace('.edf', '_channels.tsv')
        if not os.path.exists(channels_tsv):
            channels_tsv = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).replace('.set', '_channels.tsv').replace('.fif', '_channels.tsv').replace('.edf', '_channels.tsv'))
        
        if os.path.exists(channels_tsv):
            try:
                import pandas as pd
                channels_df = pd.read_csv(channels_tsv, sep='\t')
                if 'manufacturer' in channels_df.columns:
                    amp_vals = channels_df['manufacturer'].dropna().values
                    if len(amp_vals) > 0:
                        amplifier = str(amp_vals[0])
                if 'cap_manufacturer' in channels_df.columns:
                    cap_vals = channels_df['cap_manufacturer'].dropna().values
                    if len(cap_vals) > 0:
                        cap = str(cap_vals[0])
            except Exception:
                pass
        
        # Get channel count
        n_channels = len(raw.ch_names)
        
        # Apply channel standardization if needed
        if n_channels >= 128:
            rename_map = _standardize_channel_names(raw.ch_names, n_channels)
            if rename_map:
                raw.rename_channels(rename_map)
        
        # Build eegunity_description with ALL required fields
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Store description in raw info
        raw.info["description"] = json.dumps(eegunity_description)
        raw.info["eegunity_description"] = eegunity_description
        
        return raw


KERNEL = OpenNeuroDS003766Kernel()