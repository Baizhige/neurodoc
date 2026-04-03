# EEG: First Episode Psychosis vs. Control Resting Task 2

**Dataset**: `openneuro_ds003947` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003947
**Category**: Biological State | **Subjects**: 61 | **Files (Completed)**: 61
**Channels**: 64 | **Sampling Rate**: 3000 Hz

## Paradigm

Five minutes of resting-state EEG recording used to compare spontaneous brain activity between individuals with First Episode Psychosis (FEP) and healthy controls. This is a second independent resting-state dataset from the same clinical study series as ds003944, recorded at a higher sampling rate (3000 Hz). Group membership (FEP vs. control) serves as the classification label.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003947

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 61 | admin | raw | Unidentified system marker - not suitable for epoching |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: First Episode Psychosis vs. Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `control` | 0 | Healthy control subject |
  | `first_episode_psychosis` | 1 | First Episode Psychosis patient |
- **Super Meta Notes**: Derived from subject-level diagnosis labels in participants.tsv (group/clinical_status column). Kernel step: Extract group label from participants.tsv and assign to all epochs from that subject.
- **Evidence**:
  - DOI: 10.48550/arxiv.2411.18392 — Binary classification of first episode psychosis vs healthy controls from resting-state EEG using ds003947 with 4-second EEG windows
- **Kernel Notes**: Load participants.tsv to obtain diagnosis labels for each subject. Segment continuous EEG into 4-second non-overlapping windows. Assign subject-level diagnosis (FEP=1, control=0) to all corresponding epochs. Resample to 250 Hz or lower to reduce computational load (original 3000 Hz). (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Resting-state baseline characterization
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Target Definition**: None — extract spectral features (delta, theta, alpha, beta, gamma power) for characterization without labels
- **Notes**: Resting-state EEG analysis for computing normative spectral profiles. Use same segmentation as primary task for consistency.

## Data Quality Notes

- No meaningful event markers; `unknown` events should be excluded
- Very high sampling rate (~3000 Hz) may require downsampling
- Companion dataset to ds003944 (Task 1); can be combined for larger resting FEP cohort

