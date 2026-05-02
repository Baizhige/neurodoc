# BCIT Basic Guard Duty

**Dataset**: `openneuro_ds004119` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004119
**Category**: Complex Applied | **Subjects**: 22 | **Files (Completed)**: 22 | **Manual Review**: Pending
**Channels**: 262 | **Sampling Rate**: 1024 Hz

## Paradigm

A realistic sustained vigilance task in which subjects verified multiple identification card fields against reference images in a simulated security environment under varying card arrival rates. This basic guard duty variant uses a simpler verification protocol compared to the Advanced Guard Duty (ds004106), and is designed to study EEG correlates of sustained attention and vigilance decrement over extended duty periods.

## File Scan Result

> **Kernel SHA256**: `8594b07ce52c6f9b3ef4c8e9e1f01132ea83b32f4e1baffa2b183ca46bca997a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Continuous Behavioral Performance Estimation (Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.667 (approx 2 s step)
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |-------------------|---------------|
  | continuous | Continuous reaction time or accuracy derived from verification responses (`1321`, `1322`) smoothed with 90 s centered mean filter. Needs verification: no MISC channels present in File Scan Result; target may need to be computed from event-derived behavioral data rather than a recorded MISC channel. |
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Linear regression to estimate continuous behavioral performance (RT and accuracy for guard duty) from EEG power spectral density features extracted via ICA and smoothed with a 90 s centered mean filter.
- **Super Meta Notes**: Target is continuous behavioral performance metric derived from verification response events (`1321`, `1322`) aggregated over time windows and smoothed with 90 s centered mean filter per original methodology. Kernel must implement the same smoothing filter used in the reference paper to align behavioral targets with EEG epochs.
- **Kernel Notes**: Extract 3-second EEG epochs with ~2s step using sliding window segmentation, compute power spectral density features (optionally via ICA decomposition), smooth behavioral targets (reaction time/accuracy from verification responses) with 90 s centered mean filter, train linear regression model to predict continuous performance metrics. Verify actual sampling rate from file headers (analysis.md mentions 256 Hz but dataset header indicates 1024 Hz).

---

### Potential Task 1: Verification Response Classification (Correct vs Error)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1321`, `1322`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1321` | 0 | Verification error response |
  | `1322` | 1 | Verification correct response |
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Guard duty paradigm uses card field verification with response events coding accuracy; error-related neural activity expected in ERN/Pe components.
- **Kernel Notes**: Epoch around verification response events (`1321`, `1322`) to capture error-related negativity (ERN) and error positivity (Pe) components. The 1.2 s window captures pre-response preparation and post-response error processing. High-density 262-channel data will require memory-efficient processing.

---

### Potential Task 2: Stimulus Onset Evoked Response (Card Verification ERP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1311`, `1312`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1311` | 0 | Card arrival / verification stimulus onset (type 1) |
  | `1312` | 1 | Card arrival event (type 2) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.116054 — Guard duty recordings included in mega-analysis corpus with HED-annotated event epochs including card arrival/stimulus events.
- **Kernel Notes**: Epoch around stimulus onset events to capture standard visual evoked potentials (P100, N100, P200) and potential task-related modulations. Two distinct stimulus event codes may correspond to different card types or presentation conditions.

---

### Potential Task 1: High vs Low Workload (binary classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`2110`, `2120`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `2110` | 0 | High workload condition marker |
  | `2120` | 1 | Low workload condition marker |
- **Kernel Notes**: Workload condition markers indicate sustained vigilance load states. Epoching on onset captures the neural transition to different workload conditions. Small cohort (22 subjects) limits statistical power. Paired with ds004106 (Advanced Guard Duty) for combined analysis if larger sample needed. Workload condition markers may indicate sustained states rather than brief events; consider `epoch_by_long_event_hdf5` with extended windows if sustained state analysis preferred.

---

### Potential Task 2: Guard Duty Task Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1331`, `1332`, `1341`, `1342`, `1351`, `1352`, `1361`, `1362`, `1231`, `1232`, `1111`, `1112`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1331` | 0 | Guard duty task event type 1 |
  | `1332` | 1 | Guard duty task event type 2 |
  | `1341` | 2 | Guard duty task event type 3 |
  | `1342` | 3 | Guard duty task event type 4 |
  | `1351` | 4 | Guard duty task event type 5 |
  | `1352` | 5 | Guard duty task event event type 6 |
  | `1361` | 6 | Guard duty task event type 7 |
  | `1362` | 7 | Guard duty task event type 8 |
  | `1231` | 8 | Guard duty task event type 9 |
  | `1232` | 9 | Guard duty task event type 10 |
  | `1111` | 10 | Guard duty task event type 11 |
  | `1112` | 11 | Guard duty task event type 12 |
- **Kernel Notes**: Multiple task event codes require BCIT codebook documentation for proper interpretation. May represent different trial phases, sub-tasks, or behavioral checkpoints within the guard duty protocol. Full event code decoding essential before analysis.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
