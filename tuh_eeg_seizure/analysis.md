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

### Primary Task 1: Seizure event detection and localization
- **Task Type**: classification/detection
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Seizure vs background labels with temporal seizure boundaries.
- **Evidence**: TUH Seizure Corpus is primarily designed for automated seizure detection from clinical EEG. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.1109/globalsip.2013.6736803


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
