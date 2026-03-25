# A dataset recorded during development of an affective brain-computer music interface: testing session

**Dataset**: `openneuro_ds002723` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002723
**Category**: Complex Applied | **Subjects**: 8 | **Files (Completed)**: 44 | **Channels**: 37.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants interacted with a real-time affective brain-computer music interface (BCMI) that modified music on-the-fly based on detected emotional states, aiming to induce specific target affective trajectories. This is the testing session of the BCI system (see also ds002722 calibration and ds002724 training sessions). Codes 1-9 encode the target or detected affective music conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002723

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2` | 44 (files) | long | raw | Affective music condition 2 |
| `6` | 44 (files) | long | raw | Affective music condition 6 |
| `9` | 42 (files) | long | raw | Affective music condition 9 |
| `4` | 42 (files) | long | raw | Affective music condition 4 |
| `5` | 39 (files) | long | raw | Affective music condition 5 |
| `7` | 38 (files) | long | raw | Affective music condition 7 |
| `1` | 29 (files) | long | raw | Affective music condition 1 |
| `3` | 28 (files) | long | raw | Affective music condition 3 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Run
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002723 DOI: https://doi.org/10.1088/1741-2560/13/4/046022


### Normal Task 1: Affective Music Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music condition onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 8 affective conditions; decode exact valence/arousal mapping from Daly et al. 2018. Small dataset (8 subjects, 44 files). Music conditions are sustained 40-second states; these onset markers epoch at transition points.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2` | 0 | Music condition 2 |
 | `6` | 1 | Music condition 6 |
 | `9` | 2 | Music condition 9 |
 | `4` | 3 | Music condition 4 |
 | `5` | 4 | Music condition 5 |
 | `7` | 5 | Music condition 7 |
 | `1` | 6 | Music condition 1 |
 | `3` | 7 | Music condition 3 |
## Data Quality Notes

- Small dataset: 8 subjects, 44 files.
- 37-channel array includes physiological channels; verify EEG-only channel selection.
- Decode code-to-condition mapping from Daly et al. 2018 (Scientific Data).
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Neural and physiological data from participants listening to affective music, Scientific Data, 2018`
