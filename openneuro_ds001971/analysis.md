# Audiocue walking study

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 273 | **Channels**: 115 | **Sampling Rate**: 512 Hz
**Manual Review**: Mingze Tang

## Paradigm

A mobile brain-body imaging (MoBI) study where participants walked on a treadmill and adapted their gait to auditory tone sequences. Participants walked at their preferred cadence, uncued, or responded to tempo shifts (delay or advance) in an auditory metronome. The study investigated the neural dynamics of gait adaptation and rhythm entrainment during real-world locomotion. Each walking condition is a sustained state lasting multiple seconds.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `PreferredCadence` | 234 (files) | event | raw | Sustained walking at participant's preferred cadence |
| `UncuedWalking` | 234 (files) | event | raw | Sustained uncued walking (no auditory cue) |
| `DelayTempo` | 232 (files) | event | raw | Sustained walking to delayed tempo auditory cue |
| `AdvanceTempo` | 230 (files) | event | raw | Sustained walking to advanced tempo auditory cue |
| `STATUS` | 39 | admin | raw | BioSemi system status marker - exclude |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Tempo-shift gait adaptation (step-advance vs step-delay)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`AdvanceTempo`, `DelayTempo`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AdvanceTempo` | 0 | Step shortening response to faster tempo cue |
  | `DelayTempo` | 1 | Step lengthening response to slower tempo cue |
- **Evidence**:
  - DOI: 10.1038/s41597-019-0223-2 — Data descriptor confirming step-locked epoching from -1s to 3s around heel strikes for tempo shift analysis
  - DOI: 10.1523/jneurosci.3543.15.2016 — EEG analysis of tempo shifts comparing beta band oscillatory networks between step-advance and step-delay adaptation
- **Kernel Notes**: Extract epochs time-locked to tempo shift onset events. `AdvanceTempo` marks cue shifts to faster tempo (step shortening); `DelayTempo` marks cue shifts to slower tempo (step lengthening). (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Gait Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`PreferredCadence`, `UncuedWalking`, `DelayTempo`, `AdvanceTempo`]
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review