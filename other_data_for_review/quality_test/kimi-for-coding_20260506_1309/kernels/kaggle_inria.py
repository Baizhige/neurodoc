import json
import os
import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd


class KaggleINRIAKernel:
    KERNEL_ID = "kaggle_inria"
    HANDLES_UNAVAILABLE = True

    # Channel names from CSV headers: standard 10-20 extended cap
    # Source: raw CSV files; inferred by LLM, needs human review
    # Annotator: LLM; Date: 2026-04-08
    _EXPECTED_CHANNELS = [
        'Fp1', 'Fp2', 'AF7', 'AF3', 'AF4', 'AF8',
        'F7', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 'F8',
        'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8',
        'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
        'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8',
        'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8',
        'PO7', 'PO3', 'POz', 'PO4', 'PO8',
        'O1', 'Oz', 'O2'
    ]

    # Sampling rate from paper: 512 Hz
    # Source: paper_10_1007_978_3_319_24574_4_28.pdf (INRIA BCI Challenge)
    # Annotator: LLM; Date: 2026-04-08; inferred by LLM, needs human review
    _SFREQ = 512.0

    def _get_file_path(self, row):
        """Extract file path from row object."""
        if isinstance(row, (str, Path)):
            return str(row)
        fp = row.get("File Path") if hasattr(row, "get") else getattr(row, "File Path", None)
        if fp is None and hasattr(row, "__getitem__"):
            try:
                fp = row["File Path"]
            except (KeyError, TypeError):
                pass
        return str(fp) if fp is not None else None

    def _parse_subject_session(self, filepath):
        """Parse subject and session from filename like Data_S26_Sess05.csv."""
        fname = os.path.basename(filepath)
        m = re.search(r'Data_S(\d+)_Sess(\d+)', fname)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    def _find_events_tsv(self, csv_path):
        """Find sibling events.tsv file if it exists."""
        base = str(csv_path).replace('.csv', '')
        for suffix in ['_events.tsv', '.tsv', '_events.csv']:
            candidate = base + suffix
            if os.path.exists(candidate):
                return candidate
        # Check parent directory for any events file
        parent = Path(csv_path).parent
        stem = Path(csv_path).stem
        for f in parent.glob(f"{stem}*events*"):
            return str(f)
        return None

    def _find_participants_tsv(self, csv_path):
        """Find participants.tsv in parent directories."""
        p = Path(csv_path).parent
        for _ in range(5):
            candidate = p / "participants.tsv"
            if candidate.exists():
                return str(candidate)
            p = p.parent
        return None

    def _read_events(self, csv_path):
        """Read events from sibling events file if available."""
        events_tsv = self._find_events_tsv(csv_path)
        if events_tsv is None:
            return None
        try:
            if events_tsv.endswith('.csv'):
                df = pd.read_csv(events_tsv)
            else:
                df = pd.read_csv(events_tsv, sep='\t')
            return df
        except Exception:
            return None

    def _read_participants(self, csv_path):
        """Read participants.tsv if available."""
        ppt_tsv = self._find_participants_tsv(csv_path)
        if ppt_tsv is None:
            return None
        try:
            return pd.read_csv(ppt_tsv, sep='\t')
        except Exception:
            return None

    def _get_subject_info(self, csv_path):
        """Get subject info from participants.tsv or infer from filename."""
        subj, sess = self._parse_subject_session(csv_path)
        info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }
        # Try to read participants.tsv
        ppt = self._read_participants(csv_path)
        if ppt is not None and subj is not None:
            # Look for subject column
            subj_col = None
            for col in ppt.columns:
                if col.lower() in ['subject', 'participant_id', 'participant', 'subj', 'sub']:
                    subj_col = col
                    break
            if subj_col is not None:
                # Match subject - may be "S26", "26", "sub-26", etc.
                for _, row in ppt.iterrows():
                    val = str(row[subj_col])
                    if str(subj) in val.replace('S', '').replace('sub-', '').replace('sub', ''):
                        for key in ['age', 'sex', 'gender', 'handedness', 'hand', 'amplifier', 'cap', 'captype']:
                            if key in ppt.columns:
                                val2 = row[key]
                                if pd.isna(val2):
                                    continue
                                val2 = str(val2).strip()
                                if key in ['sex', 'gender']:
                                    v = val2.lower()
                                    if v in ['m', 'male', '1']:
                                        info['sex'] = 'male'
                                    elif v in ['f', 'female', '2']:
                                        info['sex'] = 'female'
                                elif key == 'age':
                                    info['age'] = val2
                                elif key in ['handedness', 'hand']:
                                    info['handedness'] = val2.lower()
                                elif key == 'amplifier':
                                    info['amplifier'] = val2
                                elif key in ['cap', 'captype']:
                                    info['cap'] = val2
                        break
        # Dataset-specific defaults from literature
        # Source: INRIA BCI Challenge papers; inferred by LLM, needs human review
        # Annotator: LLM; Date: 2026-04-08
        if info['cap'] == 'unknown':
            info['cap'] = 'extended 10-20 (61 channels)'  # inferred by LLM, needs human review
        if info['amplifier'] == 'unknown':
            info['amplifier'] = 'BrainAmp MR plus (Brain Products)'  # inferred by LLM, needs human review
        return info, subj, sess

    def load(self, row):
        """Load CSV data into MNE Raw object."""
        filepath = self._get_file_path(row)
        if filepath is None:
            raise ValueError("Could not determine file path from row")

        # Read CSV
        df = pd.read_csv(filepath)

        # Time column should be first
        if 'Time' in df.columns:
            times = df['Time'].values
            ch_names = [c for c in df.columns if c != 'Time']
            data = df[ch_names].values.T
        else:
            # Assume first column is time
            times = df.iloc[:, 0].values
            ch_names = list(df.columns[1:])
            data = df.iloc[:, 1:].values.T

        # Determine sampling rate from time differences
        if len(times) > 1:
            dt = np.median(np.diff(times))
            sfreq = 1.0 / dt if dt > 0 else self._SFREQ
        else:
            sfreq = self._SFREQ

        # Create MNE info
        info = mne.create_info(
            ch_names=ch_names,
            sfreq=sfreq,
            ch_types='eeg'
        )

        # Create Raw object
        raw = mne.io.RawArray(data, info)

        # Set original description
        raw.info["description"] = json.dumps({
            "original_description": "",
            "eegunity_description": {}
        })

        return raw

    def _build_annotations_from_events(self, raw, csv_path):
        """Build annotations from events sidecar if available."""
        events_df = self._read_events(csv_path)
        if events_df is None or len(events_df) == 0:
            return

        # Determine onset and description columns
        onset_col = None
        desc_col = None
        duration_col = None

        for col in events_df.columns:
            cl = col.lower()
            if cl in ['onset', 'time', 'timestamp', 'sample', 'latency']:
                onset_col = col
            elif cl in ['trial_type', 'event', 'label', 'type', 'value', 'description', 'code']:
                desc_col = col
            elif cl in ['duration', 'dur', 'length']:
                duration_col = col

        if onset_col is None:
            # Try first numeric column for onset
            for col in events_df.columns:
                if pd.api.types.is_numeric_dtype(events_df[col]):
                    onset_col = col
                    break

        if desc_col is None:
            # Use second column or any non-numeric
            for col in events_df.columns:
                if col != onset_col:
                    desc_col = col
                    break

        if onset_col is None or desc_col is None:
            return

        onsets = events_df[onset_col].values.astype(float)
        # Convert samples to seconds if needed
        if np.max(onsets) > raw.n_times:
            # Likely in samples
            onsets = onsets / raw.info['sfreq']
        elif np.max(onsets) > 1000 and raw.times[-1] < 1000:
            # Likely in milliseconds
            onsets = onsets / 1000.0

        descriptions = events_df[desc_col].astype(str).values

        if duration_col is not None:
            durations = events_df[duration_col].values.astype(float)
            # Same unit conversion
            if np.max(durations) > raw.n_times / raw.info['sfreq'] * 2:
                durations = durations / raw.info['sfreq']
            elif np.max(durations) > 1000:
                durations = durations / 1000.0
        else:
            durations = np.zeros(len(onsets))

        # Ensure no negative onsets
        onsets = np.maximum(onsets, 0)

        # Create annotations
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions
        )
        raw.set_annotations(annot)

    def apply(self, udataset, raw, row):
        filepath = self._get_file_path(row)
        subj, sess = self._parse_subject_session(filepath)

        # Get subject info
        info, _, _ = self._get_subject_info(filepath)

        # If raw was not fully loaded (e.g., passed from EEGUnity), ensure data is loaded
        if not hasattr(raw, '_data') or raw._data is None:
            raw.load_data()

        # Rename channels to standard names if needed
        # The CSV files already have standard names, but ensure consistency
        current_names = raw.ch_names
        rename_map = {}
        for i, name in enumerate(current_names):
            clean = name.strip()
            if clean != name:
                rename_map[name] = clean

        # Handle any duplicate names after cleaning
        if rename_map:
            # Check for duplicates
            target_names = [rename_map.get(n, n) for n in current_names]
            seen = set()
            for i, tn in enumerate(target_names):
                if tn in seen:
                    # Append suffix
                    j = 1
                    new_name = f"{tn}_{j}"
                    while new_name in seen:
                        j += 1
                        new_name = f"{tn}_{j}"
                    orig = current_names[i]
                    rename_map[orig] = new_name
                seen.add(rename_map.get(current_names[i], current_names[i]))

            if rename_map:
                raw.rename_channels(rename_map, allow_duplicates=True)

        # Set channel types to EEG
        eeg_picks = [n for n in raw.ch_names if n.upper() not in ['TIME', 'TIMESTAMP', 'SAMPLE', 'MARKER', 'STI', 'STATUS']]
        ch_type_map = {n: 'eeg' for n in eeg_picks}
        raw.set_channel_types(ch_type_map)

        # Set montage for EEG channels
        try:
            raw.set_montage('standard_1020', on_missing='ignore')
        except Exception:
            pass  # Some channels may not be in standard_1020

        # Build annotations from events sidecar if raw lacks sufficient annotations
        if raw.annotations is None or len(raw.annotations) == 0:
            self._build_annotations_from_events(raw, filepath)

        # Set description
        original_desc = raw.info.get("description", "")
        try:
            orig_parsed = json.loads(original_desc) if original_desc else {}
            if isinstance(orig_parsed, dict):
                orig_desc = orig_parsed.get("original_description", str(original_desc))
            else:
                orig_desc = str(original_desc)
        except json.JSONDecodeError:
            orig_desc = str(original_desc)

        eegunity_desc = {
            "age": str(info['age']) if info['age'] != 'unknown' else 'unknown',
            "sex": info['sex'],
            "amplifier": info['amplifier'],
            "cap": info['cap'],
            "handedness": info['handedness'],
        }

        raw.info["description"] = json.dumps({
            "original_description": orig_desc,
            "eegunity_description": eegunity_desc
        })

        return raw


KERNEL = KaggleINRIAKernel()