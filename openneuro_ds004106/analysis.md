# BCIT Advanced Guard Duty

**Dataset**: `openneuro_ds004106` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004106
**Category**: Complex Applied | **Subjects**: 29 | **Files (Completed)**: 29
**Channels**: 262 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a sustained vigilance task simulating advanced security guard duties by verifying multiple fields on replica ID cards against reference images, under varying workloads and stochastic arrival rates of cards. EEG was recorded to identify biomarkers of mental fatigue and vigilance decrement over extended duty periods. Part of the BCIT sustained attention / guard duty dataset series.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1311` | 29 files | event | raw | Card/stimulus arrival event - type 1311 |
| `1312` | 29 files | event | raw | Card/stimulus arrival event - type 1312 |
| `1321` | 29 files | event | raw | Verification response event |
| `1322` | 29 files | event | raw | Verification response event |
| `1331`-`1362` | 27-29 files | event | raw | Guard duty task events (various verification stages) |
| `1341`-`1342` | 29 files | event | raw | Guard duty task events |
| `1351`-`1352` | 27-29 files | event | raw | Guard duty task events |
| `1221`-`1222` | 29 files | event | raw | Guard duty task events |
| `1211`-`1212` | 28 files | event | raw | Guard duty task events |
| `1231`-`1232` | 28 files | event | raw | Guard duty task events |
| `1241`-`1242` | 27 files | event | raw | Guard duty task events |
| `1251`-`1252` | 27 files | event | raw | Guard duty task events |
| `1121`-`1122` | 27 files | event | raw | Guard duty task events |
| `2110` | 29 files | event | raw | Workload condition marker - high |
| `2120` | 29 files | event | raw | Workload condition marker - low |
| `3111`-`3112` | 26 files | event | raw | Block/session markers |
| `3231`-`3232` | 2 files | event | raw | Rare condition events |


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
- **Epoch Parameters**: segment_length = 3 s, overlap = 0.33 (500-point step on 750-point window) *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `segment` | continuous | Lane deviation (meters) - smoothed with 90s centered mean filter |
  | `segment` | continuous | Reaction time (seconds) - smoothed with 90s centered mean filter |
  | `segment` | continuous | Accuracy (proportion correct) - smoothed with 90s centered mean filter |
- **Super Meta Notes**: Derived from continuous behavioral metrics (lane deviation, perturbation RT, accuracy) recorded during the ID verification task. Kernel step: Apply 90s centered mean filter to both EEG spectral features (ICA-based) and behavioral measures, then use linear regression to predict performance metrics from EEG power spectra.
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Linear regression with ICA-based EEG spectral features estimates continuous behavioral performance (lane deviation, RT, accuracy) in simulated guard duty task, achieving correlation coefficients of 0.548±0.117 for driving and 0.701±0.154 for guard duty tasks.
- **Kernel Notes**: Extract EEG spectral features via ICA, compute power spectra in sliding windows (3s segment, ~2s step), apply 90s centered mean smoothing, train linear regression model to predict behavioral metrics. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: High vs Low Workload (binary)
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
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Study used high vs low workload conditions in guard duty task paradigm.
- **Kernel Notes**: Epoch EEG relative to workload condition markers (2110=high, 2120=low). Extract spectral features and classify workload condition. 262-channel BioSemi data requires memory-efficient processing.

## Data Quality Notes

- 262 channels - largest EEG cap in the BCIT series; high memory requirements
- Full event decoding requires BCIT codebook documentation
- Very limited subjects (29) for the large channel count


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review