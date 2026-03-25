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

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds003947 DOI: https://doi.org/10.18112/openneuro.ds003947.v1.0.1


### Normal Task 1: FEP vs. Control Classification (binary, resting-state segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (label from participants.tsv group column)
- **Notes**: Purely resting-state dataset; segment continuously and assign subject-level diagnosis labels (FEP=1, control=0). High sampling rate (3000 Hz) - consider downsampling to 500 Hz before processing to reduce computational load.
## Data Quality Notes

- No meaningful event markers; `unknown` events should be excluded
- Very high sampling rate (~3000 Hz) may require downsampling
- Companion dataset to ds003944 (Task 1); can be combined for larger resting FEP cohort

## References

- _No paper reference available_
