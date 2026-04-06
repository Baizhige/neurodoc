# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Liu Peng

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. No trial-level event markers are stored in the BIDS EEG files; the task condition is reflected continuously in the EEG signal itself.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; continuous neurofeedback paradigm |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Covert Visuospatial Attention Decoding (Left vs Right Hemifield)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.0, target_events = [`left_cue`, `right_cue`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_cue` | 0 | Attend to left hemifield (left half-circle cue) |
  | `right_cue` | 1 | Attend to right hemifield (right half-circle cue) |
- **Super Meta Notes**: Derived from experimental paradigm (cue direction). No raw EEG event markers present in BIDS files. Kernel must derive trial onsets from experimental protocol timing or use the task labels from the dataset's sidecar JSON if available.
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — Post-hoc single-trial binary classification to decode attended side (left vs right) from alpha-band EEG lateralization features using LDA classifiers with 10-fold cross-validation.
- **Kernel Notes**: Compute alpha-band (8-13 Hz) power spectral density using 1s sliding windows with 62.5ms overlap across the epoch. Calculate Lateralization Index (LI = (right - left) / (right + left)) from posterior electrodes (PO7, PO8, O1, O2). Use averaged features across trial for classification. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Alpha Lateralization Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.9375, target_events = [`left_cue`, `right_cue`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_cue` | continuous | Alpha Lateralization Index (negative = left lateralized) |
  | `right_cue` | continuous | Alpha Lateralization Index (positive = right lateralized) |
- **Super Meta Notes**: Regression target is the computed alpha-band lateralization index per trial. Raw events derived from experimental cue direction (left vs right half-circle).
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — Real-time neurofeedback study on alpha-band lateralization; dataset includes continuous alpha-LI values during feedback runs.
- **Kernel Notes**: For each sliding window, compute PSD in alpha band (8-13 Hz) for left (PO7, O1) and right (PO8, O2) posterior electrodes. Compute LI = (alpha_R - alpha_L) / (alpha_R + alpha_L). Aggregate windows within epoch for regression target. (replaces Classical Task 2 from original analysis.md)

### Potential Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: Continuous neurofeedback paradigm; alpha lateralization index may be computed from raw EEG as a continuous target if desired.

## Data Quality Notes

- No trial-level event markers detected in any EEG files; only continuous recordings available.
- Real-time neurofeedback paradigm - EEG signal itself contains the task-relevant information.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review