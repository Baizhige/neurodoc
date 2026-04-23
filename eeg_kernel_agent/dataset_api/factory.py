"""Dispatch a parsed Task block to the correct Dataset class.

The task dict shape mirrors `parseTasks` output in app/index.html and
`task_synthesizer_v2` kernel_requirements. Expected keys:

    {
        "label_route":        "event" | "misc" | "info",
        "task_type":          "classification" | "regression",
        "label_field":        Optional[str],     # required for misc/info
        "target_rows":        List[Dict],        # Target Definition rows
        # target_rows schema by (route, task_type):
        #   event/classification: {"event_id": str, "y": int | str, "meaning": str}
        #   event/regression:     {"event_id": str, "value": float, "meaning": str}
        #   misc/regression:      {"misc_channel": str, "value": str, "notes": str}  # 1 row
        #   info/classification:  {"info_field": str, "value": str, "y": int, "meaning": str}
        #   info/regression:      {"info_field": str, "range": str, "notes": str}    # 1 row
    }
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import BaseHDF5Dataset
from .event_dataset import EventDataset
from .info_dataset import InfoDataset
from .misc_dataset import MISCDataset

_VALID_ROUTES = ("event", "misc", "info")
_VALID_TYPES = ("classification", "regression")


@dataclass
class DatasetDispatchError(Exception):
    kind: str        # "schema" | "missing_event" | "missing_misc" | "missing_info" | "bad_target_def"
    message: str
    label_route: Optional[str] = None
    label_field: Optional[str] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.kind}] {self.message}"


def _require(cond: bool, kind: str, msg: str, **extra) -> None:
    if not cond:
        raise DatasetDispatchError(kind=kind, message=msg, **extra)


def _validate_zero_indexed_sequential(y_values, where: str) -> None:
    """Enforce that the distinct y values form set(range(N)). Many-to-one OK.

    Rejects: non-int y (should be caught upstream), gapped y ({0, 2}),
    offset y ({1, 2}), empty. Runs at factory dry_run so detect.py and
    reconcile both get the check for free.
    """
    s = set(y_values)
    if not s:
        raise DatasetDispatchError(
            kind="bad_target_def",
            message=f"{where}: no y values after parsing.",
        )
    expected = set(range(len(s)))
    if s != expected:
        raise DatasetDispatchError(
            kind="bad_target_def",
            message=(f"{where}: distinct y values {sorted(s)} are not 0-based sequential "
                     f"(expected 0..{len(s)-1}; many-to-one merges OK but no gaps or offset)."),
        )


def _parse_events_map(task: Dict[str, Any]) -> Dict[str, Any]:
    rows = task.get("target_rows") or []
    _require(bool(rows), "bad_target_def", "event task has empty Target Definition.")
    events_map: Dict[str, Any] = {}
    task_type = task["task_type"]
    for r in rows:
        eid = r.get("event_id")
        _require(bool(eid), "bad_target_def", f"event row missing event_id: {r}")
        if task_type == "classification":
            y = r.get("y")
            _require(y is not None, "bad_target_def", f"classification row missing y: {r}")
            try:
                events_map[eid] = int(y)
            except (ValueError, TypeError):
                raise DatasetDispatchError(
                    kind="bad_target_def",
                    message=(f"classification row has non-int y={y!r} in row {r}; "
                             f"y must be a 0-based int (rulebook v3.2)."),
                )
        else:
            v = r.get("value")
            _require(v is not None, "bad_target_def", f"regression row missing value: {r}")
            events_map[eid] = float(v)
    if task_type == "classification":
        _validate_zero_indexed_sequential(
            events_map.values(), where="event-classification task",
        )
    return events_map


def _parse_info_map(task: Dict[str, Any]) -> Dict[str, int]:
    rows = task.get("target_rows") or []
    _require(bool(rows), "bad_target_def", "info classification task has empty Target Definition.")
    info_map: Dict[str, int] = {}
    for r in rows:
        val = r.get("value")
        y = r.get("y")
        _require(val is not None and y is not None,
                 "bad_target_def", f"info classification row needs value+y: {r}")
        try:
            info_map[str(val)] = int(y)
        except (ValueError, TypeError):
            raise DatasetDispatchError(
                kind="bad_target_def",
                message=(f"info classification row has non-int y={y!r} in row {r}; "
                         f"y must be a 0-based int (rulebook v3.2)."),
            )
    _validate_zero_indexed_sequential(
        info_map.values(), where="info-classification task",
    )
    return info_map


def build_dataset_from_task(
    task: Dict[str, Any],
    h5_path: Optional[str] = None,
    dry_run: bool = False,
    **loader_kwargs,
) -> Optional[BaseHDF5Dataset]:
    """Dispatch task → Dataset class. With `dry_run=True`, validate args only.

    Returns a constructed Dataset when `dry_run=False`, else `None`.
    Raises `DatasetDispatchError` with `.kind` in {schema, bad_target_def,
    missing_event, missing_misc, missing_info} on any failure.
    """
    route = task.get("label_route")
    ttype = task.get("task_type")
    label_field = task.get("label_field")

    _require(route in _VALID_ROUTES, "schema",
             f"label_route must be one of {_VALID_ROUTES}, got {route!r}.",
             label_route=route)
    _require(ttype in _VALID_TYPES, "schema",
             f"task_type must be one of {_VALID_TYPES}, got {ttype!r}.",
             label_route=route, label_field=label_field)

    if route == "misc":
        _require(ttype == "regression", "schema",
                 "misc route is regression-only (rulebook §77条之六).",
                 label_route=route, label_field=label_field)
        _require(bool(label_field), "schema",
                 "misc route requires non-empty label_field.",
                 label_route=route)

    if route == "info":
        _require(bool(label_field), "schema",
                 "info route requires non-empty label_field.",
                 label_route=route)

    if route == "event":
        events_map = _parse_events_map(task)
        if dry_run:
            return None
        _require(h5_path is not None, "schema",
                 "h5_path required when dry_run=False.", label_route=route)
        return EventDataset(
            h5_path=h5_path,
            events_map=events_map,
            task_type=ttype,
            **loader_kwargs,
        )

    if route == "misc":
        if dry_run:
            return None
        _require(h5_path is not None, "schema",
                 "h5_path required when dry_run=False.", label_route=route)
        return MISCDataset(
            h5_path=h5_path,
            misc_channel=label_field,
            **loader_kwargs,
        )

    # route == "info"
    info_map = _parse_info_map(task) if ttype == "classification" else None
    if dry_run:
        return None
    _require(h5_path is not None, "schema",
             "h5_path required when dry_run=False.", label_route=route)
    return InfoDataset(
        h5_path=h5_path,
        info_field=label_field,
        task_type=ttype,
        info_map=info_map,
        **loader_kwargs,
    )
