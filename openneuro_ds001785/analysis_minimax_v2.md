# Evidence accumulation relates to perceptual consciousness and monitoring

**Dataset**: `openneuro_ds001785` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds001785
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 54 | **Channels**: 71.0 | **Sampling Rate**: 1024.0 Hz

## Paradigm

Participants performed a threshold-level vibrotactile detection task in which a weak tactile stimulus was either present (threshold condition) or absent (adapt condition). After each trial, participants provided a confidence rating. The study investigated the neural mechanisms of evidence accumulation and metacognitive monitoring using signal detection theory outcomes (hit, miss, correct rejection, false alarm) as trial labels.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, confidence, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001785

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim-thr` | large | short | raw | Stimulus onset - threshold vibrotactile stimulus present |
| `stim-adapt` | large | short | raw | Stimulus onset - adapt condition (no stimulus) |
| `hit` | large | short | raw | Correct detection: target present, response given |
| `miss` | large | short | raw | Miss: target present, no response |
| `cr` | large | short | raw | Correct rejection: no target, no response |
| `fa` | large | short | raw | False alarm: no target, but response given |
| `conf` | large | short | raw | Confidence rating onset |
| `conf-resp` | large | short | raw | Confidence rating button-press response |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stim-thr`, `stim-adapt`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Normal Task 1: Signal Detection Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Four-class SDT labels enable analysis of detection sensitivity and response bias. `stim-thr` and `stim-adapt` are stimulus onset markers - use as alternative epoch triggers if SDT label counts are imbalanced. Regression target: `confidence` from misc channel.

 | Event | y | Meaning |
 |-------|---|-|
 | `hit` | 0 | Correct detection |
 | `miss` | 1 | Missed target |
 | `cr` | 2 | Correct rejection |
 | `fa` | 3 | False alarm |


## Data Quality Notes

- Check class balance across hit/miss/cr/fa - miss and fa classes may be sparse for threshold stimuli.
- Confidence ratings stored in misc channel `confidence`; response times in `response_time`.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Evidence accumulation relates to perceptual consciousness and monitoring`
