from __future__ import annotations

import math
from pathlib import Path

import pytest
import torch

from eeg_kernel_agent.dataset_api import MISCDataset
from eeg_kernel_agent.dataset_api.tests._fixtures import make_synthetic_h5


@pytest.fixture
def h5_path(tmp_path: Path) -> Path:
    # 4 epochs total: 2 per source; accuracy vector aligns to data
    return make_synthetic_h5(
        tmp_path / "misc.h5",
        sources=[
            {"group_name": "sub-01", "events": ["target", "target"],
             "source_attrs": {"age": "25"}},
            {"group_name": "sub-02", "events": ["target", "target"],
             "source_attrs": {"age": "31"}},
        ],
        misc_channels={
            "accuracy": [1.0, 0.0, 1.0, 1.0],
            "rt_sec":   [0.42, 0.55, 0.48, math.nan],
        },
    )


def test_reads_misc_values(h5_path: Path) -> None:
    ds = MISCDataset(h5_path=str(h5_path), misc_channel="accuracy", max_len=100)
    assert len(ds) == 4
    labels = [float(ds[i][1].item()) for i in range(len(ds))]
    assert labels == [1.0, 0.0, 1.0, 1.0]

    data, label, meta = ds[0]
    assert data.shape == (4, 100)
    assert label.dtype == torch.float32
    assert "source_group" in meta


def test_nan_values_excluded(h5_path: Path) -> None:
    ds = MISCDataset(h5_path=str(h5_path), misc_channel="rt_sec", max_len=100)
    assert len(ds) == 3   # one nan filtered out
    for i in range(len(ds)):
        _, label, _ = ds[i]
        assert not math.isnan(label.item())


def test_missing_misc_channel_raises(h5_path: Path) -> None:
    with pytest.raises(KeyError) as exc:
        MISCDataset(h5_path=str(h5_path), misc_channel="not_a_channel")
    assert "Available" in str(exc.value)


def test_missing_misc_meta_group_raises(tmp_path: Path) -> None:
    # Build v2.1 file without misc_channels → /misc_meta/ absent
    path = make_synthetic_h5(
        tmp_path / "no_misc.h5",
        sources=[{"group_name": "g", "events": ["e"], "source_attrs": {}}],
    )
    with pytest.raises(KeyError) as exc:
        MISCDataset(h5_path=str(path), misc_channel="accuracy")
    assert "/misc_meta/" in str(exc.value)


def test_rejects_empty_misc_channel() -> None:
    with pytest.raises(ValueError):
        MISCDataset(h5_path="unused", misc_channel="")
