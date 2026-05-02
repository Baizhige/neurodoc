# ERP-Based Brain-Computer Interface Recordings

**Dataset**: `physionet_erpbci` | **Year**: 2014 | **URL**: https://physionet.org/content/erpbci/1.0.0/
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 245 | **Channels**: 70 | **Sampling Rate**: 2048 Hz | **Manual Review**: Liu Peng

## Paradigm

Participants spelled characters using a standard 6x6 matrix speller while EEG was recorded with a BioSemi ActiveTwo system (64 EEG + 2 earlobe reference + 4 EOG channels) at 2048 Hz (Riccio et al., 2013). Each row and column of the 6x6 character matrix was randomly intensified for 100 ms with a 50 ms gap (150 ms SOA). Each row/column flashed approximately 20 times per trial, and participants mentally counted target character flashes to sustain attention. The kernel processes raw row/column flash events and classifies each as `seen` (target - the row or column containing the attended character flashed) or `unseen` (non-target) for both rows and columns separately.

## File Scan Result

> **Kernel SHA256**: `e0a11f6326ce932b8d655a71963420e1b77d7b011e8ab2e0e3a96f36b3fac752`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `seen (column)` | 2391 | event | raw | Target column flash (attended character's column lit up) |
| `seen (row)` | 2005 | event | raw | Target row flash (attended character's row lit up) |
| `unseen (column)` | 11819 | event | raw | Non-target column flash |
| `unseen (row)` | 9614 | event | raw | Non-target row flash |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | No subject age demographic information is publicly available in this dataset. |
| `subject_sex` | missing | No subject sex demographic information is publicly available in this dataset. |
| `device` | missing | Recordings collected via BioSemi ActiveTwo EEG system (2048 Hz sampling rate), with 64 EEG channels, 2 earlobe references, and 4 EOG channels; software re-referencing required for full CMRR. |


## Tasks

### Classical Task 1: P300 Target vs. Non-Target Classification in Matrix Speller
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (column)`, `seen (row)`, `unseen (column)`, `unseen (row)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seen (row)` | 1 | Target row flash (attended character's row intensified) |
  | `seen (column)` | 1 | Target column flash (attended character's column intensified) |
  | `unseen (row)` | 0 | Non-target row flash |
  | `unseen (column)` | 0 | Non-target column flash |
- **Evidence**:
  - 10.13026/C2101S — Dataset page describes ERP-based BCI recordings from a P300 matrix speller paradigm where participants spell characters by focusing on target flashes; row/column intensifications can be classified as target (attended) or non-target.
- **Notes**: Verify event ID mapping from events.tsv. Extract epochs centered on each row/column intensification event (±0.1/0.8s window). Combine `seen (row)` and `seen (column)` as positive class (y=1), `unseen (row)` and `unseen (column)` as negative class (y=0). EOG channels should be excluded from features. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Row vs. Column P300 Speller Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (column)`, `seen (row)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `seen (row)` | 0 | Target flash occurred in a row |
  | `seen (column)` | 1 | Target flash occurred in a column |
- **Evidence**:

- **Notes**: Use intersection of identified target row and target column to determine spelled character.

## Data Quality Notes

- Very high sampling rate (2048 Hz); consider downsampling to 256 or 512 Hz for computational efficiency.
- Class imbalance: 2 target flashes vs. 10 non-target flashes per sequence (1:5 ratio); balance with oversampling or cost-sensitive learning.
- EOG channels present (4 channels); apply artifact rejection before P300 classification.
- Age and sex information are not available.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
