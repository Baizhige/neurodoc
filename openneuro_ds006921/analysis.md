# High-Density Resting-State EEG of Phantom Limb Pain and Controls

**Dataset**: `openneuro_ds006921` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006921
**Category**: Biological State | **Subjects**: 152 | **Files (Completed)**: 152 | **Channels**: 128 | **Sampling Rate**: 2400 Hz

## Paradigm

High-density resting-state EEG recordings were collected from three groups: amputees with phantom limb pain (PLP), amputees without phantom limb pain, and healthy controls. Recordings were made during eyes-open and eyes-closed conditions. The dataset enables investigation of neural correlates associated with phantom limb pain, cortical reorganization following amputation, and resting-state oscillatory differences across groups.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006921

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous resting-state EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds006921 DOI: https://doi.org/10.18112/openneuro.ds006921.v1.1.1


### Primary Task 2: Publisher-defined BIDS task: EYESOPEN
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006921 DOI: https://doi.org/10.18112/openneuro.ds006921.v1.1.1


### Primary Task 3: Publisher-defined BIDS task: EYESCLOSED
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006921 DOI: https://doi.org/10.18112/openneuro.ds006921.v1.1.1


### Normal Task 1: Resting-State Segmentation (segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no event markers; group labels from participants.tsv)
- **Notes**: No trial-level events. Group labels (PLP amputee / non-PLP amputee / healthy control) must be derived from participants.tsv metadata. Very high sampling rate (2400 Hz); downsample before analysis.
## Data Quality Notes

- Very high sampling rate (2400 Hz); downsample to 500-1000 Hz for most analyses.
- 152 files may include multiple sessions per subject; verify session structure.
- High-density 128-channel system (likely EGI/Geodesic); non-standard montage.

## References

- **Reference**: `High Density Resting State EEG of Phantom Limb Pain and Controls`
