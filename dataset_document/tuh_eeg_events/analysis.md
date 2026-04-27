# TUH EEG Events Corpus

**Dataset**: `tuh_eeg_events` | **Year**: 2015-2016 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 290 | **Files (Completed)**: 518 | **Channels**: 24-33 | **Sampling Rate**: 250 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

The TUH EEG Event Corpus, a subset of the larger TUH EEG Corpus, contains annotated EEG data crucial for the analysis of various brain events. The dataset includes labeled recordings of events such as spike and slow wave discharges (spsw), generalized periodic epileptiform discharges (gped), periodic lateralized epileptiform discharges (pled), eye movements (eyem), artifacts (artf), and background (bckg) activities. This version of the corpus offers data files in the European Data Format (edf) and various annotation types, including lab and rec files, detailing event onset and duration.

The dataset is divided into two main sets: training and evaluation. The training set contains 359 files, with annotations spanning all event categories. The evaluation set is made up of 159 files, offering a separate set for testing algorithms developed on the training data. Files are stored with a systematic naming convention that references unique patient identifiers and session numbers. Two EEG channel configurations are used: averaged reference (AR) and linked ears reference (LE), aligning with standard 10/20 electrode montages for comprehensive data analysis.

This corpus is primarily used for EEG event classification, which is valuable for advancing research in epilepsy and neurological disorders. The data has been meticulously curated to support research in EEG signal processing and classification techniques.

## File Scan Result

> **Kernel SHA256**: `9c93f64e385e08686b90b12f5de77c778e1be7fb1cc6420c41ee7a4cc817dacd`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `artifact` | 13257 | event | raw | Non-specific artifact |
| `background` | 73372 | event | raw | Normal background EEG activity |
| `eye movement` | 1399 | event | raw | Eye movement artifact |
| `generalized periodic epileptiform discharges` | 15931 | event | raw | GPEDs - generalized periodic epileptiform pattern |
| `periodic lateralized epileptiform discharges` | 8182 | event | raw | PLEDs - lateralized epileptiform pattern |
| `spike and sharp wave` | 1212 | event | raw | Spike or sharp wave discharge |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 6-class EEG Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1.0 s, overlap = 0, target_events = [`artifact`, `background`, `eye movement`, `generalized periodic epileptiform discharges`, `periodic lateralized epileptiform discharges`, `spike and sharp wave`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `background` | 0 | Normal background EEG |
  | `spike and sharp wave` | 1 | Epileptiform spike/sharp wave |
  | `generalized periodic epileptiform discharges` | 2 | GPEDs |
  | `periodic lateralized epileptiform discharges` | 3 | PLEDs |
  | `artifact` | 4 | Non-specific artifact |
  | `eye movement` | 5 | Eye movement artifact |
- **Evidence**:
  - 10.1109/spmb.2015.7405421 — Performs 6-way EEG event classification (SPSW, GPED, PLED, ARTF, EYEM, BCKG) using 1-sec epochs with features computed every 0.1 s. Direct mapping to dataset event IDs confirmed.
- **Notes**: epoch_by_long_event_hdf5

### Classical Task 2: Binary Epileptiform vs. Background Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 1.0 s, overlap = 0, target_events = [`background`, `generalized periodic epileptiform discharges`, `periodic lateralized epileptiform discharges`, `spike and sharp wave`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `background` | 0 | Normal background EEG |
  | `spike and sharp wave` | 1 | Epileptiform spike/sharp wave |
  | `generalized periodic epileptiform discharges` | 1 | Epileptiform (GPEDs) |
  | `periodic lateralized epileptiform discharges` | 1 | Epileptiform (PLEDs) |
- **Evidence**:
  - 10.1109/spmb.2015.7405421 — Explicitly evaluates a 2-way (epileptiform vs background) classification paradigm collapsing SPSW, GPED, and PLED into one class.
- **Notes**: The background is long event, so here we use “epoch_by_long_event_hdf5" method

## Data Quality Notes

- Background annotations are long events; epileptiform events are short - class length mismatch may cause imbalance.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
