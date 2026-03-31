# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 949
**Channels**: 63 | **Sampling Rate**: 5000 Hz | **Manual Review**: Liu Peng |

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimate of participants were collected using a visual analogue scale.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: response_time, reaction time, confidence, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002158

## Event Structure

| Event ID | Trials | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| active_response/obs_response | 119±5 | short | raw | Response onset marker - actual trial type may be in events.tsv `value` column. |

> **Event Type Description**:
>
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5` (Hypothetical existence; not mentioned in the paper)
> - `admin`: system/boundary marker, **not used for epoching**.
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Normal Task 1: Confidence Regression from EEG during Speeded Perceptual Decisions
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`response_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  
  | y | Meaning |
  |---|---------|
  | confidence (continuous 0-1) | Metacognitive confidence rating (0=sure error, 0.5=unsure, 1=sure correct) |
- **Raw Meta Notes**: Confidence ratings are raw behavioral data, aligned with epochs time-locked to the response onset (button press in active condition, virtual hand appearance in observation condition). The paper also analyzed post-response windows (0-200ms, 200-450ms) for multivariate decoding of confidence.
- **Evidence**:
  
  - DOI: 10.1073/pnas.1918335117 — EEG amplitude time-locked to first-order response onset used to model confidence via linear regression; multivariate EEG decoding derived single-trial confidence predictions.
- **Kernel Notes**: Extract confidence values from behavioral metadata files as regression target. Verify from events.tsv that `response_onset` corresponds to the correct behavioral trigger (button press/visual hand). 

### Normal Task 2: Publisher-defined BIDS task: Main
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002158 DOI: https://doi.org/10.1073/pnas.1918335117

### Normal Task 3: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002158 DOI: https://doi.org/10.1073/pnas.1918335117


## Data Quality Notes

- Event label `unknown` is a placeholder - actual trial type information may be in events.tsv `value` or `trial_type` columns.
- Confidence ratings stored in misc channel `confidence`; reaction times in `response_time`.
- High sampling rate (5000 Hz); significant downsampling required.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging`
