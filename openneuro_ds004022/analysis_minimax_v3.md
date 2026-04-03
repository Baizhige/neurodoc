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
> **Status**: wait_manual_review
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

### Primary Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 7` | 0 | Motor imagery - Reach |
  | `S 8` | 1 | Motor imagery - Twist |
  | `S 9` | 2 | Motor imagery - Lift |
  | `S 10` | 3 | Motor imagery - Grasp |
- **Evidence**:
  - DOI: 10.1371/journal.pone.0335364 — Uses OpenNeuro ds004022 with four MI classes (Reach, Twist, Lift, Grasp) from event markers S 7-S 10 for motor imagery classification
  - DOI: 10.3389/fnhum.2025.1583342 — Uses event markers S 8 and S 10 for motor imagery data selection in EEG denoising experiments
- **Kernel Notes**: Extract epochs time-locked to MI cue onsets (S 7-S 10). Exclude `condition 12` admin block marker and rest cues (S 1, S 3, S 4). Use all 18 channels including sensorimotor C3, C4, Cz for classification. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: EEG Anomaly Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.512 s * (256 samples at 500 Hz), overlap = 0.2, target_events = [`S 7`, `S 8`, `S 9`, `S 10`, `S 1`, `S 3`, `S 4`, `S 2`, `S 5`, `S 6`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy segment` | 0 | Normal EEG segment without artifacts |
  | `anomalous segment` | 1 | EEG segment with artifacts or anomalies |
- **Super Meta Notes**: Derived by applying pre-trained BiLSTM classifier to all continuous EEG data; labels are model predictions (88% accuracy) distinguishing healthy from anomalous segments. Kernel step: Segment continuous EEG into sliding windows, run BiLSTM inference to produce binary health label per segment.
- **Evidence**:
  - DOI: 10.1016/j.bspc.2025.108597 — Uses openneuro_ds004022 dataset for anomaly detection, segmenting EEG into 256-point windows and labeling each as healthy (0) or anomalous (1) using BiLSTM
- **Kernel Notes**: Apply sliding window segmentation across entire recording (all events are candidate boundaries). Train BiLSTM or apply pre-trained model to classify each window. Post-process overlapping predictions via majority voting.

### Primary Task 3: Binary Health Classification (Healthy vs Orthopedic Impairment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.0 *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy` | 0 | Subject from healthy control cohort |
  | `orthopedic impairment` | 1 | Subject with orthopedic impairment (from ds004022) |
- **Super Meta Notes**: Derived from subject group membership. Motor imagery task identity (S 7-S 10) is used only for extracting MI segments but not as classification target. Kernel step: Combine this dataset (orthopedic=1) with healthy MI dataset, extract 1-s windows from MI intervals, train classifier to predict health status.
- **Evidence**:
  - DOI: 10.1371/journal.pone.0335364 — Uses OpenNeuro ds004022 (orthopedic-impairment dataset) combined with healthy MI dataset to train Conditional VAE for binary classification of health status using 1-s EEG windows
- **Kernel Notes**: Requires merging with external healthy cohort dataset. Extract 1-s non-overlapping windows from MI intervals only (S 7-S 10), exclude rest/baseline periods. Apply bandpass 8-50 Hz filtering. Use per-recording z-scoring for normalization.

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

