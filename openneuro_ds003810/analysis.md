# Motor Imagery vs Rest - Low-Cost EEG System

**Dataset**: `openneuro_ds003810` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003810
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 50
**Channels**: 15 | **Sampling Rate**: 125 Hz

## Paradigm

Participants performed kinesthetic motor imagery of grasping movements with the dominant hand during EEG recording using a low-cost consumer-grade EEG system. Sessions included a preliminary run of actual hand movements followed by motor imagery blocks alternating with resting-state baselines. OpenViBE (OVTK) event triggers mark trial onset, cue type, feedback, and session boundaries. The study evaluates BCI performance using motor imagery and demonstrates applicability of affordable EEG hardware.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003810

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `OVTK_GDF_Right` | 50 | long | raw | Right-hand motor imagery cue onset |
| `OVTK_GDF_Tongue` | 50 | long | raw | Tongue motor imagery cue onset (second class) |
| `OVTK_GDF_Start_Of_Trial` | 50 | short | raw | Trial start marker |
| `OVTK_GDF_Cross_On_Screen` | 50 | short | raw | Fixation cross display (inter-trial) |
| `OVTK_GDF_Feedback_Continuous` | 50 | short | raw | Continuous BCI feedback onset |
| `OVTK_GDF_End_Of_Trial` | 50 | short | raw | Trial end marker |
| `OVTK_GDF_Correct` | 50 | short | raw | Correct classification feedback |
| `OVTK_GDF_Incorrect` | 50 | short | raw | Incorrect classification feedback |
| `OVTK_StimulationId_BaselineStart` | 50 | rest | raw | Resting baseline period start |
| `OVTK_StimulationId_BaselineStop` | 50 | rest | raw | Resting baseline period end |
| `OVTK_StimulationId_Beep` | 50 | short | raw | Auditory beep cue for trial start |
| `OVTK_StimulationId_Train` | 48 | short | raw | Training phase marker |
| `OVTK_StimulationId_ExperimentStart` | 46 | admin | raw | Experiment start marker |
| `OVTK_StimulationId_ExperimentStop` | 48 | admin | raw | Experiment stop marker |
| `OVTK_GDF_End_Of_Session` | 48 | admin | raw | Session end marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `OVTK_StimulationId_BaselineStart`, `OVTK_StimulationId_BaselineStop`, `OVTK_StimulationId_Beep`, `OVTK_StimulationId_Train`, `OVTK_StimulationId_ExperimentStart`, `OVTK_StimulationId_ExperimentStop`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds003810 DOI: https://doi.org/10.1016/j.heliyon.2020.e03425


### Primary Task 2: Publisher-defined BIDS task: MIvs Rest RUN2
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003810 DOI: https://doi.org/10.1016/j.heliyon.2020.e03425


### Primary Task 3: Publisher-defined BIDS task: MIvs Rest RUN3
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003810 DOI: https://doi.org/10.1016/j.heliyon.2020.e03425


### Normal Task 1: Motor imagery category classification (binary, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Motor imagery periods are typically 4-6 s; use long-event epoching. 10 subjects with 5 files each (50 total). Low-cost 15-channel EEG at 125 Hz; limited spatial and temporal resolution compared to research-grade systems.

| Event | y | Meaning |
 |-------|---|------|
| `OVTK_GDF_Right` | 1 | Right hand motor imagination period |
| `OVTK_GDF_Tongue` | 0 | Tongue movement imagination period (control type) |
## Data Quality Notes

- Low-cost EEG system; lower signal quality and spatial resolution than research-grade systems.
- Low sampling rate (125 Hz); limits temporal resolution and applicable frequency range.
- `OVTK_StimulationId_ExperimentStart/Stop` and `OVTK_GDF_End_Of_Session` are admin markers; exclude from epoching.

## References

- **Reference**: `Motor Imagery vs Rest using a low-cost EEG system. OpenNeuro ds003810.`
