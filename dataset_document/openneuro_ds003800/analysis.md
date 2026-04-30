# Auditory Gamma Entrainment

**Dataset**: `openneuro_ds003800` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003800
**Category**: Sensory/Response | **Subjects**: 8 | **Files (Completed)**: 24 | **Manual Review**:
**Channels**: 19 | **Sampling Rate**: 250 Hz

## Paradigm

Elderly participants with dementia received 40 Hz amplitude-modulated (AM) auditory stimulation to induce gamma-band entrainment of brain oscillations. The paradigm alternated between active 40 Hz AM stimulation (Stimulus) periods and quiet rest periods. The study investigates whether auditory gamma entrainment can modulate neural oscillations in a dementia population, potentially as a therapeutic intervention. EEG was recorded using a standard 10-20 system.

## File Scan Result

> **Kernel SHA256**: `acb182177b3fe8a79612be884d45c0ccf55fa8409970c03de87bf032381bb0fb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Rest` | 65 | event | raw | Trial phase onset: rest |
| `Stimulus` | 78 | event | raw | Trial phase onset: stimulus |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Stimulus vs Rest Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`Rest`, `Stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Rest | 0 | Trial phase onset: rest |
  | Stimulus | 1 | Trial phase onset: stimulus |
- **Evidence**:
  - 10.18178/ijpmbs.13.1.14-18 — Binary classification of 40 Hz AM auditory stimulation periods versus quiet rest periods. Stimulus trials are 40s duration (event code 2), rest trials are 20s duration (event code 1). Six stimulus and five rest periods per session alternating throughout the 340s recording.
  - sub-001_task-AuditoryGammaEntrainment_events.json — Explicitly maps value '1' to 'Rest' and value '2' to 'Stimulus' in the Levels field under the value column.
  - sub-001_task-AuditoryGammaEntrainment_events.tsv — Shows alternating 20s Rest/40s Stimulus blocks with consistent event codes across all trials.
- **Notes**: Long-event epoching captures full stimulation/rest periods. Note that Rest epochs are only 20s duration while tmax=40s; this will result in shorter effective epochs for Rest trials. The tmax=40s is set to accommodate the longer Stimulus periods per the reference specification.

### Potential Task 1: MMSE Score Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MMSE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | MMSE | 19–28 (score) | Mini-Mental State Examination; partial coverage (12/13 participants); higher scores indicate better cognitive function; standard dementia screening tool |
- **Evidence**:
- **Notes**: 10-second non-overlapping segmentation chosen as standard for subject-level regression from continuous EEG, allowing multiple samples per subject to be associated with the same MMSE score. MMSE values are drawn from participants.tsv as a native info field (archetype B3). No event-based alignment is used; the model must learn to predict a per-subject clinical score from arbitrary EEG segments.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | Age | 65–89 (years) | Continuous age of elderly participants with dementia; complete for all 13 subjects |
- **Evidence**:
- **Notes**: Subject-level regression using 10-second non-overlapping segments. Age is a native participants.tsv column (B3 archetype, Meta Level = raw). Segmentation provides sufficient samples per subject for spectral feature extraction relevant to brain-age prediction. The 10s window length was inferred as a standard choice for subject-level regression tasks; overlap was set to 0.0 as no specific overlap was indicated.

### Potential Task 3: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | F | 0 | Female |
  | Gender | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level binary classification using 10-second non-overlapping windows from the continuous EEG recordings. Each window inherits the participant's Gender label from participants.tsv. The 10-second segment length is chosen to provide sufficient data for stable feature extraction while yielding multiple samples per subject (34 windows per 340s recording). This is a B3 archetype task using a native participants.tsv column as the label source.

### Potential Task 4: Resting-State Eyes-Open Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MMSE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | MMSE | 19–28 (score) | Mini-Mental State Examination score; missing for 1/13 subjects (sub-06 per README, though participants.tsv shows sub-06 has MMSE=23; actual missing rest recordings for sub-06 and sub-13) |
- **Evidence**:
- **Notes**: Standard resting-state EEG segmentation approach: 60-second eyes-open recordings are divided into 10-second non-overlapping windows, yielding up to 6 segments per subject. MMSE is used as the regression target since Group field is entirely missing. The task-Rest recordings contain no events, so segmentation is required. Meta Level is raw because MMSE is a native participants.tsv column.

## Data Quality Notes

- Metadata conflict: File Scan Result indicates 13 subjects with complete Age/Gender data, but dataset header shows only 8 subjects with 24 completed files. The Tasks section references 13 participants in participants.tsv, suggesting some subjects may lack EEG recordings or have incomplete data.
- Missing standard BIDS fields: `subject_age` and `subject_sex` are missing at the EEG metadata level, though `Age` and `Gender` are available via participants.tsv (archetype B3).
- `Group` field is entirely missing, preventing group-level analyses (e.g., dementia severity stratification).
- `MMSE` coverage is partial (12/13), with one missing value; however, README and participants.tsv disagree on which subject is missing MMSE data.
- Rest recordings are missing for sub-06 and sub-13, affecting Potential Task 4 and reducing effective sample size for rest-based analyses.
- `device` field is missing, limiting reproducibility of equipment specifications.
- Rest epochs are only 20s duration while Stimulus epochs are 40s; the fixed tmax=40s in Classical Task 1 will produce shorter effective Rest epochs, which may affect classification performance.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
