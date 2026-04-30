# A dataset recorded during development of an affective brain-computer music interface: testing session

**Dataset**: `openneuro_ds002723` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002723
**Category**: Complex Applied | **Subjects**: 8 | **Files (Completed)**: 44 | **Channels**: 37 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants interacted with a real-time affective brain-computer music interface (BCMI) that modified music on-the-fly based on detected emotional states, aiming to induce specific target affective trajectories. This is the testing session of the BCI system (see also ds002722 calibration and ds002724 training sessions). Codes 1-9 encode the target or detected affective music conditions.

## File Scan Result

> **Kernel SHA256**: `567d94e30faa6107dc4c0b55e4c1c3e13d47c23ef7830f2bd9f83748c7437e1c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Affective Music Condition Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, overlap = 0.0, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `1` | 0 | Music condition 1 |
  | `2` | 1 | Music condition 2 |
  | `3` | 2 | Music condition 3 |
  | `4` | 3 | Music condition 4 |
  | `5` | 4 | Music condition 5 |
  | `6` | 5 | Music condition 6 |
  | `7` | 6 | Music condition 7 |
  | `9` | 7 | Music condition 9 |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0507-6 — Data descriptor explicitly describing the BCMI testing dataset (ds002723) with 8 participants, ~1.3 hours per participant of EEG+ECG+GSR recordings. The synthetic music conditions 1-9 are used as affective state markers, with condition 8 excluded from analysis per the experimental protocol.
- **Kernel Notes**: Events are long-type markers representing sustained 60-second trials with three distinct phases: 20s target affective state, 20s identify state, and 20s alter state. Use epoch_by_long_event_hdf5 to extract the full 60s window capturing the complete affective trajectory. Verify EEG-only channel selection from the 37-channel array (includes physiological channels). Validate channel count consistency across subjects before pooling.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
