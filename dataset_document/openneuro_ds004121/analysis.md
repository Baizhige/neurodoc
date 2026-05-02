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
| `age` | missing | N/A |
| `sex` | missing | N/A |
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
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | year_of_birth | Continuous regression target: birth year 1976–1993. Approximate age at study ~21–38 years (circa 2014); single value per subject applied to all segments. |
- **Evidence**:
  - participants.tsv — year_of_birth column complete for all 21 subjects with range 1976–1993
- **Notes**: Segmentation-based approach for subject-level biomarker regression. No event structure required; 4-second segments with 50% overlap are standard for resting/baseline EEG feature extraction in subject-level prediction tasks. The year_of_birth field is native to participants.tsv (B3 archetype, raw meta level). Age is a fundamental demographic variable predictive of EEG spectral properties including alpha frequency slowing and theta power increases.

---

### Classical Task 2: Subject Age Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | year_of_birth | Binary classification: ≤1980 → class 0 (Older), >1980 → class 1 (Younger). Median split derived from participants.tsv year_of_birth column. |
- **Evidence**:
- **Notes**: Median split at 1980 derived from participants.tsv year_of_birth column (sample values: 1984, 1979, 1978, 1976, 1993, 1980, 1985). With N=21 subjects, this task is underpowered but technically valid. The group column is constant ('Normal') and provides no discriminability. Segmentation-based epoching is used to extract 4-second non-overlapping/overlapping windows for subject-level spectral feature extraction, standard for biomarker classification from continuous driving EEG. The binary split creates balanced classes if the birth year distribution permits.

---

### Classical Task 3: Driving with continuous segmentation (subject-level age)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | year_of_birth | Continuous regression target: birth year 1976–1993. Subject birth year from participants.tsv; age can be derived as (study_year - year_of_birth) if needed. Used as continuous subject-level target for regression across segmented driving epochs. |
- **Evidence**:
  - 10.1016/j.neuroimage.2019.116054 — Mega-analysis paper using continuous EEG with temporal overlap regression for cognitive aspects; supports segmentation-based regression on sustained naturalistic paradigms.
- **Notes**: Archetype C with native info column (year_of_birth). The kernel does not need to derive any channels; segmentation produces fixed-length windows from the continuous driving recording, and each window inherits the subject's year_of_birth as the regression target. 10s non-overlapping segments chosen to capture slower dynamics relevant to fatigue/mind wandering while providing independent samples.

---

### Classical Task 4: Driving with continuous segmentation (subject-level labID)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `legacy_labID`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | legacy_labID | 21-class classification: 21 unique legacy_labID values (2043, 2044, 2048, 2051, 2055, 2056, 2061, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076) mapped to sequential labels 0–20. Subject-level identification from continuous driving EEG segments. |
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
