# EEG Recordings during Sham Neurofeedback in Virtual Reality

**Dataset**: `openneuro_ds006839` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006839
**Category**: Complex Applied | **Subjects**: 144 | **Files (Completed)**: 144 | **Channels**: 29 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed an attentional task within a virtual reality environment while receiving sham neurofeedback with positive, negative, or control feedback valences. The study investigates alpha-band modulation in response to perceived performance feedback without actual neurofeedback. Numeric trigger codes mark trial onsets and feedback conditions. The paradigm examines placebo effects of neurofeedback on neural oscillations and attention.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006839

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `190` | 10264 | short | raw | Positive feedback condition marker |
| `222` | 5389 | short | raw | Control (neutral) feedback condition |
| `126` | 576 | short | raw | Trial/block onset marker |
| `238` | 431 | short | raw | Negative feedback condition marker |
| `0` | 98 | admin | raw | Null/reset event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Positive
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006839 DOI: https://doi.org/10.18112/openneuro.ds006839.v1.0.0


### Primary Task 2: Publisher-defined BIDS task: Control
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006839 DOI: https://doi.org/10.18112/openneuro.ds006839.v1.0.0


### Primary Task 3: Publisher-defined BIDS task: Negative
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006839 DOI: https://doi.org/10.18112/openneuro.ds006839.v1.0.0


### Normal Task 1: Neurofeedback Valence Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Decode trigger codes from events.tsv. Code `0` is a null/reset event. Primary contrast is positive (190) vs negative (238) vs neutral (222) feedback valence. Classes are imbalanced (190: 10264 vs 238: 431).

 | Event | y | Meaning |
 |-------|---|---------|
 | `126` | 0 | Trial/block onset marker |
 | `190` | 1 | Positive sham neurofeedback |
 | `238` | 2 | Negative sham neurofeedback |
 | `222` | 3 | Control (neutral) feedback |
 | `0` | 4 | Null/reset event |
## Data Quality Notes

- Classes are imbalanced: code 190 (10264) >> 238 (431); balance before classification.
- VR environment may introduce motion artifact; check for movement-related noise.
- Numeric trigger codes require decoding from events.tsv or README.

## References

- **Reference**: `EEG recordings during sham neurofeedback in virtual reality`
