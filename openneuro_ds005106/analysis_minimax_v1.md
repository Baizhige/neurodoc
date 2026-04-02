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

### Primary Task 1: 200-Way Multiclass Object Image Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`1`, `2`, `3`, ..., `200`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Object image ID 1 |
  | `2` | 1 | Object image ID 2 |
  | ... | ... | ... |
  | `200` | 199 | Object image ID 200 |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04744-z — This paper describes the dataset of 42 infant EEG recordings during rapid serial visual presentation of 200 object images, using epochs from -100 to 800 ms relative to stimulus onset for representational similarity analysis and multivariate pattern classification to decode object-specific neural representations.
  - DOI: 10.31234/osf.io.dzrkq — This paper presents the OpenNeuro ds005106 dataset of 42 infant EEG recordings during RSVP of 200 object images and performs time-resolved multivariate pattern analysis to decode object identity from neural responses.
- **Kernel Notes**: Exclude event code -1 (baseline/ITI marker). Each object code has ~219 occurrences. The 5Hz RSVP rate means stimuli are presented every 200ms; epoch window captures the N200/P300 ERP window typical for object recognition.

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
