# BCI Competition IV Dataset 4 (ECoG Finger Flexion Prediction)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.pdf
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 53/67/69 (48/62/64 ECoG + 5 misc) | **Sampling Rate**: 1000 Hz | **Manual Review**: anonymous for review

## Paradigm

BCI Competition IV Dataset 4 is an ECoG finger flexion prediction dataset, not a motor imagery dataset. Three epilepsy patients performed actual visually cued finger movements with ECoG recorded from 48-64 subdural electrodes over sensorimotor cortex. Visual cues named one of five fingers, and subjects repeatedly flexed the cued finger during a 2 s cue period while finger-position amplitudes were recorded with a data glove as five continuous target signals. The public release contains one MATLAB file per subject with `train_data` containing 400 s of labeled ECoG, `train_dg` containing the five training finger-position traces, and `test_data` containing 200 s of ECoG with labels withheld. Cue timing and per-cue labels are not included, so `train_segment` and `test_segment_onset` are administrative markers rather than movement-class events.

## File Scan Result

> **Kernel SHA256**: `a70a20c716fdf52ce64804f37490c4b4369921ba52a7542cb2c262c233299254`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `test_segment_onset` | 3 | event | raw | Onset of the 200 s public test segment; finger-position labels are withheld in the release, so `finger1`-`finger5` are NaN in this segment. |
| `train_segment` | 3 | event | raw | Start of the 400 s labeled training segment containing valid continuous finger-position traces in `finger1`-`finger5`. |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `finger1` | native (raw misc in EEG file) | raw | Continuous thumb flexion trace from `train_dg` column 1; valid in `train_segment`, NaN in the public test segment. |
| `finger2` | native (raw misc in EEG file) | raw | Continuous index-finger flexion trace from `train_dg` column 2; valid in `train_segment`, NaN in the public test segment. |
| `finger3` | native (raw misc in EEG file) | raw | Continuous middle-finger flexion trace from `train_dg` column 3; valid in `train_segment`, NaN in the public test segment. |
| `finger4` | native (raw misc in EEG file) | raw | Continuous ring-finger flexion trace from `train_dg` column 4; valid in `train_segment`, NaN in the public test segment. |
| `finger5` | native (raw misc in EEG file) | raw | Continuous little-finger flexion trace from `train_dg` column 5; valid in `train_segment`, NaN in the public test segment. |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Not provided in the public competition release. |
| `amplifier` | complete | Acquisition amplifier reported by the official dataset description. |
| `bandpass_hz` | complete | Acquisition band-pass range reported in the competition description. |
| `cap` | complete | Subdural clinical ECoG grid/array rather than a scalp EEG cap. |
| `data_glove_lag_sec` | complete | Approximate glove-to-amplifier lag reported by the official description. |
| `data_glove_native_rate_hz` | complete | Native sampling rate of the original finger-position glove measurements. |
| `data_glove_release_rate_hz` | complete | Sampling rate of the released ECoG and supersampled glove traces. |
| `dataset` | complete | Dataset identifier written by the kernel. |
| `device` | complete | Acquisition stack summarized from the public competition description. |
| `ecog_channel_count` | complete | Number of neural ECoG channels before the five finger misc channels are appended. |
| `finger_label_channels` | complete | Names of the five continuous glove-label channels materialized by the kernel. |
| `finger_label_names` | complete | Finger-name order corresponding to `finger1` through `finger5`. |
| `finger_label_valid_segment` | complete | Segment in which the glove labels are valid and non-NaN. |
| `handedness` | missing | Not provided in the public competition release. |
| `recording_type` | complete | Invasive ECoG recording, not scalp EEG. |
| `reference` | complete | Reference/ground scheme described for the original acquisition before rereferencing. |
| `sampling_rate_hz` | complete | Final sample rate of the released ECoG recordings. |
| `sex` | missing | Not provided in the public competition release. |
| `source_file` | complete | Original public MATLAB container file for the subject. |
| `subject_id` | complete | Subject identifier inferred from the MATLAB filename. |
| `test_duration_sec` | complete | Duration of the unlabeled public test segment. |
| `test_label_policy` | complete | Explains why the finger misc channels are NaN during the public test segment. |
| `train_duration_sec` | complete | Duration of the labeled training segment. |


## Tasks

### Classical Task 1: Continuous Finger Flexion Regression — Thumb
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger1` | continuous thumb flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger1` corresponds to the thumb trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; thumb prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a thumb-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger1` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 2: Continuous Finger Flexion Regression — Index Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger2` | continuous index-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger2` corresponds to the index-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; index-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as an index-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger2` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 3: Continuous Finger Flexion Regression — Middle Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger3` | continuous middle-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger3` corresponds to the middle-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; middle-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a middle-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger3` data-glove trace over the labeled 400 s `train_segment`.

### Classical Task 4: Continuous Finger Flexion Regression — Ring Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger4` | continuous ring-finger flexion trace (a.u.; present in labels/submission format, excluded from official final scoring) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger4` corresponds to the ring-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation page notes that the ring finger was excluded from the final averaged score, although the trace remains part of the five-column data-glove target format.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. The ring-finger trace exists in the released label structure and prediction format, but it was excluded from the official final average score. It should not be treated as a ring-vs-other-fingers classification task.

### Classical Task 5: Continuous Finger Flexion Regression — Little Finger
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 400 s, overlap = 0, target_events = []
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `finger5` | continuous little-finger flexion trace (a.u.) |
- **Evidence**:
  - https://www.bbci.de/competition/iv/desc_4.pdf — The official competition description defines Dataset 4 as an ECoG finger flexion prediction task. The training labels are provided as `train_dg`, ordered as thumb, index, middle, ring, and little finger; `finger5` corresponds to the little-finger trace.
  - https://www.bbci.de/competition/iv/results/index.html — The official evaluation uses correlations between predicted and true finger-flexion traces; little-finger prediction is one of the scored finger traces.
- **Notes**: This is a schema-compatible single-target projection of the original five-output continuous regression benchmark. It should not be treated as a little-finger-vs-other-fingers classification task. The public files do not provide cue-onset markers or per-cue finger class labels, so the valid formulation is continuous regression from ECoG to the `finger5` data-glove trace over the labeled 400 s `train_segment`.

## Data Quality Notes

- The public competition `.mat` files contain no cue-onset markers and no per-cue finger-class event stream, even though the experimental protocol used visual finger cues.
- `train_segment` and `test_segment_onset` are administrative segmentation markers only; they must not be treated as motor imagery labels or movement-class labels.
- This is ECoG from subdural clinical grids, not scalp EEG. No standard 10-20 montage applies, and the official description notes that channel order was scrambled.
- Actual ECoG channel counts are sub1 = 62, sub2 = 48, sub3 = 64. With the five kernel-created finger misc channels, the MNE raws have 67, 53, and 69 channels.
- Test-segment finger labels are withheld in the original public `.mat` competition release; the kernel uses NaN for `finger1`-`finger5` in the 200 s test segment so supervised loaders ignore those samples. Official true labels were later made available on the competition results page for offline evaluation.
- Data-glove measurements were sampled at 25 Hz and super-sampled to 1000 Hz in the released `train_dg`; the official description reports an approximately 37 ms glove/amplifier lag.
- The five target traces are thumb, index, middle, ring, and little finger flexion. The ring finger trace is present in the data and prediction format, but was excluded from the official final average score.
- Age, sex, handedness, anatomical electrode names, and subject-specific electrode locations are not available in the released files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed