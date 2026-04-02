# EEG-Asymmetries Dataset

**Dataset**: `openneuro_ds007172` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007172
**Category**: High-level Mental | **Subjects**: 100 | **Files (Completed)**: 501 | **Channels**: 32 | **Sampling Rate**: 500 Hz

## Paradigm

Multi-task EEG battery investigating hemispheric asymmetries across resting state and four cognitive categorization tasks: emotion recognition (face stimuli with emotional valence), language comprehension, face perception (identity discrimination), and visual discrimination (house images). The dataset examines relationships between N1 lateralization and alpha asymmetry across task domains. BrainVision trigger codes (Stimulus/S1xx and S2xx families) encode stimulus conditions per task.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007172

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S111` | 12800 | long | raw | Emotion/language task condition S111 |
| `Stimulus/S223` | 12800 | long | raw | Emotion/language task condition S223 |
| `Stimulus/S212` | 12800 | long | raw | Emotion/language task condition S212 |
| `Stimulus/S214` | 12800 | long | raw | Emotion/language task condition S214 |
| `Stimulus/S211` | 12800 | long | raw | Emotion/language task condition S211 |
| `Stimulus/S123` | 12800 | long | raw | Emotion/language task condition S123 |
| `Stimulus/S114` | 12800 | long | raw | Emotion/language task condition S114 |
| `Stimulus/S112` | 12800 | long | raw | Emotion/language task condition S112 |
| `Stimulus/S222` | 12000 | long | raw | Emotion/language task condition S222 |
| `Stimulus/S113` | 12000 | long | raw | Emotion/language task condition S113 |
| `Stimulus/S121` | 12000 | long | raw | Emotion/language task condition S121 |
| `Stimulus/S122` | 12000 | long | raw | Emotion/language task condition S122 |
| `Stimulus/S124` | 12000 | long | raw | Emotion/language task condition S124 |
| `Stimulus/S221` | 12000 | long | raw | Emotion/language task condition S221 |
| `Stimulus/S213` | 12000 | long | raw | Emotion/language task condition S213 |
| `Stimulus/S224` | 12000 | long | raw | Emotion/language task condition S224 |
| `Stimulus/S217` | 11998 | long | raw | Face task condition S217 |
| `Stimulus/S218` | 11998 | long | raw | Face task condition S218 |
| `Stimulus/S118` | 11998 | long | raw | Face task condition S118 |
| `Stimulus/S117` | 11998 | long | raw | Face task condition S117 |
| `Stimulus/S227` | 11998 | long | raw | Face task condition S227 |
| `Stimulus/S228` | 11998 | long | raw | Face task condition S228 |
| `Stimulus/S127` | 11998 | long | raw | Face task condition S127 |
| `Stimulus/S128` | 11998 | long | raw | Face task condition S128 |
| `Stimulus/S 21` | 11998 | long | raw | Houses/visual task condition S21 |
| `Stimulus/S 11` | 11998 | long | raw | Houses/visual task condition S11 |
| `Stimulus/S 22` | 11998 | long | raw | Houses/visual task condition S22 |
| `New Segment/` | 501 | admin | raw | Segment boundary marker |
| `Comment/actiCAP Data On` | 383 | admin | raw | Hardware status marker |
| `Comment/actiCAP USB Power On` | 134 | admin | raw | Hardware status marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S111`, `Stimulus/S223`, `Stimulus/S212`, `Stimulus/S214`, `Stimulus/S211`, `Stimulus/S123`, `Stimulus/S114`, `Stimulus/S112`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Normal Task 1: Multi-Condition EEG Asymmetry (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S111` | 0 | Emotion/language condition S111 |
  | `Stimulus/S223` | 1 | Emotion/language condition S223 |
  | `Stimulus/S212` | 2 | Emotion/language condition S212 |
  | `Stimulus/S214` | 3 | Emotion/language condition S214 |
  | `Stimulus/S211` | 4 | Emotion/language condition S211 |
  | `Stimulus/S123` | 5 | Emotion/language condition S123 |
  | `Stimulus/S114` | 6 | Emotion/language condition S114 |
  | `Stimulus/S112` | 7 | Emotion/language condition S112 |
  | `Stimulus/S222` | 8 | Emotion/language condition S222 |
  | `Stimulus/S113` | 9 | Emotion/language condition S113 |
  | `Stimulus/S121` | 10 | Emotion/language condition S121 |
  | `Stimulus/S122` | 11 | Emotion/language condition S122 |
  | `Stimulus/S124` | 12 | Emotion/language condition S124 |
  | `Stimulus/S221` | 13 | Emotion/language condition S221 |
  | `Stimulus/S213` | 14 | Emotion/language condition S213 |
  | `Stimulus/S224` | 15 | Emotion/language condition S224 |
  | `Stimulus/S217` | 16 | Face task condition S217 |
  | `Stimulus/S218` | 17 | Face task condition S218 |
  | `Stimulus/S118` | 18 | Face task condition S118 |
  | `Stimulus/S117` | 19 | Face task condition S117 |
  | `Stimulus/S227` | 20 | Face task condition S227 |
  | `Stimulus/S228` | 21 | Face task condition S228 |
  | `Stimulus/S127` | 22 | Face task condition S127 |
  | `Stimulus/S128` | 23 | Face task condition S128 |
  | `Stimulus/S 21` | 24 | Houses/visual task condition S21 |
  | `Stimulus/S 11` | 25 | Houses/visual task condition S11 |
  | `Stimulus/S 22` | 26 | Houses/visual task condition S22 |
- **Kernel Notes**: 5 task files per subject (emotions, faces, houses, language, rest). `New Segment/`, `Comment/actiCAP Data On`, `Comment/actiCAP USB Power On` are hardware/admin markers; exclude from stimulus analysis. Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## Data Quality Notes

- 501 files from 100 subjects includes 5 task types per subject.
- `New Segment/` and all `Comment/` markers are administrative; never use as classification targets.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

