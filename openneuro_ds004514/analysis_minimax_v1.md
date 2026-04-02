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

### Primary Task 1: Binary Semantic Decoding of Animal vs Tool Categories
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s *, overlap = 0.0 *, target_events = [`animal_silent_naming_task`, `tool_silent_naming_task`, `animal_visual_imagery_task`, `tool_visual_imagery_task`, `animal_auditory_imagery_task`, `tool_auditory_imagery_task`, `animal_drawing_imagery_task`, `tool_drawing_imagery_task`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `animal_silent_naming_task` | 0 | Animal mental imagery |
  | `animal_visual_imagery_task` | 0 | Animal mental imagery |
  | `animal_auditory_imagery_task` | 0 | Animal mental imagery |
  | `animal_drawing_imagery_task` | 0 | Animal mental imagery |
  | `tool_silent_naming_task` | 1 | Tool mental imagery |
  | `tool_visual_imagery_task` | 1 | Tool mental imagery |
  | `tool_auditory_imagery_task` | 1 | Tool mental imagery |
  | `tool_drawing_imagery_task` | 1 | Tool mental imagery |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04967-0 — This data descriptor paper describes simultaneous EEG and fNIRS recordings from participants performing four mental tasks (silent naming, visual imagery, auditory imagery, tactile/drawing imagery) to distinguish between semantic categories of animals and tools, with mental task epochs lasting 3 seconds each.
- **Kernel Notes**: Binary classification labels derived directly from BIDS event marker names by parsing animal vs tool category. Use long_event epoching (tmin=0.0s, tmax=3.0s) to capture the sustained mental imagery period. Note: Dataset 2 uses 5s epochs - consider separate training runs or metadata-aware kernel.

### Primary Task 2: Multi-class Mental Imagery Modality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s *, overlap = 0.0 *, target_events = [`animal_silent_naming_task`, `tool_silent_naming_task`, `animal_visual_imagery_task`, `tool_visual_imagery_task`, `animal_auditory_imagery_task`, `tool_auditory_imagery_task`, `animal_drawing_imagery_task`, `tool_drawing_imagery_task`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `animal_silent_naming_task` | 0 | Animal silent naming |
  | `tool_silent_naming_task` | 1 | Tool silent naming |
  | `animal_visual_imagery_task` | 2 | Animal visual imagery |
  | `tool_visual_imagery_task` | 3 | Tool visual imagery |
  | `animal_auditory_imagery_task` | 4 | Animal auditory imagery |
  | `tool_auditory_imagery_task` | 5 | Tool auditory imagery |
  | `animal_drawing_imagery_task` | 6 | Animal drawing imagery |
  | `tool_drawing_imagery_task` | 7 | Tool drawing imagery |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04967-0 — This paper describes four mental tasks (silent naming, visual imagery, auditory imagery, drawing imagery) across two semantic categories, enabling 8-class classification of both category and modality.
- **Kernel Notes**: Multi-class classification combining semantic category and imagery modality. Labels embedded in event names - parse both animal/tool and imagery type. Dataset has 4 modalities x 2 categories = 8 conditions.

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
