# HD-EEGtask (Dataset 1)

**Dataset**: `openneuro_ds003420` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds003420
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 92
**Channels**: 256 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed visual naming and spelling tasks of visually presented objects while high-density 256-channel EEG and speech onset data were recorded. This is Dataset 1 of the conneXion project. Trigger codes 0 and 1 mark stimulus events (likely object presentation onset and response/naming onset). Speech onset timing is also captured for reaction time analysis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, reaction time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003420

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 92 (files) | short | raw | Visual object stimulus onset (or naming task trigger) |
| `0` | 91 (files) | short | raw | Stimulus condition 0 (or response trigger) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Visual naming task decoding with speech latency
- **Task Type**: classification/regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation` and `misc`
- **Target Definition**: Stimulus condition codes (0/1) and speech-onset latency targets (`reaction_time`/`response_time`) when available.
- **Evidence**: ConneXion Dataset 1 records visual naming tasks with trigger events and speech-onset timing for latency analysis. Source: https://openneuro.org/datasets/ds003420 DOI: https://doi.org/10.18112/openneuro.ds003420.v1.0.2


### Normal Task 1: Stimulus-Locked ERP/Regression (regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: N/A (null(regression primary; code 1 serves as epoch anchor))
- **Notes**: Codes 0 and 1 require decoding from events.tsv - likely stimulus onset and response. Specific kernel decodes numeric codes and extracts speech onset timing as `response_time`. High-density 256-channel EEG provides excellent spatial coverage for naming task analysis.

- **Regression target**:`response_time`(speech onset / naming latency from misc channel)
## Data Quality Notes

- Trigger codes 0/1 require semantic decoding from events.tsv or conneXion project documentation.
- High-density 256-channel array; significant computational overhead.
- Speech onset timing recorded - useful for naming latency regression.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `conneXion`
