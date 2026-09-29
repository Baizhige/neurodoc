import json
import os
import numpy as np
import pandas as pd
import mne


class OpenneuroDs004022Kernel:
    KERNEL_ID = "openneuro_ds004022"
    KERNEL_NAME = "OpenNeuro ds004022 - Right-Upper Limb Motor Imagery"
    KERNEL_DESCRIPTION = "EEG kernel for 4-class right-upper limb motor imagery (reaching, grasping, lifting, twisting) in Parkinson's disease and healthy controls"
    KERNEL_CITATION = "10.18112/openneuro.ds004022.v1.0.0"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds004022"

    # BIDS mapping
    required_event_ids = ['S  2', 'S  3', 'S  4', 'S  5', 'S  6', 'S  7', 'S  8', 'S  9', 'S 10']
    required_info_fields = ['Hand Dominance', 'Years Since Diagnosis', 'age', 'sex']
    required_native_misc = []
    derived_misc_channels = ['age_binned', 'diagnosis_duration_binned']

    # Standard 10-20 channel names for this dataset
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F3': 'F3',
        'F4': 'F4',
        'C3': 'C3',
        'C4': 'C4',
        'P3': 'P3',
        'P4': 'P4',
        'O1': 'O1',
        'O2': 'O2',
        'F7': 'F7',
        'F8': 'F8',
        'T7': 'T7',
        'T8': 'T8',
        'P7': 'P7',
        'P8': 'P8',
        'Fz': 'Fz',
        'Cz': 'Cz',
        'Pz': 'Pz',
        'Oz': 'Oz',
        'FC1': 'FC1',
        'FC2': 'FC2',
        'CP1': 'CP1',
        'CP2': 'CP2',
        'FC5': 'FC5',
        'FC6': 'FC6',
        'CP5': 'CP5',
        'CP6': 'CP6',
        'AFz': 'AFz',
        'AF3': 'AF3',
        'AF4': 'AF4',
        'AF7': 'AF7',
        'AF8': 'AF8',
        'F1': 'F1',
        'F2': 'F2',
        'F5': 'F5',
        'F6': 'F6',
        'FT7': 'FT7',
        'FT8': 'FT8',
        'C1': 'C1',
        'C2': 'C2',
        'C5': 'C5',
        'C6': 'C6',
        'TP7': 'TP7',
        'TP8': 'TP8',
        'P1': 'P1',
        'P2': 'P2',
        'P5': 'P5',
        'P6': 'P6',
        'PO3': 'PO3',
        'PO4': 'PO4',
        'PO7': 'PO7',
        'PO8': 'PO8',
        'POz': 'POz',
        'Fpz': 'Fpz',
        'CP3': 'CP3',
        'CP4': 'CP4',
        'FC3': 'FC3',
        'FC4': 'FC4',
        'F9': 'F9',
        'F10': 'F10',
        'FT9': 'FT9',
        'FT10': 'FT10',
        'TP9': 'TP9',
        'TP10': 'TP10',
        'P9': 'P9',
        'P10': 'P10',
        'PO9': 'PO9',
        'PO10': 'PO10',
        'O9': 'O9',
        'O10': 'O10',
        'Iz': 'Iz',
        'Nz': 'Nz',
        'T9': 'T9',
        'T10': 'T10',
        'A1': 'A1',
        'A2': 'A2',
        'M1': 'M1',
        'M2': 'M2',
        'TPP7h': 'TPP7h',
        'TPP8h': 'TPP8h',
        'CPP1': 'CPP1',
        'CPP2': 'CPP2',
        'CPP3': 'CPP3',
        'CPP4': 'CPP4',
        'CPP5': 'CPP5',
        'CPP6': 'CPP6',
        'FPP1': 'FPP1',
        'FPP2': 'FPP2',
        'FCC3': 'FCC3',
        'FCC4': 'FCC4',
        'FCC5': 'FCC5',
        'FCC6': 'FCC6',
        'CCP3': 'CCP3',
        'CCP4': 'CCP4',
        'CCP5': 'CCP5',
        'CCP6': 'CCP6',
        'PPO1': 'PPO1',
        'PPO2': 'PPO2',
        'PPO9': 'PPO9',
        'PPO10': 'PPO10',
        'OI1': 'OI1',
        'OI2': 'OI2',
        'I1': 'I1',
        'I2': 'I2',
        'AFp1': 'AFp1',
        'AFp2': 'AFp2',
        'AFp3': 'AFp3',
        'AFp4': 'AFp4',
        'AFp5': 'AFp5',
        'AFp6': 'AFp6',
        'AFp7': 'AFp7',
        'AFp8': 'AFp8',
        'AFp9': 'AFp9',
        'AFp10': 'AFp10',
        'AFF1': 'AFF1',
        'AFF2': 'AFF2',
        'AFF3': 'AFF3',
        'AFF4': 'AFF4',
        'AFF5': 'AFF5',
        'AFF6': 'AFF6',
        'AFF7': 'AFF7',
        'AFF8': 'AFF8',
        'AFF9': 'AFF9',
        'AFF10': 'AFF10',
        'FFT7h': 'FFT7h',
        'FFT8h': 'FFT8h',
        'FFT9h': 'FFT9h',
        'FFT10h': 'FFT10h',
        'FTT7h': 'FTT7h',
        'FTT8h': 'FTT8h',
        'FTT9h': 'FTT9h',
        'FTT10h': 'FTT10h',
        'TTP7h': 'TTP7h',
        'TTP8h': 'TTP8h',
        'TTP9h': 'TTP9h',
        'TTP10h': 'TTP10h',
        'TPP9h': 'TPP9h',
        'TPP10h': 'TPP10h',
        'PPO5': 'PPO5',
        'PPO6': 'PPO6',
        'PPO7h': 'PPO7h',
        'PPO8h': 'PPO8h',
        'OPP1': 'OPP1',
        'OPP2': 'OPP2',
        'OPP3': 'OPP3',
        'OPP4': 'OPP4',
        'OPP5': 'OPP5',
        'OPP6': 'OPP6',
        'POO1': 'POO1',
        'POO2': 'POO2',
        'POO3': 'POO3',
        'POO4': 'POO4',
        'POO5': 'POO5',
        'POO6': 'POO6',
        'POO7': 'POO7',
        'POO8': 'POO8',
        'POO9': 'POO9',
        'POO10': 'POO10',
        'OOp1': 'OOp1',
        'OOp2': 'OOp2',
        'OOp3': 'OOp3',
        'OOp4': 'OOp4',
        'OOp5': 'OOp5',
        'OOp6': 'OOp6',
        'OOp7': 'OOp7',
        'OOp8': 'OOp8',
        'OOp9': 'OOp9',
        'OOp10': 'OOp10',
        'OIz': 'OIz',
        'OzIz': 'OzIz',
        'POzO1': 'POzO1',
        'POzO2': 'POzO2',
    }

    def __init__(self):
        pass

    def _get_bids_root(self, raw_path):
        """Extract BIDS root from raw file path."""
        parts = raw_path.split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                return os.sep.join(parts[:i])
        current = os.path.dirname(raw_path)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return None

    def _get_subject_id(self, raw_path):
        """Extract subject ID from file path."""
        parts = raw_path.split(os.sep)
        for part in parts:
            if part.startswith("sub-"):
                return part
        return None

    def _read_participants_info(self, bids_root, subject_id):
        """Read subject info from participants.tsv."""
        if bids_root is None:
            return {}
        p_tsv = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(p_tsv):
            return {}
        try:
            df = pd.read_csv(p_tsv, sep='\t')
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            subj_rows = df[df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                if subject_id.startswith('sub-'):
                    alt_id = subject_id[4:]
                else:
                    alt_id = 'sub-' + subject_id
                subj_rows = df[df[subj_col] == alt_id]

            if len(subj_rows) == 0:
                return {}

            row = subj_rows.iloc[0]
            info = {}
            for field in self.required_info_fields:
                if field in row:
                    val = row[field]
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
            return info
        except Exception:
            return {}

    def _find_events_tsv(self, raw_path):
        """Find corresponding events.tsv file."""
        if raw_path.endswith('_eeg.set'):
            base = raw_path[:-8]
            events_tsv = base + '_events.tsv'
            if os.path.exists(events_tsv):
                return events_tsv
        # Try common patterns
        dir_name = os.path.dirname(raw_path)
        base_name = os.path.basename(raw_path)
        if '_eeg.' in base_name:
            prefix = base_name.split('_eeg.')[0]
            events_tsv = os.path.join(dir_name, prefix + '_events.tsv')
            if os.path.exists(events_tsv):
                return events_tsv
        return None

    def _read_events_tsv(self, events_tsv_path):
        """Read events from events.tsv file."""
        if events_tsv_path is None or not os.path.exists(events_tsv_path):
            return None
        try:
            df = pd.read_csv(events_tsv_path, sep='\t')
            return df
        except Exception:
            return None

    def _events_to_annotations(self, events_df, sfreq):
        """Convert events dataframe to MNE Annotations."""
        if events_df is None or len(events_df) == 0:
            return None
        onsets = []
        durations = []
        descriptions = []
        for _, event_row in events_df.iterrows():
            if 'onset' in event_row:
                onset = float(event_row['onset'])
            elif 'sample' in event_row:
                onset = float(event_row['sample']) / sfreq
            else:
                continue
            duration = float(event_row.get('duration', 0))
            if duration <= 0:
                duration = 0.0
            if 'trial_type' in event_row and pd.notna(event_row['trial_type']):
                desc = str(event_row['trial_type'])
            elif 'value' in event_row and pd.notna(event_row['value']):
                desc = str(event_row['value'])
            elif 'stim_file' in event_row and pd.notna(event_row['stim_file']):
                desc = str(event_row['stim_file'])
            else:
                continue
            onsets.append(onset)
            durations.append(duration)
            descriptions.append(desc)
        if len(onsets) == 0:
            return None
        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def _add_derived_misc(self, raw, channel_name, value, sfreq):
        """Add a derived misc channel with constant value."""
        data = np.full((1, len(raw.times)), float(value), dtype=np.float64)
        info = mne.create_info([channel_name], sfreq=sfreq, ch_types=['misc'])
        misc_raw = mne.io.RawArray(data, info, verbose=False)
        raw.add_channels([misc_raw], force_update_info=True)
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row or raw
        filepath = None
        if hasattr(raw, 'filenames') and raw.filenames:
            filepath = raw.filenames[0]
        elif hasattr(raw, 'fname'):
            filepath = raw.fname
        elif isinstance(row, pd.Series):
            for key in ['file_path', 'filepath', 'filename', 'path']:
                if key in row.index:
                    filepath = row[key]
                    break
        
        if filepath is None:
            filepath = ''
        
        # Get BIDS root and subject ID
        bids_root = self._get_bids_root(filepath)
        subject_id = self._get_subject_id(filepath)
        
        # Read participants info
        participants_info = self._read_participants_info(bids_root, subject_id)
        
        # Get original description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Build eegunity_description
        eegunity_desc = {
            "age": participants_info.get('age', 'unknown'),
            "sex": participants_info.get('sex', 'unknown').lower() if participants_info.get('sex') else 'unknown',
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": participants_info.get('Hand Dominance', 'unknown'),
        }
        # Add extra required info fields
        for field in self.required_info_fields:
            if field not in ['age', 'sex', 'Hand Dominance']:
                eegunity_desc[field] = participants_info.get(field, 'unknown')
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Channel rename before set_montage
        current_names = raw.ch_names
        rename_map = {}
        for ch in current_names:
            if ch in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Add derived misc channels from participants.tsv
        sfreq = raw.info['sfreq']
        
        # age_binned: from participants.tsv:age, threshold at 65
        age_val = participants_info.get('age')
        if age_val is not None and age_val != 'unknown':
            try:
                age_num = float(age_val)
                age_binned = 1.0 if age_num >= 65 else 0.0
                raw = self._add_derived_misc(raw, 'age_binned', age_binned, sfreq)
            except (ValueError, TypeError):
                pass  # skip if cannot parse
        
        # diagnosis_duration_binned: from participants.tsv:Years Since Diagnosis, median split at ~24
        diag_val = participants_info.get('Years Since Diagnosis')
        if diag_val is not None and diag_val != 'unknown':
            try:
                diag_num = float(diag_val)
                diagnosis_duration_binned = 1.0 if diag_num >= 24 else 0.0
                raw = self._add_derived_misc(raw, 'diagnosis_duration_binned', diagnosis_duration_binned, sfreq)
            except (ValueError, TypeError):
                pass  # skip if cannot parse
        
        return raw


KERNEL = OpenneuroDs004022Kernel()