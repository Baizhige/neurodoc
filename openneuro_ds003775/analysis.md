# SRM Resting-State EEG

**Dataset**: `openneuro_ds003775` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003775
**Category**: Biological State | **Subjects**: 111 | **Files (Completed)**: 153
**Channels**: 64 | **Sampling Rate**: 1024 Hz

## Paradigm

Four minutes of uninterrupted eyes-closed resting-state EEG recorded from healthy adult participants as part of a larger experimental paradigm. This dataset was collected to provide a normative baseline for comparing resting EEG characteristics across studies. The resting-state recording provides a standardized, task-free EEG sample suitable for spectral power analysis, functional connectivity, and individual difference studies.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; pure resting-state EEG |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Age Regression from Resting-State EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s *, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | age | Subject age in years (continuous) |
- **Super Meta Notes**: Derived from dataset subject metadata (demographics CSV). Kernel step: Extract subject age from BIDS participants.tsv and map to each epoch segment.
- **Evidence**:
  - DOI: `10.1016/j.clinph.2024.09.019` — Spectral feature harmonization and age-correlation analysis using ComBat methods across five datasets; confirms Oslo dataset (n=111) from openneuro_ds003775 was used
- **Kernel Notes**: Extract 5-second epochs from continuous resting-state signal using sliding window with 50% overlap. Load participant ages from dataset metadata (participants.tsv). Train regression model to predict age from spectral features (alpha, beta, theta, delta power). (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Sex Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s *, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (categorical) | male | Male subject |
  | N/A (categorical) | female | Female subject |
- **Super Meta Notes**: Derived from dataset subject metadata (demographics CSV). Kernel step: Extract subject sex from BIDS participants.tsv and map to each epoch segment.
- **Evidence**:
  - DOI: `10.1016/j.clinph.2024.09.019` — Same dataset used for harmonization analysis includes sex as a covariate; confirms Oslo dataset from openneuro_ds003775
- **Kernel Notes**: Extract 5-second epochs from continuous resting-state signal using sliding window with 50% overlap. Load participant sex from dataset metadata (participants.tsv). Train binary classifier to predict sex from spectral features.

### Potential Task 1: Resting state EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null - no labels, used for unsupervised analysis or individual differences research)
- **Notes**: Pure 4-minute eyes-closed resting-state; 111 subjects, 153 files (some subjects may have multiple sessions). Suitable for individual alpha frequency, spectral power, and connectivity analyses. Large normative dataset.

## Data Quality Notes

- Purely resting-state; no task events or stimuli.
- 153 files from 111 subjects; some subjects have multiple files (repeat sessions).
- 64-channel EEG at 1024 Hz; standard configuration for resting-state analysis.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review