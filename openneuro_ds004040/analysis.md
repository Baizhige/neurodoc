# Trance channeling EEG study

**Dataset**: `openneuro_ds004040` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004040
**Category**: High-level Mental | **Subjects**: 13 | **Files (Completed)**: 26
**Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants who are experienced trance channelers performed alternating 5-minute blocks of trance channeling (a mediumistic altered state of consciousness) and matched resting state conditions across two separate sessions. The study investigates neural correlates of voluntarily induced altered states of consciousness compared to wakeful rest. Labels for trance vs. rest blocks must be derived from the session/task structure rather than discrete event markers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004040

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STATUS` | 26 files | admin | raw | System hardware status marker - not suitable for epoching |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Trance
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004040 DOI: https://doi.org/10.18112/openneuro.ds004040.v1.0.0


### Normal Task 1: Trance vs. Resting State (binary, segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (condition label from task/session structure)
- **Notes**: STATUS is an admin marker and must be excluded. Block-level labels (trance vs. rest) should come from the BIDS task name or session metadata. 13 subjects x 2 sessions = 26 files. Small sample size; suitable for within-subject analysis.
## Data Quality Notes

- Only STATUS admin marker present; no task-level event markers
- Small sample (13 specialized subjects who practice trance channeling)
- Two sessions per subject - verify session labeling in BIDS structure

## References

- **Reference**: `Trance channeling EEG study`
