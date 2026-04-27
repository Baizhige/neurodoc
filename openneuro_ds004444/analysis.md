# The BMI-HDEEG dataset 1

**Dataset**: `openneuro_ds004444` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004444
**Category**: Action/Output | **Subjects**: 465 | **Files (Completed)**: 465 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Brain-computer interfacing task based on sensorimotor rhythms (SMR) using high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the first of four BMI-HDEEG datasets, enabling classification of motor imagery across all four classes.

## File Scan Result

> **Kernel SHA256**: `7099a55557381396528266b6d303f832d46976f4878c0906ade12f39be7104ff`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 18.0–27.0 (years) | Subject age from participants.tsv; complete for all 30 participants |
- **Evidence**:
  - participants.tsv — N=30 subjects with ages 18.0–27.0 (sample: 22, 23, 24); complete coverage
- **Notes**: Segmentation-based regression task using 4-second non-overlapping windows (50% overlap) from continuous EEG. No event structure required. Age is a native participants.tsv column, so Meta Level = raw. The kernel only needs to read the pre-existing `age` field from participants.tsv and assign the same label to all epochs belonging to a given subject.

### Classical Task 2: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | female | 0 | Female subject |
  | gender | male | 1 | Male subject |
- **Evidence**:
  - participants.tsv — N=30 subjects with gender column: 5 female, 25 male (complete, categorical)
- **Notes**: Subject-level demographic classification using 4-second sliding windows with 50% overlap. Class imbalance is severe (1:5 ratio) which should be noted for model training. The label is drawn from participants.tsv native info field, requiring no kernel derivation.

### Classical Task 3: Handedness Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | left | 0 | left-handed |
  | handedness | right | 1 | right-handed |
- **Evidence**:
- **Notes**: Subject-level biomarker classification using 4-second non-overlapping segments of continuous EEG. The handedness label is drawn from participants.tsv, a native BIDS info field. Epoch parameters are inferred from standard continuous EEG segmentation practice (4s windows, 50% overlap) as no trial structure is used. Highly imbalanced classes (1 left-handed vs 29 right-handed subjects) but valid 2-class problem.

## Data Quality Notes

- No event markers detected in file scan despite motor imagery paradigm requiring cue-based events.
- Task definitions rely on segmentation-based approaches rather than event-locked epochs, which conflicts with the described SMR-BCI motor imagery paradigm.
- Subject count discrepancy: metadata claims 465 subjects but task evidence references only 30 participants in participants.tsv.
- `device` field is completely missing from info scan, limiting equipment provenance tracking.
- Event structure table is empty; no event counts or IDs available to validate motor imagery class distributions.
- Severe class imbalance noted in demographic tasks (gender: 1:5 ratio; handedness: 1:29 ratio).

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
