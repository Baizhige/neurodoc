# BCI Competition IV Dataset 4 (ECoG Finger Flexion Prediction)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.pdf
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 53/67/69 (48/62/64 ECoG + 5 misc) | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

BCI Competition IV Dataset 4 is an ECoG finger flexion prediction dataset. Three epilepsy patients performed actual cued movements of individual fingers on the hand contralateral to the implanted ECoG grid; this is not a motor imagery dataset. Visual cues named one of five fingers, subjects repeatedly flexed the cued finger during a 2 s cue period, and finger positions were recorded with a data glove. The public competition release contains one MATLAB file per subject with `train_data` (400 s labeled ECoG), `train_dg` (five continuous finger-position traces for the training segment), and `test_data` (200 s ECoG with true finger-position labels withheld). Cue timing and per-cue finger labels are not present in the released `.mat` files, so `train_segment` and `test_segment_onset` are administrative markers rather than movement-class events.

## File Scan Result

> **Kernel SHA256**: `a174bec8d905e6e36fecefd78c35aa3ae9b4f31d6ceaf5e7c6d53fe2a3aaec05`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `test_segment_onset` | 3 | event | raw |  |
| `train_segment` | 3 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | complete | e.g. Synamps2 (Neuroscan) |
| `bandpass_hz` | complete | e.g. 0.15-200 |
| `cap` | complete | e.g. subdural ECoG electrode grid/array (Ad-Tech) |
| `data_glove_lag_sec` | complete | e.g. 0.037 |
| `data_glove_native_rate_hz` | complete | e.g. 25 |
| `data_glove_release_rate_hz` | complete | e.g. 1000 |
| `dataset` | complete | e.g. bcic_iv_4 |
| `device` | complete | e.g. BCI2000 acquisition with Synamps2 amplifier |
| `ecog_channel_count` | complete | e.g. 62, 48, 64 |
| `finger_label_channels` | complete | e.g. finger1,finger2,finger3,finger4,finger5 |
| `finger_label_names` | complete | e.g. thumb,index,middle,ring,little |
| `finger_label_valid_segment` | complete | e.g. train_segment |
| `handedness` | missing |  |
| `recording_type` | complete | e.g. ECoG |
| `reference` | complete | e.g. scalp reference and ground before common-average rereferencing |
| `sampling_rate_hz` | complete | e.g. 1000.0 |
| `sex` | missing |  |
| `source_file` | complete | e.g. sub1_comp.mat, sub2_comp.mat, sub3_comp.mat |
| `subject_id` | complete | e.g. sub1, sub2, sub3 |
| `test_duration_sec` | complete | e.g. 200 |
| `test_label_policy` | complete | e.g. withheld in public release; misc finger values are NaN |
| `train_duration_sec` | complete | e.g. 400 |

## Tasks

### Classical Task 1: Thumb Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.36 s, target_events = []
- **Label Route**: `misc`
- **Label Field**: `finger1`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `finger1` | continuous data-glove position (a.u.) | Thumb flexion trajectory; use finite labels from `train_segment` only. |
- **Super Meta Notes**: The kernel materializes `train_dg` column 1 as a misc channel and fills the public test segment with NaN. No movement onset detection, thresholding, or class mapping is performed.
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf - Official Dataset 4 description defines prediction of individual finger flexion from ECoG, with `train_dg` ordered thumb, index, middle, ring, little and official scoring across non-ring fingers.
- **Notes**: The 0.4 s window with 0.36 s overlap gives a 40 ms stride matching the native 25 Hz data-glove granularity while retaining short ECoG context. Finger misc channels must be excluded from the feature channel set.

### Classical Task 2: Index-Finger Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.36 s, target_events = []
- **Label Route**: `misc`
- **Label Field**: `finger2`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `finger2` | continuous data-glove position (a.u.) | Index-finger flexion trajectory; use finite labels from `train_segment` only. |
- **Super Meta Notes**: The kernel materializes `train_dg` column 2 as a misc channel and fills the public test segment with NaN. No movement onset detection, thresholding, or class mapping is performed.
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf - Official Dataset 4 description defines prediction of individual finger flexion from ECoG, with `train_dg` ordered thumb, index, middle, ring, little and official scoring across non-ring fingers.
- **Notes**: The 0.4 s window with 0.36 s overlap gives a 40 ms stride matching the native 25 Hz data-glove granularity while retaining short ECoG context. Finger misc channels must be excluded from the feature channel set.

### Classical Task 3: Middle-Finger Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.36 s, target_events = []
- **Label Route**: `misc`
- **Label Field**: `finger3`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `finger3` | continuous data-glove position (a.u.) | Middle-finger flexion trajectory; use finite labels from `train_segment` only. |
- **Super Meta Notes**: The kernel materializes `train_dg` column 3 as a misc channel and fills the public test segment with NaN. No movement onset detection, thresholding, or class mapping is performed.
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf - Official Dataset 4 description defines prediction of individual finger flexion from ECoG, with `train_dg` ordered thumb, index, middle, ring, little and official scoring across non-ring fingers.
- **Notes**: The 0.4 s window with 0.36 s overlap gives a 40 ms stride matching the native 25 Hz data-glove granularity while retaining short ECoG context. Finger misc channels must be excluded from the feature channel set.

### Classical Task 4: Little-Finger Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.36 s, target_events = []
- **Label Route**: `misc`
- **Label Field**: `finger5`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `finger5` | continuous data-glove position (a.u.) | Little-finger flexion trajectory; use finite labels from `train_segment` only. |
- **Super Meta Notes**: The kernel materializes `train_dg` column 5 as a misc channel and fills the public test segment with NaN. No movement onset detection, thresholding, or class mapping is performed.
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf - Official Dataset 4 description defines prediction of individual finger flexion from ECoG, with `train_dg` ordered thumb, index, middle, ring, little and official scoring across non-ring fingers.
- **Notes**: The 0.4 s window with 0.36 s overlap gives a 40 ms stride matching the native 25 Hz data-glove granularity while retaining short ECoG context. Finger misc channels must be excluded from the feature channel set.

### Potential Task 1: Ring-Finger Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.36 s, target_events = []
- **Label Route**: `misc`
- **Label Field**: `finger4`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | `finger4` | continuous data-glove position (a.u.) | Ring-finger flexion trajectory; use finite labels from `train_segment` only. |
- **Super Meta Notes**: The kernel materializes `train_dg` column 4 as a misc channel and fills the public test segment with NaN. No movement onset detection, thresholding, or class mapping is performed.
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf - Official Dataset 4 description states that ring-finger position is included in training data, but the ring finger is not used for official evaluation because it is correlated with middle or little finger movement.
- **Notes**: This is kept as Potential rather than Classical because the released training labels include ring-finger position, but the official competition score excludes this finger.

## Data Quality Notes

- The public `.mat` files contain no cue-onset markers and no per-cue finger-class event stream, even though the experimental protocol used visual finger cues.
- `train_segment` and `test_segment_onset` are administrative segmentation markers only; they must not be treated as motor imagery labels or movement-class labels.
- This is ECoG from subdural clinical grids, not scalp EEG. No standard 10-20 montage applies, and the official description notes that channel order was scrambled.
- Actual ECoG channel counts are sub1 = 62, sub2 = 48, sub3 = 64. With the five kernel-created finger misc channels, the MNE raws have 67, 53, and 69 channels.
- Test-segment finger labels are withheld in the public competition release; the kernel uses NaN for `finger1`-`finger5` in the 200 s test segment so supervised loaders ignore those samples.
- Data-glove measurements were sampled at 25 Hz and super-sampled to 1000 Hz in the released `train_dg`; the official description reports an approximately 37 ms glove/amplifier lag.
- Age, sex, handedness, anatomical electrode names, and subject-specific electrode locations are not available in the released files.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
