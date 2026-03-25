# Intracranial EEG During Cortical Stimulation Evoking Visual Effects

**Dataset**: `openneuro_ds005169` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005169
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 112 | **Channels**: 82 | **Sampling Rate**: 4096 Hz

## Paradigm

Intracranial EEG was recorded from drug-resistant epilepsy patients undergoing presurgical evaluation during direct electrical stimulation (DES) of cortical sites that evoke visual hallucinations and perceptual effects. `Comment/prestim` (112 total) marks pre-stimulation baseline periods and `Comment/poststim` (111) marks post-stimulation response windows. UUID-format Comment events (2-10 per file) are patient-specific or trial-specific annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005169

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/prestim` | 112 | long | raw | Pre-stimulation baseline period |
| `Comment/poststim` | 111 | long | raw | Post-stimulation response window |
| `Comment/[UUID]` | 2-10/file | admin | raw | Patient/trial-specific annotation (UUID format, exclude) |
| `Comment/[electrode] [mA] SYM` | ~2/file | admin | raw | Stimulation parameter annotation (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Comment/prestim`, `Comment/poststim`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Dcs
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://doi.org/10.1002/hbm.25749


### Normal Task 1: Pre vs Post Stimulation (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: UUID-format and electrode/mA Comment events are admin - exclude. Very high sampling rate (4096 Hz) - downsample before processing. iEEG data; stimulation artifact present in poststim windows.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Comment/prestim` | 0 | Pre-stimulation baseline |
 | `Comment/poststim` | 1 | Post-stimulation response |
## Data Quality Notes

- Very high sampling rate (4096 Hz) - downsample to <=1000 Hz before analysis.
- Intracranial EEG - different noise profile from scalp EEG; stimulation artifacts expected.
- UUID-format Comment events are patient-specific annotations - exclude from epoching.

## References

- **Reference**: `Imaging the effective networks associated with cortical function through intracranial high-frequency stimulation. DOI: 10.1002/hbm.25749`
