# EEG Datasets of Stroke Patients (Motor Imagery)

**Dataset**: `figshare_stroke` | **Year**: 2022 | **URL**: https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5
**Category**: Action/Output | **Subjects**: 50 | **Files (Completed)**: 50 | **Channels**: 33 | **Sampling Rate**: 500 Hz | **Manual Review**: anonymous for review

## Paradigm

Fifty stroke patients (sub-01 to sub-50) performed a cued left/right hand motor imagery task (ZhenTec NT1 amplifier, Ag/AgCl cap). EEG was recorded from 29 scalp channels plus 2 EOG channels (HEOL, VEOR). Each recording session contained 20 trials per hand class (20 left + 20 right = 40 trials total). Each trial comprised three phases: an instruction period (visual cue indicating the target hand), a motor imagery period (subject imagines the indicated hand movement), and a break period (rest). The dataset is designed to study MI-based BCI performance in stroke rehabilitation. Subject ages range from 31 to 77 years (median 57.5), with predominantly right-handed subjects (48/50) and a male-majority cohort (39M/11F).

## File Scan Result

> **Kernel SHA256**: `11759583348321d136db5d087841f6b3abe68cf483378b87d118cc3a59ca49b8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Break beginning - Left hand` | 1000 | admin | raw | Rest/break period following a left-hand trial |
| `Break beginning - Right hand` | 1000 | admin | raw | Rest/break period following a right-hand trial |
| `Instruction beginning - Left hand` | 1000 | admin | raw | Instruction cue onset for left-hand trial |
| `Instruction beginning - Right hand` | 1000 | admin | raw | Instruction cue onset for right-hand trial |
| `Motor imagery beginning - Left hand` | 1000 | event | raw | Left-hand motor imagery period onset |
| `Motor imagery beginning - Right hand` | 1000 | event | raw | Right-hand motor imagery period onset |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | also showed in task-motor-imagery_eeg.json |


## Tasks

### Classical Task 1: Motor Imagery Classification (Left vs. Right Hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Motor imagery beginning - Left hand`, `Motor imagery beginning - Right hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Motor imagery beginning - Left hand` | 0 | Left-hand motor imagery |
  | `Motor imagery beginning - Right hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - 10.1016/j.compbiomed.2025.111285 — Uses figshare stroke dataset (50 subjects) for left/right hand motor imagery classification, segmenting EEG trials from 1 to 4 seconds post-cue with multi-domain features and SCSO-optimized BLS classifier achieving 96.41% accuracy. Deviation: tmin=1.0s used to avoid residual VEPs (kernel default tmin=0.0s).
  - 10.48084/etasr.15300 — Uses figshare stroke motor imagery dataset (50 patients, 40 trials each) to classify left-hand vs right-hand motor imagery EEG signals using CNN, LSTM, and hybrid CNN-LSTM models.
- **Notes**: tmin=0.0s marks MI onset precisely per event markers. Paper DOI: 10.1016/j.compbiomed.2025.111285 uses tmin=1.0s to exclude early VEP components from the preceding instruction cue — mark deviation. Standard paradigm window is 0–4 s per the dataset design (instruction → motor imagery → break).

## Data Quality Notes

- Stroke patient population: highly variable EEG quality due to neurological deficits and movement impairments.
- Very small per-subject trial count (20 per class); cross-subject aggregation is essential.
- EOG channels present (HEOL, VEOR); apply artifact rejection or EOG regression before MI classification.
- Two left-handed subjects (sub-06, sub-15); consider excluding or annotating for lateralization analyses.
- Age range 31-77 years (median 57.5); age-related EEG changes may confound MI classification.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
