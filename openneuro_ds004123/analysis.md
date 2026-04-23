# BCIT Traffic Complexity

**Dataset**: `openneuro_ds004123` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004123
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 74 | **Sampling Rate**: 1024 Hz
**Manual Review**:

## Paradigm

Subjects performed a simulated driving task with varying levels of visual traffic complexity (low, medium, high density of surrounding vehicles) while correcting for lateral vehicle perturbations. EEG was recorded to assess how increasing traffic complexity interacts with fatigue-related neural signatures. Part of the BCIT driving fatigue dataset series examining environmental complexity effects on driver workload.

## File Scan Result

> **Kernel SHA256**: `7c20f0f885e99333e4abe19bf41e82f12c5fb6fcf705c4088f6789c3b3412006`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Year of Birth Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | year_of_birth | 1976–1995 | Subject year of birth; ~19 year span across 29 subjects. Used as proxy for chronological age in continuous EEG regression. |
- **Evidence**:
- **Notes**: Segmentation-based epoching (4s non-overlapping segments) enables subject-level regression without event-locked constraints. The year_of_birth field in participants.tsv provides complete demographic coverage (N=29, range ~1976-1995), supporting age-related EEG pattern learning. No event markers are required for this task architecture.

### Potential Task 2: Continuous Driving Segmentation with Year of Birth Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | year_of_birth | 1954–1997 (year) | Subject chronological age proxy; all subjects adult (range ~23–69 years at typical study date). Value used as scalar regressor per segment. |
- **Evidence**:
- **Notes**: Native info field from participants.tsv; no kernel derivation required. Segmentation treats continuous driving as brain-state prediction problem with subject-level age covariate. 10s windows with 50% overlap chosen to capture slow fluctuations in fatigue-related EEG signatures that may vary with age, per dataset's stated goal of fatigue biomarker discovery.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
