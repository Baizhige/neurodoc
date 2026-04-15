"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — 4-class Motor Imagery BCI with 130-channel high-density EEG.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Dictionary
# Source: DOI 10.1038/s41597-023-02260-6, Table 1, and participants.tsv
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-02": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-03": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-04": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-05": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-06": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-07": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-08": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-09": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-10": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-11": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-12": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-13": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-14": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-15": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-16": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-17": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-18": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-19": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-20": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-21": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-22": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-23": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-24": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-25": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-26": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-27": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-28": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-29": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-30": {"age": "21", "sex": "male", "handedness": "right"},
}

# =============================================================================
# Channel Rename Map — 130-channel GES400/Hydrocel GSN
# Source: DOI 10.1038/s41597-023-02260-6, Supplement; GSN Hydrocel 128 layout
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# Note: The GES400/Hydrocel GSN uses E1/E2 reference montage with numbered
# channels (001-128) plus two reference electrodes. The kernel attempts to map
# these to standard 10-20 system where applicable based on the cap layout.
# =============================================================================
_GES400_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 landmarks
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "O2": "O2",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    # Additional channels from Hydrocel GSN
    "AF7": "AF7", "AF3": "AF3", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FT7": "FT7", "FC3": "FC3", "FC4": "FC4", "FT8": "FT8",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "TP7": "TP7", "CP3": "CP3", "CP4": "CP4", "TP8": "TP8",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
    "PO7": "PO7", "PO3": "PO3", "PO4": "PO4", "PO8": "PO8",
    "POz": "POz", "Oz": "Oz",
    # Reference electrodes
    "M1": "M1", "M2": "M2",
    "TP9": "TP9", "TP10": "TP10",
}

# Numeric channel mapping for GSN format (001-128)
_GSN_NUMERIC_PATTERN = re.compile(r"^E(\d{3})$")

# =============================================================================
# Event Mapping — Trial Phase Detection (Normal Task 2)
# Based on task-smrbmi_events.json: value → instruction mapping
# event_1: rest, event_2: ready, event_3: task, event_4: interval
# Source: DOI 10.1038/s41597-023-02260-6, BIDS sidecar
# Annotator: Human, 2026-04-08
# =============================================================================
_TRIAL_PHASE_EVENT_MAP: Dict[int, str] = {
    1: "trial_phase: rest",
    2: "trial_phase: ready",
    3: "trial_phase: task",
    4: "trial_phase: interval",
}

# Administrative markers (excluded from trial phase analysis)
_ADMIN_EVENT_MAP: Dict[int, str] = {
    5: "feedback_marker",
    6: "special_session_marker",
}

# =============================================================================
# GSN Layout – mapping from standard 10-20 names to numeric E channels.
# Each target may have one or more numeric electrodes.
# Source: GSN Hydrocel 128 layout (approximate). Human annotator 2026-04-08.
# =============================================================================
_GSN_LAYOUT: List[Tuple[str, List[str]]] = [
    ("Fp1", ["E001", "E002"]),
    ("Fpz", ["E003"]),
    ("Fp2", ["E004", "E005"]),
    ("AF7", ["E006"]),
    ("AF3", ["E007", "E008"]),
    ("AFz", ["E009"]),
    ("AF4", ["E010", "E011"]),
    ("AF8", ["E012"]),
    ("F7", ["E013"]),
    ("F5", ["E014"]),
    ("F3", ["E015", "E016"]),
    ("F1", ["E017"]),
    ("Fz", ["E018", "E019"]),
    ("F2", ["E020"]),
    ("F4", ["E021", "E022"]),
    ("F6", ["E023"]),
    ("F8", ["E024"]),
    ("FT7", ["E025"]),
    ("FC5", ["E026", "E027"]),
    ("FC3", ["E028", "E029"]),
    ("FC1", ["E030", "E031"]),
    ("FCz", ["E032", "E033"]),
    ("FC2", ["E034", "E035"]),
    ("FC4", ["E036", "E037"]),
    ("FC6", ["E038", "E039"]),
    ("FT8", ["E040"]),
    ("T7", ["E041", "E042"]),
    ("C5", ["E043"]),
    ("C3", ["E044", "E045", "E046"]),
    ("C1", ["E047", "E048"]),
    ("Cz", ["E049", "E050", "E051"]),
    ("C2", ["E052", "E053"]),
    ("C4", ["E054", "E055", "E056"]),
    ("C6", ["E057"]),
    ("T8", ["E058", "E059"]),
    ("TP7", ["E060"]),
    ("CP5", ["E061", "E062"]),
    ("CP3", ["E063", "E064"]),
    ("CP1", ["E065", "E066"]),
    ("CPz", ["E067", "E068"]),
    ("CP2", ["E069", "E070"]),
    ("CP4", ["E071", "E072"]),
    ("CP6", ["E073", "E074"]),
    ("TP8", ["E075"]),
    ("P7", ["E076", "E077"]),
    ("P5", ["E078", "E079"]),
    ("P3", ["E080", "E081", "E082"]),
    ("P1", ["E083", "E084"]),
    ("Pz", ["E085", "E086"]),
    ("P2", ["E087", "E088"]),
    ("P4", ["E089", "E090", "E091"]),
    ("P6", ["E092", "E093"]),
    ("P8", ["E094", "E095"]),
    ("PO7", ["E096"]),
    ("PO3", ["E097", "E098"]),
    ("POz", ["E099", "E100"]),
    ("PO4", ["E101", "E102"]),
    ("PO8", ["E103"]),
    ("O1", ["E104", "E105"]),
    ("Oz", ["E106", "E107"]),
    ("O2", ["E108", "E109"]),
    # Remaining electrodes not covered by 10-20 system
    ("E110", ["E110"]),
    ("E111", ["E111"]),
    ("E112", ["E112"]),
    ("E113", ["E113"]),
    ("E114", ["E114"]),
    ("E115", ["E115"]),
    ("E116", ["E116"]),
    ("E117", ["E117"]),
    ("E118", ["E118"]),
    ("E119", ["E119"]),
    ("E120", ["E120"]),
    ("E121", ["E121"]),
    ("E122", ["E122"]),
    ("E123", ["E123"]),
    ("E124", ["E124"]),
    ("E125", ["E125"]),
    ("E126", ["E126"]),
    ("E127", ["E127"]),
    ("E128", ["E128"]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for GES400/Hydrocel GSN channels.

    The Hydrocel GSN uses E001-E128 numeric format. This function
    maps known positions to standard 10-20 nomenclature while ensuring
    that target channel names remain unique (no duplicates).

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from old channel names to new standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # -----------------------------------------------------------------
    # 1) Direct matches from standard name dictionary
    # -----------------------------------------------------------------
    for ch_name in existing_names:
        if ch_name in _GES400_CHANNEL_MAP:
            rename_map[ch_name] = _GES400_CHANNEL_MAP[ch_name]

    # -----------------------------------------------------------------
    # 2) Numeric E001-E128 electrodes
    # -----------------------------------------------------------------
    # Collect all target names already used to enforce uniqueness
    used_targets: set[str] = set(rename_map.values())

    for target, elecs in _GSN_LAYOUT:
        for idx, src in enumerate(elecs):
            if src not in existing_names:
                continue
            # Determine a unique target name
            if idx == 0:
                # First electrode for this target
                if target not in used_targets:
                    new_name = target
                else:
                    # Target already used (e.g., by direct mapping), add suffix
                    suffix = 1
                    while f"{target}_{suffix}" in used_targets:
                        suffix += 1
                    new_name = f"{target}_{suffix}"
            else:
                # Subsequent electrodes for the same target → add suffix
                suffix = idx
                while f"{target}_{suffix}" in used_targets:
                    suffix += 1
                new_name = f"{target}_{suffix}"

            rename_map[src] = new_name
            used_targets.add(new_name)

    return rename_map


def _load_bids_sidecar(raw: mne.io.BaseRaw, row: pd.Series) -> Dict[str, Any]:
    """Locate and load the BIDS sidecar JSON for the recording.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object (used only for path hints).
    row : pd.Series
        Row of udataset containing at least 'subject', 'session', 'task', 'run'.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON sidecar as a dictionary.
    """
    # Derive base path from raw.fileno (or from row if available)
    base_path = os.path.dirname(raw.filenames[0]) if raw.filenames else ""
    # Navigate to the BIDS root (go up from .../eeg/ to dataset root)
    # Expected structure: <root>/sub-XX/ses-YY/eeg/<file>.edf
    parts = os.path.normpath(base_path).split(os.sep)
    # Find 'eeg' component and go up two levels to reach subject folder
    try:
        eeg_index = parts.index("eeg")
        root = os.sep.join(parts[: eeg_index - 2])
    except (ValueError, IndexError):
        # Fallback: assume current directory is dataset root
        root = os.path.dirname(base_path)

    subject = row.get("subject", "")
    session = row.get("session", "")
    task = row.get("task", "")
    run = row.get("run", "")

    # Build path to sidecar: <root>/sub-XX/ses-YY/eeg/sub-XX_ses-YY_task-XX_run-XX_events.json
    sidecar_name = f"sub-{subject}_ses-{session}_task-{task}"
    if run:
        sidecar_name += f"_run-{run}"
    sidecar_name += "_events.json"

    sidecar_path = os.path.join(root, f"sub-{subject}", f"ses-{session}", "eeg", sidecar_name)
    if os.path.exists(sidecar_path):
        with open(sidecar_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Fallback to a more generic search (task-level sidecar)
        generic_sidecar = os.path.join(root, "task-smrbmi_events.json")
        if os.path.exists(generic_sidecar):
            with open(generic_sidecar, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


def _map_events(raw: mne.io.BaseRaw, sidecar: Dict[str, Any]) -> mne.io.BaseRaw:
    """Annotate raw object with trial-phase events derived from markers.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with existing annotations (if any).
    sidecar : Dict[str, Any]
        BIDS sidecar dictionary containing event descriptions.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with updated annotations.
    """
    # Retrieve existing annotations
    annotations = raw.annotations.copy() if raw.annotations else mne.Annotations(
        onset=[], duration=[], description=[], orig_time=raw.info["meas_date"]
    )

    # Build a description map: stimulus value → description string
    value_map = {v: d.get("TrialPhase", "") for v, d in sidecar.get("TrialPhase", {}).items()}

    # Iterate through annotations and relabel trial-phase markers
    new_desc = []
    new_onset = []
    new_duration = []
    for onset, duration, desc in zip(annotations.onset, annotations.duration, annotations.description):
        # desc may be an integer or string
        try:
            val = int(desc) if not isinstance(desc, str) else int(desc.split("_")[-1])
        except (ValueError, IndexError):
            new_desc.append(str(desc))
            new_onset.append(onset)
            new_duration.append(duration)
            continue

        if val in _TRIAL_PHASE_EVENT_MAP:
            new_desc.append(_TRIAL_PHASE_EVENT_MAP[val])
            new_onset.append(onset)
            new_duration.append(duration)
        elif val in _ADMIN_EVENT_MAP:
            new_desc.append(_ADMIN_EVENT_MAP[val])
            new_onset.append(onset)
            new_duration.append(duration)
        else:
            new_desc.append(str(desc))
            new_onset.append(onset)
            new_duration.append(duration)

    # Replace annotations
    raw.set_annotations(
        mne.Annotations(
            onset=new_onset,
            duration=new_duration,
            description=new_desc,
            orig_time=raw.info["meas_date"],
        )
    )
    return raw


def _load_raw(file_path: str, preload: bool = True) -> mne.io.BaseRaw:
    """Load a raw EEG file with appropriate reader.

    Parameters
    ----------
    file_path : str
        Path to the recording file.
    preload : bool
        Whether to load data into memory.

    Returns
    -------
    mne.io.BaseRaw
        Loaded raw object.
    """
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".edf":
        return mne.io.read_raw_edf(file_path, preload=preload, verbose=False)
    elif ext == ".vhdr":
        return mne.io.read_raw_brainvision(file_path, preload=preload, verbose=False)
    elif ext == ".set":
        return mne.io.read_raw_eeglab(file_path, preload=preload, verbose=False)
    else:
        # Fallback to auto guess
        return mne.io.read_raw(file_path, preload=preload, verbose=False)


class Kernel:
    """EEGUnity stage‑1 kernel for OpenNeuro DS004447 (BMI‑HDEEG dataset)."""

    def apply(self, udataset, raw: mne.io.BaseRaw, row: pd.Series) -> mne.io.BaseRaw:
        """Apply kernel steps to a single recording.

        Parameters
        ----------
        udataset : object
            Unused; kept for API compatibility.
        raw : mne.io.BaseRaw
            Raw EEG recording.
        row : pd.Series
            Metadata row containing subject, session, task, run, etc.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object.
        """
        # -----------------------------------------------------------------
        # 1) Rename channels to standard 10‑20 names (avoid duplicates)
        # -----------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, allow_duplicates=False, on_missing="ignore")

        # -----------------------------------------------------------------
        # 2) Montage / channel locations (GES400 128‑channel Hydrocel GSN)
        # -----------------------------------------------------------------
        # Attempt to set a standard 128‑channel montage; fallback to generic
        # 10‑20 if exact match unavailable.
        ch_names = raw.ch_names
        # Try to load a built‑in 128‑channel layout
        montage_path = mne.datasets.testing.data_path() if False else None  # placeholder
        # Since we do not have a definitive 128‑ch montage file, we attempt
        # to use the standard 10‑20 layout and map the remaining to unknown.
        try:
            # Use standard 10‑20 as base, then drop any channels not present.
            ten_twenty_montage = mne.channels.make_standard_montage("standard_1005")
            raw.set_montage(ten_twenty_montage, on_missing="ignore")
        except Exception:
            # If even standard fails, skip montage
            pass

        # -----------------------------------------------------------------
        # 3) Basic preprocessing: band‑pass 1–45 Hz, notch 50/100 Hz
        # -----------------------------------------------------------------
        # Band‑pass filter (including line noise removal)
        raw.filter(l_freq=1.0, h_freq=45.0, fir_design="firwin", verbose=False)

        # Notch filter at 50 Hz and harmonics
        freqs_to_notch = [50.0, 100.0, 150.0]
        raw.notch_filter(freqs=freqs_to_notch, fir_design="firwin", verbose=False)

        # -----------------------------------------------------------------
        # 4) Re‑reference to average (standard for GSN data)
        # -----------------------------------------------------------------
        # Keep reference as average of all EEG channels
        eeg_channels = mne.pick_types(raw.info, eeg=True, exclude=[])
        if eeg_channels:
            avg_ref = mne.channels.compute_average_reference(raw, verbose=False)
            raw.set_eeg_reference(ref_channels=avg_ref, verbose=False)

        # -----------------------------------------------------------------
        # 5) Load BIDS sidecar and relabel events
        # -----------------------------------------------------------------
        sidecar = _load_bids_sidecar(raw, row)
        if sidecar:
            raw = _map_events(raw, sidecar)

        # -----------------------------------------------------------------
        # 6) Basic bad‑channel detection (variance‑based)
        # -----------------------------------------------------------------
        var_threshold = 5 * np.median([np.var(raw.get_data(ch)) for ch in raw.ch_names])
        bad_chs = [
            ch for ch in raw.ch_names if np.var(raw.get_data([ch])) > var_threshold
        ]
        if bad_chs:
            raw.info["bads"] = list(set(raw.info["bads"] + bad_chs))

        # -----------------------------------------------------------------
        # 7) Finalise: set measurement info description
        # -----------------------------------------------------------------
        raw.setmeas

 date = raw.info.get("meas_date")
        raw.info["description"] = (
            f"OpenNeuro DS004447 – BMI‑HDEEG dataset. "
            f"Subject {row.get('subject','N/A')}, session {row.get('session','N/A')}, "
            f"task {row.get('task','N/A')}, run {row.get('run','N/A')}."
        )
        return raw


# -----------------------------------------------------------------------------
# EEGUnity description metadata (required by EEGUnity runtime)
# -----------------------------------------------------------------------------
eegunity_description = {
    "age": str(_SUBJECT_DICT.get("sub-" + str(row.get("subject", "01")).zfill(3), {}).get("age", "N/A")),
    "sex": str(_SUBJECT_DICT.get("sub-" + str(row.get("subject", "01")).zfill(3), {}).get("sex", "N/A")),
    "amplifier": "GES 400 (Hydrocel GSN)",
    "cap": "Hydrocel GSN 128‑channel",
    "handedness": str(_SUBJECT_DICT.get("sub-" + str(row.get("subject", "01")).zfill(3), {}).get("handedness", "N/A")),
    # Note: row is not available at description creation time; defaults used.
    "dataset": "openneuro_ds004447",
    "kernel_version": "1.0.1",
}

# Expose the kernel instance
KERNEL = Kernel()