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
- **Epoch Parameters**: tmin = -4.0 s, tmax = 10.0 s, target_events = [`AdvanceTempo`, `DelayTempo`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AdvanceTempo` | 0 | Step shortening (tempo advance) |
  | `DelayTempo` | 1 | Step lengthening (tempo delay) |
- **Evidence**:
  - DOI: 10.1523/jneurosci.3543_15_2016 — Segmenting EEG into epochs time-locked to cue tempo shifts (from -4s to 10s) to compare beta band oscillatory networks between step-advance and step-delay adaptation conditions.
  - DOI: 10.1038/s41597_019_0223_2 — Data descriptor presenting high-density EEG during gait adaptation with sudden tempo shifts (advance or delay), using step-locked epoching from -1s to 3s around heel strikes for analysis.
- **Kernel Notes**: Epochs are shift-locked (tempo change onset). The first paper uses -4s to +10s window; use this range for comprehensive analysis. Apply 0.5s epoch rejection for motion artifacts. Map AdvanceTempo to y=0, DelayTempo to y=1 for binary classification.

### Normal Task 1: Gait Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Walking conditions are sustained states (multiple seconds each) - use long_event epoching. `STATUS` is a BioSemi admin marker - excluded. Misc channel `response_time` available for regression.

 | Event | y | Meaning |
 |-------|---|---------|
 | `PreferredCadence` | 0 | Walking at preferred cadence |
 | `UncuedWalking` | 1 | Uncued walking |
 | `DelayTempo` | 2 | Walking to delayed tempo cue |
 | `AdvanceTempo` | 3 | Walking to advanced tempo cue |

## Data Quality Notes

- MoBI dataset with 115 channels including motion capture; verify EEG-only channel selection.
- `STATUS` events are BioSemi system markers - do not include in target_events.
- Walking produces motion artifacts; independent component analysis (ICA) for artifact removal is recommended.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: [`Johanna Wagner (June 6, 2019)`](https://www.jneurosci.org/content/36/7/2212.short)
