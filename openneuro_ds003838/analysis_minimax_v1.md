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

### Primary Task 1: Memory vs Control Task Classification (Cognitive Load)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 17.5 s, overlap = 0.0, target_events = [`memory task (memorize digits)`, `control task (listen without memorizing)`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `control task (listen without memorizing)` | 0 | Passive listening condition (no memory load) |
  | `memory task (memorize digits)` | 1 | Active memorization condition (working memory engaged) |
- **Evidence**:
  - DOI: 10.1038/s41598.023.48917.5 — Analyzes PPG and ECG data from OpenNeuro ds003838 to investigate how pulse wave amplitude and heart rate track cognitive load during digit span task comparing memory vs control conditions.

### Primary Task 2: Correct vs Error Memory Encoding (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.5 s, target_events = [`memory .*/correct`, `memory .*/error`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `memory .*/correct` | 0 | Digit correctly recalled later |
  | `memory .*/error` | 1 | Digit forgotten later |
- **Evidence**:
  - DOI: 10.1038/s41597.022.01414.2 — Data descriptor describing 64-channel EEG, ECG, PPG and pupillometry recordings from 86 participants performing digit span task with event codes encoding recall outcome (correct vs error) for binary classification.
  - DOI: 10.1111/psyp.14275 — Analyzes EEG and pupillometric data to examine working memory overload effects, epoching data from −1500 to 3500 ms relative to digit presentation and classifying correct vs error recall across digit sequences.

### Normal Task 1: Correct vs Error Memory Encoding (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Events encode digit position, sequence length, and recall outcome. Note this dataset contains only 2-channel ECG/PPG data (not EEG cap channels); EEG data may be in a separate modality. STATUS is an admin marker and must be excluded. Aggregate correct vs error across all sequence lengths for binary classification.

| Event | y | Meaning |
 |-------|---|------|
 | `memory .*/correct` (all correct events) | 0 | Digit correctly recalled later |
 | `memory .*/error` (all error events) | 1 | Digit forgotten later |

## Data Quality Notes

- Only 2 channels (PPG + ECG) - this is a physiological signal dataset, not a scalp EEG cap
- EEG data may be stored separately; verify file naming convention
- Large number of event subtypes (~30 distinct labels); grouping by outcome (correct/error) is necessary

## References

- **Reference**: `EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task`
