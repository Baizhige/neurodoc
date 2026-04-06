# EEG: Probabilistic Selection Task (PST) + PST with Cabergoline Challenge

**Dataset**: `openneuro_ds004532` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004532
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 80 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed the Probabilistic Selection Task (PST) in two sessions: a placebo session and a session with cabergoline (dopamine D2/D3 agonist). The PST involves learning to choose symbols with higher reward probability through feedback. Events encode training stimuli (Trn Stim), test stimuli (Tst Stim), feedback (FB), and outcome (correct/incorrect). The study investigates dopaminergic modulation of reinforcement learning.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Trn Stim` | ~80xN | event | raw | Training stimulus onset |
| `Tst Stim` | ~80xN | event | raw | Test stimulus onset |
| `FB` | ~80xN | event | raw | Feedback onset |
| `correct` | ~80xN | event | raw | Correct response outcome |
| `incorrect` | ~80xN | event | raw | Incorrect response outcome |
| `STATUS` | ~80xN | admin | raw | BrainVision hardware status marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Trn Stim`, `Tst Stim`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Binary Outcome Classification (correct vs incorrect)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 5.0 s *, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `correct` | 0 | Correct response (reward) |
  | `incorrect` | 1 | Incorrect response (punishment) |
- **Super Meta Notes**: (NONE - meta_level is raw)
- **Evidence**:
  - DOI: 10.1038/ncomms6394 — Nature Communications paper presenting the original PST EEG study with 64-channel recordings at 500 Hz, demonstrating binary outcome classification (correct vs incorrect) using feedback-locked epochs (-1500 to 5000 ms) and confirming the dataset was used for reinforcement learning analysis.
- **Kernel Notes**: Epoch around `FB` (feedback onset) to capture the neural response to outcome. Use `correct` and `incorrect` events occurring after each FB to derive labels. Baseline correction: -300 to -200 ms prior to feedback onset (per paper). (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Outcome Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin event - exclude from target_events. Trn Stim and Tst Stim are stimulus onset events; FB is the feedback onset. correct/incorrect provide clear binary outcome labels.

| Event | y | Meaning |
|-------|---|---------|
| `correct` | 0 | Correct response outcome |
| `incorrect` | 1 | Incorrect response outcome |

## Data Quality Notes

- 40 subjects x 2 sessions (placebo + cabergoline) = 80 files
- STATUS markers are BrainVision hardware events, not task-related
- Two sessions per subject enable within-subject drug effect analysis


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review