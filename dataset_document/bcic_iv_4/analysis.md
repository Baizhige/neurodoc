# BCI Competition IV Dataset 4 (ECoG Finger Movement Decoding)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.html
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 48-64 | **Sampling Rate**: 1000 Hz

## Paradigm

Three subjects (sub1-sub3) performed individual finger flexions under instruction while ECoG (electrocorticography) was recorded from 48-64 electrodes implanted over sensorimotor cortex (BCI Competition IV, 2008). Subjects flexed each of the five fingers individually on cue. Continuous finger flexion amplitude was measured via a data glove and stored as 5 labels per time sample. The dataset contains a training segment (~400 s per subject) with labeled finger flexion signals and a test segment (~200 s) with labels withheld. The Case B kernel concatenates train and test segments into a single continuous raw signal per subject; finger flexion signals (5 channels) are stored as `misc`-type stim channels (`finger1`-`finger5`).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `train_segment` | 1/subject | admin | raw | Annotates the entire training segment (with labeled finger flexions) |
| `test_segment_onset` | 1/subject | admin | raw | Marks the onset of the unlabeled test segment |

>
> Finger flexion labels are **not** stored as event annotations but as 5 continuous `misc` stim channels (`finger1`-`finger5`). This is a regression/continuous decoding task.


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
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Continuous Finger Flexion Trajectory Decoding (5 fingers)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.56 s (256 time points at 1000Hz), overlap = 0.99 * (1 time point sliding), target_events = see Super Meta Notes
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Finger | y | Meaning |
  |--------|---|---------|
  | finger1 (thumb) | continuous 0-1 | Flexion amplitude trajectory |
  | finger2 (index) | continuous 0-1 | Flexion amplitude trajectory |
  | finger3 (middle) | continuous 0-1 | Flexion amplitude trajectory |
  | finger4 (ring) | continuous 0-1 | Flexion amplitude trajectory |
  | finger5 (little) | continuous 0-1 | Flexion amplitude trajectory |
- **Super Meta Notes**: Derived from raw misc channels `finger1`-`finger5` stored in dataset (originally sampled at 25Hz via data glove, upsampled to 1000Hz). Kernel must extract the 5 finger channel values at each time point as regression targets. Ring finger (finger4) was excluded from official competition evaluation.
- **Evidence**:
  - DOI: 10.1109/ieeeconf58974.2023.10405112 — "FingerFlex, a convolutional encoder-decoder for finger movement regression on BCI Competition IV dataset 4, achieving correlation coefficients up to 0.74"
  - DOI: 10.1109/tim.2025.3644562 — "DeepFingerNet for decoding continuous finger trajectories from ECoG signals, achieving an average correlation coefficient of 0.69 on this dataset"
- **Kernel Notes**: Extract sliding windows of 256 samples (2.56s) with 1-sample overlap. For each window, extract the 5 finger channel values from the misc channels (`finger1`-`finger5`) as multi-output regression targets. Exclude finger channels from EEG feature matrix. Evaluate using Pearson correlation coefficient between predicted and actual finger trajectories.

### Classical Task 2: Binary Left vs Right Hand Finger Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`train_segment`, `test_segment_onset`] (derived movement events)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | left_hand_movement | 0 | Any finger flexion by left hand |
  | right_hand_movement | 1 | Any finger flexion by right hand |
- **Super Meta Notes**: Derived from raw finger flexion amplitude channels (`finger1`-`finger5` misc channels) by thresholding: if majority of fingers on left hand side exceed amplitude threshold (>0.1 *) → left_hand_movement; similarly for right hand. Kernel must compute movement events from continuous finger data before epoch extraction.
- **Evidence**:
  - DOI: 10.1109/i2ct61223.2024.10543868 — "classify finger flexion movements into five classes, achieving 80% accuracy with Random Forest classifier on binary left-hand vs right-hand classification"
- **Kernel Notes**: Step 1: Apply bandpass filter (0.15-200Hz) to ECoG. Step 2: Threshold the finger amplitude channels to detect movement onset/offset. Step 3: Classify as left vs right based on which hand's fingers are moving. Step 4: Extract epochs locked to detected movement onsets using epoch_by_event_hdf5. Verify event ID mapping from events.tsv.

### Potential Task 1: Finger Flexion Decoding - Training Segment (epoch_by_long_event)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = duration of `train_segment`, overlap = 0.5 s (sliding window), target_events = [`train_segment`]
- **Label Route**: `misc`
- **Target Definition**: N/A (target labels are continuous; see notes below)
- **Notes**: This is a **regression task**, not a standard classification task. The `train_segment` annotation spans the entire training portion (~400 s); use `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5` to extract fixed-length windows. Within each epoch, extract the corresponding `finger1`-`finger5` misc-channel values as regression targets. The `test_segment_onset` annotation marks where labels become unavailable. Finger channels must be **excluded** from the EEG feature matrix but retained as label sources. (replaces Potential Task 1 from original analysis.md)

### Potential Task 2: Active vs. Rest Finger Movement Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: Requires custom thresholding of finger channel amplitudes to define discrete movement epochs; not directly supported by standard `epoch_by_event_hdf5`.
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `misc`
- **Target Definition**: Needs verification.
- **Notes**: Threshold the `finger1`-`finger5` misc channels to identify movement onset events, then apply `epoch_by_event_hdf5`. Active finger movement (amplitude > threshold) vs. rest (amplitude <= threshold) yields a binary classification problem per finger.

## Data Quality Notes

- ECoG data, not scalp EEG: electrode locations are patient-specific implants over sensorimotor cortex; no standard montage applies.
- Channel count varies per subject: sub1 = 62, sub2 = 64, sub3 = 48 ECoG channels.
- Each file additionally contains 5 `misc` channels (`finger1`-`finger5`) storing continuous flexion amplitudes; **exclude these from EEG analysis but use them as regression labels**.
- No age or sex information available.
- High sampling rate (1000 Hz); consider downsampling to <=250 Hz for classification tasks.
- Test-segment labels are withheld; only the `train_segment` portion is usable for supervised learning.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update