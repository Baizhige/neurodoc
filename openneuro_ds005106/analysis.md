# Human Infant EEG for 200 Object Images in Rapid Visual Streams

**Dataset**: `openneuro_ds005106` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005106
**Category**: Sensory/Response | **Subjects**: 42 | **Files (Completed)**: 42 | **Channels**: 32 | **Sampling Rate**: 500 Hz

## Paradigm

Infants viewed 200 distinct object images presented in rapid visual streams (RSVP) while EEG was recorded to study the development of visual object representations. Each numeric trigger code corresponds to one of 200 object IDs; code -1 is a baseline/inter-stimulus marker. The dataset enables decoding of object-specific neural representations in the infant brain.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005106

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `-1` | 43105 | short | raw | Baseline / inter-stimulus marker |
| `155` | 220 | short | raw | Object image 155 onset |
| `123` | 220 | short | raw | Object image 123 onset |
| `72` | 219 | short | raw | Object image 72 onset |
| `147` | 219 | short | raw | Object image 147 onset |
| `(~196 more object codes)` | ~219 each | short | raw | Individual object image onsets (IDs 1-200) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Fix
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005106 DOI: https://doi.org/10.1167/13.10.1


### Normal Task 1: Object Image Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Code -1 is a baseline/ITI marker - exclude from classification. ~200 object classes with ~219 occurrences each. Representational similarity analysis (RSA) is a primary use case.

 | Event | y | Meaning |
 |-------|---|---------|
 | (numeric codes 1-200) | 0-199 | Object image ID (200 classes) |
## Data Quality Notes

- ~200 unique object trigger codes - each code represents one object image.
- Code -1 is a baseline/ITI marker and should be excluded.
- Infant EEG - expect high noise and movement artifacts.

## References

- **Reference**: `Human Infant EEG Recordings for 200 Object Images Presented in Rapid Visual Streams`
