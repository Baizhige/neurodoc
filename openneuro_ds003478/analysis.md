# EEG: Depression rest

**Dataset**: `openneuro_ds003478` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003478
**Category**: Biological State | **Subjects**: 122 | **Files (Completed)**: 243
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recording featuring alternating one-minute intervals of eyes-open and eyes-closed conditions in participants with varying scores on the Beck Depression Inventory (BDI). The study aims to identify EEG biomarkers of depression severity. Each session includes multiple alternating eyes-open and eyes-closed blocks, with `Start and Finish` markers indicating session boundaries. STATUS is a BioSemi admin marker.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003478

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Eyes Open` | 368 (files) | long | raw | Eyes-open resting state block (~1 min) |
| `Eyes Closed` | 368 (files) | long | raw | Eyes-closed resting state block (~1 min) |
| `STATUS` | 243 (files) | admin | raw | BioSemi system status marker - exclude |
| `Start and Finish` | 184 (files) | admin | raw | Session start/end boundary marker - exclude |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds003478 DOI: https://doi.org/10.18112/openneuro.ds003478.v1.1.0


### Normal Task 1: Eyes Open vs Eyes Closed Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is BioSemi admin marker; `Start and Finish` marks session boundaries - both excluded. Eyes-open vs eyes-closed is the primary binary classification. BDI scores in participants.tsv can serve as continuous regression targets for depression severity prediction.

| Event | y | Meaning |
 |-------|---|------|
 | `Eyes Open` | 0 | Eyes-open resting state (~1 min block) |
 | `Eyes Closed` | 1 | Eyes-closed resting state (~1 min block) |
## Data Quality Notes

- `STATUS` is BioSemi hardware marker - exclude.
- `Start and Finish` marks session boundaries - admin marker, exclude.
- Large dataset: 122 subjects, 243 files; subject-level BDI scores available for depression prediction.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `EEG: Depression rest`
