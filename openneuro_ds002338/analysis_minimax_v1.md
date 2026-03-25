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

### Primary Task 1: Motor Imagery Neurofeedback Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Rest`, `Task-NF`, `Task-MI`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest / baseline block |
  | `Task-NF` | 1 | Motor imagery neurofeedback block |
  | `Task-MI` | 1 | Motor imagery without neurofeedback block |
- **Evidence**:
  - DOI: 10.1038/s41597.020.0498-3 — Binary classification of Rest vs Motor Imagery neurofeedback task blocks (20s each) during simultaneous EEG-fMRI acquisition with right-hand kinaesthetic MI
  - DOI: 10.18112/openneuro.ds002338.v1.0.0 — Two-class motor imagery vs rest with tmin=0s, tmax=20s block duration, baseline=10s before motor imagery for ERD computation
  - DOI: 10.1101.862375 — XP2 dataset with 20s alternating Rest and Task-NF blocks, EEG NF scores computed as ERD in 8-30Hz band
- **Kernel Notes**: Labels derived directly from BrainVision stimulus markers (S 99 = Rest block start, S 2 = Task-NF/MI block start). Downsample from 5000 Hz to 200 Hz before epoching. Exclude TPULSE/* MRI gradient artifacts.

## Data Quality Notes

- MRI gradient artifacts contaminate EEG; TPULSE markers indicate artifact windows.
- High sampling rate (5000 Hz); downsampling recommended.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Simultaneous MRI-EEG during a motor imagery neurofeedback task: an open access brain imaging dataset for multi-modal data integration`
