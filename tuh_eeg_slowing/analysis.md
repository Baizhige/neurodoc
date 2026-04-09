# TUH EEG Slowing Corpus

**Dataset**: `tuh_eeg_slowing` | **Year**: 2022 | **URL**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_slowing/v2.0.1/
**Category**: Biological State | **Subjects**: ~47 | **Files (Completed)**: 112 | **Channels**: 27-41 | **Sampling Rate**: 250-512 Hz

## Paradigm

The TUH EEG Slowing Corpus (v2.0.1) contains 112 clinical EEG recordings with time-stamped annotations for EEG slowing, seizure activity, and background segments. Expert annotators labeled each segment using companion CSV sidecar files (channel, start_time, stop_time, label). EEG slowing (diffuse or focal slow-wave activity) is a neurological biomarker of conditions such as encephalopathy, stroke, or post-ictal states. The corpus enables the development of algorithms to automatically detect and localize EEG slowing.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `seiz` | varies | long | raw | Seizure activity |
| `slow` | varies | long | raw | EEG slowing (pathological slow-wave activity) |
| `bckg` | varies | long | raw | Background - normal EEG |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Multiple annotations may appear in a single recording (e.g., `bckg + slow`, `bckg + seiz`). Per the CSV analysis, top events include `seiz:22`, `seiz:43`, `slow:64`, and `bckg:43,slow:63`.

### Info

Additional file scan metadata not available.

## Tasks

### Primary Task 1: EEG slowing detection (focal/generalized vs background)
- **Task Type**: classification/detection
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Slowing-related event labels against normal background segments.
- **Evidence**: TUH Slowing Corpus provides curated slowing annotations for automated slowing detection tasks. Source: https://isip.piconepress.com/projects/tuh_eeg/ DOI: https://doi.org/10.3389/fnins.2016.00196


### Normal Task 1: EEG Slowing Detection - Normal vs. Slowing (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, use annotation duration, overlap = 0.0 s; or sliding window 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `seiz` events if slowing-specific detection is the goal, or include as a third class. CSV sidecars required.

| Event | y | Meaning |
|-------|----|---------|
| `bckg` | 0 | Normal background EEG |
| `slow` | 1 | EEG slowing |


### Normal Task 2: 3-Class EEG State Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, use annotation duration, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|----|---------|
| `bckg` | 0 | Background |
| `slow` | 1 | Slowing |
| `seiz` | 2 | Seizure |

## Data Quality Notes

- Small dataset (112 files, ~47 subjects); limited sample size.
- CSV sidecars required; if missing, the kernel raises a ValueError.
- Variable sampling rate (250-512 Hz); normalize before cross-recording analysis.
- Annotations may overlap (e.g., slowing + seizure in the same segment); handle compound annotations carefully.
- Sex is not reliably available.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_slowing/v2.0.1/