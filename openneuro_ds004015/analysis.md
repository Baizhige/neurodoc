# Attended Speaker Paradigm (cEEGrid Data)

**Dataset**: `openneuro_ds004015` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004015
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 36 | **Channels**: 18 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A two-competing speaker auditory attention paradigm in which participants were instructed to selectively attend to one of two simultaneously presented audiobooks under varying spatial (same location vs. different locations) and loudness conditions. EEG was recorded using a cEEGrid around-the-ear electrode array with 18 channels. The dataset is intended for auditory attention decoding (AAD) research using ear-worn EEG systems.

## File Scan Result

> **Kernel SHA256**: `79c682e2ff72a23474a44ecccfb73cc8d0fa50f5254957ea7af7e1c3ce0dedf1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Beep` | 756 | event | raw | Auditory cue tone for attention cueing or calibration |
| `Calib_End` | 102 | event | raw | End of calibration period marker |
| `Calib_Start` | 21 | event | raw | Start of calibration period marker |
| `StartTrigger` | 120 | event | raw | Block onset marker for experimental blocks |
| `beam` | 420 | event | raw | Same spatial location condition (both speakers at same location) |
| `boundary` | 21 | event | raw | Automated boundary marker (data segment discontinuity) |
| `omni` | 420 | event | raw | Different spatial location condition (speakers at different locations) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Auditory Attention Classification (Attended vs Ignored Speaker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `attended_speaker` | 1 | Participant attended to this audiobook (derived from task metadata) |
  | `ignored_speaker` | 0 | Participant ignored this audiobook (derived from task metadata) |
- **Super Meta Notes**: Labels must be derived from experimental instructions—participants were instructed which audiobook to attend per block. The `beam` and `omni` events (420 each) mark spatial condition blocks (same vs different location), but attended/ignored speaker labels are NOT present in raw event markers. Kernel step: Load participant metadata files to determine attended speaker condition per block; assign labels to corresponding EEG segments.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.869426
- **Kernel Notes**: Segment continuous EEG into 60s non-overlapping windows aligned with experimental blocks using `StartTrigger` events for block onset. Use task metadata to determine which speaker (left/right audiobook) was attended during each block. Apply speech envelope tracking features, spectral entropy, or intersubject correlation for classification. cEEGrid provides only 18 channels—limited spatial coverage compared to standard scalp EEG.

### Potential Task 1: Continuous Auditory Attention Decoding (Fine-Grained Segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `StartTrigger` | — | Block onset marker for segment alignment |
  | `beam` | — | Same-location spatial condition marker |
  | `omni` | — | Different-location spatial condition marker |
- **Super Meta Notes**: Labels derived from stimulus envelopes (attended vs ignored speech stream); no discrete trial events marking attended vs ignored speaker—must be computed from continuous speech streams.
- **Kernel Notes**: Use 2s sliding windows with 50% overlap aligned to `StartTrigger` events for fine-grained AAD. cEEGrid's 18-channel coverage limits spatial filtering; envelope tracking dynamics better captured at finer temporal resolution. Speech envelope features should be correlated against EEG segments to decode attended stream across time.

### Normal Task 1: Spatial Attention Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 60.0, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `beam` | 1 | Same spatial location condition (both speakers at same location) |
  | `omni` | 0 | Different spatial location condition (speakers at different locations) |
- **Evidence**: Paradigm description; 420 `beam` and 420 `omni` events correspond to spatial condition blocks
- **Kernel Notes**: `beam` and `omni` events (420 each) directly encode spatial attention manipulation. Classify spatial condition from EEG features within each block to assess how spatial separation affects neural signatures of auditory attention. Exclude calibration events (`Beep`, `Calib_Start`, `Calib_End`) from analysis epochs.