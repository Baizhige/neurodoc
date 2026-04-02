# EEG-attention-rsvp-exp2

**Dataset**: `openneuro_ds004817` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004817
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 40
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task (Experiment 2) investigating the neural dynamics of prioritizing task-relevant information, using stimuli consisting of small objects superimposed on large letters. Participants performed target detection in rapid streams. Experiment 2 is a companion to Experiment 1 (ds004816) with different stimulus configurations (objects on letters rather than letters on objects).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004817

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 69137 | short | raw | RSVP event type 1 (task-relevant stimulus) |
| `E 2` | 69137 | short | raw | RSVP event type 2 (task-irrelevant stimulus) |
| `1` | 29376 | short | raw | Trigger code 1 (response or condition marker) |
| `0` | 29376 | short | raw | Trigger code 0 |
| `Event/E 1` | 10385 | short | raw | RSVP event type 1 (alternate format) |
| `Event/E 2` | 10385 | short | raw | RSVP event type 2 (alternate format) |
| `E 3` | 1921 | short | raw | RSVP event type 3 |
| `Event/E 3` | 289 | short | raw | RSVP event type 3 (alternate format) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: RSVP stimulus identity MVPA decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`, `Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` / `Event/E 1` | 0-15 | 16 object images (attended/task-relevant) |
  | `E 2` / `Event/E 2` | 0-15 | 16 object images (unattended/task-irrelevant) |
  | `E 3` / `Event/E 3` | 0-15 | 16 letters |
- **Super Meta Notes**: N/A (raw meta level)
- **Evidence**:
  - DOI: 10.51628/001c.21174 — EEG epochs extracted from -100ms to 1000ms relative to stimulus onset; MVPA decoding classified which of 16 objects or 16 letters was presented, plus object category (bird/fish/boat/plane) and animacy (animal/vehicle) classification.
- **Kernel Notes**: Aggregate duplicate event formats (E 1 with Event/E 1, etc.) before classification. The paper shows separate decoders for: (1) stimulus identity (16 objects + 16 letters), (2) category, and (3) animacy.

### Primary Task 2: Publisher-defined BIDS task: Rsvp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`E 1`, `E 2`, `E 3`, `Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004817 DOI: https://doi.org/10.51628/001c.21174

### Normal Task 1: RSVP target classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Companion to ds004816 (Experiment 1). Event/E 1 and Event/E 2 are identical events in different naming format - treat as same class or aggregate.

| Event | y | Meaning |
 |-------|---|------|
 | `E 1` | 0 | RSVP event type 1 |
 | `E 2` | 1 | RSVP event type 2 |
 | `E 3` | 2 | RSVP event type 3 |
 | `1` | 3 | Response/condition code 1 |
 | `0` | 4 | Response/condition code 0 |

## Data Quality Notes

- E 1/Event/E 1 and E 2/Event/E 2 are duplicate event formats - aggregate for analysis.
- Companion dataset: ds004816 is Experiment 1.

## References

- **Reference**: `Grootswagers T., Robinson A.K., Shatek S.M., Carlson T.A. (2021). The neural dynamics underlying prioritisation of task-relevant information. Neurons, Behaviour, Data Analysis, and Theory, 5(1)`
