# EEG and motion capture data set for a full-body/joystick rotation task

**Dataset**: `openneuro_ds004460` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004460
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 40
**Channels**: 160 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a spatial orientation task in a virtual environment, navigating via either active physical rotation of the body or joystick-controlled rotation on a flat screen. EEG and motion capture were simultaneously recorded to compare neural dynamics of active (full-body) vs. passive (joystick) spatial navigation and heading changes.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004460

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ground_rotate` | 40 | short | raw | Ground/environment rotation onset |
| `object_fadeInOut` | 40 | short | raw | Object appearance/disappearance |
| `'/Event/Label/targ_color_change'` | 53 | short | raw | Target color change event |
| `('/Event/Category/Participant response'` | 40 | short | raw | Participant response event |
| `'/Event/Label/wii_button'` | 40 | short | raw | Wii/button press response |
| `('/Event/Category/Experimental stimulus/Instruction/Attend/'` | 80 | short | raw | Attend instruction stimulus |
| `('/Event/Category/Experimental stimulus/Instruction/Read/'` | 40 | short | raw | Read instruction stimulus |
| `duration` | 40 | admin | raw | Duration annotation |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `('/Event/Category/Experimental stimulus/Instruction/Attend/'`, `('/Event/Category/Experimental stimulus/Instruction/Read/'`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Physical vs. Joystick Rotation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 12.0 s, target_events = [`ground_rotate`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ground_rotate` | 0 | Physical full-body rotation condition (physR) |
  | `ground_rotate` | 1 | Joystick-controlled visual flow condition (joyR) |
- **Super Meta Notes**: (meta=super) Derived by inferring rotation condition from run-level metadata (body vs joystick). Kernel step: Read run annotation to determine if the run corresponds to physR or joyR condition, then assign y=0 or y=1 to all epochs within that run.
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — Classification of physical rotation vs joystick rotation conditions during a spatial orientation task with 13s epochs
- **Kernel Notes**: Verify that `ground_rotate` corresponds to rotation onset. Run metadata determines physR vs joyR condition assignment. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Object-Related Neural Response Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`object_fadeInOut`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `object_fadeInOut` | 0 | Object appearance (fade in) * |
  | `object_fadeInOut` | 1 | Object disappearance (fade out) * |
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — Paper analyzes neural responses to virtual environment stimuli including object/sphere onset
- **Kernel Notes**: Verify object_fadeInOut event meaning. Check if event encodes direction (fade-in vs fade-out). May need to parse event metadata.

### Primary Task 3: Participant Response Locked Epoching
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`/Event/Label/wii_button`, `(/Event/Category/Participant response`] (note: original has trailing quote issue in raw events list)
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `/Event/Label/wii_button` | 0 | Wii button press response |
  | `(/Event/Category/Participant response` | 1 | General participant response * |
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — Button press marks trial end; response-locked analysis performed
- **Kernel Notes**: Correct raw event ID parsing required due to unusual event string formatting in dataset.

### Normal Task 1: Navigation Mode Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: HED (Hierarchical Event Descriptor) tags are used as event labels - very verbose names. 160 channels includes motion capture channels. 40 files from 20 subjects (2 conditions: body vs. joystick rotation).

| Event | y | Meaning |
|-------|---|------|
| `ground_rotate` | 0 | Spatial rotation stimulus |
| `object_fadeInOut` | 1 | Object appearance/disappearance |
| `'/Event/Label/targ_color_change'` | 2 | Target color change |

## Data Quality Notes

- HED-format event labels are very long strings - ensure proper parsing
- 160 channels includes motion capture data channels in addition to EEG
- 40 files from 20 subjects (2 runs each: body rotation and joystick rotation)

