# Multiple Object Monitoring EEG

**Dataset**: `openneuro_ds006768` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006768
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 210 | **Channels**: 65 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Subjects completed a Multiple Object Monitoring (MOM) task requiring sustained visual attention to track multiple moving objects simultaneously. In each trial, a subset of objects is designated as targets at the start, then all objects move during a tracking period, and subjects report which objects were targets. EEG captures neural correlates of visual attention load and tracking accuracy. Events mark trial onset, target designation, and distractor appearances.

## File Scan Result

> **Kernel SHA256**: `b6b038c288020932ef1894336a754f1696681df732c914559be3feb92d3cc719`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### MISC Label Summary
No MISC labels identified in this dataset.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Target vs. Distractor Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["target", "distractor"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `target` | 1 | Target object to be tracked |
| `distractor` | 2 | Distractor object |

- **Evidence**: DOI: https://doi.org/10.1101/2025.07.10.663816 (Using EEG to Detect Lapses in Sustained Attention to Moving Stimuli)
- **Kernel Notes**: Event duration classified as "short" (<2s) confirms onset-aligned epoching. Dataset provides perfectly balanced classes (11004 target / 11004 distractor), ideal for binary classification. The `event` marker (20384 occurrences) is a generic trial marker and should be excluded as it does not differentiate conditions. Apply bandpass filter (0.5–40 Hz) and artifact rejection prior to epoching.

### Classical Task 2: Attentional Lapse Prediction from Decodability Drop
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["target", "distractor", "miss_response"]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `target` | 1 | Target object to be tracked |
| `distractor` | 2 | Distractor object |
| `miss_response` | 0 | Missed target response (attentional lapse) |

- **Evidence**: DOI: https://doi.org/10.1101/2025.07.10.663816
- **Kernel Notes**: This is the primary task described in the reference paper—predicting attentional lapses using neural decodability of target vs. distractor as a predictor. Requires deriving behavioral outcome labels (correct vs. lapse) from trial response data. Super-meta level integration of behavioral outcomes with raw event markers needed. Authors are from Macquarie University matching dataset contributors; abstract explicitly mentions MOM task and EEG decoding to predict attentional lapses.

### Normal Task 1: Trial-Level Segmentation for Sustained Tracking Analysis
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, segment_length = 4.0 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `event` | 0 | Generic trial onset marker |

- **Evidence**: Partial support from DOI: https://doi.org/10.1371/journal.pone.0022660 (EEG Correlates of Attentional Load during Multiple Object Tracking); DOI: https://doi.org/10.1088/1741-2552/abb9bc (Continuous decoding of cognitive load from EEG)
- **Kernel Notes**: For sustained tracking analysis, segment trials around the `event` marker indicating trial onset. The 4s window accommodates the full trial structure including target designation, tracking period, and response. Supports primary classification/segmentation task defined in dataset metadata. 210 files from 30 subjects with ~7 runs each requires consistent run-level handling.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
