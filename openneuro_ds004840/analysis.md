# EEG/ECG/EMG During Music Therapy in ICU Burn Patients

**Dataset**: `openneuro_ds004840` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004840
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 68 | **Channels**: 10 | **Sampling Rate**: 1024 Hz

## Paradigm

Electrophysiological recordings (EEG, ECG, EMG) of adult burn patients in a clinical ICU environment during Music-Assisted Relaxation (MAR) therapy sessions. No event markers are present; EEG is continuous throughout the therapy recording. The study investigates physiological responses to music therapy as a pain and anxiety management intervention.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Music Therapy Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PRE` | 0 | Pre-intervention baseline (5 min resting state before music therapy) |
  | `MTI` | 1 | Music Therapy Intervention period (during MAR session, ~15 min average) |
  | `POST` | 2 | Post-intervention recovery (5 min resting state after music therapy) |
- **Super Meta Notes**: Derived from session timing metadata. The three phases (PRE/MTI/POST) are not present as event markers in the raw EEG data but are defined based on the experimental protocol timing documented in the study methods. Kernel step: Read session timing from dataset JSON/participants.tsv to determine start/end timestamps for each phase, then assign segment labels based on which phase each epoch falls within.
- **Evidence**:
  - DOI: 10.1038/s41598-024-73211-3 — Three-class classification of EEG/ECG/EMG epochs into PRE, MTI, and POST periods in 9 ICU burn patients during Music-Assisted Relaxation sessions
- **Kernel Notes**: Use sliding window segmentation (3s window, 50% overlap) on continuous EEG. Assign labels based on epoch timestamp relative to pre-defined session phase boundaries (5min PRE, ~15min MTI, 5min POST). ECG uses longer central windows (5min PRE, 15min MTI, 5min POST) per the paper but EEG epoching is as specified.

### Potential Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: None
- **Notes**: No event markers. Use sliding-window segmentation. Condition labels (pre-therapy / during / post-therapy) may be available from session metadata or participants.tsv. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- No event markers; continuous EEG during music therapy.
- Clinical ICU environment - subject motion, medical equipment interference expected.
- Only 10 channels including ECG and EMG - limited spatial resolution for EEG analysis.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review