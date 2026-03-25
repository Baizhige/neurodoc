# EEG During Sport-Related Motor Imagery and Observation Tasks

**Dataset**: `openneuro_ds007327` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007327
**Category**: Action/Output | **Subjects**: 35 | **Files (Completed)**: 105 | **Channels**: 88 | **Sampling Rate**: 1000 Hz

## Paradigm

EEG was recorded during two sports-related tasks (ball passing and dribbling) to study motor intention and motor observation. The paradigm uses a 2x2 design crossing motor intention (MI = motor intention, MO = motor observation) with movement execution modality, yielding four compound conditions: MIMI (imagine intention), MIMO (imagine observation), MOMI (observe intention), MOMO (observe observation). Additional single-factor conditions (MI, MO, MO_MI) and a static/rest baseline are included.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007327

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `MOMI` | 8396 | short | raw | Motor observation of intention trials |
| `MIMO` | 8394 | short | raw | Motor imagination of observation trials |
| `MOMO` | 8394 | short | raw | Motor observation of observation trials |
| `MIMI` | 8335 | short | raw | Motor imagination of intention trials |
| `static` | 4313 | short | raw | Static baseline condition |
| `MO` | 4200 | short | raw | Motor observation condition |
| `MO_MI` | 4198 | short | raw | Motor observation with motor intention |
| `MI` | 4195 | short | raw | Motor intention condition |
| `rest` | 4073 | short | raw | Resting/baseline period |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: The official dataset page describes sport-related motor imagery and motor observation conditions that support a primary motor-intention decoding benchmark. Source: https://openneuro.org/datasets/ds007327


### Normal Task 1: Motor Intention/Observation Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 9-class design; 2x2 factorial core (MIMI/MIMO/MOMI/MOMO ~8300 each) plus single-factor and baseline conditions (~4000 each). 105 files = 35 subjects x 3 task types (ballpass, dribble, passing).

 | Event | y | Meaning |
 |-------|---|---------|
 | `MIMI` | 0 | Motor imagination x intention |
 | `MIMO` | 1 | Motor imagination x observation |
 | `MOMI` | 2 | Motor observation x intention |
 | `MOMO` | 3 | Motor observation x observation |
 | `MI` | 4 | Motor intention |
 | `MO_MI` | 5 | Motor observation with intention |
 | `static` | 6 | Static baseline |
 | `MO` | 7 | Motor observation |
 | `rest` | 8 | Rest baseline |
## Data Quality Notes

- High channel count (88) includes 24 BIP channels for EMG/kinematic data; exclude BIP channels from EEG analysis.
- 35 subjects x 3 task files = 105 files; verify task structure.
- Apply bandpass filter (0.5-40 Hz), remove BIP channels, and artifact reject prior to epoching.

## References

- _No paper reference available_
