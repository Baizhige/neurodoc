# EEG: Simon Conflict with Reinforcement + Cabergoline Challenge

**Dataset**: `openneuro_ds003518` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003518
**Category**: High-level Mental | **Subjects**: 110 | **Files (Completed)**: 137
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

This study examines whether conflict acts as an implicit cost in reinforcement learning using a modified Simon task with pharmacological manipulation. Healthy participants performed a Simon conflict task across training and test phases, with a double-blind Cabergoline (dopamine D2/D3 agonist) challenge administered to examine dopaminergic modulation. The training phase included reinforcement feedback to shape behavior; the test phase probed learned conflict avoidance. Mid-frontal theta and error-related negativity are key EEG measures.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Trn Stim` | 2192 | event | raw | Training phase stimulus (congruent/incongruent Simon) |
| `Test Stim` | 1644 | event | raw | Test phase stimulus |
| `correct` | 548 | event | raw | Correct response outcome |
| `incorrect` | 547 | event | raw | Incorrect response / error outcome |
| `Trn Resp` | 547 | event | raw | Training phase button-press response |
| `Test Resp` | 548 | event | raw | Test phase button-press response |
| `FB` | 274 | event | raw | Feedback stimulus in training phase |
| `Trn No Response` | 136 | event | raw | Missing response in training phase |
| `Test No Response` | 55 | event | raw | Missing response in test phase |
| `STATUS` | 137 | admin | raw | System status marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
| `stim_route` | available | Route: `stim`; Role: Trigger-channel or stimulus-marker based labeling |
| `candidate_trigger_labels` | available | `Trn Stim`, `Test Stim`, `STATUS` |

## Tasks

### Classical Task 1: Correct/Incorrect Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`correct`, `incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `incorrect` | 0 | Error response |
  | `correct` | 1 | Correct response |
- **Evidence**:
  - DOI: `10.1038/ncomms6394` — EEG analysis of Simon conflict task to examine how response conflict modulates reinforcement learning; epochs analyzed from -500 to +1000 ms relative to stimulus events; correct vs incorrect classification used to examine frontal theta dynamics predicting choice behavior.
- **Kernel Notes**: Epochs extracted around `Trn Stim` and `Test Stim` events using the cue epoch window (-1500 to +5000 ms) from the original study, with analysis focused on the peri-response window (-500 to +1000 ms). Labels derived from `correct` and `incorrect` outcome events. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- 64-channel EEG with 110 subjects across cabergoline and placebo conditions.
- Drug condition information in participants.tsv; use as a grouping variable for stratified analysis.
- Some subjects may have two sessions; verify file-to-subject mapping.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review