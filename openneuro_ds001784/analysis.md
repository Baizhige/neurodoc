# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 38 | **Channels**: 65 | **Sampling Rate**: 1450 Hz

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) was toggled ON or OFF. The study investigated how DBS of the internal capsule affects cognitive control and prefrontal cortex function. No trial-level event markers are present in the BIDS EEG files; the DBS condition (ON/OFF) is tracked as metadata rather than inline event triggers.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; DBS condition tracked via metadata |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Cognitive control decoding (interference vs control trials)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`interference_trial`, `control_trial`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `interference_trial` | 1 | High-interference MSIT trial (cognitive conflict) |
  | `control_trial` | 0 | Control trial (low interference) |
- **Super Meta Notes**: Derived from experimental design metadata. Trial type (interference/control) inferred from task timing and Psychophysics Toolbox markers. Dataset has no inline EEG event triggers; trial labels are derived from BIDS events.tsv files. Kernel step: Parse events.tsv to extract trial_type column and map to binary labels.
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4 — Shows interference vs control trial classification as primary cognitive control analysis
- **Kernel Notes**: Read BIDS events.tsv files for each subject to extract `trial_type` column. Epochs should be aligned to IAPS stimulus onset (trial start). Verify that tmin/tmax align with -1.5s to +3.4s window around IAPS onset. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: DBS stimulation state classification (ON vs OFF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4.9 s (matching trial duration), overlap = 0.0, target_events = [`DBS_ON`, `DBS_OFF`] | segment_length = 4.9 s *, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `DBS_ON` | 1 | Deep brain stimulation turned ON during recording |
  | `DBS_OFF` | 0 | Deep brain stimulation turned OFF during recording |
- **Super Meta Notes**: Derived from subject-level metadata. DBS condition stored as participant/stimulus metadata not inline EEG triggers. Kernel step: Read participants.tsv or Stimulus metadata to obtain DBS condition per session/run, then assign epoch-level labels based on which condition each trial belongs to.
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4 — Shows DBS ON vs OFF as key two-class classification for understanding stimulation effects on prefrontal cortex function
- **Kernel Notes**: DBS ON/OFF is a sustained experimental condition per recording session, not trial-level events. For long-event method: epoch_by_long_event_hdf5 with tmin=0, tmax=session_duration. For segmentation: use segment_length matching trial duration (4.9s). Assign labels by matching segment timing to DBS condition from participants.tsv. (replaces Classical Task 2 from original analysis.md)

### Classical Task 3: BIDS task "afmsit" (active foreground MSIT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s *, tmax = 3.4 s *, target_events = [`afmsit_trial`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `afmsit_trial` | 0 | Active foreground MSIT task trial |
- **Evidence**:
  - DOI: 10.18112/openneuro.ds001784.v1.1.2 — Dataset metadata defines 'afmsit' as a completed BIDS task
- **Kernel Notes**: Use task label 'afmsit' from BIDS dataset. Epoch by event markers in events.tsv with task='afmsit'. Verify timing aligns with MSIT trial structure. (replaces Classical Task 2 from original analysis.md)

### Classical Task 4: BIDS task "rest"
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `rest_segment` | 0 | Resting-state recording segment |
- **Evidence**:
  - DOI: 10.18112/openneuro.ds001784.v1.1.2 — Dataset metadata defines 'rest' as a completed BIDS task
- **Kernel Notes**: Sliding window segmentation on continuous rest recordings. Use default 4s window with 50% overlap. (replaces Classical Task 3 from original analysis.md)

### Potential Task 1: Resting/Continuous Segmentation (general)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (no trial-level labels available)
- **Notes**: DBS ON vs OFF condition labels are subject-level metadata. If DBS condition is available from participants.tsv, it can be used as a subject-level binary label post-hoc.

## Data Quality Notes

- No trial-level event markers detected in any EEG files; only continuous recordings available.
- DBS condition (ON/OFF) distinguishes experimental conditions but is not encoded as EEG events.
- High sampling rate (1450 Hz); consider downsampling for computational efficiency.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review