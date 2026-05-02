# TUH EEG Seizure Corpus

**Dataset**: `tuh_eeg_seizure` | **Year**: 2018 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg
**Category**: Biological State | **Subjects**: 675 | **Files (Completed)**: 7361 | **Channels**: 17-128 | **Sampling Rate**: 250/256/400/1000 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The TUH EEG Seizure Corpus (TUSZ) is a specialized dataset developed to advance seizure detection algorithms through machine learning. A subset of the broader TUH EEG Corpus, this dataset includes sessions specifically featuring seizure events, alongside sessions without seizures for testing false alarm rates. It consists of data from three primary directories: training (train), development (dev), and evaluation (eval), with 7361 files in total, across various seizure and non-seizure events.

The dataset features EEG data in European Data Format (edf), with event-based annotations captured in both multi-class and bi-class formats. Multi-class annotations provide detailed seizure types, while bi-class annotations simplify the dataset into seizure (seiz) and background (bckg) labels. These annotations are recorded per channel, capturing the spread of seizures across multiple electrodes.

EEG recordings are captured using two common reference configurations: averaged reference (AR) and linked ears reference (LE), with the data adhering to the standard 10/20 channel montage for consistency across files. The dataset includes a vast number of seizure events, with specific counts for training, development, and evaluation sets.

The TUSZ corpus plays a vital role in the development and testing of advanced seizure detection systems, supporting both the detection of seizures and the analysis of seizure-free segments

## File Scan Result

> **Kernel SHA256**: `0c90e3ec94547026731787ac95cb32b924b667dc778975c503f0d947daff981f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `absz` | 121 | event | raw | Absence seizure |
| `bckg` | 15454 | event | raw | Background activity |
| `cpsz` | 1520 | event | raw | Complex partial seizure |
| `fnsz` | 4891 | event | raw | Focal non-specific seizure |
| `gnsz` | 2491 | event | raw | Generalized non-specific seizure |
| `mysz` | 3 | event | raw | Myoclonic seizure |
| `seiz` | 146 | event | raw | Seizure event (Common seizure class which can include all types of seizure) |
| `spsz` | 57 | event | raw | Simple partial seizure |
| `tcsz` | 199 | event | raw | Tonic-clonic seizure (At first stiffening and then jerking of body (Grand Mal)) |
| `tnsz` | 126 | event | raw | Tonic seizure (Stiffening of body during seizure, EEG effects disappears) |


> the meaning from dataset file "seizures_types_v02.xlsx"

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Binary Seizure Detection (Seizure vs Background)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`absz`, `bckg`, `cpsz`, `fnsz`, `gnsz`, `mysz`, `seiz`, `spsz`, `tcsz`, `tnsz`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Background / non-seizure |
  | `gnsz` | 1 | Generalized non-specific seizure |
  | `fnsz` | 1 | Focal non-specific seizure |
  | `cpsz` | 1 | Complex partial seizure |
  | `absz` | 1 | Absence seizure |
  | `tnsz` | 1 | Tonic seizure |
  | `spsz` | 1 | Simple Partial Seizure |
  | `mysz` | 1 | Myoclonic Seizure |
  | `tcsz` | 1 | Tonic Clonic Seizure |
- **Evidence**:
  - 10.1088/1741-2552/ac7d0d — Uses TUH EEG with 1-second windows (50% overlap) for binary seizure vs non-seizure classification; leave-one-out cross-subject evaluation
  - 10.1109/tii.2023.3274913 — Uses TUH EEG with 4-second non-overlapping epochs for binary seizure detection; CNN classifier achieved 98.48% average accuracy with leave-one-patient-out cross-validation
- **Notes**: 

### Potential Task 1: Multi-class Seizure Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`absz`, `cpsz`, `fnsz`, `gnsz`, `mysz`, `spsz`, `tcsz`, `tnsz`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `gnsz` | 0 | Generalized non-specific seizure |
  | `fnsz` | 1 | Focal non-specific seizure |
  | `cpsz` | 2 | Complex partial seizure |
  | `absz` | 3 | Absence seizure |
  | `tnsz` | 4 | Tonic seizure |
  | `spsz` | 5 | Simple Partial Seizure |
  | `tcsz` | 6 | Tonic Clonic Seizure |
  | `mysz` | 7 | Myoclonic Seizure |
- **Evidence**:

- **Notes**: classify further specific seizure, more challenge.

## Data Quality Notes

- ## Kernel Responsibilities

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
