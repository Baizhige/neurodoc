# A test-retest resting and cognitive state EEG dataset

**Dataset**: `openneuro_ds004148` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004148
**Category**: High-level Mental | **Subjects**: 60 | **Files (Completed)**: 1797 | **Channels**: 61 | **Sampling Rate**: 500 Hz

## Paradigm

A test-retest reliability study recording EEG during five cognitive/resting conditions: eyes closed (EC), eyes open (EO), mental arithmetic (Ma), memory task (Me), and music listening (Mu), repeated across three sessions. Each file corresponds to one 5-minute condition block, with a single condition marker embedded (S 33=EO, S 44=EC, S 55=Mu, S 66=Me, S 77=Ma). Subjects are healthy adults aged 18-45.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004148

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 44` | 360 | long | raw | Eyes-closed resting state block label |
| `S 77` | 360 | long | raw | Mental arithmetic task block label |
| `S 66` | 360 | long | raw | Memory task block label |
| `S 55` | 360 | long | raw | Music listening block label |
| `S 33` | 357 | long | raw | Eyes-open resting state block label |
| `Sync Off` | ~270000 | admin | raw | Periodic sync signal (~150/file), not a trial event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 44`, `S 77`, `S 66`, `S 55`, `S 33`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Eyes closed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004148 DOI: https://doi.org/10.18112/openneuro.ds004148.v1.0.1


### Primary Task 2: Publisher-defined BIDS task: Mathematic
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004148 DOI: https://doi.org/10.18112/openneuro.ds004148.v1.0.1


### Primary Task 3: Publisher-defined BIDS task: Eyes open
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004148 DOI: https://doi.org/10.18112/openneuro.ds004148.v1.0.1


### Normal Task 1: Cognitive State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Each file contains exactly one condition marker; 1797 files x ~150s each. Sync Off is a periodic synchronization signal (150 per file), excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S 33` | 0 | Eyes-open resting state |
 | `S 44` | 1 | Eyes-closed resting state |
 | `S 55` | 2 | Music listening |
 | `S 66` | 3 | Memory task |
 | `S 77` | 4 | Mental arithmetic |
## Data Quality Notes

- Sync Off at ~150 events/file is hardware sync, not a task event
- Three test-retest sessions allow reliability analyses

## References

- **Reference**: `A test-retest resting and cognitive state EEG dataset`
