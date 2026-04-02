# EEG: Simon Conflict with Reinforcement + Cabergoline Challenge

**Dataset**: `openneuro_ds003518` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003518
**Category**: High-level Mental | **Subjects**: 110 | **Files (Completed)**: 137
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

This study examines whether conflict acts as an implicit cost in reinforcement learning using a modified Simon task with pharmacological manipulation. Healthy participants performed a Simon conflict task across training and test phases, with a double-blind Cabergoline (dopamine D2/D3 agonist) challenge administered to examine dopaminergic modulation. The training phase included reinforcement feedback to shape behavior; the test phase probed learned conflict avoidance. Mid-frontal theta and error-related negativity are key EEG measures.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003518

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Trn Stim` | 2192 | short | raw | Training phase stimulus (congruent/incongruent Simon) |
| `Test Stim` | 1644 | short | raw | Test phase stimulus |
| `correct` | 548 | short | raw | Correct response outcome |
| `incorrect` | 547 | short | raw | Incorrect response / error outcome |
| `Trn Resp` | 547 | short | raw | Training phase button-press response |
| `Test Resp` | 548 | short | raw | Test phase button-press response |
| `FB` | 274 | short | raw | Feedback stimulus in training phase |
| `Trn No Response` | 136 | short | raw | Missing response in training phase |
| `Test No Response` | 55 | short | raw | Missing response in test phase |
| `STATUS` | 137 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Trn Stim`, `Test Stim`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Correct/Incorrect Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`correct`, `incorrect`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `incorrect` | 0 | Error response |
  | `correct` | 1 | Correct response |
- **Evidence**:
  - DOI: `10.1038/ncomms6394` — EEG analysis of Simon conflict task to examine how response conflict modulates reinforcement learning; epochs analyzed from -500 to +1000 ms relative to stimulus events; correct vs incorrect classification used to examine frontal theta dynamics predicting choice behavior.
- **Kernel Notes**: Epochs extracted around `Trn Stim` and `Test Stim` events using the cue epoch window (-1500 to +5000 ms) from the original study, with analysis focused on the peri-response window (-500 to +1000 ms). Labels derived from `correct` and `incorrect` outcome events. (replaces Normal Task 1 from original analysis.md)


## Data Quality Notes

- 64-channel EEG with 110 subjects across cabergoline and placebo conditions.
- Drug condition information in participants.tsv; use as a grouping variable for stratified analysis.
- Some subjects may have two sessions; verify file-to-subject mapping.

## References

- **Reference**: `Conflict acts as an implicit cost in reinforcement learning. Nature Communications, 2014. DOI: 10.1038/ncomms6394`
