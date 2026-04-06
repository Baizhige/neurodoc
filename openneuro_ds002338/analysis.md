# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP2

**Dataset**: `openneuro_ds002338` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002338
**Category**: Action/Output | **Subjects**: 16 | **Files (Completed)**: 169 | **Channels**: 64 | **Sampling Rate**: 5000 Hz

## Paradigm

Participants performed right-hand motor imagery and received neurofeedback (1D or 2D display) during simultaneous EEG-fMRI acquisition to learn to regulate sensorimotor rhythms. The task alternated between sustained Rest blocks and Task-NF (neurofeedback) blocks. MRI gradient artifacts are marked with TPULSE markers which must be excluded. This is XP2 of a two-experiment series; XP1 is ds002336.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 101 (files) | event | raw | Rest / baseline block |
| `Task-NF` | 101 (files) | event | raw | Neurofeedback motor imagery task block |
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


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 99`, `Stimulus/S 2`, `Stimulus/S101`, `Stimulus/S 35`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Rest vs Motor Imagery Neurofeedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0 *, target_events = [`Rest`, `Task-NF`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest / baseline block |
  | `Task-NF` | 1 | Motor imagery neurofeedback task block |
- **Super Meta Notes**: (replaces Potential Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.18112/openneuro.ds002338.v1.0.0 — confirms binary Rest vs Task-NF classification with 20s alternating blocks
  - DOI: 10.1038/s41597-020-0498-3 — confirms block design with 20s Rest and 20s Task-NF, EEG downsampled to 200Hz for classification
  - DOI: 10.1101/862375 — confirms ERD computation for NF score from 20s task blocks
  - DOI: 10.1038/s41597-020-0498-3 — confirms S 99 indicates Rest block start, S 2 indicates Task block start
- **Kernel Notes**: Exclude MRI artifacts marked by TPULSE/* markers. High sampling rate (5000 Hz); downsample to 200-500 Hz for ML. Use long-event epoching on Rest and Task-NF annotations (20s duration each).

## Data Quality Notes

- MRI gradient artifacts contaminate EEG; TPULSE markers indicate artifact windows.
- High sampling rate (5000 Hz); downsampling recommended.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review