# EEG: Three armed bandit gambling task

**Dataset**: `openneuro_ds003458` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003458
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 23
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a three-armed bandit gambling task with oscillating reinforcement probabilities to investigate reward processing and reward prediction error signals in EEG. Each trial includes a stimulus presentation (choice between Left, Right, or Up options), a button-press response, and outcome feedback (Win, Loss, or Null). The Fixation event marks trial onset. STATUS is a BioSemi admin marker.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003458

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus (Left` | 138 (files) | short | raw | Stimulus onset with left option available |
| `Right` | 138 (files) | short | raw | Stimulus with right option available |
| `Up)` | 138 (files) | short | raw | Stimulus with up option available |
| `X` | 92 (files) | short | raw | Option marker X - decode from events.tsv |
| `Y` | 92 (files) | short | raw | Option marker Y - decode from events.tsv |
| `Z` | 92 (files) | short | raw | Option marker Z - decode from events.tsv |
| `Response` | 69 (files) | short | raw | Participant button-press choice response |
| `Fixation` | 23 (files) | short | raw | Trial-onset fixation cross |
| `Feedback Win` | 23 (files) | short | raw | Outcome: reward received |
| `Feedback Loss` | 23 (files) | short | raw | Outcome: no reward |
| `Feedback Null` | 13 (files) | short | raw | Outcome: null/neutral feedback |
| `STATUS` | 23 (files) | admin | raw | BioSemi system status marker - exclude |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus (Left`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Three Armed Bandit
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`Feedback Win`, `Feedback Loss`, `Feedback Null`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Feedback Win` | 0 | Win feedback (reward received) |
  | `Feedback Loss` | 1 | Loss feedback (no reward) |
  | `Feedback Null` | 2 | Null/neutral feedback |
- **Evidence**:
  - DOI: https://doi.org/10.18112/openneuro.ds003458.v1.1.0 — OpenNeuro metadata defines this as a three-armed bandit gambling task with feedback events
  - DOI: 10.1016/j.neuroimage.2015.02.007 — Related study uses feedback-locked analysis window 250-500 ms post-feedback in similar three-armed bandit paradigm (different dataset)
- **Kernel Notes**: Parameters estimated from paradigm literature; verify against events.tsv before implementation.

### Normal Task 1: Feedback Outcome Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is a BioSemi admin marker - excluded. Event label `Stimulus (Left` contains a parenthesis fragment - this is a truncated label; the full label may span `Stimulus (Left`, `Right`, `Up)`. Feedback events are the primary scientific targets for reward prediction error analysis. `Response` marks button-press choices.

| Event | y | Meaning |
 |-------|---|------|
 | `Feedback Win` | 0 | Win feedback (reward received) |
 | `Feedback Loss` | 1 | Loss feedback (no reward) |
 | `Feedback Null` | 2 | Null/neutral feedback |

## Data Quality Notes

- Event label `Stimulus (Left` is a truncated label fragment - verify full label from events.tsv.
- `STATUS` is BioSemi hardware marker - exclude from analysis.
- Small dataset: 23 subjects, 1 file each.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `EEG: Three armed bandit gambling task`
