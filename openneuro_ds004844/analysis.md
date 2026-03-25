# T22 (Semi-Automated Driving Trust Paradigm)

**Dataset**: `openneuro_ds004844` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004844
**Category**: Complex Applied | **Subjects**: 68 | **Files (Completed)**: 68 | **Channels**: 72 | **Sampling Rate**: 1024 Hz

## Paradigm

Simulated semi-automated driving in a leader-follower paradigm focused on predicting and influencing trust-based decisions regarding control authority hand-off and take-over between human and automation. EEG was recorded during sustained driving across multiple automation levels. Event codes are hierarchically structured 7-digit identifiers encoding driving state and automation mode.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004844

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2310002` | 8978 | long | raw | Driving state code |
| `2310001` | 8978 | long | raw | Driving state code |
| `4111101` | 8716 | long | raw | Driving state code |
| `2572001` | 3231 | long | raw | Driving state code |
| `2562001` | 2880 | long | raw | Driving state code |
| `2552001` | 1983 | long | raw | Driving state code |
| `3110002` | 1884 | long | raw | Driving state code |
| `2812002` | 1884 | long | raw | Driving state code |
| `3110001` | 1884 | long | raw | Driving state code |
| `2812001` | 1884 | long | raw | Driving state code |
| `2714111` | 1591 | long | raw | Driving state code |
| `1410001` | 1591 | long | raw | Driving state code |
| `1410002` | 1591 | long | raw | Driving state code |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Drive
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004844 DOI: https://doi.org/10.18112/openneuro.ds004844.v1.0.0


### Normal Task 1: Driving State Classification (multiclass/long)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All codes are 7-digit hierarchical identifiers encoding driving condition and automation level. Full decode table required from dataset README. Related dataset: ds004657.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2310002` | 0 | Driving state code |
 | `2310001` | 1 | Driving state code |
 | `4111101` | 2 | Driving state code |
 | `2572001` | 3 | Driving state code |
 | `2562001` | 4 | Driving state code |
 | `2552001` | 5 | Driving state code |
 | `3110002` | 6 | Driving state code |
 | `2812002` | 7 | Driving state code |
## Data Quality Notes

- All event codes are 7-digit hierarchical numeric identifiers - full decode needed.
- 40+ unique codes; group by condition category for practical classification.

## References

- **Reference**: `Predicting and influencing trust-based decisions about control authority hand-off and take-over during simulated, semi-automated driving in a leader-follower paradigm`
