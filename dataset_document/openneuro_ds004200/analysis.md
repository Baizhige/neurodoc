# Temporal Scaling

**Dataset**: `openneuro_ds004200` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004200
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 37 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants learned to produce and judge short, medium, and long temporal intervals through interleaved production and perception tasks with visual feedback. Trigger codes encode condition combinations: tens digit indicates task type (1x=production, 2x=perception, 3x=judgment, 4x-6x=additional conditions), and units digit indicates subcondition or phase. The study investigates how humans scale temporal interval representations. DOI: 10.1073/pnas.2214638119

## File Scan Result

> **Kernel SHA256**: `ada696a32bc7d9b051ca9f489674553d553e60ea1d229421516cac83235bf9c6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `11` | 1180 | event | raw | Production task, phase 1 |
| `13` | 1180 | event | raw | Production task, phase 3 |
| `16` | 18 | event | raw | Production task, phase 6 (rare/practice) |
| `17` | 623 | event | raw | Production task, feedback/response |
| `18` | 310 | event | raw | Production task, supplementary |
| `19` | 229 | event | raw | Production task, supplementary |
| `2` | 3542 | admin | raw | Block/session boundary marker |
| `21` | 1180 | event | raw | Perception task, phase 1 |
| `22` | 1180 | event | raw | Perception task, phase 2 |
| `23` | 1180 | event | raw | Perception task, phase 3 |
| `26` | 19 | event | raw | Perception task, phase 6 (rare) |
| `31` | 1140 | event | raw | Judgment task, phase 1 |
| `32` | 1140 | event | raw | Judgment task, phase 2 |
| `33` | 1180 | event | raw | Judgment task, phase 3 |
| `36` | 28 | event | raw | Judgment task, phase 6 |
| `37` | 57 | event | raw | Judgment task, phase 7 |
| `38` | 534 | event | raw | Judgment task, phase 8 |
| `39` | 135 | event | raw | Judgment task, phase 9 |
| `41` | 1020 | event | raw | Condition 4, phase 1 |
| `42` | 160 | event | raw | Condition 4, phase 2 |
| `43` | 100 | event | raw | Condition 4, phase 3 |
| `44` | 160 | event | raw | Condition 4, phase 4 |
| `45` | 1020 | event | raw | Condition 4, phase 5 |
| `46` | 247 | event | raw | Condition 4, phase 6 |
| `47` | 833 | event | raw | Condition 4, feedback/response |
| `51` | 280 | event | raw | Condition 5, phase 1 |
| `52` | 1060 | event | raw | Condition 5, phase 2 |
| `53` | 1120 | event | raw | Condition 5, phase 3 |
| `54` | 1020 | event | raw | Condition 5, phase 4 |
| `55` | 160 | event | raw | Condition 5, phase 5 |
| `56` | 28 | event | raw | Condition 5, phase 6 |
| `57` | 114 | event | raw | Condition 5, feedback/response |
| `61` | 1020 | event | raw | Condition 6, phase 1 |
| `62` | 1080 | event | raw | Condition 6, phase 2 |
| `63` | 1080 | event | raw | Condition 6, phase 3 |
| `64` | 280 | event | raw | Condition 6, phase 4 |
| `65` | 1060 | event | raw | Condition 6, phase 5 |
| `66` | 270 | event | raw | Condition 6, phase 6 |
| `67` | 783 | event | raw | Condition 6, feedback/response |
| `Cond1_Feedback` | 462 | event | raw | Production task feedback (annotation) |
| `Cond1_Phase1` | 550 | event | raw | Production task phase 1 (annotation) |
| `Cond1_Phase2` | 398 | event | raw | Production task phase 2 (annotation) |
| `Cond1_Phase3` | 293 | event | raw | Production task phase 3 (annotation) |
| `Cond2_Feedback` | 1120 | event | raw | Perception task feedback (annotation) |
| `Cond2_Phase1` | 1127 | event | raw | Perception task phase 1 (annotation) |
| `Cond2_Phase2` | 1148 | event | raw | Perception task phase 2 (annotation) |
| `Cond2_Phase3` | 1172 | event | raw | Perception task phase 3 (annotation) |
| `Cond3_Feedback` | 1165 | event | raw | Judgment task feedback (annotation) |
| `Cond3_Phase1` | 1100 | event | raw | Judgment task phase 1 (annotation) |
| `Cond3_Phase2` | 442 | event | raw | Judgment task phase 2 (annotation) |
| `Cond3_Phase3` | 936 | event | raw | Judgment task phase 3 (annotation) |
| `Cond4_Phase1` | 61 | event | raw | Condition 4 phase 1 (annotation) |
| `Cond4_Phase2` | 41 | event | raw | Condition 4 phase 2 (annotation) |
| `admin: marker-2` | 1180 | admin | super | Block boundary (pre-processed annotation) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Temporal Interval Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [Cond1_Phase1, Cond1_Phase2, Cond1_Phase3, Cond2_Phase1, Cond2_Phase2, Cond2_Phase3, Cond3_Phase1, Cond3_Phase2, Cond3_Phase3]
- **Label Route**: `event`
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | Cond1_Phase1 | 0 | Cond 1 phase 1 (short interval production) |
 | Cond1_Phase2 | 1 | Cond 1 phase 2 (medium interval production) |
 | Cond1_Phase3 | 2 | Cond 1 phase 3 (long interval production) |
 | Cond2_Phase1 | 3 | Cond 2 phase 1 (short interval perception) |
 | Cond2_Phase2 | 4 | Cond 2 phase 2 (medium interval perception) |
 | Cond2_Phase3 | 5 | Cond 2 phase 3 (long interval perception) |
 | Cond3_Phase1 | 6 | Cond 3 phase 1 (short interval judgment) |
 | Cond3_Phase2 | 7 | Cond 3 phase 2 (medium interval judgment) |
 | Cond3_Phase3 | 8 | Cond 3 phase 3 (long interval judgment) |

- **Evidence**: 10.1073/pnas.2214638119 | DOI: https://doi.org/10.1073/pnas.2214638119
- **Kernel Notes**: Use pre-processed Cond*_Phase annotation events as primary label source. Exclude `admin:marker-2` (3542 counts = block boundaries) and raw numeric codes (11, 12, 13, 21, 22, 23, 31, 32, 33, etc.) due to count inconsistencies with per-subject design. Nine-class paradigm directly maps to temporal scaling phenomenon (short/medium/long intervals × production/perception/judgment tasks). Alignment: onset with baseline correction.

### Normal Task 1: Production vs Perception Task Differentiation (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [Cond1_Phase1, Cond1_Phase2, Cond1_Phase3, Cond2_Phase1, Cond2_Phase2, Cond2_Phase3]
- **Label Route**: `event`
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | Cond1_Phase1 | 0 | Production task |
 | Cond1_Phase2 | 0 | Production task |
 | Cond1_Phase3 | 0 | Production task |
 | Cond2_Phase1 | 1 | Perception task |
 | Cond2_Phase2 | 1 | Perception task |
 | Cond2_Phase3 | 1 | Perception task |

- **Evidence**: 10.1073/pnas.2214638119 (paradigm support); OpenNeuro dataset readme
- **Kernel Notes**: Collapses across interval lengths to test task-type differentiation. Paradigm explicitly describes interleaved production and perception tasks. The tens digit encoding (1x=production, 2x=perception) supports this binary distinction.

### Potential Task 1: Feedback-Related Potential Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, overlap = null, target_events = [Cond1_Feedback, Cond2_Feedback, Cond3_Feedback]
- **Label Route**: `event`
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | Cond1_Feedback | 0 | Feedback following production |
 | Cond2_Feedback | 1 | Feedback following perception |
 | Cond3_Feedback | 2 | Feedback following judgment |

- **Evidence**: Paradigm description (visual feedback component); partial support from 10.1073/pnas.2214638119
- **Kernel Notes**: Shorter epoch window (0.8s) appropriate for feedback processing neural correlates. Feedback events exist in pre-processed annotations but may require validation against paradigm description. May capture feedback-locked ERPs differentiated by underlying task type.

### Potential Task 2: Temporal Interval Length Classification (Short/Medium/Long)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [Cond1_Phase1, Cond1_Phase2, Cond1_Phase3]
- **Label Route**: `event`
- **Target Definition**:

 | Event | y | Meaning |
 |-------|---|---------|
 | Cond1_Phase1 | 0 | Short interval (production) |
 | Cond1_Phase2 | 1 | Medium interval (production) |
 | Cond1_Phase3 | 2 | Long interval (production) |

- **Evidence**: 10.1073/pnas.2214638119 (paradigm support)
- **Kernel Notes**: Core temporal scaling task within production paradigm. Three-class classification of interval duration scaling. Can be extended to Cond2 and Cond3 phases separately. Paradigm explicitly states participants learned to produce/judge short, medium, and long intervals.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
