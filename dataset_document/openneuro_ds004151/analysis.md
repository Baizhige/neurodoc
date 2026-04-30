# Effect of obesity on inhibitory control in preadolescents during stop-signal task. An event-related potentials study

**Dataset**: `openneuro_ds004151` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004151
**Category**: Sensory/Response | **Subjects**: 57 | **Files (Completed)**: 57 | **Channels**: 128 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Preadolescents (obese and normal-weight, ages 9-10) performed a stop-signal task to investigate the impact of obesity on reactive inhibitory control using ERPs. Participants respond to a go tone stimulus (Ton-, trigger code) but must suppress the response when a stop signal tone follows (Ton+, trigger code). The study tests whether obese children show electrophysiological differences in inhibition-related brain activity (N2, P3 components) compared to normal-weight peers. The 128-channel EGI HydroCel Geodesic Sensor Net was used for EEG acquisition at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `192766816e023e07da05021619601b5aa6434d8f43ad7ecdcd7453d8dcbefb23`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CELL` | 232 | event | raw | Cell marker (trial block indicator) |
| `Fix+` | 20520 | event | raw | Fixation onset marker |
| `SESS` | 58 | event | raw | Session marker |
| `TRSP` | 20520 | event | raw | Transport/break marker |
| `Ton+` | 6156 | event | raw | Stop-signal tone (inhibition required) |
| `Ton-` | 14364 | event | raw | Go tone (response required) |
| `bgin` | 20520 | event | raw | Begin marker |
| `break cnt` | 230 | event | raw | Break counter |
| `resp` | 16144 | event | raw | Response recorded |
| `sync` | 230 | event | raw | Sync marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: BMI Regression from Stop-Signal Task EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Ton-`, `Ton+`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Ton-` | continuous | Go trial — BMI score (regression target) |
  | `Ton+` | continuous | Stop-signal trial — BMI score (regression target) |
- **Evidence**:
  - DOI: `10.1109/OJEMB.2024.3425855` — Demonstrates BMI score prediction using EEG-derived functional network features from Go and Stop-signal trials in the openneuro_ds004151 dataset
- **Kernel Notes**:
    1. Extract epochs from both event IDs `Ton-` (14364 events, Go trials) and `Ton+` (6156 events, Stop-signal trials) using tmin=-0.2s, tmax=0.8s
    2. Apply baseline correction [-200, 0] ms
    3. Apply artifact rejection (±120 μV threshold)
    4. Compute beta band (13-30 Hz) wPLI connectivity and network features (clustering coefficient, characteristic path length, global efficiency, local efficiency)
    5. Load participant-level BMI scores from dataset metadata
    6. Assign BMI value as regression target to all epochs from each participant
    7. Train stepwise multiple linear regression model to predict BMI from network features

### Classical Task 2: BMI Group Classification from Stop-Signal Task EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Ton-`, `Ton+`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Ton-` | categorical | Go trial — BMI group (obese=1 / normal-weight=0) |
  | `Ton+` | categorical | Stop-signal trial — BMI group (obese=1 / normal-weight=0) |
- **Evidence**:
  - DOI: `10.1016/j.ijpsycho.2021.04.003` — Study design compares 27 obese preadolescents (mean BMI=25.9) vs 29 normal-weight peers (mean BMI=17.5) during stop-signal task; Go trials (Ton-) and Stop-signal trials (Ton+) analyzed for N200, P300a, P300b ERP components with group as independent variable
- **Kernel Notes**:
    1. Extract epochs from event IDs `Ton-` (Go trials) and `Ton+` (Stop-signal trials) using tmin=-0.2s, tmax=0.8s
    2. Apply baseline correction [-200, 0] ms
    3. Load participant BMI values and derive binary group labels using standard pediatric BMI percentile thresholds
    4. Assign group label to all epochs from each participant
    5. Class imbalance: ~70% go vs ~30% stop trials; consider stratified sampling during model training
    6. Verify participant group labels exist in dataset metadata or derive from BMI values stored in misc route

### Potential Task 1: Go vs Stop Trial Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`Ton-`, `Ton+`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Ton-` | categorical | Go trial — response required |
  | `Ton+` | categorical | Stop-signal trial — inhibition required |
- **Evidence**: Plausible from paradigm structure alone; stop-signal paradigm inherently defines two distinct trial types with different cognitive demands (response execution vs response inhibition)
- **Kernel Notes**:
    1. Extract epochs from both event IDs `Ton-` (14364 events) and `Ton+` (6156 events)
    2. Use event type as binary classification target (raw meta level)
    3. Class imbalance: ~70% go (Ton-) vs ~30% stop (Ton+) trials
    4. Useful as a sanity check task before applying to BMI-related analyses

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
