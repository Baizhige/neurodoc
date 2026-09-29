import json
import os
import numpy as np
import pandas as pd
import mne


class PhysionetAuditoryEegKernel:
    KERNEL_ID = "physionet_auditoryeeg"
    KERNEL_NAME = "PhysioNet auditory-eeg - 20-class EEG Biometric Identification"
    KERNEL_DESCRIPTION = "EEG kernel for 20-subject biometric identification using 2-minute EEG segments across 8 auditory conditions"
    KERNEL_CITATION = "10.13026/ps31-fc50"
    KERNEL_LICENSE = "ODC-By"
    KERNEL_URL = "https://physionet.org/content/auditory-eeg/1.0.0/"

    required_event_ids = [
        'subject_01', 'subject_02', 'subject_03', 'subject_04', 'subject_05',
        'subject_06', 'subject_07', 'subject_08', 'subject_09', 'subject_10',
        'subject_11', 'subject_12', 'subject_13', 'subject_14', 'subject_15',
        'subject_16', 'subject_17', 'subject_18', 'subject_19', 'subject_20'
    ]
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = ['condition_id']

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
        'TP9': 'TP9',
        'TP10': 'TP10',
        'POz': 'POz',
    }

    # Condition mapping from directory structure / filename patterns
    CONDITIONS = {
        'rest_eo': 1,   # resting-state eyes open
        'rest_ec': 2,   # resting-state eyes closed
        'am': 3,        # amplitude modulated noise
        'chor': 4,      # choral music
        'country': 5,   # country music
        'edm': 6,       # electronic dance music
        'classical': 7, # classical music
        'metal': 8,     # metal music
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # Look for dataset root (contains subjects, references, etc.)
        for i, part in enumerate(parts):
            if 'auditory' in part.lower() or 'physionet' in part.lower():
                # Go up to find the actual root with sub-XX folders
                for j in range(i, len(parts)):
                    if parts[j].startswith('sub-'):
                        return os.sep.join(parts[:j])
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        return os.path.dirname(filepath)

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        # Try from filename
        basename = os.path.basename(filepath)
        if 'sub' in basename.lower():
            # Extract sub-XX pattern
            import re
            match = re.search(r'sub[_-]?(\d+)', basename, re.IGNORECASE)
            if match:
                return f"sub-{int(match.group(1)):02d}"
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        # Check common locations
        for p_tsv in [
            os.path.join(bids_root, 'participants.tsv'),
            os.path.join(os.path.dirname(bids_root), 'participants.tsv'),
            os.path.join(bids_root, 'dataset', 'participants.tsv'),
        ]:
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

            # Normalize subject ID for matching
            search_ids = [subject_id]
            if subject_id.startswith('sub-'):
                search_ids.append(subject_id[4:])  # without 'sub-' prefix
                search_ids.append(f"sub{subject_id[4:]}")
                search_ids.append(str(int(subject_id[4:])))  # numeric
            else:
                search_ids.append(f"sub-{subject_id}")
                search_ids.append(f"sub{subject_id}")

            subj_rows = df[df[subj_col].isin(search_ids)]
            if len(subj_rows) == 0:
                # Try numeric match
                for sid in search_ids:
                    try:
                        num_sid = int(sid)
                        subj_rows = df[df[subj_col] == num_sid]
                        if len(subj_rows) > 0:
                            break
                    except (ValueError, TypeError):
                        continue

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
                        info[field] = str(val).strip()
                else:
                    info[field] = "unknown"
            return info
        except Exception:
            return {}

    def _find_data_trim_csv(self, bids_root):
        """Find data_trim.csv file."""
        if bids_root is None:
            return None
        for path in [
            os.path.join(bids_root, 'data_trim.csv'),
            os.path.join(os.path.dirname(bids_root), 'data_trim.csv'),
            os.path.join(bids_root, 'dataset', 'data_trim.csv'),
        ]:
            if os.path.exists(path):
                return path
        return None

    def _read_trim_info(self, data_trim_csv, subject_id, task_name):
        """Read trim points for a specific subject and task from data_trim.csv."""
        if data_trim_csv is None or not os.path.exists(data_trim_csv):
            return None
        try:
            df = pd.read_csv(data_trim_csv)
            # Normalize subject ID
            sub_num = None
            if subject_id and subject_id.startswith('sub-'):
                sub_num = int(subject_id[4:])
            
            # Try to match by subject number and task
            for _, row in df.iterrows():
                row_sub = row.get('subject', row.get('Subject', None))
                row_task = row.get('task', row.get('Task', None))
                
                # Match subject
                sub_match = False
                if row_sub is not None:
                    try:
                        if int(row_sub) == sub_num:
                            sub_match = True
                    except (ValueError, TypeError):
                        if str(row_sub).lower() == str(sub_num).lower():
                            sub_match = True
                
                # Match task
                task_match = False
                if row_task is not None and task_name:
                    task_str = str(row_task).lower().replace('-', '_').replace(' ', '_')
                    task_name_norm = task_name.lower().replace('-', '_').replace(' ', '_')
                    if task_str in task_name_norm or task_name_norm in task_str:
                        task_match = True
                
                if sub_match and task_match:
                    start = row.get('start', row.get('Start', None))
                    stop = row.get('stop', row.get('Stop', None))
                    if start is not None and stop is not None:
                        return {'start': float(start), 'stop': float(stop)}
            return None
        except Exception:
            return None

    def _get_condition_from_path(self, filepath):
        """Extract condition from file path or name."""
        parts = os.path.normpath(filepath).split(os.sep)
        filename = os.path.basename(filepath).lower()
        
        # Check directory names and filename for condition indicators
        all_parts = parts + [filename]
        for part in all_parts:
            part_lower = part.lower()
            if 'rest_eo' in part_lower or 'resting_eo' in part_lower or 'eyes_open' in part_lower:
                return 'rest_eo'
            elif 'rest_ec' in part_lower or 'resting_ec' in part_lower or 'eyes_closed' in part_lower:
                return 'rest_ec'
            elif 'am_' in part_lower or '_am_' in part_lower or 'amplitude' in part_lower:
                return 'am'
            elif 'chor' in part_lower:
                return 'chor'
            elif 'country' in part_lower:
                return 'country'
            elif 'edm' in part_lower or 'electronic' in part_lower or 'dance' in part_lower:
                return 'edm'
            elif 'classical' in part_lower or 'classic' in part_lower:
                return 'classical'
            elif 'metal' in part_lower:
                return 'metal'
        
        # Infer from filename pattern: sub-XX_task-YYYY_run-ZZ
        # Try to extract task name
        import re
        task_match = re.search(r'task[-_](\w+)', filename, re.IGNORECASE)
        if task_match:
            task = task_match.group(1).lower()
            for cond_name in self.CONDITIONS:
                if cond_name in task or task in cond_name:
                    return cond_name
        
        return 'rest_eo'  # inferred by LLM, needs human review

    def _get_task_name_from_path(self, filepath):
        """Extract BIDS task name from path."""
        filename = os.path.basename(filepath)
        import re
        task_match = re.search(r'task[-_](\w+)', filename, re.IGNORECASE)
        if task_match:
            return task_match.group(1)
        # Try from directory
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            task_match = re.search(r'task[-_](\w+)', part, re.IGNORECASE)
            if task_match:
                return task_match.group(1)
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find events.tsv file corresponding to EEG file."""
        base = eeg_file_path.replace('.set', '').replace('.edf', '').replace('.eeg', '').replace('.fif', '')
        # Try BIDS naming
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        # Try in same directory
        dirname = os.path.dirname(eeg_file_path)
        basename = os.path.basename(eeg_file_path)
        # Remove extensions
        base_name = basename.split('.')[0]
        for fname in os.listdir(dirname) if os.path.exists(dirname) else []:
            if fname.endswith('_events.tsv') and base_name in fname:
                return os.path.join(dirname, fname)
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

    def _create_annotations_from_events_tsv(self, raw, events_df):
        """Create MNE Annotations from events.tsv DataFrame."""
        if events_df is None or len(events_df) == 0:
            return None
        
        onsets = []
        durations = []
        descriptions = []
        
        for _, row in events_df.iterrows():
            onset = row.get('onset', row.get('sample', None))
            duration = row.get('duration', 0.0)
            if pd.isna(duration):
                duration = 0.0
            
            # Use trial_type if available, else value, else description
            desc = None
            for col in ['trial_type', 'value', 'description', 'event_type']:
                if col in row and pd.notna(row[col]):
                    desc = str(row[col])
                    break
            
            if desc is None:
                continue
            
            if onset is not None and pd.notna(onset):
                # Convert sample to time if needed
                if 'sample' in row and 'onset' not in row:
                    onset = float(onset) / raw.info['sfreq']
                else:
                    onset = float(onset)
                onsets.append(onset)
                durations.append(float(duration))
                descriptions.append(desc)
        
        if len(onsets) == 0:
            return None
        
        annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
        return annot

    def _create_subject_annotation(self, raw, subject_id):
        """Create a single annotation covering the entire recording for subject ID."""
        if subject_id is None:
            return None
        # Map sub-XX to subject_XX event ID
        sub_num = subject_id.replace('sub-', '')
        event_id = f"subject_{int(sub_num):02d}"
        
        # Create annotation for entire duration
        duration = raw.times[-1] if len(raw.times) > 0 else 0
        annot = mne.Annotations(onset=[0.0], duration=[duration], description=[event_id])
        return annot

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('File Path', None)
        if filepath is None:
            filepath = row.get('file_path', None)
        if filepath is None:
            filepath = row.get('filename', None)
        
        # Extract subject ID
        subject_id = self._get_subject_id_from_path(filepath) if filepath else None
        
        # Find BIDS root
        bids_root = self._find_bids_root(filepath) if filepath else None
        
        # Read participants info
        participants_tsv = self._find_participants_tsv(bids_root)
        info = self._read_participants_info(participants_tsv, subject_id) if subject_id else {}
        
        # Ensure required fields exist
        age = info.get('age', "unknown")
        sex = info.get('sex', "unknown").lower()
        if sex not in ['male', 'female']:
            sex = "unknown"
        
        # Get condition info
        condition = self._get_condition_from_path(filepath) if filepath else 'rest_eo'
        condition_id = self.CONDITIONS.get(condition, 0)
        
        # Get task name for trim lookup
        task_name = self._get_task_name_from_path(filepath)
        
        # Read trim info if available
        trim_info = None
        if filepath and subject_id:
            data_trim_csv = self._find_data_trim_csv(bids_root)
            trim_info = self._read_trim_info(data_trim_csv, subject_id, task_name or condition)
        
        # Apply trimming if data_trim.csv specifies it
        if trim_info is not None:
            start_time = trim_info['start']
            stop_time = trim_info['stop']
            # Crop the raw data
            if start_time < raw.times[-1] and stop_time > raw.times[0]:
                raw.crop(tmin=max(start_time, 0), tmin=min(stop_time, raw.times[-1]))
        
        # Channel renaming
        # First, check current channel names and rename to standard 10-20
        current_names = raw.ch_names
        rename_map = {}
        for ch in current_names:
            ch_upper = ch.upper()
            # Direct match
            if ch in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
            elif ch_upper in [k.upper() for k in self.CHANNEL_RENAME_MAP]:
                for k, v in self.CHANNEL_RENAME_MAP.items():
                    if k.upper() == ch_upper:
                        rename_map[ch] = v
                        break
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known EEG channels
        eeg_channels = [ch for ch in raw.ch_names if ch in self.CHANNEL_RENAME_MAP.values()]
        ch_types = {ch: 'eeg' for ch in eeg_channels}
        
        # Apply channel types
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage (standard 10-20)
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass  # inferred by LLM, needs human review
        
        # Handle events: create subject annotation for entire recording
        # This dataset has no native triggers, so we create annotations from subject identity
        annot = self._create_subject_annotation(raw, subject_id)
        
        # Also check for events.tsv sidecar
        events_tsv = self._find_events_tsv(filepath) if filepath else None
        events_df = self._read_events_tsv(events_tsv)
        if events_df is not None and len(events_df) > 0:
            # Use events.tsv annotations if available
            annot_from_tsv = self._create_annotations_from_events_tsv(raw, events_df)
            if annot_from_tsv is not None:
                annot = annot_from_tsv
        
        if annot is not None:
            raw.set_annotations(annot)
        
        # Create derived misc channel for condition ID
        # This is a constant value channel indicating which experimental condition
        if 'condition_id' in self.derived_misc_channels:
            condition_data = np.full((1, len(raw.times)), float(condition_id))
            condition_info = mne.create_info(
                ch_names=['condition_id'],
                sfreq=raw.info['sfreq'],
                ch_types=['misc']
            )
            condition_raw = mne.io.RawArray(condition_data, condition_info)
            raw.add_channels([condition_raw], force_update_info=True)
        
        # Set description with metadata
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Build eegunity_description
        eegunity_desc = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }
        
        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in ['age', 'sex'] and field in info:
                eegunity_desc[field] = str(info[field]) if info[field] is not None else "unknown"
        
        # Add condition info
        eegunity_desc['condition'] = condition
        eegunity_desc['condition_id'] = str(condition_id)
        eegunity_desc['subject_id'] = subject_id if subject_id else "unknown"
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        return raw


KERNEL = PhysionetAuditoryEegKernel()