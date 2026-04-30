# Interval Timing Task

**Dataset**: `openneuro_ds004579` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004579
**Category**: Sensory/Response | **Subjects**: 139 | **Files (Completed)**: 139 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants performed an interval timing task where they estimated durations of different intervals. The dataset includes both Parkinson's disease (PD) patients and healthy controls, with participants completing cognitive assessments including the Montreal Cognitive Assessment (MoCA) and Unified Parkinson's Disease Rating Scale (UPDRS). EEG was recorded continuously during task performance using a 64-channel system at 512 Hz sampling rate. The study investigates neural oscillations, temporal processing mechanisms, and potential EEG biomarkers for Parkinson's disease and cognitive impairment.

## File Scan Result

> **Kernel SHA256**: `464b935071c0e7b1526544d59f3eb63f5c8cce7af296c6f01261de426c39747f`
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

### Potential Task 1: Parkinson's disease vs control classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `GROUP`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GROUP | Control | 0 | Healthy control participant |
  | GROUP | PD | 1 | Parkinson's disease participant |
- **Evidence**:
- **Notes**: Subject-level classification using the GROUP column from participants.tsv. Continuous EEG is segmented into 2-second non-overlapping windows; all windows from a given subject share the same label. The TYPE column (0/1) also encodes group membership and could be used as a cross-check, but GROUP is the primary categorical variable.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `AGE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | AGE | 56–80+ (years) | Participant chronological age; continuous numeric target for brain-age prediction. Values span 56 to 81+ years in PD and control cohort (N=139). |
- **Evidence**:
- **Notes**: Native info field from participants.tsv; no kernel derivation required. Standard 2-second segmentation windows with no overlap are commonly used in EEG-based brain-age prediction to extract local spectral features across continuous recordings. The AGE column is complete for all 139 subjects.

### Potential Task 3: MoCA cognitive score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `MOCA`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | MOCA | 10–30 (points) | Montreal Cognitive Assessment total score; lower values indicate greater cognitive impairment. Complete for all 139 subjects (94 PD, 45 Control). |
- **Evidence**:
  - participants.tsv — MOCA scores range 10-30, complete for all 139 subjects
  - dataset_description.json — Dataset includes Parkinson's disease and control subjects with cognitive assessments
  - README — 139 subjects: 94 PD, 45 controls; multiple cognitive tasks including IntervalTiming with EEG recording
- **Notes**: Segmentation-based regression with no event-locked structure. The 2-second segment length is inferred from typical cognitive state prediction paradigms; no trial timing constraints apply since the target (MOCA) is a static per-subject measure. The kernel must segment continuous EEG into non-overlapping 2-second windows and associate all windows from a subject with that subject's MOCA score.

### Potential Task 4: UPDRS motor severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `UPDRS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | UPDRS | 10–28 (score) | Unified Parkinson's Disease Rating Scale motor severity; higher = more severe |
- **Evidence**:
- **Notes**: Native info column from participants.tsv; no kernel derivation needed. Segmentation-based epochs (2 s non-overlapping windows) allow EEG biomarker discovery for continuous UPDRS prediction across the full recording. All 139 subjects have complete UPDRS scores (PD range 10–28, controls not scored or excluded).

### Potential Task 5: TYPE Disease Subtype Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `TYPE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | TYPE | 0 | 0 | Type 0 (e.g., tremor-dominant PD / OFF state) |
  | TYPE | 1 | 1 | Type 1 (e.g., PIGD PD / ON state) |
- **Evidence**:
  - participants.tsv — TYPE column complete for all 139 subjects with binary values {0, 1}; context from README indicates PD study with 94 PD patients and 45 controls, TYPE likely encodes PD motor subtype or medication state
- **Notes**: Segmentation-based task for subject-level disease subtype classification. The TYPE column is a native participants.tsv field with binary values. The exact clinical meaning of TYPE (e.g., tremor-dominant vs. postural-instability-gait-disorder, or ON vs. OFF medication) is not explicitly defined in available metadata, but the binary structure supports a 2-class classification paradigm. Segment length of 2s with no overlap chosen to extract multiple samples per subject's continuous recording for robust subject-level prediction.

### Potential Task 6: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `GENDER`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | GENDER | F | 0 | Female |
  | GENDER | M | 1 | Male |
- **Evidence**:
- **Notes**: Standard demographic classification task from resting/continuous EEG. Participants.tsv GENDER column is complete with M/F values. Segmentation approach divides continuous recordings into non-overlapping 2-second windows for subject-level gender prediction. No event alignment needed since labels are per-subject demographic variables.

### Potential Task 7: Continuous EEG Segmentation with PD Status
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
- **Notes**: Archetype C (segmentation + info-native) with Meta Level = raw. The GROUP field is a native participants.tsv column requiring no kernel derivation. Continuous 2-second non-overlapping segments are extracted from the full resting-state-style recording, with each segment inheriting the subject-level PD vs Control label. This leverages the full continuous EEG without requiring event-locked epochs, treating the interval timing task as a background cognitive state during which group-differentiating neural signatures may be detected.

## Data Quality Notes

- No event structure was detected in the file scan (empty Event Structure table), which conflicts with the interval timing task paradigm that should contain stimulus and response markers.
- The existing draft referenced BrainVision S-codes (S 1-S 7) and R 3 button press events, but these are not present in the authoritative File Scan Result.
- Subject count discrepancy: existing draft states 30 subjects, but the authoritative scan and tasks indicate 139 subjects (94 PD, 45 Control).
- Missing standard BIDS fields: `subject_age`, `subject_sex`, and `device` are not present; demographic data is instead available in custom info fields (`AGE`, `GENDER`).
- All info fields from participants.tsv (`GROUP`, `ID`, `EEG`, `AGE`, `GENDER`, `MOCA`, `UPDRS`, `TYPE`) are complete, enabling multiple subject-level prediction tasks.
- The `TYPE` field meaning is ambiguous — could encode PD motor subtype, medication state, or other clinical grouping; documentation does not explicitly define its clinical interpretation.
- UPDRS scores are only meaningful for PD patients; controls may have missing or non-applicable values despite field being marked complete.
- No known data quality issues for the segmentation-based tasks since they rely on continuous EEG without event-locking requirements.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
