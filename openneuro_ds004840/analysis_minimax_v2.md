# EEG/ECG/EMG During Music Therapy in ICU Burn Patients

**Dataset**: `openneuro_ds004840` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004840
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 68 | **Channels**: 10 | **Sampling Rate**: 1024 Hz

## Paradigm

Electrophysiological recordings (EEG, ECG, EMG) of adult burn patients in a clinical ICU environment during Music-Assisted Relaxation (MAR) therapy sessions. No event markers are present; EEG is continuous throughout the therapy recording. The study investigates physiological responses to music therapy as a pain and anxiety management intervention.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004840

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Music Therapy Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PRE` | 0 | Pre-intervention baseline (5 min resting state before music therapy) |
  | `MTI` | 1 | Music Therapy Intervention period (during MAR session, ~15 min average) |
  | `POST` | 2 | Post-intervention recovery (5 min resting state after music therapy) |
- **Super Meta Notes**: Derived from session timing metadata. The three phases (PRE/MTI/POST) are not present as event markers in the raw EEG data but are defined based on the experimental protocol timing documented in the study methods. Kernel step: Read session timing from dataset JSON/participants.tsv to determine start/end timestamps for each phase, then assign segment labels based on which phase each epoch falls within.
- **Evidence**:
  - DOI: 10.1038/s41598.024.73211-3 — Three-class classification of EEG/ECG/EMG epochs into PRE, MTI, and POST periods in 9 ICU burn patients during Music-Assisted Relaxation sessions
- **Kernel Notes**: Use sliding window segmentation (3s window, 50% overlap) on continuous EEG. Assign labels based on epoch timestamp relative to pre-defined session phase boundaries (5min PRE, ~15min MTI, 5min POST). ECG uses longer central windows (5min PRE, 15min MTI, 5min POST) per the paper but EEG epoching is as specified.

### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None
- **Notes**: No event markers. Use sliding-window segmentation. Condition labels (pre-therapy / during / post-therapy) may be available from session metadata or participants.tsv. (replaces Normal Task 1 from original analysis.md)


## Data Quality Notes

- No event markers; continuous EEG during music therapy.
- Clinical ICU environment - subject motion, medical equipment interference expected.
- Only 10 channels including ECG and EMG - limited spatial resolution for EEG analysis.

## References

- **Reference**: `Dataset of electrophysiological signals (EEG, ECG, EMG) during Music therapy with adult burn patients in the Intensive Care Unit.`
