# BCIT Auditory Cueing

**Dataset**: `openneuro_ds004105` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004105
**Category**: Complex Applied | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 74 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

Participants performed a long-duration simulated driving task involving lane maintenance with periodic lateral vehicle perturbations, while receiving auditory cues at varying intervals. EEG biomarkers of fatigue were investigated as performance and alertness declined over the driving session. The study is part of the BCIT (Brain Computer Interface and Technology) driving fatigue dataset series.

## File Scan Result

> **Kernel SHA256**: `15a9f9dcc5b04551e1547b5193f96d83490be1323bc13f58e9d9c6bcaf152ccd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | year_of_birth | Age computed as 2022 - year_of_birth; ~16 year span across 17 subjects (1978–1994). Native participants.tsv column used directly—model can regress on year_of_birth directly or user can derive age in preprocessing. |
- **Evidence**:
- **Notes**: Native participants.tsv column used directly for regression. The kernel does not need to compute age explicitly—the model can regress on year_of_birth directly (monotonically related to age) or the user can derive age as 2022 - year_of_birth in preprocessing. Segment-based epoching with 4s non-overlapping windows is standard for biomarker/regression analysis on continuous driving data, treating the sustained driving task as a quasi-resting state for age-related EEG feature extraction.

## Data Quality Notes

- No events detected in the File Scan Result event structure table, despite the Tasks section referencing specific event codes (1211, 1212, 4311, 4312, 4210, 4220, 4230, 3111, 3112) from the existing draft.
- Subject age and sex metadata are completely missing from the dataset info fields.
- Device information is missing from the dataset info fields.
- Only 17 subjects have year_of_birth data available for the age regression task, despite 34 total subjects/files in the dataset, indicating incomplete demographic coverage.
- The Tasks section contains only a single potential task (Subject Age Regression), with no classical or normal tasks defined in the authoritative block provided.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
