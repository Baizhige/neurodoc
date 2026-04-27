"""OpenNeuro DS004745 stage1 kernel for EEGUnity.

Dataset: 8-channel SSVEP EEG with 6 subjects performing tasks at 2/4/8 Hz
stimulation frequencies under artifact-free and artifact conditions.

Source: https://openneuro.org/datasets/ds004745
Reference: DOI 10.1109/EMBC46164.2021.9629771
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import mne


# ---- Device metadata ---------------------------------------------------
# Source: Official OpenNeuro dataset page and reference paper
# DOI 10.1109/EMBC46164.2021.9629771
# "The EEG signals were acquired with a g.USBamp amplifier (gtec, Graz, Austria)
#  and an electrode cap with 8 active electrodes."
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_DEVICE_METADATA: Dict[str, Any] = {
    "amplifier": "g.USBamp",  # gtec Graz, Austria
    "cap": "Ag/AgCl active electrode cap",  # LLM 推断，需人类复核
    "handedness": "unknown",  # No handedness info in公开文档
}

# ---- Event mapping ----------------------------------------------------
# Raw event IDs found in events.tsv:
#   1, 2, 3, 4, 5, 6, 7, 8, 10
# Event 2/4/8 = 2/4/8 Hz SSVEP conditions (artifact-free)
# Event 10 = artifact/rest condition
# Events 1, 3, 5, 6, 7 have 36 occurrences each — decode uncertain;
# preserved as-is in raw meta pending verified decode table.
_EVENT_MAP: Dict[int, str] = {
    1: "marker-1",
    2: "ssvep-2hz",
    3: "marker-3",
    4: "ssvep-4hz",
    5: "marker-5",
    6: "marker-6",
    7: "marker-7",
    8: "ssvep-8hz",
    10: "artifact-rest",
}


def _detect_paradigm(file_path: str) -> str | None:
    """Return paradigm prefix if sub-directory encodes a paradigm, else None."""
    # No paradigm ambiguity in this dataset; single SSVEP paradigm.
    return None


def _load_raw_with_bids(
    root: str,
    subject_id: str,
) -> tuple[mne.io.BaseRaw, mne.find_desc._annotations_like | None]:
    """Read BIDS EEG file for a given subject."""
    import glob

    sub_dir = os.path.join(root, f"sub-{subject_id}", "eeg")
    if not os.path.isdir(sub_dir):
        return None, None

    eeg_files = glob.glob(os.path.join(sub_dir, "*.vhdr"))
    if eeg_files:
        raw = mne.io.read_raw_brainvision(eeg_files[0], preload=False, verbose=False)
    else:
        eeg_files = glob.glob(os.path.join(sub_dir, "*.edf"))
        if eeg_files:
            raw = mne.io.read_raw_edf(eeg_files[0], preload=False, verbose=False)
        else:
            eeg_files = glob.glob(os.path.join(sub_dir, "*.set"))
            if eeg_files:
                raw = mne.io.read_raw_eeglab(eeg_files[0], preload=False, verbose=False)
            else:
                return None, None

    # Load BIDS sidecar events
    events_tsv = os.path.join(sub_dir, f"sub-{subject_id}_task-SSVEP_events.tsv")
    if os.path.exists(events_tsv):
        import pandas as pd
        ev_df = pd.read_csv(events_tsv, sep="\t")
        if "onset" in ev_df.columns and "value" in ev_df.columns:
            from scipy.stats import mode as sp_mode
            # Use value column; coerce numeric entries
            onsets = []
            durations = []
            descriptions = []
            for _, r in ev_df.iterrows():
                try:
                    val = int(float(r["value"]))
                except (ValueError, TypeError):
                    val = 0
                onsets.append(float(r["onset"]))
                durations.append(float(r.get("duration", 0)))
                desc = _EVENT_MAP.get(val, f"marker-{val}")
                descriptions.append(desc)

            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            return raw, annotations

    return raw, None


class OpenNeuroDS004745Kernel:
    """Stage1 kernel for OpenNeuro DS004745."""

    KERNEL_ID: str = "openneuro-ds004745-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path: str = row.get("File Path", "")
        dataset_root: str = row.get("Dataset Root", os.path.dirname(file_path))

        # ---- 1. Subject info from BIDS participants.tsv -----------------
        subject_id = row.get("Subject ID", "")
        participants_tsv = os.path.join(dataset_root, "participants.tsv")

        age_str = "unknown"
        sex_str = "unknown"

        if os.path.exists(participants_tsv):
            import pandas as pd

            df = pd.read_csv(participants_tsv, sep="\t")
            col_id = "participant_id" if "participant_id" in df.columns else None
            if col_id is None:
                col_id = df.columns[0]
            sub_row = df[df[col_id].str.endswith(subject_id)]
            if not sub_row.empty:
                r = sub_row.iloc[0]
                # age
                if "age" in r.index:
                    val = r["age"]
                    if isinstance(val, (int, float)) and not pd.isna(val):
                        age_str = str(int(val))
                    elif isinstance(val, str) and val.strip():
                        age_str = val.strip()
                # sex
                if "sex" in r.index:
                    val = r["sex"]
                    if isinstance(val, str):
                        v = val.strip().lower()
                        if v in ("m", "male"):
                            sex_str = "male"
                        elif v in ("f", "female"):
                            sex_str = "female"

        # ---- 2. Load raw (BIDS read, bypass EEGUnity auto-parse) --------
        # Re-read the file ourselves to inject annotations.
        raw2, annotations = _load_raw_with_bids(dataset_root, subject_id)
        if raw2 is not None:
            raw = raw2
        if annotations is not None:
            raw.set_annotations(annotations)

        # ---- 3. Channel rename (8-channel standard 1020) -----------------
        # Source: g.USBamp 8-channel cap — standard positions
        # Channel order (from reference paper): Fz, Cz, Pz, POz, O1, O2, P3, P4
        # Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        CHANNEL_RENAME_MAP: Dict[str, str] = {
            "EEG1": "Fz",
            "EEG2": "Cz",
            "EEG3": "Pz",
            "EEG4": "POz",
            "EEG5": "O1",
            "EEG6": "O2",
            "EEG7": "P3",
            "EEG8": "P4",
        }
        rename_map = {
            src: tgt
            for src, tgt in CHANNEL_RENAME_MAP.items()
            if src in raw.ch_names
        }
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 1020 montage after rename
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass

        # ---- 4. Build description ----------------------------------------
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = str(original_desc)

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age_str,
                "sex": sex_str,
                "amplifier": _DEVICE_METADATA["amplifier"],
                "cap": _DEVICE_METADATA["cap"],
                "handedness": _DEVICE_METADATA["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004745Kernel()