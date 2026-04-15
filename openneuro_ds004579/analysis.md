# Interval Timing Task

**Dataset**: `openneuro_ds004579` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004579
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants performed an interval timing task where they estimated durations of different intervals. BrainVision S-codes (S 1-S 7) encode different timing conditions or interval lengths. Participants produced or reproduced time intervals by button press (R 3). The study investigates neural oscillations and temporal processing mechanisms.

## File Scan Result

> **Kernel SHA256**: `18fc452a26fc4918298b0772b72fb28c0e4751623f656214e9b7e166eb75e8e2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Interval Timing Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = ["S  1", "S  2", "S  3", "S  4", "S  5", "S  6", "S  7"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|--------|
| `S  1` | 0 | Short interval timing condition |
| `S  2` | 0 | Short interval timing condition |
| `S  3` | 0 | Short interval timing condition |
| `S  4` | 1 | Long interval timing condition |
| `S  5` | 1 | Long interval timing condition |
| `S  6` | 1 | Long interval timing condition |
| `S  7` | 1 | Long interval timing condition |

- **Evidence**: DOI: 10.1523/JNEUROSCI.1675-24.2025
- **Kernel Notes**: S 1-S 7 represent 7 timing conditions that can be mapped to binary short/long intervals based on temporal bisection paradigm. S 6 has significantly higher event count (75846) than other conditions - verify for potential duplicate markers. Exclude boundary, S255, and unexpected events (S 49-S 55, S 63) from target_events.

### Potential Task 2: Response-Locked Timing Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 0.5 s (relative to button press), target_events = ["R  3"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|--------|
| `R  3` | 0 | Timing estimation response |

- **Evidence**: Plausible from paradigm - R 3 button presses encode participant timing estimation responses for motor preparation analysis.
- **Kernel Notes**: Response-locked epochs allow analysis of neural activity during motor preparation and execution of temporal judgments. Pre-response window (-1.0s) captures pre-movement preparation related to timing estimation.

### Potential Task 3: Timing Condition Classification (7-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = ["S  1", "S  2", "S  3", "S  4", "S  5", "S  6", "S  7"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|--------|
| `S  1` | 0 | Timing condition 1 |
| `S  2` | 1 | Timing condition 2 |
| `S  3` | 2 | Timing condition 3 |
| `S  4` | 3 | Timing condition 4 |
| `S  5` | 4 | Timing condition 5 |
| `S  6` | 5 | Timing condition 6 |
| `S  7` | 6 | Timing condition 7 |

- **Evidence**: Plausible from paradigm - S 1-S 7 encode 7 distinct timing conditions in interval timing task.
- **Kernel Notes**: High trial count variation across conditions (S 6: 75846 vs S 7: 3397) requires balanced sampling or class weighting. Consider verifying S 49-S 55, S 63 events for potential sub-condition encoding.