# Somatosensory evoked potentials in the human spinal cord to mixed and sensory nerve stimulation

**Dataset**: `openneuro_ds004389` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004389
**Category**: Sensory/Response | **Subjects**: 26 | **Files (Completed)**: 260
**Channels**: 90 | **Sampling Rate**: 10000 Hz

## Paradigm

Simultaneous EEG, epidural spinal cord (ESG), nerve conduction (ENG), and EMG recordings during resting state and various conditions of mixed and sensory nerve stimulation of the arms and legs to evoke somatosensory potentials. The study compares spinal cord vs. cortical potentials for different stimulation types and sites.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004389

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 260x~1500 | long | raw | Electrical nerve stimulation onset |

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

### Primary Task 1: Publisher-defined BIDS task: Mediansensory
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004389 DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0


### Primary Task 2: Publisher-defined BIDS task: Medianmixed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004389 DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0


### Primary Task 3: Publisher-defined BIDS task: Tibialmixed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004389 DOI: https://doi.org/10.18112/openneuro.ds004389.v1.0.0


### Normal Task 1: SEP Stimulus Epoching (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one event class; suitable for evoked potential analysis. Multiple nerve sites (median mixed, median sensory, tibial) and stimulation conditions encoded in file/run naming.

| Event | y | Meaning |
 |-------|---|------|
 | `stimulus` | 0 | Nerve stimulation onset |
## Data Quality Notes

- Very high sampling rate (10 kHz) for SEP/ESG; downsampling required for standard EEG analysis
- 90 channels includes ESG, ENG, EMG, EOG, ECG channels - filter to EEG channels only
- 260 files across 26 subjects (multiple runs/conditions per subject)

## References

- **Reference**: `Somatosensory evoked potentials in the human spinal cord to mixed and sensory nerve stimulation.`
