# EEG: Simon Conflict with Reinforcement + Cabergoline Challenge

**Dataset**: `openneuro_ds003518` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003518
**Category**: High-level Mental | **Subjects**: 110 | **Files (Completed)**: 137 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

This study examines whether conflict acts as an implicit cost in reinforcement learning using a modified Simon task with pharmacological manipulation. Healthy participants performed a Simon conflict task across training and test phases, with a double-blind Cabergoline (dopamine D2/D3 agonist) challenge administered to examine dopaminergic modulation. The training phase included reinforcement feedback to shape behavior; the test phase probed learned conflict avoidance. Mid-frontal theta and error-related negativity are key EEG measures.

## File Scan Result

> **Kernel SHA256**: `acb6b744009087a86d617f1b6e416921b67ad6d6365b12f26c4430057c8d8fe9`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Regression of Subject Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|------------------|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Continuous EEG is segmented into 2-second non-overlapping windows for brain-age prediction. No event structure is required—each window inherits the subject's age as the regression target. This follows standard brain-age prediction setups where subject-level demographics are predicted from resting/task-continuous EEG features.

### Potential Task 2: 2-class sex classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|------------------|
  | subject_sex | Male -> 0; Female -> 1 |
- **Evidence**:
  - participants.tsv — N=110 subjects with complete sex information (46 Male, 64 Female)
- **Notes**: Subject-level sex classification from continuous EEG using 2-second non-overlapping windows. The sex field is a native participants.tsv column with two balanced classes, making this a straightforward demographic prediction benchmark. Segmentation allows the model to learn sex-differentiating spectral/spatial patterns across the continuous recording without event-locked constraints.

## Data Quality Notes

- Event structure table is empty in File Scan Result, indicating no event codes were successfully extracted or parsed from the dataset files.
- `device` field is completely missing from info metadata, limiting knowledge about EEG amplifier/equipment used across studies.
- Drug condition fields (`sess1_Drug`, `sess2_Drug`) are highly incomplete (27/110 subjects), restricting pharmacological analyses to Study 2 subset only.
- Study 1 and Study 2 have substantially different sample sizes (83 vs 27) and experimental designs, creating potential confounds for cross-study analyses.
- No known data quality issues for core demographic fields (`subject_age`, `subject_sex`, `Original_ID`, `Study`) which are all complete.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
