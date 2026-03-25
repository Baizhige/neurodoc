# Neural Tracking to Go

**Dataset**: `openneuro_ds003801` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003801
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 24 | **Sampling Rate**: 250 Hz

## Paradigm

A mobile EEG study where participants performed a dichotic listening task (two competing speakers) while either sitting in a quiet indoor environment or walking along a pre-defined indoor route with environmental distractions. The study investigates how locomotion and environmental complexity affect neural tracking of attended speech (measured by auditory EEG envelope tracking). No discrete trial-level event markers were embedded in the EEG recording.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003801

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG during dichotic listening and walking |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Neural Tracking To Go
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003801 DOI: https://doi.org/10.18112/openneuro.ds003801.v1.0.0


### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (conditional label sit/walk needs to be obtained from file-level metadata))
- **Notes**: Mobile EEG; motion artifacts expected during walking condition. 20 subjects, 20 files (1 per subject). Condition (sitting/walking) is file-level metadata. Neural tracking of speech envelope requires cross-correlation with audio stimulus waveform.
## Data Quality Notes

- Mobile EEG recording; significant motion artifacts during walking condition.
- No trial-level event markers; condition label is file-level or block-level.
- Small dataset (20 subjects, 20 files); limited statistical power.
- 24-channel EEG at 250 Hz; modest spatial and temporal resolution.

## References

- **Reference**: `Neural Tracking to Go. OpenNeuro ds003801.`
