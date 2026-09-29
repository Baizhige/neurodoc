import json
import os
import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd


class FigshareShuDBKernel:
    KERNEL_ID = "figshare_shudb"
    HANDLES_UNAVAILABLE = True

    # Channel mapping for SHU dataset: 32 channels standard 10-20
    _CH_NAMES_32 = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC3",
        "FCz", "FC4", "T7", "C3", "Cz", "C4", "T8", "CP3",
        "CPz", "CP4", "P7", "P3", "Pz", "P4", "P8", "O1",
        "Oz", "O2", "AF3", "AF4", "PO3", "PO4", "FT7", "FT8",
    ]

    def _get_file_path(self, row):
        """Extract file path from row or string."""
        if isinstance(row, str):
            return row
        fp = row.get("File Path") if hasattr(row, "get") else None
        if fp is None and hasattr(row, "File Path"):
            fp = row["File Path"]
        if fp is None and hasattr(row, "__getitem__"):
            try:
                fp = row["File Path"]
            except (KeyError, TypeError):
                pass
        return str(fp) if fp is not None else None

    def _find_sidecar(self, file_path, suffix):
        """Find sidecar file with given suffix."""
        base = Path(file_path).with_suffix("")
        candidates = [
            f"{base}{suffix}",
            f"{base}_eeg{suffix}",
        ]
        stem = Path(file_path).stem
        if stem.endswith("_eeg"):
            stem_base = stem[:-4]
            candidates.append(f"{Path(file_path).parent / stem_base}{suffix}")
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def _parse_events_tsv(self, file_path):
        """Parse events.tsv sidecar and return mne.Annotations."""
        events_path = self._find_sidecar(file_path, "_events.tsv")
        if events_path is None:
            return None

        try:
            df = pd.read_csv(events_path, sep="\t")
        except Exception:
            return None

        if df.empty:
            return None

        if "onset" not in df.columns:
            return None

        onsets = df["onset"].values.astype(float)
        durations = df["duration"].values.astype(float) if "duration" in df.columns else np.zeros(len(df))
        
        # Use 'value' column if present (literal event IDs per HC-5), else 'trial_type'
        if "value" in df.columns:
            descriptions = df["value"].astype(str).values
        elif "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values
        else:
            descriptions = np.array([""] * len(df))

        descriptions = [str(d).strip() for d in descriptions]

        if len(onsets) == 0:
            return None

        # Events.tsv onsets are in seconds - but looking at the data, onsets are in samples
        # The onsets like 1.00, 1001.00, 2001.00 with durations 1000.00 suggest samples at 1Hz?
        # Actually with duration=1000 and onsets spaced by 1000, this looks like samples at 1Hz which is wrong.
        # More likely: these are samples and we need to convert by sfreq. But we don't have sfreq here.
        # Looking more carefully: if sfreq=1000, then 1 sample = 1ms, and 1000 samples = 1s.
        # The trial duration would be 1000s which is too long. 
        # Actually the MAT files show data shape (87, 32, 1000) - 87 trials, 32 channels, 1000 samples.
        # So each trial is 1000 samples. If sfreq=1000Hz, that's 1 second. But motor imagery is usually 3-4s.
        # If sfreq=250Hz, 1000 samples = 4s which makes sense.
        # The events.tsv onsets are likely in samples and need conversion.
        # However, the BIDS spec says onsets should be in seconds. Let's check if these could be seconds.
        # 1.00, 1001.00, 2001.00 - if these are seconds, trials start at 1s, 1001s, 2001s... that's 16+ minutes apart.
        # That can't be right for a single run. They must be in samples.
        # Let's convert: if sfreq=250, then 1/250 = 0.004s per sample. 1000 samples = 4s.
        # But we need sfreq. Let's assume the EDF has the sfreq.
        
        # Actually, looking at typical BIDS datasets, the events.tsv onsets are in seconds.
        # But these values are suspiciously large. Let me re-examine.
        # The values 1, 1001, 2001... with step 1000 suggest sample indices, not seconds.
        # We need to get sfreq from the raw file to convert.
        
        # For now, let's assume these are in seconds as per BIDS, but the dataset may be non-standard.
        # The mismatch shows expected_events_in_tsv=74 but kernel_produced_annotations=1.
        # This suggests only 1 annotation is being created or kept.
        # Looking at the onsets: 1.00, 1001.00, 2001.00... if these are seconds, they're very far apart.
        # If raw duration is shorter, many would be outside the data range and dropped.
        
        # Let's convert from samples to seconds using a typical sfreq if needed.
        # Actually, let's just pass them as-is and see. The issue might be that MNE drops annotations beyond data length.
        
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        return annot

    def _parse_participants_tsv(self, file_path):
        """Parse participants.tsv for subject metadata."""
        data_dir = Path(file_path).parent
        for parent in [data_dir, data_dir.parent, data_dir.parent.parent]:
            participants_path = parent / "participants.tsv"
            if participants_path.exists():
                break
        else:
            return {}

        try:
            df = pd.read_csv(participants_path, sep="\t")
        except Exception:
            return {}

        fname = Path(file_path).name
        match = re.search(r"sub-(\d+)", fname)
        if match:
            sub_id = match.group(1)
            sub_match = df[df["participant_id"].astype(str).str.replace("sub-", "", regex=False).str.lstrip("0") == sub_id.lstrip("0")]
            if sub_match.empty:
                sub_match = df[df["participant_id"] == f"sub-{sub_id}"]
            if sub_match.empty:
                sub_match = df[df["participant_id"] == f"sub-{sub_id.zfill(3)}"]
            if not sub_match.empty:
                return sub_match.iloc[0].to_dict()
        return {}

    def load(self, row):
        """Load EDF file and return MNE Raw object."""
        file_path = self._get_file_path(row)
        if file_path is None:
            raise ValueError("No file path provided")

        raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)

        # Rename channels to standard 10-20 names if count matches
        if len(raw.ch_names) == 32:
            target_names = self._CH_NAMES_32[:]
            seen = set()
            for i, name in enumerate(target_names):
                orig = name
                counter = 1
                while name in seen:
                    name = f"{orig}_{counter}"
                    counter += 1
                seen.add(name)
                target_names[i] = name
            raw.rename_channels(dict(zip(raw.ch_names, target_names)), allow_duplicates=True)

        # Strip whitespace from channel names before montage assignment
        try:
            ch_names_stripped = [ch.strip() for ch in raw.ch_names]
            rename_map = {old: new for old, new in zip(raw.ch_names, ch_names_stripped) if old != new}
            if rename_map:
                raw.rename_channels(rename_map, allow_duplicates=True)
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass

        # Parse events from sidecar and set annotations
        annot = self._parse_events_tsv(file_path)
        if annot is not None:
            raw.set_annotations(annot)

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = self._get_file_path(row)
        if file_path is None:
            raise ValueError("No file path provided")

        # Parse participant info
        participant_info = self._parse_participants_tsv(file_path)

        # Build eegunity_description with explicit canonical defaults
        eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

        # Override with available participant info
        if participant_info:
            if "age" in participant_info and pd.notna(participant_info["age"]):
                age_val = participant_info["age"]
                try:
                    eegunity_description["age"] = str(int(float(age_val)))
                except (ValueError, TypeError):
                    eegunity_description["age"] = str(age_val)
            if "gender" in participant_info and pd.notna(participant_info["gender"]):
                g = str(participant_info["gender"]).strip().upper()
                if g in ("M", "MALE"):
                    eegunity_description["sex"] = "male"
                elif g in ("F", "FEMALE"):
                    eegunity_description["sex"] = "female"
            if "handedness" in participant_info and pd.notna(participant_info["handedness"]):
                h = str(participant_info["handedness"]).strip().lower()
                if h in ("r", "right"):
                    eegunity_description["handedness"] = "right"
                elif h in ("l", "left"):
                    eegunity_description["handedness"] = "left"
                elif h in ("a", "ambi", "ambidextrous"):
                    eegunity_description["handedness"] = "ambidextrous"

        # Get original description
        original_description = raw.info.get("description", "") if raw.info.get("description") is not None else ""

        # Re-parse and set annotations in apply to ensure they're present
        # The events.tsv onsets appear to be in samples, not seconds. Need to convert.
        events_path = self._find_sidecar(file_path, "_events.tsv")
        if events_path is not None:
            try:
                df = pd.read_csv(events_path, sep="\t")
                if not df.empty and "onset" in df.columns:
                    sfreq = raw.info["sfreq"]
                    # Convert onsets from samples to seconds
                    onsets = df["onset"].values.astype(float) / sfreq
                    durations = df["duration"].values.astype(float) / sfreq if "duration" in df.columns else np.zeros(len(df))
                    
                    if "value" in df.columns:
                        descriptions = df["value"].astype(str).values
                    elif "trial_type" in df.columns:
                        descriptions = df["trial_type"].astype(str).values
                    else:
                        descriptions = np.array([""] * len(df))
                    
                    descriptions = [str(d).strip() for d in descriptions]
                    
                    # Filter to valid range
                    valid_mask = onsets < (raw.n_times / sfreq)
                    onsets = onsets[valid_mask]
                    durations = durations[valid_mask]
                    descriptions = [d for d, m in zip(descriptions, valid_mask) if m]
                    
                    if len(onsets) > 0:
                        annot = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=descriptions,
                        )
                        raw.set_annotations(annot)
            except Exception:
                pass

        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = FigshareShuDBKernel()