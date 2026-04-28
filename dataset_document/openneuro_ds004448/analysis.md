# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 56 | **Files (Completed)**: 280 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants performed a sensorimotor rhythm-based brain-computer interface task using high-density scalp EEG. This is the fourth BMI-HDEEG dataset with a two-class (binary) motor imagery design (left hand vs. right hand). The experimental paradigm involved motor imagery training with neurofeedback components, where subjects alternated between performing motor imagery and relaxation/rest periods.

## File Scan Result

> **Kernel SHA256**: `d72f26fbb472eccd2b3469776dfe7698494f2e80185fb7afd92c7a5e7ba46828`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 277 | event | raw | Trial phase onset: Trial start |
| `event_2` | 1723 | event | raw | Unknown event code not present in BIDS events.tsv annotations |
| `event_3` | 1875 | event | raw | Unknown event code not present in BIDS events.tsv annotations |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 1.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–58.0 (years) | Subject chronological age from participants.tsv; all 56 subjects have complete age data |
- **Evidence**:
  - participants.tsv — N=56 subjects, age range 19.0–58.0 years, complete data for all subjects
  - dataset_description.json — BMI-HDEEG dataset with demographic metadata
- **Notes**: Segmentation-based regression task using uniform 2-second windows with 50% overlap. Each segment inherits the subject's chronological age as the regression target. No event structure required. Epoch parameters inferred from standard practice for subject-level demographic prediction from continuous EEG.

### Potential Task 2: Gender Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 1.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | male | 0 | male subject |
  | gender | female | 1 | female subject |
- **Evidence**:
- **Notes**: Standard 2-second segmentation with 50% overlap (overlap=1.0) for subject-level demographic prediction. Highly imbalanced class distribution (49 male vs 7 female, ~87.5% vs 12.5%); stratified sampling or class weighting recommended. Label drawn directly from participants.tsv 'gender' column (native info field, no kernel derivation needed).

## Data Quality Notes

- Event codes `event_2` (n=1723) and `event_3` (n=1875) are present in the raw data but have no corresponding annotations in BIDS events.tsv files, limiting interpretability of trial structure.
- The `device` info field is completely missing, preventing equipment-specific quality assessments or channel location verification.
- File count (280) exceeds subject count (56), indicating multiple files per subject (likely multiple runs/sessions); users should verify within-subject consistency before pooling.
- Gender classification task has severe class imbalance (~87.5% male vs ~12.5% female) which may bias model training without mitigation strategies.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
