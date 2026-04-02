# A multi-subject and multi-session EEG dataset for modelling human visual object recognition

**Dataset**: `openneuro_ds005589` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005589
**Category**: Sensory/Response | **Subjects**: 32 | **Files (Completed)**: 1592 | **Channels**: 133 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants underwent Rapid Serial Visual Presentation (RSVP) at 5 Hz and a low-speed visual presentation task to record brain responses to visual object recognition across multiple image categories. Codes 1-20 correspond to object categories in the low-speed task; codes 21-27 to RSVP categories; code 99 is catch trials; codes 252/254 are feedback. Multiple sessions were recorded per subject.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005589

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `252` | 141374 | short | raw | Correct response feedback |
| `1`-`20` | ~80332 each | short | raw | Object category codes 1-20 (low-speed presentation) |
| `99` | ~157200 | short | raw | Catch trial |
| `254` | ~40000 | short | raw | Incorrect response feedback |
| `21`-`27` | ~798 each | short | raw | Object category codes 21-27 (RSVP task) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: 20-Category Visual Object Recognition Decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 0.5 s, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `99`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Object category 1 |
  | `2` | 1 | Object category 2 |
  | `3` | 2 | Object category 3 |
  | `4` | 3 | Object category 4 |
  | `5` | 4 | Object category 5 |
  | `6` | 5 | Object category 6 |
  | `7` | 6 | Object category 7 |
  | `8` | 7 | Object category 8 |
  | `9` | 8 | Object category 9 |
  | `10` | 9 | Object category 10 |
  | `11` | 10 | Object category 11 |
  | `12` | 11 | Object category 12 |
  | `13` | 12 | Object category 13 |
  | `14` | 13 | Object category 14 |
  | `15` | 14 | Object category 15 |
  | `16` | 15 | Object category 16 |
  | `17` | 16 | Object category 17 |
  | `18` | 17 | Object category 18 |
  | `19` | 18 | Object category 19 |
  | `20` | 19 | Object category 20 |
  | `99` | 20 | Catch trial (special stimulus) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-04843-x — This paper presents the MSS dataset (openneuro_ds005589) with ~800,000 RSVP trials and ~40,000 low-speed trials for 20-category visual object recognition, using epochs of 0-500ms post-stimulus for EEG classification validation with a fully connected neural network.
- **Kernel Notes**: Use 500ms epochs from stimulus onset (tmin=0s, tmax=0.5s). Map event IDs 1-20 to labels 0-19 for 20-category classification. Event ID 99 represents catch/special stimuli (label 20). Filter out feedback codes 252/254 before training or use them as separate auxiliary labels. Apply bandpass filter (1-40 Hz) and baseline correction. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Visual Object Recognition (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30 event classes. Primary task: decode object category from EEG (codes 1-20 or 21-27). Codes 252/254 and 99 may be used for filtering.

 | Event | y | Meaning |
 |-------|---|-|
 | `1` | 0 | Object category 1 |
 | `2` | 1 | Object category 2 |
 | `3` | 2 | Object category 3 |
 | `4` | 3 | Object category 4 |
 | `5` | 4 | Object category 5 |
 | `6` | 5 | Object category 6 |
 | `7` | 6 | Object category 7 |
 | `8` | 7 | Object category 8 |
 | `9` | 8 | Object category 9 |
 | `10` | 9 | Object category 10 |
 | `11` | 10 | Object category 11 |
 | `12` | 11 | Object category 12 |
 | `13` | 12 | Object category 13 |
 | `14` | 13 | Object category 14 |
 | `15` | 14 | Object category 15 |
 | `16` | 15 | Object category 16 |
 | `17` | 16 | Object category 17 |
 | `18` | 17 | Object category 18 |
 | `19` | 18 | Object category 19 |
 | `20` | 19 | Object category 20 |
 | `99` | 20 | Catch trial |
 | `252` | 21 | Correct feedback |
 | `254` | 22 | Incorrect feedback |
 | `21` | 23 | RSVP category 21 |
 | `22` | 24 | RSVP category 22 |
 | `23` | 25 | RSVP category 23 |
 | `24` | 26 | RSVP category 24 |
 | `25` | 27 | RSVP category 25 |
 | `26` | 28 | RSVP category 26 |
 | `27` | 29 | RSVP category 27 |


## Data Quality Notes

- Large dataset (32 subjects x 1592 files); multi-session design - account for session effects.
- Apply bandpass filter (1-40 Hz) and baseline correction prior to analysis.

## References

- **Reference**: `A multi-subject and multi-session EEG dataset for modelling human visual object recognition`
