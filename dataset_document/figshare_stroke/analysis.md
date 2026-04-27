# EEG Datasets of Stroke Patients (Motor Imagery)

**Dataset**: `figshare_stroke` | **Year**: 2022 | **URL**: https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5
**Category**: Action/Output | **Subjects**: 50 | **Files (Completed)**: 50 | **Channels**: 33 | **Sampling Rate**: 500 Hz
**Manual Review**: Jiping Cui

## Paradigm

Fifty stroke patients (sub-01 to sub-50) performed a cued left/right hand motor imagery task (ZhenTec NT1 amplifier, Ag/AgCl cap). EEG was recorded from 29 scalp channels plus 2 EOG channels (HEOL, VEOR). Each recording session contained 20 trials per hand class (20 left + 20 right = 40 trials total). Each trial comprised three phases: an instruction period (visual cue indicating the target hand), a motor imagery period (subject imagines the indicated hand movement), and a break period (rest). The dataset is designed to study MI-based BCI performance in stroke rehabilitation. Subject ages range from 31 to 77 years (median 57.5), with predominantly right-handed subjects (48/50) and a male-majority cohort (39M/11F).

## File Scan Result

> **Kernel SHA256**: `fb851de3e4dbb6b9db1391ae068830a750d9dcec09ea21d253d9bcad876d6f4d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Break beginning - Left hand` | 1000 | admin | raw | Rest/break period following a left-hand trial |
| `Break beginning - Right hand` | 1000 | admin | raw | Rest/break period following a right-hand trial |
| `Instruction beginning - Left hand` | 1000 | admin | raw | Instruction cue onset for left-hand trial |
| `Instruction beginning - Right hand` | 1000 | admin | raw | Instruction cue onset for right-hand trial |
| `Motor imagery beginning - Left hand` | 1000 | event | raw | Left-hand motor imagery period onset |
| `Motor imagery beginning - Right hand` | 1000 | event | raw | Right-hand motor imagery period onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Motor Imagery Classification (Left vs. Right Hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Motor imagery beginning - Left hand`, `Motor imagery beginning - Right hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Motor imagery beginning - Left hand` | 0 | Left-hand motor imagery |
  | `Motor imagery beginning - Right hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1016/j.compbiomed.2025.111285 — Uses figshare stroke dataset (50 subjects) for left/right hand motor imagery classification, segmenting EEG trials from 1 to 4 seconds post-cue with multi-domain features and SCSO-optimized BLS classifier achieving 96.41% accuracy.
  - DOI: 10.1109/JBHI.2025.3646871 — Proposes mutual generation framework for stroke patients' motor imagery classification using the Stroke MI 50 dataset to classify left vs. right hand motor imagery and predict functional recovery.
  - DOI: 10.48084/etasr.15300 — Uses figshare stroke motor imagery dataset (50 patients, 40 trials each) to classify left-hand vs right-hand motor imagery EEG signals using CNN, LSTM, and hybrid CNN-LSTM models.
- **Kernel Notes**: tmin=0.0s marks MI onset precisely per event markers. Some papers use tmin=0.5s or 1.0s to avoid residual Visual Evoked Potentials (VEPs) from the preceding instruction cue.

### Potential Task 2: Stroke Patient Subgroup Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Same as Task 1 (MI events); group labels (age, lesion side, etc.) from `participants.tsv`.
- **Notes**: Clinical metadata (age, sex, stroke side, handedness) is embedded in the kernel's `_SUBJECT_DICT`. Cross-subject analysis with clinical covariates is the primary use case.

## Data Quality Notes

- Stroke patient population: highly variable EEG quality due to neurological deficits and movement impairments.
- Very small per-subject trial count (20 per class); cross-subject aggregation is essential.
- EOG channels present (HEOL, VEOR); apply artifact rejection or EOG regression before MI classification.
- Two left-handed subjects (sub-06, sub-15); consider excluding or annotating for lateralization analyses.
- Age range 31-77 years (median 57.5); age-related EEG changes may confound MI classification.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review