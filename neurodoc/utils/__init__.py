"""neurodoc.utils — task-ready HDF5 export utilities.

Public API:
    build_task_hdf5(...)   — build/reuse one (dataset, task) HDF5
    JobResult              — per-job outcome
    load_task_spec(...)    — parse a Task block from analysis.md
"""
from .task_h5_builder import JobResult, build_task_hdf5, load_task_spec

__all__ = ["build_task_hdf5", "JobResult", "load_task_spec"]
