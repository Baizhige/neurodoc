# Executive Functioning Study for Assessing the Effect of Neurofeedback

**Dataset**: `openneuro_ds004350` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004350
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 480
**Channels**: 64 | **Sampling Rate**: 256 Hz

## Paradigm

Participants performed a battery of executive function tasks including a visual N-back working memory task (stimuli A/B/C/D), a Sustained Attention to Response Task (SART, target/nontarget), and a Local-Global hierarchical stimulus task (largeH/largeT x smallH/smallT). The study assessed the effect of neurofeedback training on executive function performance.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: reaction time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004350

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `target` | 44xx | short | raw | Target stimulus (requires response) |
| `nontarget` | 44xx | short | raw | Non-target stimulus (no-go) |
| `A` | 144xx | short | raw | N-back stimulus A |
| `B` | 144xx | short | raw | N-back stimulus B |
| `C` | 144xx | short | raw | N-back stimulus C |
| `D` | 144xx | short | raw | N-back stimulus D |
| `largeHSmallH` | 48xx | short | raw | Large H / Small H (local-global congruent) |
| `largeHSmallT` | 48xx | short | raw | Large H / Small T (local-global incongruent) |
| `largeTSmallH` | 48xx | short | raw | Large T / Small H (local-global incongruent) |
| `largeTSmallT` | 48xx | short | raw | Large T / Small T (local-global congruent) |
| `responseLargeH` | 48xx | short | raw | Response: Large H selected |
| `responseLargeT` | 48xx | short | raw | Response: Large T selected |
| `responseSmallH` | 48xx | short | raw | Response: Small H selected |
| `responseSmallT` | 48xx | short | raw | Response: Small T selected |
| `rt` | 188xx | short | raw | Reaction time marker |
| `255` | 2 | admin | raw | System trigger code 255 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: NB1
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004350 DOI: https://doi.org/10.1038/nn1233


### Primary Task 2: Publisher-defined BIDS task: NB3
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004350 DOI: https://doi.org/10.1038/nn1233


### Primary Task 3: Publisher-defined BIDS task: LG
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004350 DOI: https://doi.org/10.1038/nn1233


### Normal Task 1: SART Target Detection (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical codes (1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 128, 255) are likely system/artifact markers - exclude from target_events. Multiple tasks in one dataset; files are per-task. Separate HDF5 files per task recommended.

| Event | y | Meaning |
 |-------|---|------|
 | `nontarget` | 0 | Non-target (go) stimulus |
 | `target` | 1 | Target (no-go) stimulus |
## Data Quality Notes

- Multiple distinct tasks (SART, N-back, Local-Global) in same dataset; files are per-task
- Numerical trigger codes (1-255) are system markers, not task events
- 480 files across 24 subjects (multiple sessions/tasks per subject)

## References

- **Reference**: `Executive Functionning Study for Assessing the Effect of Neurofeedback`
