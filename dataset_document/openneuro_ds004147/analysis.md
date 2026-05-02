# OpenNeuro ds004147: EEG during reinforcement learning with varying feedback validity

**Dataset**: `openneuro_ds004147` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004147
**Category**: High-level Mental| **Subjects**: 12 | **Files (Completed)**: 12 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A reinforcement learning task requiring participants to learn cue-response mappings for colored shapes under varying conditions of feedback validity (0.5 vs 0.8 probability). Participants learned which button press was rewarded for each cue, with the value of the correct response varying across conditions. EEG was recorded to investigate neural correlates of value-based learning and the average reward rate representation.

## File Scan Result

> **Kernel SHA256**: `2d517e6aef5ec2951e8b06c29efcb48dbe165d27c87ebc315a392515d203e068`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Active Shielding: On` | 12 | event | raw |  |
| `New Segment` | 12 | event | raw |  |
| `S  1` | 1728 | event | raw |  |
| `S  2` | 1728 | event | raw |  |
| `S  3` | 1728 | event | raw |  |
| `S  4` | 831 | event | raw |  |
| `S  5` | 787 | event | raw |  |
| `S  6` | 789 | event | raw |  |
| `S  7` | 829 | event | raw |  |
| `S 11` | 864 | event | raw |  |
| `S 12` | 864 | event | raw |  |
| `S 13` | 864 | event | raw |  |
| `S 14` | 434 | event | raw |  |
| `S 15` | 373 | event | raw |  |
| `S 16` | 422 | event | raw |  |
| `S 17` | 385 | event | raw |  |
| `S 21` | 864 | event | raw |  |
| `S 22` | 864 | event | raw |  |
| `S 23` | 864 | event | raw |  |
| `S 24` | 379 | event | raw |  |
| `S 25` | 437 | event | raw |  |
| `S 26` | 536 | event | raw |  |
| `S 27` | 280 | event | raw |  |
| `S 31` | 1728 | event | raw |  |
| `S 32` | 1728 | event | raw |  |
| `S 33` | 1728 | event | raw |  |
| `S 34` | 803 | event | raw |  |
| `S 35` | 852 | event | raw |  |
| `S 36` | 997 | event | raw |  |
| `S 37` | 658 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | 22–77 (years); N=12 subjects with 55-year span. Each segment inherits the subject's age label. |
- **Evidence**:
- **Notes**: Segmentation-based regression using subject-level demographic variable. No trial-level events are used as labels; 2-second windows with 50% overlap provide multiple samples per subject for age prediction from resting/task-continuous EEG spectral features. Epoch parameters inferred from default segmentation settings for subject-level regression tasks.

### Potential Task 2: sex classification from continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | F -> 0 (female); M -> 1 (male) |
- **Evidence**:
  - participants.tsv — N=12, sex={'F': 7, 'M': 5}, complete categorical field
- **Notes**: Segmentation-based subject-level classification using 2-second windows with 50% overlap. Class balance is moderate (58% female). Cross-validation must be performed at the subject level to prevent data leakage, as all segments from the same participant share the same sex label. The task uses the native participants.tsv `sex` column (archetype B3), requiring no kernel derivation.

## Data Quality Notes

- Only 12 subjects - very small sample; unsuitable for cross-subject generalization
- Event codes `S  1` through `S 37` have unknown meanings; mapping to conditions requires manual verification from BIDS events.tsv files or documentation
- `Active Shielding: On` and `New Segment` are system/admin markers and should be excluded from epoching
- Device information is missing from metadata
- The `stimuli` field contains one anomalous value `an orange a lemon` (sub-30) that should be canonicalized to `a lemon an orange`
- No reference papers were successfully classified for this dataset
- Event code meanings are not documented in the scan output; behavioral outcomes for reinforcement learning must be derived from events.tsv

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
