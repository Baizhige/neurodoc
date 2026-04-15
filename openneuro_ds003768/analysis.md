# Simultaneous EEG and fMRI Signals During Sleep from Humans

**Dataset**: `openneuro_ds003768` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds003768
**Category**: Biological State | **Subjects**: 33 | **Files (Completed)**: 254 | **Channels**: 32 | **Sampling Rate**: 5000 Hz
**Manual Review**: Pending

## Paradigm

Simultaneous EEG-fMRI recordings were acquired during resting-state wakefulness and multiple sleep sessions (NREM, REM) to analyze spontaneous brain activity and sleep stage dynamics. Participants underwent extended sleep sessions in an MRI scanner while 32-channel MR-compatible EEG was recorded concurrently with fMRI. BrainVision numeric stimulus codes (S1, S2, S3) and response codes (R128) mark sleep stage transitions or scoring events annotated by a Registered Polysomnographic Technologist (RPT). The dataset supports multimodal sleep neuroscience research.

## File Scan Result

> **Kernel SHA256**: `4c62d576cc9d09d80f102d36b7c8a924ed9e16f4eb3686c4d3b2652de816cbed`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 2 | event | raw | System marker for recording segment boundary |
| `Response/R128` | 98870 | admin | raw | BrainVision response trigger (scoring event marker) |
| `Stimulus/S  1` | 31977 | event | raw | BrainVision S1 trigger (sleep stage marker: Wake/N1) |
| `Stimulus/S  2` | 32062 | event | raw | BrainVision S2 trigger (sleep stage marker: N2) |
| `Stimulus/S  3` | 183 | event | raw | BrainVision S3 trigger (sleep stage marker: N3) |
| `SyncStatus/Sync Off` | 4373 | event | raw | fMRI sync pulse off marker |
| `SyncStatus/Sync On` | 104952 | event | raw | fMRI sync pulse on marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep stage classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 0 | Wake (W) |
  | `Stimulus/S  1` | 1 | NREM1 (N1) |
  | `Stimulus/S  2` | 2 | NREM2 (N2) |
  | `Stimulus/S  3` | 3 | NREM3 (N3) |
- **Super Meta Notes**: Derived from raw events [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`] by mapping BrainVision triggers to AASM sleep stage labels. Sleep stages are manually annotated by a Registered Polysomnographic Technologist (RPT) based on AASM guidelines, stored in sourcedata folder as w=wake, 1=NREM1, 2=NREM2, 3=NREM3. Kernel step: Extract 30-sec EEG epochs aligned to S1/S2/S3 trigger onset, then map each epoch to corresponding sleep stage label from sourcedata annotations.
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.109059 — Data descriptor paper documenting simultaneous EEG-fMRI sleep dataset with 33 participants, 32-channel MR-compatible EEG, manually scored 4-class sleep stages (W, N1, N2, N3) by RPT on 30-sec AASM-standard epochs
  - DOI: 10.1016/j.neuroimage.2022.119720 — Uses same OpenNeuro ds003768 dataset (version 1.0.9) analyzing 27 subjects with simultaneous EEG, fMRI, and autonomic recordings during resting-state and sleep transitions
- **Kernel Notes**: Use 30-sec long-event epoching aligned with AASM standard sleep scoring. Downsample from 5000 Hz to 250 Hz to reduce computation. Apply gradient artifact removal for EEG-fMRI data (e.g., gradient interpolation). Verify event-to-sleep-stage mapping from sourcedata/events.tsv. Class imbalance expected (N3 rare). Consider subject-level cross-validation. Note: REM epochs not available in this dataset (no REM triggers in event structure).

### Classical Task 2: Arousal state binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 20.0 s, overlap = 0.5, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 0 | Awake (W) |
  | `Stimulus/S  1` | 1 | Sleep (N1) |
  | `Stimulus/S  2` | 1 | Sleep (N2) |
  | `Stimulus/S  3` | 1 | Sleep (N3) |
- **Super Meta Notes**: Derived from raw events [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]. Binarizes sleep stage labels: W/N1 from S1 triggers → awake (0); N1/N2/N3 from S1/S2/S3 → sleep (1). Kernel step: Extract 20-sec EEG epochs aligned to S1/S2/S3 onset, then binarize labels (W=awake, N1/N2/N3=sleep).
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.109059 — Documents dataset with scored wake and sleep epochs enabling binary wake vs sleep classification
  - DOI: 10.1016/j.neuroimage.2022.119720 — Uses same dataset for arousal state analysis during resting-state and sleep transitions; analyzes transient arousal dynamics with EEG-fMRI
- **Kernel Notes**: Use 20-sec epochs with 50% overlap (10-sec sliding window) for denser sampling. Downsample to 250 Hz. Apply MRI gradient artifact removal before epoching. Verify sleep/wake labeling from sourcedata. Class imbalance likely (sleep more frequent than wake in sleep session data).

### Potential Task 1: Sleep microarchitecture analysis (short-epoch ERP-like)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 0 | Sleep stage transition marker (W/N1 onset) |
  | `Stimulus/S  2` | 1 | Sleep stage transition marker (N2 onset) |
  | `Stimulus/S  3` | 2 | Sleep stage transition marker (N3 onset) |
- **Super Meta Notes**: Shorter window around S1/S2/S3 trigger events to capture transient EEG patterns within sleep stages (e.g., sleep spindles in N2, slow waves in N3). Labels derived from trigger events; exact mapping to sleep stages must be verified from sourcedata.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119720 — Analyzes transient arousal dynamics and neural events at arousal changes; suggests utility of short-epoch analysis around transition markers
- **Kernel Notes**: Apply MRI artifact removal before short-epoch extraction. Downsample to 250 Hz. Use symmetric window (tmin=-1s, tmax=2s) to capture pre-trigger baseline and post-transition activity. Verify trigger-to-stage mapping from sourcedata/events.tsv for accurate labeling.