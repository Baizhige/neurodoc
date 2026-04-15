# Deception_data

**Dataset**: `openneuro_ds004511` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004511
**Category**: High-level Mental | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed a deception task while EEG was recorded. The dataset contains continuous EEG recordings; only a single hardware synchronization marker (Sync) is present per recording rather than trial-level event markers. No meaningful trial annotations are available for epoch-based analysis.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No task event markers detected (`no_events`). Only hardware sync marker `Sync(1)` present - this is a system/hardware event, not a task event._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: Sync(1) is a hardware synchronization marker, not a task event. Use sliding window segmentation for feature extraction.

## Data Quality Notes

- No trial-level event markers
- Sync(1) is a hardware-only event and should not be used for epoching


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: failed

---

> **auto_eeg FAILED**: No trial-level event markers exist in this dataset—only hardware sync markers are present, making supervised ML tasks impossible. The references either discuss deception detection but use different datasets (LieWaves vs. this 64-channel dataset) or are methodologically irrelevant. Without identifiable labels or trial structure, epoch-based analysis is not viable.
