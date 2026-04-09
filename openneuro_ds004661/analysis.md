# ANDI: Auditory N-back Dual-task EEG

**Dataset**: `openneuro_ds004661` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004661
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 17 | **Channels**: 64 | **Sampling Rate**: 128 Hz

## Paradigm

A dual-task paradigm combining a guided visual search task (tracking a red annulus) with an auditory N-back working memory task to study cognitive interference. Event code `10` marks the dominant condition (likely standard/no-target trials, 29,820 total) and `11` marks the minority condition (likely target/match trials, 2,948 total). The large imbalance between codes suggests `10` = non-target and `11` = N-back target detection.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `10` | 29820 | short | raw | Non-target trial (dominant condition) |
| `11` | 2948 | short | raw | N-back target match (minority condition) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

- **Reference**: `Ries, et al., 2016`

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Nback
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004661 DOI: https://doi.org/10.18112/openneuro.ds004661.v1.1.0


### Normal Task 1: Target vs Non-target N-back Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Strong class imbalance (29,820 vs 2,948 ~ 10:1); undersample class 0 or use weighted loss. Low sampling rate (128 Hz) limits spectral resolution. Verify code meanings from dataset README or Ries et al., 2016.

 | Event | y | Meaning |
 |-------|---|---------|
 | `10` | 0 | Non-target trial |
 | `11` | 1 | N-back target match |

## Data Quality Notes

- Only 2 event codes; binary classification.
- Strong class imbalance (~10:1); undersample majority class.
- Low sampling rate (128 Hz); limited for high-frequency analyses.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004661