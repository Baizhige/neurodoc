# RS_TMSEEG_Data

**Dataset**: `openneuro_ds001849` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds001849
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 120 | **Channels**: 30 | **Sampling Rate**: 5000.0 Hz

## Paradigm

Participants performed a variety of internal mental tasks across multiple runs. The core paradigm includes four distinct mental states: **Mental Arithmetic** (complex subtraction), **Relaxation** (resting with eyes closed), **Internalized Speech** (silently repeating words), and **Breath Sensing** (focusing on the sensation of breathing). Each state was sustained for a specific duration per trial, making this a "long event" or "segmentation" style dataset.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract task onset/offset markers from the events stream.
- **Type 2 (Raw + Super meta integration)**: Map raw triggers (which may vary by run) to the four primary mental state labels (Arithmetic, Relaxation, Speech, Breath).
- **Type 3 (Label-route orchestration)**: Route final task labels to the `Annotation` channel for EEGUnity compatibility.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Task labels require mapping raw event codes to specific mental state categories based on trial structure.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001849

## Event Structure

| Event ID | Count | Type | Meta Level | Meaning |
|----------|-------|------|------------|---------|
| `math`   | -     | long | raw        | Mental Arithmetic task period |
| `relax`  | -     | long | raw        | Relaxation/Resting period |
| `breath` | -     | long | raw        | Breath sensing task period |
| `speech` | -     | long | raw        | Internalized speech/repetition period |
| `R128`   | 120   | admin| raw        | BrainVision system/sync marker (Exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Internal Mental State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 10.0 s (sliding window within long event)
- **Label Route**: `Annotation`
- **Meta Level**: super (mapped from raw triggers)
- **Target Definition**:
    - `0`: Mental Arithmetic
    - `1`: Relaxation
    - `2`: Breath Sensing
    - `3`: Internalized Speech
- **Evidence**: Dataset description on OpenNeuro explicitly lists these internal states as the primary experimental variables for decoding mental activity.

## Data Quality Notes

- **Sampling Rate**: Original 500 Hz is sufficient; no extreme downsampling required compared to TMS-EEG datasets.
- **Artifacts**: Focus on EOG/EMC removal as mental arithmetic and speech tasks may induce subtle muscle tension or eye movements.
- **Review Note**: Channels include 31 EEG + 1 EOG/ECG, totaling 32.


