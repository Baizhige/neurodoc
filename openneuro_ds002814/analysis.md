# A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans

**Dataset**: `openneuro_ds002814` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002814
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 168 | **Channels**: 68.0 | **Sampling Rate**: 1200.0 Hz

## Paradigm

A multimodal neuroimaging study (EEG + MEG/MRI) investigating the spatiotemporal dynamics of visual processing in humans. Despite the dataset title implying an active visual processing task, no event markers are detectable in the BIDS EEG files. The visual stimulation protocol may be encoded in other modality files or events are not available in the EEG files processed by the locator pipeline.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002814

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Task category Selectivity
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002814 DOI: https://doi.org/10.18112/openneuro.ds002814.v1.3.0


### Primary Task 2: Publisher-defined BIDS task: TODO: full task name for category Selectivity
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002814 DOI: https://doi.org/10.18112/openneuro.ds002814.v1.3.0


### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: No event markers found in EEG locator metadata. High sampling rate (1200 Hz); downsampling recommended. Part of a multimodal dataset - check MEG/MRI files for corresponding event timing.
## Data Quality Notes

- No event markers detected in any of the 168 EEG files.
- High sampling rate (1200 Hz); downsampling required before most analyses.
- Part of multimodal dataset; MEG or MRI-derived event timing may be applicable if aligned.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans`
