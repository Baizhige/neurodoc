# EEG: Attended Speaker Paradigm (Own Name in Ignored Stream)

**Dataset**: `openneuro_ds003516` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003516
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 49 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a cocktail-party selective auditory attention task with two competing speakers. They listened to audio books from one speaker (attended stream) while their own name was occasionally presented in the ignored stream. This paradigm investigates the neural correlates of selective attention and the salience of self-referential stimuli (own name) in the unattended auditory channel. No discrete trial-level event markers were recorded in the EEG data.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003516

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG recording |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Attended Speaker Paradigm Own Name
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003516 DOI: https://doi.org/10.1038/nn.3063


### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no labels, for unsupervised or feature extraction))
- **Notes**: No trial-level annotations available; treat as continuous listening EEG. Suitable for neural tracking analyzes or subject-level classification using demographic labels.
## Data Quality Notes

- No event markers present; cannot epoch by stimulus onset.
- Continuous EEG during selective attention task; audio stimuli timing not embedded in EEG annotations.

## References

- **Reference**: `Bjorn Holtze (January, 2021). Own-name salience in selective auditory attention.`
