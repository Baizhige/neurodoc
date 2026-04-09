# DataSet2 - Visual Object Naming EEG (High-Density)

**Dataset**: `openneuro_ds002833` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002833
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 257 | **Sampling Rate**: 1000 Hz

## Paradigm

High-density 257-channel EEG recorded during a visual object naming or picture viewing task, companion to DataSet1 (ds002791). The DIN1 marker is an EGI/Geodesic system digital input trigger marking stimulus onset. The `unknown` label in 20 files indicates undecodable trigger codes for those sessions. The study likely involves the same visual object paradigm as ds002791 (30 object categories), recorded with an EGI system.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `DIN1` | 60 (files) | short | raw | EGI digital input trigger - stimulus onset marker |
| `unknown` | 20 (files) | admin | raw | Undecodable trigger code - treat as admin/uncertain |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

- **File scan status**: Completed (80 files)
- **Trigger verification**: DIN1 marker confirmed; unknown events require events.tsv cross-reference

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Pictures Naming
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002833 DOI: https://doi.org/10.18112/openneuro.ds002833.v1.0.0


### Normal Task 1: Stimulus-Locked ERP / Regression (regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to DIN1 onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: N/A (null (regression only; DIN1 serves as epoch anchor; `unknown` excluded))
- **Notes**: DIN1 is the EGI stimulus trigger; use as epoch anchor. `unknown` events are undecodable - exclude from target events. For classification, trial type information would need to come from events.tsv `trial_type` or `value` columns.

- **Regression target**: `response_time` from misc channel

## Data Quality Notes

- 257-channel EGI HydroCell array provides very high spatial density.
- `unknown` events in 20 files may indicate corrupted trigger codes - verify from events.tsv.
- DIN1 triggers mark stimulus onsets; actual stimulus identity requires events.tsv lookup.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002833