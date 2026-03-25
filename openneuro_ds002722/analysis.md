# A dataset recorded during development of an affective brain-computer music interface: calibration session

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 94 | **Channels**: 37.0 | **Sampling Rate**: 1000.0 Hz

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) as a calibration session for an affective brain-computer music interface (BCMI). EEG and physiological signals were recorded to build a mapping from neural/physiological features to targeted emotional states. Codes 1-9 are primary music condition labels; 100-200 range codes encode specific music clip identifiers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002722

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9` | 94 (files) | long | raw | Music condition 9 onset (high arousalx) |
| `4` | 90 (files) | long | raw | Music condition 4 onset |
| `5` | 89 (files) | long | raw | Music condition 5 onset |
| `6` | 89 (files) | long | raw | Music condition 6 onset |
| `7` | 89 (files) | long | raw | Music condition 7 onset |
| `2` | 89 (files) | long | raw | Music condition 2 onset |
| `1` | 60 (files) | long | raw | Music condition 1 onset |
| `3` | 59 (files) | long | raw | Music condition 3 onset |
| `104`-`205` range | 19 (files each) | long | raw | Specific music clip identifiers |

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
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002722 DOI: https://doi.org/10.1145/3059005


### Normal Task 1: Affective Music Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to music clip onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Codes 1-9 are primary valence/arousal condition labels. 100-200 range codes are specific music clip IDs (22 clips per subject); these could alternatively be used as 22-class stimulus labels. Decode exact mapping from Daly et al. 2018. 40-second clips are long events; epoch on onset markers.

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

- 30 distinct event types; codes 1-9 are the primary condition labels.
- Decode exact valence/arousal mapping for codes 1-9 from Daly et al. 2018 paper.
- 37-channel EEG includes physiological channels (ECG, GSR, etc.); identify EEG-only channels.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Daly, I., Nicolaou, N., Williams, D., Hwang, F., Kirke, A., Miranda, E., Nasuto, S.J., Neural and physiological data from participants listening to affective music, Scientific Data, 2018.`
