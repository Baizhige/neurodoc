# EEG Meditation Study

**Dataset**: `openneuro_ds001787` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz
**Manual Review**: Pending

## Paradigm

Subjects engaged in focused meditation sessions that were interrupted every two minutes by a brief probe assessing concentration level and mind-wandering. EEG was recorded continuously with stimulus markers at probe onsets and response markers at button-press responses. The study examined neural correlates of sustained attention and mind-wandering during meditation using ERP and time-frequency analysis.

## File Scan Result

> **Kernel SHA256**: `9d3d67226d1c06193b644bd0935be37f43659721c58212bfdc971c34eb530363`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_128` | 983 | event | raw | Meditation trial/probe onset (occurs ~41 times per subject at 2-min intervals) |
| `event_16` | 2 | event | raw | Session start/end marker |
| `event_2` | 1131 | event | raw | Button-press response to probe question |
| `event_254` | 4 | event | raw | Practice trial or calibration marker |
| `event_4` | 754 | event | raw | Probe type A (e.g., concentration level) |
| `event_8` | 258 | event | raw | Probe type B (e.g., mind-wandering assessment) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: EEG ISA-GSR Phase-Amplitude Coupling Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`event_128`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_128` | 1 | High d-prime group (high ISA-GSR coupling) |
  | `event_128` | 0 | Low d-prime group (low ISA-GSR coupling) |
- **Super Meta Notes**: Labels derived from raw event(s) [`event_128`, `event_2`] by computing d-prime of phase-amplitude coupling between EEG infraslow activity (0.01-0.1 Hz) phase and GSR amplitude during first 30s of each meditation trial. Kernel step: Load EEG and GSR signals, compute ISA phase via Hilbert transform, compute GSR amplitude envelope, calculate phase-amplitude coupling d-prime, threshold at median to create binary high/low coupling labels per subject.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paper analyzes coupling between EEG infraslow activity (0.01-0.1 Hz) phase and galvanic skin response amplitude during the first 30 seconds of each meditation trial from openneuro dataset ds001787, computing d-prime values and dividing subjects into high/low coupling groups.
- **Kernel Notes**: Event_128 (983 counts, ~41 per subject) corresponds to meditation trial/probe onsets occurring at ~2-minute intervals. Event_2 (1131 counts) corresponds to button-press responses. Verify event_128 maps to stimulus (meditation onset) per kernel recommendations. ISA-GSR coupling computed per subject then thresholded for binary classification.

### Normal Task 1: Probe Response ERP
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = 0.0, target_events = [`event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_2` | 1 | Probe response correct |
  | `event_2` | 0 | Probe response incorrect |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paradigm includes brief probes assessing concentration level and mind-wandering; event_2 likely corresponds to button-press responses to probe questions.
- **Kernel Notes**: Requires verification of which events (event_4, event_8, event_2) correspond to probe types and response correctness. Response accuracy labels may need to be derived from behavioral data or annotations if not directly available in events.tsv.

### Potential Task 1: Expert vs Novice Meditator Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`event_128`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_128` | 1 | Expert meditator |
  | `event_128` | 0 | Novice meditator |
- **Super Meta Notes**: Labels derived from subject group assignment (expert vs novice) as defined in dataset demographics. Kernel step: Load subject metadata from participants.tsv, map subject IDs to expertise level, create binary labels per trial.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paper compares expert versus novice meditators in EEG ISA-GSR coupling analysis.
- **Kernel Notes**: Requires verification of expertise level encoding in participants.tsv. Same epoch structure as ISA-GSR coupling since both tasks analyze the same 30-second meditation trial windows.