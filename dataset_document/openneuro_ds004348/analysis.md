# Ear-EEG Sleep Monitoring 2017 (EESM17)

**Dataset**: `openneuro_ds004348` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004348
**Category**: Biological State | **Subjects**: 9 | **Files (Completed)**: 36 | **Channels**: 35 | **Sampling Rate**: 200 Hz | **Manual Review**:

## Paradigm

Nightly sleep monitoring and pre-sleep resting recordings using ear-EEG and partial polysomnography in a naturalistic home environment. Nine healthy subjects were recorded simultaneously with PSG and ear-EEG for one night each. Subjects wore ear-mounted EEG devices during sleep, enabling investigation of sleep stage classification using AASM guidelines and comparison between ear-EEG and conventional PSG signals. Manual scoring was performed by trained clinical experts following AASM guidelines.

## File Scan Result

> **Kernel SHA256**: `f3dc6f84457dde259198b2c8ce281375ff4cefab30da313223fbbeef7bd99c92`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `512` | 16 | admin | raw | EDF+ annotation channel conversion marker - generic system marker from EEGLAB edfToSet conversion, no meaningful experimental event |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Gender Classification from Sleep EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | subject_sex | m -> 0; f -> 1 |
- **Evidence**:
  - participants.tsv — N=9 subjects with complete gender information (6 male, 3 female)
- **Notes**: Binary classification of participant sex from continuous sleep EEG segments. Uses 30-second non-overlapping segmentation matching standard sleep epoch duration. Class imbalance noted (6:3 male:female ratio). The Info Field name `subject_sex` reflects the BIDS-compliant field name from the current File Scan Result, superseding the legacy `gender` reference.

### Classical Task 2: Wake Resting-State Segmentation with Gender Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | subject_sex | m -> 0; f -> 1 |
- **Evidence**:
- **Notes**: Archetype C with native info column (gender from participants.tsv). Since gender is a pre-existing BIDS participants.tsv column, no kernel derivation is needed — Meta Level remains raw. The 10-s segmentation with no overlap is applied to continuous wake resting-state recordings (task-wake, ~3.5h duration) where no discriminating events exist; the 512 marker is an EDF-to-SET conversion artifact, not an experimental event. The Info Field name `subject_sex` reflects the BIDS-compliant field name from the current File Scan Result.

### Classical Task 3: Sleep Segmentation with Gender Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | subject_sex | m -> 0; f -> 1 |
- **Evidence**:
- **Notes**: Continuous sleep EEG is segmented into 30-second epochs (standard sleep epoch length per SKILL default, marked with * since inferred). Gender labels are drawn from participants.tsv as a native info field. This task serves as an alternative to event-based sleep staging when annotation quality is uncertain, predicting participant gender from raw EEG spectral and temporal features without requiring manual sleep stage scoring. The Info Field name `subject_sex` reflects the BIDS-compliant field name from the current File Scan Result.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
