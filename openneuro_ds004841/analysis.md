# TX14 (Semi-Autonomous Vehicle Monitoring)

**Dataset**: `openneuro_ds004841` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004841
**Category**: Complex Applied | **Subjects**: 11 | **Files (Completed)**: 11 | **Channels**: 70 | **Sampling Rate**: 256 Hz

## Paradigm

Participants monitored a semi-autonomous vehicle system and performed local situational awareness tasks within a simulated environment, with EEG recorded to characterize cognitive states during supervised automation. Event codes are hierarchically structured 7-digit identifiers encoding operational state and task type.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004841

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2210001` | 998 | long | raw | Hierarchical operational state code |
| `2210002` | 947 | long | raw | Hierarchical operational state code |
| `2110000` | 220 | long | raw | Hierarchical operational state code |
| `4310000` | 195 | long | raw | Hierarchical operational state code |
| `4100001` | 195 | long | raw | Hierarchical operational state code |
| `4320000` | 195 | long | raw | Hierarchical operational state code |
| `4300010` | 107 | long | raw | Hierarchical operational state code |
| `4300020` | 96 | long | raw | Hierarchical operational state code |
| `4300100` | 80 | long | raw | Hierarchical operational state code |
| `1110002` | 76 | long | raw | Hierarchical operational state code |
| `1110001` | 76 | long | raw | Hierarchical operational state code |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Drive On Mission
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004841 DOI: https://doi.org/10.18112/openneuro.ds004841.v1.0.1


### Normal Task 1: Operational State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All codes are 7-digit hierarchical identifiers. Full decode table required from dataset README. Only 11 subjects - small dataset.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2210001` | 0 | Operational state code |
 | `2210002` | 1 | Operational state code |
 | `2110000` | 2 | Operational state code |
 | `4310000` | 3 | Operational state code |
 | `4100001` | 4 | Operational state code |
 | `4320000` | 5 | Operational state code |
## Data Quality Notes

- 7-digit hierarchical numeric codes - full decode needed.
- Only 11 subjects; limited sample size for generalization.

## References

- **Reference**: `TX14. ReadMe: TX14 dataset`
