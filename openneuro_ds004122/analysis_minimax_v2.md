# BCIT Speed Control

**Dataset**: `openneuro_ds004122` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004122
**Category**: Complex Applied | **Subjects**: 63 | **Files (Completed)**: 63
**Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

A simulated driving task assessing driver fatigue and performance through a speed control manipulation: subjects drove under either manual speed control (maintaining speed without cruise control) or automated speed control (cruise control active), while also performing manual steering corrections for lateral vehicle perturbations. The study investigates how automation of one driving sub-task affects neural fatigue signatures.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004122

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4210` | 63 files | short | raw | Perturbation onset |
| `4220` | 63 files | short | raw | Perturbation event |
| `4230` | 63 files | short | raw | Perturbation/direction event |
| `4311` | 63 files | short | raw | Lateral perturbation type 1 |
| `4312` | 63 files | short | raw | Lateral perturbation type 2 |
| `3200` | 63 files | short | raw | Speed control state marker |
| `3111` | 63 files | short | raw | Perturbation onset |
| `3310` | 63 files | short | raw | Performance metric event |
| `1211` | 63 files | short | raw | Lane correction event |
| `1212` | 59 files | short | raw | Lane correction event |
| `1121`-`1122` | 63 files | short | raw | Driver response events |
| `1111`-`1112` | 63 files | short | raw | Driver response events |
| `2621`-`2622` | 61 files | short | raw | Behavioral response / auditory cue |
| `3112` | 59 files | short | raw | Perturbation response |
| `4411` | 5 files | short | raw | Rare event |
| `4421` | 6 files | short | raw | Rare event |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Lateral Perturbation Direction (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = [`4311`, `4312`]
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `4311` | 0 | Lateral perturbation - type 1 |
  | `4312` | 1 | Lateral perturbation - type 2 |
- **Evidence**: No paper evidence specifically references this dataset with this task.
- **Kernel Notes**: Verify event ID mapping from events.tsv. Speed control condition (manual vs. automated) may serve as between-subjects variable.


## Data Quality Notes

- 74-channel BioSemi ActiveTwo; 1024 Hz sampling
- Speed control condition variable requires session metadata from participants.tsv
- Full event code decoding requires BCIT codebook

## References

- _No paper reference available_
