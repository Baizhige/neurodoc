# Longitudinal EEG Test-Retest Reliability in Healthy Individuals

**Dataset**: `openneuro_ds007176` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007176
**Category**: Biological State | **Subjects**: 43 | **Files (Completed)**: 300 | **Channels**: 60 | **Sampling Rate**: 1000 Hz

## Paradigm

Longitudinal resting-state EEG recordings collected over four sessions spanning two years to evaluate test-retest reliability of quantitative EEG measures. Recordings are continuous resting-state without structured task events. The dataset enables assessment of EEG biomarker stability across sessions and time points.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007176

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0` | 2 | admin | raw | Null trigger code - no experimental meaning |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: CE
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1016/j.bspc.2026.109484


### Primary Task 2: Publisher-defined BIDS task: OE
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1016/j.bspc.2026.109484


### Normal Task 1: Resting-State Segmentation (long_event)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `stim`
- **Target Definition**: N/A (no trial events; target_events: null)
- **Notes**: Only event code `0` present (2 total); this is a null trigger with no experimental meaning. Resting-state data; use segmentation across full recording. Session/time-point labels available from participants.tsv for longitudinal analysis.

## Data Quality Notes

- No meaningful event markers; purely continuous resting-state EEG.
- 43 subjects x ~7 sessions/subject = 300 files; multi-session longitudinal design.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## References

- **Paper**: `Longitudinal test-retest reliability of quantitative EEG in healthy individuals using an automated preprocessing approach` (DOI: 10.1016/j.bspc.2026.109484)
