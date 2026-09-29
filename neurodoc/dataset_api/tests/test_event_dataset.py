from __future__ import annotations

from pathlib import Path

import pytest
import torch

from neurodoc.dataset_api import EventDataset
from neurodoc.dataset_api.tests._fixtures import make_synthetic_h5


@pytest.fixture
def h5_path(tmp_path: Path) -> Path:
    return make_synthetic_h5(
        tmp_path / "event.h5",
        sources=[
            {"group_name": "sub-01", "events": ["A", "B", "A", "C"],
             "source_attrs": {"age": "25"}},
            {"group_name": "sub-02", "events": ["B", "C", "A", "B"],
             "source_attrs": {"age": "31"}},
        ],
    )


def test_classification_maps_event_codes(h5_path: Path) -> None:
    ds = EventDataset(h5_path=str(h5_path),
                      events_map={"A": 0, "B": 1, "C": 2},
                      task_type="classification",
                      max_len=100)
    assert len(ds) == 8
    data, label, meta = ds[0]
    assert data.shape == (4, 100)
    assert data.dtype == torch.float32
    assert label.dtype == torch.long
    assert label.item() in (0, 1, 2)
    assert meta["source_group"] in ("sub-01", "sub-02")


def test_classification_filters_unknown_events(h5_path: Path) -> None:
    ds = EventDataset(h5_path=str(h5_path),
                      events_map={"A": 0, "B": 1},   # drops "C"
                      task_type="classification",
                      max_len=100)
    assert len(ds) == 6  # 8 total - 2 C-events
    for i in range(len(ds)):
        _, label, _ = ds[i]
        assert label.item() in (0, 1)


def test_regression_floats(h5_path: Path) -> None:
    ds = EventDataset(h5_path=str(h5_path),
                      events_map={"A": 0.1, "B": 0.5, "C": 0.9},
                      task_type="regression",
                      max_len=100)
    assert len(ds) == 8
    _, label, _ = ds[0]
    assert label.dtype == torch.float32


def test_channel_select_and_pad(h5_path: Path) -> None:
    ds = EventDataset(h5_path=str(h5_path),
                      events_map={"A": 0, "B": 1, "C": 2},
                      channels_select=["EEG0", "EEG2"],
                      max_len=50,
                      pad_to_multiple=64)
    data, _, _ = ds[0]
    assert data.shape == (2, 64)   # trim to 50 then pad to 64


def test_missing_channel_raises(h5_path: Path) -> None:
    with pytest.raises(KeyError):
        EventDataset(h5_path=str(h5_path),
                     events_map={"A": 0},
                     channels_select=["EEG_NONEXISTENT"])


def test_pickle_roundtrip_closes_handle(h5_path: Path) -> None:
    import pickle
    ds = EventDataset(h5_path=str(h5_path),
                      events_map={"A": 0, "B": 1, "C": 2})
    _ = ds[0]  # opens handle
    assert ds._h5_file is not None
    restored = pickle.loads(pickle.dumps(ds))
    assert restored._h5_file is None
    _, label, _ = restored[0]
    assert label.item() in (0, 1, 2)


def test_empty_events_map_rejected(h5_path: Path) -> None:
    with pytest.raises(ValueError):
        EventDataset(h5_path=str(h5_path), events_map={})


def test_bad_task_type_rejected(h5_path: Path) -> None:
    with pytest.raises(ValueError):
        EventDataset(h5_path=str(h5_path),
                     events_map={"A": 0},
                     task_type="segmentation")   # type: ignore[arg-type]
