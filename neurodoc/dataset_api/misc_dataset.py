"""MISCDataset - torch Dataset for Label Route = misc tasks.

Requires HDF5 v2.1+ with a `/misc_meta/<misc_channel>` dataset of shape (N,).
Supports both regression and classification (rulebook Article 77, clause 6).
For classification the kernel must write pre-encoded integer class indices into
the misc channel; MISCDataset casts them to torch.long.
"""
from __future__ import annotations

import math
from typing import List, Literal, Optional

import h5py
import numpy as np
import torch

from .base import BaseHDF5Dataset


class MISCDataset(BaseHDF5Dataset):
    def __init__(
        self,
        h5_path: str,
        misc_channel: str,
        task_type: Literal["classification", "regression"] = "regression",
        channels_select: Optional[List[str]] = None,
        max_len: int = 800,
        pad_to_multiple: Optional[int] = None,
    ) -> None:
        if not misc_channel:
            raise ValueError("misc_channel must be a non-empty string.")
        if task_type not in ("classification", "regression"):
            raise ValueError(f"task_type must be classification|regression, got {task_type!r}.")
        self.misc_channel = misc_channel
        self.task_type = task_type
        self._label_dtype = torch.long if task_type == "classification" else torch.float32

        super().__init__(h5_path, channels_select, max_len, pad_to_multiple)

    def _build_index(self) -> None:
        with h5py.File(self.h5_path, "r") as f:
            if "misc_meta" not in f:
                raise KeyError(
                    f"HDF5 '{self.h5_path}' has no /misc_meta/ group. "
                    "The kernel must be rebuilt with misc_channels=[...] so per-epoch "
                    "MISC values are written (see kernel_requirements.required_native_misc / "
                    "derived_misc_channels)."
                )
            if self.misc_channel not in f["misc_meta"]:
                available = sorted(f["misc_meta"].keys())
                raise KeyError(
                    f"misc channel '{self.misc_channel}' not found under /misc_meta/. "
                    f"Available: {available}."
                )
            values = np.asarray(f[f"misc_meta/{self.misc_channel}"][:], dtype=np.float64)
            groups = f["epoch_meta/source_group"][:].astype(str)

        for flat_idx, (val, group) in enumerate(zip(values, groups)):
            if not math.isnan(float(val)):
                self.index.append((group, flat_idx, float(val)))

    def __getitem__(self, idx: int):
        group, flat_idx, label = self.index[idx]
        data = self._load_epoch(flat_idx)
        label_t = torch.tensor(label, dtype=self._label_dtype)
        meta = {"source_group": group, "flat_idx": flat_idx}
        return data, label_t, meta
