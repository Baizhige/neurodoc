# Mood Manipulation and PST, Experiment 1
**Manual Review**:
## Paradigm

(See existing draft)

## File Scan Result

> **Kernel SHA256**: `20311fff644cb38d02ca2a4ee3141e0b26b865840ae3880ecc1a8a9509306953`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 2063 | event | raw |  |
| `S  2` | 2050 | event | raw |  |
| `S  3` | 931 | event | raw |  |
| `S  4` | 918 | event | raw |  |
| `S  5` | 38 | event | raw |  |
| `S  7` | 48 | event | raw |  |
| `S  8` | 6800 | event | raw |  |
| `S  9` | 5149 | event | raw |  |
| `S 12` | 200 | event | raw |  |
| `S 13` | 200 | event | raw |  |
| `S 14` | 200 | event | raw |  |
| `S 15` | 200 | event | raw |  |
| `S 16` | 200 | event | raw |  |
| `S 21` | 200 | event | raw |  |
| `S 23` | 200 | event | raw |  |
| `S 24` | 200 | event | raw |  |
| `S 25` | 200 | event | raw |  |
| `S 26` | 200 | event | raw |  |
| `S 31` | 200 | event | raw |  |
| `S 32` | 200 | event | raw |  |
| `S 34` | 200 | event | raw |  |
| `S 35` | 200 | event | raw |  |
| `S 36` | 200 | event | raw |  |
| `S 41` | 200 | event | raw |  |
| `S 42` | 200 | event | raw |  |
| `S 43` | 200 | event | raw |  |
| `S 45` | 200 | event | raw |  |
| `S 46` | 200 | event | raw |  |
| `S 51` | 200 | event | raw |  |
| `S 52` | 200 | event | raw |  |
| `S 53` | 200 | event | raw |  |
| `S 54` | 200 | event | raw |  |
| `S 56` | 200 | event | raw |  |
| `S 61` | 200 | event | raw |  |
| `S 62` | 200 | event | raw |  |
| `S 63` | 200 | event | raw |  |
| `S 64` | 200 | event | raw |  |
| `S 65` | 200 | event | raw |  |
| `S101` | 4006 | event | raw |  |
| `S102` | 4126 | event | raw |  |
| `S103` | 1851 | event | raw |  |
| `S104` | 1966 | event | raw |  |
| `S105` | 48 | event | raw |  |
| `S116` | 1999 | event | raw |  |
| `S125` | 2000 | event | raw |  |
| `S134` | 2000 | event | raw |  |
| `S143` | 1999 | event | raw |  |
| `S152` | 1999 | event | raw |  |
| `S161` | 2000 | event | raw |  |
| `boundary` | 50 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Feedback-Locked Reward Positivity (RewP) Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 6.0 s, baseline = (-0.2 s, 0 s), target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` aligned to Correct outcome | 0 | Correct response (reward feedback) |
  | `FB` aligned to Incorrect outcome | 1 | Incorrect response (punishment feedback) |
- **Super Meta Notes**: Epochs extracted around feedback onset (`FB`). Labels derived from events.tsv trial outcome column mapping Correct → y=0 and Incorrect → y=1. ROI at electrode FCz for RewP analysis.
- **Evidence**: DOI: 10.1111/psyp.14276 — EEG data from OpenNeuro ds004315 examined RewP ERP (200-350ms at FCz) epoched -2s to 6s relative to feedback onset, comparing correct vs incorrect feedback outcomes across mood induction groups.
- **Kernel Notes**: Extract epochs for all `FB` events. Apply baseline correction -200ms to 0ms. Focus ROI at electrode FCz. Use events.tsv trial outcome column to assign y-labels post-extraction. Class imbalance: Correct (~200) >> Incorrect (~55-85); consider class balancing during classification training.

### Potential Task 2: Short-Window Feedback Outcome Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, baseline = (-0.2 s, 0 s), target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` aligned to Correct outcome | 0 | Correct response |
  | `FB` aligned to Incorrect outcome | 1 | Incorrect response |
- **Super Meta Notes**: Short-window feedback-locked epochs targeting immediate feedback processing and early outcome evaluation. Labels derived from events.tsv Correct/Incorrect outcomes.
- **Evidence**: Paradigm-based plausibility (reinforcement learning task with clear feedback outcomes); epoch alignment recommendation from kernel.
- **Kernel Notes**: Status is admin/system marker—exclude from target events. Class imbalance noted (Correct >> Incorrect); apply class balancing or weighted loss. Shorter window captures early feedback processing components (FRN, P300) distinct from late RewP.

### Potential Task 3: Testing Phase Stimulus-Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, baseline = (-0.5 s, 0 s), target_events = [`TESTING`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `TESTING` with correct outcome sub-label | 0 | Correct response during testing |
  | `TESTING` with incorrect outcome sub-label | 1 | Incorrect response during testing |
- **Super Meta Notes**: TESTING phase contains rich sub-labels in events.tsv (e.g., 'TESTING: Right Press, Correct'); extract trial_type column for detailed outcome and response classification.
- **Evidence**: Paradigm-based plausibility (reinforcement learning testing phase with novel stimulus pairs).
- **Kernel Notes**: Extract epochs for TESTING events. Parse events.tsv trial_type column for sub-label mapping (response direction + outcome). Window captures stimulus presentation, response, and feedback during testing trials.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
