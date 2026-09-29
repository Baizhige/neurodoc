import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class TuhEegSlowingKernel:
    KERNEL_ID = "tuh_eeg_slowing"
    KERNEL_NAME = "TUH EEG Slowing Corpus"
    KERNEL_DESCRIPTION = "Temple University Hospital EEG Slowing Corpus v2.0.1 — clinical EEG with slowing annotations"
    KERNEL_CITATION = "10.3389/fnins.2016.00196"
    KERNEL_LICENSE = "TUH EEG Restricted License"
    KERNEL_URL = "https://isip.piconepress.com/projects/tuh_eeg/"

    # No required event IDs — this is clinical EEG with variable annotations
    required_event_ids = []
    # TUH dataset has age, sex in participants.tsv; we also need amplifier, cap, handedness
    required_info_fields = ['age', 'sex', 'amplifier', 'cap', 'handedness']
    # Native misc channels that may appear in TUH files (non-EEG channels)
    required_native_misc = []
    # Derived misc channels — we will create these from events.tsv if present
    derived_misc_channels = []

    # TUH channel name standardization: map various spellings to standard 10-20
    CHANNEL_RENAME_MAP = {
        # Standard 10-20 channels (pass through)
        'FP1': 'Fp1', 'FP2': 'Fp2', 'FPZ': 'Fpz',
        'FZ': 'Fz', 'CZ': 'Cz', 'PZ': 'Pz', 'OZ': 'Oz',
        'F3': 'F3', 'F4': 'F4', 'F7': 'F7', 'F8': 'F8',
        'T3': 'T7', 'T4': 'T8', 'T5': 'P7', 'T6': 'P8',
        'C3': 'C3', 'C4': 'C4', 'P3': 'P3', 'P4': 'P4',
        'O1': 'O1', 'O2': 'O2',
        'A1': 'A1', 'A2': 'A2',
        # Extended 10-10
        'AF7': 'AF7', 'AF8': 'AF8', 'AF3': 'AF3', 'AF4': 'AF4', 'AFZ': 'AFz',
        'F1': 'F1', 'F2': 'F2', 'F5': 'F5', 'F6': 'F6', 'F9': 'F9', 'F10': 'F10',
        'FT7': 'FT7', 'FT8': 'FT8', 'FT9': 'FT9', 'FT10': 'FT10',
        'FC1': 'FC1', 'FC2': 'FC2', 'FC3': 'FC3', 'FC4': 'FC4', 'FC5': 'FC5', 'FC6': 'FC6', 'FCZ': 'FCz',
        'C1': 'C1', 'C2': 'C2', 'C5': 'C5', 'C6': 'C6',
        'TP7': 'TP7', 'TP8': 'TP8', 'TP9': 'TP9', 'TP10': 'TP10',
        'CP1': 'CP1', 'CP2': 'CP2', 'CP3': 'CP3', 'CP4': 'CP4', 'CP5': 'CP5', 'CP6': 'CP6', 'CPZ': 'CPz',
        'P1': 'P1', 'P2': 'P2', 'P5': 'P5', 'P6': 'P6', 'P9': 'P9', 'P10': 'P10',
        'PO7': 'PO7', 'PO8': 'PO8', 'PO3': 'PO3', 'PO4': 'PO4', 'POZ': 'POz',
        'I1': 'I1', 'I2': 'I2', 'IZ': 'Iz',
        # ECG/EKG
        'EKG': 'ECG', 'ECG': 'ECG',
        # EMG
        'EMG': 'EMG',
        # Misc channels (will be set to misc type)
        'PHOTIC': 'PHOTIC', 'PHOTIC PH': 'PHOTIC PH', 'PHOTIC-REF': 'PHOTIC',
        'BURSTS': 'BURSTS', 'SUPPR': 'SUPPR',
        'ROC': 'ROC', 'LOC': 'LOC',
        'RESP1': 'RESP1', 'RESP2': 'RESP2', 'RESP': 'RESP',
        'DC1': 'DC1', 'DC2': 'DC2', 'DC3': 'DC3', 'DC4': 'DC4',
        'DC5': 'DC5', 'DC6': 'DC6', 'DC7': 'DC7', 'DC8': 'DC8',
        'DC1-DC': 'DC1-DC', 'DC2-DC': 'DC2-DC', 'DC3-DC': 'DC3-DC', 'DC4-DC': 'DC4-DC',
        'DC5-DC': 'DC5-DC', 'DC6-DC': 'DC6-DC', 'DC7-DC': 'DC7-DC', 'DC8-DC': 'DC8-DC',
        'SP1': 'SP1', 'SP2': 'SP2', 'SP1/SP2': 'SP1/SP2',
        'REF': 'REF', 'AUX': 'AUX',
    }

    # Channels that should be forced to 'misc' type
    MISC_CHANNEL_PATTERNS = [
        'PHOTIC', 'BURSTS', 'SUPPR', 'ROC', 'LOC',
        'RESP', 'DC', 'SP', 'REF', 'AUX',
        'EKG', 'ECG', 'EMG',
    ]

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # Look for version directory pattern (v2.0.1, etc.)
        for i, part in enumerate(parts):
            if re.match(r'v\d+\.\d+\.\d+', part):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'edf' directory
        for i, part in enumerate(parts):
            if part == 'edf':
                return os.sep.join(parts[:i+1])
        # Fallback: look for subject pattern (aaaaXXXX)
        for i, part in enumerate(parts):
            if re.match(r'^[a-z]{4}[a-z]{4}$', part):
                return os.sep.join(parts[:i])
        return None

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from TUH file path."""
        # TUH format: aaaaXXXX_sNNN_tNNN.edf
        basename = os.path.basename(filepath)
        # Match subject code: first 8 chars before _s
        match = re.match(r'^([a-z]{8})_s\d+_t\d+', basename)
        if match:
            return match.group(1)
        # Fallback: look for 8-letter code in path
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if re.match(r'^[a-z]{8}$', part):
                return part
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        # TUH has _participants.tsv at root (with underscore)
        for name in ['_participants.tsv', 'participants.tsv']:
            p_tsv = os.path.join(bids_root, name)
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
                if col.lower() in ['participant_id', 'subject', 'subject_id', 'patient_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            # Match subject — TUH uses 8-letter codes
            subj_rows = df[df[subj_col].astype(str).str.lower() == subject_id.lower()]
            if len(subj_rows) == 0:
                # Try with sub- prefix
                subj_rows = df[df[subj_col].astype(str).str.lower() == f"sub-{subject_id.lower()}"]
            if len(subj_rows) == 0:
                # Try partial match
                subj_rows = df[df[subj_col].astype(str).str.contains(subject_id, case=False, na=False)]

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
        """Find events.tsv sidecar for an EEG file."""
        # TUH events are in .rec files or .lbl files, not standard BIDS events.tsv
        # Check for various event file patterns
        base = eeg_file_path
        # Remove extension
        for ext in ['.edf', '.EDF', '.set', '.SET', '.fif', '.FIF']:
            if base.endswith(ext):
                base = base[:-len(ext)]
                break

        # Check for events.tsv (BIDS style)
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv

        # Check for .rec file (TUH event file)
        rec_file = base + '.rec'
        if os.path.exists(rec_file):
            return rec_file

        # Check for .lbl file (TUH label file)
        lbl_file = base + '.lbl'
        if os.path.exists(lbl_file):
            return lbl_file

        # Check in parent directory for session-level events
        parent = os.path.dirname(eeg_file_path)
        for fname in os.listdir(parent) if os.path.isdir(parent) else []:
            if fname.endswith(('.rec', '.lbl', '_events.tsv')):
                return os.path.join(parent, fname)

        return None

    def _read_events_tsv(self, events_tsv):
        """Read events from file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None

        try:
            if events_tsv.endswith('.rec'):
                # TUH .rec file format: space-separated, may have header
                with open(events_tsv, 'r') as f:
                    lines = f.readlines()

                events = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            onset = float(parts[0])
                            duration = float(parts[1]) - float(parts[0]) if len(parts) > 1 else 0.0
                            description = ' '.join(parts[2:]) if len(parts) > 2 else 'unknown'
                            events.append({
                                'onset': onset,
                                'duration': max(duration, 0.0),
                                'description': description
                            })
                        except ValueError:
                            continue
                return pd.DataFrame(events) if events else None

            elif events_tsv.endswith('.lbl'):
                # TUH .lbl file format
                with open(events_tsv, 'r') as f:
                    lines = f.readlines()

                events = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            onset = float(parts[0])
                            duration = float(parts[1]) - onset if len(parts) > 1 else 0.0
                            description = ' '.join(parts[2:]) if len(parts) > 2 else 'unknown'
                            events.append({
                                'onset': onset,
                                'duration': max(duration, 0.0),
                                'description': description
                            })
                        except ValueError:
                            continue
                return pd.DataFrame(events) if events else None

            else:
                # Standard BIDS events.tsv
                df = pd.read_csv(events_tsv, sep='\t')
                # Ensure required columns
                if 'onset' not in df.columns:
                    return None
                if 'duration' not in df.columns:
                    df['duration'] = 0.0
                if 'trial_type' in df.columns and 'description' not in df.columns:
                    df['description'] = df['trial_type']
                elif 'value' in df.columns and 'description' not in df.columns:
                    df['description'] = df['value'].astype(str)
                elif 'description' not in df.columns:
                    df['description'] = 'unknown'
                return df

        except Exception:
            return None

    def _standardize_channel_names(self, raw):
        """Standardize channel names to 10-20 convention."""
        raw = raw.copy()
        ch_names = raw.ch_names
        rename_map = {}

        for ch in ch_names:
            ch_upper = ch.upper().strip()
            # Direct match in map
            if ch_upper in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch_upper]
            else:
                # Try to clean up common patterns
                cleaned = ch_upper.replace('-REF', '').replace('-LE', '').replace('-AR', '')
                cleaned = cleaned.replace(' ', '').replace('-', '')
                if cleaned in self.CHANNEL_RENAME_MAP:
                    rename_map[ch] = self.CHANNEL_RENAME_MAP[cleaned]
                # Check for ECG/EKG variants
                elif 'EKG' in ch_upper or 'ECG' in ch_upper:
                    rename_map[ch] = 'ECG'
                # Keep original if no match
                else:
                    rename_map[ch] = ch

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _set_channel_types(self, raw):
        """Set appropriate channel types for TUH channels."""
        raw = raw.copy()
        ch_names = raw.ch_names

        # Build type mapping
        ch_types = {}
        for ch in ch_names:
            ch_upper = ch.upper()

            # ECG
            if ch_upper == 'ECG' or 'EKG' in ch_upper:
                ch_types[ch] = 'ecg'
            # EMG
            elif ch_upper == 'EMG':
                ch_types[ch] = 'emg'
            # Misc patterns
            elif any(pat in ch_upper for pat in self.MISC_CHANNEL_PATTERNS):
                ch_types[ch] = 'misc'
            # Default to eeg for everything else (standard 10-20)
            else:
                # Check if it looks like an EEG channel
                eeg_pattern = re.match(r'^[A-Z]{1,2}\d{1,2}$|^[A-Z]{1,2}Z$', ch_upper)
                if eeg_pattern or ch_upper in ['A1', 'A2', 'CZ', 'FZ', 'PZ', 'OZ', 'FPZ']:
                    ch_types[ch] = 'eeg'
                else:
                    # Unknown, mark as misc to be safe
                    ch_types[ch] = 'misc'

        # Apply types
        try:
            raw.set_channel_types(ch_types)
        except Exception:
            # If some channels fail, try individually
            for ch, typ in ch_types.items():
                try:
                    raw.set_channel_types({ch: typ})
                except Exception:
                    pass

        return raw

    def _infer_sex(self, info):
        """Infer sex from available info."""
        if 'sex' in info and info['sex'].lower() not in ['unknown', 'nan', '']:
            val = info['sex'].lower()
            if val in ['m', 'male']:
                return 'male'
            elif val in ['f', 'female']:
                return 'female'
        # inferred by LLM, needs human review
        return 'unknown'  # inferred by LLM, needs human review

    def _infer_age(self, info):
        """Infer age from available info."""
        if 'age' in info and info['age'].lower() not in ['unknown', 'nan', '']:
            # Extract numeric age
            match = re.search(r'(\d+)', str(info['age']))
            if match:
                return match.group(1)
        # inferred by LLM, needs human review
        return 'unknown'  # inferred by LLM, needs human review

    def _infer_amplifier(self, info):
        """Infer amplifier from available info or path."""
        if 'amplifier' in info and info['amplifier'].lower() not in ['unknown', 'nan', '']:
            return info['amplifier']
        # inferred by LLM, needs human review
        return 'unknown'  # inferred by LLM, needs human review

    def _infer_cap(self, info):
        """Infer cap/montage from available info or path."""
        if 'cap' in info and info['cap'].lower() not in ['unknown', 'nan', '']:
            return info['cap']
        # inferred by LLM, needs human review
        return 'unknown'  # inferred by LLM, needs human review

    def _infer_handedness(self, info):
        """Infer handedness from available info."""
        if 'handedness' in info and info['handedness'].lower() not in ['unknown', 'nan', '']:
            return info['handedness']
        # inferred by LLM, needs human review
        return 'unknown'  # inferred by LLM, needs human review

    def _add_annotations_from_events(self, raw, events_df):
        """Add annotations from events dataframe to raw."""
        if events_df is None or len(events_df) == 0:
            return raw

        raw = raw.copy()
        onsets = []
        durations = []
        descriptions = []

        for _, row in events_df.iterrows():
            onset = float(row['onset'])
            duration = float(row.get('duration', 0.0)) if pd.notna(row.get('duration', 0.0)) else 0.0
            description = str(row.get('description', row.get('trial_type', 'unknown')))

            # Validate onset is within data range
            if onset >= 0 and onset < raw.times[-1]:
                onsets.append(onset)
                durations.append(max(duration, 0.0))
                descriptions.append(description)

        if len(onsets) > 0:
            # Remove existing annotations to avoid duplicates
            raw.set_annotations(None)
            annot = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions
            )
            raw.set_annotations(annot)

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Make a copy to avoid modifying original
        raw = raw.copy()

        # Get file path
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)

        # Find BIDS root and read participants info
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_id = self._get_subject_id_from_path(filepath)

        # Read participant info
        info = {}
        if subject_id:
            info = self._read_participants_info(participants_tsv, subject_id)

        # Standardize channel names BEFORE set_montage
        raw = self._standardize_channel_names(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Try to set montage for EEG channels
        try:
            # Get EEG channel positions
            eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
            if len(eeg_picks) > 0:
                # Try standard 10-20 montage
                montage = mne.channels.make_standard_montage('standard_1020')
                # Only set for channels that exist in montage
                available_chs = set(raw.ch_names) & set(montage.ch_names)
                if len(available_chs) > 0:
                    raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass

        # Handle events/annotations
        events_tsv = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv)

        # EDF format may not carry its own triggers — derive from events file if present
        if events_df is not None and len(events_df) > 0:
            raw = self._add_annotations_from_events(raw, events_df)

        # Build description with required fields
        original_desc = raw.info.get('description', '')
        if isinstance(original_desc, bytes):
            try:
                original_desc = original_desc.decode('utf-8')
            except Exception:
                original_desc = str(original_desc)

        # Extract info fields with inference
        age = self._infer_age(info)
        sex = self._infer_sex(info)
        amplifier = self._infer_amplifier(info)
        cap = self._infer_cap(info)
        handedness = self._infer_handedness(info)

        # Build eegunity_description with all required fields
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }

        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in info:
                val = info[field]
                eegunity_desc[field] = str(val) if val is not None else "unknown"

        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })

        return raw


KERNEL = TuhEegSlowingKernel()