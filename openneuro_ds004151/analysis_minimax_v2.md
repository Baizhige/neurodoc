# Effect of obesity on inhibitory control in preadolescents during stop-signal task. An event-related potentials study

**Dataset**: `openneuro_ds004151` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004151
**Category**: Sensory/Response | **Subjects**: 57 | **Files (Completed)**: 57
**Channels**: 128 | **Sampling Rate**: 500 Hz

## Paradigm

Preadolescents (obese and normal-weight, ages 9-10) performed a stop-signal task to investigate the impact of obesity on reactive inhibitory control using ERPs. Participants respond to a go stimulus (trigger code 1) but must suppress the response when a stop signal follows (trigger code 2). The study tests whether obese children show electrophysiological differences in inhibition-related brain activity (N2, P3 components) compared to normal-weight peers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004151

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | ~14,364 | short | raw | Go trial stimulus onset |
| `2` | ~6,156 | short | raw | Stop-signal trial (inhibition required) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: BMI Regression from Stop-Signal Task EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`1`, `2`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | continuous | Go trial — BMI score (regression target) |
  | `2` | continuous | Stop-signal trial — BMI score (regression target) |
- **Super Meta Notes**: Derived from participant metadata (BMI scores) associated with each trial. Kernel must load participant BMI values and assign them as regression targets to all epochs from that participant. The paper uses beta band (13-30 Hz) wPLI connectivity and network metrics (clustering coefficient, characteristic path length, global efficiency, local efficiency) as super-meta features extracted from each epoch for stepwise multiple linear regression.
- **Evidence**:
  - DOI: `10.1109/OJEMB.2024.3425855` — Demonstrates BMI score prediction using EEG-derived functional network features from Go and Stop-signal trials in the openneuro_ds004151 dataset
- **Kernel Notes**: 
    1. Extract epochs from both event IDs `1` and `2` using tmin=-0.2s, tmax=0.8s
    2. Apply baseline correction [-200, 0] ms
    3. Apply artifact rejection (±120 μV threshold)
    4. Compute beta band (13-30 Hz) wPLI connectivity and network features
    5. Load participant-level BMI scores from dataset metadata
    6. Assign BMI value as regression target to all epochs from each participant
    7. Train stepwise multiple linear regression model to predict BMI from network features
    (replaces Normal Task 2 from original analysis.md)

### Normal Task 1: Raw-meta task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification

- **Kernel Notes**: Exclude admin markers from target labels.


## Data Quality Notes

- Event IDs are numeric (1, 2); decoded from stop-signal paradigm description
- 128-channel EGI cap; verify consistent montage across subjects
- Class imbalance: ~70% go trials vs ~30% stop-signal trials

## References

- **Reference**: `Effect of obesity on inhibitory control in preadolescents during stop-signal task (DOI: 10.1016/j.ijpsycho.2021.04.003)`
