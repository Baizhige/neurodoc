# Continuous Feedback Processing

**Dataset**: `openneuro_ds004262` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004262
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 21
**Channels**: 31 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants predicted the final height of an animated rising bar based on cues with varying predictability to study continuous feedback processing and prediction error. Each trial involved observing bar motion and registering a prediction, allowing examination of EEG correlates of reward prediction error and uncertainty-driven learning.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 21x900 | event | raw | Stimulus onset marker (bar appearance) |
| `New Segment` | 21 | admin | raw | Recording segment boundary |
| `Comment` | 21 | admin | raw | Experimenter comment/annotation |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus Processing (single-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one event class available for epoching. New Segment and Comment are admin markers. Behavioral metadata (prediction, actual height) may be available in events.tsv for regression tasks.

| Event | y | Meaning |
|-------|---|----------|
| `Stimulus` | 0 | Stimulus onset (bar presentation) |

## Data Quality Notes

- Only one non-admin event type (Stimulus); classification requires additional label parsing from events.tsv metadata columns
- New Segment and Comment are system/admin events excluded from epoching


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review