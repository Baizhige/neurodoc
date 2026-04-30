# BCIT Speed Control

**Dataset**: `openneuro_ds004122` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004122
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 32 | **Channels**: 74 | **Sampling Rate**: 1024 Hz | **Manual Review**:

## Paradigm

A simulated driving task assessing driver fatigue and performance through a speed control manipulation: subjects drove under either manual speed control (maintaining speed without cruise control) or automated speed control (cruise control active), while also performing manual steering corrections for lateral vehicle perturbations. The study investigates how automation of one driving sub-task affects neural fatigue signatures.

## File Scan Result

> **Kernel SHA256**: `346e3a371a26942ac2dcdada07e4c7eacaac1795abc6836ff6e497cd309f904c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `correction_duration` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `perturbation_to_correction_latency` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `proactive_reactive_index` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `time_into_session` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `correction_duration`, `perturbation_to_correction_latency`, `proactive_reactive_index`, `time_into_session`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Subject Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | year_of_birth | 1975–1996 (year) | Continuous numeric; age can be derived as 2022 - year_of_birth if desired. Subject-level label applied to all segments from that subject. |
- **Evidence**:
  - participants.tsv — year_of_birth column present for all 32 subjects with values ranging from 1975 to 1996
- **Notes**: Segmentation-based regression with no event structure required. The label year_of_birth is a native participants.tsv column (archetype B3, Meta Level = raw). Standard 4-second non-overlapping windows are used for resting-state style subject-level prediction. The kernel simply reads the year_of_birth info field and assigns it to all epochs from that subject.

### Potential Task 2: Subject Age Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `year_of_birth`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | year_of_birth | ≤ median age | 0 | Younger group (age ≤ 34) |
  | year_of_birth | > median age | 1 | Older group (age > 34) |
- **Evidence**:
  - participants.tsv — year_of_birth complete for all 32 subjects; values range 1975-1996; median split yields balanced binary classification
- **Notes**: Kernel derivation step: Compute age = 2022 - year_of_birth (dataset collected ~2022 per curation timeline); apply median split across all subjects (median birth year ≈ 1988, corresponding to age ≈ 34); assign y=0 for below-median (younger), y=1 for above-median (older); broadcast as subject-level label for all EEG segments. Since all subjects have group=Normal, year_of_birth is the only viable demographic discriminator in participants.tsv.

## Data Quality Notes

- Subject count discrepancy: existing draft states 63 subjects but File Scan Result and Tasks indicate 32 subjects with complete year_of_birth data
- All 32 subjects have group=Normal with no clinical/control contrast available
- subject_age and subject_sex fields are missing for all subjects; only year_of_birth is available for demographic prediction
- device field is missing; equipment details (74-channel BioSemi ActiveTwo) come from prior documentation, not from scanned metadata
- Event structure table in File Scan Result is empty; no events were detected during scan despite prior documentation listing extensive event codes
- MISC channels present in raw files (correction_duration, perturbation_to_correction_latency, proactive_reactive_index, time_into_session) require verification of role and units
- Speed control condition (manual vs. automated) referenced in paradigm description is not present in scanned info fields; may require session-level metadata extraction

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
