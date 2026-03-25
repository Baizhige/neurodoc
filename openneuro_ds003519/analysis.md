# EEG: Visual Working Memory + Cabergoline Challenge

**Dataset**: `openneuro_ds003519` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003519
**Category**: High-level Mental | **Subjects**: 27 | **Files (Completed)**: 54
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a visuospatial working memory task under a double-blind Cabergoline (dopamine D2/D3 agonist) drug challenge to investigate pharmacological modulation of working memory processing. The task involved memorizing spatial locations of stimuli followed by a probe stimulus requiring a match/non-match judgment. Distractor stimuli were presented during the retention interval. The study examines individual differences in working memory capacity and dopaminergic modulation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003519

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stim Onset` | 162 | short | raw | Study stimulus onset (to-be-remembered) |
| `Question Mark Probe` | 108 | short | raw | Probe stimulus requiring match judgment |
| `Response` | 108 | short | raw | Participant button-press response |
| `STATUS` | 54 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stim Onset`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Visual Working Memory
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.3758/s13415-018-0584-6


### Normal Task 1: Stimulus presentation ERP (single class, can be used for feature extraction)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Study stimulus vs probe comparison captures encoding vs retrieval phases. Two sessions per subject (drug vs placebo); treat session as covariate.

| Event | y | Meaning |
 |-------|---|------|
| `Stim Onset` | 0 | Memory stimulus presentation |
| `Question Mark Probe` | 1 | Probe stimulus presentation |
## Data Quality Notes

- 54 files for 27 subjects; two sessions per subject (drug/placebo crossover design).
- Drug condition information should be in participants.tsv or scans.tsv.
- Limited event types; primary utility is ERP characterization of encoding and retrieval phases.

## References

- **Reference**: `Dopamine D2 agonist affects visuospatial working memory distractor interference depending on individual differences in baseline working memory span. Cognitive, Affective, & Behavioral Neuroscience, 2018. DOI: 10.3758/s13415-018-0584-6`
