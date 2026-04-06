# Interval Timing Task

**Dataset**: `openneuro_ds004579` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004579
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed an interval timing task where they estimated durations of different intervals. BrainVision S-codes (S 1-S 7) encode different timing conditions or interval lengths. Participants produced or reproduced time intervals by button press (R 3). The study investigates neural oscillations and temporal processing mechanisms.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | ~30xN | event | raw | Timing condition 1 |
| `S 2` | ~30xN | event | raw | Timing condition 2 |
| `S 3` | ~30xN | event | raw | Timing condition 3 |
| `S 4` | ~30xN | event | raw | Timing condition 4 |
| `S 5` | ~30xN | event | raw | Timing condition 5 |
| `S 6` | ~30xN | event | raw | Timing condition 6 |
| `S 7` | ~30xN | event | raw | Timing condition 7 |
| `R 3` | ~30xN | event | raw | Button press response |
| `boundary` | ~30xN | admin | raw | Recording boundary marker |
| `S255` | ~30xN | admin | raw | BrainVision overflow/system marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 1`, `S 2`, `S 3`, `S 4`, `S 5`, `S 6`, `S 7`, `S255`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Potential Task 1: Timing Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: boundary and S255 are admin events - exclude from target_events. R 3 is a response event - can be used as an additional classification target. S255 is a BrainVision system marker (overflow/sync), not a task event.

| Event | y | Meaning |
 |-------|---|------|
 | `S 1` | 0 | Timing condition 1 |
 | `S 2` | 1 | Timing condition 2 |
 | `S 3` | 2 | Timing condition 3 |
 | `S 4` | 3 | Timing condition 4 |
 | `S 5` | 4 | Timing condition 5 |
 | `S 6` | 5 | Timing condition 6 |
 | `S 7` | 6 | Timing condition 7 |

## Data Quality Notes

- boundary and S255 must be excluded from epoching
- S255 is a BrainVision system marker, not a task event
- 30 subjects with 7 timing conditions


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review