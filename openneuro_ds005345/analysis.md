# Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset

**Dataset**: `openneuro_ds005345` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005345
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 28
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants engaged in naturalistic listening to excerpts of "Le Petit Prince" (The Little Prince) under single-talker and multi-talker conditions during simultaneous EEG and 7T fMRI recording. The study investigates neural processing of speech under cocktail-party-style listening conditions. Stimulus/S 11 marks single-talker condition onsets; Stimulus/S 31-S 34 mark multi-talker condition variants. `Comment/actiCAP Data On` is an EEG system administrative marker.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005345

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 11` | ~19/file | long | raw | Single-talker listening block onset |
| `Stimulus/S 31` | ~6/file | long | raw | Multi-talker condition variant 31 onset |
| `Stimulus/S 32` | ~6/file | long | raw | Multi-talker condition variant 32 onset |
| `Stimulus/S 33` | ~6/file | long | raw | Multi-talker condition variant 33 onset |
| `Stimulus/S 34` | ~6/file | long | raw | Multi-talker condition variant 34 onset |
| `Comment/actiCAP Data On` | 25/file | admin | raw | EEG recording system marker (exclude) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Multitalker
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005345 DOI: https://doi.org/10.18112/openneuro.ds005345.v1.0.1


### Primary Task 2: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005345 DOI: https://doi.org/10.18112/openneuro.ds005345.v1.0.1


### Normal Task 1: Listening Condition Classification (binary/multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `Comment/actiCAP Data On` is admin - exclude. Naturalistic listening paradigm with sustained EEG blocks. Very small dataset (28 files, 25 subjects).

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus/S 11` | 0 | Single-talker listening |
 | `Stimulus/S 31` | 1 | Multi-talker condition 31 |
 | `Stimulus/S 32` | 2 | Multi-talker condition 32 |
 | `Stimulus/S 33` | 3 | Multi-talker condition 33 |
 | `Stimulus/S 34` | 4 | Multi-talker condition 34 |
## Data Quality Notes

- Very small dataset (28 files, 25 subjects).
- `Comment/actiCAP Data On` is an admin system marker - exclude from epoching.
- Simultaneous 7T fMRI - MR gradient artifacts may require removal if present.

## References

- **Reference**: `Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset`
