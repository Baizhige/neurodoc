# Embodied Learning for Literacy EEG

**Dataset**: `openneuro_ds004017` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004017
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 126
**Channels**: 65 | **Sampling Rate**: 2048 Hz

## Paradigm

A pre-post intervention study assessing literacy and orthographic processing in children through two tasks: a two-alternative forced choice letter discrimination task (b vs. d confusion) and a visual search task. EEG was recorded across multiple sessions to evaluate the neural effects of an embodied learning intervention on letter processing. Trigger codes 10/20 and 100/200 likely encode the two letter types or correct/incorrect responses.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004017

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `100.0` | 63 files | short | raw | Stimulus onset - letter type B or condition 100 |
| `200.0` | 63 files | short | raw | Stimulus onset - letter type D or condition 200 |
| `20.0` | 61 files | short | raw | Stimulus onset - response or sub-condition 20 |
| `10.0` | 61 files | short | raw | Stimulus onset - response or sub-condition 10 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Letter discrimination (b vs d) under embodied literacy intervention
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`100.0`, `200.0`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `100.0` | 0 | Letter type b (condition 100) |
  | `200.0` | 1 | Letter type d (condition 200) |
- **Super Meta Notes**: (none)
- **Evidence**:
  - DOI: `10.31234/osf.io.zmctf` — This paper analyzes EEG data from Study 1 where 18 children (6-8 years) performed a visual search task discriminating letters 'b' and 'd' under embodied movement (MOVE) vs gaze fixation (CON) conditions, extracting stimulus-locked ERP components (P300a, N200, P300b) from epochs time-locked to target letter onset.
- **Kernel Notes**: Preprocessing: high-pass 0.1 Hz, low-pass 40 Hz, baseline correction -100ms to 0ms, downsample to 512 Hz. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Pre-post intervention longitudinal analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`100.0`, `200.0`, `10.0`, `20.0`]
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `100.0` | 0 | Letter type b (condition 100) |
  | `200.0` | 1 | Letter type d (condition 200) |
  | `10.0` | * | Response/sub-condition 10 (verify mapping) |
  | `20.0` | * | Response/sub-condition 20 (verify mapping) |
- **Notes**: 21 subjects × 6 sessions = 126 files. Pre-post intervention design allows longitudinal analysis of literacy-related neural changes. Events 10.0/20.0 may encode response outcomes or sub-conditions — verify against dataset documentation.

## Data Quality Notes

- Numerical trigger codes; full decoding requires dataset documentation
- 21 subjects x 6 sessions - session-level structure must be considered
- High sampling rate (2048 Hz); consider downsampling for efficiency

