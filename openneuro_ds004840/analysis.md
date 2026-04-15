# EEG/ECG/EMG During Music Therapy in ICU Burn Patients

**Dataset**: `openneuro_ds004840` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004840
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 68 | **Channels**: 10 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Electrophysiological recordings (EEG, ECG, EMG) of adult burn patients in a clinical ICU environment during Music-Assisted Relaxation (MAR) therapy sessions. No event markers are present in the raw EEG data; however, phase events (PRE/MTI/POST) are derived from protocol timing metadata and mapped as events in the dataset. The study investigates physiological responses to music therapy as a pain and anxiety management intervention in ICU patients.

## File Scan Result

> **Kernel SHA256**: `69c061b4eadbd047a04d1d44739863d381a72d22ce257a30157daece15d69c4a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `phase:MTI` | 65 | event | raw | Music Therapy Intervention period (during MAR session, ~15 min average) |
| `phase:POST` | 42 | event | raw | Post-intervention recovery (5 min resting state after music therapy) |
| `phase:PRE` | 68 | event | raw | Pre-intervention baseline (5 min resting state before music therapy) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Music Therapy Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `phase:PRE` | 0 | Pre-intervention baseline (5 min resting state before music therapy) |
  | `phase:MTI` | 1 | Music Therapy Intervention period (during MAR session, ~15 min average) |
  | `phase:POST` | 2 | Post-intervention recovery (5 min resting state after music therapy) |
- **Evidence**:
  - DOI: 10.1038/s41598-024-73211-3 — Three-class classification of EEG/ECG/EMG epochs into PRE, MTI, and POST periods in 9 ICU burn patients during Music-Assisted Relaxation sessions
- **Super Meta Notes**: Phase boundaries (PRE/MTI/POST) are derived from protocol timing metadata and mapped to event markers in the dataset. Kernel must align epoch timestamps to phase event boundaries using session timing information. Event counts for validation: phase:PRE=68, phase:MTI=65, phase:POST=42.
- **Kernel Notes**: Use sliding-window segmentation (3s window, 50% overlap) on continuous EEG. Assign labels by mapping epoch timestamps to the nearest phase event boundary. Clinical ICU environment—expect reduced signal quality from medical equipment and patient motion. ECG channels available for heart rate variability analysis alongside EEG.

### Potential Task 1: Continuous Monitoring Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: None (unlabeled segmentation)
- **Notes**: Unlabeled continuous segmentation task using shorter 2s windows for exploratory physiological monitoring or feature extraction. No target labels required; suitable for unsupervised feature analysis, artifact detection, or dimensionality reduction benchmarking on clinical ICU data.