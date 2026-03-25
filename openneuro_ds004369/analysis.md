# Blink-Pause-Relation (Competing Speaker Paradigm)

**Dataset**: `openneuro_ds004369` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004369
**Category**: High-level Mental | **Subjects**: 41 | **Files (Completed)**: 41
**Channels**: 7 | **Sampling Rate**: 500 Hz

## Paradigm

A two-competing speaker paradigm where participants selectively attended to one of two concurrently presented audiobooks while ignoring the other. EEG was recorded to study the relationship between eye blinks and speech pauses during continuous auditory attention. No trial-level event markers are present in the EEG files.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004369

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

### Primary Task 1: Publisher-defined BIDS task: Attended Speaker Paradigm
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004369 DOI: https://doi.org/10.18112/openneuro.ds004369.v1.0.1


### Normal Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: No trial markers in EEG files; use sliding window segmentation. Only 7 channels (very low-density). Subject-level labels (attended speaker, blink/pause occurrence) may be available from behavioral logs.
## Data Quality Notes

- Very sparse channel setup (7 channels only)
- No trial-level event markers in the EEG files
- Continuous naturalistic listening paradigm (audiobook)

## References

- **Reference**: `Jaeger et al. (2020); Holtze et al. (2021)`
