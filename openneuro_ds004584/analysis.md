# Rest Eyes Open (Parkinson's Disease)

**Dataset**: `openneuro_ds004584` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004584
**Category**: Biological State | **Subjects**: 149 | **Files (Completed)**: 149 | **Channels**: 63 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

Resting-state EEG was collected from 149 participants (100 with Parkinson's disease and 49 healthy controls) who sat quietly with eyes open for approximately two minutes. The study characterizes spontaneous neural oscillatory patterns to differentiate PD patients from controls. No active task was required; participants fixated on a cross and remained still.

## File Scan Result

> **Kernel SHA256**: `893b33a9e023d1f9d733bfdcee8853ce439ca4ca0056a9afb09c50a7a0106c61`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 149 | admin | raw | Recording boundary marker at file start |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Cognitive Impairment Classification (MoCA)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MOCA`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | MOCA | >= 26 | 0 | cognitively_normal |
  | MOCA | < 26 | 1 | cognitive_impairment |
- **Evidence**:
  - 10.21203/rs.3.rs-2666578/v1 — Uses this dataset (149 participants, 100 PD + 49 controls) to classify cognitive impairment from resting-state EEG using MoCA threshold 26; achieves ~80% accuracy with spectral features.
  - 10.1038/s41531-023-00602-0 — Uses this dataset with LPC coefficients for cognitive impairment classification; applies sliding-window segmentation to continuous ~2-3 min resting-state recordings.
- **Notes**: Segmentation-based approach on continuous resting-state eyes-open EEG. MoCA scores are binarized at threshold 26 (standard clinical cutoff for normal cognition). The 4s window length and 0.5 overlap are inferred from dataset documentation and typical resting-state segmentation practices; papers mention sliding-window segmentation but do not specify exact parameters.

### Potential Task 1: Parkinson's disease vs healthy control classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `GROUP`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GROUP | PD | 0 | Parkinson's disease patient |
  | GROUP | Control | 1 | Healthy control subject |
- **Evidence**:
- **Notes**: Segmentation-based classification using 4-second non-overlapping windows (50% overlap) from resting-state eyes-open EEG. The GROUP column in participants.tsv provides the disease-state label with complete coverage: 100 PD patients and 49 healthy controls. Since GROUP is a native participants.tsv column, Meta Level is raw. Epoch parameters are inferred from standard resting-state analysis conventions as no dataset-specific epoching reference was found.

### Potential Task 2: UPDRS motor severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `UPDRS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | UPDRS | 0–55 (score) | Partial availability (100/149); controls have structural missing values (healthy, no PD symptoms). Kernel must handle NaN labels. Higher scores indicate greater motor impairment. |
- **Evidence**:
- **Notes**: Standard resting-state eyes-open segmentation with 4-second non-overlapping windows (50% overlap). UPDRS is a native participants.tsv column (dtype=numeric, partial completeness), requiring no kernel derivation. The structural missingness in controls (49 subjects) must be handled by the kernel—common approaches include training on PD patients only or imputing control scores as 0.

### Potential Task 3: MoCA score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MOCA`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | MOCA | 0–30 (points) | Montreal Cognitive Assessment total score; complete for all 149 participants; higher scores indicate better cognitive function |
- **Evidence**:
  - 10.1038/s41531-023-00602-0 — Reference mentions regression tasks alongside classification; MoCA is continuous numeric (0-30) in participants.tsv, complete for all 149 participants
- **Notes**: Resting-state eyes-open EEG segmentation with 4-second non-overlapping windows (50% overlap inferred from classification variant). Predicts raw MoCA score as continuous regression target, preserving full granularity versus binarized cognitive impairment classification. Natural extension of classical cognitive impairment task using identical epoching parameters.

### Potential Task 4: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `AGE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | AGE | 56–81 (years) | Continuous age from participants.tsv; complete for all 149 subjects |
- **Evidence**:
- **Notes**: Standard resting-state segmentation for age prediction. The AGE column is a native participants.tsv field with complete coverage across all 149 subjects. Segmentation parameters follow common resting-state EEG preprocessing conventions (4-second non-overlapping or partially overlapping windows).

### Potential Task 5: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `GENDER`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GENDER | M | 0 | Male |
  | GENDER | F | 1 | Female |
- **Evidence**:
- **Notes**: Resting-state eyes-open EEG segmented into 4-second non-overlapping windows (50% overlap) for binary gender classification. The GENDER field is complete for all 149 participants (100 PD, 49 Control). Class balance should be checked given potential sex imbalance in the PD cohort. This task may serve as a biological state marker or confound control variable for other analyses. Epoch parameters inferred from standard resting-state segmentation practices; no specific reference found for gender classification in this dataset.

### Potential Task 6: PD subtype classification (TYPE)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `TYPE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | TYPE | 0 | 0 | PD subtype 0 (likely PIGD) |
  | TYPE | 1 | 1 | PD subtype 1 (likely tremor-dominant) |
- **Evidence**:
  - participants.tsv — TYPE column complete with values [0, 1]; numeric encoding for PD subtype stratification
  - README — Dataset includes 100 PD patients and 49 controls; resting-state eyes-open EEG collected
  - doi:10.1101/2022.07.26.22278079 — PD subtype classification common in Parkinson's disease research
- **Notes**: Standard resting-state segmentation with 4-second non-overlapping windows. TYPE values 0/1 encode PD motor subtypes (tremor-dominant vs. postural-instability-gait-disorder), a well-established stratification in PD research. The coding scheme (0 vs. 1) requires verification against the original paper. Only PD subjects have meaningful TYPE labels; controls may need exclusion or could be assigned a separate class if the analysis warrants. All parameters marked with * are inferred from standard resting-state EEG analysis conventions.

### Potential Task 7: cognitive impairment 3-class (MOCA tertiles)
- **Task Type**: info + classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MOCA`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | MOCA | 26–30 | 0 | normal (MOCA 26–30) |
  | MOCA | 18–25 | 1 | mild impairment (MOCA 18–25) |
  | MOCA | <18 | 2 | severe impairment (MOCA <18) |
- **Evidence**:
  - participants.tsv column MOCA — dtype=numeric, completeness=complete, sample=[19, 17, 26]; source for kernel derivation of ordinal severity scale
- **Notes**: Derived from native participants.tsv MOCA column via kernel that applies clinical cutoffs to create a 3-level severity scale (normal/mild/severe). Rewritten from misc route to info route since MOCA is a native participants.tsv column. The y values encode ordinal severity but are treated as class indices for classification. Segmentation parameters match the classical resting-state task (4-second non-overlapping or overlapping windows).

## Data Quality Notes

- Standard BIDS fields `subject_age` and `subject_sex` are missing; age and gender information is instead available as `AGE` and `GENDER` in the info fields with complete coverage.
- Device information is missing from standard BIDS fields; no equipment metadata is available in the scan.
- UPDRS scores have partial availability (100/149 subjects) due to structural missingness in healthy controls who do not have Parkinson's disease symptoms.
- Event structure contains only `boundary` markers (admin type) with no task-related events, consistent with resting-state paradigm.
- TYPE field encoding (0 vs. 1) for PD subtypes requires verification against original publication to confirm mapping to tremor-dominant vs. PIGD subtypes.
- All epoch segmentation parameters (4 s window, 0.5 overlap) are inferred from standard resting-state conventions rather than explicitly documented in dataset materials.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
