# BCIT Auditory Cueing

**Dataset**: `openneuro_ds004105` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004105
**Category**: Complex Applied | **Subjects**: 34 | **Files (Completed)**: 34
**Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed a long-duration simulated driving task involving lane maintenance with periodic lateral vehicle perturbations, while receiving auditory cues at varying intervals. EEG biomarkers of fatigue were investigated as performance and alertness declined over the driving session. The study is part of the BCIT (Brain Computer Interface and Technology) driving fatigue dataset series.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4210` | 34 files | short | raw | Driving event code 4210 (lateral perturbation onset) |
| `4220` | 34 files | short | raw | Driving event code 4220 |
| `4230` | 34 files | short | raw | Driving event code 4230 |
| `4311` | 34 files | short | raw | Lane deviation/correction event |
| `4312` | 34 files | short | raw | Lane deviation/correction event |
| `3200` | 34 files | short | raw | Speed/control event |
| `3111` | 34 files | short | raw | Perturbation/response event |
| `3112` | 34 files | short | raw | Perturbation/response event |
| `3310` | 34 files | short | raw | Performance metric event |
| `1211` | 34 files | short | raw | Auditory cue event |
| `1212` | 34 files | short | raw | Auditory cue event |
| `2621` | 34 files | short | raw | Behavioral response event |
| `2622` | 34 files | short | raw | Behavioral response event |
| `1111`-`1322` | 17 files | short | raw | Condition-specific events (half of subjects) |
| `4411` | 1 file | short | raw | Rare event |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### Info

- Dataset scanned: openneuro_ds004105
- File count: 34 completed
- Sampling rate: 1024 Hz
- Channel count: 74

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds004105 DOI: https://doi.org/10.1016/j.neuroimage.2017.02.057


### Normal Task 1: Lateral Perturbation Response (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Full BCIT event code decoding requires the dataset codebook. Part of the BCIT driving fatigue series alongside ds004106, ds004118, ds004119, ds004120, ds004121, ds004122, ds004123. Auditory cueing conditions are the primary manipulation.

| Event | y | Meaning |
|-------|---|------|
| `4311` | 0 | Lane perturbation - direction/type 1 |
| `4312` | 1 | Lane perturbation - direction/type 2 |

## Data Quality Notes

- Numerical event codes require codebook from BCIT documentation for full decoding
- 74-channel BioSemi ActiveTwo; high-density cap with 1024 Hz sampling
- Part of a larger BCIT driving series - consider combining with related datasets

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004105