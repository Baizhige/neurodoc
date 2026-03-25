# EEG: First Episode Psychosis vs. Control Resting Task 1

**Dataset**: `openneuro_ds003944` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003944
**Category**: Biological State | **Subjects**: 82 | **Files (Completed)**: 82
**Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

A 5-minute eyes-open resting-state EEG recording comparing spontaneous brain activity between individuals with First Episode Psychosis (FEP) and age-matched healthy controls. The dataset is designed to identify EEG biomarkers of psychosis onset. No trial-level stimuli are presented; the label of interest is the clinical group membership (FEP vs. control) stored in participants.tsv.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003944

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 82 | admin | raw | Unidentified system marker - not suitable for epoching |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: FEP vs. Control Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Control` | 0 | Healthy control subject |
  | `FEP` | 1 | First Episode Psychosis patient |
- **Super Meta Notes**: Labels derived from clinical group membership in `participants.tsv` (column: group/diagnosis). Subject-level diagnosis applied to all EEG segments from each participant. No raw event markers available in data; all segments from a subject receive that subject's group label.
- **Evidence**:
  - DOI: 10.1038/s41598.024.66110.0 — Classifies FEP vs healthy controls using PSD features from 30-second segments of 5-min resting-state EEG, achieving 95.51% accuracy with Gaussian Process Classifier.
  - DOI: 10.3390/biomedicines11123223 — Uses ciSSA decomposition with entropy/statistical/frequency features, achieving 96.23% accuracy with SVM/ANN/ensemble classifiers.
- **Kernel Notes**: Load `participants.tsv`, extract group label for each subject (FEP vs Control), apply subject-level label to all segments. For 5-min recording at 1000 Hz with 30-s segments and 0.5 overlap: ~9-10 segments per subject. Extract PSD or time-frequency features per segment, then train binary classifier.

### Normal Task 1: FEP vs. Control Classification (binary, resting-state segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (label from participants.tsv group column)
- **Notes**: Purely resting-state dataset; segment continuously and assign subject-level diagnosis labels (FEP=1, control=0). No task events are available for epoch_by_event. Group label must be extracted from participants metadata.


## Data Quality Notes

- No meaningful event markers; `unknown` events should be excluded
- Subject count not specified in header; 82 files suggests ~82 subjects
- Verify FEP/control group balance in participants.tsv before training

## References

- _No paper reference available_
