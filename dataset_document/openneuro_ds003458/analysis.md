# EEG: Three Armed Bandit Gambling Task

**Dataset**: `openneuro_ds003458` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003458
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 66 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Participants performed a three-armed bandit gambling task with oscillating reinforcement probabilities to investigate reward processing and reward prediction error signals in EEG. Each trial includes a stimulus presentation (choice between Left, Right, or Up options), a button-press response, and outcome feedback (Win, Loss, or Null). The task is designed to study cortical delta activity reflecting reward prediction error as referenced in the associated publication (DOI: 10.1016/j.neuroimage.2015.02.007). BioSemi system status markers (S4) indicate admin events to be excluded from analysis.

## File Scan Result

> **Kernel SHA256**: `6ad9d6a9fc4dbf8426679203081ba1d10524c5e37df2654ff92805f400126037`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 3671 | event | raw | Stimulus: Left option available |
| `S  2` | 3774 | event | raw | Stimulus: Right option available |
| `S  3` | 3571 | event | raw | Stimulus: Up option available |
| `S  4` | 24 | event | raw | BioSemi system status marker - exclude from analysis |
| `S  5` | 8961 | event | raw | Response event A (primary button-press response) |
| `S  6` | 2055 | event | raw | Response event B (alternative response variant) |
| `S 23` | 1840 | event | raw | Feedback variant C (sub-condition) |
| `S 32` | 1840 | event | raw | Feedback variant D (sub-condition) |
| `S100` | 11040 | event | raw | Feedback Win (reward received) |
| `S113` | 1840 | event | raw | Feedback Loss (no reward) |
| `S131` | 1840 | event | raw | Feedback Null (neutral outcome) |
| `S212` | 1840 | event | raw | Feedback variant A (alternative feedback) |
| `S221` | 1840 | event | raw | Feedback variant B (alternative feedback) |
| `boundary` | 23 | event | raw | Continuous recording segment boundary marker |


### MISC Label Summary
*No misc channels detected in this dataset.*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | Age information not provided in dataset metadata |
| `subject_sex` | complete | Sex information not provided in dataset metadata |
| `device` | missing | Device information not provided in dataset metadata |

## Tasks

### Classical Task 1: Feedback Outcome Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [S100, S113, S131, S212, S221]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---|
| S100 | 0 | Win feedback (reward received) |
| S113 | 1 | Loss feedback (no reward) |
| S131 | 2 | Null/neutral feedback |
| S212 | 3 | Alternative feedback variant A |
| S221 | 4 | Alternative feedback variant B |

- **Evidence**: DOI: 10.1016/j.neuroimage.2015.02.007 (Cortical delta activity reflects reward prediction error; three-armed bandit paradigm with feedback-locked EEG analysis)
- **Kernel Notes**: Events S100 and S113 each have 1840 occurrences (23 subjects × ~80 trials/condition). S131, S212, S221 similarly distributed. S4 (24 occurrences) is BioSemi STATUS admin marker - exclude. Decode event-to-condition mapping from events.tsv; trigger decoding table must be versioned per kernel protocol.

### Normal Task 1: Stimulus Choice Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [S1, S2, S3]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|-------|---|---|
| S1 | 0 | Stimulus: Left option available |
| S2 | 1 | Stimulus: Right option available |
| S3 | 2 | Stimulus: Up option available |

- **Evidence**: OpenNeuro ds003458 paradigm description; epoch alignment recommendation for Stimulus_Choice.
- **Kernel Notes**: S1, S2, S3 each have ~3500-3700 occurrences (138 files × ~27 trials each). Raw event labels in analysis.md ("Stimulus (Left", "Right", "Up)") are truncated fragments - verify full labels from events.tsv. Concatenate fragmented stimulus labels during preprocessing.

### Potential Task 1: Full Trial Segmentation Classification
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, segment_length = 4.0 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|-------|----|---|
| Fixation | 0 | Full trial segment (fixation → stimulus → response → feedback) |

- **Evidence**: Epoch alignment recommendation for Full_Trial segmentation; plausible from paradigm structure (Fixation marks trial onset; 4s window captures stimulus processing, response selection, and outcome processing).
- **Kernel Notes**: Boundary markers (23 total) indicate continuous recording segments requiring concatenation before epoching. Full trial segmentation enables holistic cognitive sequence analysis but has lower temporal resolution for feedback-specific effects.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
