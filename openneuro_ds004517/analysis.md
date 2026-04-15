# EEG recordings for semantic decoding of imagined animals and tools during auditory imagery task

**Dataset**: `openneuro_ds004517` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004517
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 32 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants imagined animals and tools in response to auditory cues while EEG was recorded. Each trial consisted of an audio cue followed by a sustained auditory imagery period (~5 s). The study investigates EEG correlates of semantic imagery for living (animals) vs non-living (tools) concepts in the auditory domain.

## File Scan Result

> **Kernel SHA256**: `3de7ce8fbacbf61a7bcd8b46a4e88f13102a3d33be83e15c1038cccf2cdc905a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_4223` | 6 | event | raw | Boundary/admin marker (rest or session transition) |
| `event_4351` | 11872 | event | raw | Sustained auditory imagery task marker (animal/tool condition) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Animal vs Tool Auditory Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `event_4351` | 0 | Auditory imagery of animals (living concepts) |
| `event_4351` | 1 | Auditory imagery of tools (non-living concepts) |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-04967-0 (Simultaneous EEG and fNIRS recordings for semantic decoding of imagined animals and tools)
- **Kernel Notes**: The sustained imagery periods (~5 s) are ideal for long_event epoching. Event_4351 (11872 occurrences) aligns with expected trial count (~20 trials × 20 subjects). Actual event labels require verification against raw BIDS events.tsv to confirm animal/tool condition mapping; interim mapping based on analysis.md descriptions. Event_4223 (6 occurrences) represents rare boundary/admin markers not used for primary epoching.

### Classical Task 2: Audio Cue Onset ERP Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, overlap = null
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|----|--------|
| `event_4351` | 0 | Auditory cue onset for animal imagery |
| `event_4351` | 1 | Auditory cue onset for tool imagery |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-04967-0
- **Kernel Notes**: Short audio cue onsets captured for ERP analysis. tmin=-0.5s allows baseline correction; tmax=1.0s captures brief cue presentation period. Condition labels derived from analysis.md descriptions of audio_animal/audio_tool cue onsets.

### Normal Task 1: Rest vs Active Imagery State Segmentation
- **Task Type**: segmentation/classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 0.0 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|--------|
| `event_4351` | 1 | Active sustained imagery period |
| `event_4223` | 0 | Rest/boundary marker |

- **Evidence**: DOI: https://doi.org/10.1038/s41597-025-04967-0 (paradigm includes explicit rest periods between imagery blocks)
- **Kernel Notes**: Event_4223 (6 occurrences) represents rare boundary/rest markers. Verify per-subject event structure before epoching. This task supports alternative approaches to semantic classification by first segmenting active vs rest states.

### Potential Task 1: Semantic Decoding of Living vs Non-living Concepts
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 4.5 s, overlap = 0.25 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**: Event-to-label mapping for living (animal) vs non-living (tool) semantic categories
- **Evidence**: Paradigm described in DOI: https://doi.org/10.1038/s41597-025-04967-0
- **Kernel Notes**: This super-level task derives semantic labels from raw imagery conditions. Requires super meta integration to map raw events to semantic categories. Mid-to-late imagery window (0.5-4.5s) recommended for optimal semantic decoding based on sustained imagery dynamics.