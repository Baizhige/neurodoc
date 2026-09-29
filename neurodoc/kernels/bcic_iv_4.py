"""BCI Competition IV Dataset 4 kernel for EEGUnity.

The public files are MATLAB ``sub*_comp.mat`` files. Each file contains:

- ``train_data``: first 400 s of ECoG data, shape time x channels.
- ``test_data``: final 200 s of ECoG data, shape time x channels.
- ``train_dg``: five data-glove finger position traces for ``train_data``.

This is an actual finger-movement ECoG regression dataset, not a motor imagery
dataset. The public competition release does not include cue onset markers or
finger-class event codes, so this kernel only emits administrative segment
annotations and exposes the continuous data-glove traces as ``misc`` channels.
The withheld test labels are represented as NaN to keep them out of supervised
training instead of silently treating them as zeros.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple

import mne
import numpy as np
import scipy.io as sio


_DATASET_ID = "bcic_iv_4"
_SFREQ = 1000.0
_EXPECTED_TRAIN_SAMPLES = 400_000
_EXPECTED_TEST_SAMPLES = 200_000
_FINGER_NAMES = ["finger1", "finger2", "finger3", "finger4", "finger5"]
_FINGER_LABELS = {
    "finger1": "thumb",
    "finger2": "index",
    "finger3": "middle",
    "finger4": "ring",
    "finger5": "little",
}


def _row_get(row, *keys: str) -> str:
    if isinstance(row, (str, os.PathLike)):
        return os.fspath(row)

    for key in keys:
        try:
            value = row.get(key)
        except AttributeError:
            try:
                value = row[key]
            except Exception:
                value = None
        if value not in (None, ""):
            return str(value)
    return ""


def _get_file_path(row) -> str:
    return _row_get(row, "File Path", "file_path", "filepath", "path")


def _subject_id_from_path(file_path: str) -> str:
    match = re.search(r"(sub\d+)", Path(file_path).name, flags=re.IGNORECASE)
    return match.group(1).lower() if match else "unknown"


def _load_arrays(file_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mat = sio.loadmat(file_path, simplify_cells=True)
    required = ("train_data", "test_data", "train_dg")
    missing = [name for name in required if name not in mat]
    if missing:
        raise ValueError(f"{Path(file_path).name} is missing required arrays: {missing}")

    train_data = np.asarray(mat["train_data"], dtype=np.float64)
    test_data = np.asarray(mat["test_data"], dtype=np.float64)
    train_dg = np.asarray(mat["train_dg"], dtype=np.float64)

    if train_data.ndim != 2 or test_data.ndim != 2 or train_dg.ndim != 2:
        raise ValueError(f"Unexpected array dimensions in {file_path}")
    if train_data.shape[1] != test_data.shape[1]:
        raise ValueError(f"train_data/test_data channel counts differ in {file_path}")
    if train_dg.shape != (train_data.shape[0], len(_FINGER_NAMES)):
        raise ValueError(f"train_dg does not align with train_data in {file_path}")

    return train_data, test_data, train_dg


def _make_description(
    file_path: str,
    subject_id: str,
    n_ecog_channels: int,
    train_samples: int,
    test_samples: int,
) -> str:
    eegunity_description: Dict[str, object] = {
        "dataset": _DATASET_ID,
        "subject_id": subject_id,
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "device": "BCI2000 acquisition with Synamps2 amplifier",
        "amplifier": "Synamps2 (Neuroscan)",
        "cap": "subdural ECoG electrode grid/array (Ad-Tech)",
        "recording_type": "ECoG",
        "reference": "scalp reference and ground before common-average rereferencing",
        "sampling_rate_hz": _SFREQ,
        "bandpass_hz": "0.15-200",
        "ecog_channel_count": str(n_ecog_channels),
        "train_duration_sec": f"{train_samples / _SFREQ:g}",
        "test_duration_sec": f"{test_samples / _SFREQ:g}",
        "finger_label_channels": ",".join(_FINGER_NAMES),
        "finger_label_names": ",".join(_FINGER_LABELS[name] for name in _FINGER_NAMES),
        "finger_label_valid_segment": "train_segment",
        "test_label_policy": "withheld in public release; misc finger values are NaN",
        "data_glove_native_rate_hz": "25",
        "data_glove_release_rate_hz": "1000",
        "data_glove_lag_sec": "0.037",
        "source_file": Path(file_path).name,
    }
    return json.dumps(
        {
            "original_description": "",
            "eegunity_description": eegunity_description,
        },
        separators=(",", ":"),
    )


def _build_raw_from_mat(file_path: str) -> mne.io.BaseRaw:
    train_data, test_data, train_dg = _load_arrays(file_path)
    subject_id = _subject_id_from_path(file_path)

    n_train_samples, n_ecog_channels = train_data.shape
    n_test_samples = test_data.shape[0]
    if n_train_samples != _EXPECTED_TRAIN_SAMPLES:
        raise ValueError(f"Unexpected train sample count in {file_path}: {n_train_samples}")
    if n_test_samples != _EXPECTED_TEST_SAMPLES:
        raise ValueError(f"Unexpected test sample count in {file_path}: {n_test_samples}")

    ecog_data = np.concatenate([train_data, test_data], axis=0).T
    withheld_test_dg = np.full(
        (n_test_samples, len(_FINGER_NAMES)), np.nan, dtype=np.float64
    )
    finger_data = np.concatenate([train_dg, withheld_test_dg], axis=0).T

    ch_names = [f"ECoG{i + 1:03d}" for i in range(n_ecog_channels)] + _FINGER_NAMES
    ch_types = ["ecog"] * n_ecog_channels + ["misc"] * len(_FINGER_NAMES)
    info = mne.create_info(ch_names=ch_names, sfreq=_SFREQ, ch_types=ch_types)
    raw = mne.io.RawArray(np.vstack([ecog_data, finger_data]), info, verbose=False)

    train_duration = n_train_samples / _SFREQ
    raw.set_annotations(
        mne.Annotations(
            onset=[0.0, train_duration],
            duration=[train_duration, 0.0],
            description=["train_segment", "test_segment_onset"],
        )
    )
    raw.info["description"] = _make_description(
        file_path=file_path,
        subject_id=subject_id,
        n_ecog_channels=n_ecog_channels,
        train_samples=n_train_samples,
        test_samples=n_test_samples,
    )
    return raw


def _is_kernel_built_raw(raw) -> bool:
    if raw is None:
        return False

    try:
        n_data_channels = int(raw.get_data().shape[0])
        if n_data_channels != len(raw.ch_names):
            return False

        has_finger_channels = all(name in raw.ch_names for name in _FINGER_NAMES)
        has_segment_markers = {"train_segment", "test_segment_onset"}.issubset(
            {str(desc) for desc in raw.annotations.description}
        )
        description = json.loads(raw.info.get("description", "") or "{}")
        dataset = description.get("eegunity_description", {}).get("dataset")

        # Some intermediate loaders can carry the finger channel names in info/ch_names
        # without actually materializing the misc data rows yet. Require the picks to be
        # readable as real channels before accepting the raw as fully kernel-built.
        for name in _FINGER_NAMES:
            picked = raw.get_data(picks=[name])
            if picked.shape[0] != 1 or picked.shape[1] != raw.n_times:
                return False
    except Exception:
        return False

    return has_finger_channels and has_segment_markers and dataset == _DATASET_ID


class BCICIV4Kernel:
    """Stage-1 kernel for BCI Competition IV Dataset 4."""

    KERNEL_ID = _DATASET_ID
    HANDLES_UNAVAILABLE = True

    def load(self, *args) -> mne.io.BaseRaw:
        row = args[-1]
        file_path = _get_file_path(row)
        if not file_path:
            raise ValueError("No file path provided for bcic_iv_4 kernel load()")
        return _build_raw_from_mat(file_path)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        if _is_kernel_built_raw(raw):
            return raw

        file_path = _get_file_path(row)
        if not file_path:
            return raw

        # The generic MATLAB loader can miss train_dg, so rebuild from the
        # authoritative arrays whenever a file path is available.
        return _build_raw_from_mat(file_path)


KERNEL = BCICIV4Kernel()
