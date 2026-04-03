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
> **Status**: wait_manual_review
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

### Primary Task 1: Binary Seizure Detection (Seizure vs Background)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = annotation duration, overlap = 0.0 s, target_events = [`bckg`, `gnsz`, `fnsz`, `cpsz`, `absz`, `tnsz`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `bckg` | 0 | Background / non-seizure |
  | `gnsz` | 1 | Generalized non-specific seizure |
  | `fnsz` | 1 | Focal non-specific seizure |
  | `cpsz` | 1 | Complex partial seizure |
  | `absz` | 1 | Absence seizure |
  | `tnsz` | 1 | Tonic seizure |
- **Evidence**:
  - DOI: 10.1088/1741-2552.ac7d0d — Uses TUH EEG with 1-second windows (50% overlap) for binary seizure vs non-seizure classification
  - DOI: 10.1109/tii.2023.3274913 — Uses TUH EEG with 4-second epochs (no overlap) for binary seizure vs background detection
  - DOI: 10.1117/12.2670106 — Uses TUH EEG Seizure Corpus v1.5.2 for binary seizure vs background detection using XGBoost, Random Forest, KNN, and SVC
- **Kernel Notes**: Extract epochs spanning full annotation duration for each seizure type and background. Apply sliding window (e.g., 1-4s window, 0-50% overlap) within each epoch for data augmentation if needed. Handle extreme class imbalance (bckg >> seizure) via undersampling or class weighting. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Seizure Type Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Use annotation duration (seizure-type segments only), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use only seizure-type annotations (gnsz=0, fnsz=1, cpsz=2, absz=3, tnsz=4); exclude `bckg`.
- **Notes**: Severe class imbalance across seizure types; some types (absz, tnsz) are rare.

### Normal Task 2: Multi-class Seizure Detection with Background (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s (annotation onset), duration = annotation duration, overlap = 0.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Extreme class imbalance: `bckg` >> all seizure types combined. Undersample background or use cost-sensitive learning. CSV sidecars required alongside EDF files.

| Event | y | Meaning |
|-------|---|-|
| `bckg` | 0 | Background / no seizure |
| `gnsz` | 1 | Generalized seizure |
| `fnsz` | 2 | Focal seizure |
| `cpsz` | 3 | Complex partial seizure |
| `absz` | 4 | Absence seizure |
| `tnsz` | 5 | Tonic seizure |

## Data Quality Notes

- **Extreme class imbalance**: background constitutes >80% of annotations; severely balance before training.
- Variable channel count (17-128) and sampling rate (250-1000 Hz); normalize per recording.
- Train/dev split is pre-defined; respect it for evaluation. Split encoded in file path (`/train/`, `/dev/`).
- Sex is not reliably available.
- Long recordings may span multiple seizure episodes; temporal context is important.

