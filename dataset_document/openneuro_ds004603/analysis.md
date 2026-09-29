# Visual Attribute-Specific Contextual Trajectory Paradigm

**Dataset**: `openneuro_ds004603` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004603
**Category**: Sensory/Response | **Subjects**: 37 | **Files (Completed)**: 37 | **Channels**: 65 | **Sampling Rate**: 1024 Hz | **Manual Review**: Pending

## Paradigm

Participants observed sequences of visual stimuli that either followed or violated an established contextual trajectory in one of three visual attributes - brightness (color), size, or orientation. The paradigm tests predictive coding by contrasting EEG responses to expected (step) stimuli against unexpected violations and a no-trajectory control condition. Each sequence comprised four ordered steps followed by a target or violation stimulus.

## File Scan Result

> **Kernel SHA256**: `4860f906f09be5425b2d5c3349412c1e15a89f3558fb12efd51ecd254971da68`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S    1` | 31368 | event | raw | Sequence step 1 - first ordered stimulus in trajectory |
| `Stimulus/S    2` | 31367 | event | raw | Sequence step 2 |
| `Stimulus/S    3` | 31367 | event | raw | Sequence step 3 |
| `Stimulus/S    4` | 31367 | event | raw | Sequence step 4 - final step before target/violation |
| `Stimulus/S   10` | 4735 | event | raw | Color/brightness trajectory violation |
| `Stimulus/S   20` | 4736 | event | raw | Size trajectory violation |
| `Stimulus/S   30` | 4735 | event | raw | Orientation trajectory violation |
| `Stimulus/S   40` | 14203 | event | raw | No-trajectory control condition |
| `Stimulus/S   50` | 2958 | event | raw | Catch trial requiring button-press response |
| `Stimulus/S  255` | 1 | admin | raw | System initialization trigger (exclude) |
| `Stimulus/S65536` | 39 | event | raw | Unknown event (exclude until identified) |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `Status`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Attribute Violation Detection (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.7 s, baseline = [-0.1, 0.0] s, target_events = [`Stimulus/S   10`, `Stimulus/S   20`, `Stimulus/S   30`, `Stimulus/S   40`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S   40` | 0 | No-trajectory control condition |
  | `Stimulus/S   20` | 1 | Size trajectory violation |
  | `Stimulus/S   30` | 2 | Orientation trajectory violation |
  | `Stimulus/S   10` | 3 | Color/brightness trajectory violation |
- **Evidence**:
  - DOI: `10.1016/j.cortex.2023.08.004` — Linear SVM classifiers decoded expectation violation signals by comparing each violation type (brightness/size/orientation) to physically identical control trials using epoched EEG data segmented -200 to 700 ms post-stimulus with baseline correction -100 to 0 ms. The paper demonstrates that while violations share a common temporal signature, attribute-specific information influences latency.
- **Kernel Notes**: Violations occur at the final sequence position (after step_4). Baseline correction applied -100 to 0 ms pre-stimulus. Exclude `Stimulus/S  255` (system initialization trigger) and `Stimulus/S   50` (catch trials with motor response component). Event codes use MNE-style naming: `Stimulus/S   10`=col_vio, `Stimulus/S   20`=siz_vio, `Stimulus/S   30`=ori_vio, `Stimulus/S   40`=control. The unknown event `Stimulus/S65536` (39 occurrences) should be excluded until identified.

---

### Potential Task 1: Trajectory Prediction Build-up Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, baseline = [-0.1, 0.0] s, target_events = [`Stimulus/S    1`, `Stimulus/S    2`, `Stimulus/S    3`, `Stimulus/S    4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `Stimulus/S    1` | 1 | First step in trajectory (lowest prediction) |
  | `Stimulus/S    2` | 2 | Second step (building prediction) |
  | `Stimulus/S    3` | 3 | Third step (strengthening prediction) |
  | `Stimulus/S    4` | 4 | Final step before violation/control (strongest prediction) |
- **Evidence**:
  - DOI: `10.1016/j.cortex.2023.08.004` — The paradigm is designed to test predictive coding mechanisms; the paper analyzes how expectation signals develop across the trajectory sequence. While the primary publication focuses on violation decoding, the step-by-step sequence structure enables investigation of prediction build-up via ERPs or multivariate patterns across step positions.
- **Kernel Notes**: Analyze each step position separately to examine how prediction strength builds across the sequence. Step_4 represents maximum expectation before the terminal stimulus. Baseline correction applied -100 to 0 ms pre-stimulus. Slight count imbalance (step_1=31368 vs others=31367) suggests some trials terminated early.

---

### Potential Task 1: Catch Trial Response Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, baseline = [-0.1, 0.0] s, target_events = [`Stimulus/S   50`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S   50` | 1 | Catch trial requiring button-press response |
- **Evidence**:
  - Plausible from paradigm: Catch trials test whether participants detect violations and require motor responses, enabling reaction time and hit rate analysis alongside EEG correlates of response preparation and execution.
- **Kernel Notes**: Extended tmax=1.5 s captures button press timing (~0.2-0.8 s post-stimulus) and associated motor potentials (CNV, lateralized readiness potential). These trials contain motor response contamination and should be analyzed separately from perception-only violation trials. Count: 2958 catch trials across 37 subjects (~80 per subject).

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
