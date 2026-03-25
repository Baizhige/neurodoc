# EEG: Probabilistic Selection Task (PST) + PST with Cabergoline Challenge

**Dataset**: `openneuro_ds004532` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004532
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 80 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed the Probabilistic Selection Task (PST) in two sessions: a placebo session and a session with cabergoline (dopamine D2/D3 agonist). The PST involves learning to choose symbols with higher reward probability through feedback. Events encode training stimuli (Trn Stim), test stimuli (Tst Stim), feedback (FB), and outcome (correct/incorrect). The study investigates dopaminergic modulation of reinforcement learning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004532

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Trn Stim` | ~80xN | short | raw | Training stimulus onset |
| `Tst Stim` | ~80xN | short | raw | Test stimulus onset |
| `FB` | ~80xN | short | raw | Feedback onset |
| `correct` | ~80xN | short | raw | Correct response outcome |
| `incorrect` | ~80xN | short | raw | Incorrect response outcome |
| `STATUS` | ~80xN | admin | raw | BrainVision hardware status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Trn Stim`, `Tst Stim`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: PST
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004532 DOI: https://doi.org/10.1038/ncomms6394


### Normal Task 1: Outcome Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin event - exclude from target_events. Trn Stim and Tst Stim are stimulus onset events; FB is the feedback onset. correct/incorrect provide clear binary outcome labels.

| Event | y | Meaning |
 |-------|---|------|
 | `correct` | 0 | Correct response outcome |
 | `incorrect` | 1 | Incorrect response outcome |
## Data Quality Notes

- 40 subjects x 2 sessions (placebo + cabergoline) = 80 files
- STATUS markers are BrainVision hardware events, not task-related
- Two sessions per subject enable within-subject drug effect analysis

## References

- **Reference**: `EEG: Probabilistic Selection Task (PST) + PST with Cabergoline Challenge`
