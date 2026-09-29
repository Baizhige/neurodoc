# High Gamma Dataset

**Dataset**: `other_highgammadataset` | **Year**: 2017 | **URL**: https://github.com/robintibor/high-gamma-dataset
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 128 | **Channels**: 128 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

This dataset contains EEG recordings from 14 healthy subjects performing motor imagery and motor execution tasks. Subjects performed movements (or imagined movements) of the left hand, right hand, feet, and rest periods in a cue-guided paradigm. The data was recorded with a 128-channel active electrode system at 500 Hz sampling rate. The dataset was originally published to support development and evaluation of deep learning methods for EEG decoding, particularly convolutional neural networks applied to raw EEG signals.

## File Scan Result

> **Kernel SHA256**: `84cf1609a8c8c8b100fb5db96d48bb3e82ba482aebc118166b0ab10de95aa28e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `feet` | 3372 | event | raw | Trial phase onset: feet |
| `left_hand` | 3370 | event | raw | Trial phase onset: left_hand |
| `rest` | 3370 | event | raw | Trial phase onset: rest |
| `right_hand` | 3372 | event | raw | Trial phase onset: right_hand |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing |  |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | missing |  |

## Tasks

### Classical Task 1: 4-class motor imagery/execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`, `feet`, `rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_hand` | 0 | Trial phase onset: left_hand |
  | `right_hand` | 1 | Trial phase onset: right_hand |
  | `feet` | 2 | Trial phase onset: feet |
  | `rest` | 3 | Trial phase onset: rest |
- **Evidence**:
  - 10.1002/hbm.23730 — Schirrmeister et al. 2017 (HBM) describes 4-class classification of left hand, right hand, left foot, right foot from raw EEG using deep ConvNets; 4-second trials with cropped training strategy
- **Notes**: The event meanings are trial phase markers per the locked ground truth, not explicit MI class labels. However, the classical task treats these as condition labels for motor imagery/execution classification following the primary paper's paradigm. The `rest` condition serves as a baseline/4th class. The effective motor task combines imagined and executed movements per limb as the dataset does not distinguish these phases at the event level.

### Classical Task 2: 3-class motor execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`, `feet`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `left_hand` | 0 | Trial phase onset: left_hand |
  | `right_hand` | 1 | Trial phase onset: right_hand |
  | `feet` | 2 | Trial phase onset: feet |
- **Evidence**:
  - 10.1002/hbm.23730 — Derived from the classical 4-class task by excluding rest condition. The three movement events (left_hand, right_hand, feet) represent executed movements. 4-second trials per primary paper.
- **Notes**: This task uses trial phase onset markers as classification targets for motor execution. The dataset contains both imagined and executed movements, but EDF annotations do not distinguish them; this candidate uses the available event structure for pure motor execution classification without rest baseline. The epoch parameters are inferred from the 4-class task configuration (same primary paper).

### Potential Task 1: 2-class hand vs feet motor imagery/execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`, `feet`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | left_hand | 0 | hand |
  | right_hand | 0 | hand |
  | feet | 1 | feet |
- **Evidence**:
  - 10.1002/hbm.23730 — Binary reduction of the 4-class task: collapse left_hand and right_hand into a single 'hand' class (y=0) versus feet (y=1). Useful for evaluating limb-category discrimination. The original paper's FBCSP and ConvNet analyses included such binary decompositions.
- **Notes**: Two-class limb-category discrimination by merging the two hand conditions. Event IDs confirmed as trial phase onset markers in EDF annotations across all sampled files. Despite being phase markers rather than explicit MI class labels, they form a valid classification task for hand vs feet limb-category discrimination as analyzed in the referenced work.

### Potential Task 2: 2-class left vs right hand motor imagery/execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_hand` | 0 | Trial phase onset: left_hand |
  | `right_hand` | 1 | Trial phase onset: right_hand |
- **Evidence**:
  - 10.1002/hbm.23730 — Binary reduction focusing on lateralized hand discrimination: left_hand (y=0) versus right_hand (y=1). Classic BCI application derived from the 4-class task. Excludes feet and rest events.
- **Notes**: Event IDs confirmed by direct reading of EDF annotation headers. Following the isolation rules, these are interpreted as trial phase markers rather than motor imagery class labels, since the dataset files do not explicitly state they represent motor imagery classes. However, they form a valid classification task as distinct trial phase conditions.

### Potential Task 3: 2-class movement vs rest
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`, `feet`, `rest`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | left_hand | 0 | movement |
  | right_hand | 0 | movement |
  | feet | 0 | movement |
  | rest | 1 | rest |
- **Evidence**:
  - 10.1002/hbm.23730 — Binary task discriminating any movement condition from rest; collapse left_hand, right_hand, feet into 'movement' class versus rest baseline.
- **Notes**: All four events are trial phase onset markers per the locked ground truth. This task uses them as state labels (movement engagement vs. rest) rather than motor imagery class labels, which is valid under binding rule 1. The movement class (y=0) merges three distinct movement-related trial phases, while rest (y=1) provides an explicit baseline condition.

### Potential Task 4: 4-class trial phase state detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`left_hand`, `right_hand`, `feet`, `rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | left_hand | 0 | Trial phase onset: left_hand |
  | right_hand | 1 | Trial phase onset: right_hand |
  | feet | 2 | Trial phase onset: feet |
  | rest | 3 | Trial phase onset: rest |
- **Evidence**:
- **Notes**: This task treats the four event types as trial phase state markers rather than motor imagery class labels, consistent with the dataset's event meanings. The same four events used in motor imagery framing are here reinterpreted as state indicators for phase detection. Epoch timing is inferred from typical trial-phase classification windows; the dataset lacks explicit duration metadata.


## Data Quality Notes

- All subject demographic metadata (age, sex, handedness) is missing from the dataset files.
- Equipment metadata (amplifier, cap) is missing from the dataset files.
- The event annotations are trial phase onset markers rather than explicit motor imagery or motor execution class labels; the dataset does not distinguish imagined versus executed movements at the event level.
- Event counts are well-balanced across conditions (~3370-3372 per class).
- The dataset contains both motor imagery and motor execution data, but this distinction is not encoded in the EDF annotations.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
