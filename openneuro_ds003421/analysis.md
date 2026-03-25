# HD-EEGtask (Dataset 2)

**Dataset**: `openneuro_ds003421` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003421
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 80
**Channels**: 257 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants completed a multi-condition experiment including resting state, visual and auditory object naming tasks, and a recognition-based working memory task, with high-density 257-channel EEG recording. This is Dataset 2 of the conneXion project (companion to ds003420). Trigger codes 0 and 1 mark stimulus onset and response events; the specific kernel provides speech onset timing as `response_time` for regression analysis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003421

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 60 (files) | long | raw | Sustained task or stimulus condition 1 onset |
| `0` | 57 (files) | long | raw | Sustained task or stimulus condition 0 onset |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Pictures Naming
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003421 DOI: https://doi.org/10.18112/openneuro.ds003421.v1.0.2


### Normal Task 1: Task State Classification / Regression (regression + long_event)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: N/A (null(regression primary; codes require decoding))
- **Notes**: Codes 0/1 mark multi-second sustained task states (resting, naming, memory) - long_event epoching appropriate. Specific kernel decodes numeric codes and extracts speech onset as `response_time`. Not all 80 files contain both events (60 vs 57).

- **Regression target**:`response_time`(speech onset / naming latency from misc channel)
## Data Quality Notes

- Trigger codes 0/1 require semantic decoding from events.tsv or conneXion project documentation.
- High-density 257-channel EGI array; significant computational overhead.
- Multi-condition design includes resting state, naming, and working memory - verify condition assignments.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `HD-EEGtask (Dataset 2) - conneXion project`
