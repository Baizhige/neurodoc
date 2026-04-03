# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 119 | **Files (Completed)**: 119
**Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. The `confidence` rating is stored as a misc channel for regression analysis. High sampling rate (5000 Hz) requires downsampling before epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Status**: wait_manual_review
> **Evidence Keywords**: response_time, reaction time, confidence, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002158

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 119 (files) | short | raw | Trial onset marker - actual trial type may be in events.tsv `value` column; used as epoch anchor |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Confidence Regression from EEG during Speeded Perceptual Decisions
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`unknown`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---------|
  | confidence (continuous 0-1) | Metacognitive confidence rating (0=sure error, 0.5=unsure, 1=sure correct) |
- **Super Meta Notes**: Derived from misc channel `confidence` (visual analog scale responses). Kernel must extract `confidence` values from the misc channel and align with epochs time-locked to the response onset (using `unknown` as trial anchor; verify from events.tsv if `unknown` corresponds to response_onset or trial_start). The papers also used 0-200ms and 200-450ms post-response windows for decoding.
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — EEG amplitude time-locked to first-order response onset used to model confidence via linear regression; multivariate EEG decoding derived single-trial confidence predictions.
- **Kernel Notes**: High sampling rate (5000 Hz) requires downsampling. The `unknown` event serves as epoch anchor - verify from events.tsv that it corresponds to response onset (button press/visual hand appearance). Extract confidence values from misc channel as regression target. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Publisher-defined BIDS task: Main
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002158 DOI: https://doi.org/10.1073/pnas.1918335117

### Normal Task 2: Publisher-defined BIDS task: Rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002158 DOI: https://doi.org/10.1073/pnas.1918335117

## Data Quality Notes

- Event label `unknown` is a placeholder - actual trial type information may be in events.tsv `value` or `trial_type` columns.
- Confidence ratings stored in misc channel `confidence`; reaction times in `response_time`.
- High sampling rate (5000 Hz); significant downsampling required.
- Verify channel count consistency across subjects before pooling.

