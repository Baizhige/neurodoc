# Braille Letters EEG

**Dataset**: `openneuro_ds004951` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004951
**Category**: Sensory/Response | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants identified Braille letters presented via tactile stimulation to the left or right index fingers while EEG was recorded with a 64-channel system at 1000 Hz. The study investigates cortical plasticity by comparing sighted controls and congenitally blind individuals in Braille letter processing. Stimulus codes S10-S16 mark individual Braille letter presentations to the right hand (~3298-3301 trials each), while S1-S8 correspond to left-hand stimulation.

## File Scan Result

> **Kernel SHA256**: `2a0d33acc56d02fbe3ab1e2835ffdfa68ff4fdf0b9daddfd0ffaa442ac6bea45`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 10` | 3299 | event | raw | Letter stimulus onset for right hand (S 10) |
| `Stimulus/S 11` | 3300 | event | raw | Letter stimulus onset for right hand (S 11) |
| `Stimulus/S 12` | 3298 | event | raw | Letter stimulus onset for right hand (S 12) |
| `Stimulus/S 13` | 3298 | event | raw | Letter stimulus onset for right hand (S 13) |
| `Stimulus/S 14` | 3299 | event | raw | Letter stimulus onset for right hand (S 14) |
| `Stimulus/S 15` | 3301 | event | raw | Letter stimulus onset for right hand (S 15) |
| `Stimulus/S 16` | 3301 | event | raw | Letter stimulus onset for right hand (S 16) |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `HEOG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `HEOG` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
- **Candidate Labels**: `HEOG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: 8-class Braille letter identity (right hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [Stimulus/S 10, Stimulus/S 11, Stimulus/S 12, Stimulus/S 13, Stimulus/S 14, Stimulus/S 15, Stimulus/S 16]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 10` | 0 | Letter stimulus onset for right hand (S 10) |
  | `Stimulus/S 11` | 1 | Letter stimulus onset for right hand (S 11) |
  | `Stimulus/S 12` | 2 | Letter stimulus onset for right hand (S 12) |
  | `Stimulus/S 13` | 3 | Letter stimulus onset for right hand (S 13) |
  | `Stimulus/S 14` | 4 | Letter stimulus onset for right hand (S 14) |
  | `Stimulus/S 15` | 5 | Letter stimulus onset for right hand (S 15) |
  | `Stimulus/S 16` | 6 | Letter stimulus onset for right hand (S 16) |
- **Evidence**:
  - 10.7554/eLife.98148 — Right-hand analog of the classical left-hand task. Events S10-S16 correspond to the same 8 Braille letters (B, C, D, L, M, N, V, Z) presented to the right index finger. README confirms S9-S16 are right hand stimuli. Same trial counts (~3298-3301 each) as left hand. Enables cross-hand transfer learning analysis.
- **Notes**: Right-hand counterpart to the classical left-hand Braille letter classification task. Per README, triggers S1-S8 are left hand stimuli and S9-S16 are right hand stimuli. The 8 events S10-S16 (note: S9 appears to be unused or grouped with S10-S16 in the actual data) represent 8 distinct Braille letters presented to the right index finger, forming an 8-class classification problem analogous to the left-hand task.

### Potential Task 2: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 29–61 (years) | Participant chronological age from participants.tsv; N=11, mean ~45. Each segment inherits the subject's age as regression target. |
- **Evidence**:
- **Notes**: Archetype B3: age is a native numeric column in participants.tsv, requiring no kernel derivation. Segmentation produces fixed-length windows from continuous EEG; each segment is labeled with the corresponding subject's age. The 2s segment length and 50% overlap are standard defaults for continuous-data regression tasks when no event structure is needed.

### Potential Task 3: Sex Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Binary classification of participant sex from segmented continuous EEG. Uses 2-second non-overlapping segments (50% overlap) with subject-level labels from participants.tsv. Highly imbalanced dataset (8F/3M) but valid 2-class problem. No event structure required due to segmentation approach.

### Potential Task 4: HEOG Regression (Native Misc)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [Stimulus/S 10, Stimulus/S 11, Stimulus/S 12, Stimulus/S 13, Stimulus/S 14, Stimulus/S 15, Stimulus/S 16]`
- **Label Route**: `misc`
- **Label Field**: `HEOG`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | HEOG | continuous (µV) | Horizontal electrooculogram; native continuous misc channel recorded during Braille letter stimulus presentation |
- **Evidence**:
- **Notes**: Native HEOG channel is the only continuous non-EEG channel available in this dataset (EOGChannelCount=1, EMGChannelCount=0, MiscChannelCount=0). The task regresses HEOG amplitude from EEG channels time-locked to right-hand Braille letter stimulus onsets (S 10-S 16), capturing ocular activity/artifact during tactile letter processing. Epoch window [-0.2, 0.8] s covers pre-stimulus baseline and post-stimulus ocular response. All seven right-hand stimulus event IDs are pooled as epoch anchors since they share the same functional role (letter onset for right hand) per the README and events structure.

## Data Quality Notes

- Only right-hand stimulus events (S10-S16) are present in the scanned files; left-hand events (S1-S8) referenced in documentation are not found in this scan, suggesting either incomplete file coverage or data subset.
- Event counts show near-perfect balance across S10-S16 (~3298-3301 each), indicating well-controlled trial randomization.
- The `device` field is completely missing from metadata, limiting hardware reproducibility.
- HEOG is the only available ocular channel; no VEOG or EMG channels are present, which may limit artifact correction options.
- Task definitions assume S10-S16 map to 8 distinct Braille letters (B, C, D, L, M, N, V, Z) per README and publication, but this mapping is not directly encoded in event labels—requires external documentation for interpretability.
- Age regression task notes N=11 for age data, but dataset reports 23 subjects total; verify age availability across all participants.
- Sex classification task notes highly imbalanced distribution (8F/3M), which may affect model training and evaluation.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
