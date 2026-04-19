# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based motor task with a 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The experimental design includes both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) paradigm sessions, with thirty subjects participating and handedness information available in the participants metadata.

## File Scan Result

> **Kernel SHA256**: `e16d0c8cb2adcc85767cc9744f62a010feb13ae4d5e6bd49459b5909e0a27ce5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 327 | event | raw | Rest/baseline period onset |
| `event_2` | 5090 | event | raw | Trial phase onset: task (in 2-phase paradigm sessions) OR ready (in 4-phase paradigm sessions) |
| `event_3` | 3270 | event | raw | Motor execution phase onset |
| `event_4` | 1237 | event | raw | Inter-trial interval/feedback period onset |
| `event_5` | 1237 | event | raw | Trial phase onset: ready |
| `event_6` | 91 | admin | raw | Unclear |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Motor Execution State Detection
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`event_1`, `event_2`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `event_1` | 0 | Rest/baseline period onset |
  | `event_2` | 1 | Task execution period onset |
- **Evidence**:
  - DOI: 10.1038/s41597-023-02260-6 — Dataset paper describing SMR-BMI paradigm with rest vs motor imagery classification
- **Kernel Notes**: Alignment = onset. Binary classification of active motor execution vs passive rest states. The 3s window captures the task execution phase (~6s duration from events.tsv) while avoiding overlap with the subsequent interval period. Valid across both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) sessions.

### Classical Task 2: Motor Preparation Detection
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.5 s, target_events = [`event_5`, `event_3`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `event_5` | 0 | Ready/preparation phase onset |
  | `event_3` | 1 | Motor execution phase onset |
- **Evidence**:
  - DOI: 10.1038/s41597-023-02260-6 — Dataset paper describing motor preparation and execution phases in SMR-BMI paradigm
- **Kernel Notes**: Alignment = onset. Contrasts motor preparation (ready phase, ~2s) vs motor execution (task phase). The 2.5s window encompasses the ready phase plus margin to capture transition into execution. Valid only for 4-phase paradigm sessions (rest→ready→task→interval).

### Potential Task 1: Trial-Level Motor Learning Regression
- **Task Type**: regression
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`event_2`]
- **Label Route**: misc
- **Label Field**: trial
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `trial` | 1–N (integer) | Trial index within session block |
- **Evidence**:
  - DOI: 10.1038/s41597-023-02260-6 — Dataset paper describes motor learning paradigm; trial progression may reflect performance adaptation
- **Kernel Notes**: The `trial` column from events.tsv provides sequential trial indices within each session. Regression target captures motor learning/progression effects across repeated trials. Epoch window targets task execution phase (event_2) at 2s to avoid overlap with subsequent rest periods.

## Data Quality Notes

- The `device` metadata field is missing across the dataset.
- Event_6 has unclear meaning with 91 occurrences marked as "admin" type.
- Event_2 and event_5 have paradigm-dependent meanings requiring session-aware handling (2-phase vs 4-phase sessions).
- Handedness information is available and complete for all 30 subjects.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
