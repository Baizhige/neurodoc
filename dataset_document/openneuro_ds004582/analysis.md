# FakeFaceEmo_data

**Dataset**: `openneuro_ds004582` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004582
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants viewed fake face images with different emotional expressions while EEG was recorded. The dataset contains continuous EEG recordings; only hardware/metadata markers (New Segment, Comment) are present in the event files rather than trial-level stimulus markers. No trial-level event markers are available for epoch-based analysis.

## File Scan Result

> **Kernel SHA256**: `3845a0c331dc5f16a329a15339e10b0bc56df899f063f2efaa8ccce6f8a59519`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Sampled

### Event Structure

_No task event markers detected (`no_events`). Only hardware/metadata markers present._

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | ~30x1 | admin | raw | Recording segment boundary (hardware marker) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

No MISC labels detected in this dataset.

### Info

No additional scan information available.

## Tasks

### Classical Task 1: Publisher-defined BIDS task: FF
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004582 DOI: https://doi.org/10.18112/openneuro.ds004582.v1.0.0

---

### Potential Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: New Segment/ is a BrainVision hardware recording marker, not a task event. Use sliding window segmentation for feature extraction.

## Data Quality Notes

- No trial-level event markers
- New Segment/ is a hardware-only event and should not be used for epoching
- 30 subjects with continuous EEG recordings

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
