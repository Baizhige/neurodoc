import json
import os
import re
import numpy as np
import pandas as pd
import mne


class PhysionetUcddbKernel:
    KERNEL_ID = "physionet_ucddb"
    KERNEL_NAME = "PhysioNet UCDDB - University College Dublin Sleep Apnea Database"
    KERNEL_DESCRIPTION = "Sleep EEG recordings with ECG, respiratory, and oxygen saturation signals for sleep apnea detection"
    KERNEL_CITATION = "10.13026/C26C7D"
    KERNEL_LICENSE = "ODbL"
    KERNEL_URL = "https://physionet.org/content/ucddb/1.0.0/"

    # No event IDs needed - this is a sleep/continuous recording dataset without trial events
    required_event_ids = []
    # Fields to extract from participants.tsv
    required_info_fields = ['age', 'sex', 'bmi', 'ahi', 'odi']
    # No native misc channels to preserve
    required_native_misc = []
    # No derived misc channels needed
    derived_misc_channels = []

    # Standard 10-20 channel mapping for this dataset
    # UCDDB uses standard EDF channel names that are already MNE-compatible
    CHANNEL_RENAME_MAP = {
        # EEG channels (standard 10-20)
        'Fpz': 'Fpz',
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F7': 'F7',
        'F3': 'F3',
        'Fz': 'Fz',
        'F4': 'F4',
        'F8': 'F8',
        'T3': 'T7',  # T3 -> T7 (10-10 naming)
        'T7': 'T7',
        'C3': 'C3',
        'Cz': 'Cz',
        'C4': 'C4',
        'T4': 'T8',  # T4 -> T8 (10-10 naming)
        'T8': 'T8',
        'T5': 'P7',  # T5 -> P7 (10-10 naming)
        'P7': 'P7',
        'P3': 'P3',
        'Pz': 'Pz',
        'P4': 'P4',
        'T6': 'P8',  # T6 -> P8 (10-10 naming)
        'P8': 'P8',
        'O1': 'O1',
        'O2': 'O2',
        'A1': 'A1',
        'A2': 'A2',
        # EOG channels
        'ROC': 'EOG1',  # Right outer canthus
        'LOC': 'EOG2',  # Left outer canthus
        # EMG channels
        'EMG1': 'EMG1',
        'EMG2': 'EMG2',
        'EMG': 'EMG',
        # ECG
        'ECG': 'ECG',
        # Respiratory channels
        'THOR': 'THOR',  # Thoracic effort
        'ABD': 'ABD',    # Abdominal effort
        # Airflow
        'AIRFLOW': 'AIRFLOW',
        # Oxygen saturation
        'SAO2': 'SpO2',  # Oxygen saturation
        # Position
        'POSITION': 'POSITION',
    }

    def __init__(self):
        pass

    def _find_dataset_root(self, filepath):
        """Find dataset root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part == 'ucddb' or part == '1.0.0':
                # Go up to include version if present, or stop at ucddb
                if part == '1.0.0':
                    return os.sep.join(parts[:i+1])
                else:
                    # Check if 1.0.0 exists below
                    candidate = os.sep.join(parts[:i+1])
                    if os.path.exists(os.path.join(candidate, '1.0.0')):
                        return os.path.join(candidate, '1.0.0')
                    return candidate
        # Fallback: search for ucddb in path
        for i, part in enumerate(parts):
            if 'ucddb' in part.lower():
                return os.sep.join(parts[:i+1])
        return os.path.dirname(filepath)

    def _find_participants_tsv(self, dataset_root):
        """Find participants.tsv file."""
        if dataset_root is None:
            return None
        # Check common locations
        for p_tsv in [
            os.path.join(dataset_root, 'participants.tsv'),
            os.path.join(os.path.dirname(dataset_root), 'participants.tsv'),
            os.path.join(dataset_root, '..', 'participants.tsv'),
        ]:
            p_tsv = os.path.normpath(p_tsv)
            if os.path.exists(p_tsv):
                return p_tsv
        return None

    def _extract_subject_id(self, filepath):
        """Extract subject ID from filename."""
        basename = os.path.basename(filepath)
        # Pattern: ucddbXXX_lifecard.edf or ucddbXXX.edf
        match = re.match(r'(ucddb\d+)', basename, re.IGNORECASE)
        if match:
            return match.group(1).lower()
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
                if col.lower() in ['participant_id', 'subject', 'subject_id', 'ucddb id']:
                    subj_col = col
                    break
            if subj_col is None:
                # Try first column
                subj_col = df.columns[0]

            # Match subject - try various formats
            subject_variants = [
                subject_id,
                subject_id.upper(),
                subject_id.lower(),
                subject_id.replace('ucddb', ''),
                'ucddb' + subject_id.replace('ucddb', ''),
            ]

            for variant in subject_variants:
                subj_rows = df[df[subj_col].astype(str).str.lower() == str(variant).lower()]
                if len(subj_rows) > 0:
                    break

            if len(subj_rows) == 0:
                # Try partial match
                for variant in subject_variants:
                    mask = df[subj_col].astype(str).str.contains(variant, case=False, na=False)
                    subj_rows = df[mask]
                    if len(subj_rows) > 0:
                        break

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

    def _standardize_sex(self, sex_str):
        """Standardize sex to lowercase male/female/unknown."""
        if sex_str is None or sex_str == "unknown":
            return "unknown"
        sex_lower = str(sex_str).lower().strip()
        if sex_lower in ['m', 'male', '1']:
            return "male"
        elif sex_lower in ['f', 'female', '2']:
            return "female"
        elif sex_lower in ['o', 'other', 'unknown', 'nan', '']:
            return "unknown"
        return "unknown"  # Default for unrecognized

    def _get_channel_type(self, ch_name):
        """Determine channel type based on name."""
        ch_upper = ch_name.upper()
        # EOG
        if any(x in ch_upper for x in ['EOG', 'ROC', 'LOC', 'EYE']):
            return 'eog'
        # EMG
        if 'EMG' in ch_upper:
            return 'emg'
        # ECG
        if 'ECG' in ch_upper or 'EKG' in ch_upper:
            return 'ecg'
        # Respiratory / other physiological
        if any(x in ch_upper for x in ['THOR', 'ABD', 'AIRFLOW', 'POSITION', 'SAO2', 'SPO2']):
            return 'misc'
        # Reference electrodes
        if ch_upper in ['A1', 'A2', 'M1', 'M2']:
            return 'misc'
        # Default to EEG
        return 'eeg'

    def _apply_channel_renames(self, raw):
        """Apply channel renaming to standard names."""
        rename_map = {}
        for ch_name in raw.ch_names:
            # Try exact match first
            if ch_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_name]
            else:
                # Try case-insensitive match
                for key, val in self.CHANNEL_RENAME_MAP.items():
                    if ch_name.upper() == key.upper():
                        rename_map[ch_name] = val
                        break
        if rename_map:
            raw.rename_channels(rename_map)
        return raw

    def _set_channel_types(self, raw):
        """Set appropriate channel types for all channels."""
        ch_types = {}
        for ch_name in raw.ch_names:
            ch_types[ch_name] = self._get_channel_type(ch_name)
        raw.set_channel_types(ch_types)
        return raw

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file."""
        base = eeg_file_path
        # Remove extension
        for ext in ['.edf', '.set', '.fif', '.eeg', '.vhdr', '.vmrk']:
            if base.endswith(ext):
                base = base[:-len(ext)]
                break
        
        # Check for events.tsv
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Check in same directory with matching prefix
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)
        
        for f in os.listdir(dir_name) if os.path.exists(dir_name) else []:
            if f.endswith('_events.tsv') and f.startswith(base_name):
                return os.path.join(dir_name, f)
        
        return None

    def _load_events_from_tsv(self, events_tsv, raw):
        """Load events from BIDS events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return raw
        
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            if len(df) == 0:
                return raw
            
            # Required columns
            if 'onset' not in df.columns:
                return raw
            
            # Build annotations
            onsets = []
            durations = []
            descriptions = []
            
            for _, row in df.iterrows():
                onset = row['onset']
                if pd.isna(onset):
                    continue
                
                duration = row.get('duration', 0)
                if pd.isna(duration):
                    duration = 0
                
                # Description from trial_type or value
                desc = None
                if 'trial_type' in row and not pd.isna(row['trial_type']):
                    desc = str(row['trial_type'])
                elif 'value' in row and not pd.isna(row['value']):
                    desc = str(row['value'])
                else:
                    desc = 'event'
                
                onsets.append(float(onset))
                durations.append(float(duration))
                descriptions.append(desc)
            
            if len(onsets) > 0:
                # Remove any existing annotations first
                raw.set_annotations(None)
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)
        except Exception:
            pass
        
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row['file_path'] if 'file_path' in row else ''
        
        # Find dataset root and participants.tsv
        dataset_root = self._find_dataset_root(filepath)
        participants_tsv = self._find_participants_tsv(dataset_root)
        
        # Extract subject ID
        subject_id = self._extract_subject_id(filepath)
        
        # Read participants info
        info = self._read_participants_info(participants_tsv, subject_id)
        
        # Ensure required fields exist with defaults
        age = info.get('age', 'unknown')
        sex = self._standardize_sex(info.get('sex', 'unknown'))
        bmi = info.get('bmi', 'unknown')
        ahi = info.get('ahi', 'unknown')
        odi = info.get('odi', 'unknown')
        
        # Build eegunity_description with all required fields
        eegunity_description = {
            'age': str(age) if age != 'unknown' else 'unknown',
            'sex': sex,
            'amplifier': 'Lifecard CF',  # inferred by LLM, needs human review
            'cap': 'standard 10-20',  # inferred by LLM, needs human review
            'handedness': 'unknown',  # not provided in dataset
            'bmi': str(bmi) if bmi != 'unknown' else 'unknown',
            'ahi': str(ahi) if ahi != 'unknown' else 'unknown',
            'odi': str(odi) if odi != 'unknown' else 'unknown',
        }
        
        # Store original description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Set description
        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_description
        })
        
        # Apply channel renaming BEFORE set_montage
        raw = self._apply_channel_renames(raw)
        
        # Set channel types
        raw = self._set_channel_types(raw)
        
        # Set montage for EEG channels
        try:
            # Try to set standard 10-20 montage
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only set for EEG channels that exist in montage
            eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
            eeg_ch_names = [raw.ch_names[i] for i in eeg_picks]
            montage_ch_names = set(montage.ch_names)
            valid_ch_names = [c for c in eeg_ch_names if c in montage_ch_names]
            if valid_ch_names:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        
        # Check for events.tsv and load if present
        # EDF files may not carry annotations, so we need to check for sidecar
        events_tsv = self._find_events_tsv(filepath)
        if events_tsv:
            raw = self._load_events_from_tsv(events_tsv, raw)
        
        # Ensure no misc channels are accidentally dropped
        # This dataset has physiological channels that should be preserved
        
        return raw


KERNEL = PhysionetUcddbKernel()