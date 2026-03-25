# Visual Attribute-Specific Contextual Trajectory Paradigm

**Dataset**: `openneuro_ds004603` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004603
**Category**: Sensory/Response | **Subjects**: 37 | **Files (Completed)**: 37 | **Channels**: 65 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants observed sequences of visual stimuli that either followed or violated an established contextual trajectory in one of three visual attributes - brightness (color), size, or orientation. The paradigm tests predictive coding by contrasting EEG responses to expected (step) stimuli against unexpected violations and a no-trajectory control condition. Each sequence comprised four ordered steps followed by a target or violation stimulus.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004603

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `step_1` | 31368 | short | raw | Sequence step 1 - first ordered stimulus in trajectory |
| `step_2` | 31367 | short | raw | Sequence step 2 |
| `step_3` | 31367 | short | raw | Sequence step 3 |
| `step_4` | 31367 | short | raw | Sequence step 4 - final step before target/violation |
| `control` | 14203 | short | raw | Control condition - no established trajectory |
| `siz_vio` | 4736 | short | raw | Size trajectory violation |
| `ori_vio` | 4735 | short | raw | Orientation trajectory violation |
| `col_vio` | 4735 | short | raw | Color/brightness trajectory violation |
| `catch` | 2958 | short | raw | Catch trial requiring button-press response |
| `initalising_triggers` | 1 | admin | raw | System initialisation trigger (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `initalising_triggers`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: CTP
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004603 DOI: https://doi.org/10.18112/openneuro.ds004603.v1.1.0


### Normal Task 1: Violation Detection (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `initalising_triggers` (1 total) is admin - exclude. Sequence steps (step_1-step_4) can be used for prediction build-up ERP analysis.

 | Event | y | Meaning |
 |-------|---|---------|
 | `control` | 0 | No-trajectory control |
 | `siz_vio` | 1 | Size violation |
 | `ori_vio` | 2 | Orientation violation |
 | `col_vio` | 3 | Color violation |
## Data Quality Notes

- Exclude `initalising_triggers` from all analysis.
- Catch trials have a motor response component - treat separately or exclude from violation analysis.

## References

- **Reference**: `Visual Attribute-Specific Contextual Trajectory Paradigm`
