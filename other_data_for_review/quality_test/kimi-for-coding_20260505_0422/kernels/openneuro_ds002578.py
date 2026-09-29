import json
import os
import numpy as np
import pandas as pd
import mne
from mne.io import BaseRaw


class OpenneuroDs002578Kernel:
    """
    Kernel for OpenNeuro ds002578 - Visual Oddball with Selective Attention
    =========================================================================
    Dataset: EEG data from visual oddball paradigm with 5 spatial boxes.
             Subjects attend to one box and detect when a disc appears there.
    
    Raw format: EEGLAB .set files (via mne.io.read_raw_eeglab)
    - Contains event codes 31-45 in raw annotations (Attend-to/Cue positions)
    - Processed events.tsv has generic 'Picture' events (condition codes cleaned)
    - Must extract original numeric codes from raw .set file annotations
    
    Tasks:
    1. Attend-3: Target=33 (disc in box 3), Distractors=31,34,35
    2. Attend-4: Target=44 (disc in box 4), Distractors=41,42,43,45
    
    Required event IDs: 31-35, 41-45, 'Picture', 'Response'
    Required info fields: age, gender (from participants.tsv)
    """

    # ------------------------------------------------------------------
    # Kernel metadata
    # ------------------------------------------------------------------
    KERNEL_ID = "openneuro_ds002578"
    dataset_name = "openneuro_ds002578"
    version = "1.0.0"

    # What the downstream pipeline expects this kernel to expose
    kernel_requirements = {
        "required_event_ids": [
            "31", "32", "33", "34", "35",
            "41", "42", "43", "44", "45",
            "Picture", "Response"
        ],
        "required_info_fields": ["age", "gender"],
        "required_native_misc": [],
        "derived_misc_channels": []
    }

    # ------------------------------------------------------------------
    # BIDS helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _find_bids_root(file_path: str) -> str:
        """Walk upward until we find a directory containing participants.tsv."""
        current = os.path.dirname(os.path.abspath(file_path))
        while current != os.path.dirname(current):  # stop at filesystem root
            if os.path.isfile(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return ""

    @staticmethod
    def _parse_bids_entities(file_path: str) -> dict:
        """Extract subject, session, task, run from BIDS filename."""
        basename = os.path.basename(file_path)
        entities = {}
        parts = basename.replace(".set", "").replace(".eeg", "").replace(".fdt", "").split("_")
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
        """Load age and gender from participants.tsv for given subject."""
        info = {"age": "unknown", "gender": "unknown"}
        if not bids_root:
            return info
        
        tsv_path = os.path.join(bids_root, "participants.tsv")
        if not os.path.isfile(tsv_path):
            return info
        
        try:
            df = pd.read_csv(tsv_path, sep="\t")
            # BIDS subject IDs may or may not include 'sub-' prefix
            for _, row in df.iterrows():
                pid = str(row.get("participant_id", "")).strip()
                if pid == subject_id or pid == f"sub-{subject_id}":
                    # age
                    age_val = row.get("age", "")
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val)))
                    # gender/sex
                    gender_val = row.get("gender", row.get("sex", ""))
                    if pd.notna(gender_val):
                        g = str(gender_val).strip().lower()
                        if g in ("m", "male"):
                            info["gender"] = "male"
                        elif g in ("f", "female"):
                            info["gender"] = "female"
                        else:
                            info["gender"] = g
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
        
        # Try exact match first
        candidates = []
        
        # Standard BIDS path: sub-XX/[ses-YY/]eeg/sub-XX_task-..._events.tsv
        sub_path = os.path.join(bids_root, f"sub-{subject}")
        if session:
            sub_path = os.path.join(sub_path, f"ses-{session}")
        sub_path = os.path.join(sub_path, "eeg")
        
        for fname in os.listdir(sub_path) if os.path.isdir(sub_path) else []:
            if not fname.endswith("_events.tsv"):
                continue
            # Check if task and run match
            if task and f"task-{task}" not in fname:
                continue
            if run and f"run-{run}" not in fname:
                continue
            candidates.append(os.path.join(sub_path, fname))
        
        # Fallback: look in same directory as file
        if not candidates:
            for fname in os.listdir(base_dir) if os.path.isdir(base_dir) else []:
                if fname.endswith("_events.tsv"):
                    candidates.append(os.path.join(base_dir, fname))
        
        return candidates[0] if candidates else ""

    def _read_events_tsv(self, events_tsv: str) -> pd.DataFrame:
        """Read events.tsv and return DataFrame."""
        if not events_tsv or not os.path.isfile(events_tsv):
            return pd.DataFrame()
        try:
            return pd.read_csv(events_tsv, sep="\t")
        except Exception:
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Main apply()
    # ------------------------------------------------------------------
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("file_path", ""))
        
        # ------------------------------------------------------------------
        # 1. BIDS metadata
        # ------------------------------------------------------------------
        bids_root = self._find_bids_root(file_path)
        entities = self._parse_bids_entities(file_path)
        subject_id = entities.get("subject", "")
        
        # Load participant info
        participant_info = self._load_participants(bids_root, subject_id)
        
        # ------------------------------------------------------------------
        # 2. Preserve original description
        # ------------------------------------------------------------------
        original_description = raw.info.get("description", "")
        
        # ------------------------------------------------------------------
        # 3. Handle events - raw .set files contain original numeric codes 31-45
        # ------------------------------------------------------------------
        # The raw EEGLAB .set files have the original event codes in annotations
        # We need to preserve these and also add any events.tsv events
        
        # Get existing annotations from raw
        existing_annotations = raw.annotations
        
        # Read events.tsv for additional events (Picture, Response)
        events_tsv = self._find_events_tsv(file_path, bids_root, entities)
        events_df = self._read_events_tsv(events_tsv)
        
        # Build list of all annotations
        onsets = []
        durations = []
        descriptions = []
        
        # Add existing raw annotations (numeric codes 31-45)
        if existing_annotations is not None:
            for i in range(len(existing_annotations)):
                onsets.append(existing_annotations.onset[i])
                durations.append(existing_annotations.duration[i])
                descriptions.append(str(existing_annotations.description[i]))
        
        # Add events from events.tsv
        if not events_df.empty:
            for _, ev_row in events_df.iterrows():
                onset = ev_row.get("onset", np.nan)
                duration = ev_row.get("duration", 0.0)
                trial_type = ev_row.get("trial_type", "")
                value = ev_row.get("value", "")
                
                # Skip if onset is missing
                if pd.isna(onset):
                    continue
                
                # Use trial_type if available, otherwise value
                desc = str(trial_type).strip() if pd.notna(trial_type) and str(trial_type).strip() else str(value).strip()
                
                # Skip if no description
                if not desc:
                    continue
                
                # Skip numeric codes already in raw annotations to avoid duplicates
                if desc in ("31", "32", "33", "34", "35", "41", "42", "43", "44", "45"):
                    continue
                
                onsets.append(float(onset))
                durations.append(float(duration) if pd.notna(duration) else 0.0)
                descriptions.append(desc)
        
        # Create new annotations if we have any
        if onsets:
            # Sort by onset time
            sorted_indices = np.argsort(onsets)
            onsets = [onsets[i] for i in sorted_indices]
            durations = [durations[i] for i in sorted_indices]
            descriptions = [descriptions[i] for i in sorted_indices]
            
            new_annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(new_annotations)
        
        # ------------------------------------------------------------------
        # 4. Build eegunity_description
        # ------------------------------------------------------------------
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("gender", "unknown"),
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown"
        }
        
        # ------------------------------------------------------------------
        # 5. Set description as JSON string
        # ------------------------------------------------------------------
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenneuroDs002578Kernel()