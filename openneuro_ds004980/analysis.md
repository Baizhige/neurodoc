# EEG Data for an Architectural Affordances Task

**Dataset**: `openneuro_ds004980` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004980
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 17 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants navigated a virtual architectural environment using keyboard controls while EEG was recorded to investigate neural responses to architectural affordances - the action possibilities offered by built spaces. The study examines how the brain processes spatial features (doors, corridors, rooms) that afford specific navigational actions. SAM (Self-Assessment Manikin) rating events mark periodic subjective valence/arousal/dominance assessments.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Key released: UpArrow (forward)` | 13072 | short | raw | Forward key release |
| `Key pressed: UpArrow (forward)` | 13063 | short | raw | Forward key press |
| `Key pressed: RightArrow (turn right)` | 8915 | short | raw | Right turn key press |
| `Key released: RightArrow (turn right)` | 8911 | short | raw | Right turn key release |
| `Key pressed: LeftArrow (turn left)` | 7360 | short | raw | Left turn key press |
| `Key released: LeftArrow (turn left)` | 7356 | short | raw | Left turn key release |
| `Player left StartSquare` | 6904 | short | raw | Participant exits start zone |
| `Player entered SAM Activator` | 4584 | short | raw | SAM rating zone entered |
| `SAM:start` | 4521 | short | raw | SAM rating starts |
| `SAM:completed` | 4517 | short | raw | SAM rating completed |
| `Player left SAM Activator` | 4567 | short | raw | SAM rating zone exited |
| `Wall touched: trial failed!` | 2183 | short | raw | Navigation error |
| `Door opened` | 2427 | short | raw | Door affordance activated |
| `ColliderRoom1 has been entered` | 1528 | short | raw | Room 1 entered |
| `ColliderRoom2 has been entered` | 1523 | short | raw | Room 2 entered |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

### Info

- File scan not yet completed. Placeholder for future file structure details.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Default Task
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004980 DOI: https://doi.org/10.18112/openneuro.ds004980.v1.0.0


### Normal Task 1: Navigation Action Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: SAM events (SAM:start, SAM:completed) mark subjective rating periods - treat separately or exclude. Reset/admin events (Reset insideActivator flag, player position reseted) are admin.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Key pressed: UpArrow (forward)` | 0 | Forward navigation |
 | `Key pressed: RightArrow (turn right)` | 1 | Right turn |
 | `Key pressed: LeftArrow (turn left)` | 2 | Left turn |
 | `Door opened` | 3 | Door affordance activated |
 | `ColliderRoom1 has been entered` | 4 | Room 1 entered |
 | `ColliderRoom2 has been entered` | 5 | Room 2 entered |

## Data Quality Notes

- 30+ unique event types; focus on key presses and spatial boundary events.
- SAM rating events mark active rating periods - exclude from navigation classification.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004980