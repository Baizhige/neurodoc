# EEG During Mental Arithmetic Task

**Dataset**: `physionet_eegmat` | **Year**: 2018 | **URL**: https://physionet.org/content/eegmat/1.0.0/
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 72 | **Channels**: 23 | **Sampling Rate**: 500 Hz | **Manual Review**: Liu Peng

## Paradigm

Thirty-six healthy subjects (Subject00-Subject35, ages 16-26, predominantly female) completed a mental arithmetic task while EEG was recorded monopolarly using a Neurocom 23-channel system with Ag/AgCl electrodes (Zyma et al., 2019). Each subject contributed two files: a background resting-state recording (suffix `_1.edf`) and a mental arithmetic task recording (suffix `_2.edf`). During the mental arithmetic task, subjects performed serial subtraction (e.g., 3141 minus 42) while EEG was recorded. A separate `Count quality` field in `subject-info.csv` rates the subject's arithmetic performance as Good or Bad, providing a behavioral quality label.

## File Scan Result

> **Kernel SHA256**: `2d377403dfb36e0b6ad6454cf2d69b00d8096cf9a7ebb560a8baff950dedaad6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Background EEG;Count Quality: Bad` | 12 | event | raw | Resting-state recording with poor arithmetic performance label |
| `Background EEG;Count Quality: Good` | 24 | event | raw | Resting-state recording with good arithmetic performance label |
| `Mental Arithmetic Task EEG;Count Quality: Bad` | 12 | event | raw | Mental arithmetic task recording with poor performance label |
| `Mental Arithmetic Task EEG;Count Quality: Good` | 24 | event | raw | Mental arithmetic task recording with good performance label |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Age range: 16–26 years, mean age: approximately 18.33 years |
| `sex` | complete | Males (M): 8, females (F): 28, predominantly female |
| `device` | missing | EEG was recorded using a 23-channel Neurocom monopolar system (XAI-MEDICA, Ukraine) with silver/silver chloride electrodes placed per the international 10–20 system, linked ear reference, 500 Hz sampling rate, 0.5–45 Hz bandpass filtering, 50 Hz notch filtering, and electrode impedance kept below 5 kΩ. |


## Tasks

### Classical Task 1: Mental Arithmetic vs Rest Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Resting-state, bad quality |
  | `Background EEG;Count Quality: Good` | 1 | Resting-state, good quality |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 2 | Mental arithmetic, bad quality |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 3 | Mental arithmetic, good quality |
- **Evidence**:
  - Paradigm section describes two conditions: background resting-state (`_1.edf`) and mental arithmetic task (`_2.edf`)
  - Event Structure table confirms four event types combining condition and count quality
- **Notes**: Binary classification of cognitive state (rest vs mental arithmetic), collapsing across count quality. Long epochs (60s) assumed to capture full recording duration; adjust if actual durations differ.

### Classical Task 2: Mental Arithmetic Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Poor arithmetic performance |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good arithmetic performance |
- **Evidence**:
  - Paradigm section states `Count quality` field rates arithmetic performance as Good or Bad
  - Event Structure table shows 10 Bad and 26 Good mental arithmetic recordings
- **Notes**: Classifies arithmetic performance quality during mental arithmetic task only. Excludes background recordings. Imbalanced classes (10 vs 26).

### Classical Task 3: Resting-State Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Poor arithmetic performance (rest) |
  | `Background EEG;Count Quality: Good` | 1 | Good arithmetic performance (rest) |
- **Evidence**:
  - Paradigm section notes count quality is a behavioral label from `subject-info.csv`
  - Event Structure table shows 10 Bad and 26 Good background recordings
- **Notes**: Investigates whether arithmetic quality correlates with resting-state EEG patterns. Same subjects in both conditions, so quality label is subject-level. Imbalanced classes (10 vs 26).

### Classical Task 4: Four-Way Condition-Quality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`, `Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Rest, bad quality |
  | `Background EEG;Count Quality: Good` | 1 | Rest, good quality |
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 2 | Task, bad quality |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 3 | Task, good quality |
- **Evidence**:
  - Paradigm describes full 2x2 design: condition (rest/task) x quality (good/bad)
  - Event Structure table provides all four combinations
- **Notes**: Multi-class extension exploring interaction between cognitive state and performance quality. Very imbalanced (10/26/10/26). May require stratified sampling or class weighting.

### Potential Task 1: Subject Age Regression from Mental Arithmetic
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping |
- **Evidence**:
  - Paradigm section notes ages 16-26
  - Info table confirms `age` is complete
- **Notes**: Predicts subject age from mental arithmetic EEG. Requires pairing event epochs with info metadata by subject ID. Age range is narrow (10 years), limiting regression difficulty.

### Potential Task 2: Subject Sex Classification from Mental Arithmetic
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 60 s, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | no mapping |
- **Evidence**:
  - Paradigm notes predominantly female subjects
  - Info table confirms `sex` is complete
- **Notes**: Binary sex classification from mental arithmetic EEG. Predominantly female sample may cause class imbalance. Requires super meta pairing with subject info.

### Potential Task 3: Continuous Quality Regression (Rest Condition)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`Background EEG;Count Quality: Bad`, `Background EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |---|---|---|
  | `Background EEG;Count Quality: Bad` | 0 | Bad quality label |
  | `Background EEG;Count Quality: Good` | 1 | Good quality label |
- **Evidence**:
  - Event Structure provides binary quality labels embedded in event descriptions
  - Paradigm notes count quality is behavioral performance metric
- **Notes**: Treats binary quality as pseudo-continuous regression target (0/1) using sliding windows. Alternative formulation of Task 3. Overlap creates more samples from limited data.

### Potential Task 4: Continuous Quality Regression (Task Condition)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`Mental Arithmetic Task EEG;Count Quality: Bad`, `Mental Arithmetic Task EEG;Count Quality: Good`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |---|---|---|
  | `Mental Arithmetic Task EEG;Count Quality: Bad` | 0 | Bad quality label |
  | `Mental Arithmetic Task EEG;Count Quality: Good` | 1 | Good quality label |
- **Evidence**:
  - Same evidence as Potential Task 3, applied to mental arithmetic condition
  - Event Structure confirms task condition events with quality labels
- **Notes**: Regression formulation of Task 2. Sliding window approach for more samples. Quality label is subject-level, so all windows from same subject share identical target.

## Data Quality Notes

- Two files per subject (`_1.edf` = background, `_2.edf` = task); pair them by Subject ID.
- Count quality (Good/Bad) is embedded in the annotation description after the semicolon; always parse carefully.
- ECG channel present (channel `A2-A1`) in some recordings; exclude from EEG feature extraction.
- Small dataset (36 subjects x 2 = 72 files); limited generalization.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
