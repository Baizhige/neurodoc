# Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts

**Dataset**: `openneuro_ds004784` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004784
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 10 | **Channels**: 264 | **Sampling Rate**: 512 Hz

## Paradigm

Technical validation study using an electrically conductive head phantom to simulate brain activity under various artifact conditions (motion, muscle, eye movements) for testing EEG cleaning algorithms. Code 65471 appears in all 10 files (20 total events); code 65343 appears in all 10 files (10 total events). These likely mark artifact-on vs artifact-off conditions or different artifact types.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004784

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `65471` | 20 | short | raw | Artifact condition marker A (e.g., artifact-on) |
| `65343` | 10 | short | raw | Artifact condition marker B (e.g., clean condition) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Artifact Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`65471`, `65343`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `65471` | 0 | Artifact condition A (artifact-on) |
  | `65343` | 1 | Artifact condition B (artifact-off/clean) |
- **Evidence**:
  - DOI: https://doi.org/10.3390/s23198214 — This paper validates the iCanClean artifact removal algorithm on the OpenNeuro ds004784 phantom EEG dataset for binary artifact condition classification (artifact-on vs artifact-off) using event markers 65471 and 65343.
- **Kernel Notes**: Extract epochs around event codes 65471 and 65343. Apply binary classification to distinguish artifact-on vs artifact-off conditions. Note: Very small dataset (10 files, 30 total events) with class imbalance 2:1.

### Normal Task 1: Artifact Condition Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very small dataset (10 files, 30 total events). Verify code meanings from dataset README. 264 channels - ultra-high density EEG phantom. Class imbalance 2:1 (20 vs 10).

 | Event | y | Meaning |
 |-------|---|---------|
 | `65471` | 0 | Artifact condition A |
 | `65343` | 1 | Artifact condition B |

## Data Quality Notes

- Very small dataset (10 files, 30 events total) - insufficient for standard classification.
- 264-channel phantom EEG; not standard scalp EEG configuration.
- Designed for artifact algorithm validation, not neural decoding.

## References

- **Reference**: `Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts and Example Scripts`
