# EEG recordings for semantic decoding of imagined animals and tools during auditory imagery task

**Dataset**: `openneuro_ds004517` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004517
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 32 | **Sampling Rate**: 500 Hz

## Paradigm

Participants imagined animals and tools in response to auditory cues while EEG was recorded. Each trial consisted of an audio cue followed by a sustained auditory imagery period (~5 s). The study investigates EEG correlates of semantic imagery for living (animals) vs non-living (tools) concepts in the auditory domain.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004517

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `animal_auditory_imagery_task` | ~20xN | long | raw | Sustained auditory imagery of animals |
| `tool_auditory_imagery_task` | ~20xN | long | raw | Sustained auditory imagery of tools |
| `audio_animal` | ~20xN | short | raw | Auditory cue onset for animal |
| `audio_tool` | ~20xN | short | raw | Auditory cue onset for tool |
| `rest` | ~20xN | rest | raw | Rest period between imagery blocks |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Eeg
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004517 DOI: https://doi.org/10.18112/openneuro.ds004517.v1.0.2


### Normal Task 1: Animal vs Tool Auditory Imagery (binary, long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Imagery tasks are sustained (~5 s) - use long_event epoching. audio_animal/audio_tool are short cue onsets; rest events are inter-block resting periods.

| Event | y | Meaning |
 |-------|---|------|
 | `animal_auditory_imagery_task` | 0 | Auditory imagery of animals |
 | `tool_auditory_imagery_task` | 1 | Auditory imagery of tools |
## Data Quality Notes

- 32 EEG channels
- Sustained imagery periods (~5 s) are suitable for long_event epoching
- 20 subjects with balanced animal/tool imagery conditions

## References

- **Reference**: `EEG recordings for semantic decoding of imagined animals and tools during auditory imagery task`
