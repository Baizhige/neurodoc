# EEG and motion capture data set for a full-body/joystick rotation task

**Dataset**: `openneuro_ds004460` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004460
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 40 | **Channels**: 160 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a spatial orientation task in a virtual environment, navigating via either active physical rotation of the body or joystick-controlled rotation on a flat screen. EEG and motion capture were simultaneously recorded to compare neural dynamics of active (full-body) vs. passive (joystick) spatial navigation and heading changes.

## File Scan Result

> **Kernel SHA256**: `f873576bee7413de764fdb6572d83e95997183334f165f5d91c93b8979f39a37`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: no_events_detected` | 40 | event | raw | No event annotations found in data files |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Physical vs. Joystick Rotation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 12.0 s, target_events = [`ground_rotate`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `ground_rotate` | 0 | Physical full-body rotation condition (physR) |
  | `ground_rotate` | 1 | Joystick-controlled visual flow condition (joyR) |
- **Super Meta Notes**: Labels derived from run-level metadata (body vs joystick). Kernel step: read run annotation to determine physR or joyR condition, then assign y=0 or y=1 to all epochs within that run.
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — 19 participants, MoBI setup with physical vs joystick rotation conditions; classification of cortical dynamics between conditions with 13s epochs around ground_rotate
  - DOI: 10.1101/417972 — bioRxiv preprint of same study from 2018; identical methodology and dataset
- **Kernel Notes**: Verify `ground_rotate` corresponds to rotation onset. Run metadata determines physR vs joyR condition assignment. Cross-validate EEG events against motion capture rotation data for timing accuracy.

### Normal Task 1: Object Appearance vs. Disappearance Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`object_fadeInOut`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `object_fadeInOut` | 0 | Object appearance (fade in) |
  | `object_fadeInOut` | 1 | Object disappearance (fade out) |
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — Paper analyzes neural responses to virtual environment stimuli including object/sphere onset; indirect support for stimulus-locked analysis
- **Kernel Notes**: Verify `object_fadeInOut` event meaning. Parse event metadata to determine fade-in (y=0) vs fade-out (y=1) direction. Check if event encodes direction in auxiliary fields.

### Normal Task 2: Participant Response Locked Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`/Event/Label/wii_button`, `(/Event/Category/Participant response`] (sanitized)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `/Event/Label/wii_button` | 0 | Wii button press response |
  | `(/Event/Category/Participant response` | 1 | General participant response |
- **Evidence**:
  - DOI: 10.1038/s41598-021-97749-8 — Button press marks trial end; response-locked analysis performed in the paper; indirect support for motor response epochs
- **Kernel Notes**: Raw event ID strings contain malformed syntax (trailing quotes, parentheses) requiring sanitization before epoching. Correct event IDs: `/Event/Label/wii_button` and `(/Event/Category/Participant response`.

### Potential Task 1: Attend vs. Read Instruction Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`/Event/Category/Experimental stimulus/Instruction/Attend/`, `'/Event/Category/Experimental stimulus/Instruction/Read/'`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `/Event/Category/Experimental stimulus/Instruction/Attend/` | 0 | Attend instruction stimulus |
  | `/Event/Category/Experimental stimulus/Instruction/Read/` | 1 | Read instruction stimulus |
- **Evidence**: Plausible from paradigm alone; instruction events present in dataset (80 Attend + 40 Read occurrences) suggest task requiring attention vs reading phases
- **Kernel Notes**: Event strings require sanitization. Two instruction types may reflect different cognitive processing demands (visual attention vs comprehension).
