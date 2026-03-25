# High-Gamma EEG Motor Imagery Dataset

**Dataset**: `other_highgammadataset` | **Year**: 2017 | **URL**: https://gin.g-node.org/robintibor/high-gamma-dataset/src/master/data
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 28 | **Channels**: 133 | **Sampling Rate**: 500 Hz

## Paradigm

Fourteen subjects performed four-class cued motor imagery (left hand, right hand, feet, tongue) while high-density EEG was recorded from 128+ channels using a NeurOne amplifier (Mega Electronics Ltd, Kuopio, FI) with a WaveGuard Original cap (ANT, Enschede, NL) at 500 Hz (Schirrmeister et al., 2017). Each subject contributed two sessions: a training set and a test set. Per session, 40-225 trials per class were recorded depending on subject. This dataset is notably used to evaluate deep learning models (EEGNet, ShallowConvNet, DeepConvNet) for motor imagery BCI and is one of the highest-density publicly available MI datasets.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://gin.g-node.org/robintibor/high-gamma-dataset/src/master/data

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `left_hand` | ~4200 total | short | raw | Left-hand motor imagery cue onset |
| `right_hand` | ~4200 total | short | raw | Right-hand motor imagery cue onset |
| `feet` | ~1400 total | short | raw | Feet motor imagery cue onset |
| `tongue` | ~1400 total | short | raw | Tongue motor imagery cue onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Trial counts per session are variable (40-225 per class). Approximate totals across all 28 files.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://doi.org/10.1002/hbm.23730


### Normal Task 1: 4-Class Motor Imagery Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `left_hand` | 0 | Left-hand motor imagery |
| `right_hand` | 1 | Right-hand motor imagery |
| `feet` | 2 | Feet motor imagery |
| `tongue` | 3 | Tongue motor imagery |


### Normal Task 2: Left vs. Right Hand Motor Imagery (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: `left_hand` -> 0, `right_hand` -> 1 (discard feet and tongue trials).
## Data Quality Notes

- No age or sex information available in the public release.
- High channel count (128+ EEG); high-gamma frequency analysis (60-300 Hz) is a primary use case.
- Trial counts are imbalanced across classes (more left/right hand than feet/tongue); balance before 4-class training.
- Two sessions per subject (train/test): separate by filename suffix for proper evaluation.

## References

- **Reference**: Schirrmeister RT et al. (2017). Deep learning with convolutional neural networks for EEG decoding and visualization. *Human Brain Mapping*, 38(11), 5391-5420. https://doi.org/10.1002/hbm.23730
