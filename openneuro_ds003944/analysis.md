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

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds003944 DOI: https://doi.org/10.18112/openneuro.ds003944.v1.0.1


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
