# EEG During Mental Arithmetic Task

**Dataset**: `physionet_eegmat` | **Year**: 2020 | **URL**: https://physionet.org/content/eegmat/1.0.0/
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 23 | **Sampling Rate**: 500 Hz | **Manual Review**: Liu Peng

## Paradigm

Thirty-six healthy subjects (Subject00-Subject35, ages 16-26, predominantly female) completed a mental arithmetic task while EEG was recorded monopolarly using a Neurocom 23-channel system with Ag/AgCl electrodes (Zyma et al., 2019). Each subject contributed two files: a background resting-state recording (suffix `_1.edf`) and a mental arithmetic task recording (suffix `_2.edf`). During the mental arithmetic task, subjects performed serial subtraction (e.g., 3141 minus 42) while EEG was recorded. A separate `Count quality` field in `subject-info.csv` rates the subject's arithmetic performance as Good or Bad, providing a behavioral quality label.

## File Scan Result

> **Kernel SHA256**: `2d377403dfb36e0b6ad6454cf2d69b00d8096cf9a7ebb560a8baff950dedaad6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Background EEG;Count Quality: Bad` | 10 | event | raw | Resting-state recording, subject's arithmetic quality was Bad |
| `Background EEG;Count Quality: Good` | 26 | event | raw | Resting-state recording, subject's arithmetic quality was Good |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 10 | event | raw | Mental arithmetic recording, quality Bad |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 26 | event | raw | Mental arithmetic recording, quality Good |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Mental Arithmetic Task vs Resting State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, overlap = 2.5 s *, target_events = [`Background EEG;Count Quality: Good`, `Background EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Background EEG;Count Quality: Good` | 0 | Resting-state EEG |
  | `Background EEG;Count Quality: Bad` | 0 | Resting-state EEG |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Mental arithmetic task |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | Mental arithmetic task |
- **Evidence**:
  - DOI: 10.13026/C2JQ1P — "The EEGMAT database contains 36 subjects with two 60-second EEG recordings each: background resting-state (_1.edf) and mental arithmetic task (_2.edf), with annotations encoding both condition type and count quality."
- **Kernel Notes**: Parse event annotation prefix before semicolon to extract task label (Background vs Mental Arithmetic). Each recording is 60s long; sliding window epoching extracts overlapping 5s segments. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Arithmetic Performance Quality Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, overlap = 2.5 s *, target_events = [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor arithmetic performance |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good arithmetic performance |
- **Evidence**:
  - DOI: 10.13026/C2JQ1P — "annotations encoding both condition type and count quality"
  - DOI: 10.1038/s41598-026-36434-0 — "good counters show significantly increased synchronization (PC-entropy) in beta band during task vs rest, while poor counters show no significant changes"
- **Kernel Notes**: Filter to Mental Arithmetic recordings only; parse suffix after semicolon for Count Quality label. Class imbalance expected (24 Good vs 12 Bad).

### Classical Task 3: Mental Stress Classification During Arithmetic Task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0 *, target_events = [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`]
- **Label Route**: `event`
- **Meta Level**: super
- **Super Meta Notes**: Derived from raw events [`Mental Arithmetic Task EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`] by k-means clustering on log-band power features (delta, theta, alpha, beta). Kernel step: Extract log-band power features from 5s EEG segments, apply k-means (k=2), map clusters to High-stress/Low-stress labels based on posterior overlap with Count Quality. See DOI: 10.1109/wccest66994.2025.11389948
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 0 | Low-stress (good performers) |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 1 | High-stress (poor performers) |
- **Evidence**:
  - DOI: 10.1109/wccest66994.2025.11389948 — "classify mental stress levels (High-stress vs Low-stress) by segmenting EEG into 5-second epochs, applying k-means clustering on frequency band powers"
- **Kernel Notes**: Segment Mental Arithmetic recordings into 5s non-overlapping windows; compute log-band power in delta, theta, alpha, beta bands; apply k-means clustering to derive stress labels.

## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
