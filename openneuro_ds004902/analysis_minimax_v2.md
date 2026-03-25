# Resting-State EEG Dataset for Sleep Deprivation

**Dataset**: `openneuro_ds004902` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004902
**Category**: Biological State | **Subjects**: 71 | **Files (Completed)**: 218 | **Channels**: 61 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings with eyes open and eyes closed were conducted under two conditions: normal sleep and 24-hour sleep deprivation. The study investigates how sleep loss modulates spontaneous brain activity. Subjects participated in two sessions (normal sleep vs sleep-deprived). Files are split by condition (eyesopen/eyesclosed) with 5-minute continuous blocks. Event marker `S 33` (60 total) appears as a resting-state session marker in a subset of files; all other S-codes are rare system markers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004902

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 33` | 60 | rest | raw | Resting-state session marker (BrainVision) |
| `S 45` | 7 | admin | raw | Rare system marker (exclude) |
| `S 44` | 7 | admin | raw | Rare system marker (exclude) |
| `S 55` | 7 | admin | raw | Rare system marker (exclude) |
| `S119` | 7 | admin | raw | Rare system marker (exclude) |
| `S 66` | 7 | admin | raw | Rare system marker (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 33`, `S 45`, `S 44`, `S 55`, `S119`, `S 66`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep Deprivation Classification (Normal vs Sleep Deprived)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `normal` | 0 | Normal sleep session (NS) |
  | `sleep_deprived` | 1 | Sleep deprivation session (SD) |
- **Super Meta Notes**: Derived from session metadata (ses-normal vs ses-sleepdeprived folders and participants.tsv), not from raw event markers. Each 5-minute recording belongs to either NS or SD session; kernel assigns label based on which session the file belongs to. Condition labels (eyesopen/eyesclosed) are available as secondary attribute.
- **Evidence**:
  - DOI: 10.1038/s41597-024-03268-2 — Resting-state EEG dataset for sleep deprivation with 4-second epochs used in validation
  - DOI: 10.1109/tnsre.2025.3547616 — Binary classification between normal and sleep deprived using 4-second non-overlapping windows
- **Kernel Notes**: Segment 5-minute continuous recordings into 75 non-overlapping 4-second epochs (300s/4s). Assign epoch label based on parent session condition (NS or SD) from folder/participants.tsv. S 33 appears in subset of files but is not used for labeling; condition is file-level metadata. (replaces Primary Tasks 1-3 from original analysis.md)

### Normal Task 1: Sleep Deprivation Resting-State Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None
- **Notes**: Majority of files have no event markers - purely continuous resting-state. Use filename-derived or participants.tsv condition labels (eyesopen/eyesclosed x normal/deprived) for downstream classification. S 44/45/55/66/119 are rare admin system markers - exclude.


## Data Quality Notes

- Most files have no event markers; condition derived from filename (eyesopen/eyesclosed).
- Session condition (normal sleep / sleep deprivation) in participants.tsv.
- S 44/45/55/66/119 are rare admin BrainVision system markers - exclude.

## References

- **Reference**: `Xiang, C., Fan, X., Bai, D. et al. A resting-state EEG dataset for sleep deprivation. Sci Data 11, 427 (2024).`
