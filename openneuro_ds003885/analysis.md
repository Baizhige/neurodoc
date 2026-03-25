# Capacity for movement is an organisational principle in object representations: EEG data from Experiment 1

**Dataset**: `openneuro_ds003885` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003885
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 48
**Channels**: 127 | **Sampling Rate**: 250 Hz

## Paradigm

Participants performed a semantic classification task (alive vs. not alive) and a passive viewing task using RSVP streams of images to investigate the neural representations of object movement and aliveness. Images spanned animate and inanimate categories with varying degrees of movement capacity, presented at ~3 Hz in RSVP. The study aimed to decode movement-related object properties from EEG representational geometry.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003885

## Event Structure

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

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Movement
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003885 DOI: https://doi.org/10.18112/openneuro.ds003885.v1.0.8


### Normal Task 1: Movement Capacity Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: E 8 and E 9 together account for ~76% of all events (~4,800 each per subject vs ~1,600 for conditions 1-5). E 4 is rare (40/subject) and likely a block marker. Data from derivatives/eeglab with 128-channel cap. Consider binary alive/not-alive classification using E 8/E 9.

| Event | y | Meaning |
 |-------|---|------|
 | `E 1` | 0 | Object category 1 |
 | `E 2` | 1 | Object category 2 |
 | `E 3` | 2 | Object category 3 |
 | `E 5` | 3 | Object category 5 |
 | `E 8` | 4 | Object category 8 (most frequent - likely animate/movement-capable) |
 | `E 9` | 5 | Object category 9 (most frequent - likely inanimate/no movement) |
## Data Quality Notes

- Data from derivatives/eeglab; preprocessed with EEGLAB
- 128 channels recorded but analysis.md reports 127 (one likely reference or EOG)
- Very consistent event counts across all 24 subjects

## References

- **Reference**: `Shatek, S. M., Robinson, A. K., Grootswagers, T., & Carlson, T. A. (2022). Capacity for movement is an organisational principle in object representations. NeuroImage, 261, 119517.`
