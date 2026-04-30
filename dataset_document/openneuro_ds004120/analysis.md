# BCIT Baseline Driving

**Dataset**: `openneuro_ds004120` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004120
**Category**: Complex Applied | **Subjects**: 131 | **Files (Completed)**: 131 | **Channels**: 266 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

Subjects performed a 60-minute simulated driving task involving manual steering and speed control, requiring corrective responses to lateral vehicle perturbations to study fatigue-related EEG biomarkers over an extended session. This baseline driving condition serves as the primary long-duration fatigue paradigm in the BCIT series, without auditory cueing or traffic complexity manipulation.

## File Scan Result

> **Kernel SHA256**: `c1596dc907fa8284a41e0aa9a0490ec3b2206f8ae63cba3717997bc2716f30a6`
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

### Potential Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | year_of_birth | 1960–1995 (years) | Convert to approximate age at study time (~2012–2014); 91/109 subjects have valid values (83.5% complete) |
- **Evidence**:
- **Notes**: Continuous driving EEG with no discrete event structure suitable for age prediction. Segmentation with 10s windows enables spectral biomarker extraction for fatigue-related age regression. year_of_birth from participants.tsv is the native info field; approximate age computed as study_year - year_of_birth where study_year inferred from README site dates (2012–2014). Partial completeness (91/109) is acceptable for regression; missing subjects will be excluded during kernel processing.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
