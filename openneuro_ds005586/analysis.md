# EEG responses to the number of objects in partially occluded and uncovered scenes

**Dataset**: `openneuro_ds005586` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005586
**Category**: Sensory/Response | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants passively viewed game boards depicting varying numbers of game pieces under partial occlusion and subsequent uncovering conditions. The study investigates EEG responses to numerosity perception under occlusion, measuring visual evoked potentials to quantify object tracking. Stimulus codes encode number of objects (1 or 2 digits) and condition (occluded vs uncovered).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 95` | 14399 | event | raw | Catch / fixation stimulus |
| `Stimulus/S 21` | 6884 | event | raw | Stimulus condition (2-digit code: object count x condition) |
| `Stimulus/S 11` | 6875 | event | raw | Stimulus condition (2-digit code: object count x condition) |
| `Stimulus/S 15` | 2241 | event | raw | Stimulus condition |
| `Stimulus/S127` | 1413 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S223` | 1299 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S111` | 903 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S124` | 866 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S224` | 866 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S226` | 864 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S126` | 864 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S215` | 864 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S115` | 864 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S118` | 863 | event | raw | Stimulus condition (3-digit code) |
| `Stimulus/S218` | 863 | event | raw | Stimulus condition (3-digit code) |

### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 95`, `Stimulus/S 21`, `Stimulus/S 11`, `Stimulus/S 15`, `Stimulus/S127`, `Stimulus/S223`, `Stimulus/S111`, `Stimulus/S124`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: ERP Classification for Numerosity Perception (Occluded vs Uncovered)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 21`, `Stimulus/S 11`, `Stimulus/S 15`, `Stimulus/S127`, `Stimulus/S223`, `Stimulus/S111`, `Stimulus/S124`, `Stimulus/S224`, `Stimulus/S226`, `Stimulus/S126`, `Stimulus/S215`, `Stimulus/S115`, `Stimulus/S118`, `Stimulus/S218`, `Stimulus/S 95`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 95` | 0 | Catch/fixation baseline |
  | `Stimulus/S127` | 1 | Occluded condition (3-digit code) |
  | `Stimulus/S223` | 2 | Uncovered condition (3-digit code) |
  | `Stimulus/S111` | 3 | Occluded condition (3-digit code) |
  | `Stimulus/S124` | 4 | Occluded condition (3-digit code) |
  | `Stimulus/S224` | 5 | Uncovered condition (3-digit code) |
  | `Stimulus/S226` | 6 | Uncovered condition (3-digit code) |
  | `Stimulus/S126` | 7 | Occluded condition (3-digit code) |
  | `Stimulus/S215` | 8 | Uncovered condition (3-digit code) |
  | `Stimulus/S115` | 9 | Occluded condition (3-digit code) |
  | `Stimulus/S118` | 10 | Occluded condition (3-digit code) |
  | `Stimulus/S218` | 11 | Uncovered condition (3-digit code) |
  | `Stimulus/S 21` | 12 | Condition code 21 (2-digit) |
  | `Stimulus/S 11` | 13 | Condition code 11 (2-digit) |
  | `Stimulus/S 15` | 14 | Condition code 15 (2-digit) |
- **Evidence**:
  - DOI: 10.1162/jocn_a_02264 — ERP analysis of P1, N1, P2, P3 components in response to partially occluded vs uncovered game board stimuli, epoched -0.2 to 1.0s
- **Kernel Notes**: Baseline correct epochs from -0.2 to 0s. Apply bandpass filter (1-40 Hz). Artifact rejection before epoching. Stimulus codes encode numerosity (visible pieces × uncovered pieces); codes starting with 1xx indicate 4 visible pieces, codes starting with 2xx indicate 32 visible pieces. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Object Numerosity / Occlusion (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Stimulus codes encode object count x occlusion condition; decode from events.tsv. `New Segment/` is admin and excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Stimulus/S 95` | 0 | Catch/fixation |
 | `Stimulus/S127` | 1 | Condition code 127 |
 | `Stimulus/S223` | 2 | Condition code 223 |
 | `Stimulus/S111` | 3 | Condition code 111 |
 | `Stimulus/S 21` | 4 | Condition code 21 |
 | `Stimulus/S 11` | 5 | Condition code 11 |
 | `Stimulus/S117` | 6 | Condition code 117 |
 | `Stimulus/S124` | 7 | Condition code 124 |
 | `Stimulus/S224` | 8 | Condition code 224 |
 | `Stimulus/S227` | 9 | Condition code 227 |
 | `Stimulus/S118` | 10 | Condition code 118 |
 | `Stimulus/S218` | 11 | Condition code 218 |
 | `Stimulus/S122` | 12 | Condition code 122 |
 | `Stimulus/S217` | 13 | Condition code 217 |
 | `Stimulus/S222` | 14 | Condition code 222 |
 | `Stimulus/S212` | 15 | Condition code 212 |
 | `Stimulus/S123` | 16 | Condition code 123 |
 | `Stimulus/S113` | 17 | Condition code 113 |
 | `Stimulus/S213` | 18 | Condition code 213 |
 | `Stimulus/S112` | 19 | Condition code 112 |
 | `Stimulus/S226` | 20 | Condition code 226 |
 | `Stimulus/S211` | 21 | Condition code 211 |
 | `Stimulus/S126` | 22 | Condition code 126 |
 | `Stimulus/S221` | 23 | Condition code 221 |
 | `Stimulus/S121` | 24 | Condition code 121 |
 | `Stimulus/S216` | 25 | Condition code 216 |
 | `Stimulus/S116` | 26 | Condition code 116 |
 | `Stimulus/S214` | 27 | Condition code 214 |
 | `Stimulus/S114` | 28 | Condition code 114 |

## Data Quality Notes

- Small dataset (23 subjects, 23 files); verify that all subjects completed the same number of trials.
- `New Segment/` is an admin event and should be excluded.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review