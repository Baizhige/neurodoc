# EEG: Probabilistic Learning with Affective Feedback: Exp #2

**Dataset**: `openneuro_ds003753` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003753
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task involving probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to affective stimulus properties. Participants made binary choices (left/right button) between cue stimuli (CUE) associated with positive or negative affective feedback images. Following each choice, an affective feedback image (FB) was presented. The study examines whether the RewP tracks reward value beyond mere monetary reward, responding to affective liking of feedback stimuli.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003753

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | 100 | short | raw | Cue stimulus requiring binary choice |
| `FB` | 100 | short | raw | Affective feedback stimulus (liked/disliked image) |
| `Left Button` | 25 | short | raw | Left button press response |
| `Right Button` | 25 | short | raw | Right button press response |
| `STATUS` | 25 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Affective Feedback Valence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`FB (liked/rewarding)`, `FB (disliked/non-rewarding)`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `FB (liked/rewarding)` | 1 | Liked affective feedback (puppy images, positive outcome) |
  | `FB (disliked/non-rewarding)` | 0 | Disliked affective feedback (chair/negative images, negative outcome) |
- **Super Meta Notes**: Labels derived from events.tsv `trial_type` column - liked/disliked affective value decoded from IAPS picture categories (puppy=liked, chair/negative=disliked). Baseline correction applied -200 to 0 ms before feedback onset. RewP ERP quantified as mean amplitude 200-350ms at Cz for reward vs punishment conditions.
- **Evidence**:
  - DOI: 10.3758/s13415.021.00950-5 — This paper analyzes EEG data from 25 participants performing a reinforcement learning task with probabilistic affective feedback (puppy vs chair images, points), examining how the Reward Positivity (RewP) ERP component tracks hedonic liking of feedback stimuli.
- **Kernel Notes**: Must decode FB event subtypes from events.tsv trial_type column. Epoch window is −1.0 to 3.0 s relative to feedback onset per paper methodology. Baseline correct using −200 to 0 ms pre-feedback.

### Normal Task 1: Feedback type classification (requires decoding FB subtypes from events.tsv)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: FB event subtypes (liked vs disliked) must be decoded from events.tsv `trial_type` column. 25 subjects only; small dataset. Sister dataset to ds003822 (Exp #1).

| Event | y | Meaning |
 |-------|---|------|
| `FB` (liked/rewarding) | 1 | Liked emotional feedback (needs to be decoded from events.tsv) |
| `FB` (disliked/non-rewarding) | 0 | Disliked emotional feedback (needs to be decoded from events.tsv) |

## Data Quality Notes

- Small dataset (25 subjects, 25 files).
- FB event subtype labels (affective value) must be decoded from events.tsv metadata.
- STATUS is a single admin marker per file; exclude from epoching.

## References

- **Reference**: `The Reward Positivity is sensitive to affective liking. OpenNeuro ds003753.`
