from __future__ import annotations

from pathlib import Path

import pytest
import torch

from eeg_kernel_agent.dataset_api import InfoDataset
from eeg_kernel_agent.dataset_api.tests._fixtures import make_synthetic_h5


@pytest.fixture
def h5_path(tmp_path: Path) -> Path:
    return make_synthetic_h5(
        tmp_path / "info.h5",
        sources=[
            {"group_name": "sub-01", "events": ["e", "e", "e"],
             "source_attrs": {"sex": "M", "age": "25", "p_factor": "1.42"}},
            {"group_name": "sub-02", "events": ["e", "e"],
             "source_attrs": {"sex": "F", "age": "31", "p_factor": "-0.18"}},
            {"group_name": "sub-03", "events": ["e", "e"],
             "source_attrs": {"sex": "M", "age": "28"}},  # p_factor missing
        ],
    )


def test_regression_broadcast(h5_path: Path) -> None:
    ds = InfoDataset(h5_path=str(h5_path),
                     info_field="p_factor",
                     task_type="regression",
                     max_len=100)
    # 3+2+2=7 epochs, sub-03 dropped (missing attr) → 3+2=5
    assert len(ds) == 5
    for i in range(len(ds)):
        _, label, meta = ds[i]
        assert label.dtype == torch.float32
        assert meta["source_group"] in ("sub-01", "sub-02")


def test_classification_with_info_map(h5_path: Path) -> None:
    ds = InfoDataset(h5_path=str(h5_path),
                     info_field="sex",
                     task_type="classification",
                     info_map={"M": 0, "F": 1},
                     max_len=100)
    assert len(ds) == 7  # all three sources have sex
    for i in range(len(ds)):
        _, label, _ = ds[i]
        assert label.dtype == torch.long
        assert label.item() in (0, 1)


def test_classification_requires_info_map(h5_path: Path) -> None:
    with pytest.raises(ValueError):
        InfoDataset(h5_path=str(h5_path),
                    info_field="sex",
                    task_type="classification",
                    info_map=None)


def test_unmapped_value_excluded(h5_path: Path) -> None:
    ds = InfoDataset(h5_path=str(h5_path),
                     info_field="sex",
                     task_type="classification",
                     info_map={"M": 0},   # F is unmapped → sub-02 dropped
                     max_len=100)
    assert len(ds) == 5  # 3 (sub-01) + 2 (sub-03) = 5; sub-02's 2 epochs dropped


def test_regression_parse_fail_excluded(tmp_path: Path) -> None:
    path = make_synthetic_h5(
        tmp_path / "bad_info.h5",
        sources=[
            {"group_name": "g1", "events": ["e"],
             "source_attrs": {"score": "3.14"}},
            {"group_name": "g2", "events": ["e"],
             "source_attrs": {"score": "not-a-number"}},
        ],
    )
    ds = InfoDataset(h5_path=str(path), info_field="score", task_type="regression")
    assert len(ds) == 1


def test_missing_info_field_yields_empty(h5_path: Path) -> None:
    ds = InfoDataset(h5_path=str(h5_path),
                     info_field="nonexistent_field",
                     task_type="regression")
    assert len(ds) == 0


def test_rejects_bad_task_type(h5_path: Path) -> None:
    with pytest.raises(ValueError):
        InfoDataset(h5_path=str(h5_path),
                    info_field="sex",
                    task_type="bogus")  # type: ignore[arg-type]
