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

### Primary Task 1: Three-class classification of music therapy phases (PRE/MTI/POST)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `PRE` | 0 | pre-intervention resting state |
  | `MTI` | 1 | music therapy intervention during |
  | `POST` | 2 | post-intervention recovery |
- **Super Meta Notes**: Labels are derived from experimental protocol timing - the three phases (PRE/MTI/POST) are not present as event markers in the raw data but are defined based on the session structure documented in the study methods (5 min PRE, ~15 min MTI, 5 min POST).
- **Evidence**:
  - DOI: 10.1038/s41598.024.73211.3 — This study analyzes EEG, ECG, and EMG recordings from 9 ICU burn patients during Music-Assisted Relaxation (MAR) sessions, comparing PRE (pre-intervention), MTI (during intervention), and POST (post-intervention) periods to identify statistically significant changes in brain oscillations, heart rate variability, and muscle tone.
- **Kernel Notes**: Segment continuous EEG into 3s epochs with 50% overlap. Derive phase labels (PRE/MTI/POST) from session timing metadata: PRE = first 5 minutes, MTI = middle therapy period (~15 min), POST = last 5 minutes. Map segments to corresponding phase labels for three-class classification.

### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None
- **Notes**: No event markers. Use sliding-window segmentation. Condition labels (pre-therapy / during / post-therapy) may be available from session metadata or participants.tsv.

## Data Quality Notes

- No event markers; continuous EEG during music therapy.
- Clinical ICU environment - subject motion, medical equipment interference expected.
- Only 10 channels including ECG and EMG - limited spatial resolution for EEG analysis.

## References

- **Reference**: `Dataset of electrophysiological signals (EEG, ECG, EMG) during Music therapy with adult burn patients in the Intensive Care Unit.`
