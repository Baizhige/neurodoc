"""Base HDF5 torch Dataset with lazy per-worker file handle.

Subclasses implement `_build_index()` to populate `self.index` — a list of
`(source_group, flat_idx, label)` tuples where `flat_idx` points into the
flat `/data` array of the v2/v2.1 HDF5 file.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

import h5py
import numpy as np
import torch

_SUPPORTED_VERSIONS = {"2.0", "2.1"}


class BaseHDF5Dataset(torch.utils.data.Dataset):
    def __init__(
        self,
        h5_path: str,
        channels_select: Optional[List[str]] = None,
        max_len: int = 800,
        pad_to_multiple: Optional[int] = None,
    ) -> None:
        if not os.path.exists(h5_path):
            raise FileNotFoundError(f"HDF5 file not found: {h5_path}")

        self.h5_path = h5_path
        self.channels_select = channels_select
        self.max_len = max_len
        self.pad_to_multiple = pad_to_multiple

        self.index: list = []
        self._h5_file: Optional[h5py.File] = None
        self._ch_cache: dict = {}

        self._check_version_and_init_channels()
        self._build_index()

    def _check_version_and_init_channels(self) -> None:
        with h5py.File(self.h5_path, "r") as f:
            version = f.attrs.get("version")
            if version not in _SUPPORTED_VERSIONS:
                raise ValueError(
                    f"HDF5 '{self.h5_path}' version={version!r} is unsupported; "
                    f"expected one of {sorted(_SUPPORTED_VERSIONS)}."
                )
            if self.channels_select:
                ch_names = np.array(json.loads(f.attrs["ch_names"]))
                missing = [c for c in self.channels_select if c not in ch_names]
                if missing:
                    raise KeyError(f"Channels not in HDF5: {missing}")
                self._ch_cache[None] = [
                    int(np.where(ch_names == c)[0][0]) for c in self.channels_select
                ]

    def _build_index(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.index)

    def _get_h5_file(self) -> h5py.File:
        if self._h5_file is None:
            self._h5_file = h5py.File(self.h5_path, "r")
        return self._h5_file

    def _load_epoch(self, flat_idx: int) -> torch.Tensor:
        f = self._get_h5_file()
        epoch = f["data"][flat_idx]  # (n_ch, n_times)
        if self.channels_select:
            epoch = epoch[self._ch_cache[None], :]
        epoch = epoch[:, : self.max_len]
        if self.pad_to_multiple is not None:
            time_len = epoch.shape[-1]
            pad = (self.pad_to_multiple - time_len % self.pad_to_multiple) % self.pad_to_multiple
            if pad > 0:
                padding = [(0, 0)] * (epoch.ndim - 1) + [(0, pad)]
                epoch = np.pad(epoch, padding, mode="constant", constant_values=0)
        return torch.tensor(epoch, dtype=torch.float32)

    def get_ch_names(self) -> list:
        with h5py.File(self.h5_path, "r") as f:
            return json.loads(f.attrs["ch_names"])

    def close(self) -> None:
        h5 = getattr(self, "_h5_file", None)
        if h5 is not None:
            h5.close()
            self._h5_file = None

    def __getstate__(self):
        self.close()
        state = self.__dict__.copy()
        state["_h5_file"] = None
        return state

    def __setstate__(self, state) -> None:
        self.__dict__.update(state)
        self._h5_file = None

    def __del__(self) -> None:
        self.close()
