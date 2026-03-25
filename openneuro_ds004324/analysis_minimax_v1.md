# ToonFaces

**Dataset**: `openneuro_ds004324` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004324
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26
**Channels**: 38 | **Sampling Rate**: 500 Hz

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of three types of face images - real photographs (img), stylized toon faces (toon), and schematic stick-figure faces (sf) - each shown at different emotional intensity levels (0-4). Subjects evaluated emotion detection and affective states, allowing ERP-based comparison across face types and intensity levels.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004324

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `img/0` | 26x45 | short | raw | Real face image, intensity 0 (neutral) |
| `img/1` | 26x195 | short | raw | Real face image, intensity 1 |
| `img/2` | 26x15 | short | raw | Real face image, intensity 2 |
| `img/3` | 26x15 | short | raw | Real face image, intensity 3 |
| `img/4` | 26x30 | short | raw | Real face image, intensity 4 (most intense) |
| `toon/0` | 26x45 | short | raw | Toon face, intensity 0 (neutral) |
| `toon/1` | 26x195 | short | raw | Toon face, intensity 1 |
| `toon/2` | 26x15 | short | raw | Toon face, intensity 2 |
| `toon/3` | 26x15 | short | raw | Toon face, intensity 3 |
| `toon/4` | 26x30 | short | raw | Toon face, intensity 4 |
| `sf/0` | 26x45 | short | raw | Schematic face, intensity 0 (neutral) |
| `sf/1` | 26x195 | short | raw | Schematic face, intensity 1 |
| `sf/2` | 26x15 | short | raw | Schematic face, intensity 2 |
| `sf/3` | 26x15 | short | raw | Schematic face, intensity 3 |
| `sf/4` | 26x30 | short | raw | Schematic face, intensity 4 |
| `BlockEnd` | 26x3 | admin | raw | End of block marker |
| `block1` | 26 | admin | raw | Block 1 start marker |
| `block2` | 26 | admin | raw | Block 2 start marker |
| `block3` | 26 | admin | raw | Block 3 start marker |
| `Intro` | 22 | admin | raw | Introduction screen marker |
| `Instructions1` | 25 | admin | raw | Instructions screen 1 |
| `Instructions2` | 25 | admin | raw | Instructions screen 2 |
| `Instructions3` | 25 | admin | raw | Instructions screen 3 |
| `PracticeInstructions` | 25 | admin | raw | Practice instructions marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Face Type Classification (RSVP ERP)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`img/0`, `img/1`, `img/2`, `img/3`, `img/4`, `toon/0`, `toon/1`, `toon/2`, `toon/3`, `toon/4`, `sf/0`, `sf/1`, `sf/2`, `sf/3`, `sf/4`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `img/0`...`img/4` | 0 | Real photograph face (IMG) |
  | `toon/0`...`toon/4` | 1 | Stylized toon face (TOON) |
  | `sf/0`...`sf/4` | 2 | Schematic stick-figure face (SF) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2023.1160800 — Uses RSVP paradigm with three face categories (IMG, TOON, SF) and analyzes EEG ERP features (N170, LCP, differential entropy) for emotion detection; epoch parameters tmin=-0.2s, tmax=0.8s with -200ms baseline correction
- **Kernel Notes**: Apply baseline correction from -200ms to 0ms. Exclude block markers (block1/2/3, BlockEnd) and instruction markers from epoching. The intensity levels (0-4) can be used for secondary analysis but are not part of the primary three-class classification.

### Normal Task 1: Face Type Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Block markers (block1/2/3, BlockEnd) and instruction markers are admin events - exclude from target_events. Intensity sub-levels can be used for finer-grained multiclass analysis.

| Event | y | Meaning |
 |-------|---|------|
 | `img/0`...`img/4` | 0 | Real photograph face |
 | `toon/0`...`toon/4` | 1 | Stylized toon face |
 | `sf/0`...`sf/4` | 2 | Schematic stick-figure face |

## Data Quality Notes

- Block/instruction markers must be excluded from epoching
- Unequal counts across intensity levels (intensity 1: 195 vs intensity 2/3: 15 per face type)
- 26 subjects; consistent event structure across subjects

## References

- **Reference**: `Images of stylized faces improve ERP features used for emotion detection`
