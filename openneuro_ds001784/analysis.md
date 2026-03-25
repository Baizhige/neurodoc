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

### Primary Task 1: Cognitive control decoding in MSIT paradigm
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation` or `misc`
- **Target Definition**: Interference/congruency condition and/or DBS ON/OFF effect labels
- **Evidence**: Dataset/paper center on MSIT cognitive control under DBS modulation. Source: https://openneuro.org/datasets/ds001784 DOI: https://doi.org/10.18112/openneuro.ds001784.v1.1.2


### Primary Task 2: Publisher-defined BIDS task: Afmsit
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds001784 DOI: https://doi.org/10.18112/openneuro.ds001784.v1.1.2


### Primary Task 3: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds001784 DOI: https://doi.org/10.18112/openneuro.ds001784.v1.1.2


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
