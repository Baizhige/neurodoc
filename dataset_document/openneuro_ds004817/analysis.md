# EEG-attention-rsvp-exp2

**Dataset**: `openneuro_ds004817` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004817
**Category**: Sensory/Response | **Subjects**: 20 | **Files (Completed)**: 20 | **Manual Review**:
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

A Rapid Serial Visual Presentation (RSVP) task (Experiment 2) investigating the neural dynamics of prioritizing task-relevant information, using stimuli consisting of small objects superimposed on large letters. Participants performed target detection in rapid streams. Experiment 2 is a companion to Experiment 1 (ds004816) with different stimulus configurations (objects on letters rather than letters on objects).

## File Scan Result

> **Kernel SHA256**: `3a82a14f640b20e68beb91e412e3f7f183abfdb657e0d2a4b15b4857043dc177`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 138274 | event | raw | Stimulus presentation marker (alternating component of RSVP stimulus stream) |
| `E 2` | 138274 | event | raw | Stimulus presentation marker (alternating component of RSVP stimulus stream) |
| `E 3` | 3842 | event | raw | Trial phase onset: stream/block start |
| `boundary` | 20 | admin | raw | Recording segment boundary (New Segment marker) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Subject age regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19–36 (years) | Subject chronological age from participants.tsv; all 20 subjects have complete age data |
- **Evidence**:
  - Grootswagers et al. (2021) — Dataset README and participants.tsv document age range 19–36 years for all 20 subjects
- **Notes**: Segmentation-based epochs (2s windows, 50% overlap) are used because age is a subject-level variable with no trial-level event structure. The kernel simply reads the native `age` column from participants.tsv and assigns it to all epochs from that subject. No derivation is needed.

### Potential Task 2: Subject handedness classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | R | 0 | Right-handed |
  | handedness | L | 1 | Left-handed |
- **Evidence**:
  - participants.tsv — Handedness column complete for all 20 subjects (R=17, L=3)
- **Notes**: Segmentation-based epochs with 2s windows and 50% overlap used because handedness is a subject-level demographic variable with no event-based structure. All epochs from a given subject receive the same label. Imbalanced 2-class problem (17:3 ratio).

### Potential Task 3: Subject gender classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | F | 0 | Female |
  | gender | M | 1 | Male |
- **Evidence**:
  - participants.tsv — gender column complete for all 20 subjects (F=17, M=3)
  - dataset_description.json — confirms dataset is EEG-attention-rsvp-exp2 with 20 subjects
- **Notes**: Highly imbalanced 2-class problem (17F/3M). Segmentation-based epochs required because gender is a subject-level label with no discriminating event structure. All epochs from a given subject share the same label. SKILL default segmentation parameters used (2s windows, 50% overlap) as no event-based structure exists for this subject-level prediction task.

### Potential Task 4: RSVP Continuous EEG Segmentation with Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 19.0–36.0 (years) | Subject chronological age from participants.tsv; predicted from 2-second non-overlapping sliding windows of continuous RSVP EEG |
- **Evidence**:
- **Notes**: Archetype C segmentation formulation of age prediction. Uses fixed 2-second windows with 50% overlap across the entire continuous RSVP recording, rather than event-locked epochs. The kernel must segment the raw EEG without event alignment, assigning the same subject-level age label to all windows from a given recording. This provides a segmentation-focused alternative to event-based or trial-averaged approaches for subject-level biomarker prediction.

## Data Quality Notes

- Subject count discrepancy: existing draft lists 40 subjects but File Scan Result and Tasks sections indicate 20 subjects (age range 19–36, 17R/3L handedness, 17F/3M gender).
- Device metadata is missing for all files.
- Event counts for E 1 and E 2 are identical (138274 each), consistent with alternating RSVP stimulus components.
- E 3 events (3842) represent stream/block starts, substantially fewer than stimulus presentation markers.
- Only 20 boundary events total across all files suggests minimal recording interruptions.
- The Tasks section contains only segmentation-based subject-level prediction tasks (age, handedness, gender) and no event-based RSVP classification tasks despite the RSVP paradigm description.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
