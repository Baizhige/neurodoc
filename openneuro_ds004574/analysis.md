# Cross-modal Oddball Task

**Dataset**: `openneuro_ds004574` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004574
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed an oddball task with cross-modal stimuli (visual and auditory). Standard stimuli (S 1), deviant stimuli (S 2), and rare stimuli (S 3) were presented in mixed modality streams. The study investigates the mismatch negativity (MMN) and P300 components elicited by deviant stimuli across sensory modalities.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | ~30xN | event | raw | Standard stimulus |
| `S 2` | ~30xN | event | raw | Deviant stimulus |
| `S 3` | ~30xN | event | raw | Rare/target stimulus |
| `boundary` | ~30xN | admin | raw | Recording boundary marker |
| `S255` | ~30xN | admin | raw | BrainVision overflow/system marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 1`, `S 2`, `S 3`, `S255`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`S 1`, `S 2`, `S 3`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 1` | 0 | Standard stimulus |
  | `S 2` | 1 | Deviant stimulus |
  | `S 3` | 2 | Rare/target stimulus |
- **Evidence**:
  - DOI: 10.1101/2022.07.26.22278079 — Preprint describing cross-modal oddball task with standard (S 1), deviant (S 2), and rare (S 3) stimuli for MMN and P300 analysis
- **Kernel Notes**: Exclude `boundary` and `S255` admin markers from epoching. Classify ERPs to detect target vs non-target stimuli across modalities.

### Potential Task 1: Oddball Stimulus Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: boundary and S255 are admin events - exclude from target_events. S255 is a BrainVision system marker (overflow/sync), not a task event.

| Event | y | Meaning |
|-------|---|------|
| `S 1` | 0 | Standard stimulus |
| `S 2` | 1 | Deviant stimulus |
| `S 3` | 2 | Rare/target stimulus |

## Data Quality Notes

- boundary and S255 must be excluded from epoching
- S255 is a BrainVision system marker, not a stimulus event
- 30 subjects with standard oddball structure


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review