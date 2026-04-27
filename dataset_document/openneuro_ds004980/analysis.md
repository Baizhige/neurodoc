# EEG Data for an Architectural Affordances Task

**Dataset**: `openneuro_ds004980` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004980
**Category**: Complex Applied | **Subjects**: 17 | **Files (Completed)**: 17 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants navigated a virtual architectural environment using keyboard controls while EEG was recorded to investigate neural responses to architectural affordances - the action possibilities offered by built spaces. The study examines how the brain processes spatial features (doors, corridors, rooms) that afford specific navigational actions. SAM (Self-Assessment Manikin) rating events mark periodic subjective valence/arousal/dominance assessments.

## File Scan Result

> **Kernel SHA256**: `a4ee721c67fc7e3f214518ed2177ab65a92391289b064776f62f01ad052f2cdc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

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
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["Key pressed: UpArrow (forward)", "Key pressed: RightArrow (turn right)", "Key pressed: LeftArrow (turn left)", "Door opened", "ColliderRoom1 has been entered", "ColliderRoom2 has been entered"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |-------|---|---|
  | `Key pressed: UpArrow (forward)` | 0 | Forward navigation |
  | `Key pressed: RightArrow (turn right)` | 1 | Right turn action |
  | `Key pressed: LeftArrow (turn left)` | 2 | Left turn action |
  | `Door opened` | 3 | Door affordance activated |
  | `ColliderRoom1 has been entered` | 4 | Room 1 spatial boundary |
  | `ColliderRoom2 has been entered` | 5 | Room 2 spatial boundary |

- **Evidence**: DOI: 10.1111/ejn.16461 — "Human brain dynamics dissociate early perceptual and late motor-related stages of affordance processing" (Berlin TU research group; virtual 3D environment affordance task with door navigation and SAM ratings; partial support for paradigm relevance)
- **Kernel Notes**: Epochs align to event onset. Key released events captured but not used as primary alignment points. SAM events (SAM:start, SAM:completed) must be excluded from navigation epochs — treat separately in Normal Task 2. Admin events (Reset insideActivator flag, player position reseted) excluded. Re-verify event IDs against actual BIDS files during kernel execution.

### Normal Task 2: SAM Rating Assessment
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = ["SAM:start", "SAM:completed"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |-------|---|---|
  | `SAM:start` | 0 | SAM rating initiated |
  | `SAM:completed` | 1 | SAM rating completed |

- **Evidence**: DOI: 10.1111/ejn.16461 — Mentions SAM ratings as experimental design element; paradigm explicitly records valence/arousal/dominance assessments during virtual navigation
- **Kernel Notes**: Separate task from navigation classification. Use SAM:start as alignment point to capture pre-rating baseline and rating response. Player entered/exited SAM Activator events provide zone context but SAM:start/SAM:completed are primary epoch alignment markers.

### Potential Task 1: Navigation Error Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.8 s, target_events = ["Wall touched: trial failed!"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |-------|---|---|
  | `Wall touched: trial failed!` | 1 | Navigation error detected |

- **Evidence**: Paradigm supports error-related processing analysis; wall collision events indicate failed affordance actions
- **Kernel Notes**: Single-class detection task. Could be used as contrasting condition against successful navigation (Normal Task 1). Event count (2183 total across dataset) suggests adequate trials for detection analysis.

### Potential Task 2: Spatial Boundary Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 1.2 s, target_events = ["ColliderRoom1 has been entered", "ColliderRoom2 has been entered", "Player left StartSquare"]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

  | Event | y | Meaning |
  |-------|---|---|
  | `Player left StartSquare` | 0 | Start zone exit |
  | `ColliderRoom1 has been entered` | 1 | Room 1 entered |
  | `ColliderRoom2 has been entered` | 2 | Room 2 entered |

- **Evidence**: DOI: 10.1111/ejn.16461 — Architectural transitions investigated as affordance markers
- **Kernel Notes**: Focus on spatial boundary crossings as discrete environmental events. Plausible from paradigm alone without direct classification=relevant reference. Could complement door affordance analysis in Normal Task 1.