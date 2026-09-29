# Cross-modal Oddball Task

**Dataset**: `openneuro_ds004574` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004574
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**: Pending

## Paradigm

Participants performed an oddball task with cross-modal stimuli (visual and auditory). Standard stimuli (S 1), deviant stimuli (S 2), and rare stimuli (S 3) were presented in mixed modality streams. The study investigates the mismatch negativity (MMN) and P300 components elicited by deviant stimuli across sensory modalities.

## File Scan Result

> **Kernel SHA256**: `f3871f950ec0b4c90b0b8ea60397e67aebeb4d3fe4fa12366e7b7096bf19c9d3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | 34797 | event | raw | Standard stimulus |
| `S 2` | 34704 | event | raw | Deviant stimulus |
| `S 3` | 33925 | event | raw | Rare/target stimulus |
| `S255` | 2 | event | raw | BrainVision overflow/system marker |
| `boundary` | 148 | event | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Cross-modal Oddball Classification (MMN/P300)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S 1`, `S 2`, `S 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `S 1` | 0 | Standard stimulus |
  | `S 2` | 1 | Deviant stimulus |
  | `S 3` | 2 | Rare/target stimulus |
- **Evidence**:
  - DOI: 10.1101/2022.07.26.22278079 — Preprint describing cross-modal oddball task for MMN and P300 analysis
- **Kernel Notes**: Exclude `boundary` (148 occurrences) and `S255` (2 occurrences) admin markers from epoching. Event counts are balanced (~34k each for S 1, S 2, S 3), consistent with standard oddball probability structure. Mixed modality (visual/auditory) presentation may introduce latency confounds across conditions.

---

### Potential Task 2: Admin Marker Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.1 s, target_events = [`boundary`, `S255`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `boundary` | 0 | Recording boundary marker |
  | `S255` | 1 | BrainVision overflow/system marker |
- **Evidence**: No reference required for potential task; task is plausible from paradigm structure
- **Kernel Notes**: Identify and filter admin markers for clean downstream analysis. S255 appears only twice, boundary appears 148 times across 30 subjects.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
