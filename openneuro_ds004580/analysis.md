# Simon-conflict Task

**Dataset**: `openneuro_ds004580` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004580
**Category**: Sensory/Response | **Subjects**: 147 | **Files (Completed)**: 147 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**:

## Paradigm

Participants performed a Simon conflict task in which stimulus location (left/right) could be congruent or incongruent with the required response direction. S 1 marks visual cue onset and S 2 marks response onset; S 3 is a rare system marker. The dataset includes both Parkinson's disease (PD) patients and healthy controls, with demographic and clinical variables (AGE, GENDER, MOCA, UPDRS, GROUP, TYPE) available in participants.tsv for subject-level analyses.

## File Scan Result

> **Kernel SHA256**: `93010a60eba62473fd2ce055cffe5b0d615f2dbb6fc7cc29e883eabce9e67bce`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S  1` | 55922 | event | raw | Visual cue onset |
| `S  2` | 54800 | event | raw | Response onset |
| `S  3` | 1 | admin | raw | Unknown system marker |
| `S255` | 6 | admin | raw | Unknown system marker |
| `boundary` | 156 | admin | raw | Recording boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: PD vs Control classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `GROUP`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GROUP | PD | 0 | Parkinson's disease |
  | GROUP | Control | 1 | Healthy control |
- **Evidence**:
- **Notes**: Disease state classification using subject-level GROUP label from participants.tsv. Segmentation creates 2-second non-overlapping windows from continuous EEG recordings. Each window inherits the subject's group label. No event-based structure is used for discrimination; the task relies on distributed EEG signatures distinguishing PD from Control subjects across the continuous recording.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `AGE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | AGE | 56–81 (years) | Subject age from participants.tsv; complete for all 147 subjects |
- **Evidence**:
- **Notes**: Archetype B3: AGE is a native participants.tsv column requiring no kernel derivation. Segmentation-based epochs (2 s windows, no overlap) are used since no events discriminate age; each subject contributes many windows all labeled with the same subject age value, enabling subject-level regression from continuous EEG.

### Potential Task 3: MOCA score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `MOCA`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | MOCA | 17–29 (points) | Montreal Cognitive Assessment total score; higher indicates better cognitive function |
- **Evidence**:
  - participants.tsv — MOCA column complete for all 147 subjects, range 17-29, used as cognitive screening measure in PD research
  - dataset_description.json — Dataset supported by NIH grants for Parkinson's disease cognitive research
- **Notes**: Segmentation-based epochs with subject-level MOCA label. Each 2-second window from a subject's continuous EEG is labeled with that subject's MOCA score. Standard approach for cognitive score regression from resting/task EEG when trial-level labels are unavailable.

### Potential Task 4: UPDRS score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `UPDRS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | UPDRS | 10–28 (score) | Partial data: 99/147 subjects have UPDRS scores. Standard PD motor severity measure; higher scores indicate greater impairment. Missing values will require imputation or exclusion. |
- **Evidence**:
- **Notes**: Segmentation-based regression with subject-level label drawn from participants.tsv. Each 2-second window inherits the same UPDRS score for that subject. Incomplete data (48 missing) is noted as a modeling consideration.

### Potential Task 5: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `GENDER`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GENDER | M | 0 | Male |
  | GENDER | F | 1 | Female |
- **Evidence**:
  - participants.tsv — GENDER column complete (N=147) with values M/F; sample rows confirm male/female coding
  - dataset_description.json — describes 146 subjects (98 PD, 48 controls) with EEG recordings
- **Notes**: Segmentation-based approach required since no task events discriminate gender; 2-second non-overlapping windows standard for subject-level demographic classification from continuous EEG. GENDER is a native participants.tsv column, so Meta Level = raw.

### Potential Task 6: TYPE classification (PD subtype)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `TYPE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | TYPE | 0 | 0 | Control |
  | TYPE | 1 | 1 | PD |
- **Evidence**:
- **Notes**: Segmentation-based disease classification using the TYPE column from participants.tsv. TYPE encodes a binary label (0=Control, 1=PD) that is redundant with GROUP but provides a numeric encoding suitable for classification. The 2-second window length is a standard default for disease state classification from resting/continuous EEG segments; no task-specific epoch guidance was available in the dataset documentation.

## Data Quality Notes

- Event meanings in File Scan Result differ from original draft: S 1 is "Visual cue onset" (not "Congruent trial") and S 2 is "Response onset" (not "Incongruent trial"), indicating the event structure represents trial phase timing rather than condition labeling.
- S 3 has only 1 occurrence across all subjects, making it unsuitable for any task; previously described as "Rare/catch trial" but scan shows "Unknown system marker".
- Subject count discrepancy: original draft listed 30 subjects, but File Scan Result and Tasks indicate 147 subjects with complete data in participants.tsv.
- `subject_age` and `subject_sex` fields are missing from EEG metadata, but AGE and GENDER are complete in participants.tsv (147 subjects), requiring info-based label routing.
- UPDRS data is partial (99/147 subjects), requiring imputation or exclusion for regression tasks.
- `device` field is missing; equipment details unknown from scan metadata.
- 156 boundary markers present; segmentation-based approaches naturally handle these, but event-based analyses would need boundary-aware epoch rejection.
- TYPE and GROUP fields are redundant (both encode PD vs Control), providing duplicate classification targets.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
