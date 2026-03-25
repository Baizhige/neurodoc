# EEG Experiment measuring ERPs in VR

**Dataset**: `openneuro_ds005841` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005841
**Category**: Complex Applied | **Subjects**: 48 | **Files (Completed)**: 288 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

An investigation of event-related potentials (ERPs) during visual tasks performed within a virtual reality (VR) environment. Stimuli vary along two orthogonal dimensions: lighting (DARK vs LIGHT) and reference type (RAND = random/unpredictable vs REF = reference/predictable). The 2x2 design yields four event codes measuring visual ERP responses under prediction-error conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005841

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RAND_DARK` | 288 | short | raw | Random (unpredictable) stimulus - dark condition |
| `RAND_LIGHT` | 288 | short | raw | Random (unpredictable) stimulus - light condition |
| `REF_DARK` | 288 | short | raw | Reference (predictable) stimulus - dark condition |
| `REF_LIGHT` | 288 | short | raw | Reference (predictable) stimulus - light condition |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Lumperp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005841 DOI: https://doi.org/10.18112/openneuro.ds005841.v1.0.0


### Primary Task 2: Publisher-defined BIDS task: Signalscreen
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005841 DOI: https://doi.org/10.18112/openneuro.ds005841.v1.0.0


### Primary Task 3: Publisher-defined BIDS task: Regfront
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005841 DOI: https://doi.org/10.18112/openneuro.ds005841.v1.0.0


### Normal Task 1: VR Stimulus Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Perfectly balanced 4-class design (288 each); primary contrast is RAND vs REF (prediction error) and DARK vs LIGHT (luminance). Count per file reflects 1 file per subject.

 | Event | y | Meaning |
 |-------|---|---------|
 | `RAND_DARK` | 0 | Random dark stimulus |
 | `RAND_LIGHT` | 1 | Random light stimulus |
 | `REF_DARK` | 2 | Reference dark stimulus |
 | `REF_LIGHT` | 3 | Reference light stimulus |
## Data Quality Notes

- VR environment may introduce motion artifacts; apply ICA for artifact removal.
- 48 subjects x 6 sessions = 288 files; verify session-level consistency.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- _No paper reference available_
