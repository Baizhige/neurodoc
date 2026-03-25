# EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task

**Dataset**: `openneuro_ds003838` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003838/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 86 | **Files (Completed)**: 296
**Channels**: 2 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a classic digit span working memory task involving serial recall of digit sequences of 5, 9, or 13 digits, along with a separate eyes-closed resting state condition. Each digit in a sequence was marked with an event indicating the digit position, sequence length, and whether it was later correctly recalled or forgotten. The dataset also includes ECG/PPG physiological signals recorded simultaneously with EEG.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003838/versions/1.0.0

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `memory X/05 correct` | high | short | raw | Digit X in 5-item sequence, correctly recalled |
| `memory X/09 correct` | high | short | raw | Digit X in 9-item sequence, correctly recalled |
| `memory X/13 correct` | high | short | raw | Digit X in 13-item sequence, correctly recalled |
| `memory X/05 error` | moderate | short | raw | Digit X in 5-item sequence, forgotten |
| `memory X/09 error` | moderate | short | raw | Digit X in 9-item sequence, forgotten |
| `memory X/13 error` | high | short | raw | Digit X in 13-item sequence, forgotten |
| `STATUS` | 148 | admin | raw | System/hardware status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Correct vs Error Memory Encoding (binary classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`memory X/05 correct`, `memory X/09 correct`, `memory X/13 correct`, `memory X/05 error`, `memory X/09 error`, `memory X/13 error`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `memory X/05 correct` | 0 | Digit correctly recalled later (5-item sequence) |
  | `memory X/09 correct` | 0 | Digit correctly recalled later (9-item sequence) |
  | `memory X/13 correct` | 0 | Digit correctly recalled later (13-item sequence) |
  | `memory X/05 error` | 1 | Digit forgotten later (5-item sequence) |
  | `memory X/09 error` | 1 | Digit forgotten later (9-item sequence) |
  | `memory X/13 error` | 1 | Digit forgotten later (13-item sequence) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01414-2 — Data descriptor paper confirms this dataset contains 64-channel EEG with digit span task events encoding sequence length and recall outcome; paper performs binary classification of correct vs error memory encoding.
  - DOI: 10.1111/psyp.14275 — Analyzes EEG and pupillometric data from this dataset to examine working memory overload effects, epoching data from −1500 to 3500 ms relative to digit presentation and classifying correct vs error recall across digit sequences of 5, 9, and 13 items.
- **Kernel Notes**: Aggregate all correct events (regardless of digit position X) as class 0, all error events as class 1. Exclude `STATUS` (admin marker). Verify event ID mapping from events.tsv — raw event IDs contain placeholder 'X' for digit position but kernel should match pattern `memory .*/correct` and `memory .*/error`. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Working Memory Load Classification (multi-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.5 s *, target_events = [`memory X/05 correct`, `memory X/09 correct`, `memory X/13 correct`, `memory X/05 error`, `memory X/09 error`, `memory X/13 error`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `memory X/05 correct` | 0 | Low load (5 digits) correctly recalled |
  | `memory X/05 error` | 0 | Low load (5 digits) forgotten |
  | `memory X/09 correct` | 1 | Medium load (9 digits) correctly recalled |
  | `memory X/09 error` | 1 | Medium load (9 digits) forgotten |
  | `memory X/13 correct` | 2 | High load (13 digits) correctly recalled |
  | `memory X/13 error` | 2 | High load (13 digits) forgotten |
- **Evidence**:
  - DOI: 10.1111/psyp.14275 — Examines working memory overload effects by classifying across digit sequences of 5, 9, and 13 items (load levels).
- **Kernel Notes**: Class labels represent cognitive load level (5=low, 9=medium, 13=high), ignoring recall outcome for load classification. Paper epoched [−1500 3500 ms]; kernel should verify timing from events.tsv. *Parameters marked with * are inferred from paper methodology, not explicitly stated for this exact dataset.

### Normal Task 1: Publisher-defined BIDS task: Mixed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003838/versions/1.0.0 DOI: https://doi.org/10.18112/openneuro.ds003838.v1.0.6


## Data Quality Notes

- Only 2 channels (PPG + ECG) - this is a physiological signal dataset, not a scalp EEG cap
- EEG data may be stored separately; verify file naming convention
- Large number of event subtypes (~30 distinct labels); grouping by outcome (correct/error) is necessary

## References

- **Reference**: `EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task`
