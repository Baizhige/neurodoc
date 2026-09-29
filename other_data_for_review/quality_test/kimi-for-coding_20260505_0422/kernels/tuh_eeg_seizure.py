import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class TuhEegSeizureKernel:
    KERNEL_ID = "tuh_eeg_seizure"
    KERNEL_NAME = "TUH EEG Seizure Corpus v2.0.3"
    KERNEL_DESCRIPTION = "EEG kernel for Temple University Hospital EEG Seizure Corpus with seizure annotation-derived misc channel"
    KERNEL_CITATION = "10.1109/GlobalSIP.2013.6736803"
    KERNEL_LICENSE = "TUH EEG License"
    KERNEL_URL = "https://www.isip.piconepress.com/projects/tuh_eeg/"

    required_event_ids = []
    required_info_fields = []
    required_native_misc = []
    derived_misc_channels = ['seizure_label']

    # Standard 10-20 channel names for TUH EEG
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
        'EEG T1-REF': 'T1',
        'EEG T2-REF': 'T2',
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
        'EEG T1-LE': 'T1',
        'EEG T2-LE': 'T2',
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
        'EEG T1': 'T1',
        'EEG T2': 'T2',
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
        'T1-REF': 'T1',
        'T2-REF': 'T2',
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
        'T1-LE': 'T1',
        'T2-LE': 'T2',
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
        'T1': 'T1',
        'T2': 'T2',
        'EKG1-REF': 'EKG1',
        'EKG2-REF': 'EKG2',
        'EKG-REF': 'EKG',
        'EMG-REF': 'EMG',
        'EOG-REF': 'EOG',
        'ECG-REF': 'ECG',
        'PHOTIC-REF': 'PHOTIC',
        'IBI': 'IBI',
        'BURSTS': 'BURSTS',
        'SUPPR': 'SUPPR',
        'SP1': 'SP1',
        'SP2': 'SP2',
        'EDF ANNOTATIONS': 'EDF_ANNOTATIONS',
        'EDFANNOTATIONS': 'EDF_ANNOTATIONS',
        'EDF Annotations': 'EDF_ANNOTATIONS',
        'edf annotations': 'EDF_ANNOTATIONS',
    }

    def __init__(self):
        pass

    def _find_tuh_root(self, filepath):
        """Find TUH EEG root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'tuh_eeg_seizure' in part.lower() or 'tuh_eeg' in part.lower():
                # Go up to find the version root (e.g., v2.0.3)
                for j in range(i, len(parts)):
                    if parts[j].startswith('v') and '.' in parts[j]:
                        return os.sep.join(parts[:j+1])
                return os.sep.join(parts[:i+1])
        # Fallback: look for edf/ or train/ directories
        for i, part in enumerate(parts):
            if part in ['edf', 'train', 'dev', 'eval']:
                return os.sep.join(parts[:i])
        return None

    def _find_seizure_csv(self, filepath):
        """Find seizure annotation CSV for a given EDF file."""
        # TUH structure: .../edf/train/subject/session/01_tcp_ar/subject_session_tN.edf
        # CSV is typically at same level or in a _SEIZURES subdirectory
        edf_dir = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        
        # Try multiple possible locations for seizure CSV
        possible_paths = [
            os.path.join(edf_dir, basename + '.csv'),
            os.path.join(edf_dir, basename + '_seizures.csv'),
            os.path.join(edf_dir, basename + '_SEIZURES.csv'),
            os.path.join(edf_dir, '_SEIZURES', basename + '.csv'),
            os.path.join(edf_dir, '_SEIZURES', basename + '_seizures.csv'),
            os.path.join(edf_dir, '_SEIZURES', basename + '_SEIZURES.csv'),
            os.path.join(edf_dir, 'seizures', basename + '.csv'),
            os.path.join(edf_dir, 'seizures', basename + '_seizures.csv'),
        ]
        
        # Also try parent directories
        parent_dir = os.path.dirname(edf_dir)
        possible_paths.extend([
            os.path.join(parent_dir, basename + '.csv'),
            os.path.join(parent_dir, basename + '_seizures.csv'),
            os.path.join(parent_dir, '_SEIZURES', basename + '.csv'),
            os.path.join(parent_dir, '_SEIZURES', basename + '_seizures.csv'),
        ])
        
        # Try with session-level _SEIZURES directory
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('s') and len(part) >= 4 and part[1:4].isdigit():
                # Found session directory like s004_2015
                session_dir = os.sep.join(parts[:i+1])
                possible_paths.extend([
                    os.path.join(session_dir, '_SEIZURES', basename + '.csv'),
                    os.path.join(session_dir, '_SEIZURES', basename + '_seizures.csv'),
                    os.path.join(session_dir, '_SEIZURES', basename + '_SEIZURES.csv'),
                    os.path.join(session_dir, basename + '.csv'),
                    os.path.join(session_dir, basename + '_seizures.csv'),
                ])
                break
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try glob search in nearby directories
        import glob
        for pattern in [
            os.path.join(edf_dir, '*.csv'),
            os.path.join(edf_dir, '*SEIZURES*', '*.csv'),
            os.path.join(parent_dir, '*.csv'),
            os.path.join(parent_dir, '*SEIZURES*', '*.csv'),
        ]:
            matches = glob.glob(pattern)
            for match in matches:
                match_base = os.path.splitext(os.path.basename(match))[0]
                if basename in match_base or match_base in basename:
                    return match
        
        return None

    def _parse_seizure_csv(self, csv_path, raw_n_times, sfreq):
        """Parse TUH seizure CSV and return list of (start_sample, end_sample) tuples."""
        seizures = []
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # TUH CSV format has header lines starting with #
            # Data lines contain: start_time, stop_time, label, confidence
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        start_time = float(parts[0].strip())
                        stop_time = float(parts[1].strip())
                        
                        # Convert to samples
                        start_sample = max(0, int(start_time * sfreq))
                        end_sample = min(raw_n_times, int(stop_time * sfreq))
                        
                        if start_sample < end_sample:
                            seizures.append((start_sample, end_sample))
                    except (ValueError, IndexError):
                        continue
        except Exception:
            pass
        
        return seizures

    def _parse_seizure_xls(self, xls_path, raw_n_times, sfreq):
        """Parse TUH seizure XLS/XLSX file and return list of (start_sample, end_sample) tuples."""
        seizures = []
        try:
            # Try reading with pandas
            if xls_path.endswith('.xlsx'):
                df = pd.read_excel(xls_path, engine='openpyxl', header=None)
            else:
                df = pd.read_excel(xls_path, engine='xlrd', header=None)
            
            # Look for start/stop time columns
            for idx, row in df.iterrows():
                try:
                    # Try to find time columns - typically columns 0 and 1 or named
                    vals = row.values
                    if len(vals) >= 2:
                        start_time = float(vals[0])
                        stop_time = float(vals[1])
                        
                        start_sample = max(0, int(start_time * sfreq))
                        end_sample = min(raw_n_times, int(stop_time * sfreq))
                        
                        if start_sample < end_sample:
                            seizures.append((start_sample, end_sample))
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
        
        return seizures

    def _find_seizure_annotations(self, filepath, raw_n_times, sfreq):
        """Find and parse seizure annotations from any available source."""
        # Try CSV first
        csv_path = self._find_seizure_csv(filepath)
        if csv_path:
            if csv_path.endswith('.csv'):
                return self._parse_seizure_csv(csv_path, raw_n_times, sfreq)
            elif csv_path.endswith(('.xls', '.xlsx')):
                return self._parse_seizure_xls(csv_path, raw_n_times, sfreq)
        
        # Try XLS/XLSX directly
        edf_dir = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        
        for ext in ['.xls', '.xlsx']:
            for subdir in ['', '_SEIZURES', 'seizures']:
                xls_path = os.path.join(edf_dir, subdir, basename + ext) if subdir else os.path.join(edf_dir, basename + ext)
                if os.path.exists(xls_path):
                    return self._parse_seizure_xls(xls_path, raw_n_times, sfreq)
        
        # Try parent directory
        parent_dir = os.path.dirname(edf_dir)
        for ext in ['.xls', '.xlsx']:
            for subdir in ['', '_SEIZURES']:
                xls_path = os.path.join(parent_dir, subdir, basename + ext) if subdir else os.path.join(parent_dir, basename + ext)
                if os.path.exists(xls_path):
                    return self._parse_seizure_xls(xls_path, raw_n_times, sfreq)
        
        return []

    def _find_participants_tsv(self, filepath):
        """Find participants.tsv in TUH dataset."""
        tuh_root = self._find_tuh_root(filepath)
        if tuh_root is None:
            return None
        
        # Try various locations
        possible_paths = [
            os.path.join(tuh_root, 'participants.tsv'),
            os.path.join(os.path.dirname(tuh_root), 'participants.tsv'),
            os.path.join(tuh_root, 'edf', 'participants.tsv'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
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
                if col.lower() in ['participant_id', 'subject', 'subject_id', 'patient_id']:
                    subj_col = col
                    break
            
            if subj_col is None:
                subj_col = df.columns[0]
            
            # Match subject - TUH uses codes like 'aaaaatds'
            # Extract subject code from path or use as-is
            subj_rows = df[df[subj_col].astype(str) == str(subject_id)]
            
            if len(subj_rows) == 0:
                # Try partial match
                for idx, val in df[subj_col].items():
                    if str(subject_id) in str(val) or str(val) in str(subject_id):
                        subj_rows = df.iloc[[idx]]
                        break
            
            if len(subj_rows) == 0:
                return {}
            
            row = subj_rows.iloc[0]
            info = {}
            for field in self.required_info_fields:
                if field in row.index:
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

    def _extract_subject_id(self, filepath):
        """Extract TUH subject ID from filepath."""
        basename = os.path.splitext(os.path.basename(filepath))[0]
        # TUH format: aaaaatds_s004_t006
        parts = basename.split('_')
        if len(parts) >= 2:
            # Return first part as subject code
            return parts[0]
        
        # Fallback: use directory name
        parent = os.path.basename(os.path.dirname(filepath))
        if parent.startswith('s') and len(parent) >= 4:
            # This is a session dir, go up one more
            return os.path.basename(os.path.dirname(os.path.dirname(filepath)))
        
        return basename

    def _get_standard_1020_montage(self):
        """Get standard 10-20 montage for TUH EEG."""
        montage = mne.channels.make_standard_montage('standard_1020')
        return montage

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Ensure data is loaded for channel operations
        if not raw.preload:
            raw.load_data()
        
        filepath = row.get('file_path', '') if hasattr(row, 'get') else ''
        if not filepath and hasattr(row, 'file_path'):
            filepath = row.file_path
        
        # Get original description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Extract subject info
        subject_id = self._extract_subject_id(filepath)
        
        # Try to find participants.tsv and read info
        participants_tsv = self._find_participants_tsv(filepath)
        subject_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Build eegunity_description with required fields
        # TUH doesn't have standard BIDS participants.tsv with age/sex
        # Use unknown for required fields if not found
        eegunity_desc = {
            "age": subject_info.get('age', 'unknown'),
            "sex": subject_info.get('sex', 'unknown').lower() if subject_info.get('sex') else 'unknown',
            "amplifier": subject_info.get('amplifier', 'unknown'),
            "cap": subject_info.get('cap', 'unknown'),
            "handedness": subject_info.get('handedness', 'unknown'),
        }
        
        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in subject_info:
                eegunity_desc[field] = subject_info[field]
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Rename channels BEFORE set_montage
        rename_map = {}
        for ch_name in raw.ch_names:
            upper_name = ch_name.upper().strip()
            # Try exact match first
            if ch_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_name]
            elif upper_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[upper_name]
            else:
                # Try case-insensitive partial match
                for key, val in self.CHANNEL_RENAME_MAP.items():
                    if key.upper() == upper_name:
                        rename_map[ch_name] = val
                        break
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known non-EEG channels
        eeg_channels = [ch for ch in raw.ch_names if ch not in 
                       ['EKG1', 'EKG2', 'EKG', 'EMG', 'EOG', 'ECG', 'PHOTIC', 
                        'IBI', 'BURSTS', 'SUPPR', 'SP1', 'SP2', 'EDF_ANNOTATIONS',
                        'A1', 'A2', 'T1', 'T2']]
        
        ch_types = {}
        for ch in raw.ch_names:
            if ch in ['EKG1', 'EKG2', 'EKG', 'ECG']:
                ch_types[ch] = 'ecg'
            elif ch == 'EMG':
                ch_types[ch] = 'emg'
            elif ch == 'EOG':
                ch_types[ch] = 'eog'
            elif ch in ['PHOTIC', 'IBI', 'BURSTS', 'SUPPR', 'SP1', 'SP2', 'EDF_ANNOTATIONS']:
                ch_types[ch] = 'misc'
            elif ch in ['A1', 'A2', 'T1', 'T2']:
                # These are sometimes used as reference, keep as eeg or misc
                ch_types[ch] = 'eeg'
            else:
                ch_types[ch] = 'eeg'
        
        raw.set_channel_types(ch_types)
        
        # Set montage for EEG channels
        try:
            montage = self._get_standard_1020_montage()
            # Only set montage for channels that exist in the montage
            montage_chs = set(montage.ch_names)
            raw_eeg_chs = [ch for ch in raw.ch_names if ch in montage_chs]
            if raw_eeg_chs:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        
        # Create seizure_label derived misc channel
        sfreq = raw.info['sfreq']
        n_times = raw.n_times
        
        # Find and parse seizure annotations
        seizures = self._find_seizure_annotations(filepath, n_times, sfreq)
        
        # Create binary seizure label channel
        seizure_data = np.zeros((1, n_times), dtype=np.float64)
        
        for start_sample, end_sample in seizures:
            seizure_data[0, start_sample:end_sample] = 1.0
        
        # Create info for seizure_label channel
        seizure_info = mne.create_info(
            ch_names=['seizure_label'],
            sfreq=sfreq,
            ch_types=['misc']
        )
        
        # Create RawArray for seizure_label
        seizure_raw = mne.io.RawArray(seizure_data, seizure_info, verbose=False)
        
        # Add seizure_label channel to raw
        raw.add_channels([seizure_raw], force_update_info=True)
        
        # Ensure seizure_label is set as misc type
        raw.set_channel_types({'seizure_label': 'misc'})
        
        return raw


KERNEL = TuhEegSeizureKernel()