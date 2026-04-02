# A high-quality EEG dataset for studying visual touch perception

**Dataset**: `openneuro_ds005662` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005662
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 65 | **Sampling Rate**: 2048 Hz

## Paradigm

Participants viewed rapid streams of videos depicting touch to a hand or an object to investigate visual touch perception. The experiment used target and non-target trials to measure brain responses to observed touch. No event markers are present in the BIDS metadata; the EEG is stored as continuous recordings requiring segmentation for downstream analysis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005662

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations in events.tsv._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Visual Touch Perception - Perspective Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`no_events`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `no_events` | 0 | self-perspective touch video |
  | `no_events` | 1 | other-perspective touch video |
- **Super Meta Notes**: Derived from video metadata (perspective field). Labels: self (0) vs other (1) perspective. Kernel step: Read video file names/metadata to extract perspective label for each trial epoch; `no_events` serves as placeholder since stimulus onset events exist in data but not exported to events.tsv. Verify event ID mapping from events.tsv or derive from data.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — MVPA decoding of self vs other perspective from EEG epochs time-locked to stimulus onset
  - DOI: 10.1038/s41597-026-06714-5 — Validation dataset for visual touch perception, perspective classification
- **Kernel Notes**: (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Visual Touch Perception - Material Classification (8 categories)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`no_events`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `no_events` | 0-7 | 8 material categories (wood, plastic, glass, metal, fabric, rubber, ceramic, other) |
- **Super Meta Notes**: Derived from video metadata (material field). Kernel step: Read video file names/metadata to extract material category label for each trial epoch. Verify event ID mapping from events.tsv or derive from data.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — MVPA decoding of 8 material categories from EEG epochs
  - DOI: 10.1038/s41597-026-06714-5 — Multi-class material classification using MVPA

### Primary Task 3: Visual Touch Perception - Hand Orientation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`no_events`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `no_events` | 0 | left hand, self-perspective |
  | `no_events` | 1 | right hand, self-perspective |
  | `no_events` | 2 | left hand, other-perspective |
  | `no_events` | 3 | right hand, other-perspective |
- **Super Meta Notes**: Derived from video metadata (hand_orientation field combining hand laterality + perspective). Kernel step: Read video file names/metadata to extract hand orientation label (4 categories). Verify event ID mapping from events.tsv.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — Decoding hand orientation (left/right hand, self/other perspective)
  - DOI: 10.1038/s41597-026-06714-5 — Hand orientation 4-class classification

### Primary Task 4: Visual Touch Perception - Valence Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`no_events`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `no_events` | continuous | valence rating (negative to positive scale from Validated Touch-Video Database) |
- **Super Meta Notes**: Derived from video metadata (valence field). Kernel step: Read valence ratings from validated database metadata for each video; regress from EEG epochs. Verify event ID mapping from events.tsv.
- **Evidence**:
  - DOI: 10.1101/2025.07.10.664069 — Valence regression from EEG epochs
  - DOI: 10.1038/s41597-026-06714-5 — Continuous valence prediction

### Normal Task 1: Continuous Segmentation (resting)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no events))
- **Notes**: No trial-level events found in events.tsv. Treat as continuous EEG; sliding window segmentation only.

## Data Quality Notes

- No event markers available - cannot perform event-locked epoching without additional annotation files.
- High sampling rate (2048 Hz); downsample to 500 Hz before processing.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to segmentation.

