# TUH EEG Seizure Corpus

**Dataset**: `tuh_eeg_seizure` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_seizure/v2.0.3/
**Category**: Biological State | **Subjects**: ~675 | **Files (Completed)**: 7361 | **Channels**: 17-128 | **Sampling Rate**: 250-1000 Hz

## Paradigm

The TUH EEG Seizure Corpus (v2.0.3) is the largest publicly available seizure detection dataset, containing 7,361 clinical EEG recordings from ~675 unique patients with time-stamped seizure annotations (Shah et al., 2020). Expert neurologists labeled each segment as background (bckg) or one of five seizure types using companion CSV sidecar files (channel, start_time, stop_time, label). The dataset is pre-split into train and dev sets (directory path contains `/train/` or `/dev/`). Recording lengths range from a few minutes to several hours.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_seizure/v2.0.3/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bckg` | ~75000 | long | raw | Background - no seizure activity |
| `gnsz` | varies | long | raw | Generalized non-specific seizure |
| `fnsz` | varies | long | raw | Focal non-specific seizure |
| `cpsz` | varies | long | raw | Complex partial seizure |
| `absz` | varies | long | raw | Absence seizure |
| `tnsz` | varies | long | raw | Tonic seizure |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> `bckg` (background) is overwhelmingly the most frequent label. Seizure events are annotated with onset, offset, and type from CSV sidecars.

## Tasks

### Primary Task 1: Binary seizure detection (seizure vs. background)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 s *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `bckg` | 0 | Background / non-seizure |
  | `gnsz` | 1 | Generalized seizure |
  | `fnsz` | 1 | Focal seizure |
  | `cpsz` | 1 | Complex partial seizure |
  | `absz` | 1 | Absence seizure |
  | `tnsz` | 1 | Tonic seizure |
- **Evidence**:
  - DOI: 10.1109/tii.2023.3274913 — Uses TUH EEG dataset, segmenting EEG signals into 4-second epochs without overlap and classifying each segment as seizure or non-seizure using SS-CSV-derived features with CNN/SVM/kNN classifiers.
  - DOI: 10.1088/1741-2552.ac7d0d — Uses TUH EEG dataset with 12 selected cases for cross-subject seizure detection, segmenting signals into 1-second windows with 50% overlap and using binary classification between seizure and non-seizure EEG.
  - DOI: 10.1117/12.2670106 — Uses TUH EEG Seizure Corpus (TUSZ) version 1.5.2 with train/dev split to train XGBoost, Random Forest, KNN, and SVC classifiers for binary seizure vs background detection using channel selection based on cross-correlation analysis.
- **Kernel Notes**: Segment raw EEG into fixed-length windows, map any window containing at least one seizure annotation to label 1, windows with only bckg to label 0. Handle extreme class imbalance via undersampling or class weights.

### Normal Task 1: Seizure Detection - bckg vs. Seizure (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s (annotation onset), duration = annotation duration, overlap = 0.0 s for initial segmentation; or sliding window 5.0 s, overlap = 2.5 s on annotated segments, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Extreme class imbalance: `bckg` >> all seizure types combined. Undersample background or use cost-sensitive learning. CSV sidecars required alongside EDF files.

| Event | y | Meaning |
|-------|---|---------|
| `bckg` | 0 | Background / no seizure |
| `gnsz` | 1 | Generalized seizure |
| `fnsz` | 1 | Focal seizure |
| `cpsz` | 1 | Complex partial seizure |
| `absz` | 1 | Absence seizure |
| `tnsz` | 1 | Tonic seizure |


### Normal Task 2: Seizure Type Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Use annotation duration (seizure-type segments only), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use only seizure-type annotations (gnsz=0, fnsz=1, cpsz=2, absz=3, tnsz=4); exclude `bckg`.
- **Notes**: Severe class imbalance across seizure types; some types (absz, tnsz) are rare.

## Data Quality Notes

- **Extreme class imbalance**: background constitutes >80% of annotations; severely balance before training.
- Variable channel count (17-128) and sampling rate (250-1000 Hz); normalize per recording.
- Train/dev split is pre-defined; respect it for evaluation. Split encoded in file path (`/train/`, `/dev/`).
- Sex is not reliably available.
- Long recordings may span multiple seizure episodes; temporal context is important.

## References

- **Reference**: Shah V et al. (2020). The Temple University Hospital EEG Seizure Corpus. *Frontiers in Neural Engineering*. https://isip.piconepress.com/projects/tuh_eeg/
