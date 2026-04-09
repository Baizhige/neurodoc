# Multiple Object Monitoring EEG

**Dataset**: `openneuro_ds006768` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006768
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 210 | **Channels**: 65 | **Sampling Rate**: 1000 Hz

## Paradigm

Subjects completed a Multiple Object Monitoring (MOM) task requiring sustained visual attention to track multiple moving objects simultaneously. In each trial, a subset of objects is designated as targets at the start, then all objects move during a tracking period, and subjects report which objects were targets. EEG captures neural correlates of visual attention load and tracking accuracy. Events mark trial onset, target designation, and distractor appearances.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event` | 20384 | short | raw | Generic trial event marker |
| `target` | 11004 | short | raw | Target object onset (object to be tracked) |
| `distractor` | 11004 | short | raw | Distractor object onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### MISC Label Summary

No MISC labels identified in this dataset.

### Info

No additional scan information available.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: MOM
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006768 DOI: https://doi.org/10.1101/2025.07.10.663816


### Normal Task 1: Target vs Distractor Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Well-balanced binary contrast: target vs. distractor (11004 each). `event` is a generic trial marker. 210 files from 30 subjects (7 runs/subject on average).

 | Event | y | Meaning |
 |-------|---|---------|
 | `event` | 0 | Generic trial event marker |
 | `target` | 1 | Target object to be tracked |
 | `distractor` | 2 | Distractor object |
## Data Quality Notes

- 210 files from 30 subjects suggests ~7 runs per subject.
- `event` is a generic trial marker; prefer specific `target`/`distractor` events for classification.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006768