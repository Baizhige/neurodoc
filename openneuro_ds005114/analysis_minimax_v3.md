# EEG: DPX Cognitive Control Task in Acute Mild TBI

**Dataset**: `openneuro_ds005114` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005114
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 217 | **Channels**: 65 | **Sampling Rate**: 500 Hz

## Paradigm

The Dot Pattern Expectancy (DPX) task, a version of the Continuous Performance Task, was used to assess proactive versus reactive cognitive control in sub-acute mild traumatic brain injury (mTBI) patients and healthy controls. Participants responded to cue-probe pairs (CueA/CueB x Probe aX/aY/bY), enabling decomposition of context-maintenance and response-inhibition processes via P3a/P3b ERP components.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005114

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Response: CueCorr` | 50287 | short | raw | Correct response to cue |
| `Response: Probe_Corr` | 46594 | short | raw | Correct response to probe |
| `CueAOnset` | 43580 | short | raw | Cue A stimulus onset |
| `Probe_aX_onset` | 35272 | short | raw | Probe aX onset (congruent with CueA) |
| `STATUS` | 19463 | admin | raw | System status marker (exclude) |
| `Practice: filler trigger` | 15787 | admin | raw | Practice trial filler (exclude) |
| `Probe_aY_onset` | 6443 | short | raw | Probe aY onset |
| `Probe_bY_onset` | 5428 | short | raw | Probe bY onset |
| `Response: Probe_Incorr` | 3626 | short | raw | Incorrect probe response |
| `Feedback: ProbeErr` | 3626 | short | raw | Error feedback |
| `CueBOnset` | 2661 | short | raw | Cue B stimulus onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`, `Practice: filler trigger`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: DPX
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification *, tmax = Needs verification *, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `CueAOnset` | 0 | Cue A onset |
  | `CueBOnset` | 1 | Cue B onset |
  | `Probe_aX_onset` | 2 | Probe aX (AX trial - expected) |
  | `Probe_aY_onset` | 3 | Probe aY (AY trial - unexpected) |
  | `Probe_bY_onset` | 4 | Probe bY (BY trial) |
- **Evidence**:
  - DOI: 10.1016/j.neuropsychologia.2019.107125 — DPX task used to assess cognitive control in mTBI vs controls (P3a/P3b ERP analysis)
- **Kernel Notes**: Epoch parameters (tmin/tmax) require verification from paper code or dataset documentation. Verify event ID mapping from events.tsv.

### Normal Task 1: Cue and Probe Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`CueAOnset`, `CueBOnset`, `Probe_aX_onset`, `Probe_aY_onset`, `Probe_bY_onset`, `Response: CueCorr`, `Response: Probe_Corr`]
- **Label Route**: `Annotation`
- **Target Definition**:
 | Event | y | Meaning |
 |-------|---|---------|
 | `CueAOnset` | 0 | Cue A onset |
 | `CueBOnset` | 1 | Cue B onset |
 | `Probe_aX_onset` | 2 | Probe aX (AX trial - expected) |
 | `Probe_aY_onset` | 3 | Probe aY (AY trial - unexpected) |
 | `Probe_bY_onset` | 4 | Probe bY (BY trial) |
 | `Response: CueCorr` | 5 | Correct cue response |
 | `Response: Probe_Corr` | 6 | Correct probe response |
- **Notes**: STATUS (19,463) and Practice: filler trigger (15,787) are admin - exclude. mTBI patients and healthy controls included; participant group labels in participants.tsv.

## Data Quality Notes

- STATUS and Practice filler triggers must be excluded from training.
- Dataset includes mTBI patients and healthy controls - group label in participants.tsv.

## Data Quality Notes

- STATUS and Practice filler triggers must be excluded from training.
- Dataset includes mTBI patients and healthy controls - group label in participants.tsv.

