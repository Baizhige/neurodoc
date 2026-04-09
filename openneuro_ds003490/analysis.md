# EEG: 3-Stim Auditory Oddball and Rest in Parkinson's

**Dataset**: `openneuro_ds003490` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003490
**Category**: Sensory/Response | **Subjects**: 50 | **Files (Completed)**: 75
**Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

A three-stimulus auditory oddball task (standard tones, target tones requiring button-press response, and novel distractor tones) combined with resting-state (eyes open and eyes closed) EEG recordings in Parkinson's disease patients and age-matched healthy controls. The study aims to identify auditory P300 and mismatch negativity differences between PD patients and controls. STATUS is a BioSemi admin marker.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Standard Tone` | 75 (files) | event | raw | Frequent standard auditory tone (non-target) |
| `Target Tone` | 75 (files) | event | raw | Infrequent target tone (requires button press) |
| `Novel Tone` | 75 (files) | event | raw | Rare novel distractor tone |
| `Eyes Closed` | 75 (files) | event | raw | Eyes-closed resting state block |
| `Eyes Open` | 75 (files) | event | raw | Eyes-open resting state block |
| `STATUS` | 75 (files) | admin | raw | BioSemi system status marker - exclude |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks


### Classical Task 1: Parkinson's Disease vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 2.0 s *, target_events = [`Standard Tone`, `Target Tone`, `Novel Tone`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | PD (on medication) | 0 | Parkinson's disease patients ON levodopa |
  | PD (off medication) | 1 | Parkinson's disease patients OFF levodopa |
  | HC | 2 | Age-matched healthy controls |
- **Super Meta Notes**: Derived from raw events [`Standard Tone`, `Target Tone`, `Novel Tone`] by extracting EEG features (complexity metrics: LZC, SampEn; or frequency domain: FFT coefficients; or texture: Haralick/Fractal) per epoch, then classifying subject groups. Kernel step: Load participants.tsv to map subject IDs to group labels (PD_ON, PD_OFF, HC), then train classifier on epoch-level features.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2017.11.023 — SVM pattern classifiers on EEG responses to novelty condition achieved 82% accuracy classifying PD vs controls
  - DOI: 10.21528/cbic2023.027 — Haralick and Fractal texture features from EEG epochs (±2s) used to classify PD ON/OFF vs healthy controls
  - DOI: 10.1038/s41598-025-00826-5 — EEG complexity metrics (Lempel-Ziv, sample entropy) during 3-stimulus oddball classify PD patients from healthy controls
- **Kernel Notes**: Extract epochs around each tone stimulus per subject, compute features (complexity/frequency/texture), aggregate epoch-level features per subject (mean/std), then classify subject groups using labels from participants.tsv. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Auditory Tone Type Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s (relative to tone onset, P300 window), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is BioSemi admin marker - excluded. Tone events are short stimuli (~50 ms), not sustained states; `epoch_by_event_hdf5` is appropriate. Eyes-open/closed are separate resting blocks - do not mix with tone targets. PD vs HC group labels available in participants.tsv.

| Event | y | Meaning |
|-------|---|------|
| `Standard Tone` | 0 | Frequent standard tone (non-target) |
| `Novel Tone` | 1 | Rare novel distractor tone (P3a) |
| `Target Tone` | 2 | Infrequent target tone (P3b) |



### Potential Task 2: Resting State Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|------|
| `Eyes Open` | 0 | Eyes-open resting block |
| `Eyes Closed` | 1 | Eyes-closed resting block |

## Data Quality Notes

- `STATUS` is BioSemi hardware marker - exclude.
- Dataset includes both Parkinson's patients and age-matched controls; group label from participants.tsv.
- Three-stimulus oddball design provides Standard/Target/Novel tone categories for ERP analysis.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review