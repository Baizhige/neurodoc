import json
import os
import numpy as np
import pandas as pd
import mne


class TuhEegEventsKernel:
    KERNEL_ID = "tuh_eeg_events"
    KERNEL_NAME = "TUH EEG Events Corpus"
    KERNEL_DESCRIPTION = "Temple University Hospital EEG Events Corpus v2.0.1 - annotated EEG with seizure and other event markings"
    KERNEL_CITATION = "10.1109/globalsip.2013.6736803"
    KERNEL_LICENSE = "TUH EEG License"
    KERNEL_URL = "https://isip.piconepress.com/projects/tuh_eeg/"

    required_event_ids = []
    required_info_fields = ['age', 'sex', 'amplifier', 'cap', 'handedness']
    required_native_misc = []
    derived_misc_channels = []

    # TUH standard 10-20 channel naming with common variations
    CHANNEL_RENAME_MAP = {
        'EEG FP1-REF': 'Fp1',
        'EEG FP2-REF': 'Fp2',
        'EEG F3-REF': 'F3',
        'EEG F4-REF': 'F4',
        'EEG C3-REF': 'C3',
        'EEG C4-REF': 'C4',
        'EEG P3-REF': 'P3',
        'EEG P4-REF': 'P4',
        'EEG O1-REF': 'O1',
        'EEG O2-REF': 'O2',
        'EEG F7-REF': 'F7',
        'EEG F8-REF': 'F8',
        'EEG T3-REF': 'T7',
        'EEG T4-REF': 'T8',
        'EEG T5-REF': 'P7',
        'EEG T6-REF': 'P8',
        'EEG A1-REF': 'A1',
        'EEG A2-REF': 'A2',
        'EEG FZ-REF': 'Fz',
        'EEG CZ-REF': 'Cz',
        'EEG PZ-REF': 'Pz',
        'EEG FP1-LE': 'Fp1',
        'EEG FP2-LE': 'Fp2',
        'EEG F3-LE': 'F3',
        'EEG F4-LE': 'F4',
        'EEG C3-LE': 'C3',
        'EEG C4-LE': 'C4',
        'EEG P3-LE': 'P3',
        'EEG P4-LE': 'P4',
        'EEG O1-LE': 'O1',
        'EEG O2-LE': 'O2',
        'EEG F7-LE': 'F7',
        'EEG F8-LE': 'F8',
        'EEG T3-LE': 'T7',
        'EEG T4-LE': 'T8',
        'EEG T5-LE': 'P7',
        'EEG T6-LE': 'P8',
        'EEG A1-LE': 'A1',
        'EEG A2-LE': 'A2',
        'EEG FZ-LE': 'Fz',
        'EEG CZ-LE': 'Cz',
        'EEG PZ-LE': 'Pz',
        'EEG FP1': 'Fp1',
        'EEG FP2': 'Fp2',
        'EEG F3': 'F3',
        'EEG F4': 'F4',
        'EEG C3': 'C3',
        'EEG C4': 'C4',
        'EEG P3': 'P3',
        'EEG P4': 'P4',
        'EEG O1': 'O1',
        'EEG O2': 'O2',
        'EEG F7': 'F7',
        'EEG F8': 'F8',
        'EEG T3': 'T7',
        'EEG T4': 'T8',
        'EEG T5': 'P7',
        'EEG T6': 'P8',
        'EEG A1': 'A1',
        'EEG A2': 'A2',
        'EEG FZ': 'Fz',
        'EEG CZ': 'Cz',
        'EEG PZ': 'Pz',
        'FP1': 'Fp1',
        'FP2': 'Fp2',
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
        'T3': 'T7',
        'T4': 'T8',
        'T5': 'P7',
        'T6': 'P8',
        'A1': 'A1',
        'A2': 'A2',
        'FZ': 'Fz',
        'CZ': 'Cz',
        'PZ': 'Pz',
        'FP1-REF': 'Fp1',
        'FP2-REF': 'Fp2',
        'F3-REF': 'F3',
        'F4-REF': 'F4',
        'C3-REF': 'C3',
        'C4-REF': 'C4',
        'P3-REF': 'P3',
        'P4-REF': 'P4',
        'O1-REF': 'O1',
        'O2-REF': 'O2',
        'F7-REF': 'F7',
        'F8-REF': 'F8',
        'T3-REF': 'T7',
        'T4-REF': 'T8',
        'T5-REF': 'P7',
        'T6-REF': 'P8',
        'A1-REF': 'A1',
        'A2-REF': 'A2',
        'FZ-REF': 'Fz',
        'CZ-REF': 'Cz',
        'PZ-REF': 'Pz',
        'FP1-LE': 'Fp1',
        'FP2-LE': 'Fp2',
        'F3-LE': 'F3',
        'F4-LE': 'F4',
        'C3-LE': 'C3',
        'C4-LE': 'C4',
        'P3-LE': 'P3',
        'P4-LE': 'P4',
        'O1-LE': 'O1',
        'O2-LE': 'O2',
        'F7-LE': 'F7',
        'F8-LE': 'F8',
        'T3-LE': 'T7',
        'T4-LE': 'T8',
        'T5-LE': 'P7',
        'T6-LE': 'P8',
        'A1-LE': 'A1',
        'A2-LE': 'A2',
        'FZ-LE': 'Fz',
        'CZ-LE': 'Cz',
        'PZ-LE': 'Pz',
        # Additional common TUH channels
        'EEG P3-REF2': 'P3',
        'EEG P4-REF2': 'P4',
        'EEG C3-REF2': 'C3',
        'EEG C4-REF2': 'C4',
        'EEG F3-REF2': 'F3',
        'EEG F4-REF2': 'F4',
        'EEG O1-REF2': 'O1',
        'EEG O2-REF2': 'O2',
        'EEG T1-REF': 'T7',  # sometimes T1 is used for T7
        'EEG T2-REF': 'T8',  # sometimes T2 is used for T8
        'EEG T1-LE': 'T7',
        'EEG T2-LE': 'T8',
        'T1': 'T7',
        'T2': 'T8',
        'T1-REF': 'T7',
        'T2-REF': 'T8',
        'T1-LE': 'T7',
        'T2-LE': 'T8',
        # Sphenoidal channels often present in TUH
        'EEG SP1-REF': 'SP1',
        'EEG SP2-REF': 'SP2',
        'EEG SP1-LE': 'SP1',
        'EEG SP2-LE': 'SP2',
        'EEG SP1': 'SP1',
        'EEG SP2': 'SP2',
        'SP1-REF': 'SP1',
        'SP2-REF': 'SP2',
        'SP1-LE': 'SP1',
        'SP2-LE': 'SP2',
        'SP1': 'SP1',
        'SP2': 'SP2',
        # EKG/ECG
        'EEG EKG-REF': 'EKG',
        'EEG ECG-REF': 'ECG',
        'EKG-REF': 'EKG',
        'ECG-REF': 'ECG',
        'EKG-LE': 'EKG',
        'ECG-LE': 'EKG',
        'EKG': 'EKG',
        'ECG': 'ECG',
        # EMG
        'EMG-REF': 'EMG',
        'EMG-LE': 'EMG',
        'EMG': 'EMG',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # Look for version directory pattern (v2.0.1 etc.)
        for i, part in enumerate(parts):
            if part.startswith('v') and '.' in part:
                # Check if next parts contain edf/train or similar
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'edf' directory
        for i, part in enumerate(parts):
            if part == 'edf':
                return os.sep.join(parts[:i])
        # Fallback: go up until we find participants.tsv
        current = os.path.dirname(filepath)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        # Check multiple possible locations
        possible_paths = [
            os.path.join(bids_root, 'participants.tsv'),
            os.path.join(os.path.dirname(bids_root), 'participants.tsv'),
            os.path.join(os.path.dirname(os.path.dirname(bids_root)), 'participants.tsv'),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p
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

            # Match subject - TUH uses short IDs like 'aaaaaecc'
            clean_id = subject_id.replace('sub-', '')
            
            # Try exact match first
            subj_rows = df[df[subj_col].astype(str) == clean_id]
            if len(subj_rows) == 0:
                subj_rows = df[df[subj_col].astype(str) == subject_id]
            if len(subj_rows) == 0:
                # Try partial match
                subj_rows = df[df[subj_col].astype(str).str.contains(clean_id, na=False)]
            
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
        # TUH structure: .../train/aaaaaecc/aaaaaecc_00000002.edf
        # Subject ID is the directory containing the .edf file
        dirname = os.path.dirname(filepath)
        subject_dir = os.path.basename(dirname)
        if subject_dir and len(subject_dir) >= 4:
            return subject_dir
        # Fallback: look for pattern in filename
        basename = os.path.basename(filepath)
        # Remove extension and session suffix
        name_part = basename.replace('.edf', '').replace('.set', '').replace('.fif', '')
        # Take first 8 chars if looks like TUH ID
        if len(name_part) >= 8:
            return name_part[:8]
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find events.tsv file corresponding to EEG file."""
        # TUH events are typically in .rec files or .tse files, not BIDS events.tsv
        # But check for BIDS-style events.tsv
        base = eeg_file_path.replace('.edf', '').replace('.set', '').replace('.fif', '')
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Check in same directory
        dirname = os.path.dirname(eeg_file_path)
        basename = os.path.basename(eeg_file_path).replace('.edf', '').replace('.set', '').replace('.fif', '')
        events_tsv = os.path.join(dirname, basename + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Check for .rec file (TUH event file)
        rec_file = base + '.rec'
        if os.path.exists(rec_file):
            return rec_file
        
        rec_file2 = os.path.join(dirname, basename + '.rec')
        if os.path.exists(rec_file2):
            return rec_file2
        
        # Check for .tse file (TUH seizure annotation)
        tse_file = base + '.tse'
        if os.path.exists(tse_file):
            return tse_file
            
        tse_file2 = os.path.join(dirname, basename + '.tse')
        if os.path.exists(tse_file2):
            return tse_file2
        
        # Check for .tse_bi file (binary annotation)
        tse_bi_file = base + '.tse_bi'
        if os.path.exists(tse_bi_file):
            return tse_bi_file
            
        tse_bi_file2 = os.path.join(dirname, basename + '.tse_bi')
        if os.path.exists(tse_bi_file2):
            return tse_bi_file2
        
        return None

    def _read_tuh_events(self, events_file):
        """Read events from TUH .rec or .tse file."""
        events = []
        try:
            with open(events_file, 'r') as f:
                lines = f.readlines()
            
            # .rec file format: space-separated with header
            # .tse file format: start_time end_time label probability
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('version'):
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        onset = float(parts[0])
                        duration = float(parts[1]) - onset
                        if duration < 0:
                            duration = 0
                        description = parts[2]
                        events.append({
                            'onset': onset,
                            'duration': duration,
                            'description': description
                        })
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return events

    def _read_events_tsv(self, events_tsv):
        """Read events from BIDS-style events.tsv."""
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            events = []
            for _, row in df.iterrows():
                onset = float(row.get('onset', 0))
                duration = float(row.get('duration', 0))
                # Use trial_type if available, else description, else value
                description = str(row.get('trial_type', row.get('description', row.get('value', 'unknown'))))
                if pd.isna(description) or description == 'nan':
                    description = 'unknown'
                events.append({
                    'onset': onset,
                    'duration': duration,
                    'description': description
                })
            return events
        except Exception:
            return []

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        if not filepath and hasattr(udataset, 'current_file_path'):
            filepath = udataset.current_file_path
        
        # Extract subject ID
        subject_id = self._get_subject_id_from_path(filepath)
        
        # Find BIDS root and participants.tsv
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        
        # Read participant info
        participant_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Ensure required fields exist
        for field in self.required_info_fields:
            if field not in participant_info:
                participant_info[field] = "unknown"  # inferred by LLM, needs human review
        
        # Get original description
        original_desc = raw.info.get('description', '') if raw.info.get('description') else ''
        
        # Build eegunity_description with all required fields as strings
        eegunity_description = {
            "age": str(participant_info.get('age', 'unknown')),
            "sex": str(participant_info.get('sex', 'unknown')).lower(),
            "amplifier": str(participant_info.get('amplifier', 'unknown')),
            "cap": str(participant_info.get('cap', 'unknown')),
            "handedness": str(participant_info.get('handedness', 'unknown')),
        }
        
        # Add any extra fields from participants.tsv
        for key, val in participant_info.items():
            if key not in eegunity_description:
                eegunity_description[key] = str(val)
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description
        })
        
        # Channel renaming
        rename_map = {}
        for ch_name in raw.ch_names:
            upper_name = ch_name.upper()
            if upper_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[upper_name]
            elif ch_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_name]
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types - identify misc channels
        ch_types = {}
        for ch_name in raw.ch_names:
            upper_name = ch_name.upper()
            if any(x in upper_name for x in ['SP1', 'SP2', 'SPH', 'SPEN']):
                ch_types[ch_name] = 'misc'
            elif any(x in upper_name for x in ['A1', 'A2']) and 'REF' not in upper_name and 'LE' not in upper_name:
                # A1, A2 are often reference electrodes in TUH, treat as misc
                ch_types[ch_name] = 'misc'
            elif any(x in upper_name for x in ['EKG', 'ECG']):
                ch_types[ch_name] = 'ecg'
            elif 'EMG' in upper_name:
                ch_types[ch_name] = 'emg'
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Get EEG channels that are in the montage
            eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
            eeg_ch_names = [raw.ch_names[i] for i in eeg_picks]
            montage_ch_names = set(montage.ch_names)
            valid_ch_names = [ch for ch in eeg_ch_names if ch in montage_ch_names]
            if valid_ch_names:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        
        # Handle events from TUH annotation files
        events_file = self._find_events_tsv(filepath)
        if events_file:
            if events_file.endswith('.rec') or events_file.endswith('.tse') or events_file.endswith('.tse_bi'):
                events = self._read_tuh_events(events_file)
            else:
                events = self._read_events_tsv(events_file)
            
            if events:
                # Create annotations from events
                onsets = [e['onset'] for e in events]
                durations = [e['duration'] for e in events]
                descriptions = [e['description'] for e in events]
                
                # Remove any existing annotations first
                raw.set_annotations(None)
                
                # Create new annotations
                annot = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions
                )
                raw.set_annotations(annot)
        
        # Ensure required native misc channels exist
        for misc_name in self.required_native_misc:
            if misc_name in raw.ch_names:
                current_type = raw.get_channel_types(picks=[misc_name])[0] if misc_name in raw.ch_names else None
                if current_type != 'misc':
                    raw.set_channel_types({misc_name: 'misc'})
        
        # Create derived misc channels if needed
        for derived_name in self.derived_misc_channels:
            if derived_name not in raw.ch_names:
                # Create constant channel with zeros
                data = np.zeros((1, len(raw.times)))
                info = mne.create_info([derived_name], raw.info['sfreq'], ['misc'])
                misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
                raw.add_channels([misc_raw], force_update_info=True)
        
        return raw


KERNEL = TuhEegEventsKernel()