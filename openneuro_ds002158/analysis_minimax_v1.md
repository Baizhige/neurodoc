# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 119 | **Files (Completed)**: 119
**Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. The `confidence` rating is stored as a misc channel for regression analysis. High sampling rate (5000 Hz) requires downsampling before epoching.

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

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `unknown` | 119 (files) | short | raw | Trial onset marker - actual trial type may be in events.tsv `value` column; used as epoch anchor |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Confidence Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`response_onset`, `first-order_response`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `confidence` | 0.0–1.0 | Continuous confidence rating (0=sure error, 0.5=unsure, 1=sure correct) |
- **Super Meta Notes**: Confidence ratings are metacognitive judgments collected via visual analog scale (second-order task). The misc channel stores continuous confidence values (0-1 scale). EEG is epoched relative to first-order response onset (button press or observed hand appearance). Linear regression and multivariate decoding used to predict confidence from EEG amplitudes.
- **Evidence**:
  - DOI: 10.1073/pnas.1918335117 — PNAS 2020 paper analyzing EEG+fMRI from OpenNeuro ds002158 to study confidence in speeded perceptual decisions, using linear regression to model EEG amplitude time-locked to first-order response as a function of confidence
- **Kernel Notes**: Epoch raw EEG around response_onset event using tmin=-0.2s, tmax=0.6s. Extract confidence values from misc channel as regression targets. High sampling rate (5000 Hz); downsample before epoching. Condition labels (active vs observation) available in events.tsv value column for secondary analysis.

### Normal Task 1: Confidence Regression (regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: N/A (null(regression only; `unknown` serves as epoch trigger))
- **Notes**: `unknown` event label is the trial onset marker - use as epoch anchor. Primary task is regression of confidence rating from EEG. High sampling rate (5000 Hz); downsample before epoching.

- **Regression target**:`confidence`(metacognitive rating stored as misc channel)

## Data Quality Notes

- Event label `unknown` is a placeholder - actual trial type information may be in events.tsv `value` or `trial_type` columns.
- Confidence ratings stored in misc channel `confidence`; reaction times in `response_time`.
- High sampling rate (5000 Hz); significant downsampling required.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging`
