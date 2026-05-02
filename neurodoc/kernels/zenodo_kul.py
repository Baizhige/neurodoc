"""Zenodo KUL - Auditory Attention Decoding (AAD) dataset kernel for EEGUnity.

Dataset: https://zenodo.org/records/4004271
Biesmans et al. (2017) — 15 subjects, dichotic listening AAD task.
Format: MATLAB .mat files, one file per subject (S1.mat … S15.mat).

MATLAB structure (simplify_cells=True):
  mat['trials'] — array of 20 trial dicts
  Each trial dict:
    ['RawData']['EegData']   — EEG data, shape (n_samples, 64), float64
    ['attended_ear']         — int: 1 = left, 2 = right
                               (fallback: field may be 'attend', 'trialinfo', etc.)

EEGUnity loads only trials[0].RawData.EegData into `raw`. This kernel replaces
`raw` with a new RawArray built from all 20 trials concatenated end-to-end and
adds per-trial annotations indicating the attended ear.

Annotation labels produced (matching analysis.md Event Structure):
  'attended_left'  — Subject attends to the left-ear speaker  (trial onset)
  'attended_right' — Subject attends to the right-ear speaker (trial onset)

Annotation duration = trial duration in seconds (n_samples / sfreq).
Channel names are set to standard 10-20 names for 64-channel BioSemi layout,
then montage is applied.

Source: Biesmans et al. (2017), DOI 10.1109/TBME.2019.2911728
Kernel added: 2026-04-09 — LLM-assisted, requires human review.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne
import numpy as np
import scipy.io as scio


_SFREQ = 128.0  # Hz (fixed by dataset)
_N_CHANNELS = 64

# Possible field names for the attention label (tried in order).
_ATTEND_FIELD_CANDIDATES = ["attended_ear", "attend", "attended_speaker", "trialinfo"]

_LABEL_MAP = {1: "attended_left", 2: "attended_right"}

# Standard BioSemi ActiveTwo 64-channel 10-20 layout names.
# Source: BioSemi 64-channel cap documentation, standard 10-20 system.
# Annotator: LLM, 2026-04-09
_BIOSEMI_64_CH_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
]


def _get_attended_ear(trial: dict) -> int | None:
    """Try common field names to extract the attended ear (1=left, 2=right)."""
    for field in _ATTEND_FIELD_CANDIDATES:
        val = trial.get(field)
        if val is None:
            continue
        try:
            v = int(np.asarray(val).flat[0])
            if v in (1, 2):
                return v
        except (TypeError, ValueError, IndexError):
            continue
    return None


@dataclass
class ZenodoKulKernel:
    """Kernel for the KU Leuven auditory attention decoding (AAD) dataset."""

    KERNEL_ID: str = "zenodo-kul-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        if not file_path.lower().endswith(".mat"):
            return raw

        try:
            mat = scio.loadmat(file_path, simplify_cells=True)
        except Exception:
            return raw

        trials = mat.get("trials")
        if trials is None or len(trials) == 0:
            return raw

        # Concatenate EEG data from all trials.
        eeg_blocks: list[np.ndarray] = []
        onsets: list[float] = []
        durations: list[float] = []
        descriptions: list[str] = []

        current_offset = 0.0

        for trial in trials:
            # Extract EEG data
            raw_data = trial.get("RawData", {})
            if isinstance(raw_data, dict):
                eeg = raw_data.get("EegData")
            else:
                # Some versions may store RawData directly as array
                eeg = None

            if eeg is None:
                # Try alternative field names
                for key in trial.keys():
                    if "eeg" in key.lower() or "data" in key.lower():
                        val = trial[key]
                        if isinstance(val, np.ndarray) and val.ndim == 2:
                            eeg = val
                            break

            if eeg is None or not isinstance(eeg, np.ndarray):
                continue

            # Ensure shape is (n_channels, n_samples)
            if eeg.shape[0] < eeg.shape[1]:
                # Likely (n_samples, n_channels), transpose
                eeg = eeg.T

            n_samples = eeg.shape[1]
            trial_duration = n_samples / _SFREQ

            # Determine attended ear
            attended = _get_attended_ear(trial)
            if attended is None:
                # Try nested in RawData
                if isinstance(raw_data, dict):
                    attended = _get_attended_ear(raw_data)
                if attended is None:
                    # Default to unknown, skip annotation
                    continue

            label = _LABEL_MAP.get(attended, "unknown")
            descriptions.append(label)
            onsets.append(current_offset)
            durations.append(trial_duration)

            eeg_blocks.append(eeg)
            current_offset += trial_duration

        if len(eeg_blocks) == 0:
            return raw

        # Concatenate all trials
        all_data = np.hstack(eeg_blocks)  # shape: (n_channels, total_samples)

        # Create info
        n_ch = all_data.shape[0]
        ch_names = [f"EEG-{i}" for i in range(n_ch)]  # Temporary names

        info = mne.create_info(
            ch_names=ch_names,
            sfreq=_SFREQ,
            ch_types="eeg",
        )

        new_raw = mne.io.RawArray(all_data, info, verbose=False)

        # Set standard channel names for 64-channel BioSemi
        if n_ch == 64:
            rename_map = {f"EEG-{i}": _BIOSEMI_64_CH_NAMES[i] for i in range(64)}
            new_raw.rename_channels(rename_map)

            # Set montage (channel rename BEFORE set_montage per requirement)
            try:
                montage = mne.channels.make_standard_montage("biosemi64")
                new_raw.set_montage(montage, match_case=False, on_missing="warn")
            except Exception:
                pass  # Montage not critical for processing

        # Add annotations
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        new_raw.set_annotations(annotations)

        # Build eegunity_description
        # No participants.tsv for this dataset; all demographic info unknown
        # Device info from paper: BioSemi ActiveTwo, standard 10-20 layout
        # Source: Biesmans et al. (2017), DOI 10.1109/TBME.2019.2911728
        # Annotator: LLM, 2026-04-09
        original_desc = raw.info.get("description", "") if hasattr(raw, "info") else ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "BioSemi ActiveTwo",  # inferred by LLM, needs human review
                "cap": "BioSemi 64-channel cap",   # inferred by LLM, needs human review
                "handedness": "unknown",
            },
        }
        new_raw.info["description"] = json.dumps(description_dict)

        return new_raw


KERNEL = ZenodoKulKernel()