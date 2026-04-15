# EEG-attention-rsvp-exp2

**Dataset**: `openneuro_ds004817` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004817
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 40
**Channels**: 63 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task (Experiment 2) investigating the neural dynamics of prioritizing task-relevant information, using stimuli consisting of small objects superimposed on large letters. Participants performed target detection in rapid streams. Experiment 2 is a companion to Experiment 1 (ds004816) with different stimulus configurations (objects on letters rather than letters on objects).

## File Scan Result

> **Kernel SHA256**: `4c5a8fa7cbcb7a697d658d23470c52977654ba401b8527c802a370281a7cca44`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 138274 | event | raw | Task-relevant (attended) stimulus |
| `E 2` | 138274 | event | raw | Task-irrelevant (unattended) stimulus |
| `E 3` | 3842 | event | raw | Additional stimulus type |
| `boundary` | 20 | event | raw | Artifact boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: RSVP Stimulus Identity Classification (16 objects + 16 letters)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | Task-relevant (attended) stimulus |
  | `E 2` | 1 | Task-irrelevant (unattended) stimulus |
  | `E 3` | 2 | Additional stimulus type |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding classified which of 16 objects or 16 letters was presented from EEG epochs extracted -100ms to 1000ms relative to stimulus onset; 32-class identity problem
- **Kernel Notes**: Aggregate duplicate event formats (E 1 + Event/E 1, E 2 + Event/E 2, E 3 + Event/E 3) into unified classes. Epochs extracted from -100ms to 1000ms relative to stimulus onset aligns with published MVPA analysis.

### Classical Task 2: RSVP Category Classification (bird/fish/boat/plane)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | Attended stimulus → decode category (bird/fish/boat/plane) |
  | `E 2` | 1 | Unattended stimulus → decode category (bird/fish/boat/plane) |
  | `E 3` | 2 | Additional stimulus type → decode category |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding performed to classify object category (bird/fish/boat/plane); attention modulated category-level decodability
- **Kernel Notes**: Same epoch window as stimulus identity. Category labels (bird/fish/boat/plane) require mapping event IDs to stimulus metadata from dataset. Filter boundary events (20 total).

### Classical Task 3: RSVP Animacy Classification (animal/vehicle)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | Attended stimulus → decode animacy (animal/vehicle) |
  | `E 2` | 1 | Unattended stimulus → decode animacy (animal/vehicle) |
  | `E 3` | 2 | Additional stimulus type → decode animacy |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — MVPA decoding performed to classify animacy (animal vs vehicle); animal stimuli = bird/fish, vehicle stimuli = boat/plane
- **Kernel Notes**: Binary animacy classification using same -100ms to 1000ms window. Animal stimuli map to E 1/E 2 for bird/fish; vehicle stimuli map to E 1/E 2 for boat/plane.

### Potential Task 1: RSVP Attention Classification (attended vs unattended)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | Attended stimulus (task-relevant) |
  | `E 2` | 1 | Unattended stimulus (task-irrelevant) |
- **Evidence**:
  - DOI: `10.51628/001c.21174` — Study investigates neural dynamics of prioritizing task-relevant information; attended vs unattended distinction is fundamental to the RSVP paradigm
- **Kernel Notes**: Binary attention classification. Extended baseline window (tmin = -0.2s) captures pre-stimulus attentional state. Aggregate E 1 + Event/E 1 and E 2 + Event/E 2 as unified classes.