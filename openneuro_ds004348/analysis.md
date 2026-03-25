# Ear-EEG Sleep Monitoring 2017 (EESM17)

**Dataset**: `openneuro_ds004348` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004348
**Category**: Biological State | **Subjects**: 9 | **Files (Completed)**: 36
**Channels**: 35 | **Sampling Rate**: 200 Hz

## Paradigm

Nightly sleep monitoring and pre-sleep resting recordings using ear-EEG and partial polysomnography in a naturalistic home environment. Subjects wore ear-mounted EEG devices during sleep, allowing investigation of sleep stage classification and comparison between ear-EEG and conventional PSG signals.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004348

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Lights Off` | 9 | long | raw | Lights-off marker (sleep onset reference) |
| `Lights On` | 9 | long | raw | Lights-on marker (sleep end reference) |
| `Awake` | 1 | long | raw | Wakefulness annotation |
| `Artifact` | 9 | admin | raw | Artifact annotation |
| `Arousal` | 9 | admin | raw | Arousal annotation |
| `Beginning of Recording` | 9 | admin | raw | Recording start marker |
| `End of Study` | 9 | admin | raw | Recording end marker |
| `Montage` | 9 | admin | raw | Montage configuration event |
| `Started Analyzer - Sleep Events` | 9 | admin | raw | Analyzer start marker |
| `Started Analyzer - ECG` | 9 | admin | raw | ECG analyzer start |
| `Stopped Analyzer - ECG` | 9 | admin | raw | ECG analyzer stop |
| `Started Analyzer - Auto-Staging` | 9 | admin | raw | Auto-staging start |
| `Stopped Analyzer - Auto-Staging` | 9 | admin | raw | Auto-staging stop |
| `512` | 9 | admin | raw | Numerical trigger code 512 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Sleep stage labels (W/N1/N2/N3/REM; mapping dataset-specific)
- **Evidence**: Dataset and references explicitly center on PSG/EEG sleep scoring. Source: https://openneuro.org/datasets/ds004348 DOI: https://doi.org/10.1186/s12938-017-0400-5


### Normal Task 1: Sleep Staging (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Sleep stage labels (N1/N2/N3/REM) are typically stored in annotation files, not event markers. Use Lights Off/On as block boundaries. The dataset is primarily suitable for sleep staging classification.

| Event | y | Meaning |
 |-------|---|------|
 | `Lights Off` | 0 | Sleep period start |
 | `Lights On` | 1 | Sleep period end |
## Data Quality Notes

- Sleep stage annotations are in PSG annotation files, not directly as trial events
- Artifact markers must be excluded from analysis windows
- 35 channels includes non-EEG channels (ECG, respiratory belt, etc.)
- Only 9 subjects; limited generalization

## References

- **Reference**: `Ear-EEG Sleep Monitoring 2017 (EESM17)`
