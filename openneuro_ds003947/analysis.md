# EEG: First Episode Psychosis vs. Control Resting Task 2

**Dataset**: `openneuro_ds003947` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003947
**Category**: Biological State | **Subjects**: 61 | **Files (Completed)**: 61 | **Channels**: 64 | **Sampling Rate**: 3000 Hz
**Manual Review**: Pending

## Paradigm

Five minutes of resting-state EEG recording used to compare spontaneous brain activity between individuals with First Episode Psychosis (FEP) and healthy controls. This is a second independent resting-state dataset from the same clinical study series as ds003944, recorded at a higher sampling rate (3000 Hz). Group membership (FEP vs. control) serves as the classification label.

## File Scan Result

> **Kernel SHA256**: `1bc5069ece50456b723e7eb813ca0d6d26a4e9812ab710cd6bb0627d087949c8`
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

### Classical Task 1: First Episode Psychosis vs. Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `control` | 0 | Healthy control subject |
  | `first_episode_psychosis` | 1 | First Episode Psychosis patient |
- **Evidence**:
  - DOI: 10.48550/arxiv.2411.18392 — Binary classification of first episode psychosis vs healthy controls from resting-state EEG using ds003947 with 4-second windows
- **Kernel Notes**: Load participants.tsv to obtain diagnosis labels for each subject (clinical_status/group column). Segment continuous EEG into 4-second non-overlapping windows. Assign subject-level diagnosis (FEP=1, control=0) to all corresponding epochs as super meta. Resample to 250 Hz or lower to reduce computational load while preserving frequencies up to 125 Hz (adequate for delta through gamma bands). 5-minute recording yields ~75 epochs per subject.

### Potential Task 1: Resting-state Baseline Spectral Characterization
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | — | — | No supervised labels; extract spectral features per epoch |
- **Notes**: Extract spectral power features (delta 1–4 Hz, theta 4–8 Hz, alpha 8–13 Hz, beta 13–30 Hz, gamma 30–100 Hz) within each 4-second epoch for normative baseline characterization. Consistent segmentation with Classical Task 1 enables cross-study comparison.

### Potential Task 2: Cross-dataset FEP Classification (ds003944 + ds003947)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-------|---------|
  | `control` | 0 | Healthy control subject |
  | `first_episode_psychosis` | 1 | First Episode Psychosis patient |
- **Notes**: Combine subjects from both resting-state datasets (ds003944 and ds003947) for larger sample size and improved generalization. Requires alignment of preprocessing pipeline across datasets. See DOI 10.1038/s41598-024.66110-0 for spectral-based FEP classification on ds003944.