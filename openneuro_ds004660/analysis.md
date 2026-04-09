# TNO (Military Cognitive Workload)

**Dataset**: `openneuro_ds004660` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004660
**Category**: Complex Applied | **Subjects**: 42 | **Files (Completed)**: 42
**Channels**: 38 | **Sampling Rate**: 512 Hz

## Paradigm

A military-relevant cognitive workload study conducted at TNO research institute, involving multiple hierarchically encoded task conditions represented by 5-digit numeric trigger codes. The paradigm likely involves surveillance, target detection, or dual-task conditions common in defense research. Event codes encode task type, difficulty level, and stimulus properties in a hierarchical scheme.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `14211` | 42922 | short | raw | Hierarchical task code - primary condition |
| `14212` | 42922 | short | raw | Hierarchical task code - primary condition variant |
| `21111` | 9228 | short | raw | Hierarchical task code |
| `14112` | 9228 | short | raw | Hierarchical task code |
| `14111` | 9228 | short | raw | Hierarchical task code |
| `13001` | 3663 | short | raw | Hierarchical task code |
| `13002` | 3663 | short | raw | Hierarchical task code |
| `21201` | 3663 | short | raw | Hierarchical task code |
| `15521` | 1840 | short | raw | Hierarchical task code |
| `15421` | 1840 | short | raw | Hierarchical task code |
| `14121` | 1680 | short | raw | Hierarchical task code |
| `14122` | 1680 | short | raw | Hierarchical task code |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.


### Info

All event codes are 5-digit hierarchical numeric identifiers - full decode needed. 30+ unique event types; group by high-level condition category for practical classification.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds004660 DOI: https://doi.org/10.18112/openneuro.ds004660.v1.0.2


### Normal Task 1: Conditional classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All codes are hierarchically structured 5-digit identifiers. Full decode table required from TNO dataset README or associated paper.

| Event | y | Meaning |
|-------|---|--------|
| `14211` | 0 | Primary task code |
| `14212` | 1 | Primary task code variant |
| `21111` | 2 | Task code |
| `14112` | 3 | Task code |
| `14111` | 4 | Task code |
| `13001` | 5 | Task code |
| `13002` | 6 | Task code |
| `21201` | 7 | Task code |

## Data Quality Notes

All event codes are 5-digit hierarchical numeric identifiers - full decode needed.
30+ unique event types; group by high-level condition category for practical classification.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004660