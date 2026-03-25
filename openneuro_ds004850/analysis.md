# ODE (Social-Cognitive EEG Dataset)

**Dataset**: `openneuro_ds004850` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004850
**Category**: Complex Applied | **Subjects**: 1 | **Files (Completed)**: 1 | **Channels**: 64 | **Sampling Rate**: 128 Hz

## Paradigm

An EEG dataset (ODE) recorded during a social-cognitive paradigm with hierarchically encoded stimulus conditions. Shares the identical event structure with the STRONG (ds004849) and InsurgentCivilian (ds004852) datasets, suggesting these are companion recordings from the same experimental series. The single aggregated file requires events.tsv decoding for full interpretation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004850

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2200` | 1627 | short | raw | Dominant trigger code (primary condition) |
| `72011` | 338 | short | raw | Trigger code (category 7, type 2) |
| `52011` | 332 | short | raw | Trigger code |
| `75011` | 320 | short | raw | Trigger code |
| `55011` | 317 | short | raw | Trigger code |
| `73011` | 316 | short | raw | Trigger code |
| `74011` | 312 | short | raw | Trigger code |
| `53011` | 308 | short | raw | Trigger code |
| `54011` | 307 | short | raw | Trigger code |
| `1` | 195 | short | raw | Trigger code 1 |
| `71011` | 174 | short | raw | Trigger code |
| `2201` | 173 | short | raw | Trigger code |
| `51011` | 170 | short | raw | Trigger code |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Nback
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004850 DOI: https://doi.org/10.18112/openneuro.ds004850.v1.0.0


### Normal Task 1: Stimulus Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Identical event structure to ds004849 (STRONG) and ds004852 (InsurgentCivilian). Single aggregated file.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2200` | 0 | Primary condition code |
 | `72011` | 1 | Trigger code |
 | `52011` | 2 | Trigger code |
 | `75011` | 3 | Trigger code |
 | `55011` | 4 | Trigger code |
 | `73011` | 5 | Trigger code |
 | `74011` | 6 | Trigger code |
 | `53011` | 7 | Trigger code |
 | `54011` | 8 | Trigger code |
 | `71011` | 9 | Trigger code |
 | `2201` | 10 | Trigger code |
 | `51011` | 11 | Trigger code |
## Data Quality Notes

- Single aggregated file; individual subject data not separable.
- Identical event structure to ds004849 and ds004852 - likely companion recordings.

## References

- **Reference**: `ODE`
