"""InfoDataset — torch Dataset for Label Route = info tasks.

Reads a subject-level attribute from `/source_meta/<group>/attrs[info_field]`
and broadcasts it to every epoch belonging to that source.

Classification → `info_map` maps raw attr value (string) to int class index.
Regression     → raw attr value is parsed with `float()`.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

import h5py
import torch

from .base import BaseHDF5Dataset


class InfoDataset(BaseHDF5Dataset):
    def __init__(
        self,
        h5_path: str,
        info_field: str,
        task_type: Literal["classification", "regression"] = "classification",
        info_map: Optional[Dict[str, int]] = None,
        channels_select: Optional[List[str]] = None,
        max_len: int = 800,
        pad_to_multiple: Optional[int] = None,
    ) -> None:
        if not info_field:
            raise ValueError("info_field must be a non-empty string.")
        if task_type not in ("classification", "regression"):
            raise ValueError(f"task_type must be classification|regression, got {task_type!r}.")
        if task_type == "classification" and not info_map:
            raise ValueError("info_map is required for classification tasks.")

        self.info_field = info_field
        self.task_type = task_type
        self.info_map = info_map or {}
        self._label_dtype = torch.long if task_type == "classification" else torch.float32

        self._skipped_sources: list = []

        super().__init__(h5_path, channels_select, max_len, pad_to_multiple)

    def _build_index(self) -> None:
        with h5py.File(self.h5_path, "r") as f:
            source_labels: Dict[str, object] = {}
            for group_name, group in f["source_meta"].items():
                if self.info_field not in group.attrs:
                    self._skipped_sources.append((group_name, "attr_missing"))
                    continue
                raw = group.attrs[self.info_field]
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                raw_str = str(raw).strip()
                if raw_str == "" or raw_str.lower() in ("unknown", "nan", "n/a"):
                    self._skipped_sources.append((group_name, f"attr_blank:{raw_str!r}"))
                    continue
                try:
                    if self.task_type == "classification":
                        if raw_str not in self.info_map:
                            self._skipped_sources.append((group_name, f"unmapped:{raw_str!r}"))
                            continue
                        source_labels[group_name] = int(self.info_map[raw_str])
                    else:
                        source_labels[group_name] = float(raw_str)
                except (ValueError, TypeError):
                    self._skipped_sources.append((group_name, f"parse_fail:{raw_str!r}"))
                    continue

            if not source_labels:
                return

            groups = f["epoch_meta/source_group"][:].astype(str)

        for flat_idx, group in enumerate(groups):
            if group in source_labels:
                self.index.append((group, flat_idx, source_labels[group]))

    def __getitem__(self, idx: int):
        group, flat_idx, label = self.index[idx]
        data = self._load_epoch(flat_idx)
        label_t = torch.tensor(label, dtype=self._label_dtype)
        meta = {"source_group": group, "flat_idx": flat_idx}
        return data, label_t, meta
