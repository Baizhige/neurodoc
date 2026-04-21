"""EventDataset — torch Dataset for Label Route = event tasks.

Reads event codes from `/epoch_meta/event_code` and maps them to the caller's
label space via `events_map`. Classification → int; regression → float.
"""
from __future__ import annotations

import json
from typing import Dict, List, Literal, Optional, Union

import h5py
import torch

from .base import BaseHDF5Dataset

LabelValue = Union[int, float]


class EventDataset(BaseHDF5Dataset):
    def __init__(
        self,
        h5_path: str,
        events_map: Dict[str, LabelValue],
        task_type: Literal["classification", "regression"] = "classification",
        channels_select: Optional[List[str]] = None,
        max_len: int = 800,
        pad_to_multiple: Optional[int] = None,
    ) -> None:
        if not isinstance(events_map, dict) or not events_map:
            raise ValueError("events_map must be a non-empty Dict[str, int|float].")
        if task_type not in ("classification", "regression"):
            raise ValueError(f"task_type must be classification|regression, got {task_type!r}.")

        self.events_map = events_map
        self.task_type = task_type
        self._label_dtype = torch.long if task_type == "classification" else torch.float32

        super().__init__(h5_path, channels_select, max_len, pad_to_multiple)

    def _build_index(self) -> None:
        with h5py.File(self.h5_path, "r") as f:
            # label_map in HDF5 is {int_code: event_name}
            reverse = {int(k): v for k, v in json.loads(f.attrs["label_map"]).items()}
            code_to_label: Dict[int, LabelValue] = {
                code: self.events_map[name]
                for code, name in reverse.items()
                if name in self.events_map
            }
            if not code_to_label:
                return

            codes = f["epoch_meta/event_code"][:]
            groups = f["epoch_meta/source_group"][:].astype(str)

        for flat_idx, (code, group) in enumerate(zip(codes, groups)):
            code_int = int(code)
            if code_int in code_to_label:
                self.index.append((group, flat_idx, code_to_label[code_int]))

    def __getitem__(self, idx: int):
        group, flat_idx, label = self.index[idx]
        data = self._load_epoch(flat_idx)
        label_t = torch.tensor(label, dtype=self._label_dtype)
        meta = {"source_group": group, "flat_idx": flat_idx}
        return data, label_t, meta
