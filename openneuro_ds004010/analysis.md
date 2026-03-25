# MAVIS

**Dataset**: `openneuro_ds004010` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004010
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24
**Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

A multisensory detection task (MAVIS) in which participants identified auditory and visual targets embedded within simultaneous audio-visual noise streams to investigate selective attention and crossmodal sensory processing. The dataset contains continuous EEG recordings without discrete event markers, suggesting the stimuli were presented as ongoing streams rather than discrete trials.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004010

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

### Primary Task 1: Publisher-defined BIDS task: MAVIS
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004010 DOI: https://doi.org/10.18112/openneuro.ds004010.v1.0.0


### Normal Task 1: Continuous EEG Segmentation (resting/continuous)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (no trial-level events available)
- **Notes**: No event markers present. Use continuous segmentation for downstream tasks such as subject identification or spectral analysis. Task condition labels (if any) must come from external behavioral logs or stimulus delivery system.
## Data Quality Notes

- No trial-level event markers; only continuous EEG available
- Stimulus delivery information may be in auxiliary files outside the BIDS structure
- 64 channels at 1000 Hz provides good temporal resolution for auditory processing analysis

## References

- **Reference**: `MAVIS`
