# IACKD: Intention Action Conflict EEG-Hand Kinematics Dataset

**Dataset**: `openneuro_ds006840` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006840
**Category**: High-level Mental | **Subjects**: 128 | **Files (Completed)**: 128 | **Channels**: 29 | **Sampling Rate**: 1024 Hz

## Paradigm

This dataset investigates the neural correlates and hand kinematics associated with conflicts between intended and executed actions. In an intention-action conflict paradigm, participants are cued to perform one action but must sometimes execute a competing action, creating conflict between motor intention and execution. EEG is recorded alongside hand kinematic data during pre-movement planning (`premove`), execution (`execution`), and successful hit trials (`hit`).

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `execution` | 7032 | short | raw | Motor execution onset |
| `hit` | 7032 | short | raw | Successful action completion marker |
| `premove` | 7029 | short | raw | Pre-movement preparation period onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

[Placeholder for file scan summary information]

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Intention action congruency
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006840 DOI: https://doi.org/10.18112/openneuro.ds006840.v1.0.0

### Normal Task 1: Motor Phase Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Well-balanced 3-class design (~7032 each). Hand kinematic data available alongside EEG for multimodal analysis. BrainVision format.

 | Event | y | Meaning |
 |-------|---|---------|
 | `premove` | 0 | Pre-movement intention/preparation |
 | `execution` | 1 | Motor execution onset |
 | `hit` | 2 | Successful trial completion |
## Data Quality Notes

- Consistent event structure (~7029-7032 events per type); well-controlled paradigm.
- Kinematic data channels (VEOG, HEOG, Trigger) should be excluded from EEG analysis.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006840