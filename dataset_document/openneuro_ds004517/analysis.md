# EEG recordings for semantic decoding of imagined animals and tools during auditory imagery task

**Dataset**: `openneuro_ds004517` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004517
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 32 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants imagined animals and tools in response to auditory cues while EEG was recorded. Each trial consisted of an audio cue followed by a sustained auditory imagery period (~5 s). The study investigates EEG correlates of semantic imagery for living (animals) vs non-living (tools) concepts in the auditory domain.

## File Scan Result

> **Kernel SHA256**: `2e62a99208c7692bf48a4420df4df3ed099d09ca2006f9e01f9ecc317594e31b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_4223` | 6 | admin | raw | Unknown system marker or acquisition artifact (not documented in events.tsv or events.json) |
| `event_4351` | 11872 | event | raw | Trial phase onset: blank_white_screen |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 5 s *, overlap = 0 s *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
  - participants.tsv — age column complete for all 7 subjects (range 25–44 years)
  - README — "This dataset contains electroencephalography (EEG) signals recorded from 7 participants"
  - eeg.json — EpochLength = 5 s, matching the 5-second auditory imagery task structure
- **Notes**: Segmentation-based subject trait regression. No event structure needed; 5-second non-overlapping segments align with the dataset's native epoch length. Age is a native participants.tsv column (B3 archetype, raw meta level).

### Potential Task 2: sex classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | Female -> 0; Male -> 1 |
- **Evidence**:
- **Notes**: Subject-level binary classification using 5-second non-overlapping/overlapping segments. The eeg.json specifies EpochLength=5, matching the auditory imagery task duration. Segmentation is used because there is no event-based trial structure suitable for subject trait prediction; the kernel assigns the same subject-level label (from participants.tsv) to all segments belonging to that subject. overlap=0.5 is a SKILL default for segmentation-based tasks when not otherwise specified.

## Data Quality Notes

- Subject count discrepancy: metadata indicates 20 subjects, but Tasks section and participants.tsv evidence reference only 7 subjects with complete age/sex data.
- Device field is missing across all files, limiting hardware reproducibility.
- Event_4351 meaning in File Scan Result ("blank_white_screen") conflicts with prior draft interpretation ("sustained auditory imagery task marker"); actual semantic condition labels (animal vs tool) are not present in scanned event structure.
- Event_4223 is undocumented in BIDS events files and appears only 6 times across entire dataset, suggesting rare system artifacts or session boundaries.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
