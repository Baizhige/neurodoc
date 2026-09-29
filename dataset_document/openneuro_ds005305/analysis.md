# EEG Resting-State Microstates and Executive Functions

**Dataset**: `openneuro_ds005305` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005305
**Category**: High-level Mental | **Subjects**: 165 | **Files (Completed)**: 165 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**: Pending

## Paradigm

Resting-state EEG microstates were recorded to correlate spontaneous brain dynamics with performance on a nine-task battery of executive functions (dual N-back, Stroop, task-switching, etc.). Each file contains alternating eyes-closed (`RS_EC`) and eyes-open (`RS_EO`) resting blocks totaling 825 and 660 events respectively across 165 subjects. The study investigates whether EEG microstate metrics predict individual differences in executive function composite scores derived from behavioral measures.

## File Scan Result

> **Kernel SHA256**: `d1dd7541178bf0a18c2b351b152df0d8da05a5ea789dadc7fd4a1d499becd980`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RS_EC` | 825 | event | raw | Eyes-closed resting state block onset |
| `RS_EO` | 660 | event | raw | Eyes-open resting state block onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Executive Function Prediction from Resting-State Microstates (regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: Event-to-label mapping table below.
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | `RS_EC` | predictor block | Eyes-closed resting block for microstate extraction (predictor, not target) |
  | `RS_EO` | predictor block | Eyes-open resting block for microstate extraction (predictor, not target) |
  | `RS_EC` / `RS_EO` | executive_function_score | Super meta target from participants.tsv; event IDs mark epochs used for microstate feature extraction (Needs verification) |

- **Notes**: Microstate metrics (duration, coverage, occurrence) extracted from resting-state EEG blocks serve as predictors for executive function composite scores derived from a nine-task battery. Super meta labels stored in participants.tsv.

 | Event | y | Meaning |
 |-------|---|----------|
 | `RS_EC` | predictor | Eyes-closed resting block for microstate extraction |
 | `RS_EO` | predictor | Eyes-open resting block for microstate extraction |
 | *stim* | executive_function_score | Composite executive function score (continuous) |

- **Evidence**: DOI: `10.1016/j.cortex.2024.05.019` (Investigating the relationship between resting-state EEG microstates and executive functions: A null finding)
- **Kernel Notes**: Resting-state blocks (30–60 s each) segmented into 2-second sliding windows (50% overlap) to extract microstate features per window. Executive function composite score is a super meta target from participants.tsv—not derived from EEG events. Epoch extraction uses RS_EC/RS_EO onsets; boundary and key press events excluded as admin markers. Consider memory-efficient batching given ~74,500–89,100 total potential epochs across 165 subjects. Class imbalance is not applicable for regression; stratification relevant only for train/test splits.

---

### Potential Task 2: Eyes Open vs Eyes Closed (binary classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Event-to-label mapping table below.
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `RS_EC` | 0 | Eyes-closed resting state |
  | `RS_EO` | 1 | Eyes-open resting state |

- **Notes**: Binary classification of resting-state condition from EEG microstate dynamics. Slight class imbalance: RS_EC (825) vs RS_EO (660) (~55/45%). Paradigm plausibility supports this task; not explicitly performed in primary reference but consistent with experimental design.

 | Event | y | Meaning |
 |-------|---|----------|
 | `RS_EC` | 0 | Eyes-closed resting state |
 | `RS_EO` | 1 | Eyes-open resting state |

- **Evidence**: DOI: `10.1016/j.cortex.2024.05.019` (partial support—paradigm includes RS_EC/RS_EO alternating blocks; binary classification not explicitly performed)
- **Kernel Notes**: Each resting block is 30–60 s; 2-second sliding windows with 50% overlap yield ~30–60 epochs per block. Exclude `boundary` (165) and all key press events (admin markers). Class imbalance (~55/45) may require stratified sampling during training. Total potential epochs: RS_EC ~41,250–49,500; RS_EO ~33,000–39,600. High epoch count may require memory-efficient batching across 165 subjects with 64 channels at 512 Hz.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
