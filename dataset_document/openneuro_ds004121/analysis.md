# BCIT Mind Wandering

**Dataset**: `openneuro_ds004121` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004121
**Category**: Complex Applied | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 74 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

Subjects performed a long-duration simulated driving task involving lane maintenance, speed control, and a police vehicle vigilance sub-task (detecting a police car among traffic), while exposed to lateral perturbations and varying background audio conditions (silence vs. music vs. podcast). The mind wandering manipulation used periodic thought probes to assess on-task vs. off-task mental state. EEG biomarkers of mind wandering during driving were investigated.

## File Scan Result

> **Kernel SHA256**: `fc65488bb8fca5ce7e612a0839377096ee92ff2e3cc4f1212d8c7cec499d416b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | year_of_birth | 1976–1993 (year) | Approximate age at study ~21–38 years (circa 2014); single value per subject applied to all segments |
- **Evidence**:
  - participants.tsv — year_of_birth column complete for all 21 subjects with range 1976–1993
- **Notes**: Segmentation-based approach for subject-level biomarker regression. No event structure required; 4-second segments with 50% overlap are standard for resting/baseline EEG feature extraction in subject-level prediction tasks. The year_of_birth field is native to participants.tsv (B3 archetype, raw meta level). Age is a fundamental demographic variable predictive of EEG spectral properties including alpha frequency slowing and theta power increases.

### Classical Task 2: Subject Age Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | year_of_birth | ≤1980 | 0 | Older (born 1980 or earlier) |
  | year_of_birth | >1980 | 1 | Younger (born after 1980) |
- **Evidence**:
- **Notes**: Median split at 1980 derived from participants.tsv year_of_birth column (sample values: 1984, 1979, 1978, 1976, 1993, 1980, 1985). With N=21 subjects, this task is underpowered but technically valid. The group column is constant ('Normal') and provides no discriminability. Segmentation-based epoching is used to extract 4-second non-overlapping/overlapping windows for subject-level spectral feature extraction, standard for biomarker classification from continuous driving EEG. The binary split creates balanced classes if the birth year distribution permits.

### Classical Task 3: Driving with continuous segmentation (subject-level age)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | year_of_birth | 1976–1993 (year) | Subject birth year from participants.tsv; age can be derived as (study_year - year_of_birth) if needed. Used as continuous subject-level target for regression across segmented driving epochs. |
- **Evidence**:
  - 10.1016/j.neuroimage.2019.116054 — Mega-analysis paper using continuous EEG with temporal overlap regression for cognitive aspects; supports segmentation-based regression on sustained naturalistic paradigms.
- **Notes**: Archetype C with native info column (year_of_birth). The kernel does not need to derive any channels; segmentation produces fixed-length windows from the continuous driving recording, and each window inherits the subject's year_of_birth as the regression target. 10s non-overlapping segments chosen to capture slower dynamics relevant to fatigue/mind wandering while providing independent samples.

### Classical Task 4: Driving with continuous segmentation (subject-level labID)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `legacy_labID`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | legacy_labID | 2043 | 0 | Subject 2043 |
  | legacy_labID | 2044 | 1 | Subject 2044 |
  | legacy_labID | 2048 | 2 | Subject 2048 |
  | legacy_labID | 2051 | 3 | Subject 2051 |
  | legacy_labID | 2055 | 4 | Subject 2055 |
  | legacy_labID | 2056 | 5 | Subject 2056 |
  | legacy_labID | 2061 | 6 | Subject 2061 |
  | legacy_labID | 2063 | 7 | Subject 2063 |
  | legacy_labID | 2064 | 8 | Subject 2064 |
  | legacy_labID | 2065 | 9 | Subject 2065 |
  | legacy_labID | 2066 | 10 | Subject 2066 |
  | legacy_labID | 2067 | 11 | Subject 2067 |
  | legacy_labID | 2068 | 12 | Subject 2068 |
  | legacy_labID | 2069 | 13 | Subject 2069 |
  | legacy_labID | 2070 | 14 | Subject 2070 |
  | legacy_labID | 2071 | 15 | Subject 2071 |
  | legacy_labID | 2072 | 16 | Subject 2072 |
  | legacy_labID | 2073 | 17 | Subject 2073 |
  | legacy_labID | 2074 | 18 | Subject 2074 |
  | legacy_labID | 2075 | 19 | Subject 2075 |
  | legacy_labID | 2076 | 20 | Subject 2076 |
- **Evidence**:
  - 10.1016/j.neuroimage.2019.116054 — EEG biometric identification using subject-level labels from continuous driving task data; 21-class subject identification paradigm
- **Notes**: 21-class subject identification from 4-second non-overlapping segments of continuous driving EEG. The legacy_labID field from participants.tsv provides subject-level labels. While not a classical cognitive task, subject identification from continuous naturalistic EEG is an established benchmark for evaluating individual discriminability of neural signatures. All 21 unique legacy_labID values (2043, 2044, 2048, 2051, 2055, 2056, 2061, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076) are mapped to sequential 0-20 labels. Segment length and overlap are inferred from standard EEG biometric literature practices for multi-class identification with limited subjects.

## Data Quality Notes

- Event structure table is completely empty in the file scan result, indicating no events were detected or parsed successfully during automated scanning. This conflicts with the original draft which described specific event IDs (4311, 4312, 2221, 2222, 4621, 4622) for lateral perturbations, thought probes, and audio conditions.
- The original draft referenced 60 subjects, but the file scan result and tasks sections indicate 21 subjects with complete year_of_birth and legacy_labID data. The metadata header has been updated to reflect 21 subjects and 21 files.
- Subject age and sex are completely missing from the info fields; only year_of_birth is available as a demographic variable.
- Device information is missing from the info fields.
- The tasks section has been completely replaced with segmentation-based tasks using info fields (year_of_birth, legacy_labID) rather than event-based tasks, reflecting the absence of detected events in the file scan.
- The group field is constant ('Normal') and provides no discriminability for classification purposes.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
