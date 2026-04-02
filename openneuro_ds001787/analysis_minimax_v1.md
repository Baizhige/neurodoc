# EEG meditation study

**Dataset**: `openneuro_ds001787` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

Subjects engaged in focused meditation sessions that were interrupted every two minutes by a brief probe assessing concentration level and mind-wandering. EEG was recorded continuously with stimulus markers at probe onsets and response markers at button-press responses. The study examined neural correlates of sustained attention and mind-wandering during meditation using ERP and time-frequency analysis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001787

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `response` | 40 (files) | short | raw | Participant button-press response to attention probe |
| `stimulus` | 40 (files) | short | raw | Probe stimulus onset (attention check) |
| `STATUS` | 5 | admin | raw | BioSemi system status marker - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: EEG Infraslow-GSR Coupling Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`meditation_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `high_d_prime_group` | 1 | High phase-amplitude coupling between EEG ISA phase and GSR amplitude |
  | `low_d_prime_group` | 0 | Low phase-amplitude coupling between EEG ISA phase and GSR amplitude |
- **Super Meta Notes**: Labels derived from d-prime computation of phase-amplitude coupling between EEG ISA phase and GSR amplitude; subjects divided into high/low d-prime groups based on channel-average d-prime values. Alternative labeling: expert meditators (y=1) vs novice (y=0).
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paper analyzes the coupling between EEG infraslow activity (0.01-0.1 Hz) phase and galvanic skin response amplitude during the first 30 seconds of each meditation trial from openneuro dataset ds001787, computing d-prime values and dividing subjects into high/low coupling groups.
- **Kernel Notes**: Must derive d-prime from EEG ISA phase and GSR amplitude time series, then threshold to create binary labels. Requires GSR channel presence in dataset.

### Primary Task 2: Publisher-defined BIDS task: Meditation
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 0 s *, target_events = [`stimulus`, `response`]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds001787 DOI: https://doi.org/10.18112/openneuro.ds001787.v1.1.1

### Normal Task 1: Stimulus-Response ERP (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is a BioSemi admin marker (count=5 files only) - excluded from target_events. Regression target: `response_time` from misc channel. The count column shows files-with-event, not total trial count.

 | Event | y | Meaning |
 |-------|---|---------|
 | `stimulus` | 0 | Probe stimulus onset |
 | `response` | 1 | Button-press response |

## Data Quality Notes

- `STATUS` events are BioSemi system markers, not task events - do not epoch on these.
- Multiple `response` events may occur per `stimulus` probe; consider windowing to first response only.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Arnaud Delorme (October 17, 2018; updated June 2024)`
