# Effect of obesity on arithmetic processing in preteens with high and low math skills. An event-related potentials study

**Dataset**: `openneuro_ds004019` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004019
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 62 | **Channels**: 132 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Obese and non-obese preteens (ages 9-10) performed a delayed-verification arithmetic task to evaluate the effects of weight status and math skill level on arithmetic processing. Participants viewed an arithmetic problem (prob), then a delay (bgin), then a verification digit (face) and responded (resp). Trigger codes `0` and `1` encode response correctness (0=incorrect, 1=correct). The study uses ERPs to investigate neural correlates of arithmetic cognition in the context of childhood obesity.

## File Scan Result

> **Kernel SHA256**: `58f1a7b1af01814a0b283766fb3a3931292ebecb274da0ba0386859fe3b90f34`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0` | 4848 | event | raw | Incorrect arithmetic response |
| `1` | 9972 | event | raw | Correct arithmetic response |
| `CELL` | 256 | admin | raw | Cell/block marker |
| `SESS` | 64 | admin | raw | Session start marker |
| `bgin` | 14820 | event | raw | Trial beginning / delay period onset |
| `boundary` | 250 | admin | raw | Data boundary marker (exclude from analysis) |
| `ch++` | 14820 | event | raw | Choice/comparison stimulus onset |
| `face` | 14820 | event | raw | Verification digit (face stimulus) onset |
| `prob` | 14820 | event | raw | Arithmetic problem onset |
| `resp` | 14087 | event | raw | Participant button-press response |
| `sync` | 312 | admin | raw | Hardware sync pulse |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Correct vs Incorrect Arithmetic Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`0`, `1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `0` | 0 | Incorrect arithmetic response |
  | `1` | 1 | Correct arithmetic response |
- **Evidence**:
  - DOI: 10.3389/fnhum.2022.760234 — This paper analyzes ERP components (P150, P300, N400) time-locked to answer choice presentation to compare obese vs non-obese preteens with high/low math skills on arithmetic verification tasks, using correct vs incorrect response events (`1` and `0`) for epoching.
- **Kernel Notes**: Epochs are time-locked to response correctness events (`0`, `1`) which occur concurrent with `resp`. Class imbalance (~67% correct: 9972 vs 4848 incorrect) should be addressed using weighted loss or stratified undersampling. Exclude admin markers (sync, CELL, SESS) and boundary markers from analysis.

### Potential Task 1: Face Verification Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`face`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `face` | - | Verification digit (face stimulus) onset |
- **Evidence**: Plausible from paradigm alone — face events mark the verification digit presentation in the delayed-verification arithmetic task. Stimulus-locked analysis of face events enables investigation of perceptual evaluation processes independent of response execution. The face event precedes the response (`resp`) and correctness markers (`0`, `1`), allowing separation of stimulus evaluation from response selection.
- **Kernel Notes**: Epochs time-locked to face stimulus onset capture early perceptual processing. Can be combined with correctness labels from concurrent `0`/`1` events using super meta for secondary analysis. Remove non-EEG channels (ECG/Respiration) before analysis.

### Potential Task 2: Arithmetic Problem Presentation Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`prob`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `prob` | - | Arithmetic problem onset |
- **Evidence**: Plausible from paradigm alone — the `prob` event marks initial arithmetic problem presentation. Problem-locked epochs capture encoding and initial calculation processes, distinct from verification and response stages. Supports analysis of obesity and math skill effects on arithmetic problem processing.
- **Kernel Notes**: Problem presentation epochs capture the earliest cognitive stage of the trial. Subsequent events (`bgin`, `ch++`, `face`, `resp`) follow in sequence, enabling multi-stage trial analysis. No direct reference ties this to a specific classification task, making it a potential exploratory analysis.

### Potential Task 3: Choice/Comparison Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`ch++`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `ch++` | - | Choice/comparison stimulus onset |
- **Evidence**: Plausible from paradigm alone — the `ch++` event represents the choice/comparison stimulus presentation, distinct from the face verification digit. Epoching on this event enables analysis of comparison processing stages separate from face verification and response execution.
- **Kernel Notes**: The paradigm contains both `ch++` and `face` events, suggesting distinct cognitive stages. Verify original stimulus presentation logic to confirm whether `ch++` and `face` represent different trial phases or alternative stimulus types. Epoch parameter overlap with other tasks (tmin=-0.2s, tmax=1.0s) ensures consistency across analyses.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
