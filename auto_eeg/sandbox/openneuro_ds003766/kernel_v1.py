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
# Source: analysis.md Event Structure table
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
        # High-density system - use standard mapping
        # Try to match patterns like EEG001 -> standard positions
        for i, ch in enumerate(ch_names):
            ch_upper = ch.upper()
            # Pattern: EEG-001 or EEG001 or E001
            if re.match(r'^(EEG[-_]?)?0*(\d+)$', ch_upper):
                match = re.search(r'(\d+)$', ch_upper)
                if match:
                    idx = int(match.group(1))
                    # Map to standard 10-20 positions by index
                    if idx < len(standard_chs):
                        rename_map[ch] = standard_chs[idx]
    
    return rename_map


def _read_events_tsv(eeg_file: str) -> Optional[mne.Annotations]:
    """Read events from BIDS *_events.tsv sidecar file.
    
    Source: BIDS standard for EEG datasets
    """
    # Derive events.tsv path from EEG file path
    dir_name = os.path.dirname(eeg_file)
    base_name = os.path.basename(eeg_file)
    
    # Try common patterns: events.tsv in same dir or parent
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

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object with standardized metadata.
        """
        file_path = row.get("File Path", "")
        
        # Detect paradigm from file
        paradigm = _detect_paradigm(file_path)
        
        # Get original description
        original_desc = raw.info.get("description", "")
        
        # Extract subject info if available from BIDS
        # Source: participants.tsv (if available)
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        
        # Try to get from row metadata or participants.tsv
        if "subject_id" in row:
            subject_id = str(row["subject_id"])
        else:
            # Extract from file path: sub-XX
            match = re.search(r'sub-(\w+)', file_path)
            subject_id = match.group(1) if match else "unknown"
        
        # Try reading participants.tsv
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
                            age = str(int(float(age_val)))  # LLM 推断，需人类复核
                    if 'sex' in subj_row.columns:
                        sex_val = str(subj_row['sex'].values[0]).lower()
                        if sex_val in ['m', 'male', 'f', 'female']:
                            sex = 'male' if sex_val in ['m', 'male'] else 'female'  # LLM 推断，需人类复核
                    if 'handedness' in subj_row.columns:
                        handed_val = str(subj_row['handedness'].values[0]).lower()
                        if handed_val in ['r', 'right', 'l', 'left']:
                            handedness = 'right' if handed_val in ['r', 'right'] else 'left'  # LLM 推断，需人类复核
            except Exception:
                pass
        
        # Write eegunity_description
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Standardize channel names BEFORE set_montage
        n_channels = len(raw.ch_names)
        ch_names = raw.ch_names.copy()
        
        # Check if channels need renaming
        needs_rename = False
        for ch in ch_names:
            if ch.upper().startswith('EEG') and re.search(r'\d', ch):
                needs_rename = True
                break
        
        if needs_rename:
            rename_map = _standardize_channel_names(ch_names, n_channels)
            if rename_map:
                renamed_count = raw.rename_channels(rename_map)
        
        # Try to set montage (standard 1020 for high-density)
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Keep only channels that exist in both raw and montage
            common_chs = set(raw.ch_names) & set(montage.ch_names)
            if len(common_chs) >= 20:  # Only set if we have enough channels
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass  # Skip montage if not applicable
        
        # Extract and set annotations from trigger events
        # First check if raw has stim channels with trigger codes
        annotations = raw.annotations
        
        if len(annotations) == 0:
            # Try reading from events.tsv
            events_annot = _read_events_tsv(file_path)
            if events_annot is not None and len(events_annot) > 0:
                raw.set_annotations(events_annot)
                annotations = events_annot
        
        # If still no annotations, try to find trigger codes in data
        if len(annotations) == 0:
            try:
                # Look for stimulus channel
                stim_ch = None
                for ch in raw.ch_names:
                    if 'stim' in ch.lower() or 'trigger' in ch.lower() or 'status' in ch.lower():
                        stim_ch = ch
                        break
                
                if stim_ch is None:
                    # Try to find MISC or STIM channel
                    ch_types = raw.get_channel_types()
                    for i, (ch, ch_type) in enumerate(zip(raw.ch_names, ch_types)):
                        if ch_type in ['stim', 'misc']:
                            stim_ch = raw.ch_names[i]
                            break
                
                if stim_ch is not None:
                    stim_data, _ = raw[stim_ch]
                    # Find transitions (trigger onsets)
                    diff_data = np.diff(stim_data.flatten())
                    onsets = np.where(np.abs(diff_data) > 0)[0] / raw.info['sfreq']
                    
                    # Get trigger values at onsets
                    trigger_values = stim_data.flatten()[np.where(np.abs(diff_data) > 0)[0] + 1]
                    
                    # Filter and map trigger codes
                    valid_on = []
                    valid_dur = []
                    valid_desc = []
                    for onset, val in zip(onsets, trigger_values):
                        code = int(val)
                        if code in _EVENT_MAP:
                            valid_on.append(onset)
                            valid_dur.append(0)
                            valid_desc.append(_EVENT_MAP[code])
                        elif 200 <= code <= 600:
                            # Other trigger codes - map generically
                            valid_on.append(onset)
                            valid_dur.append(0)
                            valid_desc.append(f"trigger: {code}")
                    
                    if valid_on:
                        raw.set_annotations(mne.Annotations(
                            onset=valid_on,
                            duration=valid_dur,
                            description=valid_desc,
                        ))
            except Exception:
                pass
        
        # Filter out boundary events from annotations if present
        current_annot = raw.annotations
        if len(current_annot) > 0:
            mask = np.array([desc.lower() != 'boundary' for desc in current_annot.description])
            if not mask.all():
                new_onset = current_annot.onset[mask]
                new_duration = current_annot.duration[mask]
                new_desc = [d for d, m in zip(current_annot.description, mask) if m]
                raw.set_annotations(mne.Annotations(
                    onset=new_onset,
                    duration=new_duration,
                    description=new_desc,
                ))
        
        return raw


import numpy as np

KERNEL = OpenNeuroDS003766Kernel()