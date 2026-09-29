import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class OtherMigrainedbKernel:
    KERNEL_ID = "other_migrainedb"
    KERNEL_NAME = "MigraineDB - Multimodal Evoked Potentials in Migraine"
    KERNEL_DESCRIPTION = "EEG kernel for migraine study with SSVEP, SSAEP, and resting-state recordings"
    KERNEL_CITATION = "10.1093/braincomms/fcab061"
    KERNEL_LICENSE = "unknown"
    KERNEL_URL = "https://openneuro.org/datasets/other_migrainedb"

    required_event_ids = ['event_1', 'event_11', 'event_2', 'event_22']
    required_info_fields = ['age', 'sex', 'handedness']
    required_native_misc = []
    derived_misc_channels = []

    # Standard 10-20 channel names for Biosemi 64-channel system
    CHANNEL_RENAME_MAP = {
        'A1': 'Fp1', 'A2': 'AF7', 'A3': 'AF3', 'A4': 'F1', 'A5': 'F3', 'A6': 'F5', 'A7': 'F7', 'A8': 'FT7',
        'A9': 'FC5', 'A10': 'FC3', 'A11': 'FC1', 'A12': 'C1', 'A13': 'C3', 'A14': 'C5', 'A15': 'T7', 'A16': 'TP7',
        'A17': 'CP5', 'A18': 'CP3', 'A19': 'CP1', 'A20': 'P1', 'A21': 'P3', 'A22': 'P5', 'A23': 'P7', 'A24': 'P9',
        'A25': 'PO7', 'A26': 'PO3', 'A27': 'O1', 'A28': 'Iz', 'A29': 'Oz', 'A30': 'POz', 'A31': 'Pz', 'A32': 'CPz',
        'B1': 'Fpz', 'B2': 'Fp2', 'B3': 'AF8', 'B4': 'AF4', 'B5': 'AFz', 'B6': 'Fz', 'B7': 'F2', 'B8': 'F4',
        'B9': 'F6', 'B10': 'F8', 'B11': 'FT8', 'B12': 'FC6', 'B13': 'FC4', 'B14': 'FC2', 'B15': 'FCz', 'B16': 'Cz',
        'B17': 'C2', 'B18': 'C4', 'B19': 'C6', 'B20': 'T8', 'B21': 'TP8', 'B22': 'CP6', 'B23': 'CP4', 'B24': 'CP2',
        'B25': 'P2', 'B26': 'P4', 'B27': 'P6', 'B28': 'P8', 'B29': 'P10', 'B30': 'PO8', 'B31': 'PO4', 'B32': 'O2',
        # Status channel for triggers
        'Status': 'Status',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'migrainedb' in part.lower() or 'other_migrainedb' in part.lower():
                # The root is the directory containing subject folders
                return os.sep.join(parts[:i+1])
        # Fallback: look for subject pattern like C3, M8, P15
        for i, part in enumerate(parts):
            if re.match(r'^[CMP]\d+$', part):
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

            # Match subject - handle various formats
            subject_variants = [subject_id]
            if subject_id.startswith('sub-'):
                subject_variants.append(subject_id[4:])
            else:
                subject_variants.append('sub-' + subject_id)

            subj_rows = df[df[subj_col].isin(subject_variants)]
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
            # Match patterns like C3, M8, P15, C18, etc.
            if re.match(r'^[CMP]\d+$', part):
                return part
        # Fallback: extract from filename
        basename = os.path.basename(filepath)
        match = re.match(r'^_?([CMP]\d+)_.*\.bdf$', basename, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find events.tsv file corresponding to EEG file."""
        # For this dataset, events are embedded in BDF Status channel
        # No separate events.tsv files exist
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

    def _extract_events_from_status(self, raw):
        """Extract events from Biosemi Status channel."""
        # Biosemi BDF files store triggers in the 'Status' channel
        # The Status channel contains trigger values as bit patterns
        
        if 'Status' not in raw.ch_names:
            # Try to find status channel with different naming
            status_candidates = [ch for ch in raw.ch_names if 'status' in ch.lower() or 'trigger' in ch.lower()]
            if not status_candidates:
                return None, None
            status_ch = status_candidates[0]
        else:
            status_ch = 'Status'

        # Get status channel data
        status_idx = raw.ch_names.index(status_ch)
        status_data = raw.get_data(picks=[status_idx])[0]

        # Biosemi trigger extraction: lower 8 bits contain trigger value
        # Convert to integers and extract changes
        status_int = np.array(status_data, dtype=np.int64)
        
        # Biosemi Status channel: triggers are in lower bits
        # Mask to get 8-bit trigger values
        triggers = status_int & 0xFF
        
        # Find transitions (where trigger value changes)
        diff = np.diff(triggers, prepend=triggers[0])
        event_samples = np.where(diff != 0)[0]
        event_values = triggers[event_samples]
        
        # Filter out zero values (no trigger) and keep only rising edges to unique non-zero values
        # Group consecutive same values and take the first occurrence
        valid_events = []
        for i, (sample, value) in enumerate(zip(event_samples, event_values)):
            if value != 0:
                # Check if this is a new value or same as previous
                if i == 0 or value != event_values[i-1]:
                    valid_events.append((sample, 0, int(value)))
        
        if len(valid_events) == 0:
            return None, None
            
        events = np.array(valid_events, dtype=int)
        
        # Create event_id mapping based on observed values
        # Map to standard event names
        unique_values = sorted(set(events[:, 2]))
        event_id = {}
        for val in unique_values:
            event_id[f'event_{val}'] = val
            
        return events, event_id

    def _create_annotations_from_events(self, raw, events, event_id):
        """Create MNE Annotations from events array."""
        if events is None or len(events) == 0:
            return
            
        # Invert event_id for lookup
        id_to_name = {v: k for k, v in event_id.items()}
        
        onsets = []
        durations = []
        descriptions = []
        
        sfreq = raw.info['sfreq']
        for event in events:
            sample, _, value = event
            onset = sample / sfreq
            onsets.append(onset)
            durations.append(0.0)  # Instant events
            name = id_to_name.get(value, f'event_{value}')
            descriptions.append(name)
            
        # Remove existing annotations first
        raw.set_annotations(None)
        
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions
        )
        raw.set_annotations(annot)

    def _get_recording_type(self, filepath):
        """Determine recording type from filename."""
        basename = os.path.basename(filepath).lower()
        if 'ssvep' in basename:
            return 'SSVEP'
        elif 'ssaep' in basename:
            return 'SSAEP'
        elif 'resting' in basename or 'rest' in basename:
            return 'resting'
        return 'unknown'

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        
        # Get BIDS root and subject info
        bids_root = self._find_bids_root(filepath)
        subject_id = self._get_subject_id_from_path(filepath)
        
        # Read participants info
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Get original description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        # Build eegunity_description with required fields
        eegunity_desc = {
            "age": subject_info.get('age', "unknown"),
            "sex": subject_info.get('sex', "unknown").lower() if subject_info.get('sex') else "unknown",
            "amplifier": "Biosemi ActiveTwo",  # inferred by LLM, needs human review
            "cap": "Biosemi 64-channel cap",  # inferred by LLM, needs human review
            "handedness": subject_info.get('handedness', "unknown"),
        }
        
        # Add any extra required info fields
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in subject_info:
                eegunity_desc[field] = subject_info[field]
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Rename channels BEFORE set_montage
        # First, handle the Biosemi channel naming
        rename_map = {}
        for ch in raw.ch_names:
            if ch in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
            elif ch.startswith('A') or ch.startswith('B'):
                # Try to map any remaining A/B channels
                if ch in self.CHANNEL_RENAME_MAP:
                    rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types - mark Status as misc
        ch_types = {}
        for ch in raw.ch_names:
            if ch == 'Status':
                ch_types[ch] = 'misc'
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage for EEG channels
        eeg_chs = [ch for ch in raw.ch_names if ch not in ['Status', 'EXG1', 'EXG2', 'EXG3', 'EXG4', 'EXG5', 'EXG6', 'EXG7', 'EXG8']]
        if len(eeg_chs) > 0:
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                raw.set_montage(montage, match_case=False, on_missing='warn')
            except Exception:
                pass
        
        # Extract events from Status channel for Biosemi BDF
        # This is critical - BDF files store triggers in Status channel
        events, event_id = self._extract_events_from_status(raw)
        
        # Create annotations from extracted events
        if events is not None and len(events) > 0:
            self._create_annotations_from_events(raw, events, event_id)
        
        # Handle derived misc channels if needed
        # No derived misc channels required for this dataset
        
        return raw


KERNEL = OtherMigrainedbKernel()