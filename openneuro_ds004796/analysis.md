# PEARL-Neuro Database (Alzheimer's Risk Genes, Lifestyle, Neuroimaging)

**Dataset**: `openneuro_ds004796` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004796
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 233
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

A multimodal neuroimaging database of healthy middle-aged adults (50-63 years) carrying Alzheimer's risk genes (APOE, PICALM). The EEG protocol includes resting-state recordings (eyes open and closed) and two active cognitive tasks: the Multi-Source Interference Task (MSIT) and Sternberg's memory task. Stimulus and button-press response events are recorded across task sessions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004796

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 27862 | short | raw | Stimulus onset (MSIT or Sternberg item) |
| `response` | 24051 | short | raw | Participant button-press response |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Cognitive control decoding in MSIT paradigm
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation` or `misc`
- **Target Definition**: Interference/congruency condition and/or DBS ON/OFF effect labels
- **Evidence**: Dataset/paper center on MSIT cognitive control under DBS modulation. Source: https://doi.org/10.1038/s41597-024-03106-5


### Primary Task 2: Publisher-defined BIDS task: Sternberg
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1038/s41597-024-03106-5


### Primary Task 3: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1038/s41597-024-03106-5


### Normal Task 1: Stimulus vs response classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 233 files = 79 subjects x ~3 sessions. Resting-state sessions have no stimulus events; only task sessions contribute stimulus/response epochs.

| Event | y | Meaning |
 |-------|---|------|
 | `stimulus` | 0 | Stimulus onset |
 | `response` | 1 | Button-press response |
## Data Quality Notes

- Mixed resting-state and task sessions; filter by file task label.
- High channel count (127); may include non-EEG channels.

## References

- **Reference**: `PEARL-Neuro Database: EEG, fMRI, health and lifestyle data of middle-aged people at risk of dementia. DOI: 10.1038/s41597-024-03106-5`
