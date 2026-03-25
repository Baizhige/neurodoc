# Prediction Error

**Dataset**: `openneuro_ds003846` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003846
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 50
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

A virtual reality haptic interaction study where participants reached out to touch spawned virtual boxes while receiving varied combinations of visual, vibrotactile, and electrical muscle stimulation (EMS) feedback. Trials were marked as "normal" (congruent feedback) or "conflict" (incongruent prediction error condition), allowing investigation of multisensory prediction error processing. Three feedback modality conditions were run in separate sessions: visual-only, vibrotactile-only, and combined EMS conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: reaction time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003846

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `box` | 559 files | short | raw | Box spawned or box touched event |
| `vibroFeedback` | 198 files | short | raw | Vibrotactile feedback onset |
| `block` | 79 files | short | raw | Block start marker |
| `visualFeedback` | 50 files | short | raw | Visual feedback onset |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `reaction_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: ERP target detection (P300/Oddball)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Target vs non-target stimulus events
- **Evidence**: P300/oddball paradigm appears as core study objective. Source: https://openneuro.org/datasets/ds003846 DOI: https://doi.org/10.18112/openneuro.ds003846.v2.0.2


### Normal Task 1: Normal vs Conflict Prediction Error (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Events are richly annotated with metadata (reaction time, trial number, ISI, cube identity). The normal/conflict label is embedded in the event string. Epoch on box:touched events and extract the normal_or_conflict field for the label. Reaction time is also available as a regression target.

| Event | y | Meaning |
 |-------|---|------|
 | `box:touched;...normal_or_conflict:normal` | 0 | Normal (congruent) trial - box touched, expected feedback |
 | `box:touched;...normal_or_conflict:conflict` | 1 | Conflict (prediction error) trial - incongruent feedback |
## Data Quality Notes

- Events contain full JSON-like annotation strings; label extraction requires parsing the event description
- Multiple sessions per subject (EMS, Vibro, Visual) with differing session lengths
- Sampling rate is ~500 Hz (exact value varies slightly across files)

## References

- **Reference**: `Cyber-Physical Systems: Prediction Error`
