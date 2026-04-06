# Drum Trainer

**Dataset**: `openneuro_ds004152` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004152
**Category**: Complex Applied | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 31 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants learned and performed specific rhythmic drumming patterns at varying tempos using keyboard keys, receiving adaptive visual feedback on timing accuracy. EEG was recorded continuously during drumming training. Each key press generates a Stimulus event marker; the dataset contains thousands of drumming events per participant (2300-4700 Stimulus events per file).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | ~65000 | event | raw | Individual drum key press / beat onset |
| `New Segment` | 21 | admin | raw | Recording segment boundary |
| `Comment` | 21 | admin | raw | Experimenter comment marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Drum Timing Adjustment Prediction (RewP-based Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 1.5 s, target_events = [`Stimulus`, `feedback_onset` *]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus` | continuous | Drum key press / beat onset |
  | `feedback_onset` * | continuous | Feedback onset (needs verification from events.tsv) |
- **Super Meta Notes**: (none - raw meta level)
- **Evidence**:
  - DOI: 10.1111/psyp.14589 — Regression-based ERP analysis examining whether trial-to-trial fluctuations in RewP (240-340ms at fcZ) predict timing adjustment on subsequent trials during a continuous drumming task at three tempos.
- **Kernel Notes**: 
  1. Extract epochs around each Stimulus event from -1.5s to 1.5s.
  2. Compute RewP amplitude from FCz channel in 240-340ms window post-stimulus.
  3. Regression target: continuous RT adjustment value (positive = slowing, negative = speeding).
  4. Verify 'feedback_onset' event ID mapping from events.tsv - if not present, derive from Stimulus timing + feedback delay.
  5. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Drum Beat Detection (single-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus` | 0 | Drum key press / beat onset |
- **Notes**: Only one event class. Useful for stimulus-locked ERP analysis. New Segment and Comment are admin events, excluded.

## Data Quality Notes

- Very high event rate; check for event jitter in timing accuracy analysis
- Only 21 subjects; limited generalizability
- Paper used 20 participants for RewP analysis - verify subject overlap

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
## Data Quality Notes

- Very high event rate; check for event jitter in timing accuracy analysis
- Only 21 subjects; limited generalizability

