# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 38 | **Channels**: 65 | **Sampling Rate**: 1450 Hz
**Manual Review**: Pending

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) was toggled ON or OFF. The study investigated how DBS of the internal capsule affects cognitive control and prefrontal cortex function. No trial-level event markers are present in the BIDS EEG files; the DBS condition (ON/OFF) is tracked as metadata rather than inline event triggers.

## File Scan Result

> **Kernel SHA256**: `bf3a10b5d04d0f32a58fa26fc4a49a951fe98ee23080a912f303cac4ce7292fc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_2` | 1296 | event | raw | Interference trial (high-interference MSIT trial) |
| `event_4` | 2592 | event | raw | Control trial (low interference) |
| `event_6` | 1296 | event | raw | AFMSIT trial (active foreground MSIT task trial) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Cognitive control decoding (interference vs control trials)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.4 s, target_events = [`event_2`, `event_4`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `interference_trial` (event_2) | 1 | High-interference MSIT trial (cognitive conflict) |
  | `control_trial` (event_4) | 0 | Control trial (low interference) |
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4
- **Kernel Notes**: Dataset has no inline EEG event triggers; all trial labels must be derived by parsing BIDS events.tsv files to extract `trial_type` column. Verify mapping: event_2 (1296 occurrences) → interference trials, event_4 (2592 occurrences) → control trials. Epoch window captures pre-stimulus baseline (-1.5s) and post-stimulus cognitive processing (+3.4s) aligned to MSIT trial onset.

### Classical Task 2: DBS stimulation state classification (ON vs OFF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.9 s, overlap = 0.0, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `DBS_ON` | 1 | Deep brain stimulation turned ON during recording |
  | `DBS_OFF` | 0 | Deep brain stimulation turned OFF during recording |
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4
- **Kernel Notes**: DBS ON/OFF is a sustained experimental condition stored as subject-level metadata (participants.tsv), NOT as inline EEG events. All three event types (event_2, event_4, event_6) share the same DBS condition within a recording session. Use epoch_by_long_event_hdf5 with tmin=0, tmax=4.9s matching trial duration. Implement metadata lookup table mapping subject/session/run to DBS_ON/DBS_OFF for label assignment.

### Classical Task 3: AFMSIT task classification (active foreground MSIT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.4 s, target_events = [`event_6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `afmsit_trial` (event_6) | 0 | Active foreground MSIT task trial |
- **Evidence**:
  - DOI: 10.18112/openneuro.ds001784.v1.1.2
- **Kernel Notes**: Use task label 'afmsit' from BIDS dataset. Event_6 (1296 occurrences) corresponds to afmsit task trials. Verify timing aligns with MSIT trial structure (4.9s total duration). Epoch window -1.5s to +3.4s captures stimulus-locked neural activity for cognitive control assessment.

### Potential Task 1: Task engagement decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `engaged` | 1 | Actively performing MSIT task |
  | `passive` | 0 | Free behavior or rest periods |
- **Evidence**:
  - DOI: 10.1088/1741-2552/ab2c58
- **Kernel Notes**: Related work from same research group (Widge et al.) demonstrates continuous mental effort detection using conflict-based behavioral tasks. Implement fixed CCA decoder for continuous task engagement estimation. Requires annotation of behavioral segments or use of inter-trial intervals for passive baseline.

### Potential Task 2: Cognitive performance regression (RT/accuracy prediction)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 1.0 s, target_events = [`event_2`, `event_4`, `event_6`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `trial_outcome` | RT (ms) or accuracy (%) | Behavioral performance metrics per trial |
- **Evidence**:
  - DOI: 10.1088/1741-2552/acd0d5
- **Kernel Notes**: Simulation study demonstrates optimization of DBS parameters for cognitive control using MSIT behavioral outcomes (reaction time, accuracy). Extract trial-level RT/accuracy from BIDS events.tsv if available, or derive from stimulus-locked response patterns. Target variable: continuous RT or binary accuracy for regression/classification respectively.
