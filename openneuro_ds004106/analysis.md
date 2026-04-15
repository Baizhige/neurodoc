# BCIT Advanced Guard Duty

**Dataset**: `openneuro_ds004106` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004106
**Category**: Complex Applied | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 262 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a sustained vigilance task simulating advanced security guard duties by verifying multiple fields on replica ID cards against reference images, under varying workloads and stochastic arrival rates of cards. EEG was recorded to identify biomarkers of mental fatigue and vigilance decrement over extended duty periods. Part of the BCIT sustained attention / guard duty dataset series.

## File Scan Result

> **Kernel SHA256**: `028fc78b6b65cf41623d2af88d02ee671c1e40caf0f318cd7f6b3b5a58498c4e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Continuous Behavioral Performance Estimation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3 s, overlap = 0.33 (500-point step on 750-point window)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `segment` | continuous | Reaction time (seconds) - smoothed with 90s centered mean filter |
  | `segment` | continuous | Accuracy (proportion correct) - smoothed with 90s centered mean filter |
- **Super Meta Notes**: Derived from verification response events (1321, 1322) and stimulus events (1311, 1312) recorded during the ID card verification task. Kernel step: Compute RT from stimulus-response pairs, derive accuracy per segment, apply 90s centered mean filter to both EEG spectral features and behavioral measures, then use linear regression to predict performance metrics from EEG power spectra.
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Linear regression with ICA-based EEG spectral features estimates continuous behavioral performance (reaction time, accuracy) in simulated guard duty task, achieving correlation coefficients of 0.548±0.117 for driving and 0.701±0.154 for guard duty tasks.
- **Kernel Notes**: Extract EEG spectral features via ICA, compute power spectra in sliding windows (3s segment, ~2s step), apply 90s centered mean smoothing to both EEG and behavioral metrics, train linear regression model to predict behavioral metrics. 262-channel BioSemi data requires memory-efficient processing; consider channel reduction or chunked ICA computation.

### Potential Task 1: High vs Low Workload Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`2110`, `2120`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2110` | 0 | High workload condition marker |
  | `2120` | 1 | Low workload condition marker |
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Study implemented high vs low workload conditions in guard duty task paradigm with stochastic arrival rates simulating varying guard duty demands.
- **Kernel Notes**: Epoch EEG relative to workload condition markers (2110=high, 2120=low). Extract spectral features (theta, alpha, beta power) from 262-channel data using memory-efficient chunked processing. Binary classification to decode workload state from EEG signatures of mental workload.