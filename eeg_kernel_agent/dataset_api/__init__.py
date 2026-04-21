"""Torch Dataset classes that translate a v3 analysis.md Task block into
(data, label, meta) batches read from an EEGUnity v2.x HDF5 file.

Public API:
    EventDataset   — Label Route = event  (classification | regression)
    MISCDataset    — Label Route = misc   (regression only)
    InfoDataset    — Label Route = info   (classification | regression)
    build_dataset_from_task(task, h5_path, dry_run=False, **kwargs)
    DatasetDispatchError
"""
from .base import BaseHDF5Dataset
from .event_dataset import EventDataset
from .factory import DatasetDispatchError, build_dataset_from_task
from .info_dataset import InfoDataset
from .misc_dataset import MISCDataset

__all__ = [
    "BaseHDF5Dataset",
    "EventDataset",
    "MISCDataset",
    "InfoDataset",
    "build_dataset_from_task",
    "DatasetDispatchError",
]
