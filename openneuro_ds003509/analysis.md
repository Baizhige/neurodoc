# EEG: Simon Conflict in Parkinson's

**Dataset**: `openneuro_ds003509` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003509
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 84
**Channels**: 67 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

This study investigates mid-frontal theta deficits in Parkinson's disease (PD) patients during a modified Simon reaction-time task that requires cognitive control. Participants (high-performing PD patients and matched controls) performed congruent and incongruent Simon trials where stimulus position and response direction could conflict. The task included both a training phase with reinforcement feedback and a test phase without feedback. Mid-frontal theta (4-8 Hz) activity serves as an index of cognitive control and is modulated by cortical dopamine.

## File Scan Result

> **Kernel SHA256**: `42511851ad2e2f82b4cb6ccf8e24abda912c768bada14cd90c837f8102a7f97d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 5625 | event | raw | Left stimulus position marker |
| `S  2` | 5574 | event | raw | Right stimulus position marker |
| `S  3` | 2148 | event | raw | Training phase correct response |
| `S  4` | 2140 | event | raw | Training phase incorrect response |
| `S  5` | 278 | event | raw | Feedback stimulus (training phase) |
| `S  8` | 13273 | event | raw | Training phase stimulus onset (left) |
| `S  9` | 13268 | event | raw | Training phase stimulus onset (right) |
| `S 10` | 2 | event | raw | Training phase missing response |
| `S 11` | 5 | event | raw | Test phase missing response |
| `S 12` | 1312 | event | raw | Training congruent trial stimulus |
| `S 13` | 1312 | event | raw | Test congruent trial stimulus |
| `S 14` | 1312 | event | raw | Correct response marker (combined phases) |
| `S 21` | 1312 | event | raw | Training incongruent trial stimulus |
| `S 23` | 1312 | event | raw | Training response marker (incongruent condition) |
| `S 24` | 1312 | event | raw | Training response marker (incongruent condition) |
| `S 31` | 1312 | event | raw | Training response marker |
| `S 32` | 1312 | event | raw | Training response marker |
| `S 34` | 1312 | event | raw | Training response marker |
| `S 41` | 1312 | event | raw | Training response marker |
| `S 42` | 1312 | event | raw | Training response marker |
| `S 43` | 1312 | event | raw | Training response marker |
| `S101` | 13277 | event | raw | Test phase stimulus onset (left) |
| `S102` | 13264 | event | raw | Test phase stimulus onset (right) |
| `S103` | 1079 | event | raw | Test response marker |
| `S104` | 934 | event | raw | Test response marker |
| `S105` | 3073 | event | raw | Test response marker |
| `S111` | 1975 | event | raw | Test no-response marker |
| `S112` | 1919 | event | raw | Test no-response marker |
| `S113` | 1972 | event | raw | Test no-response marker |
| `S114` | 1956 | event | raw | Test no-response marker |
| `S121` | 2012 | event | raw | Test response marker |
| `S122` | 1978 | event | raw | Test response marker |
| `S123` | 2012 | event | raw | Test response marker |
| `S124` | 2030 | event | raw | Test response marker |
| `S211` | 1913 | event | raw | Test response marker |
| `S212` | 1931 | event | raw | Test response marker |
| `S213` | 1921 | event | raw | Test response marker |
| `S214` | 1919 | event | raw | Test response marker |
| `S221` | 2044 | event | raw | Test response marker |
| `S222` | 2027 | event | raw | Test response marker |
| `S223` | 2004 | event | raw | Test response marker |
| `S224` | 2014 | event | raw | Test response marker |
| `boundary` | 84 | event | raw | Recording boundary marker (file segmentation) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Conflict Trial Classification (Congruent vs Incongruent)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S 12`, `S 13`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 12` | 0 | Congruent trial (stimulus-response compatible) |
  | `S 12` | 1 | Incongruent trial (stimulus-response conflict) |
  | `S 13` | 0 | Congruent trial (stimulus-response compatible) |
  | `S 13` | 1 | Incongruent trial (stimulus-response conflict) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — SVM classification of congruent vs incongruent Simon trials using theta-band time-frequency ROI features from conflict/error contrasts.
- **Kernel Notes**: Event ID mapping required: S 12 (1312 events) maps to training phase stimuli (Trn Stim), S 13 (1312 events) maps to test phase stimuli (Test Stim). Both events carry congruent/incongruent trial_type labels in events.tsv value column that must be extracted. Baseline window: -300 to -200 ms prior to stimulus. Exclude `boundary` events (n=84). The identical count (1312) across S 12 and S 13 events suggests balanced congruent/incongruent trial distribution within each phase.

### Classical Task 2: Response Outcome Classification (Correct vs Error)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S 14`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 14` | 1 | Correct response |
  | `S 14` | 0 | Error/incorrect response |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — Classification of correct vs error responses using theta-band features, with post-correct and post-error contrast analysis.
- **Kernel Notes**: Event ID S 14 (1312 events) represents combined response markers. Filter by events.tsv value column to separate correct (336 total) from incorrect (334 total). Exclude no-response trials: `S 10` (Trn No Response: 2 events), `S 11` (Test No Response: 5 events), `S 111` (1975 events), `S 112` (1919 events), `S 113` (1972 events), `S 114` (1956 events) — these may represent extended no-response markers requiring clarification. Epoch on response onset to capture error-related negativity and post-error theta activity.

### Normal Task 1: Feedback Processing Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`S 5`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 5` | 0 | Negative feedback (incorrect) |
  | `S 5` | 1 | Positive feedback (correct) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — Study includes training phase with reinforcement feedback; mid-frontal theta is modulated by feedback processing.
- **Kernel Notes**: Event ID S 5 (278 events) maps to feedback stimulus (FB). Only present during training phase; total FB count (168) in original analysis suggests mapping to correct feedback only. May require filtering events.tsv for positive vs negative feedback valence. The shorter count relative to response events suggests only correct-response feedback trials are marked.

### Normal Task 2: Training vs Test Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S 12`, `S 13`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 12` | 0 | Training phase stimulus |
  | `S 12` | 1 | Test phase stimulus |
  | `S 13` | 0 | Training phase stimulus |
  | `S 13` | 1 | Test phase stimulus |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — Paradigm explicitly distinguishes training (with feedback) and test (without feedback) phases; phase-dependent theta modulation patterns expected.
- **Kernel Notes**: Phase discrimination serves as a confound check and enables analysis of training vs test differences in theta dynamics. Use S 12 vs S 13 event IDs as binary labels (0=training, 1=test). Combined with Task 1, allows analysis of conflict effects within each phase separately. Ensure session alignment for multi-session subjects (84 files across 56 subjects indicates ~1.5 sessions per subject on average).