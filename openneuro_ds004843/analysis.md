# Visual Situational Awareness EEG (T16)

**Dataset**: `openneuro_ds004843` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004843
**Category**: Others | **Subjects**: 7 | **Files (Completed)**: 7 | **Channels**: 70 | **Sampling Rate**: 256 Hz

## Paradigm

The `VisualSituationalAwareness` task investigates neural correlates of situational awareness during visual monitoring. Subjects viewed structured visual scenes with EEG recorded across multiple runs. The 5-digit hierarchical trigger codes encode stimulus category, load level, and response type. Codes 22301/22302 (3,384 each) and 22501/22502 (2,331/2,325) dominate; code 32000 (1,099) likely marks scene/trial boundaries. Codes ending in 01/02 mark paired conditions (onset/offset or left/right).

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `22301` | 3384 | short | raw | Condition 2-2-3, variant 01 |
| `22302` | 3384 | short | raw | Condition 2-2-3, variant 02 |
| `22501` | 2331 | short | raw | Condition 2-2-5, variant 01 |
| `22502` | 2325 | short | raw | Condition 2-2-5, variant 02 |
| `22102` | 1327 | short | raw | Condition 2-2-1, variant 02 |
| `22101` | 1325 | short | raw | Condition 2-2-1, variant 01 |
| `32000` | 1099 | admin | raw | Scene/trial boundary marker (exclude) |
| `22601` | 436 | short | raw | Condition 2-2-6, variant 01 |
| `22602` | 436 | short | raw | Condition 2-2-6, variant 02 |
| `42001` | 382 | short | raw | Condition 4-2-0, variant 01 |
| `42002` | 382 | short | raw | Condition 4-2-0, variant 02 |
| `22001` | 372 | short | raw | Condition 2-2-0, variant 01 |
| `22002` | 372 | short | raw | Condition 2-2-0, variant 02 |
| `12201` | 306 | short | raw | Condition 1-2-2, variant 01 |
| `12202` | 306 | short | raw | Condition 1-2-2, variant 02 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

Placeholder for additional file scan metadata.


## Tasks

### Primary Task 1: Publisher-defined BIDS task: Visual Situational Awareness
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004843 DOI: https://doi.org/10.18112/openneuro.ds004843.v1.0.0


### Normal Task 1: Visual Situational Awareness (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `32000` (1,099) is a scene/trial boundary - exclude. Very small dataset (7 files); balance classes by undersampling. 5-digit codes require README or paper decode.

 | Event | y | Meaning |
 |-------|---|---------|
 | `22301` | 0 | Condition 22301 |
 | `22302` | 1 | Condition 22302 |
 | `22501` | 2 | Condition 22501 |
 | `22502` | 3 | Condition 22502 |
 | `22101` | 4 | Condition 22101 |
 | `22102` | 5 | Condition 22102 |
 | `22601` | 6 | Condition 22601 |
 | `22602` | 7 | Condition 22602 |
## Data Quality Notes

- Only 7 files - very small dataset for training.
- 5-digit hierarchical codes require decode from README or paper.
- `32000` is a boundary/transition marker - exclude from epoching.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004843