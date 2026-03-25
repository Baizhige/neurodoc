# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21
**Channels**: 18 | **Sampling Rate**: 500 Hz

## Paradigm

Participants with orthopedic impairment performed four distinct motor imagery tasks (Reach, Twist, Lift, and Grasp) guided by visual cues across three experimental sessions. EEG and fNIRS were recorded simultaneously to study motor imagery neural patterns in a clinical population for BCI development. Each trial began with a rest cue (S 1) followed by a task cue (S 2-S 10), with S 7-S 10 encoding the four MI conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004022

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 2` | 21 files | short | raw | Cue onset (task start) |
| `S 7` | 21 files | short | raw | Motor imagery cue - task 1 (Reach) |
| `S 8` | 21 files | short | raw | Motor imagery cue - task 2 (Twist) |
| `S 9` | 21 files | short | raw | Motor imagery cue - task 3 (Lift) |
| `S 10` | 21 files | short | raw | Motor imagery cue - task 4 (Grasp) |
| `S 3` | 21 files | short | raw | Rest period cue |
| `S 4` | 21 files | short | raw | Rest period cue (variant) |
| `S 5` | 21 files | short | raw | Feedback/response marker |
| `S 6` | 21 files | short | raw | Feedback/response marker |
| `S 1` | 21 files | short | raw | Trial start / baseline cue |
| `condition 12` | 21 files | admin | raw | Condition block marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 2`, `S 7`, `S 8`, `S 9`, `S 10`, `S 3`, `S 4`, `S 5`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds004022 DOI: https://doi.org/10.18112/openneuro.ds004022.v1.0.0


### Normal Task 1: Four-Class Motor Imagery (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 7 subjects; small sample size limits generalization. `condition 12` is an admin/block marker to exclude. 3 sessions per subject (21 files total). Each session has 40 trials per MI class.

| Event | y | Meaning |
 |-------|---|------|
 | `S 7` | 0 | Motor imagery - Reach |
 | `S 8` | 1 | Motor imagery - Twist |
 | `S 9` | 2 | Motor imagery - Lift |
 | `S 10` | 3 | Motor imagery - Grasp |
## Data Quality Notes

- Only 7 subjects with orthopedic impairment - very small clinical sample
- 18-channel EEG with motor cortex coverage; suitable for BCI but limited spatial resolution
- `condition 12` is a block marker to exclude from epoching

## References

- **Reference**: `Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment`
