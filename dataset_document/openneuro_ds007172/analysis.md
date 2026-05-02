# EEG-Asymmetries Dataset

**Dataset**: `openneuro_ds007172` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007172
**Category**: High-level Mental | **Subjects**: 100 | **Files (Completed)**: 501 | **Channels**: 32 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Multi-task EEG battery investigating hemispheric asymmetries across resting state and four cognitive categorization tasks: emotion recognition (face stimuli with emotional valence), language comprehension, face perception (identity discrimination), and visual discrimination (house images). The dataset examines relationships between N1 lateralization and alpha asymmetry across task domains. BrainVision trigger codes (Stimulus/S1xx and S2xx families) encode stimulus conditions per task.

## File Scan Result

> **Kernel SHA256**: `5a32b4b16f401011e1c84964aa876e9dcfee503cb7499f1047c16fcafee216f6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S1` | 800 | event | raw | Resting state baseline condition |
| `Stimulus/S10001` | 1010 | event | raw | Session start marker |
| `Stimulus/S10002` | 108 | event | raw | Practice trial marker |
| `Stimulus/S10003` | 56 | event | raw | Calibration marker |
| `Stimulus/S11` | 11998 | event | raw | Visual discrimination (house category 1) |
| `Stimulus/S111` | 3232 | event | raw | Emotion/language condition (positive valence, block 1) |
| `Stimulus/S112` | 3232 | event | raw | Emotion/language condition (positive valence, block 2) |
| `Stimulus/S113` | 808 | event | raw | Emotion/language condition (positive valence, block 3) |
| `Stimulus/S114` | 3232 | event | raw | Emotion/language condition (positive valence, block 4) |
| `Stimulus/S117` | 6400 | event | raw | Face identity left (block 1) |
| `Stimulus/S118` | 6400 | event | raw | Face identity right (block 1) |
| `Stimulus/S12` | 3998 | event | raw | Visual discrimination (house category 2, mixed) |
| `Stimulus/S121` | 808 | event | raw | Emotion/language condition (negative valence, block 1) |
| `Stimulus/S122` | 808 | event | raw | Emotion/language condition (negative valence, block 2) |
| `Stimulus/S123` | 3232 | event | raw | Emotion/language condition (negative valence, block 3) |
| `Stimulus/S124` | 808 | event | raw | Emotion/language condition (negative valence, block 4) |
| `Stimulus/S127` | 1600 | event | raw | Face identity left (block 2) |
| `Stimulus/S128` | 1600 | event | raw | Face identity right (block 2) |
| `Stimulus/S13` | 3200 | event | raw | Visual task condition (category 3, mixed) |
| `Stimulus/S14` | 12800 | event | raw | Visual task condition (category 4, catch trials) |
| `Stimulus/S2` | 800 | event | raw | Resting state baseline (alternate) |
| `Stimulus/S21` | 12000 | event | raw | Visual discrimination (house category 2) |
| `Stimulus/S211` | 3232 | event | raw | Language condition (block 1) |
| `Stimulus/S212` | 3232 | event | raw | Language condition (block 2) |
| `Stimulus/S213` | 808 | event | raw | Language condition (block 3) |
| `Stimulus/S214` | 3232 | event | raw | Language condition (block 4) |
| `Stimulus/S217` | 6384 | event | raw | Face identity left (block 3) |
| `Stimulus/S218` | 6392 | event | raw | Face identity right (block 3) |
| `Stimulus/S22` | 4000 | event | raw | Visual discrimination (house category 3) |
| `Stimulus/S221` | 808 | event | raw | Emotion condition (block 1) |
| `Stimulus/S222` | 808 | event | raw | Emotion condition (block 2) |
| `Stimulus/S223` | 3232 | event | raw | Emotion condition (block 3) |
| `Stimulus/S224` | 808 | event | raw | Emotion condition (block 4) |
| `Stimulus/S227` | 1598 | event | raw | Face identity left (block 4) |
| `Stimulus/S228` | 1594 | event | raw | Face identity right (block 4) |
| `Stimulus/S23` | 3200 | event | raw | Visual task condition (category 3, catch) |
| `Stimulus/S24` | 12800 | event | raw | Visual task condition (category 4, catch trials) |
| `Stimulus/S7` | 116 | event | raw | Fixation baseline marker |
| `Stimulus/S70` | 198 | event | raw | Task instruction marker |
| `Stimulus/S71` | 182 | event | raw | Task instruction marker (alternate) |
| `Stimulus/S8` | 84 | event | raw | Inter-trial interval marker |
| `Stimulus/S99999` | 1006 | event | raw | Session end marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Multi-Condition EEG Asymmetry Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S111` | 0 | Emotion/language condition (positive valence, block 1) |
  | `Stimulus/S112` | 1 | Emotion/language condition (positive valence, block 2) |
  | `Stimulus/S113` | 2 | Emotion/language condition (positive valence, block 3) |
  | `Stimulus/S114` | 3 | Emotion/language condition (positive valence, block 4) |
  | `Stimulus/S121` | 4 | Emotion/language condition (negative valence, block 1) |
  | `Stimulus/S122` | 5 | Emotion/language condition (negative valence, block 2) |
  | `Stimulus/S123` | 6 | Emotion/language condition (negative valence, block 3) |
  | `Stimulus/S124` | 7 | Emotion/language condition (negative valence, block 4) |
  | `Stimulus/S211` | 8 | Language condition (block 1) |
  | `Stimulus/S212` | 9 | Language condition (block 2) |
  | `Stimulus/S213` | 10 | Language condition (block 3) |
  | `Stimulus/S214` | 11 | Language condition (block 4) |
  | `Stimulus/S221` | 12 | Emotion condition (block 1) |
  | `Stimulus/S222` | 13 | Emotion condition (block 2) |
  | `Stimulus/S223` | 14 | Emotion condition (block 3) |
  | `Stimulus/S224` | 15 | Emotion condition (block 4) |
  | `Stimulus/S217` | 16 | Face condition (left identity) |
  | `Stimulus/S218` | 17 | Face condition (right identity) |
  | `Stimulus/S227` | 18 | Face condition (left identity, alt) |
  | `Stimulus/S228` | 19 | Face condition (right identity, alt) |
  | `Stimulus/S11` | 20 | Visual discrimination (house type 1) |
  | `Stimulus/S21` | 21 | Visual discrimination (house type 2) |
  | `Stimulus/S22` | 22 | Visual discrimination (house type 3) |
- **Evidence**: DOI 10.1080/1357650X.2025.2591660
- **Kernel Notes**: Use New Segment/ markers to identify subject/run boundaries. 501 segments across 100 subjects suggests ~5 segments per subject. S111-S224 encode emotion/language task conditions with first digit indicating condition type and second digit indicating block. S11/S21/S22 encode house visual discrimination. High condition count (23 classes) may require condition grouping or careful class balancing.

### Potential Task 2: Face Perception Task - Identity Discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, overlap = 0.1 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S117` | 0 | Face identity left (block 1) |
  | `Stimulus/S118` | 1 | Face identity right (block 1) |
  | `Stimulus/S127` | 2 | Face identity left (block 2) |
  | `Stimulus/S128` | 3 | Face identity right (block 2) |
  | `Stimulus/S217` | 4 | Face identity left (block 3) |
  | `Stimulus/S218` | 5 | Face identity right (block 3) |
  | `Stimulus/S227` | 6 | Face identity left (block 4) |
  | `Stimulus/S228` | 7 | Face identity right (block 4) |
- **Evidence**: DOI 10.1080/1357650X.2025.2591660
- **Kernel Notes**: Tighter window (tmin=-0.2, tmax=0.8) captures early N170/VPP components critical for face identity lateralization. S117/S118 and S217/S218 differ from S127/S128 and S227/S228 by condition type (first digit). ~6,400 trials per identity condition supports robust ERP averaging. Consider grouping by hemisphere (left vs right identity) for binary asymmetry analysis.

### Potential Task 3: Visual Discrimination - House Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, overlap = 0.2 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Stimulus/S11` | 0 | House visual category 1 |
  | `Stimulus/S21` | 1 | House visual category 2 |
  | `Stimulus/S22` | 2 | House visual category 3 |
- **Evidence**: DOI 10.1080/1357650X.2025.2591660
- **Kernel Notes**: Shorter 1s window suitable for visual discrimination tasks with earlier peak latencies. S11 and S21 have ~12,000 trials each; S22 has ~4,000 trials. Class imbalance may require oversampling or class weighting. Overlap at 200ms provides adequate temporal resolution for category-specific visual evoked potentials.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
