# EEG and Sex Differences Dataset

**Dataset**: `openneuro_ds002720` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Biological State | **Subjects**: 18 | **Files (Completed)**: 18 | **Channels**: 64 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

This dataset contains resting-state EEG recordings from 18 healthy young adults (14 male, 4 female; ages 18–28 years) collected at the University of Michigan. Participants were recorded during a resting-state protocol with eyes-open and eyes-closed conditions using a 64-channel BioSemi ActiveTwo system. The primary purpose of data collection was to investigate sex differences in resting-state EEG characteristics, with continuous recordings segmented for analysis.

## File Scan Result

> **Kernel SHA256**: `20b02ceed02f2918a41ccdf3b05addfe491f0fd18b9fd72c0e6ad972d340c7af`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Potential Task 1: sex classification from resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | M → 0, F → 1 |
- **Evidence**:
- **Notes**: Subject-level sex prediction from segmented continuous EEG. All segments from a given subject share the same label (M/F). The 2-second segmentation with 50% overlap creates multiple samples per subject for training. Class imbalance: 14 male vs 4 female subjects. No event structure is used; segmentation extracts fixed-length windows from the continuous recording treating task periods as resting neural data.

### Potential Task 2: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (18–28); native participants.tsv column |
- **Evidence**:
- **Notes**: Archetype C with segmentation-based epoching and info-native label. No events are used; continuous EEG is segmented into 2-second windows with 50% overlap, and each window inherits the subject's age from participants.tsv as the regression target. The narrow age range (18–28 years, N=18) makes this a challenging regression task. Segment length and overlap are inferred from standard continuous EEG analysis practices due to lack of explicit paradigm guidance.



## Data Quality Notes

- Severe class imbalance in sex classification task: 14 male vs 4 female subjects (3.5:1 ratio), which may lead to biased classifiers and poor generalization to female subjects.
- Narrow age range (18–28 years, span of only 10 years) makes age regression a challenging task with limited biological signal variance; model may learn confounds rather than true age-related EEG patterns.
- Small sample size (N=18) limits statistical power and increases risk of overfitting for both tasks.
- No event structure present in recordings; all analysis relies on arbitrary segmentation of continuous data, which may capture non-neural artifacts or state transitions.
- Segment length and overlap parameters (2 s, 50%) are inferred rather than empirically validated for this dataset.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
