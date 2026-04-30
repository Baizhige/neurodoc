# EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task

**Dataset**: `openneuro_ds003838` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003838/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 86 | **Files (Completed)**: 296 | **Channels**: 2 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants performed a classic digit span working memory task involving serial recall of digit sequences of 5, 9, or 13 digits, along with a separate eyes-closed resting state condition. Each digit in a sequence was marked with an event indicating the digit position, sequence length, and whether it was later correctly recalled or forgotten. The dataset also includes ECG/PPG physiological signals recorded simultaneously with EEG.

## File Scan Result

> **Kernel SHA256**: `72be9b71cff9d332c437c15932ff7b2710ac85e0f5b790a157ad8c3103e48c46`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `[98]` | 8 | event | raw |  |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `PPG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `PPG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Standard segmentation approach for subject-level regression. Continuous EEG is divided into 4-second windows with 50% overlap; each window inherits the subject's age from participants.tsv as the regression target. No event structure is required since this is a subject-level biomarker prediction task.

### Potential Task 2: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | subject_sex | f → 0 (female); m → 1 (male) |
- **Evidence**:
  - participants.tsv — N=86 subjects with complete sex data: 74 female (f), 12 male (m)
- **Notes**: Standard segmentation approach for subject-level demographic classification. 4-second non-overlapping/overlapping windows are extracted from continuous EEG and labeled with the subject's sex from participants.tsv. Class imbalance is notable (86% female, 14% male) but the task remains valid with two distinct classes. The epoch parameters are inferred from standard practice for subject-level prediction tasks since no specific segmentation parameters are documented in the dataset.

### Potential Task 3: Resting State Segmentation with Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Archetype C (segmentation + info-native). Continuous 4-minute eyes-closed resting-state EEG is segmented into 4-second non-overlapping windows with 50% overlap. No event-based labels exist for rest segments, so segmentation is used with subject age as the continuous regression target. Age is a native participants.tsv column (Meta Level = raw). Segment length of 4s is standard for resting-state EEG feature extraction; overlap of 0.5 maximizes data usage for regression. The 4-minute recording duration yields approximately 120 segments per subject (240 with overlap), providing substantial sample size for age prediction models.

### Potential Task 4: Resting State Segmentation with Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | subject_sex | m → 0 (male); f → 1 (female) |
- **Evidence**:
  - participants.tsv — sex column with complete coverage (N=86: 12 male, 74 female)
  - README — describes 4 minutes of eyes-closed resting state EEG data
- **Notes**: Standard resting-state segmentation approach: continuous 4-minute eyes-closed rest EEG is divided into 4-second non-overlapping or overlapping windows. Since no event-based labels exist for rest segments, archetype C (segmentation + info-native) is used with subject sex as the binary classification target. This is a common biomarker benchmark for resting-state EEG. Segment length and overlap are inferred from standard resting-state analysis conventions.

## Data Quality Notes

- Event structure shows only a single generic event ID `[98]` with 8 total occurrences across all files, indicating event metadata is not fully parsed or the digit span trial markers are stored in a format not captured by the current scan.
- The Tasks section describes rich event-based tasks (correct vs error memory encoding, working memory load classification) but the File Scan Result does not confirm the presence of these event codes in the parsed data; event parsing may require kernel update or manual inspection.
- Device information is completely missing from info fields, limiting hardware provenance documentation.
- NASA_phys_3 field has partial completeness (85/86 subjects), leaving one missing value for physical demand at the third timepoint.
- PPG channel is present as a native MISC channel but requires verification of channel role and unit for proper physiological interpretation.
- EEG_excluded field indicates some subjects were excluded from EEG analysis due to poor signal quality; users should consider filtering on this field or using it as a quality control prediction target.
- The dataset contains only 2 EEG channels, which is unusually sparse for typical EEG analysis and may limit spatial resolution of neural signatures.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
