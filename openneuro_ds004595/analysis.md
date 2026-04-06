# EEG: RL Task (3-Armed Bandit) with Alcohol Cues in Hazardous Drinkers

**Dataset**: `openneuro_ds004595` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004595
**Category**: High-level Mental | **Subjects**: 53 | **Files (Completed)**: 53 | **Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Participants completed a reinforcement learning task using a 3-armed bandit paradigm incorporating alcohol-related and neutral beverage cues to study decision-making in hazardous drinkers versus controls. On each trial, a cue was presented followed by a three-arm choice and probabilistic win/loss feedback. The study examines electrophysiological markers of cue-driven exploration and aberrant reinforcement learning.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 53
- **Age Completeness**: 53/53 (100.0%)
- **Sex Completeness**: 53/53 (100.0%)
- **Observed Age Examples**: `43`, `50`, `22`, `18`, `31`, `24`, `44`, `38`
- **Observed Sex Examples**: `Female`, `Male`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds004595.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `5f3b4f5781dd101d4833f6050cadb1f9dfce50ba24026e4900e1754d42e5ae13`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 18550 | event | raw | Unresolved from current kernel facts |
| `S201` | 9713 | event | raw | Unresolved from current kernel facts |
| `S200` | 7254 | event | raw | Unresolved from current kernel facts |
| `S  3` | 6276 | event | raw | Unresolved from current kernel facts |
| `S  4` | 6188 | event | raw | Unresolved from current kernel facts |
| `S  2` | 5553 | event | raw | Unresolved from current kernel facts |
| `S101` | 2955 | event | raw | Unresolved from current kernel facts |
| `S104` | 2934 | event | raw | Unresolved from current kernel facts |
| `S102` | 2931 | event | raw | Unresolved from current kernel facts |
| `S106` | 2919 | event | raw | Unresolved from current kernel facts |
| `S105` | 2908 | event | raw | Unresolved from current kernel facts |
| `S103` | 2853 | event | raw | Unresolved from current kernel facts |
| `R  6` | 1068 | event | raw | Unresolved from current kernel facts |
| `R 12` | 1050 | event | raw | Unresolved from current kernel facts |
| `S  9` | 726 | event | raw | Unresolved from current kernel facts |
| `S  8` | 667 | event | raw | Unresolved from current kernel facts |
| `S 99` | 533 | event | raw | Unresolved from current kernel facts |
| `S199` | 533 | event | raw | Unresolved from current kernel facts |
| `S  7` | 194 | event | raw | Unresolved from current kernel facts |
| `S  6` | 181 | event | raw | Unresolved from current kernel facts |
| `S 10` | 173 | event | raw | Unresolved from current kernel facts |
| `S  5` | 159 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Explore/Exploit Decision-Making Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`CUE: 123`, `CUE: 231`, `CUE: 132`, `CUE: 321`, `CUE: 312`, `CUE: 213`]
- **Label Route**: `event`
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
- **Kernel Notes**: Verify cue-to-substance mapping (alcohol vs neutral) from events.tsv. CUE events encode arm-order permutations; aggregate all CUE events as 'novel cue' class for cue-elicited ERP analysis (P3a/P3b). (replaces Classical Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — "This study recorded EEG during a three-armed bandit task with alcohol and non-alcohol novel cues, epoched data from -500 to 1000ms, and used P3a/P3b amplitudes and POMDP model parameters (BONUS, IEV) to predict exploratory vs exploitative choice behavior in hazardous drinkers versus controls."

### Classical Task 2: Feedback Valence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`FB: Win`, `FB: Loss`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB: Win` | 0 | Win feedback |
  | `FB: Loss` | 1 | Loss feedback |
- **Evidence**:
  - DOI: 10.5334/cpsy.96 — Paper confirms feedback processing is part of the RL task; standard FB epoch params used for reward/feedback ERPs (N200, P300).
- **Kernel Notes**: Epoch on FB events for reward prediction error analysis. Exclude `FB: No Resp` from training.

### Potential Task 1: Feedback Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS, No Response, and FB: No Resp are admin - exclude. CUE events encode arm-order permutations; aggregate to generic CUE if order-agnostic analysis desired.

 | Event | y | Meaning |
 |-------|---|---------|
 | `FB: Win` | 0 | Win feedback |
 | `FB: Loss` | 1 | Loss feedback |

## Data Quality Notes

- STATUS markers must be excluded from training.
- CUE events encode arm order permutations - group to single CUE class if order irrelevant.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update