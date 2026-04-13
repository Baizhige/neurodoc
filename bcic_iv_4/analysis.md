# BCI Competition IV Dataset 4 (ECoG Finger Movement Decoding)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.pdf
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 48-64 | **Sampling Rate**: 1000 Hz
**Manual Review**: Zhida Shang

## Paradigm

Three subjects (sub1-sub3) performed visually cued individual finger flexions while ECoG (electrocorticography) was recorded from 48-64 subdural electrodes implanted over sensorimotor cortex (BCI Competition IV, 2008). Subjects flexed each of the five fingers individually in response to visual cues; each cue lasted 2 s and was followed by 2 s of rest, with each finger presented 30 times for a total of 150 cue presentations in a 10-minute experiment. Continuous finger flexion amplitude was measured via a data glove and provided as 5 continuous target signals. For each subject, the dataset contains one `.mat` file with a training segment (400,000 samples, 6 min 40 s) including labeled finger flexion signals (`train data`, `train dg`) and a test segment (200,000 samples, 3 min 20 s) with ECoG only (`test data`). In the kernel, these segments may be concatenated into a single continuous raw signal per subject, while finger flexion signals can be stored as `misc`-type channels (`finger1`-`finger5`) for downstream regression tasks.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `train_segment` | 1/subject | admin | raw | Annotates the entire training segment (with labeled finger flexions) |
| `test_segment_onset` | 1/subject | admin | raw | Marks the onset of the unlabeled test segment |


> Finger flexion labels are not stored as event annotations in the original dataset; instead, they are provided as 5 continuous target signals in `train dg`, which may be mapped to `misc` channels (`finger1`-`finger5`) in the kernel. This is a regression/continuous decoding task.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | Synamps2 amplifiers (Neuroscan); subdural electrode arrays (Ad-Tech); data glove (Fifth Dimension Technologies) |


## Tasks

### Classical Task 1: Continuous Finger Flexion Trajectory Decoding (5 fingers)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.56 s, overlap = 0.99
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: ``````````
- **Evidence**:
  - DOI: 10.1109/ieeeconf58974.2023.10405112 — "FingerFlex, a convolutional encoder-decoder for finger movement regression on BCI Competition IV dataset 4, achieving correlation coefficients up to 0.74"
  - DOI: 10.1109/tim.2025.3644562 — "DeepFingerNet for decoding continuous finger trajectories from ECoG signals, achieving an average correlation coefficient of 0.69 on this dataset"
- **Kernel Notes**: 

### Classical Task 2: Binary Left vs Right Hand Finger Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: , target_events = [`left_hand_movement`, `right_hand_movement`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_hand_movement` | 0 | Any finger flexion by left hand |
  | `right_hand_movement` | 1 | Any finger flexion by right hand |
- **Evidence**:
  - DOI: 10.1109/i2ct61223.2024.10543868 — "classify finger flexion movements into five classes, achieving 80% accuracy with Random Forest classifier on binary left-hand vs right-hand classification"
- **Kernel Notes**: Epoch parameters were not specified in the referenced literature.

### Potential Task 1: Active vs. Rest Finger Movement Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `Needs verification.`
- **Evidence**:
  - DOI: DOI: **Kernel Notes**: — —
- **Kernel Notes**: 

## Data Quality Notes

- ECoG data, not scalp EEG: electrode locations are patient-specific implants over sensorimotor cortex; no standard montage applies.
- Channel count varies per subject: sub1 = 62, sub2 = 48, sub3 = 64 ECoG channels.
- Each file additionally contains 5 `misc` channels (`finger1`-`finger5`) storing continuous flexion amplitudes; **exclude these from EEG analysis but use them as regression labels**.
- No age or sex information available.
- High sampling rate (1000 Hz); consider downsampling to <=250 Hz for classification tasks.
- Test-segment labels are withheld; only the `train_segment` portion is usable for supervised learning.
- Channel order has been scrambled.
- Dataglove labels were sampled at 25 Hz and super-sampled to 1000 Hz; glove-amplifier lag is 37 ± 3 ms.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
