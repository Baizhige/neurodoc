# Imagined Emotion Study

**Dataset**: `openneuro_ds003004` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 34 | **Channels**: 219.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

Participants used voice-guided imagery to induce and sustain 15 distinct emotional states, using button presses to indicate the onset and offset of each imagined emotion. Despite the paradigm involving discrete emotional state onsets (button presses), no event markers were detected in the BIDS EEG files by the locator pipeline. The button-press events may be stored in separate behavioral logs or were not encoded in the EEG trigger channel.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003004

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; button-press onsets not captured in locator |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Imagined Emotion
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003004 DOI: https://doi.org/10.18112/openneuro.ds003004.v1.1.1


### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level event markers in locator; check events.tsv directly for button-press events))
- **Notes**: High-density 219-channel EEG. If button-press onset/offset events are available in events.tsv, 15 emotional states could be used as multiclass labels with long_event epoching.
## Data Quality Notes

- No event markers detected in EEG files by locator pipeline - verify events.tsv directly.
- High-density 219-channel array; verify electrode positions and system (likely EGI/Geodesic).
- 15 distinct emotional states if properly annotated - valuable for affective BCI research.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Imagined Emotion Study`
