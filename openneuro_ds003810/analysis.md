# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50
**Channels**: 15 | **Sampling Rate**: 125 Hz

## Paradigm

Participants performed kinesthetic motor imagery of grasping movements with the dominant hand during EEG recording using a low-cost consumer-grade EEG system. Sessions included a preliminary run of actual hand movements followed by motor imagery blocks alternating with resting-state baselines. OpenViBE (OVTK) event triggers mark trial onset, cue type, feedback, and session boundaries. The study evaluates BCI performance using motor imagery and demonstrates applicability of affordable EEG hardware.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `OVTK_GDF_Right` | 50 | event | raw | Right-hand motor imagery cue onset |
| `OVTK_GDF_Tongue` | 50 | event | raw | Tongue motor imagery cue onset (second class) |
| `OVTK_GDF_Start_Of_Trial` | 50 | event | raw | Trial start marker |
| `OVTK_GDF_Cross_On_Screen` | 50 | event | raw | Fixation cross display (inter-trial) |
| `OVTK_GDF_Feedback_Continuous` | 50 | event | raw | Continuous BCI feedback onset |
| `OVTK_GDF_End_Of_Trial` | 50 | event | raw | Trial end marker |
| `OVTK_GDF_Correct` | 50 | event | raw | Correct classification feedback |
| `OVTK_GDF_Incorrect` | 50 | event | raw | Incorrect classification feedback |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Resting baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Resting baseline period end |
| `OVTK_StimulationId_Beep` | 50 | event | raw | Auditory beep cue for trial start |
| `OVTK_StimulationId_Train` | 48 | event | raw | Training phase marker |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Experiment start marker |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Experiment stop marker |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session end marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Motor imagery binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `OVTK_GDF_Right` | 1 | Right hand motor imagery (kinesthetic grasp imagination) |
  | `OVTK_GDF_Tongue` | 0 | Rest/idle condition (tongue imagination as control) |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108225 — Data in Brief paper describing motor imagery vs rest EEG dataset with 4-second imagery periods and event markers OVTK_GDF_Right (MI) and OVTK_GDF_Tongue (rest)
  - DOI: 10.1016/j.heliyon.2020.e03425 — Original study presenting consumer-grade MI-BCI system, classifying hand motor imagery vs rest with epochs extracted from 0.5-2.5s after stimulus onset
- **Kernel Notes**: Extract epochs from 0.5s to 2.5s relative to motor imagery cue onset. Label OVTK_GDF_Right events as class 1 (motor imagery) and OVTK_GDF_Tongue as class 0 (rest). (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Low-cost EEG system; lower signal quality and spatial resolution than research-grade systems.
- Low sampling rate (125 Hz); limits temporal resolution and applicable frequency range.
- `OVTK_StimulationId_ExperimentStart/Stop` and `OVTK_GDF_End_Of_Session` are admin markers; exclude from epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review