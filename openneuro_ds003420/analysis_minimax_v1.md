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

### Primary Task 1: Reaction Time Regression from Visual Object Naming
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.5 s, target_events = [`meaningful_pictures`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `meaningful_pictures` | continuous | Voice onset time (reaction time) in seconds, measured from stimulus onset to vocalization |
- **Super Meta Notes**: Reaction time derived from speech recording: time between stimulus onset and participant vocalization. Available for subset of subjects. Used as regression target for correlation with gamma-band (30-45Hz) network modularity metrics.
- **Evidence**:
  - DOI: 10.1088/1741-2552.aad7b1 — Analyzes 256-channel EEG from 20 subjects performing visual object naming of meaningful vs meaningless images, computing functional brain networks in gamma band (30-45Hz) from stimulus onset to 500ms and correlating network modularity metrics with reaction time (voice onset latency).
- **Kernel Notes**: Extract epochs aligned to meaningful picture stimulus onset; filter gamma band (30-45Hz); compute connectivity/network metrics; correlate with response_time from misc channel.

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
