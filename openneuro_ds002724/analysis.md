# A dataset recorded during development of an affective brain-computer music interface: training sessions

**Dataset**: `openneuro_ds002724` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002724
**Category**: High-level Mental | **Subjects**: 17 | **Files (Completed)**: 96 | **Channels**: 37 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) during the training phase of an affective brain-computer music interface. This is the training session companion to ds002722 (calibration) and ds002723 (testing). Codes 1-9 encode the nine target affective music conditions.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `6` | 96 (files) | long | raw | Music condition 6 onset |
| `4` | 96 (files) | long | raw | Music condition 4 onset |
| `5` | 96 (files) | long | raw | Music condition 5 onset |
| `2` | 96 (files) | long | raw | Music condition 2 onset |
| `1` | 95 (files) | long | raw | Music condition 1 onset |
| `8` | 95 (files) | long | raw | Music condition 8 onset |
| `7` | 95 (files) | long | raw | Music condition 7 onset |
| `9` | 94 (files) | long | raw | Music condition 9 onset |
| `3` | 94 (files) | long | raw | Music condition 3 onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

### Info

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Run
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002724 DOI: https://doi.org/10.1145/3059005


### Normal Task 1: Affective Music Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music condition onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 9 affective music conditions; decode valence/arousal mapping from Daly et al. 2018. Well-balanced: all conditions present in ~95-96 files. 40-second sustained stimuli; epoch at onset. 37-channel array includes physiological channels.

 | Event | y | Meaning |
 |-------|---|---------|
 | `1` | 0 | Music condition 1 |
 | `2` | 1 | Music condition 2 |
 | `3` | 2 | Music condition 3 |
 | `4` | 3 | Music condition 4 |
 | `5` | 4 | Music condition 5 |
 | `6` | 5 | Music condition 6 |
 | `7` | 6 | Music condition 7 |
 | `8` | 7 | Music condition 8 |
 | `9` | 8 | Music condition 9 |

## Data Quality Notes

- Well-balanced event counts across all 9 conditions (94-96 files each).
- 37-channel array includes EEG plus physiological channels (ECG, GSR, etc.).
- Decode code-to-affective-state mapping from Daly et al. 2018 (Scientific Data).
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002724