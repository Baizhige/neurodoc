# Rotation-tolerant representations elucidate the time course of high-level object processing

**Dataset**: `openneuro_ds004252` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004252
**Category**: Sensory/Response | **Subjects**: 1 | **Files (Completed)**: 1
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

A single participant viewed visual stimuli of objects at various rotations to investigate the neural time course of rotation-tolerant, high-level object representations. A rapid serial visual presentation (RSVP) design was used with three event types encoding distinct stimulus categories or conditions. The study is a single-subject pilot or proof-of-concept recording.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004252

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E 1` | 14400 | short | raw | Stimulus condition 1 (object/rotation category A) |
| `Event/E 2` | 14400 | short | raw | Stimulus condition 2 (object/rotation category B) |
| `Event/E 3` | 120 | short | raw | Stimulus condition 3 (object/rotation category C) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: 60-way object category classification (rotation-tolerant decoding)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Object/rotation condition 1 (subset of 60 objects) |
  | `Event/E 2` | 1 | Object/rotation condition 2 (subset of 60 objects) |
  | `Event/E 3` | 2 | Object/rotation condition 3 (subset of 60 objects) |
- **Evidence**:
  - DOI: 10.31234/osf.io.wp73u — "This study used EEG data from OpenNeuro ds004252 to decode 60-way object classification using multivariate pattern analysis, comparing fixed-rotation decoding with rotation-tolerant decoding, with epochs from -100ms to 800ms relative to stimulus onset."
- **Kernel Notes**: The 60 objects (12 categories × 5 exemplars) are presented at 8 rotations each. Raw events E1-E3 group the stimuli into 3 coarse categories. Verify if finer-grained 60-way labels can be reconstructed from stimulus metadata; otherwise use the 3-class mapping. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Object Category Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 1 subject; not suitable for cross-subject generalization. Event/E 3 count (120) is far lower than E 1 and E 2 (14400 each) - severe class imbalance. Decode exact condition mapping from paper.

| Event | y | Meaning |
|-------|---|------|
| `Event/E 1` | 0 | Object/rotation condition 1 |
| `Event/E 2` | 1 | Object/rotation condition 2 |
| `Event/E 3` | 2 | Object/rotation condition 3 |

## Data Quality Notes

- Single subject; results not generalizable across subjects
- 127 channels (1 reference electrode excluded)
- Severe class imbalance: E 1 and E 2 have 14400 trials each vs. E 3 with only 120

