# BCI Competition IV Dataset 2b (Left/Right Hand Motor Imagery)

**Dataset**: `bcic_iv_2b` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_2b.pdf
**Category**: Action/Output | **Subjects**: 9 | **Files (Completed)**: 46 | **Channels**: 6 | **Sampling Rate**: 250 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

Nine subjects (B01-B09) performed two-class cued motor imagery of the left and right hand (BCI Competition IV, 2008). Only 3 bipolar EEG channels over the sensorimotor cortex (C3, Cz, C4) and 3 EOG channels were recorded (0.5-100 Hz, notch at 50 Hz). Each subject underwent 5 sessions over two days: sessions 1-2 without feedback, sessions 3-5 with BCI feedback. Each session contained multiple runs of ~60-80 trials per class. A fixation cross preceded each trial, followed by a visual left/right arrow cue for 1.25 s, then a 4-second (begin at 3 s after cue) imagery period with optional BCI cursor feedback. Evaluation sessions (suffix `E.gdf`) have unknown cue labels that the kernel resolves from companion `.mat` files.

## File Scan Result

> **Kernel SHA256**: `f8318b338ce28894e9eb4e28cfcd174ed8fe180a3c6730d7756c660f2518fadc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `BCI feedback (continuous)` | 1440 | admin | raw | BCI feedback period (sessions 3-5 only) |
| `Cue onset left (class 1)` | 4460 | event | raw | Left-hand motor imagery cue |
| `Cue onset right (class 2)` | 4460 | event | raw | Right-hand motor imagery cue |
| `Eye blinks` | 263 | admin | raw | Eye artifact marker |
| `Eye rotation` | 263 | admin | raw | Eye artifact marker |
| `Horizontal eye movement` | 53 | admin | raw | Eye artifact marker |
| `Idling EEG (eyes closed)` | 43 | admin | raw | Resting state with eyes closed |
| `Idling EEG (eyes open)` | 43 | admin | raw | Resting state with eyes open |
| `Rejected trial` | 1253 | admin | raw | Experimenter-rejected trial |
| `Start of a new run` | 252 | admin | raw | Run boundary marker |
| `Start of a trial` | 6240 | admin | raw | Trial-onset fixation cross (pre-cue) |
| `Vertical eye movement` | 323 | admin | raw | Eye artifact marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | a device with Ag/AgCl electrode |

## Tasks

### Classical Task 1: Binary Motor Imagery Classification - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, target_events = [`Cue onset left (class 1)`, `Cue onset right (class 2)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Cue onset left (class 1)` | 0 | Left-hand motor imagery |
  | `Cue onset right (class 2)` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1109/tnsre.2022.3156076 — Segmented BCI IV-2b data into four overlapping 2-second time windows for MI classification (−0.5s to 1.5s  , 0s to 2s, 0.5 sto 2.5s , and 1 to 3s)
  - DOI: 10.1109/tnsre.2023.3241846 — Used epoched data from 3rd to 7th second relative to cue onset for left vs right hand MI (3s to  7s, start from ”Start of a trial“ event)
  - DOI: 10.3389/fnins.2020.00918 — Trained CNN classifiers on sessions 1-3 for inter-subject continuous decoding of left vs right hand MI (0.8s ~ 2.8 s, from "Cue onset")
- **Kernel Notes**: 

## Data Quality Notes

- Only 3 EEG channels (C3, Cz, C4): very limited spatial resolution; spatial filtering (CSP) is critical.
- EOG channels present; apply artifact regression before MI classification.
- Feedback sessions (3-5) may show learning effects; sessions 1-2 provide cleaner baseline.
- Evaluation files use `Cue unknown (class 783)` initially; companion `.mat` files are required by the kernel to resolve labels.
- Subject demographics: B01-B09, ages 20-32, mixed sex.
- 46 files total across 9 subjects x 5 sessions; some sessions may have extra evaluation runs.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
