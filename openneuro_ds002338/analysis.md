# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP2

**Dataset**: `openneuro_ds002338` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002338
**Category**: Action/Output | **Subjects**: 16 | **Files (Completed)**: 169 | **Channels**: 64.0 | **Sampling Rate**: 5000.0 Hz

## Paradigm

Participants performed right-hand motor imagery and received neurofeedback (1D or 2D display) during simultaneous EEG-fMRI acquisition to learn to regulate sensorimotor rhythms. The task alternated between sustained Rest blocks and Task-NF (neurofeedback) blocks. MRI gradient artifacts are marked with TPULSE markers which must be excluded. This is XP2 of a two-experiment series; XP1 is ds002336.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002338

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 101 (files) | long | raw | Rest / baseline block |
| `Task-NF` | 101 (files) | long | raw | Neurofeedback motor imagery task block |
| `Response/R128` | 68 | admin | raw | BrainVision response trigger / MRI sync - exclude |
| `Stimulus/S 99` | 68 | admin | raw | BrainVision admin code - exclude |
| `Stimulus/S 2` | 68 | admin | raw | BrainVision admin code - exclude |
| `Stimulus/S101` | 39 | admin | raw | BrainVision admin code - exclude |
| `Pulse Artifact/R` | 34 | admin | raw | MRI gradient pulse artifact - exclude |
| `Time 0/` | 34 | admin | raw | MRI timing reference - exclude |
| `TPULSE/TSTART` | 34 | admin | raw | MRI T-pulse start - exclude |
| `TPULSE/TPEAK` | 34 | admin | raw | MRI T-pulse peak - exclude |
| `TPULSE/TEND` | 34 | admin | raw | MRI T-pulse end - exclude |
| `Stimulus/S 35` | 2 | admin | raw | Sparse BrainVision code - exclude |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 99`, `Stimulus/S 2`, `Stimulus/S101`, `Stimulus/S 35`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Imagery class labels (e.g., left/right hand, feet, tongue; dataset-specific)
- **Evidence**: Dataset references indicate MI BCI paradigm as core benchmark. Source: https://openneuro.org/datasets/ds002338 DOI: https://doi.org/10.18112/openneuro.ds002338.v2.0.2


### Primary Task 2: Publisher-defined BIDS task: 1d NF
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002338 DOI: https://doi.org/10.18112/openneuro.ds002338.v2.0.2


### Primary Task 3: Publisher-defined BIDS task: MIpost
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002338 DOI: https://doi.org/10.18112/openneuro.ds002338.v2.0.2


### Normal Task 1: Motor Imagery Neurofeedback State Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All Stimulus/S*, TPULSE/*, Pulse Artifact/R, Time 0/, and R128 are MRI/system admin markers - excluded. High sampling rate (5000 Hz); downsample before epoching.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Rest` | 0 | Rest / baseline block |
 | `Task-NF` | 1 | Motor imagery neurofeedback block |
## Data Quality Notes

- MRI gradient artifacts contaminate EEG; TPULSE markers indicate artifact windows.
- High sampling rate (5000 Hz); downsampling recommended.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Simultaneous MRI-EEG during a motor imagery neurofeedback task: an open access brain imaging dataset for multi-modal data integration`
