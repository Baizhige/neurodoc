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
Channel names are preserved as numeric strings "1" … "64" to match EEGUnity's
default naming for this dataset (no standard montage available in the file).

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

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
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

        sample_offset = 0.0

        for trial in trials:
            try:
                raw_data = trial["RawData"]["EegData"]  # (n_samples, 64)
            except (KeyError, TypeError):
                continue

            eeg = np.asarray(raw_data, dtype=np.float64)
            if eeg.ndim != 2 or eeg.shape[1] != _N_CHANNELS:
                # Transpose if shape is (64, n_samples)
                if eeg.ndim == 2 and eeg.shape[0] == _N_CHANNELS:
                    eeg = eeg.T
                else:
                    continue

            n_samples = eeg.shape[0]
            trial_dur = n_samples / _SFREQ

            attended = _get_attended_ear(trial)
            label = _LABEL_MAP.get(attended, "attended_unknown")

            onsets.append(sample_offset)
            durations.append(trial_dur)
            descriptions.append(label)

            eeg_blocks.append(eeg)
            sample_offset += trial_dur

        if not eeg_blocks:
            return raw

        # Build new continuous raw from all trials concatenated.
        eeg_concat = np.concatenate(eeg_blocks, axis=0)  # (total_samples, 64)
        eeg_T = eeg_concat.T  # (64, total_samples) — MNE convention

        # Preserve channel names from EEGUnity's existing raw if available,
        # otherwise fall back to "1" … "64".
        existing_names = raw.ch_names if len(raw.ch_names) == _N_CHANNELS else [
            str(i + 1) for i in range(_N_CHANNELS)
        ]
        ch_types = ["eeg"] * _N_CHANNELS
        info = mne.create_info(ch_names=existing_names, sfreq=_SFREQ, ch_types=ch_types)

        # Copy subject description metadata.
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "BioSemi ActiveTwo",
                "cap":       "64-channel, 10-20 system",
                "age":       "unknown",
                "sex":       "unknown",
                "handedness": "unknown",
            },
        }
        info["description"] = json.dumps(description_dict)

        new_raw = mne.io.RawArray(eeg_T, info, verbose=False)

        ann = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        new_raw.set_annotations(ann)

        return new_raw


KERNEL = ZenodoKulKernel()
