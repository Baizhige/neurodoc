import json
import os
import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd


class FigshareStrokeKernel:
    KERNEL_ID = "figshare_stroke"
    HANDLES_UNAVAILABLE = False

    # inferred by LLM, needs human review
    # Channel mapping derived from paper: 10.1016/j.compbiomed.2025.111285
    # 32 EEG channels + 1 ECG channel based on standard 10-20 system
    # Date: 2026-04-08
    _EDF_CHANNEL_MAP = {
        # Standard EDF channel names observed in figshare stroke dataset
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F7': 'F7',
        'F3': 'F3',
        'Fz': 'Fz',
        'F4': 'F4',
        'F8': 'F8',
        'T3': 'T7',
        'C3': 'C3',
        'Cz': 'Cz',
        'C4': 'C4',
        'T4': 'T8',
        'T5': 'P7',
        'P3': 'P3',
        'Pz': 'Pz',
        'P4': 'P4',
        'T6': 'P8',
        'O1': 'O1',
        'O2': 'O2',
        'A1': 'A1',
        'A2': 'A2',
        'ECG': 'ECG',
        # Alternative naming patterns
        'FP1': 'Fp1',
        'FP2': 'Fp2',
        'FZ': 'Fz',
        'CZ': 'Cz',
        'PZ': 'Pz',
        'T7': 'T7',
        'T8': 'T8',
        'P7': 'P7',
        'P8': 'P8',
        'A1-A2': 'A1',
        'A2-A1': 'A2',
    }

    # Standard 10-20 montage channels for this dataset
    # inferred by LLM, needs human review
    _STANDARD_CHANNELS = [
        'Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8',
        'T7', 'C3', 'Cz', 'C4', 'T8',
        'P7', 'P3', 'Pz', 'P4', 'P8',
        'O1', 'O2'
    ]

    def __init__(self):
        self._participants_df = None
        self._participants_path = None

    def _get_file_path(self, row):
        """Extract file path from row or string."""
        if hasattr(row, 'get'):
            fp = row.get("File Path")
            if fp is not None:
                return str(fp)
        if isinstance(row, (str, Path)):
            return str(row)
        return str(row)

    def _find_participants_tsv(self, file_path):
        """Find participants.tsv relative to the data file."""
        path = Path(file_path)
        # Search upward for BIDS-like structure
        for parent in [path.parent, path.parent.parent, path.parent.parent.parent]:
            candidates = [
                parent / "participants.tsv",
                parent.parent / "participants.tsv",
            ]
            for cand in candidates:
                if cand.exists():
                    return str(cand)
        # Also check dataset root patterns
        parts = path.parts
        for i, part in enumerate(parts):
            if 'figshare' in part.lower() or 'stroke' in part.lower():
                root = Path(*parts[:i+1])
                candidates = [
                    root / "participants.tsv",
                    root / "edffile" / "participants.tsv",
                ]
                for cand in candidates:
                    if cand.exists():
                        return str(cand)
        return None

    def _load_participants(self, file_path):
        """Lazy-load participants.tsv."""
        if self._participants_df is not None:
            return self._participants_df

        ppath = self._find_participants_tsv(file_path)
        self._participants_path = ppath

        if ppath and os.path.exists(ppath):
            try:
                self._participants_df = pd.read_csv(ppath, sep='\t')
            except Exception:
                self._participants_df = pd.DataFrame()
        else:
            self._participants_df = pd.DataFrame()

        return self._participants_df

    def _get_subject_id(self, file_path):
        """Extract subject ID from file path."""
        fname = os.path.basename(file_path)
        # Pattern: sub-XX_task-..._eeg.edf
        m = re.search(r'(sub-\d+)', fname)
        if m:
            return m.group(1)
        # Alternative: just digits
        m = re.search(r'sub[_-]?(\d+)', fname)
        if m:
            return f"sub-{int(m.group(1)):02d}"
        return None

    def _get_participant_info(self, file_path):
        """Get participant info from participants.tsv."""
        df = self._load_participants(file_path)
        sub_id = self._get_subject_id(file_path)

        if df.empty or sub_id is None:
            return {}

        # Try to match participant_id column
        for col in df.columns:
            if col.lower() in ('participant_id', 'subject', 'subject_id', 'sub_id'):
                row = df[df[col] == sub_id]
                if len(row) == 1:
                    return row.iloc[0].to_dict()

        # Try matching with 'sub-' prefix variations
        for col in df.columns:
            if col.lower() in ('participant_id', 'subject', 'subject_id', 'sub_id'):
                row = df[df[col].astype(str).str.replace('sub-', '').str.zfill(2) == sub_id.replace('sub-', '').zfill(2)]
                if len(row) == 1:
                    return row.iloc[0].to_dict()

        return {}

    def _canonicalize_sex(self, val):
        """Canonicalize sex to lowercase standard."""
        if pd.isna(val) or val is None:
            return "unknown"
        s = str(val).strip().lower()
        if s in ('m', 'male', '1'):
            return "male"
        if s in ('f', 'female', '0', '2'):
            return "female"
        return "unknown"

    def _canonicalize_age(self, val):
        """Canonicalize age to string."""
        if pd.isna(val) or val is None:
            return "unknown"
        # Handle ranges like "22-45"
        s = str(val).strip()
        if '-' in s and s.replace('-', '').replace('.', '').isdigit():
            return s
        try:
            return str(int(float(s)))
        except (ValueError, TypeError):
            return "unknown"

    def _build_eegunity_description(self, file_path, original_desc=""):
        """Build eegunity_description with all required fields."""
        info = self._get_participant_info(file_path)
        sub_id = self._get_subject_id(file_path)

        # Canonical fields with defaults
        age = self._canonicalize_age(info.get('Age', 'unknown'))
        sex = self._canonicalize_sex(info.get('Gender', info.get('Sex', 'unknown')))
        handedness = str(info.get('Handedness', 'unknown')).strip().lower()
        if handedness in ('', 'nan', 'none', 'null'):
            handedness = 'unknown'

        # Device info - not available in this dataset
        # inferred by LLM, needs human review
        amplifier = "unknown"  # no device info in dataset files
        cap = "standard_1020"  # inferred by LLM, needs human review

        # Required info fields from participants.tsv
        required_fields = ['Age', 'Duration', 'Gender', 'Handedness', 'IsFirstTime',
                          'MBI', 'NIHSS', 'ParalysisSide', 'StrokeLocation', 'mRS']

        extra_info = {}
        for field in required_fields:
            if field in info and not pd.isna(info[field]):
                extra_info[field] = str(info[field])
            else:
                extra_info[field] = "unknown"

        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        # Add all required info fields
        eegunity_desc.update(extra_info)

        return {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        }

    def _clean_channel_names(self, raw):
        """Clean and standardize channel names."""
        ch_names = raw.ch_names.copy()
        new_names = []
        seen = set()

        for ch in ch_names:
            # Strip whitespace and common prefixes
            clean = ch.strip()
            # Remove common EDF prefix patterns
            clean = re.sub(r'^EEG\s+', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'^EEG-', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'^POL\s+', '', clean, flags=re.IGNORECASE)

            # Apply known mappings
            if clean in self._EDF_CHANNEL_MAP:
                clean = self._EDF_CHANNEL_MAP[clean]

            # Handle duplicates by adding suffix
            base = clean
            suffix = 1
            while clean in seen:
                clean = f"{base}-{suffix}"
                suffix += 1
            seen.add(clean)
            new_names.append(clean)

        # Check for duplicates in original that need allow_duplicates
        if len(set(ch_names)) != len(ch_names):
            raw.rename_channels({old: new for old, new in zip(ch_names, new_names)},
                              allow_duplicates=True)
        else:
            raw.rename_channels({old: new for old, new in zip(ch_names, new_names)})

        return raw

    def _set_channel_types(self, raw):
        """Set appropriate channel types."""
        ch_types = {}
        for ch in raw.ch_names:
            ch_upper = ch.upper()
            if ch_upper in ('ECG', 'EKG'):
                ch_types[ch] = 'ecg'
            elif ch_upper in ('A1', 'A2', 'M1', 'M2', 'REF', 'REFERENCE'):
                ch_types[ch] = 'misc'
            elif ch_upper.startswith('EOG') or ch_upper in ('HEO', 'VEO', 'HEOG', 'VEOG'):
                ch_types[ch] = 'eog'
            # EEG channels are default, don't need to set

        if ch_types:
            raw.set_channel_types(ch_types)

        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage."""
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass  # Montage not critical
        return raw

    def _find_events_tsv(self, file_path):
        """Find events.tsv sidecar for the given file."""
        path = Path(file_path)
        fname = path.stem  # e.g., sub-07_task-motor-imagery_eeg

        # Check same directory
        events_file = path.parent / f"{fname}_events.tsv"
        if events_file.exists():
            return str(events_file)

        # Check BIDS patterns
        events_file = path.parent / f"{fname.replace('_eeg', '')}_events.tsv"
        if events_file.exists():
            return str(events_file)

        # Check parent directories
        for parent in [path.parent, path.parent.parent]:
            for f in parent.glob("*events.tsv"):
                # Match by subject
                if self._get_subject_id(file_path) in f.name:
                    return str(f)

        return None

    def _add_annotations_from_events_tsv(self, raw, file_path):
        """Add annotations from events.tsv if present."""
        events_path = self._find_events_tsv(file_path)

        if not events_path or not os.path.exists(events_path):
            return raw

        try:
            events_df = pd.read_csv(events_path, sep='\t')

            if events_df.empty:
                return raw

            # Determine columns
            onset_col = None
            for col in ['onset', 'start_time', 'sample']:
                if col in events_df.columns:
                    onset_col = col
                    break

            duration_col = None
            for col in ['duration', 'stop_time', 'end_time']:
                if col in events_df.columns:
                    duration_col = col
                    break

            desc_col = None
            for col in ['trial_type', 'value', 'event_type', 'stim_type', 'condition', 'description']:
                if col in events_df.columns:
                    desc_col = col
                    break

            if onset_col is None or desc_col is None:
                return raw

            onsets = []
            durations = []
            descriptions = []

            for _, row in events_df.iterrows():
                onset = row[onset_col]
                if pd.isna(onset):
                    continue

                # Convert sample to time if needed
                if onset_col == 'sample':
                    onset = float(onset) / raw.info['sfreq']

                onsets.append(float(onset))

                if duration_col and not pd.isna(row.get(duration_col, np.nan)):
                    dur = float(row[duration_col])
                    if onset_col == 'sample' and duration_col == 'sample':
                        dur = dur / raw.info['sfreq']
                    durations.append(dur)
                else:
                    durations.append(0.0)

                desc = str(row[desc_col])
                descriptions.append(desc)

            if onsets:
                # Combine with existing annotations
                existing = raw.annotations
                if existing:
                    all_onsets = list(existing.onset) + onsets
                    all_durations = list(existing.duration) + durations
                    all_descriptions = list(existing.description) + descriptions
                    # Sort by onset
                    sorted_idx = np.argsort(all_onsets)
                    all_onsets = [all_onsets[i] for i in sorted_idx]
                    all_durations = [all_durations[i] for i in sorted_idx]
                    all_descriptions = [all_descriptions[i] for i in sorted_idx]
                    raw.set_annotations(mne.Annotations(
                        onset=all_onsets,
                        duration=all_durations,
                        description=all_descriptions
                    ))
                else:
                    raw.set_annotations(mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions
                    ))

        except Exception:
            pass

        return raw

    def _ensure_annotations(self, raw, file_path):
        """Ensure annotations exist, deriving from sidecars if needed."""
        # EDF files in this dataset may have annotations in header or may need events.tsv
        has_annotations = (raw.annotations is not None and
                          len(raw.annotations) > 0)

        if not has_annotations:
            raw = self._add_annotations_from_events_tsv(raw, file_path)

        return raw

    def load(self, row):
        """Load EDF file and return MNE Raw object."""
        file_path = self._get_file_path(row)

        # Load EDF
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        return raw

    def apply(self, udataset, raw, row):
        file_path = self._get_file_path(row)

        # Ensure data is loaded
        if not raw.preload:
            raw.load_data()

        # Clean channel names
        raw = self._clean_channel_names(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Set montage
        raw = self._set_montage(raw)

        # Ensure annotations from sidecars if raw lacks them
        raw = self._ensure_annotations(raw, file_path)

        # Build and set description
        original_desc = raw.info.get("description", "") or ""
        desc_dict = self._build_eegunity_description(file_path, original_desc)
        raw.info["description"] = json.dumps(desc_dict)

        return raw


KERNEL = FigshareStrokeKernel()