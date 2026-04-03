# EEG: RL Task (3-Armed Bandit) with Alcohol Cues in Hazardous Drinkers

**Dataset**: `openneuro_ds004595` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004595
**Category**: High-level Mental | **Subjects**: 53 | **Files (Completed)**: 53 | **Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Participants completed a reinforcement learning task using a 3-armed bandit paradigm incorporating alcohol-related and neutral beverage cues to study decision-making in hazardous drinkers versus controls. On each trial, a cue was presented followed by a three-arm choice and probabilistic win/loss feedback. The study examines electrophysiological markers of cue-driven exploration and aberrant reinforcement learning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_kernel_update
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004595

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Fixation` | 18550 | short | raw | Fixation cross onset (trial start) |
| `FB: Win` | 9713 | short | raw | Win feedback delivered |
| `FB: Loss` | 7254 | short | raw | Loss feedback delivered |
| `Left Button` | 6276 | short | raw | Left arm choice response |
| `Up Button` | 6188 | short | raw | Up arm choice response |
| `Right Button` | 5553 | short | raw | Right arm choice response |
| `STATUS` | 4271 | admin | raw | System status marker (exclude) |
| `CUE: 123` | 2955 | short | raw | Cue onset - arm order permutation 1-2-3 |
| `CUE: 231` | 2934 | short | raw | Cue onset - arm order permutation 2-3-1 |
| `CUE: 132` | 2931 | short | raw | Cue onset - arm order permutation 1-3-2 |
| `CUE: 321` | 2919 | short | raw | Cue onset - arm order permutation 3-2-1 |
| `CUE: 312` | 2908 | short | raw | Cue onset - arm order permutation 3-1-2 |
| `CUE: 213` | 2853 | short | raw | Cue onset - arm order permutation 2-1-3 |
| `No Response` | 533 | admin | raw | No-response trial (exclude) |
| `FB: No Resp` | 533 | admin | raw | No-response feedback (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Explore/Exploit Decision-Making Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`CUE: 123`, `CUE: 231`, `CUE: 132`, `CUE: 321`, `CUE: 312`, `CUE: 213`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `CUE: 123` | 0 | Alcohol cue - arm order 1-2-3 * |
  | `CUE: 231` | 0 | Alcohol cue - arm order 2-3-1 * |
  | `CUE: 132` | 0 | Alcohol cue - arm order 1-3-2 * |
  | `CUE: 321` | 0 | Alcohol cue - arm order 3-2-1 * |
  | `CUE: 312` | 0 | Alcohol cue - arm order 3-1-2 * |
  | `CUE: 213` | 0 | Alcohol cue - arm order 2-1-3 * |
- **Kernel Notes**: Verify cue-to-substance mapping (alcohol vs neutral) from events.tsv. CUE events encode arm-order permutations; aggregate all CUE events as 'novel cue' class for cue-elicited ERP analysis (P3a/P3b). (replaces Primary Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "This study recorded EEG during a three-armed bandit task with alcohol and non-alcohol novel cues, epoched data from -500 to 1000ms, and used P3a/P3b amplitudes and POMDP model parameters (BONUS, IEV) to predict exploratory vs exploitative choice behavior in hazardous drinkers versus controls."

### Primary Task 2: Feedback Valence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`FB: Win`, `FB: Loss`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB: Win` | 0 | Win feedback |
  | `FB: Loss` | 1 | Loss feedback |
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — Paper confirms feedback processing is part of the RL task; standard FB epoch params used for reward/feedback ERPs (N200, P300).
- **Kernel Notes**: Epoch on FB events for reward prediction error analysis. Exclude `FB: No Resp` from training.

### Normal Task 1: Feedback Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS, No Response, and FB: No Resp are admin - exclude. CUE events encode arm-order permutations; aggregate to generic CUE if order-agnostic analysis desired.

 | Event | y | Meaning |
 |-------|---|---------|
 | `FB: Win` | 0 | Win feedback |
 | `FB: Loss` | 1 | Loss feedback |

## Data Quality Notes

- STATUS markers must be excluded from training.
- CUE events encode arm order permutations - group to single CUE class if order irrelevant.

