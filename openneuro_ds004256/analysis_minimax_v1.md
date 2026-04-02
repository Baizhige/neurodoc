# Encoding of Sound Source Elevation in Human Cortex

**Dataset**: `openneuro_ds004256` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004256
**Category**: Sensory/Response | **Subjects**: 53 | **Files (Completed)**: 53
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed an auditory deviant detection task and a one-back sound localization task to investigate the cortical encoding of sound source elevation. Stimuli consisted of sounds presented from different vertical elevations, with subjects indicating perceived location. The study uses a multiclass design with conditions likely corresponding to different elevation angles.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004256

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 1` | 53x320 | short | raw | Auditory stimulus condition 1 (elevation angle) |
| `Stimulus/S 2` | 53x320 | short | raw | Auditory stimulus condition 2 (elevation angle) |
| `Stimulus/S 3` | 53x320 | short | raw | Auditory stimulus condition 3 (elevation angle) |
| `Stimulus/S 4` | 53x320 | short | raw | Auditory stimulus condition 4 (elevation angle) |
| `Stimulus/S 5` | 23x320 | short | raw | Auditory stimulus condition 5 (elevation angle) |
| `Stimulus/S 6` | 23x320 | short | raw | Auditory stimulus condition 6 (elevation angle) |
| `Stimulus/S 7` | 23x96 | short | raw | Auditory stimulus condition 7 (deviant/rare) |
| `New Segment/` | 53 | admin | raw | Recording segment boundary |
| `BAD boundary` | 53 | admin | raw | Bad epoch boundary marker |
| `EDGE boundary` | 53 | admin | raw | Edge boundary artifact marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`, `Stimulus/S 4`, `Stimulus/S 5`, `Stimulus/S 6`, `Stimulus/S 7`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sound Elevation Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.9 s, target_events = [`Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`, `Stimulus/S 4`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 1` | 0 | Auditory stimulus at 37.5° elevation |
  | `Stimulus/S 2` | 1 | Auditory stimulus at 12.5° elevation |
  | `Stimulus/S 3` | 2 | Auditory stimulus at -12.5° elevation |
  | `Stimulus/S 4` | 3 | Auditory stimulus at -37.5° elevation |
- **Evidence**:
  - DOI: 10.1101/2023.05.03.539222 — Uses OpenNeuro dataset ds004256 to decode sound elevation from EEG responses using multivariate logistic regression, analyzing ERP differences between adapter-probe pairs at different vertical elevations (37.5°, 12.5°, -12.5°, -37.5°)
- **Kernel Notes**: Epoch window 150-900ms post-probe captures the main elevation-sensitive ERP component. Include 200ms pre-stimulus baseline (tmin=-0.2s). S5/S6/S7 excluded from this primary task (different experimental conditions).

### Primary Task 2: Publisher-defined BIDS task: Deviantdetection
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004256 DOI: https://doi.org/10.18112/openneuro.ds004256.v1.0.5


### Primary Task 3: Publisher-defined BIDS task: Oneback
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004256 DOI: https://doi.org/10.18112/openneuro.ds004256.v1.0.5


### Normal Task 1: Sound Elevation Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: S 5/S 6/S 7 only present in 23 of 53 subjects; consider two-task splits. BAD boundary and EDGE boundary are admin events - exclude from target_events.

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus/S 1` | 0 | Auditory stimulus condition 1 |
 | `Stimulus/S 2` | 1 | Auditory stimulus condition 2 |
 | `Stimulus/S 3` | 2 | Auditory stimulus condition 3 |
 | `Stimulus/S 4` | 3 | Auditory stimulus condition 4 |
 | `Stimulus/S 5` | 4 | Auditory stimulus condition 5 |
 | `Stimulus/S 6` | 5 | Auditory stimulus condition 6 |
 | `Stimulus/S 7` | 6 | Auditory stimulus condition 7 (deviant) |

## Data Quality Notes

- S 5, S 6, S 7 appear in only 23 subjects (possibly a different task condition block)
- BAD boundary and EDGE boundary markers must not be used as target events
- Balance classes by undersampling; verify event counts per subject before pooling

## References

- **Reference**: `Encoding of Sound Source Elevation in Human Cortex`
