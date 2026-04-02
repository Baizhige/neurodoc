# Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant depression (EEG)

**Dataset**: `openneuro_ds001784` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001784
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 38 | **Channels**: 65.0 | **Sampling Rate**: 1450.0 Hz

## Paradigm

Participants with treatment-resistant depression performed a modified Multi-Source Interference Task (MSIT) integrated with emotional stimuli (IAPS images) while deep brain stimulation (DBS) was toggled ON or OFF. The study investigated how DBS of the internal capsule affects cognitive control and prefrontal cortex function. No trial-level event markers are present in the BIDS EEG files; the DBS condition (ON/OFF) is tracked as metadata rather than inline event triggers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001784

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; DBS condition tracked via metadata |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Cognitive control decoding (interference vs control trials)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.4 s, target_events = [`interference`, `control`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `control` | 0 | Control trial (low interference) |
  | `interference` | 1 | Interference trial (high cognitive conflict) |
- **Super Meta Notes**: Labels derived from experimental design metadata; trial type (interference/control) inferred from task timing and Psychophysics Toolbox markers. No inline EEG events present; reconstruction from metadata required.
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4 — This Nature Communications paper analyzes EEG data from the openneuro_ds001784 dataset, examining how VCVS deep brain stimulation affects cognitive control via the MSIT task, measuring interference vs control trial performance and prefrontal theta oscillations.
- **Kernel Notes**: Must reconstruct trial onsets from stimulus timing metadata (IAPS image onset). Apply baseline correction using -0.5s to -0.1s pre-stimulus. Epoch is stimulus-locked to IAPS image onset.

### Primary Task 2: DBS stimulation state classification (ON vs OFF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 3.4 s, target_events = [`DBS_ON`, `DBS_OFF`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `DBS_OFF` | 0 | Deep brain stimulation OFF |
  | `DBS_ON` | 1 | Deep brain stimulation ON |
- **Super Meta Notes**: DBS condition stored as subject-level metadata, not inline EEG triggers. Must merge with trial-level epochs post-extraction.
- **Evidence**:
  - DOI: 10.1038/s41467-019-09557-4 — This Nature Communications paper analyzes EEG data from the openneuro_ds001784 dataset, examining how VCVS deep brain stimulation affects cognitive control via the MSIT task, measuring stimulation ON vs OFF effects on prefrontal theta oscillations and clinical outcomes.
- **Kernel Notes**: DBS ON/OFF is a session-level condition. Must match epochs to corresponding DBS condition from participants.tsv metadata. Response-locked alternative: tmin=-1.5s to response, tmax=+1.5s after response.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: DBS ON vs OFF condition labels are subject-level metadata. If DBS condition is available from participants.tsv, it can be used as a subject-level binary label post-hoc.

## Data Quality Notes

- No trial-level event markers detected in any EEG files; only continuous recordings available.
- DBS condition (ON/OFF) distinguishes experimental conditions but is not encoded as EEG events.
- High sampling rate (1450 Hz); consider downsampling for computational efficiency.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Deep Brain Stimulation of the Internal Capsule Enhances Human Cognitive Control and Prefrontal Cortex Function. Nature Communications.`
