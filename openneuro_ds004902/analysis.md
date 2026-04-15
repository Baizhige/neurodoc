# Resting-State EEG Dataset for Sleep Deprivation

**Dataset**: `openneuro_ds004902` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004902
**Category**: Biological State | **Subjects**: 71 | **Files (Completed)**: 218 | **Channels**: 61 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG recordings with eyes open and eyes closed were conducted under two conditions: normal sleep and 24-hour sleep deprivation. The study investigates how sleep loss modulates spontaneous brain activity. Subjects participated in two sessions (normal sleep vs sleep-deprived). Files are split by condition (eyesopen/eyesclosed) with 5-minute continuous blocks. Event marker `S 33` (60 total) appears as a resting-state session marker in a subset of files; all other S-codes are rare system markers.

## File Scan Result

> **Kernel SHA256**: `49602d8f0eeb923fef42e76e71d7e0044b0b1af6917d41ef513240bbc140c609`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 33` | 60 | event | raw | Resting-state session marker (BrainVision) |
| `S 44` | 7 | admin | raw | Rare system marker (exclude) |
| `S 45` | 7 | admin | raw | Rare system marker (exclude) |
| `S 55` | 7 | admin | raw | Rare system marker (exclude) |
| `S 66` | 7 | admin | raw | Rare system marker (exclude) |
| `S119` | 7 | admin | raw | Rare system marker (exclude) |
| `boundary` | 14 | event | raw | Boundary marker from data concatenation |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}` | 76 | event | super | Eyes-closed resting-state recording |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}` | 142 | event | super | Eyes-open resting-state recording |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep Deprivation Classification (Normal vs Sleep Deprived)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `normal` | 0 | Normal sleep session (NS) |
  | `sleep_deprived` | 1 | Sleep deprivation session (SD) |
- **Evidence**:
  - DOI: 10.1038/s41597-024-03268-2 — Describes the dataset with 71 participants in counterbalanced NS vs SD within-subject design; 5-minute continuous EEG blocks with 4-second epochs used in validation
  - DOI: 10.1109/tnsre.2025.3547616 — Binary classification between normal and sleep deprived using 4-second non-overlapping windows
- **Kernel Notes**: Segment 5-minute continuous recordings into 75 non-overlapping 4-second epochs (300s ÷ 4s = 75). Assign epoch label based on parent session condition (NS or SD) derived from ses-normal/ses-sleepdeprived folder structure and participants.tsv. S 33 appears in a subset of files (~60) as a BrainVision resting-state marker but does not drive epoch alignment or labeling. S 44/45/55/66/119 are rare admin system markers (7 each) — exclude from all processing. Boundary events (14 total) from data concatenation require appropriate handling during segmentation. Eyes condition (eyes_open/eyes_closed) is accessible via super events as secondary attribute for multi-condition analysis if needed.

### Normal Task 1: Resting-State EEG Exploratory Analysis
- **Task Type**: regression/feature-extraction
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: None — exploratory analysis task
- **Evidence**:
  - DOI: 10.1038/s41597-024-03268-2 — Supports sliding-window analysis approach on continuous resting-state data
- **Kernel Notes**: Segment 5-minute continuous recordings into 2-second epochs with 50% overlap, yielding 149 epochs per file ((300s - 2s) / 1s + 1). Labels derived from filename (eyesopen/eyesclosed) and session metadata (normal/sleepdeprived). Higher temporal resolution with overlapping windows supports frequency-domain feature extraction and connectivity analysis. S 33 is present in subset of files but not used for epoch alignment — condition labels derive from file-level metadata. Exclude boundary events and admin markers (S 44/45/55/66/119).

### Potential Task 1: Sleep Deprivation Detection with Eyes-Condition Stratification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**: None — multi-condition classification using combined session and eyes-condition metadata
- **Kernel Notes**: Stratified classification could distinguish four conditions: (NS, eyes_open), (NS, eyes_closed), (SD, eyes_open), (SD, eyes_closed). Super events provide eyes_condition labels (76 eyes_closed, 142 eyes_open recordings). Labels constructed by combining session metadata (NS/SD) with eyes condition metadata (eyes_open/eyes_closed). Higher temporal resolution (2s, overlap=0.5) may improve fine-grained neural marker detection for sleep deprivation effects under different visual states.