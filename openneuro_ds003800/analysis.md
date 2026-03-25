# Auditory Gamma Entrainment

**Dataset**: `openneuro_ds003800` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003800
**Category**: Sensory/Response | **Subjects**: 8 | **Files (Completed)**: 24
**Channels**: 19 | **Sampling Rate**: 250 Hz

## Paradigm

Elderly participants with dementia received 40 Hz amplitude-modulated (AM) auditory stimulation to induce gamma-band entrainment of brain oscillations. The paradigm alternated between active 40 Hz AM stimulation (Stimulus) periods and quiet rest periods. The study investigates whether auditory gamma entrainment can modulate neural oscillations in a dementia population, potentially as a therapeutic intervention. EEG was recorded using a standard 10-20 system.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003800

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 13 | long | raw | 40 Hz AM auditory stimulation period onset |
| `Rest` | 13 | long | raw | Resting/quiet period |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Auditory Gamma Entrainment
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003800 DOI: https://doi.org/10.18112/openneuro.ds003800.v1.0.0


### Primary Task 2: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003800 DOI: https://doi.org/10.18112/openneuro.ds003800.v1.0.0


### Normal Task 1: Stimulation period vs resting period (binary, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Stimulation and rest periods are sustained states (likely 1-5 min each); use long-event epoching. Only 8 subjects and 24 files - very small dataset. 19-channel EEG (10-20 system).

| Event | y | Meaning |
 |-------|---|------|
| `Stimulus` | 1 | 40 Hz AM auditory stimulation activation period |
| `Rest` | 0 | Rest/quiet period |
## Data Quality Notes

- Very small dataset (8 subjects, 24 files); results may not generalize.
- Elderly dementia population; data quality may be variable.
- 19-channel 10-20 EEG; limited spatial resolution.
- 250 Hz sampling rate; adequate for gamma entrainment analysis up to 125 Hz.

## References

- **Reference**: `Auditory Gamma Entrainment in Elderly with Dementia. OpenNeuro ds003800.`
