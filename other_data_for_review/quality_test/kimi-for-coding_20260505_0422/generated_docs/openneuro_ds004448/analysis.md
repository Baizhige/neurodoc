# BMI-HDEEG: High-Density EEG Dataset for Sensorimotor Rhythm-Based Brain-Machine Interface

**Dataset**: `ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 56 | **Files (Completed)**: 56 | **Channels**: 257 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset contains high-density EEG recordings from 56 healthy participants performing a sensorimotor rhythm (SMR)-based brain-machine interface (BCI) neurofeedback paradigm. Participants alternated between 6-second rest periods and 6-second right-hand motor imagery periods in a block design, with each trial beginning with a 1-second ready period and ending with an 8-second blank period. EEG was recorded using a 257-channel Magstim EGI GES400 amplifier with a Hydrocel Geodesic Sensor Net at 1000 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `d9c0d056e9e7c159f6d2d5862b91d24fe273b10b4c1243e793619666a0ba0768`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 277 | event | raw | Trial phase onset: trial start |
| `event_2` | 1723 | event | raw | Unknown trigger code - not documented in BIDS events.tsv |
| `event_3` | 1875 | event | raw | Unknown trigger code - not documented in BIDS events.tsv |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Ages range from 22 to 24 years based on participants_tsv_sample |
| `amplifier` | missing | Manufacturer: Magstim EGI; Model: GES400 (from eeg_json) |
| `cap` | missing | CapManufacturer: Magstim EGI; CapManufacturersModelName: Hydrocel Geodesic Sensor Net; EEGPlacementScheme: 10 percent system (from eeg_json) |
| `handedness` | complete | Values are 'right' and 'left' based on participants_tsv_sample; all shown samples are 'right' |
| `sex` | complete | Field labeled as 'gender' in participants_tsv with values 'male' and 'female' |

## Tasks

### Classical Task 1: Rest vs Right-Hand Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 6 s *, target_events = [`event_2`, `event_3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 | 0 | Rest period onset (6s rest phase) |
  | event_3 | 1 | Motor imagery period onset (6s right-hand imagery phase) |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Data descriptor defines SMR-ERD neurofeedback paradigm with alternating 6s rest and 6s motor imagery periods; binary classification task for BCI. Trial structure includes 1s ready period and 8s blank period. Only 'Trial start' (value=1) appears in BIDS events.tsv; event_2 and event_3 are embedded in EDF annotation stream as rest and motor imagery phase markers respectively.
- **Notes**: The event IDs event_2 and event_3 are not documented in BIDS events.tsv but are present in the raw EDF annotation stream per pre-scan discovery. Their semantic assignment (rest=0, motor imagery=1) follows from the paradigm description in the data descriptor: rest periods alternate with motor imagery periods in a block design. The epoch parameters are inferred from the documented 6-second duration of each phase.

### Potential Task 1: Trial-locked Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | age | Continuous age in years (range 19–58); directly used as regression target |
- **Evidence**:
  - participants.tsv — Age column complete for all 56 participants, range 19.0–58.0 years
  - Iwama et al. (2023) Sci Data 10:385 — Dataset descriptor confirming SMR-BCI paradigm with trial-based structure
- **Notes**: Segmentation approach divides continuous EEG into 6-second non-overlapping segments. Each segment inherits the participant's age from participants.tsv as the regression target. This enables prediction of subject age from neural signatures during motor imagery BCI performance without requiring event-locked class labels. The 6-second segment length is inferred from typical trial period durations in SMR-BCI paradigms as a conservative default; actual trial structures may vary by session.

### Potential Task 2: trial-locked segmentation with gender classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | gender | male → 0, female → 1 |
- **Evidence**:
- **Notes**: Segmentation-based task using 6-second epochs anchored by trial-start events. Gender labels are drawn from participants.tsv (native info field), yielding a subject-level binary classification. Highly imbalanced (49 male vs 7 female) but valid 2-class formulation. No kernel derivation needed — labels are pre-existing in BIDS metadata.

### Potential Task 3: Trial-locked Segmentation with Handedness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | handedness | right → 0, left → 1 |
- **Evidence**:
- **Notes**: Segmentation-based task using 6-second windows (matching the described task period) to predict handedness from EEG. The handedness field is a native participants.tsv column with binary values (right/left). Despite the motor imagery BCI paradigm, this task uses subject-level phenotype classification rather than event-locked trial classification. The small left-handed subset (N=56 total, predominantly right-handed) creates a class imbalance but preserves a valid 2-class prediction target. No kernel derivation needed — label is directly available from participants.tsv.

### Potential Task 4: Trial-Start Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 6 s *, target_events = [`event_1`]
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous age in years (19.0–58.0), used directly as regression target |
- **Evidence**:
  - participants.tsv — N=56 subjects with age range 19.0–58.0, complete coverage
  - events.tsv (sub-001_ses-01) — value=1 with instruction='Trial start' confirms event_1 maps to trial onset markers
  - Iwama et al. (2023) Sci Data 10:385 — dataset descriptor for BMI-HDEEG SMR-BCI paradigm
- **Notes**: Epochs locked to trial start (event_1, inferred from value=1 'Trial start' annotations) with 6-second windows matching the described task period. Age is drawn from participants.tsv as a native info field; no kernel derivation required. Each subject contributes multiple trial-epoch samples sharing the same age label, enabling subject-level age regression from SMR-BCI neural signatures.

## Data Quality Notes

- Event codes event_2 and event_3 are present in raw EDF annotation streams but are not documented in BIDS events.tsv files, creating a metadata-raw mismatch that requires pre-scan discovery to resolve.
- The participants_tsv_sample shows ages 22-24, which conflicts with the full participants.tsv age range of 19-58 years noted in task evidence; the sample may not be representative of the full dataset.
- Gender distribution is highly imbalanced (49 male vs 7 female), which may affect classification performance for gender-based tasks.
- Handedness field shows predominantly right-handed participants in the sample; the full dataset distribution is unknown but likely similarly skewed.
- Channel count of 257 includes the reference channel; actual EEG channels may be 256 depending on processing pipeline.
- High sampling rate of 1000 Hz with 256+ channels produces large file sizes that may require downsampling for practical analysis.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
