# OpenBMI Motor Imagery EEG Dataset

**Dataset**: `other_openbmi` | **Year**: 2019 | **URL**: https://gigadb.org/dataset/100542
**Category**: Action/Output | **Subjects**: 54 | **Files (Completed)**: 108 | **Channels**: 62 | **Sampling Rate**: 1000 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

Fifty-four healthy subjects (24–35 years old; 25 females) participated in the OpenBMI experiments, which were recorded across two sessions on different days. For the motor imagery (MI) paradigm, EEG was acquired at 1000 Hz using a BrainAmp amplifier (Brain Products, Munich, Germany) with 62 Ag/AgCl EEG electrodes. The binary MI task comprised left- and right-hand imagery. In each trial, subjects first fixated on a central cross for 3 s and then performed the cued imagery task for 4 s according to a left or right arrow. Each MI session consisted of two phases, an offline training phase and an online test phase, and each phase contained 100 trials with balanced left- and right-hand imagery tasks. In the validation procedure reported in the paper, MI decoding was performed using 20 electrodes over the motor cortex, and EEG epochs were extracted from 1000 to 3500 ms relative to stimulus onset.

## File Scan Result

> **Kernel SHA256**: `42c2c71dbd5b0012e7422b9f830de227d3074d8ef424a3100e8bc4fb58103d75`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `left hand MI` | 5400 | event | raw | Left-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |
| `right hand MI` | 5400 | event | raw | Right-hand motor imagery trial onset (50/session x 2 sessions x 54 subjects) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (108/436) | N/A |
| `sex` | partial (108/436) | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Motor imagery decoding - Left vs. Right Hand
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`left hand MI`, `right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left hand MI` | 0 | Left-hand motor imagery |
  | `right hand MI` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1093/gigascience/giz002 — OpenBMI dataset with 54 subjects performing binary motor imagery (left vs right hand) across two sessions, using EEG epochs for CSP+LDA classification
  - DOI: 10.1016/j.neunet.2020.12.013 — Uses OpenBMI dataset for deep CNN-based transfer learning achieving 84.19% average accuracy
- **Notes**: 

## Data Quality Notes
- 
## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
