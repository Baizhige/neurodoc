# Capacity for movement is an organisational principle in object representations: EEG data from Experiment 2

**Dataset**: `openneuro_ds003887` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003887
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 48
**Channels**: 127 | **Sampling Rate**: 250 Hz

## Paradigm

Participants performed time-pressured categorization of static images based on movement capacity and completed a passive viewing task using Rapid Serial Visual Presentation (RSVP). This second experiment extends Experiment 1 by testing whether movement capacity organization in neural object representations generalizes across different task contexts and classification criteria.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 8` | ~115,200 | short | raw | RSVP image onset - condition 8 |
| `E 9` | ~115,200 | short | raw | RSVP image onset - condition 9 |
| `E 1` | ~38,400 | short | raw | RSVP image onset - condition 1 |
| `E 2` | ~38,400 | short | raw | RSVP image onset - condition 2 |
| `E 3` | ~38,400 | short | raw | RSVP image onset - condition 3 |
| `E 5` | ~38,400 | short | raw | RSVP image onset - condition 5 |
| `E 4` | ~960 | short | raw | Block boundary or special event |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### Info

No additional info available.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Movement
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003887 DOI: https://doi.org/10.18112/openneuro.ds003887.v1.2.3


### Normal Task 1: Movement Capacity Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Identical event structure to ds003885 (Experiment 1). E 8 and E 9 are the dominant categories (~4,800 each per subject). E 4 is rare (40/subject) and likely marks block boundaries. Binary E 8 vs E 9 classification (movement-capable vs not) is the primary task.

| Event | y | Meaning |
| `E 1` | 0 | Object category 1 |
| `E 2` | 1 | Object category 2 |
| `E 3` | 2 | Object category 3 |
| `E 5` | 3 | Object category 5 |
| `E 8` | 4 | Object category 8 (movement-capable / animate) |
| `E 9` | 5 | Object category 9 (no movement / inanimate) |
## Data Quality Notes

- Data from derivatives/eeglab; preprocessed with EEGLAB
- 128-channel cap, 127 usable channels after reference removal
- Consistent event counts across all 24 subjects

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003887