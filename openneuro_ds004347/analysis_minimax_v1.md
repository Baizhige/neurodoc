# Symmetry perception and affective responses: a combined EEG/EMG study

**Dataset**: `openneuro_ds004347` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004347
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed a visual perception task identifying whether stimuli were regular (symmetric) or random (asymmetric) patterns to investigate symmetry perception and affective responses. EEG and EMG were simultaneously recorded to capture both neural and facial muscle activity. No trial-level event markers are present in the EEG files; the dataset is processed as continuous recordings.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004347

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Visual Symmetry Perception Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 1.0 s, target_events = [`reflection`, `random`, `rotation`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `reflection` | 0 | Reflectional symmetry (regular pattern) |
  | `rotation` | 0 | Rotational symmetry (regular pattern) |
  | `random` | 1 | Asymmetric/random pattern |
- **Super Meta Notes**: (NONE) Raw conditions from experimental design
- **Evidence**:
  - DOI: 10.1016/j.neuropsychologia.2012.10.003 — Paper describes the experimental paradigm underlying this dataset (symmetry vs random pattern classification) using epochs time-locked to stimulus onset with 80 trials per condition, analyzing ERPs (P1, N1, sustained posterior negativity) and time-frequency power.
- **Kernel Notes**: Verify event markers in BIDS events.tsv files; baseline correction -200 to +50ms recommended for ERP epochs. Alternative epoch window tmax=3.0s supported for time-frequency analysis per the same paper.

### Normal Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: No trial markers in EEG files; use sliding window segmentation. Subject-level labels (symmetric vs. random condition blocks) may be available from experimental design metadata.

## Data Quality Notes

- No trial-level event markers in the EEG files
- 73 channels includes EMG/EOG channels that should be excluded from EEG analysis
- Continuous recordings suitable for spectral or connectivity analysis

## References

- **Reference**: `Symmetry perception and affective responses: a combined EEG/EMG study.`
