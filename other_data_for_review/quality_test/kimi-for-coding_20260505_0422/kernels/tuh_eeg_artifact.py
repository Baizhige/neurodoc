import json
import os
import numpy as np
import pandas as pd
import mne


class TuhEegArtifactKernel:
    KERNEL_ID = "tuh_eeg_artifact"
    KERNEL_NAME = "TUH EEG Artifact Corpus"
    KERNEL_DESCRIPTION = "EEG kernel for TUH EEG Artifact Corpus with artifact annotations"
    KERNEL_CITATION = "10.1109/SPMB50085.2020.9353647"
    KERNEL_LICENSE = "ODC-BY"
    KERNEL_URL = "https://isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml"

    required_event_ids = ['bckg', 'elec', 'elpp', 'eyem', 'eyem_elec', 'eyem_musc', 'musc', 'musc_elec']
    required_info_fields = []
    required_native_misc = []
    derived_misc_channels = ['artifact_label']

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
        'EEG T1-REF': 'FT7',
        'EEG T2-REF': 'FT8',
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
        'EEG T1-LE': 'FT7',
        'EEG T2-LE': 'FT8',
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
        'T1': 'FT7',
        'T2': 'FT8',
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
        'T1-REF': 'FT7',
        'T2-REF': 'FT8',
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
        'T1-LE': 'FT7',
        'T2-LE': 'FT8',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('tuh_eeg_artifact') or part.startswith('TUH_EEG_ARTIFACT'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        # Another fallback: look for participants.tsv going up
        current = os.path.dirname(filepath)
        for _ in range(6):
            if current == os.sep or not current:
                break
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
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

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
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find events.tsv file corresponding to EEG file."""
        # Try BIDS sidecar naming
        base = os.path.splitext(eeg_file_path)[0]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try in same directory
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)
        events_tsv = os.path.join(dir_name, base_name + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Look for any events.tsv in same directory
        for f in os.listdir(dir_name):
            if f.endswith('_events.tsv'):
                return os.path.join(dir_name, f)
        
        return None

    def _find_artifact_csv(self, eeg_file_path):
        """Find artifact annotation CSV file corresponding to EEG file."""
        # TUH artifact corpus has .csv files with artifact annotations
        base = os.path.splitext(eeg_file_path)[0]
        
        # Try various naming conventions
        candidates = [
            base + '.csv',
            base + '_bi.csv',
            base + '_artifact.csv',
        ]
        
        # Also check in the same directory for any CSV with similar name
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)
        
        for cand in candidates:
            if os.path.exists(cand):
                return cand
        
        # Look for CSV files in same directory with matching base name
        for f in os.listdir(dir_name):
            if f.endswith('.csv') and base_name in f:
                return os.path.join(dir_name, f)
        
        return None

    def _read_artifact_csv(self, csv_path):
        """Read artifact annotations from TUH CSV file."""
        if csv_path is None or not os.path.exists(csv_path):
            return None
        
        try:
            # TUH artifact CSVs have specific format with header rows
            # Skip comment lines starting with # and find the actual data
            with open(csv_path, 'r') as f:
                lines = f.readlines()
            
            # Find where actual data starts (after header comments)
            data_lines = []
            header = None
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if header is None:
                    header = line.split(',')
                else:
                    data_lines.append(line.split(','))
            
            if not data_lines or header is None:
                return None
            
            df = pd.DataFrame(data_lines, columns=header)
            
            # TUH artifact CSV typically has: channel, start_time, stop_time, label, confidence
            # We need to map to annotations
            annotations = []
            for _, row in df.iterrows():
                try:
                    onset = float(row.get('start_time', row.get('start', 0)))
                    duration = float(row.get('stop_time', row.get('stop', 0))) - onset
                    label = str(row.get('label', row.get('artifact', 'unknown'))).strip().lower()
                    
                    # Map to standard event IDs - keep literal labels, no remapping per HC-5
                    # Only normalize case/whitespace, preserve the actual label strings
                    annotations.append({
                        'onset': onset,
                        'duration': max(duration, 0.001),  # Ensure positive duration
                        'description': label,
                    })
                except (ValueError, KeyError):
                    continue
            
            return annotations if annotations else None
            
        except Exception:
            return None

    def _read_events_tsv(self, events_tsv):
        """Read events from BIDS events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            events = []
            for _, row in df.iterrows():
                try:
                    onset = float(row['onset'])
                    duration = float(row.get('duration', 0))
                    # Use trial_type first as it contains the meaningful trigger labels
                    # for TUH artifact dataset. Do not remap per HC-5.
                    if 'trial_type' in row:
                        description = str(row['trial_type'])
                    elif 'value' in row:
                        description = str(row['value'])
                    elif 'label' in row:
                        description = str(row['label'])
                    else:
                        description = str(row.iloc[0])
                    events.append({
                        'onset': onset,
                        'duration': duration,
                        'description': description,
                    })
                except (ValueError, KeyError):
                    continue
            return events if events else None
        except Exception:
            return None

    def _create_annotations(self, events_list, orig_time=None):
        """Create MNE Annotations from events list."""
        if not events_list:
            return None
        
        onsets = []
        durations = []
        descriptions = []
        
        for event in events_list:
            onsets.append(event['onset'])
            durations.append(event.get('duration', 0))
            descriptions.append(event['description'])
        
        return mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
            orig_time=orig_time
        )

    def load(self, filepath):
        """Load EEG file and return MNE Raw object with annotations."""
        # Determine file type and load accordingly
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.set':
            raw = mne.io.read_raw_eeglab(filepath, preload=False)
        elif ext in ['.edf', '.bdf']:
            raw = mne.io.read_raw_edf(filepath, preload=False)
        elif ext in ['.fif', '.fiff']:
            raw = mne.io.read_raw_fif(filepath, preload=False)
        elif ext == '.vhdr':
            raw = mne.io.read_raw_brainvision(filepath, preload=False)
        elif ext == '.cnt':
            raw = mne.io.read_raw_cnt(filepath, preload=False)
        elif ext == '.trc':
            raw = mne.io.read_raw_trc(filepath, preload=False)
        elif ext == '.eeg':
            # Could be BrainVision or Nihon Kohden
            vhdr = filepath.replace('.eeg', '.vhdr')
            if os.path.exists(vhdr):
                raw = mne.io.read_raw_brainvision(filepath.replace('.eeg', '.vhdr'), preload=False)
            else:
                raw = mne.io.read_raw_nihon(filepath, preload=False)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        # Rename channels to standard names
        raw.rename_channels(self.CHANNEL_RENAME_MAP)
        
        # Set montage to standard 10-20
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        # Find and load events from BIDS events.tsv (primary source)
        events_tsv = self._find_events_tsv(filepath)
        events = self._read_events_tsv(events_tsv)
        
        # Fallback to artifact CSV if no BIDS events
        if events is None:
            artifact_csv = self._find_artifact_csv(filepath)
            events = self._read_artifact_csv(artifact_csv)
        
        # Create and set annotations on the raw object
        if events:
            annotations = self._create_annotations(events, orig_time=raw.annotations.orig_time if raw.annotations else None)
            if annotations is not None:
                # Set annotations on raw - this is the critical step that was missing
                raw.set_annotations(annotations)
        
        # Get subject info
        subject_id = self._get_subject_id_from_path(filepath)
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        participants_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Build eegunity_description
        description = {
            'kernel_id': self.KERNEL_ID,
            'kernel_name': self.KERNEL_NAME,
            'filepath': filepath,
            'subject_id': subject_id,
            'sampling_frequency': raw.info['sfreq'],
            'n_channels': raw.info['nchan'],
            'n_times': raw.n_times,
            'duration_sec': raw.times[-1] if len(raw.times) > 0 else 0,
            'channel_names': raw.ch_names,
            'events_count': len(events) if events else 0,
            'events_descriptions': list(set([e['description'] for e in events])) if events else [],
            'bids_root': bids_root,
            'participants_info': participants_info,
        }
        
        # Store description in raw.info['description'] as JSON
        raw.info['description'] = json.dumps(description)
        
        return raw

    def get_event_id(self, raw):
        """Get event ID mapping from raw object annotations."""
        events, event_id = mne.events_from_annotations(raw)
        return event_id

    def get_events(self, raw):
        """Get events array from raw object."""
        events, event_id = mne.events_from_annotations(raw)
        return events


KERNEL = TuhEegArtifactKernel()