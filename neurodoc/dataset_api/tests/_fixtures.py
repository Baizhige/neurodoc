"""Synthetic v2.1 HDF5 builder for unit tests.

Produces a minimal in-memory-ish file that mimics the on-disk schema used by
`h5EpochDatasetV2` plus the v2.1 additions (`misc_meta/*`, arbitrary source
attrs). Tests use this instead of depending on a real kernel + EEGUnity scan.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import h5py
import numpy as np


def make_synthetic_h5(
    path: Path,
    *,
    version: str = "2.1",
    n_channels: int = 4,
    n_times: int = 100,
    sfreq: float = 250.0,
    ch_names: Optional[List[str]] = None,
    sources: Sequence[Dict] = (),
    misc_channels: Optional[Dict[str, List[float]]] = None,
) -> Path:
    """Build a fake v2/v2.1 HDF5 file for testing.

    Parameters
    ----------
    sources : list of dicts, each describing one source_group:
        {
            "group_name": str,
            "events": List[str],                  # event name per epoch (len = N_g)
            "source_attrs": Dict[str, str|float], # written to source_meta/<g>.attrs
        }
    misc_channels : Optional mapping `{name: [val_per_epoch_total]}` with
        length equal to total epochs across all sources; written under
        /misc_meta/<name>. Only emitted when version=="2.1".
    """
    ch_names = ch_names or [f"EEG{i}" for i in range(n_channels)]
    path = Path(path)

    # --- Pass 1: build flat arrays ---
    all_epochs: List[np.ndarray] = []
    all_event_names: List[str] = []
    all_source_groups: List[str] = []
    source_attr_map: Dict[str, Dict] = {}

    rng = np.random.default_rng(42)
    for src in sources:
        g = src["group_name"]
        n_g = len(src["events"])
        epochs = rng.normal(size=(n_g, n_channels, n_times)).astype(np.float32)
        all_epochs.append(epochs)
        all_event_names.extend(src["events"])
        all_source_groups.extend([g] * n_g)
        source_attr_map[g] = src.get("source_attrs", {})

    data = np.concatenate(all_epochs, axis=0) if all_epochs else np.zeros(
        (0, n_channels, n_times), dtype=np.float32
    )

    # Build label_map (event_name -> int code)
    unique_events: List[str] = []
    for e in all_event_names:
        if e not in unique_events:
            unique_events.append(e)
    name_to_code = {name: i for i, name in enumerate(unique_events)}
    event_codes = np.array([name_to_code[e] for e in all_event_names], dtype=np.int16)

    # --- Pass 2: write HDF5 ---
    with h5py.File(path, "w") as f:
        f.attrs["version"] = version
        f.attrs["sfreq"] = float(sfreq)
        f.attrs["ch_names"] = json.dumps(ch_names)
        f.attrs["n_channels"] = int(n_channels)
        f.attrs["n_times"] = int(n_times)
        f.attrs["n_epochs_total"] = int(data.shape[0])
        f.attrs["label_map"] = json.dumps({str(v): k for k, v in name_to_code.items()})
        f.attrs["created_by"] = "EEGUnity-test"
        f.attrs["created_at"] = datetime.datetime.now().isoformat()

        f.create_dataset("data", data=data, dtype="float32")

        em = f.create_group("epoch_meta")
        em.create_dataset(
            "source_group",
            data=np.array(all_source_groups, dtype=object),
            dtype=h5py.string_dtype(encoding="utf-8"),
        )
        em.create_dataset("event_code", data=event_codes, dtype="int16")

        sm = f.create_group("source_meta")
        for g, attrs in source_attr_map.items():
            grp = sm.create_group(g)
            grp.attrs["sfreq"] = float(sfreq)
            grp.attrs["ch_names"] = json.dumps(ch_names)
            for k, v in attrs.items():
                grp.attrs[k] = str(v) if v is not None else "unknown"

        if version == "2.1" and misc_channels:
            mm = f.create_group("misc_meta")
            mm.attrs["names"] = json.dumps(list(misc_channels.keys()))
            for name, vals in misc_channels.items():
                vals_arr = np.asarray(vals, dtype=np.float32)
                if vals_arr.shape[0] != data.shape[0]:
                    raise ValueError(
                        f"misc channel '{name}' length {vals_arr.shape[0]} != "
                        f"n_epochs_total {data.shape[0]}"
                    )
                mm.create_dataset(name, data=vals_arr, dtype="float32")

    return path
