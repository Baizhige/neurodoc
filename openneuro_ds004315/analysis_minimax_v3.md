# Mood Manipulation and PST, Experiment 1

**Dataset**: `openneuro_ds004315` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004315
**Category**: High-level Mental | **Subjects**: 50 | **Files (Completed)**: 50
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task (Probabilistic Selection Task) consisting of training and testing phases following a sad or neutral mood manipulation. Participants learned to select stimuli associated with reward or punishment, and were subsequently tested on novel stimulus pairs. EEG was recorded to examine how mood state affects the neural correlates of reinforcement learning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004315

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STIM` | 50x~240 | short | raw | Stimulus onset (stimulus pair presented) |
| `RESP` | 50x~230 | short | raw | Participant button-press response |
| `FB` | 50x~240 | short | raw | Feedback onset (reward/punishment) |
| `Correct` | 50x~200 | short | raw | Correct response outcome |
| `Incorrect` | 50x~85 | short | raw | Incorrect response outcome |
| `TESTING` | 50x~1700 | short | raw | Testing phase trial marker |
| `STATUS` | 50 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STIM`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Feedback-Locked Reward Positivity (RewP) Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 6.0 s, target_events = [`FB`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Correct` | 0 | Correct response (reward) |
  | `Incorrect` | 1 | Incorrect response (punishment) |
- **Super Meta Notes**: Derived from raw event `FB` (feedback onset) by aligning epochs to feedback onset and labeling based on trial outcome (Correct/Incorrect). Kernel step: extract FB epochs, then use events.tsv trial outcome column to assign y=0 for Correct and y=1 for Incorrect trials.
- **Evidence**:
  - DOI: 10.1111/psyp.14276 — EEG data from OpenNeuro ds004315 examined RewP ERP (200-350ms at FCz) epoched -2s to 6s relative to feedback onset, comparing correct vs incorrect feedback outcomes
- **Kernel Notes**: Epoch around FB (feedback onset). Apply baseline correction -200ms to 0ms. Extract epochs for all FB events, then derive labels from trial outcome (Correct/Incorrect) in events.tsv. Focus ROI at electrode FCz for RewP analysis. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Feedback Outcome Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin marker (exclude). TESTING events have rich sub-labels in the actual events.tsv (e.g., "TESTING: Right Press, Correct") useful for further analysis. Class imbalance: Correct >> Incorrect.

| Event | y | Meaning |
|-------|---|----------|
| `Correct` | 0 | Correct response |
| `Incorrect` | 1 | Incorrect response |

## Data Quality Notes

- STATUS is an admin/system marker and must not be included in target events
- TESTING events contain rich sub-labels in events.tsv; the trial_type column provides full label strings
- Class imbalance between Correct (~200) and Incorrect (~55 training) responses

