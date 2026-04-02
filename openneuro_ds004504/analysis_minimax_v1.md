# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176
**Channels**: 19 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings with eyes closed collected from healthy controls and patients with Alzheimer's disease (AD) and Frontotemporal Dementia (FTD). The study provides a clinical EEG dataset for developing diagnostic biomarkers and machine learning classifiers to differentiate neurodegenerative conditions from healthy aging.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004504

## Event Structure

_No event markers detected (`no_events`). This dataset contains resting-state EEG recordings without trial-level annotations._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Resting-state EEG Dementia Classification (AD vs FTD vs HC)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `CN` | 0 | Healthy control (29 subjects) |
  | `AD` | 1 | Alzheimer's disease (36 subjects) |
  | `FTD` | 2 | Frontotemporal dementia (23 subjects) |
- **Super Meta Notes**: Subject-level diagnosis labels extracted from participants.tsv metadata file — not from raw event markers (no_events dataset). Each epoch inherits the diagnostic group label of the participant it belongs to. Binary classification tasks (AD-CN and FTD-CN) are derived from this three-class labeling scheme.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2024.12.008 — SVM classifiers with time-frequency functional connectivity features achieve 95% accuracy for AD vs HC and 86% for FTD vs HC using 5-second epochs (no overlap).
  - DOI: 10.1109/access.2023.3294618 — DICE-net for binary AD-CN and FTD-CN classification using 30-second EEG windows with 15-second overlap.
  - DOI: 10.3390/data8060095 — Benchmarks classification using 4-second windows with 50% overlap, labeling epochs as AD, FTD, or CN based on subject diagnosis for Leave-One-Subject-Out validation.
- **Kernel Notes**: Since dataset has no trial-level events (no_events), use continuous segmentation. Extract subject diagnosis from participants.tsv and map each epoch to corresponding label (AD/FTD/CN). ApplyLeave-One-Subject-Out cross-validation to prevent data leakage.

### Normal Task 1: Dementia Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (subject-level labels from participants.tsv)
- **Notes**: Subject-level diagnosis labels (HC/AD/FTD) in participants.tsv used as ground truth. 19-channel 10-20 system EEG; standard clinical montage. 2 sessions per subject (176 files / 88 subjects).

## Data Quality Notes

- No trial-level event markers; pure resting-state dataset
- Subject diagnosis labels (HC/AD/FTD) available in participants.tsv
- Standard 10-20 montage (19 channels)
- 2 recordings per subject (176 files / 88 subjects)

## References

- **Reference**: `A Dataset of Scalp EEG Recordings of Alzheimers Disease, Frontotemporal Dementia and Healthy Subjects from Routine EEG`
