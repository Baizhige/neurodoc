import json
import os
import numpy as np
import pandas as pd
import mne


class OtherHighGammaDatasetKernel:
    KERNEL_ID = "other_highgammadataset"
    KERNEL_NAME = "High-Gamma Dataset - Motor Imagery/Execution"
    KERNEL_DESCRIPTION = "EEG kernel for the High-Gamma Dataset with 4-class motor imagery/execution (left hand, right hand, feet, rest) from EDF files"
    KERNEL_CITATION = "10.1002/hbm.23730"
    KERNEL_LICENSE = "ODbL"
    KERNEL_URL = "https://gin.g-node.org/robintibor/high-gamma-dataset"

    required_event_ids = ['feet', 'left_hand', 'rest', 'right_hand']
    required_info_fields = ['age', 'sex', 'amplifier', 'cap', 'handedness']
    required_native_misc = []
    derived_misc_channels = []

    # Standard 10-20 channel names for this dataset (128 channels, actiCap)
    # Based on the paper: 128-channel actiCap with 10-20 system extended
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1', 'Fpz': 'Fpz', 'Fp2': 'Fp2',
        'AF7': 'AF7', 'AF3': 'AF3', 'AFz': 'AFz', 'AF4': 'AF4', 'AF8': 'AF8',
        'F7': 'F7', 'F5': 'F5', 'F3': 'F3', 'F1': 'F1', 'Fz': 'Fz',
        'F2': 'F2', 'F4': 'F4', 'F6': 'F6', 'F8': 'F8',
        'FT7': 'FT7', 'FC5': 'FC5', 'FC3': 'FC3', 'FC1': 'FC1', 'FCz': 'FCz',
        'FC2': 'FC2', 'FC4': 'FC4', 'FC6': 'FC6', 'FT8': 'FT8',
        'T7': 'T7', 'C5': 'C5', 'C3': 'C3', 'C1': 'C1', 'Cz': 'Cz',
        'C2': 'C2', 'C4': 'C4', 'C6': 'C6', 'T8': 'T8',
        'TP7': 'TP7', 'CP5': 'CP5', 'CP3': 'CP3', 'CP1': 'CP1', 'CPz': 'CPz',
        'CP2': 'CP2', 'CP4': 'CP4', 'CP6': 'CP6', 'TP8': 'TP8',
        'P7': 'P7', 'P5': 'P5', 'P3': 'P3', 'P1': 'P1', 'Pz': 'Pz',
        'P2': 'P2', 'P4': 'P4', 'P6': 'P6', 'P8': 'P8',
        'PO7': 'PO7', 'PO3': 'PO3', 'POz': 'POz', 'PO4': 'PO4', 'PO8': 'PO8',
        'O1': 'O1', 'Oz': 'Oz', 'O2': 'O2',
        # Extended 10-10/10-5 channels commonly in 128-channel setups
        'FFC1h': 'FFC1h', 'FFC2h': 'FFC2h', 'FFC3h': 'FFC3h', 'FFC4h': 'FFC4h',
        'FFC5h': 'FFC5h', 'FFC6h': 'FFC6h',
        'FCC1h': 'FCC1h', 'FCC2h': 'FCC2h', 'FCC3h': 'FCC3h', 'FCC4h': 'FCC4h',
        'FCC5h': 'FCC5h', 'FCC6h': 'FCC6h',
        'CCP1h': 'CCP1h', 'CCP2h': 'CCP2h', 'CCP3h': 'CCP3h', 'CCP4h': 'CCP4h',
        'CCP5h': 'CCP5h', 'CCP6h': 'CCP6h',
        'CPP1h': 'CPP1h', 'CPP2h': 'CPP2h', 'CPP3h': 'CPP3h', 'CPP4h': 'CPP4h',
        'CPP5h': 'CPP5h', 'CPP6h': 'CPP6h',
        'PPO1h': 'PPO1h', 'PPO2h': 'PPO2h',
        'OI1h': 'OI1h', 'OI2h': 'OI2h',
        'I1': 'I1', 'Iz': 'Iz', 'I2': 'I2',
        # Additional channels that may appear
        'M1': 'M1', 'M2': 'M2',
        'A1': 'A1', 'A2': 'A2',
        'TP9': 'TP9', 'TP10': 'TP10',
        'FT9': 'FT9', 'FT10': 'FT10',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # Look for typical BIDS root indicators
        for i, part in enumerate(parts):
            if part.startswith('high-gamma') or part.startswith('high_gamma'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        # Another fallback: look for participants.tsv
        current = os.path.dirname(filepath)
        while current != os.sep and current != '':
            if os.path.exists(os.path.join(current, 'participants.tsv')):
                return current
            current = os.path.dirname(current)
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        p_tsv = os.path.join(bids_root, 'participants.tsv')
        if os.path.exists(p_tsv):
            return p_tsv
        return None

    def _read_participants_info(self, participants_tsv, subject_id):
        """Read subject info from participants.tsv."""
        if participants_tsv is None or not os.path.exists(participants_tsv):
            return {}
        try:
            df = pd.read_csv(participants_tsv, sep='\t')
            # Find subject column
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            # Match subject
            subj_rows = df[df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                # Try without 'sub-' prefix
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

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # EDF files should have corresponding events.tsv in BIDS
        base = os.path.splitext(eeg_file_path)[0]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without suffix variations
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(eeg_file_path)
        # Remove extension
        base_no_ext = os.path.splitext(base_name)[0]
        
        # Look for any events.tsv in same directory
        for f in os.listdir(dir_name):
            if f.endswith('_events.tsv') and f.startswith(base_no_ext.split('_')[0]):
                return os.path.join(dir_name, f)
        
        return None

    def _read_events_tsv(self, events_tsv):
        """Read events from events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            return df
        except Exception:
            return None

    def _events_to_annotations(self, events_df, raw_sfreq):
        """Convert events DataFrame to MNE Annotations."""
        if events_df is None or len(events_df) == 0:
            return None
        
        onsets = []
        durations = []
        descriptions = []
        
        for _, row in events_df.iterrows():
            # Standard BIDS columns
            onset = row.get('onset', None)
            duration = row.get('duration', 0.0)
            trial_type = row.get('trial_type', None)
            value = row.get('value', None)
            
            if onset is None:
                continue
            
            # Use trial_type if available, otherwise value
            desc = trial_type if pd.notna(trial_type) else str(value)
            if desc is None or (isinstance(desc, float) and np.isnan(desc)):
                continue
            
            onsets.append(float(onset))
            durations.append(float(duration) if pd.notna(duration) else 0.0)
            descriptions.append(str(desc))
        
        if len(onsets) == 0:
            return None
        
        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row or udataset
        filepath = row.get('File Path', None)
        if filepath is None and hasattr(udataset, 'get_file_path'):
            filepath = udataset.get_file_path(row)
        
        # Find BIDS root and participants.tsv
        bids_root = self._find_bids_root(filepath) if filepath else None
        participants_tsv = self._find_participants_tsv(bids_root)
        
        # Get subject ID
        subject_id = self._get_subject_id_from_path(filepath) if filepath else None
        
        # Read participants info for required fields
        participants_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Ensure all required fields are present
        for field in self.required_info_fields:
            if field not in participants_info:
                participants_info[field] = "unknown"
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participants_info.get("age", "unknown"),
            "sex": participants_info.get("sex", "unknown"),
            "amplifier": participants_info.get("amplifier", "unknown"),
            "cap": participants_info.get("cap", "unknown"),
            "handedness": participants_info.get("handedness", "unknown"),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Find and apply events from events.tsv
        events_tsv = self._find_events_tsv(filepath) if filepath else None
        events_df = self._read_events_tsv(events_tsv)
        annotations = self._events_to_annotations(events_df, raw.info['sfreq'])
        if annotations is not None:
            raw.set_annotations(annotations)
        
        # Add derived misc channels if specified
        for misc_name in self.derived_misc_channels:
            # Create a constant broadcast misc channel
            misc_data = np.zeros((1, len(raw.times)))
            # Create info for misc channel
            misc_info = mne.create_info([misc_name], raw.info['sfreq'], ch_types=['misc'])
            misc_raw = mne.io.RawArray(misc_data, misc_info)
            # Append to raw
            raw.add_channels([misc_raw], force_update_info=True)
        
        return raw


KERNEL = OtherHighGammaDatasetKernel()