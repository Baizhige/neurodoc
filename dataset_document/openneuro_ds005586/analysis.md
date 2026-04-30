# EEG responses to the number of objects in partially occluded and uncovered scenes

**Dataset**: `openneuro_ds005586` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005586
**Category**: Sensory/Response | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 63 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants passively viewed game boards depicting varying numbers of game pieces under partial occlusion and subsequent uncovering conditions. The study investigates EEG responses to numerosity perception under occlusion, measuring visual evoked potentials to quantify object tracking. Stimulus codes encode number of objects (1xx = 4 visible pieces, 2xx = 32 visible pieces) and condition (occluded vs uncovered).

## File Scan Result

> **Kernel SHA256**: `baf5356b61564a0375f5d160ea4039aaffd7603362c4837beaab1a47ccb903f2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/USB Error - 14:08:14.868077` | 1 | event | raw | USB communication error during recording |
| `New Segment/` | 22 | event | raw | Experiment segment marker |
| `New Segment/USB Connected - 14:08:20.161000` | 1 | event | raw | USB device connected |
| `Stimulus/S 11` | 6875 | event | raw | Condition code (2-digit) |
| `Stimulus/S 15` | 2241 | event | raw | Condition code (2-digit) |
| `Stimulus/S 21` | 6884 | event | raw | Condition code (2-digit) |
| `Stimulus/S 31` | 320 | event | raw | Condition code (2-digit) |
| `Stimulus/S 95` | 14399 | event | raw | Catch/fixation baseline stimulus |
| `Stimulus/S 98` | 9 | event | raw | Maintenance stimulus |
| `Stimulus/S 99` | 21 | event | raw | Maintenance stimulus |
| `Stimulus/S111` | 903 | event | raw | Occluded condition, 4 visible pieces (trial type 1) |
| `Stimulus/S112` | 854 | event | raw | Occluded condition, 4 visible pieces (trial type 2) |
| `Stimulus/S113` | 855 | event | raw | Occluded condition, 4 visible pieces (trial type 3) |
| `Stimulus/S114` | 862 | event | raw | Occluded condition, 4 visible pieces (trial type 4) |
| `Stimulus/S115` | 864 | event | raw | Occluded condition, 4 visible pieces (trial type 5) |
| `Stimulus/S116` | 854 | event | raw | Occluded condition, 4 visible pieces (trial type 6) |
| `Stimulus/S117` | 861 | event | raw | Occluded condition, 4 visible pieces (trial type 7) |
| `Stimulus/S118` | 863 | event | raw | Occluded condition, 4 visible pieces (trial type 8) |
| `Stimulus/S121` | 860 | event | raw | Occluded condition, 4 visible pieces (trial type 9) |
| `Stimulus/S122` | 863 | event | raw | Occluded condition, 4 visible pieces (trial type 10) |
| `Stimulus/S123` | 859 | event | raw | Occluded condition, 4 visible pieces (trial type 11) |
| `Stimulus/S124` | 866 | event | raw | Occluded condition, 4 visible pieces (trial type 12) |
| `Stimulus/S125` | 858 | event | raw | Occluded condition, 4 visible pieces (trial type 13) |
| `Stimulus/S126` | 864 | event | raw | Occluded condition, 4 visible pieces (trial type 14) |
| `Stimulus/S127` | 1413 | event | raw | Occluded condition, 4 visible pieces (trial type 15) |
| `Stimulus/S128` | 861 | event | raw | Occluded condition, 4 visible pieces (trial type 16) |
| `Stimulus/S143` | 40 | event | raw | Occasional condition code |
| `Stimulus/S211` | 862 | event | raw | Uncovered condition, 32 visible pieces (trial type 1) |
| `Stimulus/S212` | 854 | event | raw | Uncovered condition, 32 visible pieces (trial type 2) |
| `Stimulus/S213` | 855 | event | raw | Uncovered condition, 32 visible pieces (trial type 3) |
| `Stimulus/S214` | 862 | event | raw | Uncovered condition, 32 visible pieces (trial type 4) |
| `Stimulus/S215` | 864 | event | raw | Uncovered condition, 32 visible pieces (trial type 5) |
| `Stimulus/S216` | 855 | event | raw | Uncovered condition, 32 visible pieces (trial type 6) |
| `Stimulus/S217` | 861 | event | raw | Uncovered condition, 32 visible pieces (trial type 7) |
| `Stimulus/S218` | 863 | event | raw | Uncovered condition, 32 visible pieces (trial type 8) |
| `Stimulus/S221` | 860 | event | raw | Uncovered condition, 32 visible pieces (trial type 9) |
| `Stimulus/S222` | 863 | event | raw | Uncovered condition, 32 visible pieces (trial type 10) |
| `Stimulus/S223` | 1299 | event | raw | Uncovered condition, 32 visible pieces (trial type 11) |
| `Stimulus/S224` | 866 | event | raw | Uncovered condition, 32 visible pieces (trial type 12) |
| `Stimulus/S225` | 858 | event | raw | Uncovered condition, 32 visible pieces (trial type 13) |
| `Stimulus/S226` | 864 | event | raw | Uncovered condition, 32 visible pieces (trial type 14) |
| `Stimulus/S227` | 853 | event | raw | Uncovered condition, 32 visible pieces (trial type 15) |
| `Stimulus/S228` | 861 | event | raw | Uncovered condition, 32 visible pieces (trial type 16) |
| `Stimulus/S239` | 200 | event | raw | Occasional condition code |
| `Stimulus/S255` | 1 | event | raw | End-of-session marker |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `HEOG_left`, `HEOG_right`, `VEOG_lower`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: ERP Components for Numerosity Perception (Occluded vs Uncovered)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 95`, `Stimulus/S111`, `Stimulus/S112`, `Stimulus/S113`, `Stimulus/S114`, `Stimulus/S115`, `Stimulus/S116`, `Stimulus/S117`, `Stimulus/S118`, `Stimulus/S121`, `Stimulus/S122`, `Stimulus/S123`, `Stimulus/S124`, `Stimulus/S125`, `Stimulus/S126`, `Stimulus/S127`, `Stimulus/S128`, `Stimulus/S211`, `Stimulus/S212`, `Stimulus/S213`, `Stimulus/S214`, `Stimulus/S215`, `Stimulus/S216`, `Stimulus/S217`, `Stimulus/S218`, `Stimulus/S221`, `Stimulus/S222`, `Stimulus/S223`, `Stimulus/S224`, `Stimulus/S225`, `Stimulus/S226`, `Stimulus/S227`, `Stimulus/S228`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 95` | 0 | Catch/fixation baseline |
  | `Stimulus/S111` | 1 | Occluded, 4 visible pieces (trial type 1) |
  | `Stimulus/S112` | 1 | Occluded, 4 visible pieces (trial type 2) |
  | `Stimulus/S113` | 1 | Occluded, 4 visible pieces (trial type 3) |
  | `Stimulus/S114` | 1 | Occluded, 4 visible pieces (trial type 4) |
  | `Stimulus/S115` | 1 | Occluded, 4 visible pieces (trial type 5) |
  | `Stimulus/S116` | 1 | Occluded, 4 visible pieces (trial type 6) |
  | `Stimulus/S117` | 1 | Occluded, 4 visible pieces (trial type 7) |
  | `Stimulus/S118` | 1 | Occluded, 4 visible pieces (trial type 8) |
  | `Stimulus/S121` | 1 | Occluded, 4 visible pieces (trial type 9) |
  | `Stimulus/S122` | 1 | Occluded, 4 visible pieces (trial type 10) |
  | `Stimulus/S123` | 1 | Occluded, 4 visible pieces (trial type 11) |
  | `Stimulus/S124` | 1 | Occluded, 4 visible pieces (trial type 12) |
  | `Stimulus/S125` | 1 | Occluded, 4 visible pieces (trial type 13) |
  | `Stimulus/S126` | 1 | Occluded, 4 visible pieces (trial type 14) |
  | `Stimulus/S127` | 1 | Occluded, 4 visible pieces (trial type 15) |
  | `Stimulus/S128` | 1 | Occluded, 4 visible pieces (trial type 16) |
  | `Stimulus/S211` | 2 | Uncovered, 32 visible pieces (trial type 1) |
  | `Stimulus/S212` | 2 | Uncovered, 32 visible pieces (trial type 2) |
  | `Stimulus/S213` | 2 | Uncovered, 32 visible pieces (trial type 3) |
  | `Stimulus/S214` | 2 | Uncovered, 32 visible pieces (trial type 4) |
  | `Stimulus/S215` | 2 | Uncovered, 32 visible pieces (trial type 5) |
  | `Stimulus/S216` | 2 | Uncovered, 32 visible pieces (trial type 6) |
  | `Stimulus/S217` | 2 | Uncovered, 32 visible pieces (trial type 7) |
  | `Stimulus/S218` | 2 | Uncovered, 32 visible pieces (trial type 8) |
  | `Stimulus/S221` | 2 | Uncovered, 32 visible pieces (trial type 9) |
  | `Stimulus/S222` | 2 | Uncovered, 32 visible pieces (trial type 10) |
  | `Stimulus/S223` | 2 | Uncovered, 32 visible pieces (trial type 11) |
  | `Stimulus/S224` | 2 | Uncovered, 32 visible pieces (trial type 12) |
  | `Stimulus/S225` | 2 | Uncovered, 32 visible pieces (trial type 13) |
  | `Stimulus/S226` | 2 | Uncovered, 32 visible pieces (trial type 14) |
  | `Stimulus/S227` | 2 | Uncovered, 32 visible pieces (trial type 15) |
  | `Stimulus/S228` | 2 | Uncovered, 32 visible pieces (trial type 16) |
- **Evidence**:
  - DOI: 10.1162/jocn_a_02264 — ERP analysis of P1, N1, P2, P3 components in response to partially occluded vs uncovered game board stimuli, epoched -0.2 to 1.0s
  - DOI: 10.1162/jocn.a_02264 — Same publication (duplicate DOI format)
- **Kernel Notes**: Baseline correction from -0.2 to 0s. Apply bandpass filter (1-40 Hz). Artifact rejection before epoching. Stimulus codes: 1xx prefix = occluded with 4 visible pieces, 2xx prefix = uncovered with 32 visible pieces. Class labels y=1 vs y=2 distinguish occlusion condition for classification. Use y=0 (S95) as baseline/fixation rejection criteria.

### Potential Task 1: Binary Occlusion Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S111`, `Stimulus/S112`, `Stimulus/S113`, `Stimulus/S114`, `Stimulus/S115`, `Stimulus/S116`, `Stimulus/S117`, `Stimulus/S118`, `Stimulus/S121`, `Stimulus/S122`, `Stimulus/S123`, `Stimulus/S124`, `Stimulus/S125`, `Stimulus/S126`, `Stimulus/S127`, `Stimulus/S128`, `Stimulus/S211`, `Stimulus/S212`, `Stimulus/S213`, `Stimulus/S214`, `Stimulus/S215`, `Stimulus/S216`, `Stimulus/S217`, `Stimulus/S218`, `Stimulus/S221`, `Stimulus/S222`, `Stimulus/S223`, `Stimulus/S224`, `Stimulus/S225`, `Stimulus/S226`, `Stimulus/S227`, `Stimulus/S228`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S111` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S112` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S113` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S114` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S115` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S116` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S117` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S118` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S121` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S122` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S123` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S124` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S125` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S126` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S127` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S128` | 0 | Occluded (4 visible pieces) |
  | `Stimulus/S211` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S212` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S213` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S214` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S215` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S216` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S217` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S218` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S221` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S222` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S223` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S224` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S225` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S226` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S227` | 1 | Uncovered (32 visible pieces) |
  | `Stimulus/S228` | 1 | Uncovered (32 visible pieces) |
- **Evidence**: DOI: 10.1162/jocn_a_02264 — Paradigm encodes occlusion condition via stimulus code prefix (1xx=occluded, 2xx=uncovered); plausible binary classification from visual evoked responses to occlusion manipulation.
- **Kernel Notes**: Binary classification distinguishing occlusion state. Code prefix 1xx → y=0 (occluded), 2xx → y=1 (uncovered). Excludes 2-digit codes (S11, S15, S21) and catch trials (S95).

### Potential Task 2: Numerosity Discrimination (4 vs 32 Visible Pieces)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S111`, `Stimulus/S112`, `Stimulus/S113`, `Stimulus/S114`, `Stimulus/S115`, `Stimulus/S116`, `Stimulus/S117`, `Stimulus/S118`, `Stimulus/S121`, `Stimulus/S122`, `Stimulus/S123`, `Stimulus/S124`, `Stimulus/S125`, `Stimulus/S126`, `Stimulus/S127`, `Stimulus/S128`, `Stimulus/S211`, `Stimulus/S212`, `Stimulus/S213`, `Stimulus/S214`, `Stimulus/S215`, `Stimulus/S216`, `Stimulus/S217`, `Stimulus/S218`, `Stimulus/S221`, `Stimulus/S222`, `Stimulus/S223`, `Stimulus/S224`, `Stimulus/S225`, `Stimulus/S226`, `Stimulus/S227`, `Stimulus/S228`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S111` | 0 | 4 visible pieces |
  | `Stimulus/S112` | 0 | 4 visible pieces |
  | `Stimulus/S113` | 0 | 4 visible pieces |
  | `Stimulus/S114` | 0 | 4 visible pieces |
  | `Stimulus/S115` | 0 | 4 visible pieces |
  | `Stimulus/S116` | 0 | 4 visible pieces |
  | `Stimulus/S117` | 0 | 4 visible pieces |
  | `Stimulus/S118` | 0 | 4 visible pieces |
  | `Stimulus/S121` | 0 | 4 visible pieces |
  | `Stimulus/S122` | 0 | 4 visible pieces |
  | `Stimulus/S123` | 0 | 4 visible pieces |
  | `Stimulus/S124` | 0 | 4 visible pieces |
  | `Stimulus/S125` | 0 | 4 visible pieces |
  | `Stimulus/S126` | 0 | 4 visible pieces |
  | `Stimulus/S127` | 0 | 4 visible pieces |
  | `Stimulus/S128` | 0 | 4 visible pieces |
  | `Stimulus/S211` | 1 | 32 visible pieces |
  | `Stimulus/S212` | 1 | 32 visible pieces |
  | `Stimulus/S213` | 1 | 32 visible pieces |
  | `Stimulus/S214` | 1 | 32 visible pieces |
  | `Stimulus/S215` | 1 | 32 visible pieces |
  | `Stimulus/S216` | 1 | 32 visible pieces |
  | `Stimulus/S217` | 1 | 32 visible pieces |
  | `Stimulus/S218` | 1 | 32 visible pieces |
  | `Stimulus/S221` | 1 | 32 visible pieces |
  | `Stimulus/S222` | 1 | 32 visible pieces |
  | `Stimulus/S223` | 1 | 32 visible pieces |
  | `Stimulus/S224` | 1 | 32 visible pieces |
  | `Stimulus/S225` | 1 | 32 visible pieces |
  | `Stimulus/S226` | 1 | 32 visible pieces |
  | `Stimulus/S227` | 1 | 32 visible pieces |
  | `Stimulus/S228` | 1 | 32 visible pieces |
- **Evidence**: Plausible from paradigm — numerosity perception under occlusion is a core research question; DOI 10.1162/jocn_a_02264 shows differential ERP responses to different numerosity conditions.
- **Kernel Notes**: Binary numerosity discrimination. Code prefix 1xx = 4 visible pieces → y=0, Code prefix 2xx = 32 visible pieces → y=1. Same epoching as occlusion task but targeting distinct numerosity dimension.

### Potential Task 3: Multi-Condition Classification (3 Classes)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 95`, `Stimulus/S111`, `Stimulus/S127`, `Stimulus/S211`, `Stimulus/S223`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--- |--------|
  | `Stimulus/S 95` | 0 | Catch/fixation baseline |
  | `Stimulus/S111` | 1 | Occluded, 4 pieces (representative) |
  | `Stimulus/S127` | 1 | Occluded, 4 pieces (alternate code) |
  | `Stimulus/S211` | 2 | Uncovered, 32 pieces (representative) |
  | `Stimulus/S223` | 2 | Uncovered, 32 pieces (alternate code) |
- **Evidence**: Plausible from paradigm — multi-class discrimination between baseline, occluded, and uncovered conditions.
- **Kernel Notes**: Three-class classification: y=0 (baseline/fixation), y=1 (occluded with 4 visible pieces), y=2 (uncovered with 32 visible pieces). Selected representative event codes; full multi-class mapping available in Normal Task 1.

### Potential Task 4: Catch Trial Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 95`, `Stimulus/S111`, `Stimulus/S112`, `Stimulus/S113`, `Stimulus/S114`, `Stimulus/S115`, `Stimulus/S116`, `Stimulus/S117`, `Stimulus/S118`, `Stimulus/S121`, `Stimulus/S122`, `Stimulus/S123`, `Stimulus/S124`, `Stimulus/S125`, `Stimulus/S126`, `Stimulus/S127`, `Stimulus/S128`, `Stimulus/S211`, `Stimulus/S212`, `Stimulus/S213`, `Stimulus/S214`, `Stimulus/S215`, `Stimulus/S216`, `Stimulus/S217`, `Stimulus/S218`, `Stimulus/S221`, `Stimulus/S222`, `Stimulus/S223`, `Stimulus/S224`, `Stimulus/S225`, `Stimulus/S226`, `Stimulus/S227`, `Stimulus/S228`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|--- |--------|
  | `Stimulus/S 95` | 1 | Catch/fixation trial |
  | all others | 0 | Experimental stimulus |
- **Evidence**: Supported by event structure — S95 (14399 events) is the dominant event type representing catch/fixation baseline trials interspersed throughout the experiment.
- **Kernel Notes**: Binary detection of catch/fixation trials vs experimental stimuli. High class imbalance expected (S95 has 14399 events vs ~8000 total experimental events). Consider undersampling or class weighting.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
