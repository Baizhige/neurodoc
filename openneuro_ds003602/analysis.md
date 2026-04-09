# Childhood Sexual Abuse and Problem Drinking in Women: Neurobehavioral Mechanisms

**Dataset**: `openneuro_ds003602` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003602
**Category**: High-level Mental | **Subjects**: 234 | **Files (Completed)**: 699
**Channels**: 35 | **Sampling Rate**: 1000 Hz

## Paradigm

This study investigates neurobehavioral mechanisms linking childhood sexual abuse (CSA) history and problem drinking in women using affective picture viewing and startle paradigms. Participants viewed negative, neutral, and positive images including alcohol-related and non-alcohol-related content while EEG, EMG (startle), and physiological measures were recorded. Resting-state blocks (eyes open/closed) were also included. The study examines how trauma history modulates emotional reactivity and appetitive motivation for alcohol cues.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `NegStim` | 230 | short | raw | Negative picture stimulus onset |
| `NeuStim` | 230 | short | raw | Neutral picture stimulus onset |
| `PosStim` | 230 | short | raw | Positive picture stimulus onset |
| `NegAlcStimWithoutStartle` | 230 | short | raw | Negative alcohol picture (no startle probe) |
| `NeuAlcStimWithoutStartle` | 230 | short | raw | Neutral alcohol picture (no startle probe) |
| `PosAlcStimWithoutStartle` | 230 | short | raw | Positive alcohol picture (no startle probe) |
| `NegNonAlcStimWithoutStartle` | 230 | short | raw | Negative non-alcohol picture (no startle probe) |
| `NeuNonAlcStimWithoutStartle` | 230 | short | raw | Neutral non-alcohol picture (no startle probe) |
| `PosNonAlcStimWithoutStartle` | 230 | short | raw | Positive non-alcohol picture (no startle probe) |
| `NegAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Negative alcohol picture with startle probe at 1/2/3 s |
| `NeuAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Neutral alcohol picture with startle probe at 1/2/3 s |
| `PosAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Positive alcohol picture with startle probe at 1/2/3 s |
| `NegNonAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Negative non-alcohol picture with startle probe |
| `NeuNonAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Neutral non-alcohol picture with startle probe |
| `PosNonAlcP1000`/`P2000`/`P3000` | 230 each | short | raw | Positive non-alcohol picture with startle probe |
| `EyesOpen1` / `EyesOpen2` | 234 each | rest | raw | Eyes-open resting-state block marker |
| `EyesClose1` / `EyesClose2` | 234 each | rest | raw | Eyes-closed resting-state block marker |
| `EndOfRest` | 234 | admin | raw | End of resting-state block |
| `ignore` | 458 | admin | raw | Practice/ignored trial marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `NegStim`, `NeuStim`, `PosStim`, `NegAlcStimWithoutStartle`, `NeuAlcStimWithoutStartle`, `PosAlcStimWithoutStartle`, `NegNonAlcStimWithoutStartle`, `NeuNonAlcStimWithoutStartle`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

[Placeholder for additional file scan result information]

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Experiment
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003602 DOI: https://doi.org/10.18112/openneuro.ds003602.v1.0.1


### Normal Task 1: Emotional valence classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Balanced across valence conditions (~230 per category). Large dataset (699 files). Alcohol-related vs non-alcohol-related stimulus distinction available for secondary analysis.

| Event | y | Meaning |
|-------|---|--------|
| `NegStim` | 0 | Negative pictures |
| `NeuStim` | 1 | Neutral image |
| `PosStim` | 2 | Positive pictures |

## Data Quality Notes

- Large dataset with 30+ distinct event types; group by valence (Neg/Neu/Pos) and content (Alc/NonAlc) for tractable analysis.
- Eyes Open/Closed markers are resting-state block delimiters, not trial-level stimuli.
- `ignore` and `EndOfRest` are administrative markers; exclude from epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003602