# Simultaneous EEG and fNIRS recordings for semantic decoding of imagined animals and tools

**Dataset**: `openneuro_ds004514` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004514
**Category**: High-level Mental | **Subjects**: 22 | **Files (Completed)**: 22 | **Channels**: 32 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants imagined animals and tools in response to visual cues while simultaneous EEG and fNIRS were recorded. The study investigates cross-modal semantic representations of living vs non-living concepts using four imagery modalities: visual imagery, silent naming, auditory imagery, and drawing imagery. Mental imagery task epochs lasted approximately 3 seconds each.

## File Scan Result

> **Kernel SHA256**: `no_kernel`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `127.0` | 13 | event | raw | Numeric alias for event_127 |
| `255.0` | 28184 | event | raw | Numeric alias for event_255 |
| `event_127` | 13 | event | raw | Cue onset marker |
| `event_255` | 28184 | event | raw | Sustained imagery period (animal or tool concept) |
| `event_5` | 3 | event | raw | Alternate cue marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Animal vs Tool Semantic Decoding during Mental Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, overlap = 0.0, target_events = [`event_255`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_255` | ? | Sustained imagery period (animal or tool) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04967-0 — "This data descriptor paper describes simultaneous EEG and fNIRS recordings from 12 participants performing four mental tasks (silent naming, visual imagery, auditory imagery, tactile imagery) to distinguish between semantic categories of animals and tools, with mental task epochs lasting 3 seconds each."
- **Kernel Notes**: CRITICAL LIMITATION — Semantic event names (e.g., `animal_visual_imagery_task`, `tool_silent_naming_task`) described in the original paradigm and analysis.md are NOT present in the HDF5 data. Available events are numeric codes only: `event_255` (28,184 occurrences), `event_127` (13 occurrences), `event_5` (3 occurrences). Without an event code mapping document, condition-level labels (animal vs. tool, modality type) CANNOT be determined from numeric event IDs. Binary classification of semantic categories requires either: (1) original BIDS event code key to map `event_255` to condition-specific labels, or (2) manual curation of trial-level annotations from stimulus timing. The 3-second epoch window from DOI reference is confirmed but alignment must be verified. Recommend locating sidecar JSON or publication supplementary materials for event code translation.

### Potential Task 1: Cue-onset Event Detection
- **Task Type**: detection
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, overlap = 0.0, target_events = [`event_127`, `event_5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `event_127` | 0 | Cue onset marker (13 occurrences) |
  | `event_5` | 1 | Alternate cue type (3 occurrences) |
- **Evidence**:
  - Plausible from paradigm: Cues (visual images, audio, written words, drawings) precede imagery tasks per DOI methodology
- **Kernel Notes**: `event_127` (n=13) and `event_5` (n=3) likely represent cue-onset markers preceding sustained imagery periods. Low occurrence counts limit statistical power but support detecting neural responses to stimulus cue presentation. Semantic condition labels unknown without event code mapping.