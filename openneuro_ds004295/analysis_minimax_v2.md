# Reward gain and punishment avoidance reversal learning

**Dataset**: `openneuro_ds004295` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004295
**Category**: High-level Mental | **Subjects**: 26 | **Files (Completed)**: 26
**Channels**: 66 | **Sampling Rate**: 1024 Hz

## Paradigm

A reversal learning task comparing brain activity during reward gain (monetary) versus punishment avoidance (white noise) reinforcement. Participants learned stimulus-response associations that reversed mid-task, requiring cognitive flexibility. EEG was recorded to investigate feedback-related neural signatures under different reinforcement conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004295

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 81` | 26x~164 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 61` | 26x~162 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 75` | 26x~153 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 71` | 26x~148 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 52` | 26x~141 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 51` | 26x~139 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 55` | 26x~137 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 72` | 26x~132 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 60` | 26x~118 | short | raw | Stimulus trigger - decode from events.tsv |
| `S 80` | 26x~116 | short | raw | Stimulus trigger - decode from events.tsv |
| `S100` | 26x~1 | short | raw | Sample stimulus (first in pair) |
| `S200` | 26x~1 | short | raw | Probe stimulus (second in pair) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 81`, `S 61`, `S 75`, `S 71`, `S 52`, `S 51`, `S 55`, `S 72`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Feedback Valence Classification (Reward Gain vs Punishment Avoidance)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.0 s, target_events = [`S 52`, `S 51`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 52` | 0 | Positive feedback (reward gain / punishment avoidance success) |
  | `S 51` | 1 | Negative feedback (reward loss / punishment failure) |
- **Super Meta Notes**: N/A
- **Evidence**:
  - DOI: 10.1111/psyp.14235 — Single-trial regression with feedback valence as predictor examining frontal midline theta (FMθ) responses to positive vs negative feedback in reward and punishment reversal learning tasks.
- **Kernel Notes**: Verify event ID mapping from events.tsv. The paper uses feedback valence (positive vs negative) as the classification target. Based on dataset event structure patterns, S 52 is inferred as positive feedback and S 51 as negative feedback. Kernel should cross-validate against stimulus events (S 71, S 72, S 75, S 80, S 81) to confirm timing and correct mapping. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Reversal Learning Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Specific kernel required to decode BrainVision trigger codes (S 51-S 81 range) to semantic labels. Regression target: response_time from misc channels.

| Event | y | Meaning |
|-------|---|------|
| `stimulus_A_prereversalReward` | 0 | Stimulus A before reversal (reward condition) |
| `stimulus_B_prereversalPunishment` | 1 | Stimulus B before reversal (punishment condition) |
| `correct_response` | 2 | Correct response |
| `incorrect_response` | 3 | Incorrect response |
| `reversal_cue` | 4 | Reversal signal |
| `stimulus_A_postreversalPunishment` | 5 | Stimulus A after reversal (punishment condition) |
| `feedback_positive` | 6 | Positive feedback |
| `feedback_negative` | 7 | Negative feedback |


## Data Quality Notes

- BrainVision trigger codes (S 51-S 81 range) require kernel-level decoding to semantic labels
- S150/S151 appear in only 22 subjects, possibly a separate task block

## References

- **Reference**: `Reward gain and punishment avoidance reversal learning`
