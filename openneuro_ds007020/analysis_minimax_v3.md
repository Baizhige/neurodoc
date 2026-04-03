# EEG Mortality Dataset in Parkinson's Disease

**Dataset**: `openneuro_ds007020` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds007020
**Category**: Biological State | **Subjects**: 94 | **Files (Completed)**: 94 | **Channels**: 63 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings (eyes open) were collected from Parkinson's disease (PD) patients and healthy controls to evaluate EEG-based biomarkers for mortality classification. The dataset enables investigation of spectral and connectivity biomarkers that predict mortality risk in PD. The sole event marker (`New Segment/`) indicates a recording segment boundary and carries no experimental meaning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007020

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 94 | admin | raw | Recording segment boundary marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: 3-Year Mortality Classification in Parkinson's Disease
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 120 s (2 minutes), overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `deceased` | 1 | Patient died within 3 years from recording |
  | `living` | 0 | Patient survived at least 3 years after recording |
- **Super Meta Notes**: Derived from clinical metadata in participants.tsv (3-year mortality outcome). The 'New Segment/' marker is an administrative boundary and must not be used as a classification target.
- **Evidence**:
  - DOI: 10.1016/j.prdoa.2025.100409 — Binary classification of 3-year mortality status (deceased vs living) in PD patients using Linear Predictive Coding EEG features from 2-minute resting-state segments at 500 Hz (94 PD patients: 22 deceased, 72 living), achieving 83% out-of-sample accuracy.
- **Kernel Notes**: Extract 2-minute non-overlapping segments from raw EEG. Load mortality labels from participants.tsv (3-year follow-up outcome). Train binary classifier to predict mortality status from EEG-derived features (LPC or spectral features). (replaces Primary Task 1 from original analysis.md)

### Normal Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no trial events; target_events: null)
- **Notes**: `New Segment/` is a BrainVision segment boundary marker and must never be used as a classification target. Group labels (PD patient / healthy control, mortality outcome) must be derived from clinical metadata in participants.tsv.

## Data Quality Notes

- `New Segment/` is a BrainVision format boundary marker; exclude from all analyses.
- Labels for mortality prediction must be derived from clinical metadata in participants.tsv.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

