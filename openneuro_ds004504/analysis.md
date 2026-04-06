# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176
**Channels**: 19 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings with eyes closed collected from healthy controls and patients with Alzheimer's disease (AD) and Frontotemporal Dementia (FTD). The study provides a clinical EEG dataset for developing diagnostic biomarkers and machine learning classifiers to differentiate neurodegenerative conditions from healthy aging.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains resting-state EEG recordings without trial-level annotations._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Resting-state EEG Dementia Classification (AD vs FTD vs CN)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AD` | 0 | Alzheimer's disease diagnosis |
  | `FTD` | 1 | Frontotemporal dementia diagnosis |
  | `CN` | 2 | Cognitively normal / Healthy controls |
- **Super Meta Notes**: Derived from subject-level diagnosis in `participants.tsv`. Kernel step: For each segmented epoch, assign the diagnostic label of the subject from which the epoch was recorded (AD/FTD/CN). No raw event markers exist in this dataset.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2024.12.008 — SVM classifiers with time-frequency connectivity features achieved 95% accuracy for AD vs HC and 86% for FTD vs HC on ds004504 dataset.
  - DOI: 10.1109/access.2023.3294618 — DICE-net binary classification (AD-CN, FTD-CN) using 30s windows with 15s overlap on 88 subjects (36 AD, 23 FTD, 29 CN).
  - DOI: 10.3390/data8060095 — Benchmarked 4s windows with 50% overlap for AD/FTD/CN classification using Leave-One-Subject-Out validation.
- **Kernel Notes**: Extract continuous EEG, segment into sliding windows, label each epoch with subject's diagnosis from participants.tsv. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Dementia Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `HC` | 0 | Healthy control |
  | `AD` | 1 | Alzheimer's disease |
  | `FTD` | 2 | Frontotemporal dementia |
- **Notes**: Subject-level diagnosis labels (HC/AD/FTD) in participants.tsv used as ground truth. 19-channel 10-20 system EEG; standard clinical montage. 2 sessions per subject (176 files / 88 subjects).

## Data Quality Notes

- No trial-level event markers; pure resting-state dataset
- Subject diagnosis labels (HC/AD/FTD) available in participants.tsv
- Standard 10-20 montage (19 channels)
- 2 recordings per subject (176 files / 88 subjects)


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review