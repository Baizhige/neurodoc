# Audiocue walking study

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 273 | **Channels**: 115.0 | **Sampling Rate**: 512.0 Hz

## Paradigm

A mobile brain-body imaging (MoBI) study where participants walked on a treadmill and adapted their gait to auditory tone sequences. Participants walked at their preferred cadence, uncued, or responded to tempo shifts (delay or advance) in an auditory metronome. The study investigated the neural dynamics of gait adaptation and rhythm entrainment during real-world locomotion. Each walking condition is a sustained state lasting multiple seconds.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001971

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `PreferredCadence` | 234 (files) | long | raw | Sustained walking at participant's preferred cadence |
| `UncuedWalking` | 234 (files) | long | raw | Sustained uncued walking (no auditory cue) |
| `DelayTempo` | 232 (files) | long | raw | Sustained walking to delayed tempo auditory cue |
| `AdvanceTempo` | 230 (files) | long | raw | Sustained walking to advanced tempo auditory cue |
| `STATUS` | 39 | admin | raw | BioSemi system status marker - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Tempo-shift gait adaptation (step-advance vs step-delay)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`AdvanceTempo`, `DelayTempo`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AdvanceTempo` | 0 | Step shortening response to faster tempo cue |
  | `DelayTempo` | 1 | Step lengthening response to slower tempo cue |
- **Evidence**:
  - DOI: 10.1038/s41597-019-0223-2 — Data descriptor confirming step-locked epoching from -1s to 3s around heel strikes for tempo shift analysis
  - DOI: 10.1523/jneurosci.3543.15.2016 — EEG analysis of tempo shifts comparing beta band oscillatory networks between step-advance and step-delay adaptation
- **Kernel Notes**: Extract epochs time-locked to tempo shift onset events. `AdvanceTempo` marks cue shifts to faster tempo (step shortening); `DelayTempo` marks cue shifts to slower tempo (step lengthening). (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Gait Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`PreferredCadence`, `UncuedWalking`, `DelayTempo`, `AdvanceTempo`]
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PreferredCadence` | 0 | Walking at preferred cadence |
  | `UncuedWalking` | 1 | Uncued walking |
  | `DelayTempo` | 2 | Walking to delayed tempo cue |
  | `AdvanceTempo` | 3 | Walking to advanced tempo cue |
- **Notes**: Four-class classification of all gait conditions. Use step-locked epoching as per supporting papers. `STATUS` is BioSemi admin marker - excluded.

## Data Quality Notes

- MoBI dataset with 115 channels including motion capture; verify EEG-only channel selection.
- `STATUS` events are BioSemi system markers - do not include in target_events.
- Walking produces motion artifacts; independent component analysis (ICA) for artifact removal is recommended.
- Verify channel count consistency across subjects before pooling.

