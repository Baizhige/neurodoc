# EEG: Reinforcement Learning in Parkinson's

**Dataset**: `openneuro_ds003506` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003506
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 84
**Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

This study investigates the Reward Positivity (RewP) EEG component in Parkinson's disease (PD) patients compared to matched healthy controls. Participants completed a reinforcement learning task with both volitional and instructed choices, earning rewards or receiving no-reward feedback based on their selections. The RewP, a frontocentral ERP component, scales with reward prediction error and mirrors dopamine-driven learning. The study examines whether PD diminishes this signal, given dopaminergic dysfunction in PD.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003506

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Imperative Stimulus` | 84 | short | raw | Cue stimulus requiring a response |
| `Left Button Choice` | 84 | short | raw | Left-hand button press response |
| `Right Button Choice` | 84 | short | raw | Right-hand button press response |
| `Instr` | 168 | short | raw | Instruction marker (Match/Choose) |
| `FB` | 252 | short | raw | Feedback stimulus (reward +1, no-reward 0) |
| `STATUS` | 84 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Imperative Stimulus`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Reward vs No-Reward Feedback Classification (RewP ERP Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -6.0 s, tmax = 2.0 s, target_events = [`FB: +1`, `FB: 0`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB: +1` | 1 | Reward feedback (reward) |
  | `FB: 0` | 0 | No-reward feedback (no-reward) |
- **Evidence**:
  - DOI: `10.1016/j.brainres.2019.146541` — This paper analyzes EEG data from 28 PD patients and 28 matched healthy controls completing a reinforcement learning task, epoching data around feedback onset (-6000 to 2000 ms) and comparing Reward Positivity (RewP) amplitude between groups for reward (+1) versus no-reward (0) feedback conditions.
- **Kernel Notes**: Apply baseline correction using -0.2s to 0s pre-stimulus period. Exclude `FB: 'Too Slow'` and `FB: 'No Match'` events as they are rare and task-specific. Target the frontocentral channels (Fz, FCz, Cz) for RewP analysis, though kernel should extract all EEG channels.

### Normal Task 1: Feedback type classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: FB events encode reward vs. no-reward outcomes; roughly balanced across subjects. Exclude `FB: 'Too Slow'` and `FB: 'No Match'` as they are rare and task-specific.

| Event | y | Meaning |
|-------|---|------|
| `FB: +1` | 1 | Reward feedback (reward) |
| `FB: 0` | 0 | No-reward feedback (no-reward) |

## Data Quality Notes

- 67 channels including VEOG and positional channels (X, Y, Z); exclude non-EEG channels before analysis.
- Two sessions per subject for some participants; verify session-level consistency.
- STATUS is a single system marker per file; exclude from epoching.

## References

- **Reference**: `An EEG marker of reward processing is diminished in Parkinson's disease. Brain Research, 2019. DOI: 10.1016/j.brainres.2019.146541`
