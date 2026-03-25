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

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds004902 DOI: https://doi.org/10.18112/openneuro.ds004902.v1.0.8


### Primary Task 2: Publisher-defined BIDS task: Eyesclosed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004902 DOI: https://doi.org/10.18112/openneuro.ds004902.v1.0.8


### Primary Task 3: Publisher-defined BIDS task: Eyesopen
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004902 DOI: https://doi.org/10.18112/openneuro.ds004902.v1.0.8


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
