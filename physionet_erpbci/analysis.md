# ERP-Based Brain-Computer Interface Recordings

**Dataset**: `physionet_erpbci` | **Year**: 2013 | **URL**: https://physionet.org/content/erpbci/1.0.0/
**Category**: Action/Output | **Subjects**: 21 | **Files (Completed)**: 245 | **Channels**: 70 | **Sampling Rate**: 2048 Hz

## Paradigm

Participants spelled characters using a standard 6x6 matrix speller while EEG was recorded with a BioSemi ActiveTwo system (64 EEG + 2 earlobe reference + 4 EOG channels) at 2048 Hz (Riccio et al., 2013). Each row and column of the 6x6 character matrix was randomly intensified for 100 ms with a 50 ms gap (150 ms SOA). Each row/column flashed approximately 20 times per trial, and participants mentally counted target character flashes to sustain attention. The kernel processes raw row/column flash events and classifies each as `seen` (target - the row or column containing the attended character flashed) or `unseen` (non-target) for both rows and columns separately.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `seen (row)` | varies | event | raw | Target row flash (attended character's row lit up) |
| `seen (column)` | varies | event | raw | Target column flash (attended character's column lit up) |
| `unseen (row)` | varies | event | raw | Non-target row flash |
| `unseen (column)` | varies | event | raw | Non-target column flash |

>
> Each 6x6 speller has 6 rows + 6 columns = 12 flashes per sequence; 2 are target (1 row + 1 column), 10 are non-target.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: P300 Target vs. Non-Target Classification in Matrix Speller
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (row)`, `seen (column)`, `unseen (row)`, `unseen (column)`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `seen (row)` | 1 | Target row flash (attended character's row intensified) |
  | `seen (column)` | 1 | Target column flash (attended character's column intensified) |
  | `unseen (row)` | 0 | Non-target row flash |
  | `unseen (column)` | 0 | Non-target column flash |
- **Evidence**:
  - DOI: 10.13026/C2101S — Dataset page describes ERP-based BCI recordings from a P300 matrix speller paradigm where participants spell characters by focusing on target flashes; row/column intensifications can be classified as target (attended) or non-target.
- **Kernel Notes**: Verify event ID mapping from events.tsv. Extract epochs centered on each row/column intensification event (±0.1/0.8s window). Combine `seen (row)` and `seen (column)` as positive class (y=1), `unseen (row)` and `unseen (column)` as negative class (y=0). EOG channels should be excluded from features. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Row vs. Column P300 Speller Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`seen (row)`, `seen (column)`]
- **Label Route**: `event`
- **Target Definition**: Distinguish whether target flash occurred in row or column for character-level decoding.

| Event | y | Meaning |
|-------|---|---------|
| `seen (row)` | 0 | Target flash occurred in a row |
| `seen (column)` | 1 | Target flash occurred in a column |

- **Notes**: Use intersection of identified target row and target column to determine spelled character.

## Data Quality Notes

- Very high sampling rate (2048 Hz); consider downsampling to 256 or 512 Hz for computational efficiency.
- Class imbalance: 2 target flashes vs. 10 non-target flashes per sequence (1:5 ratio); balance with oversampling or cost-sensitive learning.
- EOG channels present (4 channels); apply artifact rejection before P300 classification.
- Age and sex information are not available.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review