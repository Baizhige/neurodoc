# Rotation-tolerant representations elucidate the time course of high-level object processing

**Dataset**: `openneuro_ds004252` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004252
**Category**: Sensory/Response | **Subjects**: 1 | **Files (Completed)**: 1
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

A single participant viewed visual stimuli of objects at various rotations to investigate the neural time course of rotation-tolerant, high-level object representations. A rapid serial visual presentation (RSVP) design was used with three event types encoding distinct stimulus categories or conditions. The study is a single-subject pilot or proof-of-concept recording.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E 1` | 14400 | event | raw | Stimulus condition 1 (object/rotation category A) |
| `Event/E 2` | 14400 | event | raw | Stimulus condition 2 (object/rotation category B) |
| `Event/E 3` | 120 | event | raw | Stimulus condition 3 (object/rotation category C) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: 60-way object category classification (rotation-tolerant decoding)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Object/rotation condition 1 (subset of 60 objects) |
  | `Event/E 2` | 1 | Object/rotation condition 2 (subset of 60 objects) |
  | `Event/E 3` | 2 | Object/rotation condition 3 (subset of 60 objects) |
- **Evidence**:
  - DOI: 10.31234/osf.io.wp73u — "This study used EEG data from OpenNeuro ds004252 to decode 60-way object classification using multivariate pattern analysis, comparing fixed-rotation decoding with rotation-tolerant decoding, with epochs from -100ms to 800ms relative to stimulus onset."
- **Kernel Notes**: The 60 objects (12 categories × 5 exemplars) are presented at 8 rotations each. Raw events E1-E3 group the stimuli into 3 coarse categories. Verify if finer-grained 60-way labels can be reconstructed from stimulus metadata; otherwise use the 3-class mapping. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Object Category Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 1 subject; not suitable for cross-subject generalization. Event/E 3 count (120) is far lower than E 1 and E 2 (14400 each) - severe class imbalance. Decode exact condition mapping from paper.

| Event | y | Meaning |
|-------|---|------|
| `Event/E 1` | 0 | Object/rotation condition 1 |
| `Event/E 2` | 1 | Object/rotation condition 2 |
| `Event/E 3` | 2 | Object/rotation condition 3 |

## Data Quality Notes

- Single subject; results not generalizable across subjects
- 127 channels (1 reference electrode excluded)
- Severe class imbalance: E 1 and E 2 have 14400 trials each vs. E 3 with only 120


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review