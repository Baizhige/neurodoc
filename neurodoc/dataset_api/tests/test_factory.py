from __future__ import annotations

from pathlib import Path

import pytest

from neurodoc.dataset_api import (
    DatasetDispatchError,
    EventDataset,
    InfoDataset,
    MISCDataset,
    build_dataset_from_task,
)
from neurodoc.dataset_api.tests._fixtures import make_synthetic_h5


# ---------- dry_run validation ----------

def test_event_classification_dry_run_ok() -> None:
    task = {
        "label_route": "event",
        "task_type": "classification",
        "target_rows": [
            {"event_id": "A", "y": 0, "meaning": "x"},
            {"event_id": "B", "y": 1, "meaning": "y"},
        ],
    }
    assert build_dataset_from_task(task, dry_run=True) is None


def test_event_regression_dry_run_ok() -> None:
    task = {
        "label_route": "event",
        "task_type": "regression",
        "target_rows": [{"event_id": "E", "value": 0.5, "meaning": "score"}],
    }
    assert build_dataset_from_task(task, dry_run=True) is None


def test_misc_dry_run_ok() -> None:
    task = {
        "label_route": "misc",
        "task_type": "regression",
        "label_field": "accuracy",
    }
    assert build_dataset_from_task(task, dry_run=True) is None


def test_info_classification_dry_run_ok() -> None:
    task = {
        "label_route": "info",
        "task_type": "classification",
        "label_field": "sex",
        "target_rows": [
            {"info_field": "sex", "value": "M", "y": 0, "meaning": "male"},
            {"info_field": "sex", "value": "F", "y": 1, "meaning": "female"},
        ],
    }
    assert build_dataset_from_task(task, dry_run=True) is None


def test_info_regression_dry_run_ok() -> None:
    task = {
        "label_route": "info",
        "task_type": "regression",
        "label_field": "age",
    }
    assert build_dataset_from_task(task, dry_run=True) is None


# ---------- dispatch errors ----------

def test_invalid_route() -> None:
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task({"label_route": "bogus", "task_type": "classification"},
                                dry_run=True)
    assert exc.value.kind == "schema"


def test_invalid_task_type() -> None:
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task({"label_route": "event", "task_type": "segmentation"},
                                dry_run=True)
    assert exc.value.kind == "schema"


def test_misc_classification_forbidden() -> None:
    task = {"label_route": "misc", "task_type": "classification", "label_field": "x"}
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "schema"
    assert "regression-only" in exc.value.message


def test_misc_missing_label_field() -> None:
    task = {"label_route": "misc", "task_type": "regression"}
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "schema"


def test_info_missing_label_field() -> None:
    task = {"label_route": "info", "task_type": "regression"}
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "schema"


def test_event_empty_target_rows() -> None:
    task = {"label_route": "event", "task_type": "classification", "target_rows": []}
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "bad_target_def"


def test_event_classification_missing_y() -> None:
    task = {
        "label_route": "event",
        "task_type": "classification",
        "target_rows": [{"event_id": "A", "meaning": "x"}],
    }
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "bad_target_def"


def test_info_classification_missing_rows() -> None:
    task = {
        "label_route": "info",
        "task_type": "classification",
        "label_field": "sex",
        "target_rows": [],
    }
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=True)
    assert exc.value.kind == "bad_target_def"


# ---------- real construction ----------

@pytest.fixture
def h5_event(tmp_path: Path) -> Path:
    return make_synthetic_h5(
        tmp_path / "f_event.h5",
        sources=[
            {"group_name": "g", "events": ["A", "B", "A"], "source_attrs": {}},
        ],
    )


@pytest.fixture
def h5_full(tmp_path: Path) -> Path:
    return make_synthetic_h5(
        tmp_path / "f_full.h5",
        sources=[
            {"group_name": "s1", "events": ["e", "e"],
             "source_attrs": {"sex": "M", "age": "25"}},
            {"group_name": "s2", "events": ["e", "e"],
             "source_attrs": {"sex": "F", "age": "30"}},
        ],
        misc_channels={"accuracy": [1.0, 0.0, 1.0, 1.0]},
    )


def test_factory_builds_event_dataset(h5_event: Path) -> None:
    task = {
        "label_route": "event",
        "task_type": "classification",
        "target_rows": [{"event_id": "A", "y": 0, "meaning": "m"},
                        {"event_id": "B", "y": 1, "meaning": "m"}],
    }
    ds = build_dataset_from_task(task, h5_path=str(h5_event), max_len=100)
    assert isinstance(ds, EventDataset)
    assert len(ds) == 3


def test_factory_builds_misc_dataset(h5_full: Path) -> None:
    task = {"label_route": "misc", "task_type": "regression", "label_field": "accuracy"}
    ds = build_dataset_from_task(task, h5_path=str(h5_full), max_len=100)
    assert isinstance(ds, MISCDataset)
    assert len(ds) == 4


def test_factory_builds_info_dataset(h5_full: Path) -> None:
    task = {
        "label_route": "info",
        "task_type": "classification",
        "label_field": "sex",
        "target_rows": [
            {"info_field": "sex", "value": "M", "y": 0, "meaning": "m"},
            {"info_field": "sex", "value": "F", "y": 1, "meaning": "f"},
        ],
    }
    ds = build_dataset_from_task(task, h5_path=str(h5_full), max_len=100)
    assert isinstance(ds, InfoDataset)
    assert len(ds) == 4


def test_factory_non_dry_run_without_h5_path_raises() -> None:
    task = {"label_route": "misc", "task_type": "regression", "label_field": "x"}
    with pytest.raises(DatasetDispatchError) as exc:
        build_dataset_from_task(task, dry_run=False)
    assert exc.value.kind == "schema"
    assert "h5_path" in exc.value.message
