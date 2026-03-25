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
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Stimulus condition mapping for letter discrimination (e.g., b vs d), optionally modeled with pre/post intervention session factor.
- **Evidence**: Study description centers on literacy-related letter processing and intervention effects. Source: https://openneuro.org/datasets/ds004017 DOI: https://doi.org/10.18112/openneuro.ds004017.v1.0.3


### Normal Task 1: Letter Discrimination (b vs d) (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 21 subjects x 6 sessions = 126 files. Codes 10.0/20.0 may indicate sub-conditions or response events - verify against dataset README. Pre-post intervention design allows longitudinal analysis.

| Event | y | Meaning |
 |-------|---|------|
 | `100.0` | 0 | Letter/condition type 100 (e.g., letter b) |
 | `200.0` | 1 | Letter/condition type 200 (e.g., letter d) |
## Data Quality Notes

- Numerical trigger codes; full decoding requires dataset documentation
- 21 subjects x 6 sessions - session-level structure must be considered
- High sampling rate (2048 Hz); consider downsampling for efficiency

## References

- **Reference**: `Embodied Learning for Literacy EEG`
