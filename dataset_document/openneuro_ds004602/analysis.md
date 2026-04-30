# Registered Replication Report of ERN/Pe Psychometrics

**Dataset**: `openneuro_ds004602` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004602
**Category**: Sensory/Response | **Subjects**: 182 | **Files (Completed)**: 546 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants completed Flanker, Stroop, and Go/no-go tasks to evaluate the psychometric reliability and convergent/divergent validity of error-related ERP components (ERN and Pe). The study tests whether error-related components are stable within individuals across tasks and sessions. Three task files per subject yield the 546-file count. `cor`/`err` mark correct/error responses; `con`/`inc` mark congruent/incongruent Flanker/Stroop trials; `go`/`ng`/`neu` mark Go/no-go trial types.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `cor` | 169236 | short | raw | Correct response (all tasks) |
| `go` | 58251 | short | raw | Go trial (Go/no-go task) |
| `con` | 54498 | short | raw | Congruent trial (Flanker/Stroop) |
| `inc` | 47242 | short | raw | Incongruent trial (Flanker/Stroop) |
| `err` | 24198 | short | raw | Error response (all tasks) |
| `neu` | 20890 | short | raw | Neutral trial condition |
| `ng` | 8636 | short | raw | No-go trial (Go/no-go task) |
| `boundary` | 545 | admin | raw | Segment boundary marker (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

- **Event file format**: HDF5
- **Sampling rate**: 500 Hz
- **Channel count**: 129

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Mixed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004602 DOI: https://doi.org/10.18112/openneuro.ds004602.v1.0.1


### Normal Task 1: Error vs Correct Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: boundary (545) is admin - exclude. cor (169,236) >> err (24,198) - significant class imbalance; undersample cor or use weighted loss. con/inc/go/ng/neu usable for separate task-level analyses.

 | Event | y | Meaning |
 |-------|--|--------|
 | `cor` | 0 | Correct response (ERN/Pe absent) |
 | `err` | 1 | Error response (ERN/Pe present) |


### Normal Task 2: Congruent vs Incongruent (binary, Flanker/Stroop)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 54,498 vs 47,242 - reasonably balanced. Filter by Flanker/Stroop task files only.

 | Event | y | Meaning |
 |-------|--|--------|
 | `con` | 0 | Congruent trial |
 | `inc` | 1 | Incongruent trial |

## Data Quality Notes

- boundary (545) is admin - exclude.
- 3 task files per subject (Flanker, Stroop, Go/no-go); filter by task for task-specific analyses.
- High channel count (129) may include non-EEG channels - verify channel types.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
