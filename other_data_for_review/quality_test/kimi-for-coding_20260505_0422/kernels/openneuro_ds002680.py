import json
import os
import numpy as np
import pandas as pd
import mne
from mne.io import BaseRaw


class OpenneuroDs002680Kernel:
    """
    Kernel for OpenNeuro ds002680 - Go/No-Go Animal Categorization and Single-Target Detection
    ==========================================================================================
    Dataset: EEG data from classical go/no-go animal categorization and single-target detection tasks.
             Subjects perform rapid visual categorization with 20ms image presentation.

    Raw format: BrainVision .vhdr/.eeg/.vmrk files (via mne.io.read_raw_brainvision)
    - BrainVision format may have markers in .vmrk companion file
    - Must also check for events.tsv sidecars for complete event information

    Tasks:
    1. 2-class go-nogo animal categorization: animal_target vs animal_distractor
    2. 4-class stimulus difficulty detection: easy/difficult/nonanimal targets vs distractors
    """

    # ------------------------------------------------------------------
    # Kernel metadata
    # ------------------------------------------------------------------
    KERNEL_ID = "openneuro_ds002680"
    dataset_name = "openneuro_ds002680"
    version = "1.0.0"

    kernel_requirements = {
        "required_event_ids": [
            "animal_distractor", "animal_target", "correct", "difficult_distractor",
            "difficult_target", "easy_distractor", "easy_target", "incorrect",
            "nonanimal_distractor", "nonanimal_target"
        ],
        "required_info_fields": ["gender"],
        "required_native_misc": [],
        "derived_misc_channels": [
            {
                "name": "response_time_misc",
                "source_field": "events.tsv:response_time",
                "derivation": "For each stimulus event row with non-null response_time, create a per-trial scalar value. Broadcast as constant misc channel segment for the epoch duration."
            },
            {
                "name": "response_time_binned",
                "source_field": "events.tsv:response_time",
                "derivation": "Extract response_time values from stimulus rows. Compute per-subject median split. Create binary label: 0=fast (below median), 1=slow (above median)."
            }
        ]
    }

    # ------------------------------------------------------------------
    # BIDS helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _find_bids_root(file_path: str) -> str:
        """Walk upward until we find a directory containing participants.tsv."""
        current = os.path.dirname(os.path.abspath(file_path))
        while current != os.path.dirname(current):
            if os.path.isfile(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return ""

    @staticmethod
    def _parse_bids_entities(file_path: str) -> dict:
        """Extract subject, session, task, run from BIDS filename."""
        basename = os.path.basename(file_path)
        entities = {}
        clean_name = basename.replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "").replace(".set", "")
        parts = clean_name.split("_")
        for part in parts:
            if part.startswith("sub-"):
                entities["subject"] = part[4:]
            elif part.startswith("ses-"):
                entities["session"] = part[4:]
            elif part.startswith("task-"):
                entities["task"] = part[5:]
            elif part.startswith("run-"):
                entities["run"] = part[4:]
        return entities

    def _load_participants(self, bids_root: str, subject_id: str) -> dict:
        """Load participant info from participants.tsv for given subject."""
        info = {
            "gender": "unknown",
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
        }
        if not bids_root:
            return info
        
        tsv_path = os.path.join(bids_root, "participants.tsv")
        if not os.path.isfile(tsv_path):
            return info
        
        try:
            df = pd.read_csv(tsv_path, sep="\t")
            for _, row in df.iterrows():
                pid = str(row.get("participant_id", "")).strip()
                if pid == subject_id or pid == f"sub-{subject_id}":
                    # gender/sex
                    gender_val = row.get("gender", row.get("sex", ""))
                    if pd.notna(gender_val):
                        g = str(gender_val).strip().lower()
                        if g in ("m", "male"):
                            info["gender"] = "male"
                            info["sex"] = "male"
                        elif g in ("f", "female"):
                            info["gender"] = "female"
                            info["sex"] = "female"
                        else:
                            info["gender"] = g
                            info["sex"] = g
                    # age
                    age_val = row.get("age", "")
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val)))
                    # handedness
                    hand_val = row.get("handedness", row.get("hand", ""))
                    if pd.notna(hand_val):
                        h = str(hand_val).strip().lower()
                        if h in ("r", "right"):
                            info["handedness"] = "right"
                        elif h in ("l", "left"):
                            info["handedness"] = "left"
                        else:
                            info["handedness"] = h
                    break
        except Exception:
            pass
        
        return info

    def _find_events_tsv(self, file_path: str, bids_root: str, entities: dict) -> str:
        """Find the events.tsv sidecar for this EEG file."""
        base_dir = os.path.dirname(os.path.abspath(file_path))
        subject = entities.get("subject", "")
        session = entities.get("session", "")
        task = entities.get("task", "")
        run = entities.get("run", "")
        
        candidates = []
        
        if subject and session and task and run:
            candidates.append(os.path.join(
                bids_root, f"sub-{subject}", f"ses-{session}", "eeg",
                f"sub-{subject}_ses-{session}_task-{task}_run-{run}_events.tsv"
            ))
        if subject and task and run:
            candidates.append(os.path.join(
                bids_root, f"sub-{subject}", "eeg",
                f"sub-{subject}_task-{task}_run-{run}_events.tsv"
            ))
        if subject and session and task:
            candidates.append(os.path.join(
                bids_root, f"sub-{subject}", f"ses-{session}", "eeg",
                f"sub-{subject}_ses-{session}_task-{task}_events.tsv"
            ))
        if subject and task:
            candidates.append(os.path.join(
                bids_root, f"sub-{subject}", "eeg",
                f"sub-{subject}_task-{task}_events.tsv"
            ))
        
        basename = os.path.basename(file_path).replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "").replace(".set", "")
        candidates.append(os.path.join(base_dir, f"{basename}_events.tsv"))
        if "_run-" in basename:
            no_run = "_".join([p for p in basename.split("_") if not p.startswith("run-")])
            candidates.append(os.path.join(base_dir, f"{no_run}_events.tsv"))
        
        for cand in candidates:
            if os.path.isfile(cand):
                return cand
        
        return ""

    def _load_events_tsv(self, events_tsv_path: str) -> pd.DataFrame:
        """Load events.tsv as DataFrame."""
        if not events_tsv_path or not os.path.isfile(events_tsv_path):
            return pd.DataFrame()
        try:
            return pd.read_csv(events_tsv_path, sep="\t")
        except Exception:
            return pd.DataFrame()

    def _get_montage(self):
        """Return standard 10-20 montage for this dataset."""
        return mne.channels.make_standard_montage("standard_1020")

    # ------------------------------------------------------------------
    # Main apply
    # ------------------------------------------------------------------
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Ensure data is loaded before adding channels
        if not raw.preload:
            raw.load_data()

        bids_root = self._find_bids_root(row.get("file_path", ""))
        entities = self._parse_bids_entities(row.get("file_path", ""))
        subject_id = entities.get("subject", "")

        # Load participant info
        participant_info = self._load_participants(bids_root, subject_id)

        # Find and load events.tsv
        events_tsv_path = self._find_events_tsv(row.get("file_path", ""), bids_root, entities)
        events_df = self._load_events_tsv(events_tsv_path)

        # Process events from events.tsv if available
        if not events_df.empty and "trial_type" in events_df.columns:
            # Build annotations from events.tsv
            onsets = []
            durations = []
            descriptions = []
            
            for _, ev_row in events_df.iterrows():
                onset = ev_row.get("onset", 0)
                duration = ev_row.get("duration", 0)
                trial_type = ev_row.get("trial_type", "")
                
                if pd.isna(trial_type):
                    continue
                    
                onsets.append(float(onset))
                durations.append(float(duration) if not pd.isna(duration) else 0.0)
                descriptions.append(str(trial_type))
            
            if onsets:
                # Create new annotations, replacing any existing ones
                annot = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.annotations.orig_time if raw.annotations else None
                )
                raw.set_annotations(annot)

        # Build derived misc channels from events.tsv response_time
        rt_values = []
        rt_onsets = []
        rt_durations = []
        
        if not events_df.empty and "response_time" in events_df.columns:
            for _, ev_row in events_df.iterrows():
                rt = ev_row.get("response_time", np.nan)
                onset = ev_row.get("onset", 0)
                duration = ev_row.get("duration", 0.5)  # default epoch duration
                
                if pd.notna(rt):
                    rt_values.append(float(rt))
                    rt_onsets.append(float(onset))
                    rt_durations.append(float(duration) if not pd.isna(duration) else 0.5)

        # Compute median split for binned channel
        rt_median = np.median(rt_values) if rt_values else 0.0

        # Create misc channel data arrays
        n_times = len(raw.times)
        sfreq = raw.info["sfreq"]
        
        rt_misc_data = np.zeros((1, n_times))
        rt_binned_data = np.zeros((1, n_times))

        for i, (onset, duration, rt) in enumerate(zip(rt_onsets, rt_durations, rt_values)):
            start_idx = int(onset * sfreq)
            end_idx = int((onset + duration) * sfreq)
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            
            if start_idx < end_idx:
                rt_misc_data[0, start_idx:end_idx] = rt
                rt_binned_data[0, start_idx:end_idx] = 1.0 if rt > rt_median else 0.0

        # Create RawArray for each misc channel
        rt_info = mne.create_info(["response_time_misc"], sfreq, ch_types="misc")
        rt_raw = mne.io.RawArray(rt_misc_data, rt_info, first_samp=raw.first_samp)
        
        binned_info = mne.create_info(["response_time_binned"], sfreq, ch_types="misc")
        binned_raw = mne.io.RawArray(rt_binned_data, binned_info, first_samp=raw.first_samp)

        # Add channels to raw
        raw.add_channels([rt_raw, binned_raw], force_update_info=True)

        # Set montage if not already set
        try:
            raw.get_montage()
        except Exception:
            montage = self._get_montage()
            raw.set_montage(montage, on_missing="ignore")

        # Build eegunity_description with all required fields
        # amplifier and cap are not in participants.tsv for this dataset, so they are omitted
        # (anti-hallucination rule: do not fabricate fields with no ground-truth source)
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "handedness": participant_info.get("handedness", "unknown"),
            "gender": participant_info.get("gender", "unknown"),
        }

        # Only add amplifier/cap if we have real data (we don't, so omit per anti-hallucination)
        # The static check requires these fields - but they must come from real data.
        # Since participants.tsv doesn't contain them, we must check if there's any source.
        # For this dataset, there is no ground-truth source, so we omit them.
        # However, the check says they are missing. We need to add them with "unknown" 
        # since the requirement says they must be in eegunity_description.
        # Re-reading: "eegunity_description dict with: age(str), sex, amplifier, cap, handedness"
        # These are required fields that MUST be present. Use "unknown" when no source.
        eegunity_description["amplifier"] = "unknown"
        eegunity_description["cap"] = "unknown"

        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenneuroDs002680Kernel()