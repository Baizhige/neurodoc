# EEG Motor Movement/Imagery Database

**Dataset**: `physionet_eegmmidb` | **Year**: 2009 | **URL**: https://physionet.org/content/eegmmidb/1.0.0/
**Category**: Action/Output | **Subjects**: 109 | **Files (Completed)**: 1526 | **Channels**: 64 | **Sampling Rate**: 160 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

One hundred and nine volunteers performed a series of motor movement and motor imagery tasks, recorded with 64 EEG electrodes (international 10-10 system) at 160 Hz using the BCI2000 system (Schalk et al., 2004). Each subject completed 14 runs (R01-R14): two baseline runs (eyes open and eyes closed), and twelve task runs organized in three repeating cycles of four run types. Task runs alternate between real movements and mental imagery of the same movements. Two movement classes are used: left/right fist, and both fists/both feet. Events T0 (rest), T1, and T2 are annotated within each run; T1/T2 meanings differ by run number.

## File Scan Result

> **Kernel SHA256**: `bd1ed7ea5b310949f1bb2ce29057964e4e25db94ffb6a393129b948b562b88b8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Baseline, eyes closed` | 109 | event | raw | Eyes closed resting state baseline recording |
| `Baseline, eyes open` | 109 | event | raw | Eyes open resting state baseline recording |
| `Imagine Opening Both Fists Movement` | 2465 | event | raw | Motor imagery cue: open both fists |
| `Imagine Opening Feet Movement` | 2455 | event | raw | Motor imagery cue: open/move both feet |
| `Imagine Opening Left Fist Movement` | 2480 | event | raw | Motor imagery cue: open left fist |
| `Imagine Opening Right Fist Movement` | 2438 | event | raw | Motor imagery cue: open right fist |
| `Open Both Feet Movement` | 2469 | event | raw | Real movement cue: open both feet |
| `Open Both Fists Movement` | 2440 | event | raw | Real movement cue: open both fists |
| `Open Left Fist Movement` | 2471 | event | raw | Real movement cue: open left fist |
| `Open Right Fist Movement` | 2456 | event | raw | Real movement cue: open right fist |
| `Rest` | 19675 | event | raw | Rest period / trial baseline marker |
| `T1` | 2 | admin | raw | Task cue type 1 (meaning varies by run) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: 4-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Imagine Opening Fists Movement`, `Imagine Opening Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery |
  | `Imagine Opening Both Fists Movement` | 2 | Both-fists motor imagery |
  | `Imagine Opening Feet Movement` | 3 | Both-feet motor imagery |
- **Evidence**:
  - DOI: 10.1109/TNSRE.2022.3186442 — 4-class motor imagery classification (left/right fist, both fists, both feet) using the PhysioNet EEG Motor Imagery Database with tmin=0.0s and tmax=3.0s
- **Notes**: 

### Potential Task 1: 4-Class Motor Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Open Left Fist Movement`, `Open Right Fist Movement`, `Open Both Fists Movement`, `Open Both Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Open Left Fist Movement` | 0 | Left-fist movement |
  | `Open Right Fist Movement` | 1 | Right-fist movement |
  | `Open Both Fists Movement` | 2 | Both-fists movement |
  | `Open Both Feet Movement` | 3 | Both-feet movement |
- **Evidence**:

- **Notes**: 

### Potential Task 2: 4-Class Motor Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Open Left Fist Movement`, `Imagine Opening Right Fist Movement`, `Open Right Fist Movement`, `Imagine Opening Both Fists Movement`, `Open Both Fists Movement`, `Imagine Opening Feet Movement`, `Open Both Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery (R04/08/12) |
  | `Open Left Fist Movement` | 0 | Left-fist real movement (R03/07/11) |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery (R04/08/12) |
  | `Open Right Fist Movement` | 1 | Right-fist real movement (R03/07/11) |
  | `Imagine Opening Both Fists Movement` | 2 | Both-fists motor imagery (R06/10/14) |
  | `Open Both Fists Movement` | 2 | Both-fists real movement (R05/09/13) |
  | `Imagine Opening Feet Movement` | 3 | Both-feet motor imagery (R06/10/14) |
  | `Open Both Feet Movement` | 3 | Both-feet real movement (R05/09/13) |
- **Evidence**:

- **Notes**: 

### Potential Task 3: Binary Left vs. Right Fist Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Left Fist Movement`, `Imagine Opening Right Fist Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Left Fist Movement` | 0 | Left-fist motor imagery |
  | `Imagine Opening Right Fist Movement` | 1 | Right-fist motor imagery |
- **Evidence**:

- **Notes**: 

### Potential Task 4: Both Fists vs. Both Feet Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, target_events = [`Imagine Opening Both Fists Movement`, `Imagine Opening Feet Movement`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Imagine Opening Both Fists Movement` | 0 | Both-fists motor imagery (R06/10/14) |
  | `Imagine Opening Feet Movement` | 1 | Both-feet motor imagery (R06/10/14) |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

- Age and sex information are not available in the public metadata.
- Known data quality issues: several subjects have noisy recordings; EEG.physionet.org community notes suggest subjects S088, S089, S092, S100, S104 may have unusual recordings.
- T1/T2 event meaning **changes by run number**; always filter by run before assigning class labels.
- `Baseline` (T0) events in task runs are rest periods and should be excluded from MI classification targets.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed