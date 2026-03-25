# Placebo Neuroepo multisession

**Dataset**: `openneuro_ds003195` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003195
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 19 | **Sampling Rate**: 200 Hz

## Paradigm

Resting-state EEG recorded from Parkinson's disease patients who received a placebo (not active Neuroepo) during a six-month drug evaluation trial. Recordings were taken before and after the administration period. This is the placebo control arm companion to ds003194 (Neuroepo treatment). Protocol includes resting-state (eyes open/closed), hyperventilation, and recovery periods.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003195

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ojos cerrados` | 20 (files) | long | raw | Eyes-closed resting state |
| `ojos abiertos` | 19 (files) | long | raw | Eyes-open resting state |
| `hiperventilacion 1` | 19 (files) | long | raw | Hyperventilation period 1 |
| `hiperventilacion 2` | 19 (files) | long | raw | Hyperventilation period 2 |
| `hiperventilacion 3` | 19 (files) | long | raw | Hyperventilation period 3 |
| `recuperacion` | 19 (files) | long | raw | Recovery period after hyperventilation |
| `hiperventilacion 4` | 12 (files) | long | raw | Hyperventilation period 4 |
| `discontinuity` | 8 (files) | admin | raw | Recording discontinuity marker - exclude |
| `photic stimulation` | 3 (files) | long | raw | Photic stimulation block |
| `fotoestimulacion` | 3 (files) | long | raw | Photic stimulation (Spanish label) |
| `HPVOJOS ABIERTOS` | 2 (files) | long | raw | Eyes-open during hyperventilation |
| `hipervantilacion 4` | 1 (file) | long | raw | Hyperventilation period 4 (variant spelling) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `photic stimulation`, `fotoestimulacion`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Task placebo 6m
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003195 DOI: https://doi.org/10.18112/openneuro.ds003195.v1.0.4


### Primary Task 2: Publisher-defined BIDS task: Task placebo pre
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003195 DOI: https://doi.org/10.18112/openneuro.ds003195.v1.0.4


### Normal Task 1: Brain State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `discontinuity` is a recording gap marker - excluded. Sparse counts for photic stimulation (3 files) and HPVOJOS (2 files); consider merging equivalent Spanish/English labels. Placebo arm of Neuroepo trial (NCT04110678).

| Event | y | Meaning |
 |-------|---|------|
 | `ojos cerrados` | 0 | Eyes-closed resting state |
 | `ojos abiertos` | 1 | Eyes-open resting state |
 | `hiperventilacion 1` | 2 | Hyperventilation period 1 |
 | `hiperventilacion 2` | 3 | Hyperventilation period 2 |
 | `hiperventilacion 3` | 4 | Hyperventilation period 3 |
 | `recuperacion` | 5 | Recovery period |
 | `hiperventilacion 4` | 6 | Hyperventilation period 4 |
 | `photic stimulation` | 7 | Photic stimulation |
 | `fotoestimulacion` | 8 | Photic stimulation (Spanish) |
 | `HPVOJOS ABIERTOS` | 9 | Eyes-open during hyperventilation |
 | `hipervantilacion 4` | 10 | Hyperventilation period 4 (variant spelling) |
## Data Quality Notes

- Clinical recording from Parkinson's patients; expect higher artifact rate.
- `photic stimulation` and `fotoestimulacion` are equivalent labels - merge if needed.
- `hipervantilacion 4` is a spelling variant of `hiperventilacion 4` - treat as same condition.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `NCT04110678`
