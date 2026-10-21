# High-Gamma EEG Motor Imagery Dataset

**Dataset**: `other_highgammadataset` | **Year**: 2017 | **URL**: https://gin.g-node.org/robintibor/high-gamma-dataset/src/master/data
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 28 | **Channels**: 133 | **Sampling Rate**: 500 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The High-Gamma Dataset contains EEG recordings from 14 healthy participants performing four cued motor execution conditions: left-hand finger tapping, right-hand finger tapping, bilateral toe clenching, and rest. EEG was recorded in a high-frequency-optimized laboratory using a 128-electrode WaveGuard Original cap and a NeurOne amplifier at 5 kHz. For the analyses reported in Schirrmeister et al. (2017), the data were resampled to 250 Hz and restricted to 44 electrodes over the motor cortex. Each participant completed about 13 runs, yielding roughly 963 trials on average, with the first 11 runs used for training and the last 2 runs used for testing. A key feature of this dataset is its suitability for studying movement-related activity in the high-gamma range, which makes it particularly valuable for evaluating EEG decoding methods based on deep neural networks.

## File Scan Result

> **Kernel SHA256**: `aaa8004eb70a2a4a6a4911a2a6e522e48652708968ab483419634579fb3402f5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `feet` | 1405 | event | raw | Bilateral toe clenching motor execution cue |
| `left_hand` | 1404 | event | raw | Left-hand finger tapping motor execution cue |
| `rest` | 1404 | event | raw | Rest period cue (no movement) |
| `right_hand` | 1404 | event | raw | Right-hand finger tapping motor execution cue |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Four-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left_hand`, `right_hand`, `feet`, `rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_hand` | 0 | Left-hand motor imagery |
  | `right_hand` | 1 | Right-hand motor imagery |
  | `feet` | 2 | Feet motor imagery |
  | `rest` | 3 | Rest but same cue |
- **Evidence**:
  - DOI: 10.1002/hbm.23730 — Uses the High-Gamma Dataset (HGD) with 14 subjects performing four-class motor imagery (left hand, right hand, feet, rest) across two sessions per subject, evaluating deep ConvNets against FBCSP baseline for EEG decoding.
- **Notes**: 

### Classical Task 2: Left vs. Right Hand Motor Imagery Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`left_hand`, `right_hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_hand` | 0 | Left-hand motor imagery |
  | `right_hand` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1002/hbm.23730 — Deep learning evaluation on HGD includes left/right hand motor imagery decoding as key binary classification subtask.
- **Notes**: 

## Data Quality Notes

- No exact age or sex information available in the public release.
- Two sessions per subject (train/test): separate by filename suffix for proper evaluation if needed.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
