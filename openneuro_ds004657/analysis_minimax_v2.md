# Driving with Autonomous Aids

**Dataset**: `openneuro_ds004657` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004657
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 119 | **Channels**: 74 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed a semi-automated driving task involving lane maintenance and collision avoidance to evaluate human trust in automation across manual and varying autonomous assistance conditions. The 7-digit hierarchical trigger codes encode the driving condition, task phase, and condition variant. Codes 2310002/2310001 dominate with ~10,367 events each; 4111101 appears ~10,051 times. All other codes appear 1,081-1,819 times each - consistent with less-frequent driving scenarios or transitions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004657

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `2310002` | 10367 | long | raw | Driving condition 231, variant 2 (dominant) |
| `2310001` | 10367 | long | raw | Driving condition 231, variant 1 (dominant) |
| `4111101` | 10051 | long | raw | Driving condition 411, variant 1 |
| `2320001` | 1819 | long | raw | Driving condition 232, variant 1 |
| `2320002` | 1819 | long | raw | Driving condition 232, variant 2 |
| `1410001` | 1383 | long | raw | Driving condition 141, variant 1 |
| `1410002` | 1383 | long | raw | Driving condition 141, variant 2 |
| `1420001` | 1226 | long | raw | Driving condition 142, variant 1 |
| `1420002` | 1226 | long | raw | Driving condition 142, variant 2 |
| `1320001` | 1175 | long | raw | Driving condition 132, variant 1 |
| `1320002` | 1175 | long | raw | Driving condition 132, variant 2 |
| `2541001` | 1174 | long | raw | Driving condition 254, variant 1 |
| `2781021` | 1094 | long | raw | Driving condition 278, variant 021 |
| `2781022` | 1094 | long | raw | Driving condition 278, variant 022 |
| `2561001` | 1081 | long | raw | Driving condition 256, variant 1 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Mental Workload Classification (Easy vs Hard Road Complexity)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.875 *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Easy` | 0 | Easy road complexity segment (low mental workload) |
  | `Hard` | 1 | Hard road complexity segment (high mental workload) |
- **Super Meta Notes**: N/A (meta level is raw)
- **Evidence**:
  - DOI: 10.3389/fnhum.2018.00509 — Uses asSWLDA classifier to discriminate mental workload between Easy and Hard road segments during real driving, with training on Normal+Rush hour conditions.
- **Kernel Notes**: 
  - Verify event ID mapping from events.tsv (paper uses 'Easy'/'Hard' labels but dataset contains 7-digit trigger codes; derive labels by mapping road complexity conditions from trigger codes).
  - Compute 8s moving average for WL score as referenced in paper.
  - (replaces Normal Task 1 from original analysis.md: Driving Condition Classification had different epoch method and multi-class labels, whereas this task is binary workload classification via segmentation)

### Normal Task 1: Driving Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 7-digit codes require mapping from dataset README. Codes 2310001/2310002/4111101 dominate (>10k each); all others are minority classes (1k-1.8k). Group by leading 3-4 digits for higher-level condition classification.

 | Event | y | Meaning |
 |-------|---|---------|
 | `2310001` | 0 | Driving condition 231, variant 1 |
 | `2310002` | 1 | Driving condition 231, variant 2 |
 | `4111101` | 2 | Driving condition 411, variant 1 |


## Data Quality Notes

- 7-digit hierarchical trigger codes require decode from README or paper.
- Codes 2310001/2310002/4111101 dominate (>10k each); other codes are minority classes.
- Subject count not specified in BIDS metadata.

## References

- **Reference**: `Driving with Autonomous Aids`
