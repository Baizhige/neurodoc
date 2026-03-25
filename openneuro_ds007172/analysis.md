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

### Primary Task 1: Publisher-defined BIDS task: Houses
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds007172 DOI: https://doi.org/10.1080/1357650x.2025.2591660


### Primary Task 2: Publisher-defined BIDS task: Words
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds007172 DOI: https://doi.org/10.1080/1357650x.2025.2591660


### Primary Task 3: Publisher-defined BIDS task: Emotions
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds007172 DOI: https://doi.org/10.1080/1357650x.2025.2591660


### Normal Task 1: Multi-Condition EEG Asymmetry (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 5 task files per subject (emotions, faces, houses, language, rest). `New Segment/`, `Comment/actiCAP Data On`, `Comment/actiCAP USB Power On` are hardware/admin markers; exclude from stimulus analysis.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/actiCAP Data On` | 0 | Hardware marker |
 | `Comment/actiCAP USB Power On` | 1 | Hardware power marker |
 | `Stimulus/S111` | 2 | Condition S111 |
 | `Stimulus/S223` | 3 | Condition S223 |
 | `Stimulus/S212` | 4 | Condition S212 |
 | `Stimulus/S214` | 5 | Condition S214 |
 | `Stimulus/S211` | 6 | Condition S211 |
 | `Stimulus/S123` | 7 | Condition S123 |
 | `Stimulus/S114` | 8 | Condition S114 |
 | `Stimulus/S112` | 9 | Condition S112 |
 | `Stimulus/S222` | 10 | Condition S222 |
 | `Stimulus/S113` | 11 | Condition S113 |
 | `Stimulus/S121` | 12 | Condition S121 |
 | `Stimulus/S122` | 13 | Condition S122 |
 | `Stimulus/S124` | 14 | Condition S124 |
 | `Stimulus/S221` | 15 | Condition S221 |
 | `Stimulus/S213` | 16 | Condition S213 |
 | `Stimulus/S224` | 17 | Condition S224 |
 | `Stimulus/S217` | 18 | Condition S217 |
 | `Stimulus/S218` | 19 | Condition S218 |
 | `Stimulus/S118` | 20 | Condition S118 |
 | `Stimulus/S117` | 21 | Condition S117 |
 | `Stimulus/S227` | 22 | Condition S227 |
 | `Stimulus/S228` | 23 | Condition S228 |
 | `Stimulus/S127` | 24 | Condition S127 |
 | `Stimulus/S128` | 25 | Condition S128 |
 | `Stimulus/S 21` | 26 | Condition S21 |
 | `Stimulus/S 11` | 27 | Condition S11 |
 | `Stimulus/S 22` | 28 | Condition S22 |
## Data Quality Notes

- 501 files from 100 subjects includes 5 task types per subject.
- `New Segment/` and all `Comment/` markers are administrative; never use as classification targets.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `Hemispheric asymmetries in the EEG: Is there an association between N1 lateralization and alpha asymmetryx`
