# Meta-rdk: Raw EEG data

**Dataset**: `openneuro_ds004367` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004367
**Category**: High-level Mental | **Subjects**: 42 | **Files (Completed)**: 40 | **Channels**: 68 | **Sampling Rate**: 1200 Hz
**Manual Review**: Pending

## Paradigm

A visual motion discrimination task involving left/right direction decisions on random dot kinematogram (RDK) stimuli followed by a metacognitive confidence assessment using a visual analog scale. The numerical trigger codes encode stimulus direction, coherence level, response direction, confidence level, and feedback. The dataset supports both motion perception classification and confidence/metacognition regression.

## File Scan Result

> **Kernel SHA256**: `fd3a406f83993e897bdf96fc13992ab48abb39a55c04c33855d983f9b9234a21`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Motion Direction Classification (RDK)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [3072, 3456, 3584, 3968, 4096, 4480]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `3072` | 0 | Motion stimulus onset (direction/coherence Level 1) |
| `3456` | 1 | Motion stimulus onset (direction/coherence Level 2) |
| `3584` | 2 | Motion stimulus onset (direction/coherence Level 3) |
| `3968` | 3 | Motion stimulus onset (direction/coherence Level 4) |
| `4096` | 4 | Motion stimulus onset (direction/coherence Level 5) |
| `4480` | 5 | Motion stimulus onset (direction/coherence Level 6) |

- **Evidence**: DOI: https://doi.org/10.1101/2022.10.19.22281249; Paradigm: visual motion discrimination task with RDK stimuli requiring left/right direction decisions
- **Kernel Notes**: Numerical trigger codes require kernel-level decoding to map raw IDs to direction/coherence labels. Keep versioned trigger decoding table for reproducibility. High-density 68-channel EEG (including EOG/ECG) may require ICA for artifact removal before classification.

### Classical Task 2: Metacognitive Confidence Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [confi]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `confi` | continuous | Confidence rating (0.0–1.0 visual analog scale) |

- **Evidence**: DOI: https://doi.org/10.1101/2022.10.19.22281249; Paradigm: metacognitive confidence assessment using visual analog scale following RDK decisions
- **Kernel Notes**: Confidence values are derived labels from the misc channel. Preserve derivation schema (source=misc, unit=proportion, version=1.0). Requires Type 2 kernel processing to extract and merge high-level metacognitive labels not directly in raw events.

### Normal Task 1: Response-Locked Motor Potential Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.8 s, target_events = [left_, right]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `left_` | 0 | Left direction response (N=11,884 trials) |
| `right` | 1 | Right direction response (N=81 trials) |

- **Evidence**: Paradigm: response markers extracted from trigger stream for motor planning assessment; Epoch alignment recommendation confirms response-locked analysis
- **Kernel Notes**: Asymmetric trial distribution (left=11,884 vs right=81) suggests unequal condition sampling per subject. Use caution with class imbalance handling. Response markers derived from raw numerical codes require decoding.

### Potential Task 1: Response Time Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [left_, right, confi]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `left_` | continuous | Response time aligned to left response |
| `right` | continuous | Response time aligned to right response |
| `confi` | continuous | Confidence rating as secondary predictor |

- **Evidence**: Paradigm: response_time listed as candidate MISC label; Dataset metadata supports response time extraction for RT analysis
- **Kernel Notes**: Response time values stored in misc channel require derivation source preservation. Keep mapping schema versioned (source=stim/misc, unit=ms).

### Potential Task 2: Feedback Processing Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [feedb]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `feedb` | binary | Feedback onset marker (correct/incorrect) |

- **Evidence**: Paradigm: feedback presentation follows confidence assessment; Event counts (feedb=11,881) align with trial structure
- **Kernel Notes**: Feedback labels require decoding of numerical trigger codes to determine correct/incorrect status. May need supplementary annotation for feedback valence.