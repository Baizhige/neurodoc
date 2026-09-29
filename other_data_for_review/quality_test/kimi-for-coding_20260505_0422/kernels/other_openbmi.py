import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class OtherOpenbmiKernel:
    KERNEL_ID = "other_openbmi"
    KERNEL_NAME = "OpenBMI - GigaScience EEG Dataset"
    KERNEL_DESCRIPTION = "EEG kernel for OpenBMI dataset with motor imagery and event-related potential paradigms"
    KERNEL_CITATION = "10.1093/gigascience/giz002"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://gigadb.org/dataset/view/id/100542"

    # BIDS mapping
    required_event_ids = []
    required_info_fields = ['age', 'sex', 'handedness']
    required_native_misc = []
    derived_misc_channels = []

    # OpenBMI uses standard 10-20 or extended 10-20 montage
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F7': 'F7',
        'F3': 'F3',
        'Fz': 'Fz',
        'F4': 'F4',
        'F8': 'F8',
        'FC5': 'FC5',
        'FC1': 'FC1',
        'FC2': 'FC2',
        'FC6': 'FC6',
        'T7': 'T7',
        'C3': 'C3',
        'Cz': 'Cz',
        'C4': 'C4',
        'T8': 'T8',
        'TP9': 'TP9',
        'CP5': 'CP5',
        'CP1': 'CP1',
        'CP2': 'CP2',
        'CP6': 'CP6',
        'P7': 'P7',
        'P3': 'P3',
        'Pz': 'Pz',
        'P4': 'P4',
        'P8': 'P8',
        'PO9': 'PO9',
        'O1': 'O1',
        'Oz': 'Oz',
        'O2': 'O2',
        'PO10': 'PO10',
        'AF7': 'AF7',
        'AF3': 'AF3',
        'AF4': 'AF4',
        'AF8': 'AF8',
        'F5': 'F5',
        'F1': 'F1',
        'F2': 'F2',
        'F6': 'F6',
        'FT7': 'FT7',
        'FC3': 'FC3',
        'FC4': 'FC4',
        'FT8': 'FT8',
        'C5': 'C5',
        'C1': 'C1',
        'C2': 'C2',
        'C6': 'C6',
        'TP7': 'TP7',
        'CP3': 'CP3',
        'CPz': 'CPz',
        'CP4': 'CP4',
        'TP8': 'TP8',
        'P5': 'P5',
        'P1': 'P1',
        'P2': 'P2',
        'P6': 'P6',
        'PO7': 'PO7',
        'PO3': 'PO3',
        'POz': 'POz',
        'PO4': 'PO4',
        'PO8': 'PO8',
        'Fpz': 'Fpz',
        'FCz': 'FCz',
        'CPz': 'CPz',
        'POz': 'POz',
        'AFz': 'AFz',
        'TP9': 'TP9',
        'TP10': 'TP10',
        'PO9': 'PO9',
        'PO10': 'PO10',
        # EOG channels
        'HEO': 'HEO',
        'VEO': 'VEO',
        'HEOG': 'HEOG',
        'VEOG': 'VEOG',
        'EOG': 'EOG',
        # EMG channels
        'EMG': 'EMG',
        # Misc channels that might appear
        'Trigger': 'Trigger',
        'Status': 'Status',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.lower() in ['eeg', 'sub-']:
                # Go up to find root
                if i > 0:
                    potential_root = os.sep.join(parts[:i])
                    if os.path.exists(os.path.join(potential_root, 'participants.tsv')):
                        return potential_root
        # Fallback: look for participants.tsv going upward
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
                # Try with/without 'sub-' prefix
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
            # Extract sub-XX part
            parts2 = basename.split('_')
            if parts2[0].startswith('sub-'):
                return parts2[0]
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.edf -> sub-XX_task-YY_run-ZZ_events.tsv
        dirname = os.path.dirname(eeg_file_path)
        basename = os.path.basename(eeg_file_path)
        
        # Remove extension
        base_no_ext = basename.split('.')[0]
        events_tsv = os.path.join(dirname, base_no_ext + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without modality suffix (eeg -> nothing)
        if '_eeg' in base_no_ext:
            alt_base = base_no_ext.replace('_eeg', '')
            events_tsv = os.path.join(dirname, alt_base + '_events.tsv')
            if os.path.exists(events_tsv):
                return events_tsv
        
        # Look for any events.tsv in same directory
        if os.path.exists(dirname):
            for f in os.listdir(dirname):
                if f.endswith('_events.tsv'):
                    return os.path.join(dirname, f)
        
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

    def _events_to_annotations(self, events_df):
        """Convert events dataframe to MNE Annotations."""
        if events_df is None or len(events_df) == 0:
            return None
        
        onsets = []
        durations = []
        descriptions = []
        
        for _, row in events_df.iterrows():
            # onset column is required in BIDS
            if 'onset' in row:
                onset = float(row['onset'])
            else:
                continue
            
            # duration
            if 'duration' in row and not pd.isna(row['duration']):
                duration = float(row['duration'])
            else:
                duration = 0.0
            
            # description: prefer trial_type, then value, then stimulus_type
            if 'trial_type' in row and not pd.isna(row['trial_type']):
                desc = str(row['trial_type'])
            elif 'value' in row and not pd.isna(row['value']):
                desc = str(row['value'])
            elif 'stim_type' in row and not pd.isna(row['stim_type']):
                desc = str(row['stim_type'])
            elif 'event_type' in row and not pd.isna(row['event_type']):
                desc = str(row['event_type'])
            else:
                desc = 'unknown'
            
            onsets.append(onset)
            durations.append(duration)
            descriptions.append(desc)
        
        if len(onsets) == 0:
            return None
        
        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def _normalize_sex(self, sex_str):
        """Normalize sex string to standard values."""
        if sex_str is None or sex_str == "unknown":
            return "unknown"
        sex_lower = str(sex_str).lower().strip()
        if sex_lower in ['m', 'male', '1']:
            return 'male'
        elif sex_lower in ['f', 'female', '2']:
            return 'female'
        elif sex_lower in ['o', 'other', '0']:
            return 'unknown'  # Map other to unknown for simplicity
        else:
            return "unknown"  # inferred by LLM, needs human review

    def _normalize_age(self, age_val):
        """Normalize age to string."""
        if age_val is None or age_val == "unknown":
            return "unknown"
        try:
            # Handle ranges like "20-30"
            age_str = str(age_val).strip()
            if '-' in age_str:
                # Take midpoint of range
                parts = age_str.split('-')
                if len(parts) == 2:
                    try:
                        mid = (float(parts[0]) + float(parts[1])) / 2
                        return str(int(mid))
                    except ValueError:
                        return age_str
            # Try to parse as number
            age_float = float(age_str)
            return str(int(age_float))
        except (ValueError, TypeError):
            return str(age_val) if age_val else "unknown"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row['file_path'] if 'file_path' in row else None
        if filepath is None and hasattr(udataset, 'current_file_path'):
            filepath = udataset.current_file_path
        
        # Find BIDS root and participants info
        bids_root = self._find_bids_root(filepath) if filepath else None
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_id = self._get_subject_id_from_path(filepath) if filepath else None
        
        # Read participants info
        info = self._read_participants_info(participants_tsv, subject_id)
        
        # Set default values with inference comments where needed
        age = self._normalize_age(info.get('age', "unknown"))
        sex = self._normalize_sex(info.get('sex', "unknown"))
        handedness = str(info.get('handedness', "unknown")).lower() if info.get('handedness') else "unknown"
        
        # Default amplifier and cap for OpenBMI
        amplifier = "BrainAmp"  # inferred by LLM, needs human review - OpenBMI typically uses BrainAmp
        cap = "EasyCap"  # inferred by LLM, needs human review - standard 64-channel cap
        
        # Get original description
        original_description = raw.info.get('description', '')
        if original_description is None:
            original_description = ''
        
        # Build eegunity_description with required fields and any extra from participants.tsv
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add any extra fields from required_info_fields that aren't in the canonical set
        canonical_keys = {'age', 'sex', 'amplifier', 'cap', 'handedness'}
        for field in self.required_info_fields:
            if field not in canonical_keys and field in info:
                eegunity_desc[field] = str(info[field])
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_desc
        })
        
        # Channel renaming BEFORE set_montage
        # Map channels to standard names if they match our rename map
        rename_map = {}
        for ch_name in raw.ch_names:
            # Try exact match first
            if ch_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_name]
            else:
                # Try case-insensitive match
                ch_upper = ch_name.upper()
                for key, val in self.CHANNEL_RENAME_MAP.items():
                    if key.upper() == ch_upper:
                        rename_map[ch_name] = val
                        break
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage for EEG channels
        try:
            # Try to set montage using standard 10-20
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only set for channels that exist in the montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            available = list(montage_chs & raw_chs)
            if available:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass  # Montage setting failed, continue without
        
        # Handle misc channels
        # Check for native misc channels that need type correction
        if self.required_native_misc:
            ch_types = {ch['ch_name']: ch['kind'] for ch in raw.info['chs']}
            to_fix = {}
            for ch_name in self.required_native_misc:
                if ch_name in raw.ch_names:
                    # Check if it's not already misc
                    idx = raw.ch_names.index(ch_name)
                    if raw.info['chs'][idx]['kind'] != mne.io.constants.FIFF.FIFFV_MISC_CH:
                        to_fix[ch_name] = 'misc'
            if to_fix:
                raw.set_channel_types(to_fix)
        
        # Handle derived misc channels
        # For OpenBMI, we may need to create derived channels from events or other sources
        for derived_ch in self.derived_misc_channels:
            if derived_ch not in raw.ch_names:
                # Create a constant/misc channel with zeros or derived values
                # For now, create a zero-filled misc channel as placeholder
                data = np.zeros((1, len(raw.times)))
                info_misc = mne.create_info([derived_ch], raw.info['sfreq'], ['misc'])
                raw_misc = mne.io.RawArray(data, info_misc)
                raw.add_channels([raw_misc], force_update_info=True)
        
        # Handle events.tsv annotations for formats that don't carry their own triggers
        # Check if we need to add annotations from events.tsv
        needs_events_from_tsv = False
        
        # Determine file format
        file_ext = os.path.splitext(filepath)[1].lower() if filepath else ''
        
        # Check if raw already has annotations or events
        has_annotations = len(raw.annotations) > 0
        has_events = False
        try:
            # Try to get events - this may fail if no events
            events = mne.find_events(raw, shortest_event=1, verbose=False)
            has_events = len(events) > 0
        except Exception:
            pass
        
        # For EDF, BrainVision without markers, FIF without events, or EEGLAB without events
        if file_ext in ['.edf', '.bdf']:
            # EDF/BDF may or may not have annotations
            if not has_annotations and not has_events:
                needs_events_from_tsv = True
        elif file_ext == '.eeg':
            # BrainVision .eeg without .vmrk
            vmrk_file = filepath.replace('.eeg', '.vmrk') if filepath else ''
            if not os.path.exists(vmrk_file):
                needs_events_from_tsv = True
        elif file_ext == '.fif':
            # Plain .fif without baked-in events
            if not has_events and not has_annotations:
                needs_events_from_tsv = True
        elif file_ext == '.set':
            # EEGLAB .set without populated events
            if not has_events and not has_annotations:
                needs_events_from_tsv = True
        
        # Also check if events.tsv exists
        events_tsv = self._find_events_tsv(filepath) if filepath else None
        if events_tsv and needs_events_from_tsv:
            events_df = self._read_events_tsv(events_tsv)
            if events_df is not None and len(events_df) > 0:
                annotations = self._events_to_annotations(events_df)
                if annotations is not None:
                    # Add annotations to raw
                    if len(raw.annotations) > 0:
                        # Combine with existing
                        raw.set_annotations(raw.annotations + annotations)
                    else:
                        raw.set_annotations(annotations)
        
        # Ensure required event IDs can be extracted
        if self.required_event_ids:
            try:
                events, event_id = mne.events_from_annotations(raw)
                # Verify required events exist
                if events is not None and len(events) > 0:
                    available_ids = set(event_id.values())
                    # Map string required_event_ids to int if needed
                    for req_id in self.required_event_ids:
                        try:
                            req_int = int(req_id)
                            if req_int not in available_ids:
                                warnings.warn(f"Required event ID {req_id} not found in data")
                        except ValueError:
                            # String event ID - check in event_id keys
                            if req_id not in event_id:
                                warnings.warn(f"Required event {req_id} not found in annotations")
            except Exception:
                pass  # No events available, which is OK if not required
        
        return raw


KERNEL = OtherOpenbmiKernel()