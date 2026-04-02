# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP1

**Dataset**: `openneuro_ds002336` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002336
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 107
**Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

Simultaneous EEG-fMRI acquisition during a kinesthetic motor imagery neurofeedback task. Subjects performed right-hand motor imagery or motor execution during sustained task blocks alternating with rest blocks, while receiving unimodal (EEG or fMRI) or bimodal neurofeedback. Each task block (Task-NF: neurofeedback, Task-ME: motor execution, Task-MI: motor imagery) is a sustained mental state lasting several seconds. BrainVision format with MRI artifact markers (TPULSE, R128) that must be excluded.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002336

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 93 (files) | long | raw | Rest / baseline block |
| `Task-NF` | 60 (files) | long | raw | Neurofeedback task block |
| `Task-ME` | 19 (files) | long | raw | Motor execution task block |
| `Task-MI` | 14 (files) | long | raw | Motor imagery task block |
| `Response/R128` | 14 | admin | raw | BrainVision response trigger / MRI sync - exclude |
| `Stimulus/S 99` | 14 | admin | raw | BrainVision stimulus code 99 - likely admin/sync |
| `Stimulus/S 2` | 14 | admin | raw | BrainVision stimulus code 2 - likely admin/sync |
| `Pulse Artifact/R` | 7 | admin | raw | MRI gradient pulse artifact marker - exclude |
| `Time 0/` | 7 | admin | raw | MRI timing reference marker - exclude |
| `TPULSE/TSTART` | 7 | admin | raw | MRI T-pulse start - exclude |
| `TPULSE/TPEAK` | 7 | admin | raw | MRI T-pulse peak - exclude |
| `TPULSE/TEND` | 7 | admin | raw | MRI T-pulse end - exclude |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 99`, `Stimulus/S 2`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Motor Imagery Neurofeedback Block Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0 *, target_events = [`Rest`, `Task-NF`, `Task-ME`, `Task-MI`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest / baseline block |
  | `Task-NF` | 1 | Neurofeedback task block (includes EEG-NF, fMRI-NF, EEG-fMRI-NF conditions) |
  | `Task-ME` | 2 | Motor execution block |
  | `Task-MI` | 3 | Motor imagery block |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0498-3 — Describes openneuro_ds002336 dataset with 20s rest and 20s task block design, marker codes S 99 for rest and S 2 for task; classifies rest vs motor imagery/motor execution/neurofeedback blocks.
  - DOI: 10.1101/862375 — Describes dataset containing right-hand motor imagery neurofeedback task with block design (20s rest, 20s task), classifies Rest vs Task-ME/MI/NF.
- **Kernel Notes**: Use long-event epoching to extract 20s blocks centered on each annotation. MRI artifact markers (TPULSE/*, Pulse Artifact/R, Time 0/, Response/R128) should be excluded from analysis. Downsample from 5000 Hz to 250-1000 Hz before epoching. (replaces Primary Tasks 1-3 and Normal Task 1 from original analysis.md)

## Data Quality Notes

- MRI gradient artifact contamination present; TPULSE markers indicate artifact regions.
- High sampling rate (5000 Hz); downsampling to 250-1000 Hz recommended.
- Task-ME and Task-MI blocks are sparsely present (subset of sessions only).
- Verify channel count consistency across subjects before pooling.

