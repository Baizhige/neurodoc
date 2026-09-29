import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class OpenneuroDs002034Kernel:
    KERNEL_ID = "openneuro_ds002034"
    KERNEL_NAME = "OpenNeuro ds002034 - Covert Attention EEG"
    KERNEL_VERSION = "1.0.0"

    def __init__(self):
        pass

    def _get_bids_root(self, raw_path):
        """Extract BIDS root from raw file path."""
        parts = raw_path.split(os.sep)
        # Find 'sub-' prefix to locate BIDS root
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                return os.sep.join(parts[:i])
        # Fallback: go up until we find participants.tsv
        current = os.path.dirname(raw_path)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return os.path.dirname(os.path.dirname(raw_path))

    def _get_subject_from_row(self, row):
        """Extract subject ID from row data."""
        # Try common BIDS subject fields
        for key in ["subject", "participant_id", "sub", "Subject", "Participant"]:
            if key in row and pd.notna(row[key]):
                val = str(row[key])
                if not val.startswith("sub-"):
                    val = f"sub-{val}"
                return val
        # Try to extract from file_path if available
        if "file_path" in row and pd.notna(row["file_path"]):
            fp = str(row["file_path"])
            for part in fp.split(os.sep):
                if part.startswith("sub-"):
                    return part
        return None

    def _read_participants_tsv(self, bids_root, subject_id):
        """Read participants.tsv and return row for subject."""
        participants_path = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(participants_path):
            return {}
        
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject
        subj_col = None
        for col in df.columns:
            if col.lower() in ["participant_id", "subject", "sub"]:
                subj_col = col
                break
        if subj_col is None:
            subj_col = df.columns[0]
        
        # Normalize subject IDs for matching
        def normalize_subj(s):
            s = str(s).strip()
            if not s.startswith("sub-"):
                s = f"sub-{s}"
            return s
        
        df["_norm"] = df[subj_col].apply(normalize_subj)
        norm_target = normalize_subj(subject_id)
        matches = df[df["_norm"] == norm_target]
        if len(matches) == 0:
            return {}
        return matches.iloc[0].to_dict()

    def _get_events_tsv_path(self, raw_path):
        """Find sibling events.tsv for raw file."""
        base = raw_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.fif", "")
        events_path = base + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
        # Try alternative extensions
        for ext in ["_events.tsv"]:
            alt = base + ext
            if os.path.exists(alt):
                return alt
        return None

    def _read_events_tsv(self, events_path):
        """Read events.tsv file."""
        if events_path is None or not os.path.exists(events_path):
            return None
        return pd.read_csv(events_path, sep="\t")

    def _parse_event_value(self, val):
        """Parse event value, handling mixed types."""
        if pd.isna(val):
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

    def _create_misc_channel(self, raw, name, data_values):
        """Create a misc channel with given data values."""
        info = mne.create_info([name], raw.info["sfreq"], ch_types=["misc"])
        # Ensure data is 2D (1, n_times)
        data = np.array(data_values).reshape(1, -1)
        # Make sure length matches
        if data.shape[1] != len(raw.times):
            # Interpolate or pad
            if data.shape[1] < len(raw.times):
                # Repeat last value or pad with zeros
                pad = np.zeros((1, len(raw.times) - data.shape[1]))
                data = np.concatenate([data, pad], axis=1)
            else:
                data = data[:, :len(raw.times)]
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        raw.add_channels([misc_raw], force_update_info=True)
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle different column names
        raw_path = None
        for key in ["file_path", "filepath", "path", "filename", "FilePath", "FILE_PATH"]:
            if key in row and pd.notna(row[key]):
                raw_path = str(row[key])
                break
        
        # Fallback: try to construct from other BIDS fields
        if raw_path is None:
            # Try to build from subject, session, task, run
            sub = self._get_subject_from_row(row)
            if sub:
                bids_root = None
                # Try to find bids root from any available path info
                for key in ["bids_root", "dataset_path", "root", "base_path"]:
                    if key in row and pd.notna(row[key]):
                        bids_root = str(row[key])
                        break
                if bids_root:
                    # Construct path
                    ses = str(row.get("session", row.get("ses", "ses-01")))
                    if not ses.startswith("ses-"):
                        ses = f"ses-{ses}"
                    task = str(row.get("task", "offline"))
                    run = str(row.get("run", "01"))
                    if not run.startswith("run-"):
                        run = f"run-{run}"
                    raw_path = os.path.join(bids_root, sub, ses, "eeg", 
                                           f"{sub}_{ses}_task-{task}_{run}_eeg.edf")
                    # Try to find actual file
                    if not os.path.exists(raw_path):
                        # Search for any matching file
                        eeg_dir = os.path.join(bids_root, sub, ses, "eeg")
                        if os.path.exists(eeg_dir):
                            for f in os.listdir(eeg_dir):
                                if f.startswith(f"{sub}_{ses}") and f.endswith(".edf"):
                                    raw_path = os.path.join(eeg_dir, f)
                                    break
        
        if raw_path is None:
            raise ValueError(f"Cannot determine file path from row. Available keys: {list(row.keys())}")

        bids_root = self._get_bids_root(raw_path)
        subject_id = self._get_subject_from_row(row)

        # Read participants.tsv
        participant_info = {}
        if subject_id:
            participant_info = self._read_participants_tsv(bids_root, subject_id)

        # Extract age and sex
        age = str(participant_info.get("age", "")).strip()
        if not age or age.lower() in ["nan", "none", ""]:
            age = "unknown"  # inferred by LLM, needs human review

        sex = str(participant_info.get("sex", participant_info.get("gender", ""))).strip().lower()
        if sex in ["m", "male"]:
            sex = "male"
        elif sex in ["f", "female"]:
            sex = "female"
        elif not sex or sex.lower() in ["nan", "none", ""]:
            sex = "unknown"  # inferred by LLM, needs human review
        else:
            sex = "unknown"  # inferred by LLM, needs human review

        # Get original description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        # Build eegunity_description with required info fields
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }

        # Add any extra required info fields from participants.tsv
        for field in ["age", "sex"]:
            if field in participant_info and field not in eegunity_desc:
                val = str(participant_info[field])
                if not val or val.lower() in ["nan", "none"]:
                    val = "unknown"
                eegunity_desc[field] = val

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })

        # Channel rename before set_montage
        # Standardize channel names for 10-20 system
        rename_map = {}
        for ch_name in raw.ch_names:
            new_name = ch_name.strip().upper()
            # Common EDF channel name fixes
            if new_name.startswith("EEG "):
                new_name = new_name[4:].strip()
            if new_name.endswith("-REF") or new_name.endswith("-LE"):
                new_name = new_name[:-4].strip()
            # Handle specific channel naming patterns
            if new_name and new_name != ch_name:
                rename_map[ch_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            pass  # inferred by LLM, needs human review

        # Read events.tsv for annotations and derived misc channels
        events_path = self._get_events_tsv_path(raw_path)
        events_df = self._read_events_tsv(events_path)

        # Add annotations from events.tsv if raw format doesn't carry triggers
        # EDF files typically don't have embedded event markers
        if events_df is not None and len(events_df) > 0:
            # Check if raw already has annotations or events
            has_events = False
            try:
                # Try to get events from annotations
                test_events, _ = mne.events_from_annotations(raw, verbose=False)
                if len(test_events) > 0:
                    has_events = True
            except Exception:
                pass
            
            if not has_events:
                # Create annotations from events.tsv
                onsets = []
                durations = []
                descriptions = []
                
                for _, ev_row in events_df.iterrows():
                    onset = ev_row.get("onset", ev_row.get("sample", 0))
                    if pd.isna(onset):
                        continue
                    # Convert to seconds if in samples
                    if "sample" in ev_row and "onset" not in ev_row:
                        onset = float(onset) / raw.info["sfreq"]
                    else:
                        onset = float(onset)
                    
                    duration = float(ev_row.get("duration", 0))
                    if pd.isna(duration):
                        duration = 0
                    
                    # Use trial_type or value for description
                    desc = None
                    for col in ["trial_type", "value", "event_value", "event_id"]:
                        if col in ev_row and pd.notna(ev_row[col]):
                            desc = str(ev_row[col])
                            break
                    if desc is None:
                        desc = "unknown"
                    
                    onsets.append(onset)
                    durations.append(duration)
                    descriptions.append(desc)
                
                if len(onsets) > 0:
                    annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                    raw.set_annotations(annot)

        # Create derived misc channels
        if events_df is not None and len(events_df) > 0:
            # Ensure event_value is numeric
            if "event_value" in events_df.columns:
                events_df["event_value_int"] = events_df["event_value"].apply(self._parse_event_value)
            elif "value" in events_df.columns:
                events_df["event_value_int"] = events_df["value"].apply(self._parse_event_value)
                events_df["event_value"] = events_df["value"]
            else:
                events_df["event_value_int"] = None
                events_df["event_value"] = None

            # Find trial start/end events
            # Look for trial_type or event_value indicating trial boundaries
            trial_start_mask = events_df["trial_type"].str.contains("start", case=False, na=False) if "trial_type" in events_df.columns else False
            trial_end_mask = events_df["trial_type"].str.contains("end", case=False, na=False) if "trial_type" in events_df.columns else False
            
            # Also check event_value for trial markers
            if "event_value_int" in events_df.columns:
                trial_start_mask = trial_start_mask | (events_df["event_value_int"] == 9)  # event_9 is trial_start
                trial_end_mask = trial_end_mask | (events_df["event_value_int"] == 14)  # event_14 is trial_end
            
            # Build trial segments
            trials = []
            current_trial = None
            for _, ev in events_df.iterrows():
                ev_val = ev.get("event_value_int")
                onset = float(ev.get("onset", 0))
                
                if ev_val == 9 or (pd.isna(ev_val) and "start" in str(ev.get("trial_type", "")).lower()):
                    current_trial = {"start": onset, "events": []}
                elif ev_val == 14 or (pd.isna(ev_val) and "end" in str(ev.get("trial_type", "")).lower()):
                    if current_trial is not None:
                        current_trial["end"] = onset
                        trials.append(current_trial)
                        current_trial = None
                elif current_trial is not None:
                    current_trial["events"].append(ev.to_dict())
            
            # Handle case where last trial doesn't have explicit end
            if current_trial is not None and "end" not in current_trial:
                current_trial["end"] = raw.times[-1]
                trials.append(current_trial)

            # Create cue_direction misc channel
            n_samples = len(raw.times)
            cue_direction_data = np.zeros(n_samples)
            
            for trial in trials:
                t_start = trial["start"]
                t_end = trial.get("end", raw.times[-1])
                
                # Find cue event in trial (event_value 1, 2, or 3)
                cue_val = 0  # default
                for ev in trial.get("events", []):
                    ev_val = self._parse_event_value(ev.get("event_value", ev.get("value")))
                    if ev_val in [1, 2, 3]:
                        cue_val = ev_val - 1  # 1->0 (left), 2->1 (right), 3->2 (center)
                        break
                
                # Set values for trial duration
                start_idx = max(0, int(t_start * raw.info["sfreq"]) - raw.first_samp)
                end_idx = min(n_samples, int(t_end * raw.info["sfreq"]) - raw.first_samp)
                if start_idx < n_samples and end_idx > start_idx:
                    cue_direction_data[start_idx:end_idx] = cue_val
            
            # Add cue_direction channel
            info_cue = mne.create_info(["cue_direction"], raw.info["sfreq"], ch_types=["misc"])
            cue_raw = mne.io.RawArray(cue_direction_data.reshape(1, -1), info_cue, first_samp=raw.first_samp)
            raw.add_channels([cue_raw], force_update_info=True)

            # Create reaction_time misc channel
            rt_data = np.zeros(n_samples)
            
            for trial in trials:
                t_start = trial["start"]
                t_end = trial.get("end", raw.times[-1])
                
                # Find target event (11, 12, or 13) and subsequent correct button press (15)
                target_onset = None
                button_onset = None
                
                for ev in trial.get("events", []):
                    ev_val = self._parse_event_value(ev.get("event_value", ev.get("value")))
                    ev_onset = float(ev.get("onset", 0))
                    
                    if ev_val in [11, 12, 13] and target_onset is None:
                        target_onset = ev_onset
                    elif ev_val == 15 and target_onset is not None and button_onset is None:
                        button_onset = ev_onset
                        break
                
                rt = 0.0
                if target_onset is not None and button_onset is not None:
                    rt = button_onset - target_onset
                
                # Set RT for trial duration
                start_idx = max(0, int(t_start * raw.info["sfreq"]) - raw.first_samp)
                end_idx = min(n_samples, int(t_end * raw.info["sfreq"]) - raw.first_samp)
                if start_idx < n_samples and end_idx > start_idx:
                    rt_data[start_idx:end_idx] = rt
            
            # Add reaction_time channel
            info_rt = mne.create_info(["reaction_time"], raw.info["sfreq"], ch_types=["misc"])
            rt_raw = mne.io.RawArray(rt_data.reshape(1, -1), info_rt, first_samp=raw.first_samp)
            raw.add_channels([rt_raw], force_update_info=True)

        # Ensure required native misc channels are set to 'misc' type
        # (none specified for this dataset)

        return raw


KERNEL = OpenneuroDs002034Kernel()