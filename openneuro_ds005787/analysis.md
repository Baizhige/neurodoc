# NOD-EEG

**Dataset**: `openneuro_ds005787` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005787
**Category**: Others | **Subjects**: N/A | **Files (Completed)**: 896 | **Channels**: 64 | **Sampling Rate**: 250 Hz

## Paradigm

The NOD-EEG dataset contains 64-channel EEG recordings from a stimulus-response paradigm. Each trial includes a stimulus onset (`stim_on`), participant button-press response (`resp`), and block boundary markers (`begin`, `end`). The precise experimental task and stimuli are described in the dataset README.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005787

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `resp` | 2273060 | short | raw | Participant button-press response |
| `stim_on` | 112000 | short | raw | Stimulus onset |
| `begin` | 896 | long | raw | Block begin marker |
| `end` | 896 | long | raw | Block end marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stim_on`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Image Net
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005787 DOI: https://doi.org/10.18112/openneuro.ds005787.v1.0.0


### Normal Task 1: Stimulus-Response (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very high count for `resp` (2.27M total); verify that events are correctly timestamped. `begin`/`end` mark block boundaries.

 | Event | y | Meaning |
 |-------|---|---------|
 | `resp` | 0 | Button-press response |
 | `stim_on` | 1 | Stimulus onset |
 | `begin` | 2 | Block begin |
 | `end` | 3 | Block end |
## Data Quality Notes

- Very high total event count for `resp`; verify no duplicate events.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. Scientific Data, 6, 103`
