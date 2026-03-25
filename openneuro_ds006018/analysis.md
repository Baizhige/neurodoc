# Cognitive Electrophysiology in Socioeconomic Context in Adulthood: An EEG dataset

**Dataset**: `openneuro_ds006018` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006018
**Category**: High-level Mental | **Subjects**: 127 | **Files (Completed)**: 357 | **Channels**: 31 | **Sampling Rate**: 500 Hz

## Paradigm

A suite of standardized ERP tasks from the ERP CORE compendium (Kappenman et al. 2021) measuring neural correlates of perception, cognition, and action in adults in relation to socioeconomic status and ADHD symptoms. Tasks include N170 (face perception), MMN (mismatch negativity), N2pc (visual attention), P3 (cognitive updating), N400 (semantic processing), ERN (error monitoring), and LRP (lateralized readiness potential).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006018

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S201` | 40081 | short | raw | ERP CORE stimulus code 201 |
| `S 80` | 30199 | short | raw | ERP CORE stimulus code 80 |
| `S212` | 10400 | short | raw | ERP CORE stimulus code 212 |
| `S111` | 9971 | short | raw | ERP CORE stimulus code 111 |
| `S222` | 9017 | short | raw | ERP CORE stimulus code 222 |
| `S121` | 8449 | short | raw | ERP CORE stimulus code 121 |
| `S 22` | 8268 | short | raw | ERP CORE stimulus code 22 |
| `S 11` | 8263 | short | raw | ERP CORE stimulus code 11 |
| `S 12` | 8252 | short | raw | ERP CORE stimulus code 12 |
| `S 21` | 8244 | short | raw | ERP CORE stimulus code 21 |
| `S 70` | 7977 | short | raw | ERP CORE stimulus code 70 |
| `S202` | 6292 | short | raw | ERP CORE stimulus code 202 |
| `S221` | 5197 | short | raw | ERP CORE stimulus code 221 |
| `S122` | 4665 | short | raw | ERP CORE stimulus code 122 |
| `S211` | 3707 | short | raw | ERP CORE stimulus code 211 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S201`, `S 80`, `S212`, `S111`, `S222`, `S121`, `S 22`, `S 11`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds006018 DOI: https://doi.org/10.18112/openneuro.ds006018.v1.2.2


### Primary Task 2: Publisher-defined BIDS task: Passive Auditory Oddball
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006018 DOI: https://doi.org/10.18112/openneuro.ds006018.v1.2.2


### Primary Task 3: Publisher-defined BIDS task: Active Visual Oddball
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006018 DOI: https://doi.org/10.18112/openneuro.ds006018.v1.2.2


### Normal Task 1: ERP CORE Multi-paradigm (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Multi-paradigm ERP CORE dataset. `boundary` is admin and excluded. Codes encode task x condition combinations per ERP CORE documentation.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S 12` | 0 | ERP code 12 |
 | `S 22` | 1 | ERP code 22 |
 | `S 21` | 2 | ERP code 21 |
 | `S 11` | 3 | ERP code 11 |
 | `S201` | 4 | ERP code 201 |
 | `S202` | 5 | ERP code 202 |
 | `S221` | 6 | ERP code 221 |
 | `S122` | 7 | ERP code 122 |
 | `S212` | 8 | ERP code 212 |
 | `S222` | 9 | ERP code 222 |
 | `S111` | 10 | ERP code 111 |
 | `S121` | 11 | ERP code 121 |
 | `S211` | 12 | ERP code 211 |
 | `S112` | 13 | ERP code 112 |
 | `S 80` | 14 | ERP code 80 |
 | `S 70` | 15 | ERP code 70 |
 | `S180` | 16 | ERP code 180 |
 | `S 1` | 17 | ERP code 1 |
 | `S 25` | 18 | ERP code 25 |
 | `S 23` | 19 | ERP code 23 |
 | `S 24` | 20 | ERP code 24 |
 | `S 53` | 21 | ERP code 53 |
 | `S 43` | 22 | ERP code 43 |
 | `S 45` | 23 | ERP code 45 |
 | `S 44` | 24 | ERP code 44 |
 | `S 41` | 25 | ERP code 41 |
 | `S 13` | 26 | ERP code 13 |
 | `S 14` | 27 | ERP code 14 |
 | `S 42` | 28 | ERP code 42 |
## Data Quality Notes

- Multi-paradigm dataset - participants completed multiple ERP CORE tasks; segment by task if needed.
- `boundary` is an administrative marker, excluded from target_events.
- Apply bandpass filter (0.1-40 Hz) and artifact rejection; baseline correct [-0.2, 0] s.

## References

- **Reference**: `Isbell, E., Peters, A. N., Richardson, D. M., & Rodas De Len, N. E. (2025). Cognitive electrophysiology in socioeconomic context in adulthood. Scientific Data, 12(1), 19.`
