# Evidence accumulation relates to perceptual consciousness and monitoring

**Dataset**: `openneuro_ds001785` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds001785
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 54 | **Channels**: 71 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

Participants performed a threshold-level vibrotactile detection task in which a weak tactile stimulus was either present (threshold condition) or absent (adapt condition). After each trial, participants provided a confidence rating. The study investigated the neural mechanisms of evidence accumulation and metacognitive monitoring using signal detection theory outcomes (hit, miss, correct rejection, false alarm) as trial labels.

## File Scan Result

> **Kernel SHA256**: `86c9fc412900d161a63c11717d321a8e57a629d6f374b06bcdbda89495328629`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | 18–34 (years); no mapping |
- **Evidence**:
- **Notes**: Segmentation-based regression with no event locking. 10s windows with 50% overlap provide sufficient samples per subject for subject-level age prediction while maintaining stationarity. Age is a native participants.tsv column (B3 archetype, Meta=raw).

### Potential Task 2: Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | F -> 0; M -> 1 |
- **Evidence**:
- **Notes**: Subject-level demographic classification using continuous EEG segments. No task-related events are used for labeling; instead, the sex field from participants.tsv provides binary labels (F=7, M=11). Segmentation with 10s windows and 50% overlap is standard for resting-state/demographic prediction from EEG when no discriminating events exist.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
