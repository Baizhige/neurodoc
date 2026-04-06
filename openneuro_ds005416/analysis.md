# Fatigue Characterization of EEG under Mixed Reality Stereo Vision

**Dataset**: `openneuro_ds005416` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005416
**Category**: Complex Applied | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed resting and movement scenes in a Mixed Reality (MR) stereo vision environment to characterize EEG-based fatigue during periodic visual depth and velocity changes. The study investigates neural correlates of visual fatigue induced by MR headset viewing under different dynamic visual conditions. No trial events were captured in events.tsv; data is continuous.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: None
- **Notes**: No event markers in events.tsv. EEG is continuous during MR viewing task. Use sliding-window segmentation. Condition labels (fatigue level, visual condition) may be available from session metadata.

## Data Quality Notes

- No event markers; continuous EEG during MR task.
- High sampling rate (1000 Hz) adequate for spectral fatigue analysis.
- MR headset may introduce electrical interference artifacts.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review