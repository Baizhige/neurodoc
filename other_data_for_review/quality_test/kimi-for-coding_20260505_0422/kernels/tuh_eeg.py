import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class TuhEegKernel:
    KERNEL_ID = "tuh_eeg"
    KERNEL_NAME = "TUH EEG Seizure Corpus (TUSZ)"
    KERNEL_DESCRIPTION = "Temple University Hospital EEG Seizure Corpus for seizure detection"
    KERNEL_CITATION = "10.3389/fnins.2016.00196"
    KERNEL_LICENSE = "TUH EEG Usage Agreement"
    KERNEL_URL = "https://www.isip.piconepress.com/projects/tuh_eeg/"

    required_event_ids = ['seizure']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = []

    # TUH EEG uses standard 10-20 channel names, but may have variations
    # Common TUH channel names to standardize
    CHANNEL_RENAME_MAP = {
        # Standard 10-20
        'FP1': 'Fp1', 'FP2': 'Fp2', 'FPZ': 'Fpz',
        'FZ': 'Fz', 'CZ': 'Cz', 'PZ': 'Pz', 'OZ': 'Oz',
        'CPZ': 'CPz', 'FCZ': 'FCz',
        'T3': 'T7', 'T4': 'T8', 'T5': 'P7', 'T6': 'P8',
        'A1': 'A1', 'A2': 'A2',
        'M1': 'M1', 'M2': 'M2',
        # Keep standard names as-is
        'Fp1': 'Fp1', 'Fp2': 'Fp2', 'Fpz': 'Fpz',
        'F7': 'F7', 'F8': 'F8', 'F3': 'F3', 'F4': 'F4', 'Fz': 'Fz',
        'T7': 'T7', 'T8': 'T8',
        'C3': 'C3', 'C4': 'C4', 'Cz': 'Cz',
        'P7': 'P7', 'P8': 'P8', 'P3': 'P3', 'P4': 'P4', 'Pz': 'Pz',
        'O1': 'O1', 'O2': 'O2', 'Oz': 'Oz',
        'F9': 'F9', 'F10': 'F10',
        'P9': 'P9', 'P10': 'P10',
        'FT9': 'FT9', 'FT10': 'FT10',
        'TP9': 'TP9', 'TP10': 'TP10',
        'PO9': 'PO9', 'PO10': 'PO10',
        'AF7': 'AF7', 'AF8': 'AF8', 'AF3': 'AF3', 'AF4': 'AF4', 'AFz': 'AFz',
        'F5': 'F5', 'F6': 'F6', 'F1': 'F1', 'F2': 'F2',
        'FT7': 'FT7', 'FT8': 'FT8', 'FC5': 'FC5', 'FC6': 'FC6',
        'FC3': 'FC3', 'FC4': 'FC4', 'FC1': 'FC1', 'FC2': 'FC2', 'FCz': 'FCz',
        'C5': 'C5', 'C6': 'C6', 'C1': 'C1', 'C2': 'C2',
        'TP7': 'TP7', 'TP8': 'TP8', 'CP5': 'CP5', 'CP6': 'CP6',
        'CP3': 'CP3', 'CP4': 'CP4', 'CP1': 'CP1', 'CP2': 'CP2', 'CPz': 'CPz',
        'P5': 'P5', 'P6': 'P6', 'P1': 'P1', 'P2': 'P2',
        'PO7': 'PO7', 'PO8': 'PO8', 'PO3': 'PO3', 'PO4': 'PO4', 'POz': 'POz',
        'IZ': 'Iz', 'Iz': 'Iz',
        # ECG/EMG/misc
        'ECG': 'ECG', 'EKG': 'ECG',
        'EMG': 'EMG',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # TUH is often organized with edf/ folder containing the files
        # Look for common TUH patterns
        for i, part in enumerate(parts):
            if part.lower() in ['tuh_eeg', 'tuh_eeg_seizure', 'tusz', 'v1.5.2', 'v1.5.1', 'v1.5.0']:
                # The BIDS root might be above or at this level
                candidate = os.sep.join(parts[:i+1])
                # Check for participants.tsv or typical TUH structure
                if os.path.exists(os.path.join(candidate, 'participants.tsv')):
                    return candidate
        # Fallback: look for 'sub-' pattern or go up to find participants.tsv
        for i, part in enumerate(parts):
            if part.startswith('sub-') or re.match(r'^\d{3}$', part):  # TUH uses numeric subject IDs
                return os.sep.join(parts[:i])
        # Last resort: walk up looking for participants.tsv
        current = os.path.dirname(filepath)
        while current != os.sep:
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

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from TUH file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        # TUH uses numeric subject IDs like 000, 001, etc. in paths like .../000/.../s001_2012...
        for part in parts:
            # Match 3-digit subject directory or subject prefix in filename
            if re.match(r'^\d{3}$', part):
                return part
        # Try to extract from filename like s001_2012_01_01_00_00_00.edf
        basename = os.path.basename(filepath)
        m = re.match(r'^s?(\d{3})[_\.]', basename)
        if m:
            return m.group(1)
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
                if col.lower() in ['participant_id', 'subject', 'subject_id', 'pat_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            # Match subject - try various formats
            search_ids = [subject_id]
            if subject_id and not subject_id.startswith('sub-'):
                search_ids.append('sub-' + subject_id)
            else:
                search_ids.append(subject_id.replace('sub-', '') if subject_id else '')

            for sid in search_ids:
                subj_rows = df[df[subj_col].astype(str) == str(sid)]
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

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # In BIDS, events.tsv is alongside the eeg file with same name but _events.tsv
        base = eeg_file_path
        # Remove extension
        for ext in ['.edf', '.set', '.eeg', '.fif', '.vhdr', '.vmrk', '.cnt', '.bdf']:
            if base.lower().endswith(ext):
                base = base[:-len(ext)]
                break
        
        # Try _events.tsv suffix
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try .events.tsv (some TUH versions)
        events_tsv2 = base + '.events.tsv'
        if os.path.exists(events_tsv2):
            return events_tsv2
        
        # TUH specific: look for .tse or .lbl files which contain seizure annotations
        for ext in ['.tse', '.lbl', '.bi', '.csv']:
            alt = base + ext
            if os.path.exists(alt):
                return alt
        
        # Look in parent directory for events
        parent = os.path.dirname(eeg_file_path)
        basename = os.path.basename(base)
        for fname in os.listdir(parent) if os.path.isdir(parent) else []:
            if fname.startswith(basename) and ('event' in fname.lower() or fname.endswith(('.tse', '.lbl'))):
                return os.path.join(parent, fname)
        
        return None

    def _read_tuh_seizure_annotations(self, filepath):
        """Read TUH seizure annotations from .tse or .tse_bi files."""
        annotations = []
        # Try .tse, .tse_bi, .lbl files
        base = filepath
        for ext in ['.edf', '.set', '.eeg', '.fif', '.vhdr', '.vmrk', '.cnt', '.bdf']:
            if base.lower().endswith(ext):
                base = base[:-len(ext)]
                break
        
        tse_file = base + '.tse'
        tse_bi_file = base + '.tse_bi'
        lbl_file = base + '.lbl'
        
        # Prefer .tse_bi (binary seizure/non-seizure) then .tse (multi-class)
        for ann_file in [tse_bi_file, tse_file, lbl_file]:
            if os.path.exists(ann_file):
                try:
                    with open(ann_file, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#') or line.startswith('version'):
                            continue
                        
                        # Format: start_time end_time label [confidence]
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                start = float(parts[0])
                                end = float(parts[1])
                                label = parts[2].lower()
                                
                                # Map to seizure event
                                if 'seiz' in label:
                                    annotations.append({
                                        'onset': start,
                                        'duration': end - start,
                                        'description': 'seizure'
                                    })
                            except ValueError:
                                continue
                    
                    if annotations:
                        return annotations
                except Exception:
                    continue
        
        return annotations

    def _read_events_tsv(self, events_tsv):
        """Read events from TSV file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return []
        
        # Check if it's a TUH .tse file (handled separately)
        if events_tsv.endswith(('.tse', '.tse_bi', '.lbl')):
            return self._read_tuh_seizure_annotations(events_tsv)
        
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            events = []
            
            # Standard BIDS events.tsv columns
            onset_col = 'onset' if 'onset' in df.columns else None
            duration_col = 'duration' if 'duration' in df.columns else None
            trial_type_col = 'trial_type' if 'trial_type' in df.columns else None
            value_col = 'value' if 'value' in df.columns else None
            
            # Fallbacks
            if onset_col is None:
                for col in df.columns:
                    if 'onset' in col.lower() or 'start' in col.lower():
                        onset_col = col
                        break
            
            if duration_col is None:
                for col in df.columns:
                    if 'duration' in col.lower() or 'length' in col.lower():
                        duration_col = col
                        break
            
            if trial_type_col is None:
                for col in df.columns:
                    if 'type' in col.lower() or 'label' in col.lower() or 'event' in col.lower():
                        trial_type_col = col
                        break
            
            if onset_col is None:
                return []
            
            for _, row in df.iterrows():
                try:
                    onset = float(row[onset_col])
                    duration = float(row[duration_col]) if duration_col and pd.notna(row.get(duration_col, np.nan)) else 0.0
                    
                    # Determine description
                    desc = None
                    if trial_type_col and pd.notna(row.get(trial_type_col, np.nan)):
                        desc = str(row[trial_type_col])
                    elif value_col and pd.notna(row.get(value_col, np.nan)):
                        desc = str(row[value_col])
                    else:
                        desc = 'unknown'
                    
                    # Map seizure-related labels
                    desc_lower = desc.lower()
                    if 'seiz' in desc_lower:
                        desc = 'seizure'
                    
                    events.append({
                        'onset': onset,
                        'duration': duration,
                        'description': desc
                    })
                except (ValueError, TypeError):
                    continue
            
            return events
        except Exception:
            return []

    def _standardize_sex(self, sex_str):
        """Standardize sex to lowercase male/female/unknown."""
        if sex_str is None or str(sex_str).lower() in ['unknown', 'n/a', 'na', '', ' ']:
            return "unknown"
        s = str(sex_str).lower().strip()
        if s in ['m', 'male', '1']:
            return "male"
        if s in ['f', 'female', '2', 'w']:
            return "female"
        if 'm' in s:
            return "male"
        if 'f' in s:
            return "female"
        return "unknown"  # inferred by LLM, needs human review

    def _standardize_age(self, age_val):
        """Standardize age to string."""
        if age_val is None or str(age_val).lower() in ['unknown', 'n/a', 'na', '', ' ']:
            return "unknown"
        try:
            # Handle "Y" suffix like "25Y" in TUH
            age_str = str(age_val).strip().upper().replace('Y', '')
            age_float = float(age_str)
            return str(int(age_float))
        except (ValueError, TypeError):
            return "unknown"

    def _extract_age_sex_from_path_or_file(self, filepath):
        """Try to extract age/sex from TUH path or file content if participants.tsv fails."""
        info = {}
        
        # TUH paths often contain age/sex in directory structure or filename
        # e.g., .../000/00000258/s001_2012_01_01/00_00_00.edf
        # or filename may encode info
        
        # Try to find .txt or .csv sidecars with patient info
        base = filepath
        for ext in ['.edf', '.set', '.eeg', '.fif', '.vhdr', '.vmrk', '.cnt', '.bdf']:
            if base.lower().endswith(ext):
                base = base[:-len(ext)]
                break
        
        for sidecar_ext in ['.txt', '.csv', '.json']:
            sidecar = base + sidecar_ext
            if os.path.exists(sidecar):
                try:
                    with open(sidecar, 'r') as f:
                        content = f.read()
                    # Look for age/sex patterns
                    age_match = re.search(r'age[:\s]+(\d+)', content, re.IGNORECASE)
                    if age_match:
                        info['age'] = age_match.group(1)
                    sex_match = re.search(r'sex[:\s]+([MF])', content, re.IGNORECASE)
                    if sex_match:
                        info['sex'] = 'male' if sex_match.group(1).upper() == 'M' else 'female'
                except Exception:
                    pass
        
        return info

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        filepath = row['file_path']
        
        # Find BIDS root and participants info
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_id = self._get_subject_id_from_path(filepath)
        
        # Read participants info
        info = self._read_participants_info(participants_tsv, subject_id)
        
        # Fallback: try to extract from path/file
        if not info or all(v == 'unknown' for v in info.values()):
            fallback_info = self._extract_age_sex_from_path_or_file(filepath)
            for k, v in fallback_info.items():
                if k not in info or info[k] == 'unknown':
                    info[k] = v
        
        # Standardize
        age = self._standardize_age(info.get('age', 'unknown'))
        sex = self._standardize_sex(info.get('sex', 'unknown'))
        
        # Extract additional required info fields
        extra_info = {}
        for field in self.required_info_fields:
            if field not in ['age', 'sex']:
                val = info.get(field, 'unknown')
                extra_info[field] = str(val) if val is not None else 'unknown'
        
        # Determine amplifier and cap from TUH context
        # TUH uses various amplifiers, typically Nihon Kohden or Nicolet
        # inferred by LLM, needs human review
        amplifier = "unknown"  # inferred by LLM, needs human review
        cap = "standard_1020"  # inferred by LLM, needs human review
        
        # Try to infer from file content or path
        path_lower = filepath.lower()
        if 'nihon' in path_lower or 'nk' in path_lower:
            amplifier = "Nihon Kohden"  # inferred by LLM, needs human review
        elif 'nicolet' in path_lower:
            amplifier = "Nicolet"  # inferred by LLM, needs human review
        
        # Determine handedness
        handedness = "unknown"  # inferred by LLM, needs human review
        
        # Build description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        eegunity_desc.update(extra_info)
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })
        
        # Channel renaming BEFORE set_montage
        # Get current channel names and rename to standard 10-20
        current_names = raw.ch_names
        rename_map = {}
        for ch_name in current_names:
            ch_upper = ch_name.upper()
            if ch_name in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_name]
            elif ch_upper in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_upper]
            # Also check if already standard (case-insensitive match)
            elif ch_name in self.CHANNEL_RENAME_MAP.values():
                pass  # Already standard
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if possible
        try:
            # Try standard 10-20 montage
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only set channels that exist in both
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = list(raw_chs & montage_chs)
            if common_chs:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        
        # Handle events/annotations for seizure detection
        # TUH .edf files typically do NOT carry annotations internally
        # We must derive from sidecar .tse/.tse_bi files
        
        # Check if raw already has annotations with seizure events
        has_seizure_annotations = False
        if raw.annotations and len(raw.annotations) > 0:
            for desc in raw.annotations.description:
                if 'seiz' in desc.lower():
                    has_seizure_annotations = True
                    break
        
        # If no seizure annotations in raw, read from sidecar files
        if not has_seizure_annotations:
            # Try to find and read TUH annotation files
            tse_annotations = self._read_tuh_seizure_annotations(filepath)
            
            if tse_annotations:
                # Create MNE Annotations
                onsets = [a['onset'] for a in tse_annotations]
                durations = [a['duration'] for a in tse_annotations]
                descriptions = [a['description'] for a in tse_annotations]
                
                # Remove any existing annotations to avoid duplicates
                if raw.annotations:
                    raw.set_annotations(None)
                
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions
                )
                raw.set_annotations(annotations)
            else:
                # Try standard events.tsv
                events_tsv = self._find_events_tsv(filepath)
                events = self._read_events_tsv(events_tsv)
                
                if events:
                    onsets = [e['onset'] for e in events]
                    durations = [e['duration'] for e in events]
                    descriptions = [e['description'] for e in events]
                    
                    if raw.annotations:
                        raw.set_annotations(None)
                    
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions
                    )
                    raw.set_annotations(annotations)
        
        # Ensure required event IDs exist
        # If still no seizure annotations, we can't fabricate them
        # The scan will show this file lacks seizure events
        
        # Handle required_native_misc
        for misc_ch in self.required_native_misc:
            if misc_ch in raw.ch_names:
                raw.set_channel_types({misc_ch: 'misc'})
        
        # Handle derived_misc_channels (none for this kernel)
        for derived_ch, source_field in self.derived_misc_channels.items():
            # Not implemented for TUH - would need participants.tsv column
            pass
        
        return raw


KERNEL = TuhEegKernel()