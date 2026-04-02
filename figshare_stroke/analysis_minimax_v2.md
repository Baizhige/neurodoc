# EEG Datasets of Stroke Patients (Motor Imagery)

**Dataset**: `figshare_stroke` | **Year**: 2022 | **URL**: https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5
**Category**: Action/Output | **Subjects**: 50 | **Files (Completed)**: 50 | **Channels**: 33 | **Sampling Rate**: 500 Hz

## Paradigm

Fifty stroke patients (sub-01 to sub-50) performed a cued left/right hand motor imagery task (ZhenTec NT1 amplifier, Ag/AgCl cap). EEG was recorded from 31 scalp channels plus 2 horizontal EOG channels (HEOL, HEOR). Each recording session contained 20 trials per hand class (20 left + 20 right = 40 trials total). Each trial comprised three phases: an instruction period (visual cue indicating the target hand), a motor imagery period (subject imagines the indicated hand movement), and a break period (rest). The dataset is designed to study MI-based BCI performance in stroke rehabilitation. Subject ages range from 31 to 77 years (median ~55), with predominantly right-handed subjects (49/50) and a male-majority cohort (~36M/14F).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Instruction beginning - Left hand` | 1000 | admin | raw | Instruction cue onset for left-hand trial |
| `Instruction beginning - Right hand` | 1000 | admin | raw | Instruction cue onset for right-hand trial |
| `Motor imagery beginning - Left hand` | 1000 | short | raw | Left-hand motor imagery period onset |
| `Motor imagery beginning - Right hand` | 1000 | short | raw | Right-hand motor imagery period onset |
| `Break beginning - Left hand` | 1000 | admin | raw | Rest/break period following a left-hand trial |
| `Break beginning - Right hand` | 1000 | admin | raw | Rest/break period following a right-hand trial |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Counts are totals across all 50 subjects (20 per class per recording x 50 subjects).

## Tasks

### Primary Task 1: Motor Imagery Classification (Left vs. Right Hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 1.0 s, tmax = 4.0 s, target_events = [`Motor imagery beginning - Left hand`, `Motor imagery beginning - Right hand`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Motor imagery beginning - Left hand` | 0 | Left-hand motor imagery |
  | `Motor imagery beginning - Right hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1016/j.compbiomed.2025.111285 — Uses figshare stroke dataset (50 subjects) for left/right hand motor imagery classification, segmenting EEG trials from 1 to 4 seconds post-cue with multi-domain features and SCSO-optimized BLS classifier achieving 96.41% accuracy.
  - DOI: 10.1109/JBHI.2025.3646871 — Proposes mutual generation framework for stroke patients' motor imagery classification using the Stroke MI 50 dataset to classify left vs. right hand motor imagery and predict functional recovery.
  - DOI: https://doi.org/10.48084/etasr.15300 — Uses figshare stroke motor imagery dataset (50 patients, 40 trials each) to classify left-hand vs right-hand motor imagery EEG signals using CNN, LSTM, and hybrid CNN-LSTM models.
- **Kernel Notes**: Verify tmin=1.0s aligns with motor imagery onset; some papers use tmin=0.0s for MI onset. (replaces Normal Task 1 from original analysis.md)

### Normal Task 2: Stroke Patient Subgroup Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Same as Task 1 (MI events); group labels (age, lesion side, etc.) from `participants.tsv`.
- **Notes**: Clinical metadata (age, sex, stroke side, handedness) is embedded in the kernel's `_SUBJECT_DICT`. Cross-subject analysis with clinical covariates is the primary use case.


## Data Quality Notes

- Stroke patient population: highly variable EEG quality due to neurological deficits and movement impairments.
- Very small per-subject trial count (20 per class); cross-subject aggregation is essential.
- EOG channels present (HEOL, HEOR); apply artifact rejection or EOG regression before MI classification.
- One left-handed subject (sub-06); consider excluding or annotating for lateralization analyses.
- Age range 31-77 years (mean ~55); age-related EEG changes may confound MI classification.

## References

- **Reference**: EEG datasets of stroke patients for motor imagery BCI (Figshare, 2022). https://figshare.com/articles/dataset/EEG_datasets_of_stroke_patients/21679035/5
