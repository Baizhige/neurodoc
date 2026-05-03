"""Physionet UCD Sleep Apnea Database stage1 kernel for EEGUnity.

Sleep stage encoding in _stage.txt (R&K system, one integer per 30-second epoch):
  0 → Sleep stage W   (Wake)
  1 → Sleep stage 1   (NREM Stage 1)
  2 → Sleep stage 2   (NREM Stage 2)
  3 → Sleep stage 3   (NREM Stage 3, slow-wave sleep)
  4 → Sleep stage 4   (NREM Stage 4, deep SWS)
  5 → Sleep stage REM (REM sleep)
  8 → Sleep stage 8   (undefined / movement artifact epoch)

_lifecard.edf files (ECG-only) are skipped — no annotations applied.
Subject demographics are available in SubjectDetails.xls but not parsed here
(individual subject-to-file mapping is not in the public EDF headers).

Source: https://physionet.org/content/ucddb/1.0.0/
Kernel added: 2026-04-09 — LLM-assisted, requires human review.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import mne
import numpy as np


_STAGE_MAP = {
    0: "Sleep stage W",
    1: "Sleep stage 1",
    2: "Sleep stage 2",
    3: "Sleep stage 3",
    4: "Sleep stage 4",
    5: "Sleep stage REM",
    8: "Sleep stage 8",
}

_EPOCH_DURATION = 30.0  # seconds per epoch (fixed by dataset)
_RESP_EVENT_RE = re.compile(r"^\s*(\d{2}:\d{2}:\d{2})\s+([A-Z-]+)\s+\S*\s+(\d+)\b")

# Source: dataset_document/physionet_ucddb/analysis.md and UCDDB respiratory event files
# Annotator: GPT-5 Codex, 2026-05-03 - needs human review
_APNEA_POSITIVE_TYPES = {
    "APNEA-O",
    "APNEA-C",
    "APNEA-M",
    "HYP-O",
    "HYP-C",
    "HYP-M",
}


def _resp_event_path(file_path: str) -> str:
    """Map ucddbXXX.rec -> ucddbXXX_respevt.txt."""
    stem, _ = os.path.splitext(file_path)
    return f"{stem}_respevt.txt"


def _hhmmss_to_seconds(value: str) -> float:
    hh, mm, ss = value.split(":")
    return int(hh) * 3600 + int(mm) * 60 + int(ss)


def _clock_seconds_relative_to_meas_date(meas_date, clock_str: str) -> float:
    """Convert a clock time like HH:MM:SS to seconds since recording start."""
    if meas_date is None:
        return _hhmmss_to_seconds(clock_str)

    if meas_date.tzinfo is None:
        meas_date = meas_date.replace(tzinfo=timezone.utc)
    else:
        meas_date = meas_date.astimezone(timezone.utc)

    event_clock = datetime.strptime(clock_str, "%H:%M:%S").time()
    event_time = datetime.combine(meas_date.date(), event_clock).replace(tzinfo=timezone.utc)
    if event_time < meas_date:
        event_time += timedelta(days=1)
    return (event_time - meas_date).total_seconds()


def _extract_apnea_intervals(resp_path: str, meas_date) -> list[tuple[float, float]]:
    """Parse positive apnea/hypopnea events as recording-relative intervals."""
    if not os.path.exists(resp_path):
        return []

    intervals: list[tuple[float, float]] = []
    with open(resp_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = _RESP_EVENT_RE.match(line)
            if not m:
                continue
            start_str, event_type, duration_str = m.groups()
            if event_type not in _APNEA_POSITIVE_TYPES:
                continue
            duration_sec = float(duration_str)
            if duration_sec <= 0:
                continue
            start_sec = _clock_seconds_relative_to_meas_date(meas_date, start_str)
            intervals.append((start_sec, start_sec + duration_sec))
    return intervals


def _add_misc_channel(raw: mne.io.BaseRaw, name: str, values: np.ndarray) -> mne.io.BaseRaw:
    """Append a misc channel with sample-aligned float values."""
    if name in raw.ch_names:
        raw.drop_channels([name])

    misc_info = mne.create_info(
        ch_names=[name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    misc_raw = mne.io.RawArray(values.reshape(1, -1), misc_info, first_samp=raw.first_samp, verbose=False)
    misc_raw.set_meas_date(raw.info.get("meas_date"))
    raw.add_channels([misc_raw], force_update_info=True)
    raw.set_channel_types({name: "misc"})
    return raw


def _build_apnea_label_channel(raw: mne.io.BaseRaw, resp_path: str) -> np.ndarray:
    """Return sample-wise apnea_label values.

    Values are 1 during positive apnea/hypopnea intervals, 0 otherwise.
    If the respiratory sidecar is missing, return all-NaN so downstream code
    can treat this source file as unlabeled instead of fabricating negatives.
    """
    n_samples = raw.n_times
    sfreq = float(raw.info["sfreq"])

    if not os.path.exists(resp_path):
        return np.full(n_samples, np.nan, dtype=np.float64)

    values = np.zeros(n_samples, dtype=np.float64)
    for start_sec, end_sec in _extract_apnea_intervals(resp_path, raw.info.get("meas_date")):
        start_idx = max(0, int(np.floor(start_sec * sfreq)))
        end_idx = min(n_samples, int(np.ceil(end_sec * sfreq)))
        if start_idx < end_idx:
            values[start_idx:end_idx] = 1.0
    return values


def _load_rec_preloaded(file_path: str) -> mne.io.BaseRaw:
    """Reload a .rec file as EDF with data preloaded into memory."""
    with open(file_path, "rb") as fh:
        raw_bytes = fh.read()

    with tempfile.NamedTemporaryFile(suffix=".edf", delete=False) as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    try:
        return mne.io.read_raw_edf(tmp_path, preload=True, verbose=False)
    finally:
        os.remove(tmp_path)


def _ensure_loaded(raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
    """Load data only when a derived misc channel must be appended."""
    if not getattr(raw, "preload", False):
        if str(file_path).lower().endswith(".rec"):
            return _load_rec_preloaded(file_path)
        raw.load_data()
    return raw


@dataclass
class PhysionetUcddbKernel:
    """Stage1 kernel for the physionet-ucddb dataset."""

    KERNEL_ID: str = "physionet-ucddb-stage1"
    required_info_fields: list = None
    required_native_misc: list = None
    derived_misc_channels: list = None

    def __post_init__(self):
        if self.required_info_fields is None:
            self.required_info_fields = []
        if self.required_native_misc is None:
            self.required_native_misc = []
        if self.derived_misc_channels is None:
            self.derived_misc_channels = ["apnea_label"]

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        file_name = os.path.basename(file_path)
        resp_path = _resp_event_path(file_path)

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap":       "unknown",
                "age":       "unknown",
                "sex":       "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # _lifecard.edf files are ECG-only; skip annotation injection.
        if "_lifecard" in file_name:
            raw.set_annotations(mne.Annotations([], [], []))
            return raw

        # Companion stage file: ucddbXXX.rec → ucddbXXX_stage.txt
        stage_path = file_path.replace(".rec", "_stage.txt")
        raw = _ensure_loaded(raw, file_path)
        raw.info["description"] = json.dumps(description_dict)
        if not os.path.exists(stage_path):
            raw = _add_misc_channel(
                raw,
                "apnea_label",
                _build_apnea_label_channel(raw, resp_path),
            )
            return raw

        # Parse stage file — one integer per line, each = 30-second epoch.
        onsets, durations, descriptions = [], [], []
        with open(stage_path, "r") as fh:
            for epoch_idx, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                try:
                    code = int(line)
                except ValueError:
                    continue
                label = _STAGE_MAP.get(code)
                if label is None:
                    continue
                onsets.append(epoch_idx * _EPOCH_DURATION)
                durations.append(_EPOCH_DURATION)
                descriptions.append(label)

        raw.set_annotations(
            mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
        )
        raw = _add_misc_channel(
            raw,
            "apnea_label",
            _build_apnea_label_channel(raw, resp_path),
        )
        return raw


KERNEL = PhysionetUcddbKernel()
