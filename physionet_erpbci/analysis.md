# ERP-Based Brain-Computer Interface Recordings

**Dataset**: `physionet_erpbci` | **Year**: 2014 | **URL**: https://physionet.org/content/erpbci/1.0.0/
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 245 | **Channels**: 70 | **Sampling Rate**: 2048 Hz
**Manual Review**: Liu Peng

## Paradigm

Participants spelled characters using a standard 6x6 matrix speller while EEG was recorded with a BioSemi ActiveTwo system (64 EEG + 2 earlobe reference + 4 EOG channels) at 2048 Hz (Citi et al., 2014, ERP-based BCI Dataset). Each row and column of the 6x6 character matrix was randomly intensified for 100 ms with a 50 ms gap (150 ms SOA). Each row/column flashed approximately 20 times per trial, and participants mentally counted target character flashes to sustain attention. The kernel processes raw row/column flash events and classifies each as `seen` (target--the row or column containing the attended character flashed) or `unseen` (non-target) for both rows and columns separately. (There is currently no relevant basis for key aspects such as kernel functions, ‘seen/unseen’ labelling, separate classification of rows and columns, and the processing of raw scintillation events.)

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `seen (row)` | varies | event | raw | Target row flash (attended character's row lit up) |
| `seen (column)` | varies | event | raw | Target column flash (attended character's column lit up) |
| `unseen (row)` | varies | event | raw | Non-target row flash |
| `unseen (column)` | varies | event | raw | Non-target column flash |


> 1. Each 6x6 speller has 6 rows + 6 columns = 12 flashes per sequence; 2 are target (1 row + 1 column), 10 are non-target.
> 2. The raw data does not contain any raw tags corresponding to the aforementioned Event IDs; these tags have been derived from the blinking annotations in the raw rows/columns and the target character annotations. The correct meta level should be ‘super meta’.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | No subject age demographic information is publicly available in this dataset. |
| `subject_sex` | missing | No subject sex demographic information is publicly available in this dataset |
| `device` | missing | Recordings collected via BioSemi ActiveTwo EEG system (2048 Hz sampling rate), with 64 EEG channels, 2 earlobe references, and 4 EOG channels; software re-referencing required for full CMRR. |


## Tasks

### Classical Task 1: P300 Target vs. Non-Target Classification in Matrix Speller
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (row)`, `seen (column)`, `unseen (row)`, `unseen (column)`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seen (row)` | 1 | Target row flash (attended character's row intensified) |
  | `seen (column)` | 1 | Target column flash (attended character's column intensified) |
  | `unseen (row)` | 0 | Non-target row flash |
  | `unseen (column)` | 0 | Non-target column flash |
- **Evidence**:
  
  - DOI: 10.13026/C2101S — Dataset page describes ERP-based BCI recordings from a P300 matrix speller paradigm where participants spell characters by focusing on target flashes; row/column intensifications can be classified as target (attended) or non-target.
- **Kernel Notes**: 

  1. Epoch Parameter Rationale: The [-0.1, 0.8] s epoch window is a standard configuration for P300 ERP analysis, with -0.1 to 0 s as baseline and 0 to 0.8 s for P300 feature extraction. This window is consistent with the dataset's 150 ms stimulus onset asynchrony (SOA), avoiding overlap with subsequent stimuli.
  2. Label Mapping Rationale: Target events (seen row/column flashes, corresponding to the attended character's row/column intensification) are mapped to y=1, and non-target events (unseen row/column flashes) to y=0, merging row and column events into a single binary class for P300 target vs non-target classification.
  3. Evidence Rationale: DOI 10.13026/C2101S is the official reference for this ERP-based BCI dataset, which directly validates this P300 target vs non-target classification task in a matrix speller paradigm.
  4. Meta Level Verification: All events are marked as `raw` as the seen/unseen labels are directly present in the dataset's native event annotations, not derived from raw recordings.
  5. Quality Control: Exclude artifact-contaminated epochs (ocular/muscular artifacts) and verify event label consistency across all 10 subjects before model training; exclude EOG channels from EEG feature extraction.
  6. Preprocessing Requirement: Follow dataset guidelines: re-reference to average of earlobe electrodes (EARL/EARR), apply bandpass filtering, and remove artifacts before epoch extraction.

### Potential Task 1: Row vs. Column P300 Speller Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (row)`, `seen (column)`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seen (row)` | 0 | Target row flash (attended character's row intensification) |
  | `seen (column)` | 1 | Target column flash (attended character's column intensification) |
- **Evidence**:

- **Kernel Notes**: 

  1. Task Rationale: Potential binary classification task to distinguish between row vs column target flashes in a P300 matrix speller, using only target (seen) row/column intensification events. No strong external evidence for this specific task, so marked as Potential.
  2. Epoch Parameter Rationale: [-0.1, 0.8] s epoch window is a standard configuration for P300 ERP analysis, with -0.1 to 0 s as baseline and 0 to 0.8 s for feature extraction, consistent with the dataset's 150 ms stimulus onset asynchrony (SOA).
  3. Label Mapping Rationale: Only target (seen) events are used for this task: seen (row) events are mapped to y=0, seen (column) events to y=1, excluding all non-target (unseen) events.
  4. Meta Level Verification: All events are marked as `raw` as the seen (row/column) labels are directly present in the dataset's native event annotations, not derived from raw recordings.
  5. Quality Control: Exclude artifact-contaminated epochs (ocular/muscular artifacts) and verify event label consistency across all 10 subjects before analysis; exclude EOG channels from EEG feature extraction.
  6. Preprocessing Requirement: Follow dataset guidelines: re-reference to average of earlobe electrodes (EARL/EARR), apply bandpass filtering, and remove artifacts before epoch extraction.

## Data Quality Notes

- Very high sampling rate (2048 Hz); consider downsampling to 256 or 512 Hz for computational efficiency.
- Class imbalance: 2 target flashes vs. 10 non-target flashes per sequence (1:5 ratio); balance with oversampling or cost-sensitive learning.
- EOG channels present (4 channels); apply artifact rejection before P300 classification.
- Age and sex information are not available.
- Dataset requires software re-referencing (e.g., average of EARL/EARR earlobe electrodes) to achieve full common mode rejection ratio (CMRR) and improve SNR, per official dataset guidelines.
- EEG recordings contain potential ocular/muscular artifacts; apply artifact rejection (e.g., ICA, EOG-based correction) and standard preprocessing (bandpass filtering, re-referencing) before analysis.
- 10 participants with 20 recordings each (total 200 EDF files); small dataset with limited generalization performance.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
