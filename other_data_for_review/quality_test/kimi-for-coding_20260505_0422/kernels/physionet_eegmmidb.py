import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class PhysionetEegmmidbKernel:
    KERNEL_ID = "physionet_eegmmidb"
    KERNEL_NAME = "PhysioNet EEG Motor Movement/Imagery Database"
    KERNEL_DESCRIPTION = "EEG kernel for PhysioNet EEGMMIDB with 109 subjects performing motor execution and imagery tasks"
    KERNEL_CITATION = "10.13026/C28G6P"
    KERNEL_LICENSE = "ODbL"
    KERNEL_URL = "https://physionet.org/content/eegmmidb/1.0.0/"

    required_event_ids = ['T0', 'T1', 'T2']
    required_info_fields = ['age', 'sex', 'amplifier', 'cap', 'handedness']
    required_native_misc = []
    derived_misc_channels = ['run_number', 'run_type']

    # Standard 10-20 channel names for EEGMMIDB (64 channels)
    CHANNEL_RENAME_MAP = {
        'FC5': 'FC5', 'FC3': 'FC3', 'FC1': 'FC1', 'FCz': 'FCz', 'FC2': 'FC2', 'FC4': 'FC4', 'FC6': 'FC6',
        'C5': 'C5', 'C3': 'C3', 'C1': 'C1', 'Cz': 'Cz', 'C2': 'C2', 'C4': 'C4', 'C6': 'C6',
        'CP5': 'CP5', 'CP3': 'CP3', 'CP1': 'CP1', 'CPz': 'CPz', 'CP2': 'CP2', 'CP4': 'CP4', 'CP6': 'CP6',
        'Fp1': 'Fp1', 'Fpz': 'Fpz', 'Fp2': 'Fp2',
        'AF7': 'AF7', 'AF3': 'AF3', 'AFz': 'AFz', 'AF4': 'AF4', 'AF8': 'AF8',
        'F7': 'F7', 'F5': 'F5', 'F3': 'F3', 'F1': 'F1', 'Fz': 'Fz', 'F2': 'F2', 'F4': 'F4', 'F6': 'F6', 'F8': 'F8',
        'FT7': 'FT7', 'FT8': 'FT8',
        'T7': 'T7', 'T8': 'T8', 'T9': 'T9', 'T10': 'T10',
        'TP7': 'TP7', 'TP8': 'TP8',
        'P7': 'P7', 'P5': 'P5', 'P3': 'P3', 'P1': 'P1', 'Pz': 'Pz', 'P2': 'P2', 'P4': 'P4', 'P6': 'P6', 'P8': 'P8',
        'PO7': 'PO7', 'PO3': 'PO3', 'POz': 'POz', 'PO4': 'PO4', 'PO8': 'PO8',
        'O1': 'O1', 'Oz': 'Oz', 'O2': 'O2',
        'Iz': 'Iz',
        # EOG channels
        'VEOa': 'VEOG', 'VEOb': 'VEOG', 'VEOG': 'VEOG',
        'HEOG': 'HEOG', 'HEOL': 'HEOG', 'HEOR': 'HEOG',
        # Sometimes labeled differently
        'A1': 'A1', 'A2': 'A2', 'M1': 'M1', 'M2': 'M2',
        'Ref': 'FCz', 'ref': 'FCz',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'eegmmidb' in part.lower() or part.startswith('ds'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern or 'S' subject pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-') or re.match(r'^S\d+$', part):
                return os.sep.join(parts[:i])
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        p_tsv = os.path.join(bids_root, 'participants.tsv')
        if os.path.exists(p_tsv):
            return p_tsv
        # Try alternative locations
        for root, dirs, files in os.walk(bids_root):
            if 'participants.tsv' in files:
                return os.path.join(root, 'participants.tsv')
            # Don't go too deep
            if root.count(os.sep) - bids_root.count(os.sep) >= 2:
                break
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

            # Normalize subject ID for matching
            search_ids = [subject_id]
            if subject_id.startswith('sub-'):
                search_ids.append(subject_id[4:])
            else:
                search_ids.append('sub-' + subject_id)
            # EEGMMIDB uses S001 format
            search_ids.append(subject_id.replace('sub-', 'S'))
            search_ids.append(subject_id.replace('sub-', ''))

            for sid in search_ids:
                subj_rows = df[df[subj_col].astype(str) == str(sid)]
                if len(subj_rows) > 0:
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
            return {}
        except Exception:
            return {}

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            # BIDS format: sub-001
            if part.startswith('sub-'):
                return part
            # EEGMMIDB format: S001
            m = re.match(r'^(S\d+)$', part)
            if m:
                return 'sub-' + m.group(1)[1:].zfill(3)
        # Try from filename
        basename = os.path.basename(filepath)
        m = re.search(r'S(\d{3})', basename)
        if m:
            return 'sub-' + m.group(1)
        return None

    def _extract_run_number(self, filepath):
        """Extract run number from filename or path."""
        basename = os.path.basename(filepath)
        # EEGMMIDB format: S001R01.edf, S001R01_fif.fif, etc.
        m = re.search(r'R(\d+)', basename)
        if m:
            return int(m.group(1))
        # BIDS format: ..._run-01_...
        m = re.search(r'run-(\d+)', basename)
        if m:
            return int(m.group(1))
        return None

    def _run_number_to_type(self, run_number):
        """Map run number to run type category."""
        if run_number is None:
            return "unknown"
        # Baseline runs (eyes open/closed)
        if run_number in [1, 2]:
            return "baseline"
        # Actual motor execution
        elif run_number in [3, 4, 5, 6, 11, 12, 13, 14]:
            return "actual"
        # Imagined motor
        elif run_number in [7, 8, 9, 10]:
            return "imagined"
        return "unknown"

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file."""
        # Try BIDS sidecar naming
        base = os.path.splitext(eeg_file_path)[0]
        # Handle .fif.gz, .edf, .set, etc.
        for ext in ['', '.edf', '.set', '.fif', '.fif.gz', '.eeg', '.vhdr', '.vmrk']:
            base_clean = base
            if base_clean.endswith(ext):
                base_clean = base_clean[:-len(ext)] if ext else base_clean
        
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try in same directory
        dirname = os.path.dirname(eeg_file_path)
        basename = os.path.basename(eeg_file_path)
        # Strip extensions
        name = basename
        for ext in ['.fif.gz', '.fif', '.edf', '.set', '.eeg', '.vhdr']:
            if name.endswith(ext):
                name = name[:-len(ext)]
                break
        
        events_tsv = os.path.join(dirname, name + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
            
        # Try BIDS events.tsv in parent directories
        parts = os.path.normpath(eeg_file_path).split(os.sep)
        for i in range(len(parts)-1, 0, -1):
            if parts[i].startswith('sub-') or re.match(r'^S\d+$', parts[i]):
                subj_dir = os.sep.join(parts[:i+1])
                for root, dirs, files in os.walk(subj_dir):
                    if 'events.tsv' in files:
                        return os.path.join(root, 'events.tsv')
                break
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

    def _add_misc_channel(self, raw, name, data):
        """Add a misc channel to the raw object."""
        # Create info for new channel
        info = mne.create_info([name], raw.info['sfreq'], ch_types=['misc'])
        # Create RawArray with the data
        misc_raw = mne.io.RawArray(data, info, verbose=False)
        # Add to existing raw
        raw.add_channels([misc_raw], force_update_info=True)
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from udataset or row
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        
        # Extract subject ID
        subject_id = self._get_subject_id_from_path(filepath)
        if subject_id is None:
            subject_id = 'unknown'
        
        # Find BIDS root and participants.tsv
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        
        # Read participant info - REQUIRED FIELDS
        participant_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Ensure all required fields are present with at least "unknown"
        for field in self.required_info_fields:
            if field not in participant_info:
                participant_info[field] = "unknown"
        
        # Extract run info
        run_number = self._extract_run_number(filepath)
        run_type = self._run_number_to_type(run_number)
        run_number_str = str(run_number) if run_number is not None else "unknown"
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get('age', 'unknown'),
            "sex": participant_info.get('sex', 'unknown'),
            "amplifier": participant_info.get('amplifier', 'unknown'),
            "cap": participant_info.get('cap', 'unknown'),
            "handedness": participant_info.get('handedness', 'unknown'),
            "run_number": run_number_str,
            "run_type": run_type,
            "subject_id": subject_id,
        }
        
        # Get original description
        original_description = raw.info.get('description', '') if raw.info.get('description') else ''
        
        # Set description as JSON string (MNE requires string, not dict)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Add derived misc channels
        n_times = len(raw.times)
        
        # run_number as constant broadcast misc channel
        try:
            run_num_val = float(run_number) if run_number is not None else 0.0
        except (ValueError, TypeError):
            run_num_val = 0.0
        run_number_data = np.full((1, n_times), run_num_val)
        
        # run_type encoded as numeric: 0=unknown, 1=baseline, 2=actual, 3=imagined
        run_type_map = {'unknown': 0.0, 'baseline': 1.0, 'actual': 2.0, 'imagined': 3.0}
        run_type_val = run_type_map.get(run_type, 0.0)
        run_type_data = np.full((1, n_times), run_type_val)
        
        # Add misc channels
        raw = self._add_misc_channel(raw, 'run_number', run_number_data)
        raw = self._add_misc_channel(raw, 'run_type', run_type_data)
        
        # Handle events/annotations
        # Check if raw already has annotations with T0, T1, T2
        has_events = False
        if raw.annotations is not None and len(raw.annotations) > 0:
            existing_labels = set(raw.annotations.description)
            if existing_labels & set(self.required_event_ids):
                has_events = True
        
        # If no events, try to read from events.tsv
        if not has_events:
            events_tsv = self._find_events_tsv(filepath)
            events_df = self._read_events_tsv(events_tsv)
            
            if events_df is not None and len(events_df) > 0:
                # Look for onset and trial_type or event_id columns
                onset_col = None
                for col in ['onset', 'sample', 'latency']:
                    if col in events_df.columns:
                        onset_col = col
                        break
                
                desc_col = None
                for col in ['trial_type', 'event_id', 'value', 'event_type', 'description']:
                    if col in events_df.columns:
                        desc_col = col
                        break
                
                if onset_col is not None and desc_col is not None:
                    onsets = events_df[onset_col].values
                    # Convert to seconds if in samples
                    if onset_col == 'sample':
                        onsets = onsets / raw.info['sfreq']
                    
                    descriptions = events_df[desc_col].astype(str).values
                    durations = np.zeros(len(onsets))
                    if 'duration' in events_df.columns:
                        durations = events_df['duration'].fillna(0).values
                    
                    # Create annotations, passing literal tsv labels through (no remapping per HC-5)
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
            else:
                # Try to find stim channel for events
                stim_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=True, exclude=[])
                if len(stim_picks) > 0:
                    # Extract events from stim channel
                    events = mne.find_events(raw, stim_channel=None, shortest_event=1, verbose=False)
                    if len(events) > 0:
                        # Create annotations from events - use event IDs as strings
                        event_id_map = {1: 'T0', 2: 'T1', 3: 'T2'}
                        onsets = events[:, 0] / raw.info['sfreq']
                        descriptions = [event_id_map.get(ev_id, str(ev_id)) for ev_id in events[:, 2]]
                        durations = np.zeros(len(onsets))
                        
                        annotations = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=descriptions,
                        )
                        raw.set_annotations(annotations)
        
        return raw


KERNEL = PhysionetEegmmidbKernel()