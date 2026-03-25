# HID (High-Density EEG Operational Dataset)

**Dataset**: `openneuro_ds004851` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004851
**Category**: Complex Applied | **Subjects**: 65 | **Files (Completed)**: 65 | **Channels**: 72 | **Sampling Rate**: 2048 Hz

## Paradigm

High-density EEG recorded in an operational context involving multiple conditions encoded as 4-digit numeric trigger codes. The code structure suggests stimulus classes (1xxx: primary task events, 7xxx/8xxx: secondary stimulus categories) within a cognitive workload or situational awareness paradigm.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004851

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1010` | 2181 | short | raw | Primary event onset (type A) |
| `1011` | 2179 | short | raw | Primary event (type A variant) |
| `1020` | 1970 | short | raw | Primary event (type B) |
| `1021` | 1970 | short | raw | Primary event (type B variant) |
| `1040` | 1912 | short | raw | Primary event (type D) |
| `1041` | 1912 | short | raw | Primary event (type D variant) |
| `8100` | 973 | short | raw | Secondary stimulus category 8, type 1 |
| `8101` | 973 | short | raw | Secondary stimulus category 8, type 1 variant |
| `1061` | 474 | short | raw | Primary event (type F variant) |
| `1060` | 474 | short | raw | Primary event (type F) |
| `8011` | 195 | short | raw | Secondary stimulus |
| `8010` | 195 | short | raw | Secondary stimulus |
| `8021` | 194 | short | raw | Secondary stimulus |
| `8020` | 194 | short | raw | Secondary stimulus |
| `7001`-`7019` | ~65 each | short | raw | Tertiary stimulus category (19 types) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: HID
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004851 DOI: https://doi.org/10.18112/openneuro.ds004851.v2.1.0


### Normal Task 1: Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Very high sampling rate (2048 Hz) - downsample before analysis. Full decode table required from dataset README.

 | Event | y | Meaning |
 |-------|---|---------|
 | `1010` | 0 | Primary event type A |
 | `1011` | 1 | Primary event type A variant |
 | `1020` | 2 | Primary event type B |
 | `1021` | 3 | Primary event type B variant |
 | `1040` | 4 | Primary event type D |
 | `1041` | 5 | Primary event type D variant |
 | `8100` | 6 | Secondary stimulus |
 | `8101` | 7 | Secondary stimulus variant |
## Data Quality Notes

- Very high sampling rate (2048 Hz) - downsample for efficiency.
- 30+ distinct codes; grouping by prefix category recommended.

## References

- **Reference**: `HID`
