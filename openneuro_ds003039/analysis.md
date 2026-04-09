# Free walking study

**Dataset**: `openneuro_ds003039` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003039
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

Participants walked two different outdoor routes, once while performing a self-paced button-pressing task, to study brain activity during naturalistic free-walking gait. This is a mobile EEG study; no trial-level event markers are detectable in the EEG files. Button-press events from the self-paced task may be available in separate behavioral logs.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; naturalistic free-walking paradigm |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

### Info

*Info placeholder: File scan details to be populated.*

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Neur Corr Young
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003039 DOI: https://doi.org/10.18112/openneuro.ds003039.v1.0.2


### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level events in EEG files))
- **Notes**: Mobile EEG during naturalistic walking. Motion artifacts are expected; ICA-based artifact removal recommended. Route condition (route A vs route B) may be available as a subject-level metadata label.

## Data Quality Notes

- Mobile EEG with significant motion artifacts from walking - ICA and motion artifact rejection required.
- No trial-level event markers in EEG files; button-press events may be in separate logs.
- 67-channel mobile EEG system; verify electrode positions.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.


> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003039