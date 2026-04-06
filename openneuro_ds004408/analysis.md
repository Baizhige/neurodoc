# EEG responses to continuous naturalistic speech

**Dataset**: `openneuro_ds004408` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004408
**Category**: High-level Mental | **Subjects**: 380 | **Files (Completed)**: 380
**Channels**: 128 | **Sampling Rate**: 512 Hz

## Paradigm

Participants listened to continuous segments of an audiobook version of 'The Old Man and the Sea' to record EEG responses to naturalistic narrative speech and language processing. The study investigates low-frequency cortical entrainment to speech and phoneme-level processing. No trial-level event markers are present; recordings are continuous.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings during naturalistic speech listening without trial-level annotations._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: No trial markers; use sliding window segmentation. Large dataset (380 files). Suitable for EEG-speech alignment analysis using stimulus audio envelope.

## Data Quality Notes

- No trial-level event markers; continuous listening paradigm
- Very large dataset (380 files); batch processing required
- 128-channel EEG at 512 Hz


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review