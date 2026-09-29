import json
import os
import numpy as np
import pandas as pd
import mne


class PhysionetErpbciKernel:
    KERNEL_ID = "physionet_erpbci"
    KERNEL_NAME = "PhysioNet ERP-BCI - P300-based Brain-Computer Interface"
    KERNEL_DESCRIPTION = "EEG kernel for ERP-BCI dataset with P300 speller paradigm using 8-channel EEG"
    KERNEL_CITATION = "10.13026/C2101S"
    KERNEL_LICENSE = "ODC-By"
    KERNEL_URL = "https://physionet.org/content/erpbci/1.0.0/"

    # Required fields from participants.tsv
    required_event_ids = []
    required_info_fields = ['age', 'sex', 'amplifier', 'cap', 'handedness']
    required_native_misc = []
    derived_misc_channels = []

    # Channel renaming map for this dataset (10-20 system, 8 channels)
    CHANNEL_RENAME_MAP = {
        'FZ': 'Fz',
        'FCZ': 'FCz',
        'CZ': 'Cz',
        'CPZ': 'CPz',
        'P1': 'P1',
        'PZ': 'Pz',
        'P2': 'P2',
        'POZ': 'POz',
        # Alternative capitalizations that may appear
        'Fz': 'Fz',
        'FCz': 'FCz',
        'Cz': 'Cz',
        'CPz': 'CPz',
        'Pz': 'Pz',
        'POz': 'POz',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('erpbci') or part == 'erpbci':
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        # Fallback: look for participants.tsv
        current = os.path.dirname(filepath)
        while current and current != os.sep:
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
        # Try to infer from filename
        basename = os.path.basename(filepath)
        if basename.startswith('sub-'):
            # Extract sub-XX pattern
            parts2 = basename.split('_')
            if parts2[0].startswith('sub-'):
                return parts2[0]
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # For BIDS, events.tsv is alongside the eeg file
        base = eeg_file_path
        # Remove extensions
        for ext in ['.edf', '.set', '.eeg', '.fif', '.vhdr', '.vmrk', '.dat']:
            if base.lower().endswith(ext):
                base = base[:-len(ext)]
                break
        
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without any suffix (for files like sub-01_task-erpbci_eeg.edf)
        # events should be sub-01_task-erpbci_events.tsv
        if '_eeg' in base:
            alt_events = base.replace('_eeg', '_events') + '.tsv'
            if os.path.exists(alt_events):
                return alt_events
        
        # Try in the same directory with pattern matching
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)
        
        # Look for any events.tsv in same directory
        if os.path.isdir(dir_name):
            for f in os.listdir(dir_name):
                if f.endswith('_events.tsv'):
                    # Check if it matches our subject/task
                    if base_name.split('_')[0] in f:  # subject match
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

    def _events_to_annotations(self, events_df, raw):
        """Convert events dataframe to MNE Annotations."""
        if events_df is None or len(events_df) == 0:
            return None
        
        # Required BIDS columns
        if 'onset' not in events_df.columns:
            return None
        
        onsets = events_df['onset'].values
        durations = events_df['duration'].values if 'duration' in events_df.columns else np.zeros(len(onsets))
        
        # Use 'trial_type' if available, otherwise 'value', otherwise generic
        if 'trial_type' in events_df.columns:
            descriptions = events_df['trial_type'].astype(str).values
        elif 'value' in events_df.columns:
            descriptions = events_df['value'].astype(str).values
        else:
            descriptions = np.array(['event'] * len(onsets))
        
        # Create annotations
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
            orig_time=raw.info['meas_date'] if raw.info['meas_date'] is not None else None
        )
        return annotations

    def _get_standard_10_20_montage(self):
        """Get standard 10-20 montage for channel positions."""
        return mne.channels.make_standard_montage('standard_1020')

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        filepath = row.get('file_path', None)
        if filepath is None:
            filepath = row.get('File Path', None)
        
        subject_id = self._get_subject_id_from_path(filepath) if filepath else None
        
        bids_root = self._find_bids_root(filepath) if filepath else None
        participants_tsv = self._find_participants_tsv(bids_root)
        participants_info = self._read_participants_info(participants_tsv, subject_id) if subject_id else {}
        
        original_description = raw.info.get("description", "")
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": {
                "age": participants_info.get("age", "unknown"),
                "sex": participants_info.get("sex", "unknown"),
                "amplifier": participants_info.get("amplifier", "unknown"),
                "cap": participants_info.get("cap", "unknown"),
                "handedness": participants_info.get("handedness", "unknown"),
            },
        })
        
        return raw


KERNEL = PhysionetErpbciKernel()