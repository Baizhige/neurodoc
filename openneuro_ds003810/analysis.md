# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50
**Channels**: 15 | **Sampling Rate**: 125 Hz
**Manual Review**: Pending

## Paradigm

Participants performed kinesthetic motor imagery of grasping movements with the dominant hand during EEG recording using a low-cost consumer-grade EEG system. Sessions included a preliminary run of actual hand movements followed by motor imagery blocks alternating with resting-state baselines. OpenViBE (OVTK) event triggers mark trial onset, cue type, feedback, and session boundaries. The study evaluates BCI performance using motor imagery and demonstrates applicability of affordable EEG hardware.

## File Scan Result

> **Kernel SHA256**: `204b580e30144f23817b71b655180461fc838f45ca4013825290b5350fa9be00`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `OVTK_GDF_Correct` | 697 | event | raw | Correct classification feedback |
| `OVTK_GDF_Cross_On_Screen` | 1691 | event | raw | Fixation cross display (inter-trial) |
| `OVTK_GDF_End_Of_Session` | 48 | event | raw | Session end marker |
| `OVTK_GDF_End_Of_Trial` | 1689 | event | raw | Trial end marker |
| `OVTK_GDF_Feedback_Continuous` | 1689 | event | raw | Continuous BCI feedback onset |
| `OVTK_GDF_Incorrect` | 697 | event | raw | Incorrect classification feedback |
| `OVTK_GDF_Right` | 845 | event | raw | Right-hand motor imagery cue onset |
| `OVTK_GDF_Start_Of_Trial` | 1691 | event | raw | Trial start marker |
| `OVTK_GDF_Tongue` | 845 | event | raw | Tongue motor imagery cue onset (second class) |
| `OVTK_StimulationId_BaselineStart` | 50 | event | raw | Resting baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | event | raw | Resting baseline period end |
| `OVTK_StimulationId_Beep` | 1790 | event | raw | Auditory beep cue for trial start |
| `OVTK_StimulationId_ExperimentStart` | 46 | event | raw | Experiment start marker |
| `OVTK_StimulationId_ExperimentStop` | 48 | event | raw | Experiment stop marker |
| `OVTK_StimulationId_Train` | 48 | event | raw | Training phase marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Motor Imagery Binary Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = 0.5 s, tmax = 2.5 s, target_events = [`OVTK_GDF_Right`, `OVTK_GDF_Tongue`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `OVTK_GDF_Right` | 1 | Right hand motor imagery (kinesthetic grasp imagination) |
  | `OVTK_GDF_Tongue` | 0 | Rest/idle condition (tongue imagery as control class) |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108225 — Data in Brief paper describing motor imagery vs rest EEG dataset with 4-second imagery periods; explicitly maps to OpenNeuro ds003810 with 10 subjects, 15 channels, 125 Hz sampling; binary MI classification using OVTK event markers
  - DOI: 10.1016/j.heliyon.2020.e03425 — Original feasibility study presenting consumer-grade MI-BCI system; classifies kinesthetic grasp imagination vs idle using epochs extracted 0.5–2.5s post-stimulus onset
- **Kernel Notes**: OpenViBE OVTK markers indicate cue onset alignment (confirmed by DOI:10.1016/j.dib.2022.108225). OVTK_GDF_Tongue serves as rest/control class per DOI:10.1016/j.heliyon.2020.e03425. Epoch window avoids early stimulus artifact while capturing peak mu/beta event-related desynchronization. Exclude training markers (OVTK_StimulationId_Train) and session markers (OVTK_GDF_End_Of_Session, ExperimentStart/Stop) from epoching.

### Potential Task 1: Motor Imagery vs Resting Baseline Comparison
- **Task Type**: classification
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: tmin = -0.5 s, tmax = 3.5 s, segment_length = 4.0 s, overlap = null
- **Label Route**: Annotation
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `OVTK_StimulationId_BaselineStart` | 0 | Resting baseline period (control class) |
  | `OVTK_GDF_Right` | 1 | Right hand motor imagery (active class) |
- **Evidence**:
  - Paradigm description confirms alternating motor imagery blocks with resting-state baselines; baseline periods marked by OVTK_StimulationId_BaselineStart/Stop (50 events each)
- **Kernel Notes**: Use baseline periods as rest-class epochs for offline analysis. Window matches 4s imagery duration for balanced class comparison. Requires baseline correction using pre-stimulus interval. This approach extracts rest epochs directly from dedicated baseline blocks rather than using tongue imagery as a proxy for idle state.