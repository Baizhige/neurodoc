# Steer the Ship

**Dataset**: `openneuro_ds004264` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004264
**Category**: Complex Applied | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 31 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

A ship-steering simulation where participants control a rotating arrow to maintain orientation against varying environmental and controller noise using unstable pole-and-cart physics. The task involves continuous manual control with varying noise levels, making it a real-world closed-loop BCI paradigm. EEG was recorded to study cognitive load and motor control under dynamic uncertainty. Participants completed 8 blocks total, including practice trials and catch/baseline blocks.

## File Scan Result

> **Kernel SHA256**: `539d3d2a27a6922e3847639adf4071884ff8f962a1b683cceea5719b3353e5e8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Active Shielding: On` | 21 | admin | raw | Active shielding system status annotation |
| `Stimulus/S  1` | 190 | event | raw | Practice trials, Condition 1 |
| `Stimulus/S  2` | 128 | event | raw | Practice trials, Condition 2 |
| `Stimulus/S  3` | 125 | event | raw | Practice trials, Condition 3 |
| `Stimulus/S  4` | 132 | event | raw | Practice trials, Condition 4 |
| `Stimulus/S 11` | 191 | event | raw | Block 1, Condition 1 |
| `Stimulus/S 12` | 128 | event | raw | Block 1, Condition 2 |
| `Stimulus/S 13` | 125 | event | raw | Block 1, Condition 3 |
| `Stimulus/S 14` | 132 | event | raw | Block 1, Condition 4 |
| `Stimulus/S 21` | 5450 | event | raw | Block 2, Low Noise (Condition 1) |
| `Stimulus/S 22` | 4820 | event | raw | Block 2, Condition 2 |
| `Stimulus/S 23` | 4757 | event | raw | Block 2, Condition 3 |
| `Stimulus/S 24` | 5252 | event | raw | Block 2, Condition 4 |
| `Stimulus/S 31` | 5242 | event | raw | Block 3, Low Noise (Condition 1) |
| `Stimulus/S 32` | 4675 | event | raw | Block 3, Condition 2 |
| `Stimulus/S 33` | 4376 | event | raw | Block 3, Condition 3 |
| `Stimulus/S 34` | 4993 | event | raw | Block 3, Condition 4 |
| `Stimulus/S 42` | 2995 | event | raw | Block 4, Condition 2 |
| `Stimulus/S 44` | 3129 | event | raw | Block 4, Condition 4 |
| `Stimulus/S 52` | 2811 | event | raw | Block 5, Condition 2 |
| `Stimulus/S 54` | 2984 | event | raw | Block 5, Condition 4 |
| `Stimulus/S 61` | 78 | event | raw | Catch Block 6, Condition 1 |
| `Stimulus/S 62` | 96 | event | raw | Catch Block 6, Condition 2 |
| `Stimulus/S 63` | 46 | event | raw | Catch Block 6, Condition 3 |
| `Stimulus/S 64` | 102 | event | raw | Catch Block 6, Condition 4 |
| `Stimulus/S 71` | 113 | event | raw | Catch Block 7, Condition 1 |
| `Stimulus/S 72` | 32 | event | raw | Catch Block 7, Condition 2 |
| `Stimulus/S 73` | 79 | event | raw | Catch Block 7, Condition 3 |
| `Stimulus/S 74` | 30 | event | raw | Catch Block 7, Condition 4 |
| `Stimulus/S 81` | 191 | event | raw | Block 8, Condition 1 |
| `Stimulus/S 82` | 128 | event | raw | Block 8, Condition 2 |
| `Stimulus/S 83` | 125 | event | raw | Block 8, Condition 3 |
| `Stimulus/S 84` | 132 | event | raw | Block 8, Condition 4 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Ship Steering Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [Stimulus/*]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `Stimulus/S  1` | 1 | Block 1, Condition 1 |
| `Stimulus/S  2` | 2 | Block 1, Condition 2 |
| `Stimulus/S  3` | 3 | Block 1, Condition 3 |
| `Stimulus/S  4` | 4 | Block 1, Condition 4 |
| `Stimulus/S 11` | 5 | Block 1, Condition 1 |
| `Stimulus/S 12` | 6 | Block 1, Condition 2 |
| `Stimulus/S 13` | 7 | Block 1, Condition 3 |
| `Stimulus/S 14` | 8 | Block 1, Condition 4 |
| `Stimulus/S 21` | 9 | Block 2, Low Noise |
| `Stimulus/S 22` | 10 | Block 2, Condition 2 |
| `Stimulus/S 23` | 11 | Block 2, Condition 3 |
| `Stimulus/S 24` | 12 | Block 2, Condition 4 |
| `Stimulus/S 31` | 13 | Block 3, Low Noise |
| `Stimulus/S 32` | 14 | Block 3, Condition 2 |
| `Stimulus/S 33` | 15 | Block 3, Condition 3 |
| `Stimulus/S 34` | 16 | Block 3, Condition 4 |
| `Stimulus/S 42` | 17 | Block 4, Condition 2 |
| `Stimulus/S 44` | 18 | Block 4, Condition 4 |
| `Stimulus/S 52` | 19 | Block 5, Condition 2 |
| `Stimulus/S 54` | 20 | Block 5, Condition 4 |
| `Stimulus/S 81` | 21 | Block 8, Condition 1 |
| `Stimulus/S 82` | 22 | Block 8, Condition 2 |
| `Stimulus/S 83` | 23 | Block 8, Condition 3 |
| `Stimulus/S 84` | 24 | Block 8, Condition 4 |

- **Evidence**: OpenNeuro metadata; dataset description indicates ship-steering BCI with varying noise levels. Source: https://openneuro.org/datasets/ds004264 DOI: https://doi.org/10.18112/openneuro.ds004264.v1.1.0
- **Kernel Notes**: 34 distinct Stimulus event IDs with 2-digit suffix pattern (S  1-84). Condition labels derived from events.tsv metadata columns (noise_level, trial_type). High-count events (S 21-34: 4757-5450 trials) represent continuous task markers requiring label filtering. Verify condition mapping against BIDS task events.json if available. Keep events.tsv metadata schema versioned.

### Classical Task 2: Catch/Baseline Trial Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [Stimulus/S 61, Stimulus/S 62, Stimulus/S 63, Stimulus/S 64, Stimulus/S 71, Stimulus/S 72, Stimulus/S 73, Stimulus/S 74]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `Stimulus/S 61` | 1 | Catch Block 6, Condition 1 |
| `Stimulus/S 62` | 2 | Catch Block 6, Condition 2 |
| `Stimulus/S 63` | 3 | Catch Block 6, Condition 3 |
| `Stimulus/S 64` | 4 | Catch Block 6, Condition 4 |
| `Stimulus/S 71` | 5 | Catch Block 7, Condition 1 |
| `Stimulus/S 72` | 6 | Catch Block 7, Condition 2 |
| `Stimulus/S 73` | 7 | Catch Block 7, Condition 3 |
| `Stimulus/S 74` | 8 | Catch Block 7, Condition 4 |

- **Evidence**: OpenNeuro metadata; low trial counts (30-113) indicate separate catch/baseline trial blocks distinct from main task. Source: https://openneuro.org/datasets/ds004264 DOI: https://doi.org/10.18112/openneuro.ds004264.v1.1.0
- **Kernel Notes**: Catch trials use shorter tmax=0.5s for sparse trial analysis. 8 event types with 30-113 trials each vs 4000-5500 for main task blocks. May serve as baseline/calibration conditions. Label parsing from events.tsv metadata required.

### Classical Task 3: Cognitive Load Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [Stimulus/*]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `Stimulus/*` | noise_level (continuous) | Environmental noise level from events.tsv (super meta) |
| `Stimulus/*` | performance_metric (continuous) | Steering performance (error/accuracy) from events.tsv (super meta) |

- **Evidence**: OpenNeuro metadata; paradigm description states study of cognitive load under dynamic uncertainty with varying noise levels. Source: https://openneuro.org/datasets/ds004264 DOI: https://doi.org/10.18112/openneuro.ds004264.v1.1.0
- **Kernel Notes**: Super meta labels (noise_level, performance_metric) not directly in raw event stream—must be loaded from events.tsv columns. Variable trial counts (1473-2373 per subject) across 21 subjects. Regression targets enable cognitive load estimation during closed-loop BCI control.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
