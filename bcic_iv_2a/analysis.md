# BCI Competition IV Dataset 2a (4-Class Motor Imagery)

**Dataset**: `bcic_iv_2a` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2a.pdf
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 18 | **Channels**: 25 | **Sampling Rate**: 250 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

Nine subjects (A01-A09) performed four-class cued motor imagery (BCI Competition IV, 2008): left hand, right hand, feet, and tongue. Each session contained 6 runs of 48 trials each (288 trials per session), balanced across 4 classes (72 trials per class). A fixation cross preceded each trial, followed by a visual arrow cue indicating the imagery class, and a 4-second imagery period. Short resting intervals separated trials. Each subject was recorded in two sessions: a training session (suffix `T.gdf`) with event labels, and an evaluation session (suffix `E.gdf`) with initially unknown labels replaced by kernel-loaded `.mat` companion files. EEG was recorded from 22 channels (standard 10-20, sensorimotor focus) plus 3 bipolar EOG channels (filtered 0.5-100 Hz, notch at 50 Hz).

## File Scan Result

> **Kernel SHA256**: `489182843c6974d9f77d2a7ccd1f1bad91a5f3eb1d01dfc7e15b3321e4eb8803`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Start of a trial` | 4896 | admin | raw | Trial-onset fixation cross (pre-cue marker) |
| `Cue onset tongue (class 4)` | 1656 | event | raw | Tongue motor imagery cue |
| `Cue onset foot (class 3)` | 1375 | event | raw | Feet motor imagery cue |
| `Cue onset left (class 1)` | 1224 | event | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | 1224 | event | raw | Right-hand motor imagery cue |
| `Rejected trial` | 488 | admin | raw | Trial rejected by experimenter |
| `Start of a new run` | 153 | admin | raw | Run boundary marker |
| `Eye movements` | 18 | admin | raw | Artifactual eye movement event |
| `Idling EEG (eyes closed)` | 17 | admin | raw | Resting state with eyes closed |
| `Idling EEG (eyes open)` | 17 | admin | raw | Resting state with eyes open |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`, `Cue onset foot (class 3)`, `Cue onset tongue (class 4)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
  | `Cue onset foot (class 3)` | 2 | Feet motor imagery |
  | `Cue onset tongue (class 4)` | 3 | Tongue motor imagery |
- **Evidence**:
  - DOI: (not identified) — Official BCI Competition IV Dataset 2a description defines four-class MI (left hand, right hand, feet, tongue) as benchmark task with 4s imagery window from cue onset.
  - DOI: 10.1109/tnnls.2018.2789927 — CNN trained on 0.5-2.5s MI period after cue onset.
  - DOI: 10.1109/tnsre.2022.3156076 — SincNet hybrid achieves 74.26% accuracy.
- **Kernel Notes**: 

### Potential Task 1: Binary Motor Imagery - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
- **Evidence**:

- **Kernel Notes**: 

## Data Quality Notes

- Rejected trials (variable per subject/session) should be excluded from analysis.
- EOG channels present; apply artifact rejection or regression before motor imagery classification.
- Evaluation files initially contain `Cue unknown (class 783)` entries that the kernel replaces with proper class labels from `.mat` companion files; verify companion file presence.
- Class balance is enforced by design (72 trials per class per session); minor imbalance may arise from rejected trials.
- Subject age range: 17-26 years; 7 female, 2 male subjects.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
