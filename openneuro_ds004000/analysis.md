# Fribourg Ultimatum Game in Schizophrenia Study

**Dataset**: `openneuro_ds004000` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004000
**Category**: High-level Mental | **Subjects**: 43 | **Files (Completed)**: 84
**Channels**: 132 | **Sampling Rate**: 2048 Hz

## Paradigm

A social decision-making study in which patients with psychosis and healthy controls played the Ultimatum Game in both responder and proposer roles across multiple blocks. EEG was recorded while participants decided to accept or reject monetary offers from a human or computer partner, enabling investigation of fairness processing and social cognition differences in psychosis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004000

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 1` | 42 files | short | raw | Stimulus onset type 1 |
| `Stimulus/S 2` | 42 files | short | raw | Stimulus onset type 2 |
| `Stimulus/S 3` | 42 files | short | raw | Stimulus onset type 3 |
| `Stimulus/S 4` | 42 files | short | raw | Stimulus onset type 4 |
| `Stimulus/S 64` | 42 files | short | raw | Stimulus onset - offer/condition marker |
| `Stimulus/S 96` | 42 files | short | raw | Stimulus onset marker |
| `Stimulus/S128` | 42 files | short | raw | Stimulus onset marker |
| `Stimulus/S160` | 42 files | short | raw | Stimulus onset marker |
| `Stimulus/S193`-`S201` | 28-42 files | short | raw | Condition-specific stimulus markers |
| `Stimulus/S225`-`S233` | 28-42 files | short | raw | Condition-specific stimulus markers |
| `Stimulus/S195`-`S200` | 33-41 files | short | raw | Condition-specific stimulus markers |
| `UserDefined/Blink` | 84 files | admin | raw | Blink artifact marker |
| `Time 0/` | 84 files | admin | raw | Recording start time marker |
| `Response/R 1` | 6 files | short | raw | Button press response |
| `Response/R 3` | 1 file | short | raw | Button press response |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`, `Stimulus/S 4`, `Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Responder
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004000 DOI: https://doi.org/10.18112/openneuro.ds004000.v1.0.0


### Normal Task 1: Ultimatum Game Stimulus Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: UserDefined/Blink and Time 0/ are admin markers and must be excluded. Full decoding of S-codes requires dataset documentation. Psychosis vs. control group label is available from participants.tsv for group-level classification.

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus/S 1` | 0 | Stimulus type 1 (e.g., fair offer) |
 | `Stimulus/S 2` | 1 | Stimulus type 2 |
 | `Stimulus/S 3` | 2 | Stimulus type 3 |
 | `Stimulus/S 4` | 3 | Stimulus type 4 (e.g., unfair offer) |
## Data Quality Notes

- Large number of distinct Stimulus/ codes; full mapping requires consulting the study protocol
- UserDefined/Blink and Time 0/ are administrative markers to exclude
- 43 subjects x ~2 sessions = 84 files; verify session structure

## References

- _No paper reference available_
