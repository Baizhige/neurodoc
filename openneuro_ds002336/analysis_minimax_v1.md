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

### Primary Task 1: Rest vs Motor Imagery/Execution Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Rest`, `Task-NF`, `Task-ME`, `Task-MI`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest / baseline block (triggered by S 99 marker) |
  | `Task-MI` | 1 | Motor imagery task block |
  | `Task-ME` | 2 | Motor execution task block |
  | `Task-NF` | 3 | Neurofeedback task block |
- **Evidence**:
  - DOI: 10.1038/s41597-020-0498-3 — Describes openneuro_ds002336 dataset with 20s rest/20s task block design, marker codes (S 99=rest, S 2=task), and classification of Rest vs Task-ME/MI/NF blocks
  - DOI: 10.1101/862375 — Validates the dataset with block-design (20s rest, 20s task) using BrainVision markers S 99 for rest and S 2 for task onset
  - DOI: 10.3389/fnhum.2017.00193 — Presents the experimental protocol (10 subjects, 64-channel EEG, 5kHz, 20s block design) for motor imagery neurofeedback comparing rest and task blocks
- **Kernel Notes**: Block duration is 20s per the experimental protocol. Use raw BrainVision markers S 99 and S 2 to identify block onsets. Exclude MRI artifact markers (TPULSE/*, Pulse Artifact/R). Downsample 5000Hz to 200Hz recommended for feature extraction.

### Primary Task 2: Neurofeedback Condition Classification (EEG-NF vs fMRI-NF vs EEG-fMRI-NF)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Task-NF`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Task-NF` (NF condition A) | 0 | EEG-only neurofeedback |
  | `Task-NF` (NF condition B) | 1 | fMRI-only neurofeedback |
  | `Task-NF` (NF condition C) | 2 | Bimodal EEG-fMRI neurofeedback |
- **Super Meta Notes**: Labels are derived from experimental condition metadata (run type and NF condition) rather than raw BrainVision event markers. The paper describes 6 run types (MLOC, MI_pre, NF1-3, MI_post) with 3 NF conditions (A=EEG-NF, B=fMRI-NF, C=EEG-fMRI-NF). Task-NF blocks contain the NF condition information in the derived events.tsv.
- **Evidence**:
  - DOI: 10.3389/fnhum.2017.00193 — Describes the paradigm comparing EEG-NF, fMRI-NF, and EEG-fMRI-NF conditions during right-hand kinesthetic motor imagery with 20s block design
- **Kernel Notes**: NF condition labels must be derived from the experimental run metadata or events.tsv derivatives, not from raw BrainVision markers. Requires joining with BIDS-sidecar or derivatives information to map Task-NF blocks to specific NF condition (A/B/C).

### Primary Task 3: Binary Motor Imagery vs Rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Rest`, `Task-MI`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest / baseline block |
  | `Task-MI` | 1 | Motor imagery task block |
- **Evidence**:
  - DOI: 10.3389/fnhum.2017.00193 — Describes two-class motor imagery vs rest classification for laterality-based neurofeedback with 20s task blocks alternating with 20s rest blocks
- **Kernel Notes**: Simplified binary classification focusing only on motor imagery (Task-MI) vs rest. Excludes Task-ME and Task-NF for pure MI BCI decoding.

### Normal Task 1: Motor Imagery / Neurofeedback State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: MRI artifact markers (TPULSE/*, Pulse Artifact/R, Time 0/, R128) are all admin markers - excluded. High sampling rate (5000 Hz); downsample before epoching. Task-ME and Task-MI are sparse (14-19 files).

| Event | y | Meaning |
 |-------|---|------|
 | `Rest` | 0 | Rest / baseline block |
 | `Task-NF` | 1 | Neurofeedback task block |
 | `Task-ME` | 2 | Motor execution block |
 | `Task-MI` | 3 | Motor imagery block |

## Data Quality Notes

- MRI gradient artifact contamination present; TPULSE markers indicate artifact regions.
- High sampling rate (5000 Hz); downsampling to 250-1000 Hz recommended.
- Task-ME and Task-MI blocks are sparsely present (subset of sessions only).
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Lioi, G., et al. (2019). Simultaneous MRI-EEG during a motor imagery neurofeedback task: an open access brain imaging dataset for multi-modal data integration. BioRxiv.`
