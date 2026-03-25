# BCIT Baseline Driving

**Dataset**: `openneuro_ds004120` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004120
**Category**: Complex Applied | **Subjects**: 131 | **Files (Completed)**: 131
**Channels**: 266 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a 60-minute simulated driving task involving manual steering and speed control, requiring corrective responses to lateral vehicle perturbations to study fatigue-related EEG biomarkers over an extended session. This baseline driving condition serves as the primary long-duration fatigue paradigm in the BCIT series, without auditory cueing or traffic complexity manipulation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004120

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4311` | 131 files | short | raw | Lateral perturbation - type 1 |
| `4312` | 131 files | short | raw | Lateral perturbation - type 2 |
| `4210` | 130 files | short | raw | Perturbation onset |
| `4220` | 123 files | short | raw | Perturbation event |
| `4230` | 131 files | short | raw | Perturbation/direction event |
| `3200` | 131 files | short | raw | Speed/driving state marker |
| `3111` | 128 files | short | raw | Perturbation onset |
| `3112` | 125 files | short | raw | Perturbation response |
| `3310` | 131 files | short | raw | Performance metric event |
| `1211` | 131 files | short | raw | Lane correction event |
| `1212` | 130 files | short | raw | Lane correction event |
| `1121`-`1122` | 131 files | short | raw | Driver response events |
| `1111`-`1112` | 131 files | short | raw | Driver response events |
| `2621`-`2622` | 28 files | short | raw | Auditory cue events (subset) |
| `2611`-`2612` | 28 files | short | raw | Auditory cue events (subset) |
| `5241`-`5242` | 10 files | short | raw | Rare condition events |
| `4421`-`5232` | 2-5 files | short | raw | Very rare events |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Continuous Driving Performance Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3 s *, overlap = 0.33 * (500-point step at 1024 Hz ≈ 0.49 s, giving ~33% overlap)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---------|
  | lane_deviation (m) | Continuous lateral lane deviation from vehicle state |
  | normalized_accuracy (0-1) | Normalized task accuracy by perceptual difficulty |
  | reaction_time (ms) | Response time to perturbations |
  | button_press_duration (ms) | Duration of driver button press responses |
- **Super Meta Notes**: Behavioral metrics computed from vehicle state (lane deviation) and button responses, then normalized by perceptual difficulty and target probability, then smoothed with 90s centered mean filter to create continuous performance labels aligned to EEG epochs.
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — This 2014 paper uses EEG log power spectra with PCA and linear regression to estimate continuous behavioral performance (lane deviation, accuracy, RT, duration) during a simulated driving task, using 256-channel BioSemi recordings at 1024Hz from 25 participants - an earlier version of the BCIT driving paradigm later released as openneuro_ds004120
- **Kernel Notes**: Extract 750-point epochs (~3s) from continuous EEG, compute log power spectra (possibly with PCA dimensionality reduction), train linear regression model to predict each behavioral metric. Apply 90s centered mean filter to smooth behavioral labels before alignment.

### Normal Task 1: Lateral Perturbation Direction (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 131 subjects with 60-minute sessions - large fatigue dataset. 266-channel BioSemi cap. Primary baseline driving condition for BCIT fatigue series comparison.

| Event | y | Meaning |
|-------|---|------|
| `4311` | 0 | Lateral perturbation - direction/type 1 |
| `4312` | 1 | Lateral perturbation - direction/type 2 |

## Data Quality Notes

- 266 channels - very high-density EEG; significant memory requirements
- 60-minute sessions provide extensive fatigue-related data per subject
- Full event code decoding requires BCIT codebook

## References

- _No paper reference available_
