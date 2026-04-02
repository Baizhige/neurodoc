# EEG: Amphetamine trials 5CCPT and Probabilistic Learning

**Dataset**: `openneuro_ds003987` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003987
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 69
**Channels**: 71 | **Sampling Rate**: 500 Hz

## Paradigm

A double-blind, crossover pharmacological study investigating the effects of d-amphetamine on cognitive performance using two tasks: the 5-Choice Continuous Performance Task (5CCPT), which assesses sustained attention and impulsivity, and a Probabilistic Selection Task (PST), which measures reinforcement learning. EEG was recorded across three drug sessions (placebo, low-dose, high-dose amphetamine).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003987

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `21 5CCPT` | 69 files | short | raw | 5CCPT event type 21 (likely stimulus onset) |
| `22 5CCPT` | 69 files | short | raw | 5CCPT event type 22 |
| `23 5CCPT` | 69 files | short | raw | 5CCPT event type 23 |
| `25 5CCPT` | 69 files | short | raw | 5CCPT event type 25 |
| `31 PST` | 69 files | short | raw | PST event type 31 (stimulus/feedback) |
| `32 PST` | 69 files | short | raw | PST event type 32 |
| `39 PST` | 69 files | short | raw | PST event type 39 |
| `STATUS` | 69 files | admin | raw | System hardware status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: PST Reward vs Punishment Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`31 PST`, `32 PST`, `39 PST`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31 PST` | 0 | PST event 31 (reward feedback or condition A) |
  | `32 PST` | 1 | PST event 32 (punishment feedback or condition B) |
  | `39 PST` | 2 | PST event 39 (neutral/other feedback or condition C) |
- **Kernel Notes**: Verify event ID mapping from events.tsv. Paper epochs around feedback onset (-500 to +1000ms) to classify reward vs punishment conditions using RewP ERP. The three PST event codes likely encode different feedback outcomes (reward/punishment/neutral). Map labels based on dataset documentation.
- **Evidence**:
  - DOI: 10.1007/s00213.022.06082.z — Epochs EEG around feedback onset (-500 to +1000ms) to examine reward positivity (RewP) ERP and delta-band responses to reward vs punishment feedback in probabilistic selection task.

### Normal Task 1: 5CCPT Attention Task (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS must be excluded (admin event). Events are named with task suffix (5CCPT or PST). Full event decoding requires consulting the dataset README. 23 subjects x 3 sessions (drug doses) = 69 files. Drug dose can serve as a between-condition variable.

| Event | y | Meaning |
|-------|---|------|
| `21 5CCPT` | 0 | 5CCPT condition 21 (e.g., target stimulus) |
| `22 5CCPT` | 1 | 5CCPT condition 22 |
| `23 5CCPT` | 2 | 5CCPT condition 23 |

## Data Quality Notes

- Large number of event types (30); full decoding requires dataset documentation
- Three recording sessions per subject (placebo/low/high amphetamine) - consider treating sessions independently
- STATUS is an admin marker and must be excluded

