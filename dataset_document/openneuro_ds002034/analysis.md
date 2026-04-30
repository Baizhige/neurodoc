# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. Subjects attended to left or right hemifields based on visual cue presentations (half-circle cues for left/right, full circle for center), with continuous alpha-band lateralization index computed from posterior electrodes and fed back in real-time. The paradigm included both offline calibration runs and online neurofeedback runs with trial structures comprising fixation, cue, target, and response phases.

## File Scan Result

> **Kernel SHA256**: `417360376b6b22993a001da72832486322893c67acabe84693cbc8677c6d17d4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 16179 | event | raw | Trial phase onset: cue left |
| `event_11` | 3013 | event | raw | Trial phase onset: target left |
| `event_12` | 2248 | event | raw | Trial phase onset: target right |
| `event_13` | 1129 | event | raw | Trial phase onset: target center |
| `event_15` | 938 | event | raw | Button press correct |
| `event_2` | 5020 | event | raw | Trial phase onset: cue right |
| `event_4` | 5020 | admin | raw | Run start |
| `event_5` | 9333 | admin | raw | Run end |
| `event_6` | 6720 | event | raw | Trial phase onset: trial start |
| `event_8` | 1711 | event | raw | Trial phase onset: trial start |
| `event_9` | 4995 | event | raw | Trial phase onset: fixation on |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class covert visuospatial attention (left vs right target)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`event_11`, `event_12`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_11 | 0 | target left |
  | event_12 | 1 | target right |
- **Evidence**:
  - 10.1007/s10548-019-00725-9 — Primary paper explicitly describes 2-class CVSA classification using target onset events. Left target (event_11) vs right target (event_12) with tmin=-0.5s, tmax=2.0s. 3013 left targets and 2248 right targets available. BCI decoder calibration was performed on these events as part of the neurofeedback paradigm.
- **Notes**: Event meanings confirmed by events.json sidecar: x11='target left', x12='target right'. The task uses target onset events (not cue events) to classify covert visuospatial attention direction based on lateralized alpha power modulations during the sustained attention period.

### Potential Task 1: 3-class covert visuospatial attention (left vs right vs center)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`event_11`, `event_12`, `event_13`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_11 | 0 | target left (covert attention to left hemifield) |
  | event_12 | 1 | target right (covert attention to right hemifield) |
  | event_13 | 2 | target center (no covert attention shift, control condition) |
- **Evidence**:
  - events.json — "x11": "target left", "x12": "target right", "x13": "target center" (hardware trigger value levels confirmed across all sessions)
  - events.tsv samples — event_value 11/12/13 consistently paired with event_name "target_left"/"target_right"/"target_center" in sub-01 ses-01, ses-02 (offlinecatch, onlinesham)
  - README — "a full circle around the fixation point indicated a central fixation trial (no covert attention shift)"
- **Notes**: Target events (11/12/13) mark the onset of the sustained attention phase where subjects maintain covert visuospatial attention to the cued location. Center trials serve as an explicit control condition with no lateralized attention demand, enabling 3-way classification of attention state. Epoch window [-0.5, 2.0] s captures pre-target baseline and early sustained attention period; values inferred from analogous 2-class CVSA task structure.

### Potential Task 2: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 21.0 – 27.0 (years) | Subject chronological age; N=14, mean 23±1.52 years |
- **Evidence**:
- **Notes**: Small-sample subject-level regression (N=14). Segmentation-based epoching with 4s non-overlapping windows extracts features from continuous sustained-attention EEG to predict age as a continuous biomarker. The narrow age range (21-27 years) limits predictive utility but demonstrates feasibility of age regression from EEG features.

### Potential Task 3: Sex Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — N=14 subjects with complete sex data: 7 female (F), 7 male (M)
  - README — "Fourteen healthy subjects (seven female, seven male), age 23±1.52 years"
- **Notes**: Segmentation-based approach for subject-level biomarker classification. The 4-second segment length is a standard default for continuous EEG analysis when no specific temporal structure is required; overlap=0.0 ensures independent segments. Binary classification with perfectly balanced classes (7 vs 7). Very small sample size (N=14) limits generalizability but the task is technically feasible. All segments from a given subject receive the same label from participants.tsv.

## Data Quality Notes

- `device` field is missing from all files, limiting hardware provenance tracking.
- Event counts show substantial imbalance between cue events (event_1: 16179, event_2: 5020) suggesting possible data quality issue or multiple event definitions for left cues (event_1 may conflate multiple conditions).
- Multiple trial start event IDs (event_6, event_8, event_9) with overlapping meanings may indicate inconsistent event coding across runs or sessions.
- Run end events (9333) exceed run start events (5020) by factor of ~1.86, suggesting possible duplicate or spurious run end markers.
- Small sample size (N=14) limits statistical power for subject-level biomarker tasks (age regression, sex classification).
- Age range is extremely narrow (21-27 years), severely limiting generalizability of age regression model.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
