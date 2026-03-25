# EEG: Probabilistic Learning with Affective Feedback: Exp #1

**Dataset**: `openneuro_ds003822` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003822
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task using probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to subjective reward value. Participants made binary choices (left/right button) between cue stimuli (CUE) associated with liked or disliked affective feedback images. Following each choice, a feedback cue (FB cue) predicted the affective image, then the full feedback (FB type) was presented. This is Experiment 1 in a two-experiment series (see ds003753 for Exp #2).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003822

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | 100 | short | raw | Cue stimulus requiring binary choice |
| `FB cue` | 100 | short | raw | Feedback cue (predicts upcoming affective image) |
| `FB type` | 200 | short | raw | Full affective feedback stimulus (liked/disliked) |
| `Response Accurate` | 25 | short | raw | Accurate/correct response marker |
| `Response Inaccurate` | 25 | short | raw | Inaccurate/incorrect response marker |
| `Left Button` | 25 | short | raw | Left button press |
| `Right Button` | 25 | short | raw | Right button press |
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

### Primary Task 1: Reward Valence Classification (Reward vs Punishment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`FB cue`, `FB type`, `CUE`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `puppy` (win/picture reward) | 1 | Rewarded condition (liked picture) |
  | `green_+1` (win/point reward) | 1 | Rewarded condition (point feedback) |
  | `chair` (avoid/negative) | 0 | Punished condition (disliked picture) |
  | `negative_image` | 0 | Punished condition (disliked picture) |
  | `yellow_bar` | 0 | Punished condition (point feedback) |
  | `red_-1` | 0 | Punished condition (point feedback) |
- **Evidence**:
  - DOI: 10.3758/s13415.021.00950-5 — Epochs data from -1000 to 3000 ms around outcome cue onset to classify reward (win) vs punishment (avoid) conditions using the Reward Positivity (RewP) ERP at Cz (200-350 ms window).
  - DOI: 10.3758/s13415-021-00950-5 — Uses binary valence labels derived from experimental conditions (reward vs punishment) combined with raw event markers for classification.
- **Kernel Notes**: Baseline correct using -200 to 0 ms pre-stimulus; extract RewP amplitude from Cz electrode in 200-350 ms window; map event labels to binary valence labels (reward=1, punishment=0).

### Primary Task 2: Affective Liking Classification (Liked vs Disliked Feedback Images)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`FB cue`, `FB type`, `CUE`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `puppy`, `cloud`, `sun` (liked pictures) | 1 | Liked affective feedback images |
  | `chair` (disliked picture) | 0 | Disliked affective feedback image |
- **Super Meta Notes**: Labels derived from experimental conditions (PICTURE TYPE: picture vs point) combined with raw event markers; pleasantness ratings from pre-task image rating (1-9 scale) used to validate liked/disliked categorization.
- **Evidence**:
  - DOI: 10.3758/s13415.021.00950-5 — Examines whether hedonic appraisal of picture vs point rewards modulates reward-related brain responses, classifying liked (pictures) vs disliked feedback.
  - DOI: 10.3758/s13415-021-00950-5 — Uses pleasantness ratings from pre-task image rating to derive affective liking labels for classification.
- **Kernel Notes**: Baseline correct using -200 to 0 ms; extract ERP features from Cz in 200-350 ms window; derive liked/disliked labels from experimental condition codes combined with pleasantness rating metadata.

### Normal Task 1: Feedback type classification (binary, subtype needs to be decoded from events.tsv)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `FB type` appears 200 times (2x more than CUE/FB cue = 100 each) suggesting FB type encodes both the feedback onset and a second event (e.g., image offset or rating). Decode subtype from events.tsv `trial_type` column. Sister dataset to ds003753 (Exp #2). 25 subjects only.

| Event | y | Meaning |
 |-------|---|------|
| `FB type` (liked/rewarding) | 1 | Liked emotional feedback (needs to decode subtype from events.tsv) |
| `FB type` (disliked/non-rewarding) | 0 | Disliked emotional feedback |

## Data Quality Notes

- Small dataset (25 subjects, 25 files).
- `FB type` count (200) is 2x `CUE` count (100); likely encodes two event variants per trial; verify from events.tsv.
- `Response Accurate` and `Response Inaccurate` appear only 25 times each (once per file summary count); likely one per session.
- STATUS is a single admin marker per file; exclude from epoching.

## References

- **Reference**: `The Reward Positivity is sensitive to affective liking. OpenNeuro ds003822.`
