import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class OpenNeuroDS005185Kernel:
    KERNEL_ID = "openneuro_ds005185"
    KERNEL_NAME = "OpenNeuro ds005185 - Ear-EEG Sleep Staging (EESM19)"
    KERNEL_DESCRIPTION = "EEG kernel for ear-EEG sleep staging with 5-class AASM scoring (Wake, N1, N2, N3, REM) from EESM19 dataset"
    KERNEL_CITATION = "10.1038/s41598-019-53115-3"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds005185"

    # BIDS mapping
    required_event_ids = ['Got_up', 'Lights_Out', 'Went_to_Bed', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = ['written_time']

    # Channel renaming map for ear-EEG channels (standard 10-20 approximations for ear placements)
    CHANNEL_RENAME_MAP = {
        'E1': 'E1',
        'E2': 'E2',
        'E3': 'E3',
        'E4': 'E4',
        'E5': 'E5',
        'E6': 'E6',
        'E7': 'E7',
        'E8': 'E8',
        'E9': 'E9',
        'E10': 'E10',
        'E11': 'E11',
        'E12': 'E12',
        'E13': 'E13',
        'E14': 'E14',
        'E15': 'E15',
        'E16': 'E16',
        'E17': 'E17',
        'E18': 'E18',
        'E19': 'E19',
        'E20': 'E20',
        'E21': 'E21',
        'E22': 'E22',
        'E23': 'E23',
        'E24': 'E24',
        'E25': 'E25',
        'E26': 'E26',
        'E27': 'E27',
        'E28': 'E28',
        'E29': 'E29',
        'E30': 'E30',
        'A1': 'A1',
        'A2': 'A2',
        'M1': 'M1',
        'M2': 'M2',
        'Ref': 'Ref',
        'Cz': 'Cz',
        'Fz': 'Fz',
        'Pz': 'Pz',
        'Oz': 'Oz',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds005185'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
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
        # For BIDS, events.tsv is in the same directory or parent
        base = eeg_file_path.replace('.set', '').replace('.edf', '').replace('.eeg', '').replace('.fif', '').replace('.vhdr', '').replace('.vmrk', '').replace('.dat', '')
        
        # Try same directory
        dir_path = os.path.dirname(eeg_file_path)
        
        # Look for events.tsv in same directory with matching base name
        base_name = os.path.basename(base)
        events_tsv = os.path.join(dir_path, base_name + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
            
        # Try without acq- etc modifiers
        for fname in os.listdir(dir_path) if os.path.exists(dir_path) else []:
            if fname.endswith('_events.tsv'):
                return os.path.join(dir_path, fname)
        
        return None

    def _find_diary_events_tsv(self, eeg_file_path):
        """Find diary events.tsv for writtenTime extraction."""
        # Diary events are task-sleep with acq-diary
        dir_path = os.path.dirname(eeg_file_path)
        
        # Extract subject and session from path
        parts = os.path.normpath(eeg_file_path).split(os.sep)
        subj = None
        ses = None
        for part in parts:
            if part.startswith('sub-'):
                subj = part
            if part.startswith('ses-'):
                ses = part
        
        if subj and ses:
            # Look for diary events in the same session directory
            diary_name = f"{subj}_{ses}_task-sleep_acq-diary_events.tsv"
            diary_path = os.path.join(dir_path, diary_name)
            if os.path.exists(diary_path):
                return diary_path
            
            # Try without session
            diary_name = f"{subj}_task-sleep_acq-diary_events.tsv"
            diary_path = os.path.join(dir_path, diary_name)
            if os.path.exists(diary_path):
                return diary_path
        
        # Fallback: search directory for diary events
        for fname in os.listdir(dir_path) if os.path.exists(dir_path) else []:
            if 'diary' in fname and fname.endswith('_events.tsv'):
                return os.path.join(dir_path, fname)
        
        return None

    def _parse_written_time(self, time_str):
        """Parse written time string like '23.05' to minutes since midnight."""
        if pd.isna(time_str) or time_str == '':
            return 0.0
        try:
            time_str = str(time_str).strip()
            # Handle formats like "23.05", "23:05", "2305"
            if ':' in time_str:
                parts = time_str.split(':')
                hours = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
            elif '.' in time_str:
                parts = time_str.split('.')
                hours = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
            else:
                # Assume HHMM format
                if len(time_str) >= 3:
                    hours = float(time_str[:-2])
                    minutes = float(time_str[-2:])
                else:
                    hours = float(time_str)
                    minutes = 0
            return hours * 60 + minutes
        except (ValueError, IndexError):
            return 0.0

    def _create_written_time_misc(self, raw, events_tsv_path):
        """Create written_time misc channel from diary events.tsv."""
        if events_tsv_path is None or not os.path.exists(events_tsv_path):
            # Create with zeros if no diary found
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['written_time'], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            # Ensure preload
            if not raw.preload:
                raw.load_data()
            raw.add_channels([misc_raw], force_update_info=True)
            return raw

        try:
            df = pd.read_csv(events_tsv_path, sep='\t')
            if 'writtenTime' not in df.columns or len(df) == 0:
                # Create with zeros
                data = np.zeros((1, len(raw.times)))
                info = mne.create_info(['written_time'], raw.info['sfreq'], ['misc'])
                misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
                if not raw.preload:
                    raw.load_data()
                raw.add_channels([misc_raw], force_update_info=True)
                return raw

            # Parse first writtenTime value as constant broadcast
            first_time = df['writtenTime'].iloc[0]
            minutes = self._parse_written_time(first_time)
            
            # Create constant channel
            data = np.full((1, len(raw.times)), minutes)
            info = mne.create_info(['written_time'], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            if not raw.preload:
                raw.load_data()
            raw.add_channels([misc_raw], force_update_info=True)
            return raw
            
        except Exception:
            # Create with zeros on failure
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['written_time'], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            if not raw.preload:
                raw.load_data()
            raw.add_channels([misc_raw], force_update_info=True)
            return raw

    def _add_annotations_from_events_tsv(self, raw, events_tsv_path):
        """Add annotations from events.tsv to raw if raw lacks event information."""
        if events_tsv_path is None or not os.path.exists(events_tsv_path):
            return raw

        try:
            df = pd.read_csv(events_tsv_path, sep='\t')
            if len(df) == 0:
                return raw

            # Check if raw already has meaningful annotations
            existing_annotations = len(raw.annotations) if hasattr(raw, 'annotations') else 0
            
            # For EEGLAB .set files, events might be in the file already
            # We need to ensure all required event IDs are present
            required_present = False
            if existing_annotations > 0:
                existing_desc = set(raw.annotations.description)
                required_ids = set(self.required_event_ids)
                if len(required_ids.intersection(existing_desc)) > 0:
                    required_present = True
            
            # If we have good annotations already, still check if we need to supplement
            if required_present and existing_annotations >= len(df):
                return raw

            # Build annotations from events.tsv
            onsets = []
            durations = []
            descriptions = []
            
            for _, row in df.iterrows():
                onset = row.get('onset', 0)
                duration = row.get('duration', 0)
                if pd.isna(duration) or duration == 0:
                    duration = 30.0  # Default 30s for sleep epochs
                
                # Use trial_type if available, else value, else event_type
                desc = None
                for col in ['trial_type', 'value', 'event_type', 'stim_type']:
                    if col in row and pd.notna(row[col]):
                        desc = str(row[col])
                        break
                
                if desc is None:
                    continue
                    
                onsets.append(float(onset))
                durations.append(float(duration))
                descriptions.append(desc)

            if len(onsets) > 0:
                # Create new annotations, merging with existing if any
                new_annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                
                if existing_annotations > 0:
                    # Combine annotations
                    raw.set_annotations(raw.annotations + new_annot)
                else:
                    raw.set_annotations(new_annot)
                    
        except Exception:
            pass
        
        return raw

    def _standardize_sex(self, sex_val):
        """Standardize sex to lowercase male/female/unknown."""
        if pd.isna(sex_val) or sex_val == '':
            return "unknown"
        sex_str = str(sex_val).strip().lower()
        if sex_str in ['m', 'male', '1']:
            return "male"
        elif sex_str in ['f', 'female', '2']:
            return "female"
        elif sex_str in ['o', 'other', 'unknown', '']:
            return "unknown"
        else:
            # Try to infer
            if 'm' in sex_str:
                return "male"
            elif 'f' in sex_str:
                return "female"
            return "unknown"  # inferred by LLM, needs human review

    def _standardize_age(self, age_val):
        """Standardize age to string."""
        if pd.isna(age_val) or age_val == '':
            return "unknown"
        try:
            # Handle ranges like "20-30"
            age_str = str(age_val).strip()
            if '-' in age_str:
                parts = age_str.split('-')
                return str(int(float(parts[0])))  # Take lower bound
            return str(int(float(age_val)))
        except (ValueError, TypeError):
            return "unknown"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        if hasattr(row, 'file_path'):
            filepath = row.file_path
        elif isinstance(row, dict):
            filepath = row.get('file_path', '')
        else:
            filepath = str(row)
        
        # Extract subject ID
        subject_id = self._get_subject_id_from_path(filepath)
        if subject_id is None:
            subject_id = "unknown"
        
        # Find BIDS root
        bids_root = self._find_bids_root(filepath)
        
        # Read participants info
        participants_tsv = self._find_participants_tsv(bids_root)
        info = self._read_participants_info(participants_tsv, subject_id)
        
        # Standardize age and sex
        age = self._standardize_age(info.get('age', 'unknown'))
        sex = self._standardize_sex(info.get('sex', 'unknown'))
        
        # Prepare description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Build eegunity_description with required fields
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review - ear-EEG device
            "handedness": "unknown",  # inferred by LLM, needs human review
        }
        
        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in info:
                eegunity_desc[field] = str(info[field]) if pd.notna(info[field]) else "unknown"
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Channel renaming BEFORE set_montage
        # Apply channel rename map
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in self.CHANNEL_RENAME_MAP:
                new_name = self.CHANNEL_RENAME_MAP[old_name]
                if new_name != old_name:
                    rename_map[old_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known misc channels if any
        # For this dataset, all channels are EEG except those we explicitly set
        
        # Set montage if possible (ear-EEG may not have standard montage)
        try:
            # Try to set a standard montage, fallback to None for ear-EEG
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        # Ensure preload before adding channels
        if not raw.preload:
            raw.load_data()
        
        # Find and add annotations from events.tsv for sleep scoring events
        # Look for task-sleep events (scoring)
        events_tsv = self._find_events_tsv(filepath)
        if events_tsv:
            raw = self._add_annotations_from_events_tsv(raw, events_tsv)
        
        # Also look for diary events for written_time
        diary_events_tsv = self._find_diary_events_tsv(filepath)
        
        # Create written_time derived misc channel
        raw = self._create_written_time_misc(raw, diary_events_tsv)
        
        # Ensure written_time is misc type
        if 'written_time' in raw.ch_names:
            raw.set_channel_types({'written_time': 'misc'})
        
        return raw


KERNEL = OpenNeuroDS005185Kernel()