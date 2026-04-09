# Temporal Scaling

**Dataset**: `openneuro_ds004200` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004200
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 37 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants learned to produce and judge short, medium, and long temporal intervals through interleaved production and perception tasks with visual feedback. Trigger codes encode condition combinations: tens digit indicates task type and interval length (1x=production, 2x-6x=other conditions), units digit indicates subcondition or phase. The study investigates how humans scale temporal interval representations.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `11` | ~20 | short | raw | Production short interval phase 1 |
| `12` | ~20 | short | raw | Production short interval phase 2 |
| `13` | ~20 | short | raw | Production short interval phase 3 |
| `21` | ~20 | short | raw | Condition 2, phase 1 |
| `22` | ~20 | short | raw | Condition 2, phase 2 |
| `23` | ~20 | short | raw | Condition 2, phase 3 |
| `31` | ~20 | short | raw | Condition 3, phase 1 |
| `32` | ~20 | short | raw | Condition 3, phase 2 |
| `33` | ~20 | short | raw | Condition 3, phase 3 |
| `41` | ~20 | short | raw | Condition 4, phase 1 |
| `42` | ~20 | short | raw | Condition 4, phase 2 |
| `43` | ~20 | short | raw | Condition 4, phase 3 |
| `51` | ~20 | short | raw | Condition 5, phase 1 |
| `52` | ~20 | short | raw | Condition 5, phase 2 |
| `53` | ~20 | short | raw | Condition 5, phase 3 |
| `61` | ~20 | short | raw | Condition 6, phase 1 |
| `62` | ~20 | short | raw | Condition 6, phase 2 |
| `63` | ~20 | short | raw | Condition 6, phase 3 |
| `17` | ~20 | short | raw | Feedback/response code |
| `27` | ~20 | short | raw | Feedback/response code |
| `47` | ~20 | short | raw | Feedback/response code |
| `57` | ~20 | short | raw | Feedback/response code |
| `67` | ~20 | short | raw | Feedback/response code |
| `2` | ~20 | admin | raw | Block/session boundary marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

[Placeholder content]

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Temporalscaling
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004200 DOI: https://doi.org/10.18112/openneuro.ds004200.v1.0.1


### Normal Task 1: Temporal Condition Multiclass (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Trigger code `2` is a block marker, excluded. Decode exact condition meanings from paper or events.tsv.

 | Event | y | Meaning |
 |-------|---|---------|
 | `11` | 0 | Cond 1 phase 1 |
 | `12` | 1 | Cond 1 phase 2 |
 | `13` | 2 | Cond 1 phase 3 |
 | `21` | 3 | Cond 2 phase 1 |
 | `22` | 4 | Cond 2 phase 2 |
 | `23` | 5 | Cond 2 phase 3 |
 | `31` | 6 | Cond 3 phase 1 |
 | `32` | 7 | Cond 3 phase 2 |
 | `33` | 8 | Cond 3 phase 3 |
 | `41` | 9 | Cond 4 phase 1 |
 | `42` | 10 | Cond 4 phase 2 |
 | `43` | 11 | Cond 4 phase 3 |
 | `51` | 12 | Cond 5 phase 1 |
 | `52` | 13 | Cond 5 phase 2 |
 | `53` | 14 | Cond 5 phase 3 |
 | `61` | 15 | Cond 6 phase 1 |
 | `62` | 16 | Cond 6 phase 2 |
 | `63` | 17 | Cond 6 phase 3 |
 | `17` | 18 | Feedback 1 |
 | `27` | 19 | Feedback 2 |
 | `47` | 20 | Feedback 4 |
 | `57` | 21 | Feedback 5 |
 | `67` | 22 | Feedback 6 |

## Data Quality Notes

- Numerical trigger codes require decode from paper
- Small dataset (N=20)

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004200