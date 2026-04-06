# EEG Resting-State Microstates and Executive Functions

**Dataset**: `openneuro_ds005305` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005305
**Category**: High-level Mental | **Subjects**: 165 | **Files (Completed)**: 165 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Resting-state EEG microstates were recorded to correlate spontaneous brain dynamics with performance on a nine-task battery of executive functions (dual N-back, Stroop, task-switching, etc.). Each file contains alternating eyes-closed (`RS_EC`, 825 total) and eyes-open (`RS_EO`, 660 total) resting blocks. The study investigates whether EEG microstate metrics predict individual differences in executive function. `boundary` (165) is a EEGLAB admin marker; key press events are incidental.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RS_EC` | 825 | event | raw | Resting-state eyes-closed block onset |
| `RS_EO` | 660 | event | raw | Resting-state eyes-open block onset |
| `boundary` | 165 | admin | raw | EEGLAB boundary marker (exclude) |
| `RIGHT pressed`/`RIGHT released` | 26 | admin | raw | Incidental key presses (exclude) |
| `DOWN pressed`/`DOWN released` | 22 | admin | raw | Incidental key presses (exclude) |
| `LEFT pressed`/`LEFT released` | 16 | admin | raw | Incidental key presses (exclude) |
| Other key events | rare | admin | raw | Incidental key presses (exclude) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Eyes Open vs Eyes Closed (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `boundary` (165) and all key press events are admin - exclude. Each resting block is ~30-60 s; sliding windows capture microstate dynamics. RS_EC (825) > RS_EO (660) - slight imbalance.

 | Event | y | Meaning |
 |-------|---|
 | `RS_EC` | 0 | Eyes-closed resting state |
 | `RS_EO` | 1 | Eyes-open resting state |

## Data Quality Notes

- `boundary` is EEGLAB admin marker - exclude.
- Key press events are incidental - exclude.
- Executive function scores in participants.tsv for regression analyses.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review