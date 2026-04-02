# APPLESEED Example Dataset

**Dataset**: `openneuro_ds003710` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003710
**Category**: Biological State | **Subjects**: 13 | **Files (Completed)**: 48
**Channels**: 32 | **Sampling Rate**: 5000 Hz

## Paradigm

Longitudinal spontaneous EEG recordings from infants at 4, 8, and 12 months of age during passive viewing of social and non-social stimuli (faces, speech, objects, water). The dataset validates the APPLESEED (Automated Preprocessing Pipe-Line for the Estimation of Scale-wise Entropy from EEG Data) pipeline for pediatric EEG preprocessing and entropy estimation. Stimuli include social (face, speech) and non-social (object, water) categories presented as short video clips, with attention-getter events to orient the infant.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003710

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `face` | 48 | short | raw | Face stimulus onset (social) |
| `speech` | 48 | short | raw | Speech stimulus onset (social) |
| `object` | 48 | short | raw | Object stimulus onset (non-social) |
| `water` | 48 | short | raw | Water stimulus onset (non-social) |
| `attention-getter` | 48 | short | raw | Attention-orienting stimulus before trial |
| `experimenter-pause` | 45 | admin | raw | Experimenter pause marker |
| `New Segment` | 48 | admin | raw | Recording segment boundary marker |
| `Comment` | 48 | admin | raw | Experimenter annotation |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Social vs non-social stimulus classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to stimulus onset), target_events = [`face`, `speech`, `object`, `water`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `face` | 1 | Face stimulation (social) |
  | `speech` | 1 | Verbal stimulation (social) |
  | `object` | 0 | Object stimulus (non-social) |
  | `water` | 0 | Water stimulation (non-social) |
- **Evidence**:
  - DOI: `10.1016/j.dcn.2022.101163` — This paper develops and validates the APPLESEED preprocessing pipeline using infant EEG data from OpenNeuro ds003710, applying it to analyze scale-wise entropy differences between face viewing (social) and object viewing (non-social) conditions across developmental stages.
- **Kernel Notes**: Very high sampling rate (5000 Hz); downsample to 250-500 Hz before epoching. Only epoch around `attention-getter`-preceded trials. Exclude `experimenter-pause`, `New Segment`, and `Comment` admin markers.

### Primary Task 2: Publisher-defined BIDS task: APPLESEED example
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification *, tmax = Needs verification *, overlap = Needs verification *, target_events = [Needs verification] | segment_length = Needs verification *, overlap = Needs verification *
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003710 DOI: https://doi.org/10.1186/s12916-020-01683-x

### Normal Task 1: Social vs non-social stimulus classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very high sampling rate (5000 Hz); downsample to 250-500 Hz before epoching. Infant EEG; high artifact rates expected. Only 13 subjects (48 files across 3 age points). `New Segment`, `Comment`, and `experimenter-pause` are admin markers.

| Event | y | Meaning |
 |-------|---|------|
| `face` | 1 | Face stimulation (social) |
| `speech` | 1 | Verbal stimulation (social) |
| `object` | 0 | Object stimulus (non-social) |
| `water` | 0 | Water stimulation (non-social) |

## Data Quality Notes

- Extremely high sampling rate (5000 Hz); downsampling required before standard EEG analysis.
- Infant population; high motion artifacts and data loss expected.
- Small sample (13 subjects); longitudinal design with 3-4 files per subject across age points.
- `New Segment` and `Comment` markers should be excluded from epoching.

## References

- **Reference**: `The Automated Preprocessing Pipe-Line for the Estimation of Scale-wise Entropy from EEG Data (APPLESEED): Development and validation for use in pediatric populations. OpenNeuro ds003710.`
