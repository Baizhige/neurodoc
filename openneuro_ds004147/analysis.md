## Paradigm

A reinforcement learning task requiring participants to learn cue-response mappings for colored shapes under varying conditions of feedback validity (0.5 vs 0.8 probability). Participants learned which button press was rewarded for each cue, with the value of the correct response varying across conditions. EEG was recorded to investigate neural correlates of value-based learning and the average reward rate representation.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 12 files | short | raw | Stimulus onset (cue presentation) |
| `New Segment` | 12 files | admin | raw | Recording segment boundary - exclude |
| `Comment` | 12 files | admin | raw | Experimenter annotation - exclude |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

Minimal placeholder content for File Scan Result info subsection.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Casinos
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004147 DOI: https://doi.org/10.1037/a0038339


### Normal Task 1: Stimulus-Locked Reinforcement Learning (binary/multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: New Segment and Comment are admin markers and must be excluded. Only 12 subjects - very small dataset. The `Stimulus` event needs behavioral outcome (correct/incorrect or rewarded/not-rewarded) from events.tsv for supervised learning. Feedback validity condition (0.5 vs 0.8) is available as a task variable.


| Event | y | Meaning |
|-------|---|-------|
| `Stimulus` | 0/1 | Cue onset; label from behavioral outcome (reward/no reward in events.tsv) |

## Data Quality Notes

- Only 12 subjects - very small sample; unsuitable for cross-subject generalization
- New Segment and Comment are admin markers to exclude
- Behavioral outcome labels must be extracted from events.tsv alongside Stimulus events

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.


> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004147