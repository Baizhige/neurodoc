# BCIT Calibration Driving

**Dataset**: `openneuro_ds004118` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004118
**Category**: Complex Applied | **Subjects**: 247 | **Files (Completed)**: 247
**Channels**: 266 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a 15-minute simulated driving calibration task on a straight road, maintaining lane position while correcting for periodic lateral perturbations. This calibration recording is designed to collect a baseline driving EEG profile for each subject to normalize fatigue prediction algorithms used in the broader BCIT driving fatigue study series. It is the largest file count in the BCIT series.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004118

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `3200` | 247 files | short | raw | Speed/driving state marker |
| `3111` | 247 files | short | raw | Perturbation onset |
| `3112` | 247 files | short | raw | Perturbation offset/response |
| `3310` | 247 files | short | raw | Performance metric event |
| `1211` | 247 files | short | raw | Lane correction event |
| `1212` | 247 files | short | raw | Lane correction event |
| `4311` | 246 files | short | raw | Lateral perturbation type 1 |
| `4312` | 246 files | short | raw | Lateral perturbation type 2 |
| `4230` | 246 files | short | raw | Perturbation/direction event |
| `4210` | 239 files | short | raw | Perturbation onset event |
| `4220` | 206 files | short | raw | Perturbation event |
| `1121` | 246 files | short | raw | Driver response event |
| `1122` | 246 files | short | raw | Driver response event |
| `1111` | 246 files | short | raw | Driver response event |
| `1112` | 246 files | short | raw | Driver response event |
| `2621` | 97 files | short | raw | Auditory cue onset |
| `2622` | 97 files | short | raw | Auditory cue offset |
| `4200`-`4612` | 2 files | short | raw | Rare condition events |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Lateral Perturbation Direction (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Largest file count in the BCIT series (247 subjects). 266-channel BioSemi cap - very high memory requirements. Calibration session is shorter (15 min) than fatigue driving sessions.

| Event | y | Meaning |
 |-------|---|------|
 | `4311` | 0 | Lateral perturbation - direction/type 1 |
 | `4312` | 1 | Lateral perturbation - direction/type 2 |

## Data Quality Notes

- 266 channels - very high-density EEG; significant memory requirements for batch processing
- 247 files (subjects) - large cohort; suitable for cross-subject decoding
- Full event code decoding requires BCIT codebook

## References

- _No paper reference available_

## Data Quality Notes

- 266 channels - very high-density EEG; significant memory requirements for batch processing
- 247 files (subjects) - large cohort; suitable for cross-subject decoding
- Full event code decoding requires BCIT codebook

## References

- _No paper reference available_
