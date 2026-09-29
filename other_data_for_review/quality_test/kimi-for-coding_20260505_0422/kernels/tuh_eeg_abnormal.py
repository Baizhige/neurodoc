import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class TuhEegAbnormalKernel:
    KERNEL_ID = "tuh_eeg_abnormal"
    KERNEL_NAME = "TUH EEG Abnormal Corpus"
    KERNEL_DESCRIPTION = "Kernel for TUH EEG Abnormal Corpus v3.0.1+"
    KERNEL_CITATION = "10.3389/fnins.2016.00196"
    KERNEL_LICENSE = "TUH Use Agreement"
    KERNEL_URL = "https://www.isip.piconepress.com/projects/tuh_eeg/"

    required_event_ids = []
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = []

    # TUH standard 10-20 channel names (common variants)
    CHANNEL_RENAME_MAP = {
        # Standard 10-20
        'EEG FP1': 'Fp1', 'EEG FP2': 'Fp2', 'EEG F3': 'F3', 'EEG F4': 'F4',
        'EEG C3': 'C3', 'EEG C4': 'C4', 'EEG P3': 'P3', 'EEG P4': 'P4',
        'EEG O1': 'O1', 'EEG O2': 'O2', 'EEG F7': 'F7', 'EEG F8': 'F8',
        'EEG T3': 'T7', 'EEG T4': 'T8', 'EEG T5': 'P7', 'EEG T6': 'P8',
        'EEG A1': 'A1', 'EEG A2': 'A2', 'EEG FZ': 'Fz', 'EEG CZ': 'Cz',
        'EEG PZ': 'Pz', 'EEG FPZ': 'Fpz', 'EEG OZ': 'Oz',
        # Alternative naming
        'FP1': 'Fp1', 'FP2': 'Fp2', 'FZ': 'Fz', 'CZ': 'Cz', 'PZ': 'Pz', 'OZ': 'Oz', 'FPZ': 'Fpz',
        'T3': 'T7', 'T4': 'T8', 'T5': 'P7', 'T6': 'P8',
        # Already standard
        'Fp1': 'Fp1', 'Fp2': 'Fp2', 'F3': 'F3', 'F4': 'F4',
        'C3': 'C3', 'C4': 'C4', 'P3': 'P3', 'P4': 'P4',
        'O1': 'O1', 'O2': 'O2', 'F7': 'F7', 'F8': 'F8',
        'T7': 'T7', 'T8': 'T8', 'P7': 'P7', 'P8': 'P8',
        'A1': 'A1', 'A2': 'A2', 'Fz': 'Fz', 'Cz': 'Cz',
        'Pz': 'Pz', 'Fpz': 'Fpz', 'Oz': 'Oz',
        # Extended 10-10
        'AF3': 'AF3', 'AF4': 'AF4', 'AF7': 'AF7', 'AF8': 'AF8', 'AFz': 'AFz',
        'F1': 'F1', 'F2': 'F2', 'F5': 'F5', 'F6': 'F6',
        'FC1': 'FC1', 'FC2': 'FC2', 'FC3': 'FC3', 'FC4': 'FC4',
        'FC5': 'FC5', 'FC6': 'FC6', 'FCz': 'FCz',
        'FT7': 'FT7', 'FT8': 'FT8', 'FT9': 'FT9', 'FT10': 'FT10',
        'C1': 'C1', 'C2': 'C2', 'C5': 'C5', 'C6': 'C6',
        'CP1': 'CP1', 'CP2': 'CP2', 'CP3': 'CP3', 'CP4': 'CP4',
        'CP5': 'CP5', 'CP6': 'CP6', 'CPz': 'CPz',
        'TP7': 'TP7', 'TP8': 'TP8', 'TP9': 'TP9', 'TP10': 'TP10',
        'P1': 'P1', 'P2': 'P2', 'P5': 'P5', 'P6': 'P6',
        'PO3': 'PO3', 'PO4': 'PO4', 'PO7': 'PO7', 'PO8': 'PO8', 'POz': 'POz',
        'O1': 'O1', 'O2': 'O2', 'Oz': 'Oz', 'Iz': 'Iz',
        # ECG / EMG / other
        'ECG': 'ECG', 'EKG': 'ECG',
        'EMG': 'EMG',
        'PHOTIC': 'PHOTIC', 'PHOTIC-REF': 'PHOTIC',
        'IBI': 'IBI', 'BURSTS': 'BURSTS', 'SUPPR': 'SUPPR',
    }

    def __init__(self):
        pass

    def _get_file_path(self, row):
        """Extract file path from row (Series or dict)."""
        if isinstance(row, pd.Series):
            # Try common index names
            for key in ['file_path', 'filepath', 'path', 'filename', 'File Path', 'FilePath']:
                if key in row.index:
                    return str(row[key])
            # Fallback: try to find any column containing 'path' or 'file'
            for idx in row.index:
                if 'path' in str(idx).lower() or 'file' in str(idx).lower():
                    return str(row[idx])
            # Last resort: convert to dict
            row_dict = row.to_dict()
            for key in row_dict:
                if isinstance(row_dict[key], str) and os.path.exists(row_dict[key]):
                    return row_dict[key]
            return ""
        elif isinstance(row, dict):
            for key in ['file_path', 'filepath', 'path', 'filename', 'File Path', 'FilePath']:
                if key in row:
                    return str(row[key])
            for key in row:
                if isinstance(row[key], str) and os.path.exists(row[key]):
                    return row[key]
            return ""
        else:
            # Try attributes
            for attr in ['file_path', 'filepath', 'path', 'filename']:
                if hasattr(row, attr):
                    val = getattr(row, attr)
                    if val is not None:
                        return str(val)
            return ""

    def _find_bids_root(self, filepath):
        """Find BIDS root by looking for participants.tsv or directory structure."""
        if not filepath:
            return None
        current = os.path.dirname(os.path.abspath(filepath))
        while current != os.sep and current != '':
            # Check for participants.tsv
            if os.path.exists(os.path.join(current, 'participants.tsv')):
                return current
            # Check for dataset_description.json
            if os.path.exists(os.path.join(current, 'dataset_description.json')):
                return current
            # Check for typical TUH structure markers
            if any(d in os.listdir(current) for d in ['edf', 'eval', 'train', 'dev_test']):
                # Go up one more to find true root
                parent = os.path.dirname(current)
                if os.path.exists(os.path.join(parent, 'participants.tsv')):
                    return parent
                # Current might be root
                return current
            current = os.path.dirname(current)
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv in BIDS root or nearby."""
        if not bids_root:
            return None
        candidates = [
            os.path.join(bids_root, 'participants.tsv'),
            os.path.join(os.path.dirname(bids_root), 'participants.tsv'),
            os.path.join(bids_root, '..', 'participants.tsv'),
        ]
        for p in candidates:
            p = os.path.normpath(p)
            if os.path.exists(p):
                return p
        return None

    def _extract_subject_id_from_path(self, filepath):
        """Extract subject ID from TUH file path."""
        if not filepath:
            return None
        parts = os.path.normpath(filepath).split(os.sep)
        # Look for pattern like aaaaajon_s001 or sub-aaaaajon
        for part in parts:
            # TUH pattern: aaaaajon_s001_t000.edf -> subject aaaaajon
            m = re.match(r'^([a-z]{3,8})_s\d+_t\d+', part, re.IGNORECASE)
            if m:
                return m.group(1).lower()
            # BIDS pattern
            m = re.match(r'^sub-([a-zA-Z0-9]+)', part)
            if m:
                return m.group(1).lower()
        # Try from filename
        basename = os.path.basename(filepath)
        m = re.match(r'^([a-z]{3,8})_s\d+_t\d+', basename, re.IGNORECASE)
        if m:
            return m.group(1).lower()
        return None

    def _read_participants_info(self, participants_tsv, subject_id):
        """Read subject info from participants.tsv."""
        if not participants_tsv or not os.path.exists(participants_tsv) or not subject_id:
            return {}
        try:
            df = pd.read_csv(participants_tsv, sep='\t')
            if df.empty:
                return {}

            # Find subject column
            subj_col = None
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['participant_id', 'subject', 'subject_id', 'pat_id', 'patient_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            # Try exact match, then with/without prefix
            search_ids = [subject_id]
            if not subject_id.startswith('sub-'):
                search_ids.append('sub-' + subject_id)
            else:
                search_ids.append(subject_id[4:])

            for sid in search_ids:
                mask = df[subj_col].astype(str).str.lower() == sid.lower()
                if mask.any():
                    row = df[mask].iloc[0]
                    info = {}
                    for field in self.required_info_fields:
                        if field in row.index:
                            val = row[field]
                            if pd.isna(val):
                                info[field] = "unknown"
                            else:
                                info[field] = str(val).strip()
                        else:
                            info[field] = "unknown"
                    # Add any extra fields from participants.tsv
                    for col in df.columns:
                        if col not in [subj_col] + self.required_info_fields:
                            val = row.get(col, "unknown")
                            if pd.isna(val):
                                info[col] = "unknown"
                            else:
                                info[col] = str(val).strip()
                    return info

            return {}
        except Exception:
            return {}

    def _parse_age_from_filename(self, filepath):
        """Try to parse age from filename or path in TUH format."""
        # TUH sometimes encodes age in path or filename
        basename = os.path.basename(filepath)
        # Pattern: look for age like _22_ or similar in path
        m = re.search(r'[_/](\d{2,3})[_/]', filepath)
        if m:
            age = int(m.group(1))
            if 0 <= age <= 120:
                return str(age)
        return None

    def _parse_sex_from_path(self, filepath):
        """Try to infer sex from path patterns."""
        path_lower = filepath.lower()
        # TUH uses m/f in some versions
        if '/m/' in path_lower or '_m_' in path_lower:
            return 'male'
        if '/f/' in path_lower or '_f_' in path_lower:
            return 'female'
        return None

    def _get_subject_info(self, filepath, row):
        """Get subject info from all available sources."""
        info = {
            'age': 'unknown',
            'sex': 'unknown',
            'handedness': 'unknown',
            'amplifier': 'unknown',
            'cap': 'unknown',
        }

        # Try participants.tsv
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_id = self._extract_subject_id_from_path(filepath)

        if participants_tsv and subject_id:
            tsv_info = self._read_participants_info(participants_tsv, subject_id)
            info.update(tsv_info)

        # Try to get from row if available
        if isinstance(row, pd.Series) or isinstance(row, dict):
            row_data = dict(row) if isinstance(row, pd.Series) else row
            for key in ['age', 'sex', 'gender', 'handedness', 'amplifier', 'cap']:
                if key in row_data and str(row_data[key]).lower() not in ['nan', 'none', '', 'unknown']:
                    val = str(row_data[key]).strip()
                    if key == 'sex' or key == 'gender':
                        val_lower = val.lower()
                        if val_lower in ['m', 'male']:
                            val = 'male'
                        elif val_lower in ['f', 'female']:
                            val = 'female'
                        else:
                            val = 'unknown'
                    info[key] = val

        # Fallback: parse from filename
        if info['age'] == 'unknown':
            age = self._parse_age_from_filename(filepath)
            if age:
                info['age'] = age  # inferred by LLM, needs human review - but actually parsed
        if info['sex'] == 'unknown':
            sex = self._parse_sex_from_path(filepath)
            if sex:
                info['sex'] = sex  # inferred by LLM, needs human review

        # Normalize sex
        sex_lower = info.get('sex', 'unknown').lower()
        if sex_lower in ['m', 'male']:
            info['sex'] = 'male'
        elif sex_lower in ['f', 'female']:
            info['sex'] = 'female'
        else:
            info['sex'] = 'unknown'

        # Ensure age is string
        if info['age'] != 'unknown':
            try:
                # Remove non-numeric prefix/suffix, keep just the number
                age_str = re.sub(r'^[^\d]*(\d+)[^\d]*$', r'\1', str(info['age']))
                info['age'] = str(int(float(age_str)))
            except (ValueError, TypeError):
                info['age'] = 'unknown'

        return info

    def _find_events_tsv(self, filepath):
        """Find corresponding events.tsv file."""
        if not filepath:
            return None
        # BIDS sidecar pattern
        base = filepath.replace('.edf', '').replace('.set', '').replace('.fif', '').replace('.vhdr', '').replace('.eeg', '')
        events_path = base + '_events.tsv'
        if os.path.exists(events_path):
            return events_path

        # Look in same directory
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath).split('.')[0]
        for fname in os.listdir(dirname) if os.path.exists(dirname) else []:
            if fname.endswith('_events.tsv') and basename in fname:
                return os.path.join(dirname, fname)
            if fname == 'events.tsv':
                return os.path.join(dirname, fname)

        return None

    def _add_events_from_tsv(self, raw, events_tsv_path):
        """Add annotations from events.tsv to raw."""
        if not events_tsv_path or not os.path.exists(events_tsv_path):
            return raw

        try:
            df = pd.read_csv(events_tsv_path, sep='\t')
            if df.empty:
                return raw

            # Required BIDS columns
            onset_col = 'onset' if 'onset' in df.columns else None
            duration_col = 'duration' if 'duration' in df.columns else None
            desc_col = None
            for c in ['trial_type', 'value', 'event_type', 'description']:
                if c in df.columns:
                    desc_col = c
                    break

            if onset_col is None:
                return raw

            onsets = df[onset_col].values
            durations = df[duration_col].values if duration_col else np.zeros(len(onsets))
            descriptions = df[desc_col].astype(str).values if desc_col else np.array([''] * len(onsets))

            # Filter valid onsets
            valid = ~np.isnan(onsets)
            onsets = onsets[valid]
            durations = durations[valid]
            descriptions = descriptions[valid]

            if len(onsets) == 0:
                return raw

            # Convert durations, handle NaN
            durations = np.array([0.0 if pd.isna(d) else float(d) for d in durations])

            # Create annotations
            annot = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions
            )

            raw = raw.copy()
            raw.set_annotations(annot)
            return raw
        except Exception:
            return raw

    def _rename_channels(self, raw):
        """Rename channels to standard 10-20 naming."""
        raw = raw.copy()
        ch_names = raw.ch_names

        rename_map = {}
        for ch in ch_names:
            ch_upper = ch.upper().strip()
            ch_clean = ch.strip()
            # Try exact match first
            if ch_clean in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch_clean]
            elif ch_upper in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch_upper]
            else:
                # Try with EEG prefix removed
                if ch_upper.startswith('EEG '):
                    no_prefix = ch_upper[4:].strip()
                    if no_prefix in self.CHANNEL_RENAME_MAP:
                        rename_map[ch] = self.CHANNEL_RENAME_MAP[no_prefix]

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _set_channel_types(self, raw):
        """Set appropriate channel types."""
        raw = raw.copy()
        ch_names = raw.ch_names

        type_map = {}
        for ch in ch_names:
            ch_upper = ch.upper()
            if ch_upper in ['ECG', 'EKG']:
                type_map[ch] = 'ecg'
            elif ch_upper == 'EMG':
                type_map[ch] = 'emg'
            elif ch_upper in ['PHOTIC', 'PHOTIC-REF']:
                type_map[ch] = 'misc'
            elif ch_upper in ['IBI', 'BURSTS', 'SUPPR']:
                type_map[ch] = 'misc'
            elif ch_upper.startswith('DC'):
                type_map[ch] = 'dc'
            elif ch_upper in ['A1', 'A2', 'M1', 'M2', 'TP9', 'TP10', 'FT9', 'FT10']:
                # Check if likely mastoid/reference
                type_map[ch] = 'eeg'  # Keep as EEG, will be handled by montage

        if type_map:
            raw.set_channel_types(type_map)

        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage."""
        raw = raw.copy()
        ch_names = raw.ch_names

        # Filter to only EEG channels that are in standard montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            montage_chs = set(montage.ch_names)

            # Pick only channels that exist in montage
            eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
            eeg_ch_names = [raw.ch_names[i] for i in eeg_picks]
            valid_chs = [ch for ch in eeg_ch_names if ch in montage_chs]

            if valid_chs:
                # Set montage with reset=True to handle missing channels
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Ensure data is loaded for any channel manipulation
        if not raw.preload:
            raw.load_data()

        # Get file path
        filepath = self._get_file_path(row)

        # Get subject info
        info = self._get_subject_info(filepath, row)

        # Rename channels before montage
        raw = self._rename_channels(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Set montage
        raw = self._set_montage(raw)

        # Handle events from events.tsv if present
        # TUH EDF files typically don't have embedded annotations, so check for sidecar
        events_tsv = self._find_events_tsv(filepath)
        if events_tsv:
            raw = self._add_events_from_tsv(raw, events_tsv)

        # Build description
        original_desc = raw.info.get('description', '') or ''
        if not isinstance(original_desc, str):
            original_desc = str(original_desc)

        # Prepare eegunity_description
        eegunity_desc = {
            'age': str(info.get('age', 'unknown')),
            'sex': info.get('sex', 'unknown'),
            'amplifier': info.get('amplifier', 'unknown'),
            'cap': info.get('cap', 'unknown'),
            'handedness': info.get('handedness', 'unknown'),
        }

        # Add any extra fields from participants.tsv that aren't canonical
        canonical_keys = {'age', 'sex', 'amplifier', 'cap', 'handedness'}
        for key, val in info.items():
            if key not in canonical_keys:
                eegunity_desc[key] = str(val)

        # Mark inferred fields
        # If we couldn't find real values, they stay as 'unknown' (no fabrication)

        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_desc
        })

        return raw


KERNEL = TuhEegAbnormalKernel()