# BCI Competition IV Dataset 1 (Motor Imagery, Uncued Classifier Application)

**Dataset**: `bcic_iv_1` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_1.html
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 14 | **Channels**: 59 | **Sampling Rate**: 1000 Hz | **Manual Review**: Zhida Shang

## Paradigm

Seven subjects performed two-class motor imagery without feedback in an asynchronous (self-paced) BCI paradigm (BCI Competition IV, 2008). The two movement classes differed per subject, selected from: left hand, right hand, or foot imagery. A calibration phase used visual arrow cues with 4-second imagery intervals. The evaluation phase used acoustic cues (spoken words) with variable-duration imagery (1.5-8 s) and rest periods (1.5-8 s), simulating a realistic asynchronous BCI scenario. Both calibration and evaluation `.mat` files are provided per subject; the kernel reads class names and event positions directly from the `.mat` structure.

## File Scan Result

> **Kernel SHA256**: `be708ccaca35d8c1b12185468ac158b74a29c36fa810b3dc09073853c425cde5`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `foot` | 200 | event | raw | Cue onset for foot motor imagery (subjects assigned foot class) |
| `left` | 500 | event | raw | Cue onset for left-hand motor imagery |
| `right` | 300 | event | raw | Cue onset for right-hand motor imagery (subjects assigned right class) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Two-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left`, `right`, `foot`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left` | 0 | Left-hand motor imagery |
  | `right` or `foot` | 1 | Second motor imagery class (right-hand or foot, subject-specific) |
- **Evidence**:
  - DOI: 10.1109/tnsre.2020.3020975 — Uses BCI Competition IV Dataset 1 for two-class motor imagery classification with epochs from 2-6s time window relative to cue onset
  - DOI: 10.1109/icoras.2016.7872610 — Tests SVM, k-NN, MLP-ANN, LR classifiers on two-class motor imagery from calibration data
  - DOI: 10.1109/tnsre.2021.3071140 — Applies CTFSP algorithm to this dataset with sliding window approach [2-5]s, [2.5-5.5]s, [3-6]s
- **Kernel Notes**: Class labels are subject-specific (some subjects have left+right, others have left+foot); kernel must read class assignments from the `.mat` file `nfo.className` field. Calibration files contain cue markers with 4s imagery intervals; evaluation files have variable-length uncued periods. High sampling rate (1000 Hz); consider downsampling to ≤250 Hz for efficiency. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Two-class labels vary per subject (left+right vs. left+foot); verify class names per file from the `eegunity_description` field or the `.mat` `nfo.className` field.
- No age or sex information is available in the public release.
- Evaluation phase has variable trial durations and idle periods; the idle state is unlabeled and should be identified by absence of annotations.
- High sampling rate (1000 Hz); memory-intensive; downsampling recommended.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
