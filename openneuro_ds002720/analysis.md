# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 165 | **Channels**: 19.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants used kinaesthetic motor imagery (imagining squeezing a ball) or relaxation to intentionally modulate the tempo of music in a continuous brain-computer music interface (BCMI) task. Event code 1 = motor_imagery (ball squeezing imagination) and code 2 = relaxation (rest), each lasting several seconds. The BCI decoded the EEG to adjust music tempo in real-time, creating a closed-loop feedback system.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002720

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `motor_imagery` (code 1) | 143 (files) | long | raw | Sustained motor imagery - imagining squeezing a ball |
| `relaxation` (code 2) | 143 (files) | long | raw | Sustained relaxation period |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds002720 DOI: https://doi.org/10.18112/openneuro.ds002720.v1.0.1


### Normal Task 1: Motor Imagery BCI Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (motor imagery window), target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `A dataset recorded during development of a tempo-based brain-computer music interface`
