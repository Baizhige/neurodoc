# EEG-attention-rsvp-exp2

**Dataset**: `openneuro_ds004817` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004817
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 40
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task (Experiment 2) investigating the neural dynamics of prioritizing task-relevant information, using stimuli consisting of small objects superimposed on large letters. Participants performed target detection in rapid streams. Experiment 2 is a companion to Experiment 1 (ds004816) with different stimulus configurations (objects on letters rather than letters on objects).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 69137 | event | raw | RSVP event type 1 (task-relevant stimulus) |
| `E 2` | 69137 | event | raw | RSVP event type 2 (task-irrelevant stimulus) |
| `1` | 29376 | event | raw | Trigger code 1 (response or condition marker) |
| `0` | 29376 | event | raw | Trigger code 0 |
| `Event/E 1` | 10385 | event | raw | RSVP event type 1 (alternate format) |
| `Event/E 2` | 10385 | event | raw | RSVP event type 2 (alternate format) |
| `E 3` | 1921 | event | raw | RSVP event type 3 |
| `Event/E 3` | 289 | event | raw | RSVP event type 3 (alternate format) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: RSVP Stimulus Identity Classification (16 objects + 16 letters)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`, `Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` / `Event/E 1` | 0 | Task-relevant (attended) stimulus |
  | `E 2` / `Event/E 2` | 1 | Task-irrelevant (unattended) stimulus |
  | `E 3` / `Event/E 3` | 2 | Additional stimulus type |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding classified which of 16 objects or 16 letters was presented from EEG epochs extracted -100ms to 1000ms relative to stimulus onset
- **Kernel Notes**: Aggregate duplicate event formats (E 1 + Event/E 1) into single classes. Epochs extracted from -100ms to 1000ms relative to stimulus onset. MVPA classifier trained on 32-class problem (16 objects + 16 letters). (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: RSVP Category Classification (bird/fish/boat/plane)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`, `Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` / `Event/E 1` | 0 | Attended stimulus → decode category (bird/fish/boat/plane) |
  | `E 2` / `Event/E 2` | 1 | Unattended stimulus → decode category (bird/fish/boat/plane) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding performed to classify object category (bird/fish/boat/plane)
- **Kernel Notes**: Same epoch window as stimulus identity. Category labels derived from stimulus image files (not directly in events). Requires mapping event IDs to stimulus metadata from dataset.

### Classical Task 3: RSVP Animacy Classification (animal/vehicle)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`, `Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` / `Event/E 1` | 0 | Attended stimulus → decode animacy (animal/vehicle) |
  | `E 2` / `Event/E 2` | 1 | Unattended stimulus → decode animacy (animal/vehicle) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding performed to classify animacy (animal vs vehicle)
- **Kernel Notes**: Binary animacy classification. Animal stimuli = bird/fish; Vehicle stimuli = boat/plane.

### Potential Task 1: RSVP target classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Companion to ds004816 (Experiment 1). Event/E 1 and Event/E 2 are identical events in different naming format - treat as same class or aggregate.

| Event | y | Meaning |
 |-------|---|------|
 | `E 1` | 0 | RSVP event type 1 |
 | `E 2` | 1 | RSVP event type 2 |
 | `E 3` | 2 | RSVP event type 3 |
 | `1` | 3 | Response/condition code 1 |
 | `0` | 4 | Response/condition code 0 |

## Data Quality Notes

- E 1/Event/E 1 and E 2/Event/E 2 are duplicate event formats - aggregate for analysis.
- Companion dataset: ds004816 is Experiment 1.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review