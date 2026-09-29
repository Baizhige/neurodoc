"""OpenNeuro DS001849 stage-1 kernel for EEGUnity.

RS_TMSEEG_Data contains resting-state TMS-EEG recordings in EEGLAB
``.set/.fdt`` format. The native annotations contain TMS pulse triggers
(``R128``) and EEGLAB boundary markers. Site and active/sham condition labels
are encoded by the BIDS ``acq-`` entity in each filename.

Dataset evidence used by this kernel:
- task-tmseegrest_eeg.json: 30 EEG channels, 5000 Hz, Brain Vision, 10-20.
- per-file *_channels.tsv: explicit channel names and EEG channel type.
- BIDS filename acq-* entity: dlpfc/m1/ppc site and active/sham condition.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import mne
import pandas as pd


_VALID_ACQ_LABELS = {
    "dlpfcactive",
    "dlpfcsham",
    "m1active",
    "m1sham",
    "ppcactive",
    "ppcsham",
}


def _row_get(row, *keys: str) -> str:
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


def _find_dataset_root(file_path: str) -> Optional[Path]:
    current = Path(file_path).resolve().parent
    while True:
        if (current / "dataset_description.json").is_file():
            return current
        if current.parent == current:
            return None
        current = current.parent


def _task_name_from_path(file_path: str) -> Optional[str]:
    match = re.search(r"_task-([^_]+)", os.path.basename(file_path))
    return match.group(1) if match else None


def _find_channels_tsv(file_path: str) -> Optional[Path]:
    path = Path(file_path)
    stem = path.stem
    if stem.endswith("_eeg"):
        sibling = path.with_name(stem[:-4] + "_channels.tsv")
        if sibling.is_file():
            return sibling
    sibling = path.with_name(stem + "_channels.tsv")
    return sibling if sibling.is_file() else None


def _find_eeg_json(file_path: str) -> Optional[Path]:
    root = _find_dataset_root(file_path)
    task = _task_name_from_path(file_path)
    if root and task:
        candidate = root / f"task-{task}_eeg.json"
        if candidate.is_file():
            return candidate

    path = Path(file_path)
    stem = path.stem
    if stem.endswith("_eeg"):
        sibling = path.with_name(stem[:-4] + "_eeg.json")
        if sibling.is_file():
            return sibling
    return None


def _read_json(path: Optional[Path]) -> Dict[str, object]:
    if not path:
        return {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _extract_subject_id(file_path: str) -> str:
    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else "unknown"


def _extract_acq_label(file_path: str) -> str:
    match = re.search(r"_acq-([^_]+)", os.path.basename(file_path))
    if not match:
        return "unknown"
    label = match.group(1).lower()
    return label if label in _VALID_ACQ_LABELS else "unknown"


def _split_acq_label(acq_label: str) -> Tuple[str, str]:
    if acq_label == "unknown":
        return "unknown", "unknown"
    for condition in ("active", "sham"):
        if acq_label.endswith(condition):
            return acq_label[: -len(condition)], condition
    return "unknown", "unknown"


def _set_channel_types_from_sidecar(raw: mne.io.BaseRaw, file_path: str) -> None:
    channels_path = _find_channels_tsv(file_path)
    if not channels_path:
        return

    try:
        channels_df = pd.read_csv(channels_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return

    if "name" not in channels_df.columns or "type" not in channels_df.columns:
        return

    raw_names = set(raw.ch_names)
    channel_types: Dict[str, str] = {}
    for _, channel in channels_df.iterrows():
        name = str(channel.get("name", "")).strip()
        kind = str(channel.get("type", "")).strip().upper()
        if name in raw_names and kind == "EEG":
            channel_types[name] = "eeg"

    if channel_types:
        raw.set_channel_types(channel_types)


def _set_montage(raw: mne.io.BaseRaw) -> None:
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass


class OpenNeuroDS001849Kernel:
    """Stage-1 kernel for OpenNeuro ds001849."""

    KERNEL_ID = "openneuro_ds001849"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        subject_id = _extract_subject_id(file_path) if file_path else "unknown"
        acq_label = _extract_acq_label(file_path) if file_path else "unknown"
        tms_site, stimulation_condition = _split_acq_label(acq_label)

        eeg_json = _read_json(_find_eeg_json(file_path)) if file_path else {}
        manufacturer = str(eeg_json.get("Manufacturer", "Brain Vision")).strip() or "Brain Vision"
        eeg_channel_count = eeg_json.get("EEGChannelCount", 30)
        placement = str(eeg_json.get("EEGPlacementScheme", "10-20")).strip() or "10-20"
        reference = str(eeg_json.get("EEGReference", "unknown")).strip() or "unknown"
        task_name = str(eeg_json.get("TaskName", "tmseegrest")).strip() or "tmseegrest"

        if file_path:
            # Channel names/types come directly from each *_channels.tsv file.
            # No speculative rename is performed.
            _set_channel_types_from_sidecar(raw, file_path)
            _set_montage(raw)

        original_description = raw.info.get("description", "") or ""
        eegunity_description = {
            "subject_id": subject_id,
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "device": manufacturer,
            "amplifier": manufacturer,
            "cap": f"{eeg_channel_count}-channel {placement} EEG cap",
            "eeg_reference": reference,
            "task": task_name,
            "acq": acq_label,
            "tms_site": tms_site,
            "stimulation_condition": stimulation_condition,
            "site_condition": acq_label,
        }

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenNeuroDS001849Kernel()
