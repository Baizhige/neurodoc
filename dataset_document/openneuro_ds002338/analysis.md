# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP2

**Dataset**: `openneuro_ds002338` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002338
**Category**: Action/Output | **Subjects**: 16 | **Files (Completed)**: 169 | **Channels**: 64 | **Sampling Rate**: 5000 Hz
**Manual Review**:

## Paradigm

Participants performed right-hand motor imagery and received neurofeedback (1D or 2D display) during simultaneous EEG-fMRI acquisition to learn to regulate sensorimotor rhythms. The task alternated between sustained Rest blocks and Task-NF (neurofeedback) blocks. MRI gradient artifacts are marked with TPULSE markers which must be excluded. This is XP2 of a two-experiment series; XP1 is ds002336.

## File Scan Result

> **Kernel SHA256**: `9a33afc47239ec72b6382c77e48fbbc8c664d269c06412de29f38d14bcf4030e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 1354 | event | raw | Trial phase onset: rest |
| `Task-NF` | 1350 | event | raw | Trial phase onset: neurofeedback task |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ECG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `ECG` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
- **Candidate Labels**: `ECG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Rest vs Motor Imagery Neurofeedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Rest`, `Task-NF`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Rest | 0 | Trial phase onset: rest |
  | Task-NF | 1 | Trial phase onset: neurofeedback task |
- **Evidence**:
  - https://doi.org/10.1101/862375 — Rest vs Task-NF 20-second sustained blocks for motor imagery neurofeedback
  - 10.1038/s41597-020-0498-3 — Confirmed 20-second block paradigm with alternating rest and neurofeedback task phases
  - 10.1101/397729 — Original XP2 dataset description with Rest and Task-NF trial phases
- **Notes**: This is a trial phase classification task (rest vs task state), not a motor imagery class discrimination task. The event meanings explicitly describe trial phase onsets, not MI classes. The 20-second epoch duration captures the full sustained neurofeedback block as validated by all references.

### Classical Task 2: Rest vs Task-NF with Feedback-Type Stratification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Rest`, `Task-NF`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Rest | 0 | Trial phase onset: rest |
  | Task-NF | 1 | Trial phase onset: neurofeedback task |
- **Evidence**:
  - https://doi.org/10.1101/862375 — Simultaneous MRI-EEG during motor imagery neurofeedback; describes 20-second alternating Rest/Task-NF block design
  - 10.1038/s41597-020-0498-3 — Scientific Data publication confirming XP2 dataset with 1D/2D feedback groups and sustained 20s neurofeedback blocks
- **Notes**: Binary classification of sustained brain state (rest vs. active neurofeedback task). The feedback_type stratification (1d vs 2d) is a secondary experimental manipulation within the same core paradigm. Event markers are trial phase onsets, not MI class labels, which is appropriate for this state-detection task.

### Potential Task 1: 1D vs 2D Feedback Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0, target_events = [`Task-NF`]
- **Label Route**: `info`
- **Label Field**: `feedback_type`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | feedback_type | 1d | 0 | Unidimensional neurofeedback feedback |
  | feedback_type | 2d | 1 | Bidimensional neurofeedback feedback |
- **Evidence**:
  - 10.1101/397729 — Paper explicitly compares BiDim (2D) vs UniDim (1D) feedback groups; participants.tsv contains feedback_type column with values {1d, 2d} distinguishing the two experimental groups
- **Notes**: Subject-level classification where all Task-NF epochs from a given subject share the same label based on their assigned feedback type. The epoch parameters are inferred from the block structure (20-second alternating Rest/Task-NF blocks as shown in events.tsv samples). Since feedback_type is a native participants.tsv column, Meta Level is raw.

### Potential Task 2: Neurofeedback Task-Only Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–66.0 (years) | Subject chronological age; derived from participants.tsv. Segmentation applied only within Task-NF blocks (20 s periods) to capture sustained neurofeedback brain state. |
- **Evidence**:
- **Notes**: Segmentation-based regression task using 4-second windows with 50% overlap, restricted to Task-NF periods only. The kernel must filter epochs to include only segments falling within Task-NF blocks (identified by `Task-NF` event markers with 20 s duration), excluding Rest periods. Age serves as the continuous regression target. This yields multiple samples per subject while maintaining focus on neurofeedback-related brain states.

### Potential Task 3: Full Recording Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–66.0 (years) | Participant chronological age; continuous numeric predictor of EEG spectral/temporal dynamics across rest and neurofeedback periods |
- **Evidence**:
  - Perronnet et al. (2018), Lioi et al. (2019) — Simultaneous EEG-fMRI during motor imagery neurofeedback task with 64-channel EEG acquisition; dataset includes participants.tsv with complete age records for all N=23 subjects
- **Notes**: Segmentation-based age regression across full recordings (both Rest and Task-NF periods) using sliding 4-second windows. The epoch parameters are SKILL defaults for motor imagery segmentation (4s segments, 50% overlap) and are marked as inferred. No kernel derivation is required since age is a native participants.tsv column.

### Potential Task 4: Sex Classification from Neurofeedback Blocks
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0 *, target_events = [`Task-NF`]
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — N=23 subjects with sex column: 11 F, 12 M
  - events.tsv (task-1dNF, task-2dNF) — Task-NF events mark 20-second neurofeedback blocks alternating with Rest; only Task-NF epochs used to focus on active neurofeedback state
  - Perronnet et al. 2018 (bioRxiv 397729) — simultaneous EEG-fMRI during motor imagery neurofeedback paradigm
- **Notes**: Subject-level sex label (from participants.tsv) applied to all Task-NF epochs per subject. Rest epochs excluded to focus on active neurofeedback state where sex differences in motor imagery-related EEG activity may be more pronounced. Epoch parameters inferred from dataset's block structure (20-second alternating Rest/Task-NF blocks).

### Potential Task 5: ECG Regression from Native Misc Channel
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0 *, target_events = [`Rest`, `Task-NF`]
- **Label Route**: `misc`
- **Label Field**: `ECG`
- **Meta Level**: super
- **Kernel Requirements**: `ECG` channel must be present as a native misc channel on the MNE raw object (pre-existing in BrainVision header); no derivation needed
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | ECG | continuous amplitude (mV or arbitrary units) | Native ECG channel recorded during simultaneous EEG-fMRI; contains MRI gradient artifacts during scanning periods |
- **Evidence**:
- **Notes**: Native ECG channel is available as a continuous misc channel on the raw MNE object. The kernel does not need to derive this channel; it is pre-existing in the BrainVision header data. ECG amplitude is extracted as a continuous regression target over 20-second Rest and Task-NF blocks. Caution: MRI gradient artifacts are present in the ECG signal during simultaneous fMRI acquisition.

## Data Quality Notes

- MRI gradient artifacts contaminate EEG; TPULSE markers indicate artifact windows.
- High sampling rate (5000 Hz); downsampling recommended.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
