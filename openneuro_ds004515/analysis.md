# EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants

**Dataset**: `openneuro_ds004515` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004515
**Category**: High-level Mental | **Subjects**: 42 | **Files (Completed)**: 42 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants (light and heavy drinkers) performed a reinforcement learning task involving alcohol-related and neutral imagery cues. On each trial, participants chose between left and right buttons in response to cues, with feedback (FB) indicating correct/incorrect responses. The study investigates how reward learning interacts with alcohol cue reactivity across drinking groups.

## File Scan Result

> **Kernel SHA256**: `62eab5a0a382de5ab460576ee08d4e846871d2f27852e88e4fb82ccfaa2d87c2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | 33945 | event | raw | Stimulus cue onset for imagery presentation |
| `Response` | 1373 | event | raw | Button press response |
| `S 10` | 498 | event | raw | Reward feedback (green screen) |
| `S 11` | 240 | event | raw | Punishment feedback (red screen) |
| `S 12` | 240 | event | raw | Reward feedback variant |
| `S 13` | 240 | event | raw | Punishment feedback variant |
| `S 14` | 240 | event | raw | Feedback marker variant |
| `S 20` | 462 | event | raw | Cue type marker |
| `S101` | 318 | event | raw | Feedback marker |
| `S102` | 162 | event | raw | Feedback marker |
| `S103` | 312 | event | raw | Feedback marker |
| `S104` | 168 | event | raw | Feedback marker |
| `S110` | 136 | event | raw | Cue type marker |
| `S111` | 126 | event | raw | Cue type marker |
| `S120` | 147 | event | raw | Cue type marker |
| `S200` | 480 | event | raw | Control group marker (light drinkers) |
| `S201` | 480 | event | raw | Hazardous drinkers group marker (heavy drinkers) |
| `boundary` | 54 | event | raw | Data segmentation boundary |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Reward vs Punishment Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S 10`, `S 11`, `S 12`, `S 13`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `S 10` | 1 | Reward feedback (green screen) |
  | `S 11` | 0 | Punishment feedback (red screen) |
  | `S 12` | 1 | Reward feedback variant |
  | `S 13` | 0 | Punishment feedback variant |
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — EEG classification of reward vs punishment feedback detection using RewP and delta power in a reinforcement learning task; reports differential feedback-related potentials between reward (green) and punishment (red) conditions
- **Kernel Notes**: Actual feedback markers are S10/S11/S12/S13 BrainVision trigger codes—not "FB" as described in original paradigm. S10 (318 events) and S12 (312 events) represent reward feedback; S11 (162 events) and S13 (240 events) represent punishment feedback. Verify exact color mapping from dataset documentation. Epoch window captures the RewP component (-500ms to +1000ms around feedback onset).

### Classical Task 2: Affective Imagery Type Classification (Alcohol vs Puppy)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`CUE`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `CUE` | 0 | Neutral imagery (puppy) |
  | `CUE` | 1 | Alcohol-related imagery |
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — Classification of affective imagery type (puppy vs alcohol) showing differential RewP and delta power effects across hazardous drinkers and controls
- **Kernel Notes**: CUE events (33,945 total, ~808/subject) are the primary stimulus markers. Requires cross-referencing events.tsv columns to map CUE → imagery type (puppy=0, alcohol=1). High event count suggests complex trial structure or multiple cue subtypes that must be resolved via events.tsv column annotations.

### Classical Task 3: Drinking Group Classification (Hazardous vs Control)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S 200`, `S 201`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `S 200` | 0 | Control group (light drinkers) |
  | `S 201` | 1 | Hazardous drinkers (heavy drinkers) |
- **Super Meta Notes**: Subject-level group assignment derived from AUDIT scores. S200/S201 events (480 each, exactly 42×N) encode subject group markers rather than trial-by-trial feedback. Kernel step: Map subject IDs to group labels using participant demographics file; assign group label to all epochs from each subject.
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — Reports group differences in alcohol-specific RewP correlation with AUDIT scores between hazardous drinkers and controls; AUDIT threshold ≥8 used for hazardous drinker classification
- **Kernel Notes**: Requires loading participant metadata to obtain group assignment. Use AUDIT score threshold (≥8 for hazardous) or pre-defined group labels from dataset. Verify S200/S201 → group mapping against original experiment documentation.

### Potential Task 1: Response Direction Classification (Left vs Right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `Response` | 0 | Left button press |
  | `Response` | 1 | Right button press |
- **Evidence**:
  - Partial: Paradigm describes left/right button choice task; DOI 10.1016/j.pscychresns.2023.111685 confirms binary response structure but does not specify lateralized EEG classification
- **Kernel Notes**: Original paradigm mentions "Left Button" and "Right Button" events, but actual data consolidates these into single "Response" event type (1,373 total, ~32.7/subject). Direction encoding cannot be determined from event labels alone. Inference approaches: (1) Cross-reference events.tsv response columns, (2) Infer from subsequent S-series feedback markers (S10→left choice, S11→right choice), or (3) Request annotation of response direction from original dataset authors.

### Normal Task 1: Feedback-Locked Trial Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S 10`, `S 11`, `S 12`, `S 13`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `S 10` | 1 | Reward trial segment |
  | `S 11` | 0 | Punishment trial segment |
  | `S 12` | 1 | Reward trial segment |
  | `S 13` | 0 | Punishment trial segment |
- **Evidence**:
  - Partial: DOI 10.1016/j.pscychresns.2023.111685 supports feedback-locked analysis; trial structure (CUE→Response→S10/S11) enables complete trial segmentation
- **Kernel Notes**: Use segmentation approach to extract complete trial epochs around feedback markers. Trial structure follows CUE→Response→S10/S11/S12/S13 sequence. Segmentation ensures proper baseline alignment and artifact rejection across full feedback-processing window. Account for 54 boundary events indicating continuous data segmentation breaks requiring epoch rejection.