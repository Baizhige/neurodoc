# Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts

**Dataset**: `openneuro_ds004784` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004784
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 10 | **Channels**: 264 | **Sampling Rate**: 512 Hz

## Paradigm

Technical validation study using an electrically conductive head phantom to simulate brain activity under various artifact conditions (motion, muscle, eye movements) for testing EEG cleaning algorithms. Code 65471 appears in all 10 files (20 total events); code 65343 appears in all 10 files (10 total events). These likely mark artifact-on vs artifact-off conditions or different artifact types.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65471` | 20 | event | raw | Artifact condition marker A (e.g., artifact-on) |
| `65343` | 10 | event | raw | Artifact condition marker B (e.g., clean condition) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Artifact Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`65471`, `65343`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `65471` | 0 | Artifact condition A (artifact-on) |
  | `65343` | 1 | Artifact condition B (artifact-off/clean) |
- **Evidence**:
  - DOI: https://doi.org/10.3390/s23198214 — Validates iCanClean artifact removal algorithm on OpenNeuro ds004784 phantom EEG dataset comparing artifact-on vs artifact-off conditions
- **Kernel Notes**: Extract epochs centered on event markers 65471 and 65343 with 1.2s window. Labels are binary: 0 for artifact-present condition (65471), 1 for artifact-free/clean condition (65343). Dataset contains 264-channel phantom EEG with 20 artifact-on and 10 clean events across 10 files. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Multi-class Artifact Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`65471`, `65343`]
- **Label Route**: `event`
- **Target Definition**: Multi-class mapping if artifact types are distinguishable (Brain, Brain+Eyes, Brain+NeckMuscles, Brain+FacialMuscles, Brain+WalkingMotion, Brain+AllArtifacts)
- **Notes**: The dataset may support multi-class classification of different artifact types beyond binary. Further verification of event code meanings needed from dataset README.

## Data Quality Notes

- Very small dataset (10 files, 30 events total) - insufficient for standard classification.
- 264-channel phantom EEG; not standard scalp EEG configuration.
- Designed for artifact algorithm validation, not neural decoding.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review