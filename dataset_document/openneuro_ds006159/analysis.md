# Implicit Learning EEG (BioSemi)

**Dataset**: `openneuro_ds006159` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006159
**Category**: High-level Mental | **Subjects**: 35 | **Files (Completed)**: 35 | **Channels**: 69 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

An experimental study investigating the neural correlates of implicit learning using a BioSemi EEG system. Participants underwent repeated exposure to structured sequences without explicit instructions to learn the underlying patterns. No trial-level event annotations are present in the dataset; the EEG is recorded as a continuous stream during the implicit learning protocol.

## File Scan Result

> **Kernel SHA256**: `3845a0c331dc5f16a329a15339e10b0bc56df899f063f2efaa8ccce6f8a59519`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

### Info

No additional scan result info available.

## Tasks

### Classical Task 1: Publisher-defined BIDS task: Implicitlearn
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, target_events = [Needs Verification]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006159 DOI: https://doi.org/10.18112/openneuro.ds006159.v1.0.0

---

### Potential Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: N/A (no event markers; segmentation only)
- **Notes**: No trial-level events available; purely continuous EEG. Labels must be derived from external metadata (e.g., block condition labels from participants.tsv if available).

## Data Quality Notes

- No event markers present; continuous-only processing.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
