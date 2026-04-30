# OpenNeuro ds004147: EEG during reinforcement learning with varying feedback validity

**Dataset**: `openneuro_ds004147` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004147
**Category**: reinforcement learning / value-based learning | **Subjects**: 12 | **Files (Completed)**: 12 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

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
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 22–77 (years) | Continuous age from participants.tsv; N=12 subjects with 55-year span. Each segment inherits the subject's age label. |
- **Evidence**:
- **Notes**: Segmentation-based regression using subject-level demographic variable. No trial-level events are used as labels; 2-second windows with 50% overlap provide multiple samples per subject for age prediction from resting/task-continuous EEG spectral features. Epoch parameters inferred from default segmentation settings for subject-level regression tasks.

### Potential Task 2: sex classification from continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | female |
  | sex | M | 1 | male |
- **Evidence**:
  - participants.tsv — N=12, sex={'F': 7, 'M': 5}, complete categorical field
- **Notes**: Segmentation-based subject-level classification using 2-second windows with 50% overlap. Class balance is moderate (58% female). Cross-validation must be performed at the subject level to prevent data leakage, as all segments from the same participant share the same sex label. The task uses the native participants.tsv `sex` column (archetype B3), requiring no kernel derivation.

### Potential Task 3: Handedness Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | R | 0 | Right-handed |
  | handedness | L | 1 | Left-handed |
- **Evidence**:
  - participants.tsv — handedness column with values {R, L}; 11 right-handed, 1 left-handed participant (N=12 total)
- **Notes**: Severe class imbalance (92% right-handed, only 1 left-handed participant) makes this task statistically challenging for any classifier. Included for completeness as a grounded participants.tsv variable. Segmentation creates 2-second non-overlapping windows from continuous resting/task EEG; all segments from a given participant share the same handedness label. The epoch parameters use defaults since no specific timing information is available for this info-route segmentation task.

### Potential Task 4: Task Order Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `order`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | order | 50-50 mixed 80-20 | 0 | Low-value task first, then mid-value, then high-value |
  | order | 80-20 mixed 50-50 | 1 | High-value task first, then mid-value, then low-value |
  | order | 80-20 50-50 mixed | 2 | High-value task first, then low-value, then mid-value |
  | order | mixed 80-20 50-50 | 3 | Mid-value task first, then high-value, then low-value |
  | order | mixed 50-50 80-20 | 4 | Mid-value task first, then low-value, then high-value |
  | order | 50-50 80-20 mixed | 5 | Low-value task first, then high-value, then mid-value |
- **Evidence**:
  - participants.tsv — `order` column contains 6 unique task order strings defining the sequence of low-value (50-50), mid-value (mixed), and high-value (80-20) task blocks across participants
- **Notes**: Segmentation-based approach with 2-second non-overlapping windows (50% overlap) treats the continuous resting/task-ongoing EEG as input. The `order` field is a native participants.tsv column (archetype B3, Meta Level = raw). N=12 with 6 classes yields only 2 participants per class, making this severely underpowered for meaningful classification. Included for completeness as a potential task but noted as extremely challenging due to sample size limitations. The 6 order strings encode all permutations of the three task types (low-value=50-50, mid-value=mixed, high-value=80-20).

### Potential Task 5: Stimulus Pair Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `stimuli`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | stimuli | `a lemon an orange` | 0 | lemon-orange pair |
  | stimuli | `a cherry an orange` | 1 | cherry-orange pair |
  | stimuli | `a cherry a lemon` | 2 | cherry-lemon pair |
- **Evidence**:
- **Notes**: Participants were assigned one of three stimulus pairs (colored shape cues: lemon, orange, cherry) as a between-subjects factor. The `stimuli` column in participants.tsv records which pair each participant learned. Segmentation creates non-overlapping 2-second windows from continuous EEG; each window inherits the participant's stimulus pair label. This tests whether stimulus-specific learning history is encoded in resting/task-continuous EEG features. Note: One additional value `an orange a lemon` appears in participants.tsv (sub-30) but represents the same unordered pair as `a lemon an orange`; in practice the kernel should canonicalize or this row maps to y=0.

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
