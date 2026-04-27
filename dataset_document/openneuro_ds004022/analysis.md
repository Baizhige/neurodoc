# Multimodal EEG and fNIRS Biosignal Acquisition during Motor Imagery Tasks in Patients with Orthopedic Impairment

**Dataset**: `openneuro_ds004022` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004022
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 21
**Channels**: 18 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants with orthopedic impairment performed four distinct motor imagery tasks (Reach, Twist, Lift, and Grasp) guided by visual cues across three experimental sessions. EEG and fNIRS were recorded simultaneously to study motor imagery neural patterns in a clinical population for BCI development. Each trial began with a rest cue (S 1) followed by a task cue (S 2-S 10), with S 7-S 10 encoding the four MI conditions.

## File Scan Result

> **Kernel SHA256**: `0481515d8b1b9689b75b54462dacee9442e905d4863dcc679ca11cf315dd7b08`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | 21 | event | raw | Trial start / baseline cue |
| `S 10` | 840 | event | raw | Motor imagery cue - task 4 (Grasp) |
| `S 2` | 840 | event | raw | Cue onset (task start) |
| `S 3` | 210 | event | raw | Rest period cue |
| `S 4` | 210 | event | raw | Rest period cue (variant) |
| `S 5` | 210 | event | raw | Feedback/response marker |
| `S 6` | 210 | event | raw | Feedback/response marker |
| `S 7` | 840 | event | raw | Motor imagery cue - task 1 (Reach) |
| `S 8` | 840 | event | raw | Motor imagery cue - task 2 (Twist) |
| `S 9` | 840 | event | raw | Motor imagery cue - task 3 (Lift) |
| `boundary` | 21 | event | raw | Data discontinuity marker |
| `condition 12` | 21 | admin | raw | Condition block marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary Health Classification (Healthy vs Orthopedic Impairment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.0 *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy` | 0 | Healthy control EEG segment |
  | `orthopedic` | 1 | Orthopedic impairment EEG segment |
- **Super Meta Notes**: Labels derived from subject population metadata (healthy controls vs patients with orthopedic impairment). Binary classification target distinguishes clinical population from healthy baseline.
- **Evidence**:
  - DOI: 10.1371/journal.pone.0335364 — Explicitly cites ds004022, performs binary classification achieving 93% accuracy using Conditional VAE with nonlinear dynamics features (HE, DFA, CD, LLE, KS-proxy) from windowed EEG segments; distinguishes healthy (0) vs orthopedic impairment (1) populations
- **Kernel Notes**: Exclude `condition 12` admin block marker. Use 11 scalp channels (C3, Cz, C4, FC3, FCz, FC4, CP3, CPz, CP4, F3, F4) as specified in reference. Apply windowed feature extraction (STFT, HE, DFA, CD, KS-entropy, LLE) rather than raw epoching. Align segments to MI cue events S 7-S 10. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`S 7`, `S 8`, `S 9`, `S 10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 7` | 0 | Motor imagery - Reach |
  | `S 8` | 1 | Motor imagery - Twist |
  | `S 9` | 2 | Motor imagery - Lift |
  | `S 10` | 3 | Motor imagery - Grasp |
- **Evidence**: None — task supported by paradigm description alone (4 MI conditions encoded in S 7-S 10). Reference 10.3389/fnhum.2025.1583342 uses this dataset for denoising but does not define MI classification task. Reference 10.1371/journal.pone.0335364 performs binary health classification, not 4-class MI.
- **Kernel Notes**: Extract epochs time-locked to MI cue onsets (S 7-S 10). Exclude `condition 12` admin block marker and rest cues (S 1, S 3, S 4). Use all 18 channels including sensorimotor C3, C4, Cz for classification. Alignment assumption: S 7-S 10 markers represent MI cue onset per standard BCI paradigm convention.

### Potential Task 2: EEG Anomaly Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.512 s * (256 samples at 500 Hz), overlap = 0.2, target_events = [`S 7`, `S 8`, `S 9`, `S 10`, `S 1`, `S 3`, `S 4`, `S 2`, `S 5`, `S 6`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy segment` | 0 | Normal EEG segment without artifacts |
  | `anomalous segment` | 1 | EEG segment with artifacts or anomalies |
- **Super Meta Notes**: Derived by applying pre-trained BiLSTM classifier to all continuous EEG data; labels are model predictions distinguishing healthy from anomalous segments. Requires pre-trained model availability.
- **Evidence**: None — plausible from paradigm for artifact detection pipeline but no direct reference found.
- **Kernel Notes**: Apply sliding window segmentation across entire recording (all events are candidate boundaries). Train BiLSTM or apply pre-trained model to classify each window. Post-process overlapping predictions via majority voting.