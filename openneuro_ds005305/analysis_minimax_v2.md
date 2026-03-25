# EEG Resting-State Microstates and Executive Functions

**Dataset**: `openneuro_ds005305` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005305
**Category**: High-level Mental | **Subjects**: 165 | **Files (Completed)**: 165 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Resting-state EEG microstates were recorded to correlate spontaneous brain dynamics with performance on a nine-task battery of executive functions (dual N-back, Stroop, task-switching, etc.). Each file contains alternating eyes-closed (`RS_EC`, 825 total) and eyes-open (`RS_EO`, 660 total) resting blocks. The study investigates whether EEG microstate metrics predict individual differences in executive function. `boundary` (165) is a EEGLAB admin marker; key press events are incidental.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005305

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RS_EC` | 825 | rest | raw | Resting-state eyes-closed block onset |
| `RS_EO` | 660 | rest | raw | Resting-state eyes-open block onset |
| `boundary` | 165 | admin | raw | EEGLAB boundary marker (exclude) |
| `RIGHT pressed`/`RIGHT released` | 26 | admin | raw | Incidental key presses (exclude) |
| `DOWN pressed`/`DOWN released` | 22 | admin | raw | Incidental key presses (exclude) |
| `LEFT pressed`/`LEFT released` | 16 | admin | raw | Incidental key presses (exclude) |
| Other key events | rare | admin | raw | Incidental key presses (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Normal Task 1: Eyes Open vs Eyes Closed (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `Investigating the relationship between Resting-State EEG Microstates and Executive Functions: A Null Finding`
