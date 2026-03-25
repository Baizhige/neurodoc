# EEG dataset for speech decoding

**Dataset**: `openneuro_ds006104` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006104
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 80 | **Channels**: 62 | **Sampling Rate**: 2000 Hz

## Paradigm

A phoneme discrimination task where participants listened to speech sounds - including single phonemes, phoneme pairs, and words - while undergoing transcranial magnetic stimulation (TMS) to test the role of speech motor cortex in auditory speech perception. Subjects provided button-press responses after each sound. The dataset supports decoding of speech perception from TMS-EEG.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006104

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TMS` | 29260 | short | raw | TMS pulse delivery |
| `stimulus` | 29260 | short | raw | Auditory speech stimulus onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Phonemes
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006104 DOI: https://doi.org/10.18112/openneuro.ds006104.v1.0.1


### Primary Task 2: Publisher-defined BIDS task: Words
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006104 DOI: https://doi.org/10.18112/openneuro.ds006104.v1.0.1


### Primary Task 3: Publisher-defined BIDS task: Single phoneme
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006104 DOI: https://doi.org/10.18112/openneuro.ds006104.v1.0.1


### Normal Task 1: TMS vs Stimulus Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Binary classification (TMS vs stimulus). TMS pulses produce large artifacts; apply TMS artifact rejection before epoching.

 | Event | y | Meaning |
 |-------|---|---------|
 | `TMS` | 0 | TMS pulse |
 | `stimulus` | 1 | Speech stimulus onset |
## Data Quality Notes

- Very high sampling rate (2000 Hz); downsample to 500 Hz for most analyses.
- TMS pulses produce large EEG artifacts requiring specialized artifact removal.
- Apply bandpass filter (1-80 Hz) after TMS artifact correction.

## References

- **Reference**: `Moreira et al. "An open-access EEG dataset for speech decoding: Exploring the role of articulation and coarticulation"`
