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
> **Status**: wait_manual_review
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

### Primary Task 1: Group Classification - Schizophrenia vs Healthy Controls during Ultimatum Game Responder Condition (ERP Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 64`* | 0 | Healthy control (HC) participant |
  | `Stimulus/S 64`* | 1 | Schizophrenia patient (SCZ) |
- **Super Meta Notes**: Labels derived from clinical diagnosis (participants.tsv) not raw event markers. Kernel must load participant diagnosis from participants.tsv and merge with epoch labels based on subject ID. Responder condition markers identified from Stimulus/S codes.
- **Evidence**:
  - DOI: 10.1016/j.schres.2017.05.037 — EEG study investigates differences in ERPs (P2, FRN) between 16 schizophrenic patients and 19 healthy controls during Ultimatum Game responder condition, finding reduced FRN amplitude in patients (p=0.009).
- **Kernel Notes**: Extract epochs aligned to offer/condition markers; merge with participant group labels from participants.tsv; verify Stimulus/S code mapping to responder condition from events.tsv. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Group Classification - Schizophrenia vs Healthy Controls during Ultimatum Game Responder Condition (Functional Connectivity)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.7 s, overlap = 0.0, target_events = [`Stimulus/S 64`, `Stimulus/S 96`, `Stimulus/S128`, `Stimulus/S160`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Segment | y | Meaning |
  |---------|---|---------|
  | Any segment | 0 | Healthy control (HC) participant |
  | Any segment | 1 | Schizophrenia patient (SCZ) |
- **Super Meta Notes**: Labels derived from clinical diagnosis (participants.tsv) not raw event markers. Analysis focuses on -0.7s to 0s pre-stimulus window during responder condition. Kernel must compute functional connectivity (e.g., imaginary coherence) within alpha band for each epoch.
- **Evidence**:
  - DOI: 10.1016/j.schres.2023.01.029 — Uses openneuro_ds004000 dataset to analyze EEG dynamic functional connectivity comparing 24 healthy controls and 19 schizophrenia patients during Ultimatum Game responder condition, finding significant fronto-occipital alpha-band connectivity differences in pre-stimulus window.
- **Kernel Notes**: Segment continuous data using sliding windows aligned to stimulus onset events; compute connectivity metrics in alpha band (8-13 Hz); merge segment labels with participant group from participants.tsv; verify Stimulus/S code mapping to responder condition.

## Data Quality Notes

- Large number of distinct Stimulus/ codes; full mapping requires consulting the study protocol
- UserDefined/Blink and Time 0/ are administrative markers to exclude
- 43 subjects x ~2 sessions = 84 files; verify session structure

