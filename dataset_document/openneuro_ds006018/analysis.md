# Cognitive Electrophysiology in Socioeconomic Context in Adulthood: An EEG dataset

**Dataset**: `openneuro_ds006018` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006018
**Category**: High-level Mental | **Subjects**: 127 | **Files (Completed)**: 357 | **Channels**: 31 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

A suite of standardized ERP tasks from the ERP CORE compendium (Kappenman et al. 2021) measuring neural correlates of perception, cognition, and action in adults in relation to socioeconomic status and ADHD symptoms. Tasks include N170 (face perception), MMN (mismatch negativity), N2pc (visual attention), P3 (cognitive updating), N400 (semantic processing), ERN (error monitoring), and LRP (lateralized readiness potential).

## File Scan Result

> **Kernel SHA256**: `7998c7fdd31fcb765d3a858c2d64059ceff98c366149177134ff2e5696d06109`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Buffer Overflow` | 14 | event | raw | System buffer overflow marker |
| `New Segment/` | 14 | event | raw | New recording segment marker |
| `New Segment/LostSamples: 1072` | 1 | event | raw | Segment with 1072 lost samples |
| `New Segment/LostSamples: 264` | 1 | event | raw | Segment with 264 lost samples |
| `S  1` | 106 | event | raw | N170 task filler stimulus |
| `S  2` | 69 | event | raw | N170 task filler stimulus |
| `S 11` | 8263 | event | raw | Standard stimulus (non-target) |
| `S 12` | 8252 | event | raw | Standard stimulus (non-target) |
| `S 13` | 818 | event | raw | Standard stimulus |
| `S 14` | 814 | event | raw | Standard stimulus |
| `S 15` | 812 | event | raw | Standard stimulus |
| `S 21` | 8244 | event | raw | Standard stimulus |
| `S 22` | 8268 | event | raw | Standard stimulus |
| `S 23` | 810 | event | raw | Standard stimulus |
| `S 24` | 810 | event | raw | Standard stimulus |
| `S 25` | 810 | event | raw | Standard stimulus |
| `S 31` | 806 | event | raw | MMN task stimulus |
| `S 32` | 806 | event | raw | MMN task stimulus |
| `S 33` | 806 | event | raw | MMN task stimulus |
| `S 34` | 806 | event | raw | MMN task stimulus |
| `S 35` | 806 | event | raw | MMN task stimulus |
| `S 41` | 816 | event | raw | N2pc task stimulus |
| `S 42` | 817 | event | raw | N2pc task stimulus |
| `S 43` | 818 | event | raw | N2pc task stimulus |
| `S 44` | 816 | event | raw | N2pc task stimulus |
| `S 45` | 815 | event | raw | N2pc task stimulus |
| `S 51` | 836 | event | raw | LRP task stimulus |
| `S 52` | 836 | event | raw | LRP task stimulus |
| `S 53` | 836 | event | raw | LRP task stimulus |
| `S 54` | 836 | event | raw | LRP task stimulus |
| `S 55` | 836 | event | raw | LRP task stimulus |
| `S 70` | 7977 | event | raw | N400 task prime stimulus |
| `S 80` | 30199 | event | raw | Standard tone (frequent, MMN) |
| `S111` | 9971 | event | raw | Prime stimulus (N400) |
| `S112` | 3315 | event | raw | Target stimulus (N400-eliciting) |
| `S121` | 8449 | event | raw | Standard stimulus |
| `S122` | 4665 | event | raw | Search array with target present |
| `S180` | 1710 | event | raw | N170 face stimulus |
| `S201` | 40081 | event | raw | Deviant tone (oddball, MMN-eliciting) |
| `S202` | 6292 | event | raw | Novel/deviant stimulus |
| `S211` | 3707 | event | raw | Oddball/target stimulus (P300-eliciting) |
| `S212` | 10400 | event | raw | Search array with different target color |
| `S221` | 5197 | event | raw | Error response trial (ERN) |
| `S222` | 9017 | event | raw | Correct response trial (CRN) |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `HEL`, `HER`, `LM`, `RM`, `VER`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Active Visual Oddball (P300) binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`S211`, `S 11`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 11` | 0 | Standard stimulus (non-target) |
  | `S211` | 1 | Oddball/target stimulus (P300 eliciting) |
- **Evidence**:
  - DOI: `10.1109/BIBM66473.2025.11356119` — Uses Active Visual Oddball (AVO) task from openneuro_ds006018 for binary single-trial classification of oddball versus standard stimuli under a P300 paradigm, with epochs extracted from -100ms to +1000ms around stimulus onset.
  - DOI: `10.1038/s41597-025-05209-z` — Describes openneuro_ds006018 dataset containing EEG recordings from 127 young adults during ERP CORE paradigms including active visual oddball (P300), with stimulus event codes S211 (target) and S 11 (standard).
- **Kernel Notes**: Map S 11 to standard (non-target) and S211 to oddball (target) labels. Apply baseline correction [-0.1, 0] s. Filter 0.1-40 Hz. Verify event ID mapping from events.tsv.

### Potential Task 1: Passive Auditory Oddball (MMN) binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S201`, `S 80`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 80` | 0 | Standard tone (frequent) |
  | `S201` | 1 | Deviant tone (oddball, MMN-eliciting) |
- **Evidence**:
  - DOI: `10.1038/s41597-025-05209-z` — Describes openneuro_ds006018 dataset containing EEG recordings during passive auditory oddball (MMN) paradigm with stimulus event codes S 80 (standard) and S201 (deviant).
- **Kernel Notes**: Epoch standard MMN window [-0.2, 1.0] s. Apply standard MMN analysis pipeline. Verify event ID mapping from events.tsv.

### Potential Task 2: Visual Search (N2pc) binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`S212`, `S122`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S122` | 0 | Search array with target present (color-specific) |
  | `S212` | 1 | Search array with different target color |
- **Evidence**:
  - DOI: `10.1038/s41597-025-05209-z` — Describes openneuro_ds006018 dataset containing EEG recordings during visual search task (N2pc paradigm) with stimulus event codes including S122 and S212.
- **Kernel Notes**: N2pc requires contralateral-ipsilateral difference wave analysis. Verify event ID mapping from events.tsv.

### Potential Task 3: Flanker Task (ERN) binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`S221`, `S222`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S221` | 0 | Correct response trial (CRN) |
  | `S222` | 1 | Error response trial (ERN) |
- **Evidence**:
  - DOI: `10.1038/s41597-025-05209-z` — Describes openneuro_ds006018 dataset containing EEG recordings during flanker ERN paradigm with stimulus event codes S221 (error) and S222 (correct response).
- **Kernel Notes**: ERN is response-locked requiring [-0.5, 0.5]s window centered on response onset. Monitor FCz for ERN and Cz for CRN.

### Potential Task 4: Semantic Processing (N400) binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S111`, `S112`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S111` | 0 | Prime stimulus |
  | `S112` | 1 | Target stimulus (N400-eliciting) |
- **Evidence**:
  - DOI: `10.1038/s41597-025-05209-z` — Describes openneuro_ds006018 dataset containing EEG recordings during N400 semantic priming paradigm with stimulus event codes S111 and S112.
- **Kernel Notes**: N400 analysis requires centroparietal ROI for amplitude measurement. Epoch window [-0.2, 1.0]s captures N400 peak (~300-500ms).

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
