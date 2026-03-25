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

### Primary Task 1: Correct vs Incorrect Response Classification (Simon Conflict)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 5.0 s, target_events = [`correct`, `incorrect`, `Trn Stim`, `Test Stim`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `correct` | 1 | Correct response |
  | `incorrect` | 0 | Error/incorrect response |
- **Evidence**:
  - DOI: 10.1038/ncomms6394 — This 2014 Nature Communications paper presents the original study (Study I: N=83; Study II: N=27) demonstrating that response conflict acts as an implicit cost in reinforcement learning, using a modified Simon task with EEG recordings (64-channel, 500 Hz) during training and test phases to examine how conflict diminishes reward value and enhances punishment aversion, with EEG analysis focusing on frontal midline theta (4-8 Hz) to conflict and feedback events.
- **Kernel Notes**: Epoch around stimulus onset (Trn Stim/Test Stim) from -1500 to +5000 ms; baseline correction using -300 to -200 ms pre-cue; filter ERP data 0.5-20 Hz; classify response outcomes (correct=1, incorrect=0). Drug condition (cabergoline vs placebo) available in participants.tsv as covariate.

### Primary Task 2: Conflict Cost Bias Classification (B > C vs C > B)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 5.0 s, target_events = [`Test Stim`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | B>C preference | 1 | Prefer option B over C (reward-based learning) |
  | C>B preference | 0 | Prefer option C over B (punishment-based learning) |
- **Super Meta Notes**: Conflict cost bias is derived from test phase forced-choice behavior (which option subjects chose when given B vs C choices). B>C indicates learning from rewards; C>B indicates learning from punishment avoidance. Requires aggregating response data per subject to compute preference scores.
- **Evidence**:
  - DOI: 10.1038/ncomms6394 — The study examines how response conflict during a Simon task modulates reinforcement learning, with the conflict cost contrast (B>C vs C>B) as a continuous bias measure predicting EEG theta dynamics during feedback processing.
- **Kernel Notes**: First compute per-subject preference scores from test phase choice data; derive binary label (B>C=1, C>B=0); epoch test phase stimuli; analyze feedback-locked theta (200-500 ms post-feedback) in 4-8 Hz band.

### Normal Task 1: Correct/Incorrect Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Correct and incorrect counts are closely balanced (~548 vs ~547 total). Largest dataset in the Simon-conflict series; includes drug condition variation (cabergoline vs placebo) - consider as a covariate.

| Event | y | Meaning |
 |-------|---|------|
| `correct` | 1 | Correct response |
| `incorrect` | 0 | Error response |

## Data Quality Notes

- 64-channel EEG with 110 subjects across cabergoline and placebo conditions.
- Drug condition information in participants.tsv; use as a grouping variable for stratified analysis.
- Some subjects may have two sessions; verify file-to-subject mapping.

## References

- **Reference**: `Conflict acts as an implicit cost in reinforcement learning. Nature Communications, 2014. DOI: 10.1038/ncomms6394`
