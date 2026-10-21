# BCI Competition IV Dataset 1 (Motor Imagery, Uncued Classifier Application)

**Dataset**: `bcic_iv_1` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_1.html
**Category**: Action/Output | **Subjects**: 7 | **Files (Completed)**: 14 | **Channels**: 59 | **Sampling Rate**: 1000 Hz | **Manual Review**: Zhida Shang

## Paradigm

Seven subject datasets are provided for two-class motor imagery without feedback in an asynchronous (self-paced) BCI paradigm (BCI Competition IV, 2008). The two movement classes differed per subject, selected from left hand, right hand, or foot imagery. A calibration phase used visual arrow cues with 4-second imagery intervals. The evaluation phase used acoustic cues (spoken words) with variable-duration imagery (1.5-8 s) and rest periods (1.5-8 s), simulating a realistic asynchronous BCI scenario. Both calibration and evaluation `.mat` files are provided per subject; class names are available in the `.mat` structure, whereas event positions are provided in the calibration files (`mrk.pos`) but not in the evaluation files. Later competition materials noted that three datasets (`c`, `d`, and `e`) were artificially generated.

## File Scan Result

> **Kernel SHA256**: `be708ccaca35d8c1b12185468ac158b74a29c36fa810b3dc09073853c425cde5`
> **EEGUnity Version**: `0.8.0`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `foot` | 200 | event | raw | Cue onset for foot motor imagery (subjects assigned foot class) |
| `left` | 500 | event | raw | Cue onset for left-hand motor imagery |
| `right` | 300 | event | raw | Cue onset for right-hand motor imagery (subjects assigned right class) |


> Class labels vary per subject: some subjects have `left` + `right`, others have `left` + `foot`. Event names are loaded dynamically from `nfo.className` in the `.mat` file. Counts shown are approximate per calibration file.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | BrainAmp MR plus amplifiers; Ag/AgCl electrode cap |


## Tasks

### Classical Task 1: Three-Class Motor Imagery Classification (Standard Calibration)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, target_events = [`foot`, `left`, `right`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left` | 0 | Left hand motor imagery (subject-specific class 1) |
  | `right` | 1 | Right hand motor imagery (subject-specific class 2, when paired with left) |
  | `foot` | 2 | Foot motor imagery (subject-specific class 2, when paired with left) |
- **Evidence**:
  - 10.1016/j.neuroimage.2010.03.022 — - tmin=0s tmax=4s relative to cue onset for 4-second imagery intervals during calibration
  - 10.3389/fnins.2010.00198 — - calibration phase used visual arrow cues with 4-second imagery intervals
- **Notes**: Two-class labels are subject-specific (left+right vs. left+foot); verify class names per file from `nfo.classes`. Only calibration data with fixed 4-second cue/imagery trials should be used. The primary cue-locked imagery window is 0-4 s after cue onset. A baseline-inclusive variant may use -0.5-4.0 s to include 0.5 s of pre-cue fixation baseline for offline baseline correction; this is a preprocessing/windowing variant of the same calibration task, not a separate task definition. y values encode all three possible event IDs for documentation, but actual binary classification should use the subject-specific class pair in each file.

## Data Quality Notes

- Two-class labels vary per subject (left+right vs. left+foot); verify class names per file from the `eegunity_description` field or the `.mat` `nfo.className` field.
- No age or sex information is available in the public release.
- Evaluation phase has variable trial durations and idle periods; the idle state is unlabeled and should be identified by absence of annotations.
- High sampling rate (1000 Hz); memory-intensive; downsampling recommended.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed