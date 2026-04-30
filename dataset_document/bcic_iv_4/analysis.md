# BCI Competition IV Dataset 4 (ECoG Finger Movement Decoding)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.html
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 | **Channels**: 48-64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Three subjects (sub1-sub3) performed individual finger flexions under instruction while ECoG (electrocorticography) was recorded from 48-64 electrodes implanted over sensorimotor cortex (BCI Competition IV, 2008). Subjects flexed each of the five fingers individually on cue. Continuous finger flexion amplitude was measured via a data glove and stored as 5 labels per time sample. The dataset contains a training segment (~400 s per subject) with labeled finger flexion signals and a test segment (~200 s) with labels withheld. The Case B kernel concatenates train and test segments into a single continuous raw signal per subject; finger flexion signals (5 channels) are stored as `misc`-type stim channels (`finger1`-`finger5`).

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

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

### Classical Task 1: Binary Left vs Right Hand Finger Movement Classification
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
