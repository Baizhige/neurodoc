# TX14 (Semi-Autonomous Vehicle Monitoring)

**Dataset**: `openneuro_ds004841` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004841
**Category**: Complex Applied | **Subjects**: 11 | **Files (Completed)**: 147 | **Channels**: 70 | **Sampling Rate**: 256 Hz | **Manual Review**: Pending

## Paradigm

Participants monitored a semi-autonomous vehicle system and performed local situational awareness tasks within a simulated environment, with EEG recorded to characterize cognitive states during supervised automation. Event codes are hierarchically structured 7-digit identifiers encoding operational state and task type, with prefixed variants indicating sustained states and substates.

## File Scan Result

> **Kernel SHA256**: `5015c68b45b1447cbd4bfd82f425de14e526a81633ad7792577ebe8369d4d1c7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2120000` | 405 | event | raw | Operational state code (level 2, sublevel 1) |
| `2220001` | 380 | event | raw | Operational state code (level 2, sublevel 2) |
| `2220002` | 382 | event | raw | Operational state code (level 2, sublevel 2) |
| `2230001` | 248 | event | raw | Operational state code (level 2, sublevel 3) |
| `2230002` | 252 | event | raw | Operational state code (level 2, sublevel 3) |
| `2311111` | 157 | event | raw | Task event code (context subtype 1) |
| `2311121` | 158 | event | raw | Task event code (context subtype 2) |
| `2311211` | 72 | event | raw | Task event code (context subtype 1) |
| `2311221` | 72 | event | raw | Task event code (context subtype 2) |
| `2311311` | 73 | event | raw | Task event code (context subtype 1) |
| `2311321` | 70 | event | raw | Task event code (context subtype 2) |
| `2311411` | 68 | event | raw | Task event code (context subtype 1) |
| `2311421` | 72 | event | raw | Task event code (context subtype 2) |
| `2312111` | 216 | event | raw | Task event code (context subtype 1) |
| `2312121` | 168 | event | raw | Task event code (context subtype 2) |
| `2312211` | 44 | event | raw | Task event code (context subtype 1) |
| `2312221` | 124 | event | raw | Task event code (context subtype 2) |
| `2312311` | 38 | event | raw | Task event code (context subtype 1) |
| `2312321` | 37 | event | raw | Task event code (context subtype 2) |
| `2312411` | 37 | event | raw | Task event code (context subtype 1) |
| `2312421` | 74 | event | raw | Task event code (context subtype 2) |
| `2313111` | 211 | event | raw | Task event code (context subtype 1) |
| `2313121` | 131 | event | raw | Task event code (context subtype 2) |
| `2313211` | 120 | event | raw | Task event code (context subtype 1) |
| `2313311` | 108 | event | raw | Task event code (context subtype 1) |
| `2313321` | 68 | event | raw | Task event code (context subtype 2) |
| `2313411` | 73 | event | raw | Task event code (context subtype 1) |
| `2313421` | 73 | event | raw | Task event code (context subtype 2) |
| `2314221` | 112 | event | raw | Task event code (context subtype 2) |
| `2314311` | 6 | event | raw | Task event code (context subtype 1) |
| `2314321` | 144 | event | raw | Task event code (context subtype 2) |
| `2314411` | 116 | event | raw | Task event code (context subtype 1) |
| `2314421` | 35 | event | raw | Task event code (context subtype 2) |
| `3110001` | 11 | event | raw | Driver intervention event (type 1) |
| `3110002` | 147 | event | raw | Driver intervention event (type 2) |
| `4131112` | 140 | event | raw | Perception event (scenario subtype 1, context 1) |
| `4131122` | 133 | event | raw | Perception event (scenario subtype 1, context 2) |
| `4131212` | 68 | event | raw | Perception event (scenario subtype 2, context 1) |
| `4131222` | 55 | event | raw | Perception event (scenario subtype 2, context 2) |
| `4131312` | 24 | event | raw | Perception event (scenario subtype 3, context 1) |
| `4131322` | 26 | event | raw | Perception event (scenario subtype 3, context 2) |
| `4131412` | 45 | event | raw | Perception event (scenario subtype 4, context 1) |
| `4131422` | 58 | event | raw | Perception event (scenario subtype 4, context 2) |
| `4132112` | 191 | event | raw | Perception event (scenario subtype 1, context 1) |
| `4132122` | 162 | event | raw | Perception event (scenario subtype 1, context 2) |
| `4132212` | 39 | event | raw | Perception event (scenario subtype 2, context 1) |
| `4132222` | 116 | event | raw | Perception event (scenario subtype 2, context 2) |
| `4132312` | 36 | event | raw | Perception event (scenario subtype 3, context 1) |
| `4132322` | 34 | event | raw | Perception event (scenario subtype 3, context 2) |
| `4132412` | 21 | event | raw | Perception event (scenario subtype 4, context 1) |
| `4132422` | 70 | event | raw | Perception event (scenario subtype 4, context 2) |
| `4133112` | 117 | event | raw | Perception event (scenario subtype 1, context 1) |
| `4133122` | 41 | event | raw | Perception event (scenario subtype 1, context 2) |
| `4133212` | 84 | event | raw | Perception event (scenario subtype 2, context 1) |
| `4133312` | 64 | event | raw | Perception event (scenario subtype 3, context 1) |
| `4133322` | 32 | event | raw | Perception event (scenario subtype 3, context 2) |
| `4133412` | 54 | event | raw | Perception event (scenario subtype 4, context 1) |
| `4133422` | 52 | event | raw | Perception event (scenario subtype 4, context 2) |
| `4134222` | 95 | event | raw | Perception event (scenario subtype 2, context 2) |
| `4134312` | 11 | event | raw | Perception event (scenario subtype 3, context 1) |
| `4134322` | 89 | event | raw | Perception event (scenario subtype 3, context 2) |
| `4134412` | 109 | event | raw | Perception event (scenario subtype 4, context 1) |
| `4134422` | 28 | event | raw | Perception event (scenario subtype 4, context 2) |
| `4141112` | 5 | event | raw | Driver monitoring event (scenario subtype 1, context 2) |
| `4141122` | 32 | event | raw | Driver monitoring event (scenario subtype 1, context 2) |
| `4141212` | 39 | event | raw | Driver monitoring event (scenario subtype 2, context 1) |
| `4141222` | 1 | event | raw | Driver monitoring event (scenario subtype 2, context 2) |
| `4141312` | 34 | event | raw | Driver monitoring event (scenario subtype 3, context 1) |
| `4141322` | 26 | event | raw | Driver monitoring event (scenario subtype 3, context 2) |
| `4141412` | 1 | event | raw | Driver monitoring event (scenario subtype 4, context 1) |
| `4141422` | 2 | event | raw | Driver monitoring event (scenario subtype 4, context 2) |
| `4141512` | 4 | event | raw | Driver monitoring event (scenario subtype 5, context 1) |
| `4141522` | 1 | event | raw | Driver monitoring event (scenario subtype 5, context 2) |
| `4142112` | 21 | event | raw | Driver monitoring event (scenario subtype 1, context 1) |
| `4142122` | 11 | event | raw | Driver monitoring event (scenario subtype 1, context 2) |
| `4142212` | 2 | event | raw | Driver monitoring event (scenario subtype 2, context 1) |
| `4142222` | 4 | event | raw | Driver monitoring event (scenario subtype 2, context 2) |
| `4142312` | 8 | event | raw | Driver monitoring event (scenario subtype 3, context 1) |
| `4142322` | 4 | event | raw | Driver monitoring event (scenario subtype 3, context 2) |
| `4142412` | 4 | event | raw | Driver monitoring event (scenario subtype 4, context 1) |
| `4142422` | 3 | event | raw | Driver monitoring event (scenario subtype 4, context 2) |
| `4142512` | 1 | event | raw | Driver monitoring event (scenario subtype 5, context 1) |
| `4142522` | 1 | event | raw | Driver monitoring event (scenario subtype 5, context 2) |
| `4143112` | 73 | event | raw | Driver monitoring event (scenario subtype 1, context 1) |
| `4143122` | 78 | event | raw | Driver monitoring event (scenario subtype 1, context 2) |
| `4143212` | 9 | event | raw | Driver monitoring event (scenario subtype 2, context 1) |
| `4143222` | 14 | event | raw | Driver monitoring event (scenario subtype 2, context 2) |
| `4143312` | 48 | event | raw | Driver monitoring event (scenario subtype 3, context 1) |
| `4143322` | 17 | event | raw | Driver monitoring event (scenario subtype 3, context 2) |
| `4143412` | 5 | event | raw | Driver monitoring event (scenario subtype 4, context 1) |
| `4143422` | 1 | event | raw | Driver monitoring event (scenario subtype 4, context 2) |
| `4144212` | 8 | event | raw | Driver monitoring event (scenario subtype 2, context 1) |
| `4144222` | 3 | event | raw | Driver monitoring event (scenario subtype 2, context 2) |
| `4144312` | 46 | event | raw | Driver monitoring event (scenario subtype 3, context 1) |
| `4144322` | 2 | event | raw | Driver monitoring event (scenario subtype 3, context 2) |
| `4144412` | 23 | event | raw | Driver monitoring event (scenario subtype 4, context 1) |
| `4144422` | 13 | event | raw | Driver monitoring event (scenario subtype 4, context 2) |
| `4145112` | 6 | event | raw | Driver monitoring event (scenario subtype 1, context 1) |
| `4145122` | 15 | event | raw | Driver monitoring event (scenario subtype 1, context 2) |
| `4145212` | 4 | event | raw | Driver monitoring event (scenario subtype 2, context 1) |
| `4145222` | 1 | event | raw | Driver monitoring event (scenario subtype 2, context 2) |
| `4145312` | 18 | event | raw | Driver monitoring event (scenario subtype 3, context 1) |
| `4145322` | 1 | event | raw | Driver monitoring event (scenario subtype 3, context 2) |
| `4145412` | 17 | event | raw | Driver monitoring event (scenario subtype 4, context 1) |
| `4145422` | 3 | event | raw | Driver monitoring event (scenario subtype 4, context 2) |
| `4145512` | 2 | event | raw | Driver monitoring event (scenario subtype 5, context 1) |
| `4145522` | 2 | event | raw | Driver monitoring event (scenario subtype 5, context 2) |
| `4151112` | 7 | event | raw | Monitoring event (scenario subtype 1, context 1) |
| `4151122` | 1 | event | raw | Monitoring event (scenario subtype 1, context 2) |
| `4151312` | 1 | event | raw | Monitoring event (scenario subtype 3, context 1) |
| `4151412` | 1 | event | raw | Monitoring event (scenario subtype 4, context 1) |
| `4151512` | 1 | event | raw | Monitoring event (scenario subtype 5, context 1) |
| `4152112` | 2 | event | raw | Monitoring event (scenario subtype 1, context 1) |
| `4152122` | 2 | event | raw | Monitoring event (scenario subtype 1, context 2) |
| `4152222` | 1 | event | raw | Monitoring event (scenario subtype 2, context 2) |
| `4153112` | 1 | event | raw | Monitoring event (scenario subtype 1, context 1) |
| `4153312` | 1 | event | raw | Monitoring event (scenario subtype 3, context 1) |
| `4154222` | 2 | event | raw | Monitoring event (scenario subtype 2, context 2) |
| `4154312` | 1 | event | raw | Monitoring event (scenario subtype 3, context 1) |
| `4154322` | 1 | event | raw | Monitoring event (scenario subtype 3, context 2) |
| `4154512` | 1 | event | raw | Monitoring event (scenario subtype 5, context 1) |
| `4155422` | 1 | event | raw | Monitoring event (scenario subtype 4, context 2) |
| `4155512` | 2 | event | raw | Monitoring event (scenario subtype 5, context 1) |
| `4210001` | 555 | event | raw | System state event (mode 1) |
| `4210002` | 509 | event | raw | System state event (mode 2) |
| `4300200` | 631 | event | raw | State transition event (demand level 2) |
| `4300300` | 575 | event | raw | State transition event (demand level 3) |
| `4300400` | 526 | event | raw | State transition event (demand level 4) |
| `4300500` | 16 | event | raw | State transition event (demand level 5) |
| `4301000` | 733 | event | raw | State transition event (checkpoint marker) |
| `4302000` | 789 | event | raw | State transition event (scenario change) |
| `4303000` | 712 | event | raw | State transition event (complex scenario) |
| `4304000` | 464 | event | raw | State transition event (high cognitive load) |
| `4305000` | 74 | event | raw | State transition event (critical event) |
| `state_1110001` | 918 | event | raw | Sustained operational state (low automation mode 1) |
| `state_1110002` | 918 | event | raw | Sustained operational state (low automation mode 2) |
| `state_2110000` | 2659 | event | raw | Sustained operational state (partial automation) |
| `state_2210001` | 12823 | event | raw | Sustained operational state (conditional automation mode 1) |
| `state_2210002` | 12199 | event | raw | Sustained operational state (conditional automation mode 2) |
| `state_4100001` | 2623 | event | raw | Sustained system state (driver monitoring) |
| `state_4310000` | 2623 | event | raw | Sustained system state (supervised autonomy) |
| `state_4320000` | 2633 | event | raw | Sustained system state (active monitoring) |
| `substate_4300010` | 1425 | event | raw | Fine-grained substate (monitoring level 1) |
| `substate_4300020` | 1270 | event | raw | Fine-grained substate (monitoring level 2) |
| `substate_4300100` | 1056 | event | raw | Fine-grained substate (monitoring level 3) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Operational State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = N/A, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|-----------|
 | `state_1110001` | 0 | Operational state (low automation) |
 | `state_1110002` | 1 | Operational state (low automation) |
 | `state_2110000` | 2 | Operational state (partial automation) |
 | `state_2210001` | 3 | Operational state (conditional automation) |
 | `state_2210002` | 4 | Operational state (conditional automation) |
 | `state_4100001` | 5 | System state (driver monitoring) |
 | `state_4310000` | 6 | System state (supervised autonomy) |
 | `state_4320000` | 7 | System state (active monitoring) |

- **Evidence**: Dataset README and OpenNeuro metadata (n=11, task='Drive On Mission') — https://openneuro.org/datasets/ds004841 DOI: https://doi.org/10.18112/openneuro.ds004841.v1.0.1
- **Kernel Notes**: 7-digit hierarchical codes require decode table for semantic mapping. States encode automation level (first digit) and operational mode (remaining digits). Large count range (918–12823) indicates heavily unbalanced classes. Small subject pool (n=11) — recommend leave-one-subject-out cross-validation. Type 1 kernel extracts raw state labels from state_ prefixed events.

### Normal Task 2: Substate Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.0, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|--------|
 | `substate_4300010` | 0 | Substate (fine-grained monitoring level 1) |
 | `substate_4300020` | 1 | Substate (fine-grained monitoring level 2) |
 | `substate_4300100` | 2 | Substate (fine-grained monitoring level 3) |

- **Evidence**: Dataset README — substate events (counts 1056–1425) represent finer vehicle operational granularity within parent state 4300000.
- **Kernel Notes**: Substates capture cognitive engagement variations within a single operational state. Fixed 4s segmentation ensures balanced epoch count across classes. Type 1 kernel extracts substate labels from substate_ prefixed events. Combined with Normal Task 1 for hierarchical classification.

### Potential Task 1: State Transition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = N/A, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|--------|
 | `4300200` | 0 | State transition (low→medium demand) |
 | `4300300` | 1 | State transition (medium demand) |
 | `4300400` | 2 | State transition (medium→high demand) |
 | `4301000` | 3 | State transition (monitoring checkpoint) |
 | `4302000` | 4 | State transition (scenario change) |
 | `4303000` | 5 | State transition (complex scenario) |
 | `4304000` | 6 | State transition (high cognitive load) |
 | `4305000` | 7 | State transition (critical event) |

- **Evidence**: Plausible from paradigm — 7-digit codes with format 43XXXXX encode state transitions requiring cognitive re-engagement. High event counts (464–789) support statistical classification.
- **Kernel Notes**: Captures event-related neural dynamics during vehicle state transitions. Short epoch window (-0.2 to 1.0 s) aligns with transient cognitive responses. Requires decode table for semantic state mapping. Type 1 kernel extracts raw transition labels from 43XXXXX events.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
