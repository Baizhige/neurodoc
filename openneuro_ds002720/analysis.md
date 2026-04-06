# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 165 | **Channels**: 19.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants used kinaesthetic motor imagery (imagining squeezing a ball) or relaxation to intentionally modulate the tempo of music in a continuous brain-computer music interface (BCMI) task. Event code 1 = motor_imagery (ball squeezing imagination) and code 2 = relaxation (rest), each lasting several seconds. The BCI decoded the EEG to adjust music tempo in real-time, creating a closed-loop feedback system.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `motor_imagery` (code 1) | 143 (files) | event | raw | Sustained motor imagery - imagining squeezing a ball |
| `relaxation` (code 2) | 143 (files) | event | raw | Sustained relaxation period |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Motor imagery decoding for BCMI tempo control
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 16 s, overlap = 0.0, target_events = [`motor_imagery`, `relaxation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `motor_imagery` | 0 | Kinaesthetic motor imagery - imagining squeezing a ball |
  | `relaxation` | 1 | Relaxation / rest period |
- **Evidence**:
  - DOI: `10.1038/s41597-020-0507-6` — The paper describes the 'BCMI tempo' dataset (openneuro_ds002720) recorded during development of a tempo-based BCMI where participants used kinaesthetic motor imagery to control music tempo, with EEG recorded from 19 channels during trials consisting of 4s fixation followed by 12s motor imagery tasks.
- **Kernel Notes**: Extract sustained motor imagery and relaxation epochs from continuous EEG. Each trial consists of 4s fixation + 12s motor imagery task = 16s total window. Use epoch_by_long_event_hdf5 to slide a 16-second window through each annotation. Binary classification: motor imagery (y=0) vs relaxation (y=1).

### Potential Task 1: Motor Imagery BCI Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (motor imagery window), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Motor imagery BCI task with multi-second imagination periods. Long 4-second epoch window captures the full motor imagery event. Specific kernel decodes raw codes (1->motor_imagery, 2->relaxation).

 | Event | y | Meaning |
 |-------|---|---------|
 | `motor_imagery` | 0 | Motor imagery - imagining squeezing a ball |
 | `relaxation` | 1 | Relaxation / rest period |

## Data Quality Notes

- 19-channel EEG is low density but suitable for BCI motor imagery decoding.
- Count column (143 files) indicates files-with-event, not trial count per file.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review