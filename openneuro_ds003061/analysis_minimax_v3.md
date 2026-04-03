# EEG data from an auditory oddball task

**Dataset**: `openneuro_ds003061` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003061
**Category**: Sensory/Response | **Subjects**: 39 | **Files (Completed)**: 39
**Channels**: 79 | **Sampling Rate**: 256 Hz

## Paradigm

An auditory three-stimulus oddball task in which participants pressed a key in response to infrequent target tones among frequent standard tones and rare distractor tones. The paradigm is designed to elicit P300 event-related potentials. Event labels `stimulus` (tone onset) and `response` (keypress) are present in all 39 files; `STATUS` appears as a BioSemi admin marker in 2 files.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Status**: wait_manual_review
> **Evidence Keywords**: response_time, reaction time, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003061

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 39 (files) | short | raw | Auditory tone stimulus onset |
| `response` | 39 (files) | short | raw | Participant keypress response |
| `STATUS` | 2 (files) | admin | raw | BioSemi system status marker - exclude |

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
- **Candidate Trigger Labels**: `stimulus`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Auditory Oddball Target vs Standard Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus` | 0 | Standard non-target tone (500Hz, 70% frequency) |
  | `stimulus` | 1 | Oddball target tone (1000Hz, 15% frequency) |
- **Super Meta Notes**: Derived from raw event `stimulus` combined with trial_type metadata in events.tsv to distinguish target vs standard tone frequencies. Kernel step: Join stimulus events with events.tsv trial_type column to map each stimulus onset to target (1000Hz) or standard (500Hz) label.
- **Evidence**:
  - DOI: 10.1038/s41598-023-27528-0 — Two-class auditory oddball classification with target (1000Hz, 15%) vs standard (500Hz, 70%) tones, epochs -1 to 2s around stimulus onset
- **Kernel Notes**: Only include trials with correct responses: oddball targets require button press (`response` event present), standard tones require no response. Reaction time can be computed as time difference between `stimulus` and subsequent `response` events for target trials.

### Normal Task 1: Stimulus-Locked Auditory ERP/Regression (binary + regression)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is a BioSemi CM_in_range admin marker - excluded. `response` marks keypresses; reaction time computed per trial. The events.tsv `trial_type` may further distinguish standard, target, and distractor tone types - check for sub-classification.

| Event | y | Meaning |
|-------|---|------|
| `stimulus` | 0 | Auditory tone onset |

- **Regression target**:`response_time`(reaction time from stimulus to response, from misc channel)

## Data Quality Notes

- `STATUS` is a BioSemi hardware marker - not a task event; exclude from target_events.
- `response` events mark keypresses; sub-classification by tone type (standard/target/distractor) requires events.tsv lookup.
- 79-channel BioSemi EEG; check consistent montage across subjects.
- Verify channel count consistency across subjects before pooling.

