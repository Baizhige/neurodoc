# Mood Manipulation and PST, Experiment 2

**Dataset**: `openneuro_ds004317` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004317
**Category**: High-level Mental | **Subjects**: 50 | **Files (Completed)**: 50
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task (Probabilistic Selection Task) performed by participants following sad or happy mood manipulations. The paradigm mirrors Experiment 1 but compares sad and happy mood conditions rather than sad versus neutral. EEG was recorded to examine mood-dependent differences in reinforcement learning neural signatures.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STIM` | 50x~240 | event | raw | Stimulus onset (stimulus pair presented) |
| `RESP` | 50x~230 | event | raw | Participant button-press response |
| `FB` | 50x~240 | event | raw | Feedback onset (reward/punishment) |
| `Correct` | 50x~198 | event | raw | Correct response outcome |
| `Incorrect` | 50x~100 | event | raw | Incorrect response outcome |
| `TESTING` | 50x~1664 | event | raw | Testing phase trial marker |
| `STATUS` | 50 | admin | raw | System status marker |

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STIM`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks


### Classical Task 1: Feedback Outcome Classification (Reward vs Punishment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 6.0 s, target_events = [`Correct`, `Incorrect`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Correct` | 0 | Reward feedback (positive outcome) |
  | `Incorrect` | 1 | Punishment feedback (negative outcome) |
- **Evidence**:
  - DOI: 10.1111/psyp.14276 — Used OpenNeuro dataset ds004317 (Experiment 2, N=50) to examine how mood induction affects Reward Positivity (RewP) and reward learning during a probabilistic selection task, epoching EEG data from -2000 to 6000 ms around feedback onset and classifying correct vs incorrect feedback trials.
- **Kernel Notes**: Epoch around feedback onset (FB event). The 'Correct' and 'Incorrect' labels are embedded in the trial_type column of events.tsv. Baseline correct from -200 to 0 ms before feedback. This task corresponds to the Reward Positivity (RewP) analysis commonly used in reinforcement learning EEG studies. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Feedback Outcome Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin marker (exclude). TESTING events contain rich sub-labels in events.tsv. Better class balance than Experiment 1 (~198 correct vs ~100 incorrect in training phase).

| Event | y | Meaning |
|-------|---|---------|
| `Correct` | 0 | Correct response |
| `Incorrect` | 1 | Incorrect response |

## Data Quality Notes

- STATUS is an admin/system marker and must not be included in target events
- TESTING events contain rich sub-labels in events.tsv; the trial_type column provides full label strings
- Better class balance than Experiment 1

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review