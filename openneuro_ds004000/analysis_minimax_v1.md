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

### Primary Task 1: Group Classification - Schizophrenia vs Healthy Controls (Responder Condition)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.7 s, overlap = 0.0 *, target_events = [`Stimulus/S 64` *]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | HC | 0 | Healthy control participant |
  | SCZ | 1 | Schizophrenia patient |
- **Super Meta Notes**: Group labels (HC/SCZ) are derived from clinical diagnosis in participants.tsv. Target events are extracted from stimulus onset markers (S 64 likely marks offer presentation in responder condition). The key analysis window is -0.7s to 0s (pre-stimulus anticipation period).
- **Evidence**:
  - DOI: 10.1016/j.schres.2023.01.029 — Uses dynamic functional connectivity (imaginary coherence) comparing 24 HC and 19 SCZ patients during Ultimatum Game responder condition, finding significant fronto-occipital alpha band differences in pre-stimulus window
  - DOI: 10.1016/j.schres.2017.05.037 — Analyzes ERP components (P2, FRN) comparing 16 SCZ and 19 HC during responder condition, finding reduced FRN amplitude in patients (p=0.009)
- **Kernel Notes**: Must load participants.tsv to extract group labels; epoch around stimulus onset markers for responder condition trials only; segmentation uses 700ms non-overlapping windows aligned to stimulus onset

### Primary Task 2: Group Classification - Schizophrenia vs Healthy Controls (ERP Epoch)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`Stimulus/S 64` *]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | HC | 0 | Healthy control participant |
  | SCZ | 1 | Schizophrenia patient |
- **Super Meta Notes**: Group labels derived from clinical diagnosis in participants.tsv; epoch captures FRN (320-360ms) and P2 (220-240ms) components for ERP analysis
- **Evidence**:
  - DOI: 10.1016/j.schres.2017.05.037 — Investigates P2 and FRN differences between 16 SCZ and 19 HC during Ultimatum Game play in both proposer/responder conditions
- **Kernel Notes**: Apply 0.3-30Hz bandpass filter as per paper; epoch from -200ms to +500ms relative to stimulus onset; extract ERP amplitudes for FRN and P2 windows as features

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
