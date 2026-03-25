# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21
**Channels**: 18 | **Sampling Rate**: 500 Hz

## Paradigm

Participants with orthopedic impairment performed four distinct motor imagery tasks (Reach, Twist, Lift, and Grasp) guided by visual cues across three experimental sessions. EEG and fNIRS were recorded simultaneously to study motor imagery neural patterns in a clinical population for BCI development. Each trial began with a rest cue (S 1) followed by a task cue (S 2-S 10), with S 7-S 10 encoding the four MI conditions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004022

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 2` | 21 files | short | raw | Cue onset (task start) |
| `S 7` | 21 files | short | raw | Motor imagery cue - task 1 (Reach) |
| `S 8` | 21 files | short | raw | Motor imagery cue - task 2 (Twist) |
| `S 9` | 21 files | short | raw | Motor imagery cue - task 3 (Lift) |
| `S 10` | 21 files | short | raw | Motor imagery cue - task 4 (Grasp) |
| `S 3` | 21 files | short | raw | Rest period cue |
| `S 4` | 21 files | short | raw | Rest period cue (variant) |
| `S 5` | 21 files | short | raw | Feedback/response marker |
| `S 6` | 21 files | short | raw | Feedback/response marker |
| `S 1` | 21 files | short | raw | Trial start / baseline cue |
| `condition 12` | 21 files | admin | raw | Condition block marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 2`, `S 7`, `S 8`, `S 9`, `S 10`, `S 3`, `S 4`, `S 5`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Binary Anomaly Detection (Healthy vs Anomalous EEG Segments)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 256 time points (0.512 s at 500 Hz *), overlap = 0.2 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy segment` | 0 | Normal EEG segment without anomalies |
  | `anomalous segment` | 1 | Unhealthy/anomalous EEG segment |
- **Super Meta Notes**: Labels derived using a pre-trained BiLSTM classifier (88% accuracy) that distinguishes healthy from unhealthy EEG segments; validated with manual spot checks (10% subset) and majority voting for overlapping segments.
- **Evidence**:
  - DOI: 10.1016/j.bspc.2025.108597 — Uses openneuro_ds004022 (referred to as 'Unhealthy Dataset') consisting of 18-channel EEG recordings from seven participants with orthopedic impairments during motor imagery sessions, and performs anomaly detection by segmenting EEG data into 256-point windows and labeling each segment as healthy (0) or anomalous (1) using a BiLSTM classifier
- **Kernel Notes**: Apply sliding window segmentation to raw EEG; derive anomaly labels from pre-trained BiLSTM; majority vote for overlapping segments.

### Primary Task 2: Binary Health Classification (Healthy vs Orthopedic Impairment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s (125 samples at 125 Hz resampled *), overlap = 0.0 *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy` | 0 | Healthy subject motor imagery EEG |
  | `orthopedic impairment` | 1 | Patient with orthopedic impairment motor imagery EEG |
- **Super Meta Notes**: Binary health condition label (healthy vs orthopedic impairment) is derived from subject group membership; motor imagery task identity (S 7-S 10) is used only for extracting MI segments but not as classification target.
- **Evidence**:
  - DOI: 10.1371/journal.pone.0335364 — Uses OpenNeuro ds004022 (orthopedic-impairment dataset) combined with a healthy MI dataset to train a Conditional VAE for binary classification of health status (healthy vs orthopedic impairment) using 1-s EEG windows extracted from motor imagery intervals
- **Kernel Notes**: Extract 1-s windows only from MI intervals (S 7-S 10); combine with healthy control data; train Conditional VAE for binary health classification.

### Primary Task 3: EEG Signal Denoising
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = Needs verification *, overlap = 0.0 *, target_events = [`S 1`, `S 4`, `S 8`, `S 10`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**: Continuous EEG reconstruction — no discrete labels; denoising model learns mapping from noisy to clean EEG.
- **Super Meta Notes**: Clean EEG references were created by identifying low-artifact segments based on amplitude thresholds and visual inspection, with synthetic noise injection where necessary — this is a derived/constructed reference for training the denoising models.
- **Evidence**:
  - DOI: 10.3389/fnhum.2025.1583342 — Uses the openneuro_ds004022 dataset (described as 'unhealthy' 18-channel EEG from 7 participants with orthopedic impairments during motor-imagery tasks) to train and evaluate GAN and WGAN-GP models for EEG signal denoising, applying bandpass filtering (8-30 Hz) and using specific event markers (S 1, S 4, S 8, S 10) for data selection
- **Kernel Notes**: Apply bandpass filter 8-30 Hz; focus on sensorimotor channels C3, C4, Cz; extract segments using specified event markers; train GAN/WGAN-GP for EEG denoising.

### Normal Task 1: Four-Class Motor Imagery (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 7 subjects; small sample size limits generalization. `condition 12` is an admin/block marker to exclude. 3 sessions per subject (21 files total). Each session has 40 trials per MI class.

| Event | y | Meaning |
 |-------|---|------|
 | `S 7` | 0 | Motor imagery - Reach |
 | `S 8` | 1 | Motor imagery - Twist |
 | `S 9` | 2 | Motor imagery - Lift |
 | `S 10` | 3 | Motor imagery - Grasp |

## Data Quality Notes

- Only 7 subjects with orthopedic impairment - very small clinical sample
- 18-channel EEG with motor cortex coverage; suitable for BCI but limited spatial resolution
- `condition 12` is a block marker to exclude from epoching

## References

- **Reference**: `Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment`
