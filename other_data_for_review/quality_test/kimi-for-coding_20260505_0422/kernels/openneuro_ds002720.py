import json
import os
import numpy as np
import pandas as pd
import mne


class OpenNeuroDS002720Kernel:
    KERNEL_ID = "openneuro_ds002720"
    KERNEL_NAME = "OpenNeuro ds002720 - Alpha Modulation BCI"
    KERNEL_DESCRIPTION = "EEG kernel for two-class alpha modulation BCI with lower/raise alpha conditions"
    KERNEL_CITATION = "10.1038/s41597-020-0507-6"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds002720"

    required_event_ids = ['1', '2']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = [
        {'name': 'age_bin', 'source_field': 'age', 'derivation': 'Compute median of age across all subjects. For each subject, assign 0 if age <= median, 1 if age > median. Create constant misc channel with this binary value for all time points in that subject\'s recording.'}
    ]

    # Standard 10-20 channel names for this dataset
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F7': 'F7',
        'F3': 'F3',
        'Fz': 'Fz',
        'F4': 'F4',
        'F8': 'F8',
        'T7': 'T7',
        'C3': 'C3',
        'Cz': 'Cz',
        'C4': 'C4',
        'T8': 'T8',
        'P7': 'P7',
        'P3': 'P3',
        'Pz': 'Pz',
        'P4': 'P4',
        'P8': 'P8',
        'O1': 'O1',
        'O2': 'O2',
    }

    def __init__(self):
        self._participants_df = None
        self._bids_root = None
        self._age_median = None

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds002720'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        return None

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        return None

    def _load_participants_tsv(self, bids_root):
        """Load participants.tsv into cache."""
        if self._participants_df is not None:
            return self._participants_df
        
        if bids_root is None:
            return None
        
        p_tsv = os.path.join(bids_root, 'participants.tsv')
        if not os.path.exists(p_tsv):
            return None
        
        try:
            self._participants_df = pd.read_csv(p_tsv, sep='\t')
            return self._participants_df
        except Exception:
            return None

    def _compute_age_median(self, participants_df):
        """Compute median age across all subjects."""
        if self._age_median is not None:
            return self._age_median
        
        if participants_df is None or 'age' not in participants_df.columns:
            return None
        
        try:
            ages = pd.to_numeric(participants_df['age'], errors='coerce').dropna()
            if len(ages) == 0:
                return None
            self._age_median = ages.median()
            return self._age_median
        except Exception:
            return None

    def _read_participants_info(self, participants_df, subject_id):
        """Read subject info from participants.tsv."""
        if participants_df is None:
            return {}
        
        try:
            # Find subject column
            subj_col = None
            for col in participants_df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = participants_df.columns[0]

            # Match subject
            subj_rows = participants_df[participants_df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                # Try without 'sub-' prefix
                if subject_id.startswith('sub-'):
                    alt_id = subject_id[4:]
                else:
                    alt_id = 'sub-' + subject_id
                subj_rows = participants_df[participants_df[subj_col] == alt_id]

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

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # BIDS naming: sub-X_task-Y_eeg.edf -> sub-X_task-Y_events.tsv
        base = os.path.splitext(eeg_file_path)[0]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without the _eeg suffix
        base = base.replace('_eeg', '')
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        return None

    def _read_events_tsv(self, events_tsv):
        """Read events from events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            # Check required columns
            if 'onset' not in df.columns:
                return None
            
            # Determine event value column - prioritize trial_type as it contains the actual event IDs
            value_col = None
            for col in ['trial_type', 'value', 'event_id']:
                if col in df.columns:
                    value_col = col
                    break
            
            if value_col is None:
                return None
            
            # Keep all rows - do NOT filter to required_event_ids
            # The events.tsv contains the ground truth labels
            
            if len(df) == 0:
                return None
            
            return df[['onset', 'duration', value_col]].copy()
        except Exception:
            return None

    def _normalize_sex(self, sex_val):
        """Normalize sex value to lowercase standard."""
        if sex_val is None or str(sex_val).lower() in ['unknown', 'nan', 'none', '']:
            return "unknown"
        s = str(sex_val).lower().strip()
        if s in ['m', 'male']:
            return "male"
        elif s in ['f', 'female']:
            return "female"
        elif 'm' in s:
            return "male"
        elif 'f' in s:
            return "female"
        return "unknown"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle different possible column names
        filepath = None
        for col_name in ['file_path', 'filepath', 'path', 'filename']:
            if hasattr(row, 'index') and col_name in row.index:
                filepath = row[col_name]
                break
            elif hasattr(row, col_name):
                filepath = getattr(row, col_name)
                break
        
        # Fallback: try to get from raw
        if filepath is None and hasattr(raw, 'filenames') and raw.filenames:
            filepath = raw.filenames[0]
        
        if filepath is None:
            # Cannot proceed without filepath, but still apply basic processing
            filepath = ""

        # Find BIDS root
        bids_root = self._find_bids_root(filepath)
        
        # Load participants info
        participants_df = self._load_participants_tsv(bids_root)
        subject_id = self._get_subject_id_from_path(filepath)
        
        # Read participant info
        info = self._read_participants_info(participants_df, subject_id) if subject_id else {}
        
        # Ensure required fields exist
        for field in self.required_info_fields:
            if field not in info:
                info[field] = "unknown"
        
        # Normalize sex
        info['sex'] = self._normalize_sex(info.get('sex', 'unknown'))
        
        # Ensure age is string
        if 'age' in info:
            info['age'] = str(info['age'])

        # Channel renaming
        raw.rename_channels(self.CHANNEL_RENAME_MAP)
        
        # Set montage (standard 10-20)
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass

        # Set channel types for any non-EEG channels if needed
        # This dataset appears to be pure EEG, so no special handling needed

        # Handle events from events.tsv for EDF files (which don't carry their own triggers)
        events_tsv_path = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv_path)
        
        if events_df is not None:
            # Create annotations from events.tsv
            onsets = events_df['onset'].values.astype(float)
            durations = events_df['duration'].values.astype(float) if 'duration' in events_df.columns else np.zeros(len(onsets))
            # Use the value column (trial_type or value)
            value_col = [c for c in events_df.columns if c != 'onset' and c != 'duration'][0]
            descriptions = events_df[value_col].astype(str).values
            
            # Create annotations - EDF files have no native annotations, so we must set them
            # First, clear any existing annotations to avoid conflicts
            annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(annot)

        # Create derived misc channels from derived_misc_channels specification
        # Only create if source data is actually available
        misc_raws_to_add = []
        
        for derived_spec in self.derived_misc_channels:
            name = derived_spec['name']
            source_field = derived_spec['source_field']
            
            # Parse source_field format
            if source_field.startswith('events.tsv:'):
                # events.tsv source - would need trial-locked step function
                # Not applicable for age_bin, but handle generically
                col_name = source_field.split(':', 1)[1]
                # For this dataset, no events.tsv-derived misc channels are specified
                # Skip if not available
                continue
            else:
                # participants.tsv source - constant broadcast
                col_name = source_field
                
                # Check if source column exists and subject info is available
                if participants_df is None:
                    continue
                if col_name not in participants_df.columns:
                    continue
                if subject_id is None:
                    continue
                
                # Get the value for this subject
                try:
                    # Find subject column
                    subj_col = None
                    for c in participants_df.columns:
                        if c.lower() in ['participant_id', 'subject', 'subject_id']:
                            subj_col = c
                            break
                    if subj_col is None:
                        subj_col = participants_df.columns[0]
                    
                    # Match subject
                    subj_rows = participants_df[participants_df[subj_col] == subject_id]
                    if len(subj_rows) == 0:
                        if subject_id.startswith('sub-'):
                            alt_id = subject_id[4:]
                        else:
                            alt_id = 'sub-' + subject_id
                        subj_rows = participants_df[participants_df[subj_col] == alt_id]
                    
                    if len(subj_rows) == 0:
                        continue
                    
                    source_value = subj_rows.iloc[0][col_name]
                    if pd.isna(source_value):
                        continue
                    
                    # Apply derivation for age_bin
                    if name == 'age_bin':
                        age_median = self._compute_age_median(participants_df)
                        if age_median is None:
                            continue
                        try:
                            age = float(source_value)
                            channel_value = 1.0 if age > age_median else 0.0
                        except (ValueError, TypeError):
                            continue
                    else:
                        # Generic numeric conversion for other channels
                        try:
                            channel_value = float(source_value)
                        except (ValueError, TypeError):
                            continue
                    
                    # Create constant misc channel
                    misc_data = np.full((1, len(raw.times)), channel_value)
                    misc_info = mne.create_info([name], raw.info['sfreq'], ch_types=['misc'])
                    misc_raw = mne.io.RawArray(misc_data, misc_info)
                    misc_raws_to_add.append(misc_raw)
                    
                except Exception:
                    # Skip on any error - don't fabricate data
                    continue
        
        # Add all derived misc channels
        if misc_raws_to_add:
            raw.add_channels(misc_raws_to_add, force_update_info=True)

        # Build description
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)
        elif original_desc is None:
            original_desc = ""

        eegunity_desc = {
            "age": info.get('age', 'unknown'),
            "sex": info.get('sex', 'unknown'),
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })

        return raw


KERNEL = OpenNeuroDS002720Kernel()