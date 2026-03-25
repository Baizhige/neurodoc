# RS_TMSEEG_Data

**Dataset**: `openneuro_ds001849` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds001849
**Category**: Biological State | **Subjects**: N/A | **Files (Completed)**: 120 | **Channels**: 30.0 | **Sampling Rate**: 5000.0 Hz

## Paradigm

Resting-state EEG data recorded in conjunction with Transcranial Magnetic Stimulation (TMS). Subjects were at rest (no active task) while TMS pulses were delivered; the R128 marker in BrainVision format marks a system/response trigger present in all files but does not indicate a meaningful task event. The primary scientific interest is resting-state oscillatory dynamics and TMS-evoked potentials.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001849

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `R128` | 120 (files) | admin | raw | BrainVision system/response trigger present in every file - not a task event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Tmseegrest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds001849 DOI: https://doi.org/10.18112/openneuro.ds001849.v1.0.2


### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no task events; R128 is admin))
- **Notes**: R128 appears in all 120 files and is a BrainVision recording artifact marker. High sampling rate (5000 Hz); consider downsampling. TMS artifact rejection may be needed if TMS pulses are captured in recording.
## Data Quality Notes

- R128 is a BrainVision system marker present in every file - it is not a stimulus or response event.
- High sampling rate (5000 Hz); significant downsampling required before most analyses.
- TMS artifacts may contaminate EEG within the first ~50 ms post-pulse; apply TMS artifact rejection if analyzing TMS-evoked potentials.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `RS_TMSEEG_Data`
