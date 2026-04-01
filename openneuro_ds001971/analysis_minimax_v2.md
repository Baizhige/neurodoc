# Audiocue walking study

**Dataset**: `openneuro_ds001971` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001971
**Category**: Complex Applied | **Subjects**: 18 | **Files (Completed)**: 273 | **Channels**: 115.0 | **Sampling Rate**: 512.0 Hz

## Paradigm

A mobile brain-body imaging (MoBI) study where participants walked on a treadmill and adapted their gait to auditory tone sequences. Participants walked at their preferred cadence, uncued, or responded to tempo shifts (delay or advance) in an auditory metronome. The study investigated the neural dynamics of gait adaptation and rhythm entrainment. The experimental blocks (conditions) last multiple seconds, within which discrete steps (heel strikes) and tone pips occur.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw condition block labels and step/tone markers.
- **Type 2 (Raw + Super meta integration)**: Map discrete step/tone markers (short events) to the active condition block (long events) they fall within to create super labels (e.g., classifying a step as an "AdvanceTempo_Step").
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`).

> **Selected Mode**: Type 2 + Type 3
> **Why**: Step-locked epochs require mapping discrete step events to overarching condition blocks (Super meta derivation).
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds001971

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `PreferredCadence` | 234 | long | raw | Sustained walking condition block (preferred cadence) |
| `UncuedWalking` | 234 | long | raw | Sustained walking condition block (uncued) |
| `DelayTempo` | 232 | long | raw | Sustained walking condition block (delayed tempo) |
| `AdvanceTempo` | 230 | long | raw | Sustained walking condition block (advanced tempo) |
| `heel_strike` / `tone` | N/A | short | raw | Discrete markers for steps or auditory cues |
| `STATUS` | 39 | admin | raw | BioSemi system status marker - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Tempo-shift gait adaptation (step-locked classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`AdvanceTempo_Step`, `DelayTempo_Step`]
- **Label Route**: `Annotation`
- **Meta Level**: super (Derived by checking which block the `heel_strike` falls into)
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AdvanceTempo_Step` | 0 | Heel strike occurring during an AdvanceTempo block |
  | `DelayTempo_Step` | 1 | Heel strike occurring during a DelayTempo block |
- **Evidence**:
  - DOI: 10.1038/s41597.019.0223.2 — Data descriptor confirms step-locked epoching from -1s to 3s around heel strikes.
- **Kernel Notes**: Must extract discrete step events (`short`) and map them to the active condition block (`long`) to generate the super tags `AdvanceTempo_Step` and `DelayTempo_Step`.

### Normal Task 1: Gait Condition Classification (Continuous Block Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = [`PreferredCadence`, `UncuedWalking`, `DelayTempo`, `AdvanceTempo`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PreferredCadence` | 0 | Walking at preferred cadence |
  | `UncuedWalking` | 1 | Uncued walking |
  | `DelayTempo` | 2 | Walking to delayed tempo cue |
  | `AdvanceTempo` | 3 | Walking to advanced tempo cue |
- **Notes**: Instead of step-locking, this task treats the entire condition block as a continuous state and uses a sliding window (4.0s) to classify the overall cognitive/motor state.

## Data Quality Notes

- MoBI dataset with 115 channels (High-Density EEG + Motion Capture). Ensure kernel isolates EEG channels for standard tasks.
- Heavy motion artifacts expected; ICA is critical.

## Review
| **Sampling Rate**: 512.0 Hz | **Manual Review**: Mingze Tang |
