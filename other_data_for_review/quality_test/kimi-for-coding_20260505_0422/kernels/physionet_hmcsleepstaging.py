import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class PhysionetHmcSleepStagingKernel:
    KERNEL_ID = "physionet_hmcsleepstaging"
    KERNEL_NAME = "PhysioNet HMC Sleep Staging"
    KERNEL_DESCRIPTION = "EEG kernel for HMC sleep staging dataset with standard AASM 5-class sleep staging"
    KERNEL_CITATION = "10.1109/embc58623.2025.11252818"
    KERNEL_LICENSE = "ODbL"
    KERNEL_URL = "https://physionet.org/content/hmc-sleep-staging/1.1/"

    required_event_ids = ['Sleep stage N1', 'Sleep stage N2', 'Sleep stage N3', 'Sleep stage R', 'Sleep stage W']
    required_info_fields = ['age', 'sex']
    required_native_misc = ['ECG', 'EMG chin', 'EOG E1-M2', 'EOG E2-M2']
    derived_misc_channels = []

    # Standard 10-20 channel mapping for HMC dataset
    CHANNEL_RENAME_MAP = {
        'F3': 'F3',
        'F4': 'F4',
        'C3': 'C3',
        'C4': 'C4',
        'O1': 'O1',
        'O2': 'O2',
        'M1': 'M1',
        'M2': 'M2',
        'E1': 'E1',
        'E2': 'E2',
        'ECG': 'ECG',
        'EMG1': 'EMG1',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'hmc' in part.lower() or 'sleep' in part.lower():
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
            # Find subject row
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
        # Fallback: extract from filename like SN053.edf
        basename = os.path.basename(filepath)
        name = os.path.splitext(basename)[0]
        return name

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG recording."""
        base = os.path.splitext(eeg_file_path)[0]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try alternative naming
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)
        alt_events = os.path.join(dir_name, base_name + '_events.tsv')
        if os.path.exists(alt_events):
            return alt_events
        
        # Look for any events.tsv in same directory
        try:
            for f in os.listdir(dir_name):
                if f.endswith('_events.tsv'):
                    return os.path.join(dir_name, f)
        except (OSError, FileNotFoundError):
            pass
        
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

    def _normalize_sex(self, sex_val):
        """Normalize sex value to lowercase standard."""
        if sex_val is None or str(sex_val).lower() in ['nan', 'none', 'unknown', '']:
            return "unknown"
        s = str(sex_val).lower().strip()
        if s in ['m', 'male']:
            return "male"
        elif s in ['f', 'female']:
            return "female"
        elif s in ['o', 'other']:
            return "unknown"
        return "unknown"

    def _normalize_age(self, age_val):
        """Normalize age to string."""
        if age_val is None or str(age_val).lower() in ['nan', 'none', 'unknown', '']:
            return "unknown"
        try:
            # Handle "22Y" format
            age_str = str(age_val).strip().upper().replace('Y', '')
            float(age_str)  # validate numeric
            return age_str
        except (ValueError, TypeError):
            return "unknown"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get filepath from row, handling different possible column names
        filepath = None
        for key in ['file_path', 'filepath', 'path', 'filename']:
            if hasattr(row, 'get') and key in row:
                filepath = row[key]
                break
            elif hasattr(row, key):
                filepath = getattr(row, key)
                break
        
        # Fallback: try to get from index or any attribute
        if filepath is None:
            if hasattr(row, 'to_dict'):
                row_dict = row.to_dict()
                for key in row_dict:
                    if 'path' in key.lower() or 'file' in key.lower():
                        filepath = row_dict[key]
                        break
            if filepath is None:
                # Last resort: use raw.filenames if available
                if hasattr(raw, 'filenames') and raw.filenames:
                    filepath = raw.filenames[0]
                else:
                    filepath = ""
        
        subject_id = self._get_subject_id_from_path(filepath)
        
        # Find BIDS root and participants info
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        participant_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Build description
        original_desc = raw.info.get("description", "")
        
        # Extract age and sex with normalization
        age = self._normalize_age(participant_info.get('age', 'unknown'))
        sex = self._normalize_sex(participant_info.get('sex', 'unknown'))
        
        # Build eegunity_description with required fields
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }
        
        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in ['age', 'sex']:
                val = participant_info.get(field, 'unknown')
                eegunity_desc[field] = str(val) if val is not None else "unknown"
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Channel renaming BEFORE set_montage
        rename_map = {}
        for old_name, new_name in self.CHANNEL_RENAME_MAP.items():
            if old_name in raw.ch_names and old_name != new_name:
                rename_map[old_name] = new_name
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage for EEG channels
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        # Ensure required native misc channels are typed as 'misc'
        # Map the HMC channel names to expected misc channel names
        misc_channels_to_check = {
            'ECG': 'ECG',
            'EMG chin': 'EMG1',
            'EOG E1-M2': 'E1',
            'EOG E2-M2': 'E2',
        }
        
        # Set channel types for misc channels
        for expected_name, raw_name in misc_channels_to_check.items():
            if raw_name in raw.ch_names:
                raw.set_channel_types({raw_name: 'misc'})
        
        # Handle events/annotations from events.tsv if available
        # EDF files in this dataset have no embedded annotations, so events MUST come from events.tsv
        events_tsv = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv)
        
        if events_df is not None and len(events_df) > 0:
            # Determine which columns to use for annotations
            # BIDS events.tsv typically has: onset, duration, trial_type (or value)
            onset_col = 'onset' if 'onset' in events_df.columns else None
            duration_col = 'duration' if 'duration' in events_df.columns else None
            desc_col = None
            
            # Prefer 'trial_type' for descriptions (standard BIDS), fall back to 'value'
            if 'trial_type' in events_df.columns:
                desc_col = 'trial_type'
            elif 'value' in events_df.columns:
                desc_col = 'value'
            
            if onset_col is not None and desc_col is not None:
                # Get onset values (in seconds, per BIDS spec)
                onsets = events_df[onset_col].values
                
                # Get durations, default to 0 if not present
                if duration_col is not None:
                    durations = events_df[duration_col].values
                    # Handle NaN durations by replacing with 0
                    durations = np.where(pd.isna(durations), 0, durations)
                else:
                    durations = np.zeros(len(onsets))
                
                # Get descriptions
                descriptions = events_df[desc_col].values.astype(str)
                
                # Filter to required event IDs, but also keep all events from events.tsv
                # The required_event_ids check is for validation, but we should preserve all events
                # However, the task says to preserve the specific event IDs in raw.annotations
                # So we include all events that match required IDs, or all events if none match
                
                mask = np.isin(descriptions, self.required_event_ids)
                
                # If we have matching events, use only those (per task requirement)
                # If no matching events, use all events (fallback for data integrity)
                if mask.any():
                    onsets = onsets[mask]
                    durations = durations[mask]
                    descriptions = descriptions[mask]
                
                # Create and set annotations
                if len(onsets) > 0:
                    annot = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions
                    )
                    raw.set_annotations(annot)
        
        return raw


KERNEL = PhysionetHmcSleepStagingKernel()