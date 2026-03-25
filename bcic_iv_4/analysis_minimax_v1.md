# BCI Competition IV Dataset 4 (ECoG Finger Movement Decoding)

**Dataset**: `bcic_iv_4` | **Year**: 2008 | **URL**: https://www.bbci.de/competition/iv/desc_4.html
**Category**: Action/Output | **Subjects**: 3 | **Files (Completed)**: 3 (Case B kernel) | **Channels**: 48-64 (variable per subject; ECoG) | **Sampling Rate**: 1000 Hz

## Paradigm

Three subjects (sub1-sub3) performed individual finger flexions under instruction while ECoG (electrocorticography) was recorded from 48-64 electrodes implanted over sensorimotor cortex (BCI Competition IV, 2008). Subjects flexed each of the five fingers individually on cue. Continuous finger flexion amplitude was measured via a data glove and stored as 5 labels per time sample. The dataset contains a training segment (~400 s per subject) with labeled finger flexion signals and a test segment (~200 s) with labels withheld. The Case B kernel concatenates train and test segments into a single continuous raw signal per subject; finger flexion signals (5 channels) are stored as `misc`-type stim channels (`finger1`-`finger5`).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://www.bbci.de/competition/iv/desc_4.html

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `train_segment` | 1/subject | admin | raw | Annotates the entire training segment (with labeled finger flexions) |
| `test_segment_onset` | 1/subject | admin | raw | Marks the onset of the unlabeled test segment |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Finger flexion labels are **not** stored as event annotations but as 5 continuous `misc` stim channels (`finger1`-`finger5`). This is a regression/continuous decoding task.
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Continuous Finger Flexion Trajectory Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.56 s (256 time points *), overlap = 0.99 * (sliding interval ~0.01 s), target_events = N/A (sliding window segmentation)
- **Label Route**: `misc` → `Annotation` (super meta derived from misc channels)
- **Meta Level**: super
- **Target Definition**:
  | Finger | y | Meaning |
  |--------|---|---------|
  | `finger1` | 0-1 | Thumb flexion amplitude (continuous) |
  | `finger2` | 0-1 | Index finger flexion amplitude (continuous) |
  | `finger3` | 0-1 | Middle finger flexion amplitude (continuous) |
  | `finger4` | 0-1 | Ring finger flexion amplitude (continuous) *excluded from official evaluation |
  | `finger5` | 0-1 | Little finger flexion amplitude (continuous) |
- **Super Meta Notes**: Labels are continuous finger flexion trajectories recorded via data glove at 25Hz, upsampled to 1000Hz to match ECoG. Apply MinMaxScaler (0-1 normalization) as described in papers. Use temporal alignment offset of ~0.2s to synchronize ECoG with finger movement.
- **Evidence**:
  - DOI: 10.1109/tim.2025.3644562 — Uses segmentation (256-point windows, 0.01s slide) to decode continuous finger trajectories, achieving correlation 0.69
  - DOI: 10.1109/ieeeconf58974.2023.10405112 — Proposes FingerFlex encoder-decoder for regression on 5 finger channels, achieving correlation up to 0.74
  - desc_4.pdf — Official BCI Competition IV Dataset 4 description: goal is predicting continuous finger flexion trajectories evaluated by correlation coefficient
- **Kernel Notes**: Extract sliding windows from raw ECoG (excluding finger misc channels). For each window, extract corresponding finger flexion values from finger1-finger5 misc channels as regression targets. Ring finger (finger4) was excluded from official competition evaluation.

### Primary Task 2: Left Hand vs Right Hand Finger Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 2.0 s * (aligned to 2s cue duration from desc_4.pdf), target_events = [`movement_onset_left`, `movement_onset_right`] (derived)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Left hand movement | 0 | Finger flexion of left-hand fingers (derived from thresholding finger1-finger5) |
  | Right hand movement | 1 | Finger flexion of right-hand fingers (derived from thresholding finger1-finger5) |
- **Super Meta Notes**: Labels derived by thresholding continuous finger flexion amplitude channels (finger1-finger5) to identify discrete left-hand vs right-hand movement events. Left hand comprises thumb+index (fingers 1-2) or all fingers when cued to left side; right hand similarly for right side.
- **Evidence**:
  - DOI: 10.1109/i2ct61223.2024.10543868 — Binary classification of finger flexion movements: left hand vs right hand (RH=1, LH=0), achieving 80% accuracy with Random Forest
- **Kernel Notes**: First threshold finger1-finger5 misc channels to detect movement onset (amplitude > threshold). Group fingers by hand (left: thumb/index, right: middle/ring/little or as per experimental cue). Create event markers for left/right hand movement onset, then epoch using epoch_by_event_hdf5.

### Normal Task 1: Finger Flexion Decoding - Training Segment (epoch_by_long_event)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = duration of `train_segment`, overlap = 0.5 s (sliding window), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: N/A (target labels are continuous; see notes below)
- **Notes**: This is a **regression task**, not a standard classification task. The `train_segment` annotation spans the entire training portion (~400 s); use `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5` to extract fixed-length windows. Within each epoch, extract the corresponding `finger1`-`finger5` misc-channel values as regression targets. The `test_segment_onset` annotation marks where labels become unavailable. Finger channels must be **excluded** from the EEG feature matrix but retained as label sources.

### Normal Task 2: Active vs. Rest Finger Movement Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: Requires custom thresholding of finger channel amplitudes to define discrete movement epochs; not directly supported by standard `epoch_by_event_hdf5`.
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `misc`
- **Target Definition**: Needs verification.
- **Notes**: Threshold the `finger1`-`finger5` misc channels to identify movement onset events, then apply `epoch_by_event_hdf5`. Active finger movement (amplitude > threshold) vs. rest (amplitude <= threshold) yields a binary classification problem per finger.

## Data Quality Notes

- ECoG data, not scalp EEG: electrode locations are patient-specific implants over sensorimotor cortex; no standard montage applies.
- Channel count varies per subject: sub1 = 62, sub2 = 64, sub3 = 48 ECoG channels.
- Each file additionally contains 5 `misc` channels (`finger1`-`finger5`) storing continuous flexion amplitudes; **exclude these from EEG analysis but use them as regression labels**.
- No age or sex information available.
- High sampling rate (1000 Hz); consider downsampling to <=250 Hz for classification tasks.
- Test-segment labels are withheld; only the `train_segment` portion is usable for supervised learning.

## References

- **Reference**: BCI Competition IV (2008), Dataset 4 - Finger Movements in ECoG. https://www.bbci.de/competition/iv/desc_4.html
