# Social Memory cuing

**Dataset**: `openneuro_ds003702` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003702
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 47
**Channels**: 64.0 | **Sampling Rate**: 500.0 Hz

## Paradigm

A visual working memory task performed in a virtual reality environment where participants recalled object locations and statuses following social (avatar) or non-social (stick) directional cues.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Social vs Non-Social Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.75 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `social_cue_segment` | 0 | Segments from social (avatar) cue trials |
  | `nonsocial_cue_segment` | 1 | Segments from non-social (stick) cue trials |
- **Super Meta Notes**: Derived from trial-level metadata in BIDS JSON sidecar files containing cue_type labels. Kernel step: Extract trial onsets and cue_type from external JSON/TSV files, segment EEG around those timestamps, assign social/non-social labels.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.107827 — Describes social (avatar) vs non-social (stick) cuing classification from VR working memory EEG; epochs from -1s pre-cue to +1s post-probe response.
- **Kernel Notes**: Since raw event markers (`no_events`) are absent in EEG files, segment continuous EEG into sliding windows. Use trial metadata from BIDS sidecar JSON to derive social vs non-social labels. Verify cue_type field in events.tsv or JSON sidecar files.

### Classical Task 2: Biological Sex Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.75 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `male_segment` | 0 | EEG segments from male participants |
  | `female_segment` | 1 | EEG segments from female participants |
- **Super Meta Notes**: Derived from participant demographics (sex) stored in participants.tsv. Kernel step: Read sex column from BIDS participants.json/TSV, map to labels, associate with all EEG segments from each subject.
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Uses VR spatial memory EEG to predict biological sex (binary classification) from EEG features during object-finding and maintenance phases.
- **Kernel Notes**: Map participant IDs to sex labels from participants.tsv. Apply to all segments. (replaces Potential Task 1 from original analysis.md)

### Classical Task 3: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.75 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `age_regression` | continuous | Participant age in years |
- **Super Meta Notes**: Derived from participant demographics (age) stored in participants.tsv. Kernel step: Read age column, map to labels, associate with all EEG segments from each subject.
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Uses VR spatial memory EEG to predict age (regression) from EEG features during three trial phases.
- **Kernel Notes**: Map participant IDs to age values from participants.tsv. Apply to all segments as continuous regression target.

### Classical Task 4: User Identity Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.75 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `participant_ID` | 0-46 | 47-class classification of participant identity |
- **Super Meta Notes**: Derived from participant ID embedded in BIDS filename/subject directory. Kernel step: Extract subject identifier from file path, use as class label.
- **Evidence**:
  - DOI: 10.1109/SMC58881.2025.11343511 — Uses VR spatial memory EEG for 47-class user identity classification from EEG features.
- **Kernel Notes**: Extract subject ID from BIDS directory structure (sub-XXX). Use as categorical label for classification.

### Potential Task 2: Super-meta task
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.75
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target / Label**: Derived from external metadata (participants.tsv, events.tsv, JSON sidecars)
- **Kernel Notes**: Derive and version super-meta in kernel. Read cue_type, sex, age from BIDS metadata files.

## Data Quality Notes

- Verify channel count consistency across subjects before pooling.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review