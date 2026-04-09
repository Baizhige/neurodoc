# Illusion of Agency over Electrically-Actuated Movements

**Dataset**: `openneuro_ds004561` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004561
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants experienced electrical muscle stimulation that actuated their hand movements in three conditions: stimulation (involuntary movement), pretest (voluntary movement before stimulation), and posttest (voluntary movement after stimulation). EEG was recorded to investigate illusory sense of agency over externally-driven movements. The study explores how prior voluntary movement influences agency attribution over stimulation-induced movements.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulation` | ~20xN | short | raw | Electrical stimulation onset (involuntary movement) |
| `pretest` | ~20xN | short | raw | Pre-stimulation voluntary movement |
| `posttest` | ~20xN | short | raw | Post-stimulation voluntary movement |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulation`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

- **Primary Label Routes**: Annotation, stim
- **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004561

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Agency RT
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004561 DOI: https://doi.org/10.18112/openneuro.ds004561.v1.0.0


### Normal Task 1: Agency Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 3-class classification of agency conditions. stimulation = externally actuated movement, pretest/posttest = voluntary movements before/after stimulation session.

| Event | y | Meaning |
|-------|---|------|
| `stimulation` | 0 | Electrical stimulation (involuntary movement) |
| `pretest` | 1 | Pre-stimulation voluntary movement |
| `posttest` | 2 | Post-stimulation voluntary movement |

## Data Quality Notes

- 20 subjects with balanced condition structure
- 64 channels at 512 Hz provides good temporal resolution for movement-related potentials

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.