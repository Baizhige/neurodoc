# Simultaneous EEG and fNIRS recordings for semantic decoding of imagined animals and tools

**Dataset**: `openneuro_ds004514` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004514
**Category**: High-level Mental | **Subjects**: 22 | **Files (Completed)**: 22 | **Channels**: 32 | **Sampling Rate**: 500 Hz

## Paradigm

Participants imagined animals and tools in response to visual cues while simultaneous EEG and fNIRS were recorded. Events encode the specific animal or tool category being imagined across four modalities: visual imagery, silent naming, auditory imagery, and drawing imagery. The study investigates cross-modal semantic representations of living vs non-living concepts.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004514

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `animal_visual_imagery_task` | ~22xN | long | raw | Visual imagery of animals |
| `tool_visual_imagery_task` | ~22xN | long | raw | Visual imagery of tools |
| `animal_silent_naming_task` | ~22xN | long | raw | Silent naming imagery of animals |
| `tool_silent_naming_task` | ~22xN | long | raw | Silent naming imagery of tools |
| `animal_auditory_imagery_task` | ~22xN | long | raw | Auditory imagery of animals |
| `tool_auditory_imagery_task` | ~22xN | long | raw | Auditory imagery of tools |
| `animal_drawing_imagery_task` | ~22xN | long | raw | Drawing imagery of animals |
| `tool_drawing_imagery_task` | ~22xN | long | raw | Drawing imagery of tools |
| `rest` | ~22xN | rest | raw | Rest period between imagery blocks |
| `animal_visual_image` | ~22xN | short | raw | Visual image of animal (cue) |
| `tool_visual_image` | ~22xN | short | raw | Visual image of tool (cue) |
| `audio_animal` | ~22xN | short | raw | Audio cue for animal |
| `audio_tool` | ~22xN | short | raw | Audio cue for tool |
| `written_animal` | ~22xN | short | raw | Written word cue for animal |
| `written_tool` | ~22xN | short | raw | Written word cue for tool |
| `animal_drawing` | ~22xN | short | raw | Drawing cue for animal |
| `tool_drawing` | ~22xN | short | raw | Drawing cue for tool |
| `animal_text_cue` | ~22xN | short | raw | Text cue for animal |
| `tool_text_cue` | ~22xN | short | raw | Text cue for tool |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Nirs
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004514 DOI: https://doi.org/10.18112/openneuro.ds004514.v1.1.2


### Primary Task 2: Publisher-defined BIDS task: Eeg
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004514 DOI: https://doi.org/10.18112/openneuro.ds004514.v1.1.2


### Normal Task 1: Animal vs Tool Semantic Decoding (binary, long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Imagery tasks are sustained (>=2 s) - use long_event epoching. rest events are resting periods between imagery blocks. Short cue events (visual_image, audio, written, drawing, text_cue) mark the onset stimulus, not the imagery period.

| Event | y | Meaning |
 |-------|---|------|
 | `animal_visual_imagery_task` | 0 | Animal imagery (any modality) |
 | `animal_silent_naming_task` | 0 | Animal imagery (any modality) |
 | `animal_auditory_imagery_task` | 0 | Animal imagery (any modality) |
 | `animal_drawing_imagery_task` | 0 | Animal imagery (any modality) |
 | `tool_visual_imagery_task` | 1 | Tool imagery (any modality) |
 | `tool_silent_naming_task` | 1 | Tool imagery (any modality) |
 | `tool_auditory_imagery_task` | 1 | Tool imagery (any modality) |
 | `tool_drawing_imagery_task` | 1 | Tool imagery (any modality) |
## Data Quality Notes

- Simultaneous EEG and fNIRS; only EEG channels used here
- 32 EEG channels (lower density than typical 64-ch systems)
- 4 imagery modalities x 2 categories = 8 sustained imagery conditions

## References

- **Reference**: `Simultaneous EEG and fNIRS recordings for semantic decoding of imagined animals and tools`
