# BCIT Baseline Driving

**Dataset**: `openneuro_ds004120` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004120
**Category**: Complex Applied | **Subjects**: 131 | **Files (Completed)**: 131 | **Channels**: 266 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Subjects performed a 60-minute simulated driving task involving manual steering and speed control, requiring corrective responses to lateral vehicle perturbations to study fatigue-related EEG biomarkers over an extended session. This baseline driving condition serves as the primary long-duration fatigue paradigm in the BCIT series, without auditory cueing or traffic complexity manipulation.

## File Scan Result

> **Kernel SHA256**: `3ccd3c926c7c5210cbf0a48d0a24ec3c7f0a41d767c2e0068afaaa352f45f119`
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

### Classical Task 1: Continuous Driving Performance Estimation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 3 s, overlap = 0.33, target_events = [`4210`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | continuous | float (0–1 normalized) | Lane deviation / normalized accuracy / reaction time / button press duration |
- **Super Meta Notes**: Derived from raw event(s) [`4210`, `3310`, `1211`, `1212`, `1121`, `1111`] by computing behavioral metrics from vehicle state (lane deviation) and button responses, then normalizing by perceptual difficulty and target probability, then smoothing with 90s centered mean filter. Kernel step: extract continuous behavioral metrics (lane deviation in meters, normalized accuracy 0–1, reaction time in ms, button press duration in ms) synchronized to EEG, apply 90s temporal smoothing, use as regression targets.
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — EEG log power spectra with PCA and linear regression estimate continuous behavioral performance (lane deviation, accuracy, RT, duration) during simulated driving using 256-channel BioSemi recordings at 1024Hz — this paper uses an earlier version of the BCIT driving paradigm released as openneuro_ds004120
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Common EEG features for behavioral estimation in disparate, real-world tasks; reports correlation 0.548±0.117 for driving task using SFFS and linear regression on continuous behavioral metrics
- **Kernel Notes**: Verify event ID mapping from events.tsv. Paper uses 750-point epochs (~3s) with 500-point step (~2s) sliding windows on continuous EEG, smoothed with 90s centered mean filter. Map 'perturbation onset' (4210) for epoching, but derive labels from continuous behavioral stream.

### Classical Task 2: Lane Correction Response Type
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1211`, `1212`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1211` | 0 | Lane correction event — type 1 |
  | `1212` | 1 | Lane correction event — type 2 |
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — Same paradigm defines lane correction events linked to corrective steering responses during perturbations
  - DOI: 10.1016/j.physbeh.2015.05.026 — Event-related alpha perturbations related to steering wheel corrections; documents steering response events during simulated driving
- **Kernel Notes**: Pre-stimulus baseline (-0.2s) captures pre-correction neural state; 1.0s post-window covers motor planning and execution of corrective steering responses.

### Classical Task 3: Driver Response to Perturbations
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`1121`, `1122`, `1111`, `1112`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1121` | 0 | Driver response event — type 1 |
  | `1122` | 1 | Driver response event — type 2 |
  | `1111` | 2 | Driver response event — variant 1 |
  | `1112` | 3 | Driver response event — variant 2 |
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — Documents driver response events during lateral perturbations in driving paradigm
  - DOI: 10.1016/j.neuroimage.2017.02.057 — Source analysis of delta/theta/alpha/beta bands linked to steering behavior; supports classification of proactive vs. reactive brain states in driving
- **Kernel Notes**: Longer 1.5s window accommodates full motor response cycle. 4-class decomposition distinguishes response urgency/amplitude.

### Normal Task 1: Lateral Perturbation Direction Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`4311`, `4312`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `4311` | 0 | Lateral perturbation — direction/type 1 |
  | `4312` | 1 | Lateral perturbation — direction/type 2 |
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — Lateral perturbations induce direction-specific steering corrections; event codes 4311/4312 encode perturbation direction
  - DOI: 10.1016/j.neuroimage.2017.02.057 — Directional brain-behavior interactions during perturbations; supports neural encoding of perturbation direction
- **Kernel Notes**: Pre-stimulus baseline (-0.2s) captures pre-perturbation neural state; 1.0s post-stimulus covers immediate neural response. Primary baseline driving condition for BCIT fatigue series comparison.

### Normal Task 2: Perturbation Response vs. Onset
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`3111`, `3112`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `3111` | 0 | Perturbation onset |
  | `3112` | 1 | Perturbation response |
- **Evidence**:
  - DOI: 10.3389/fnins.2014.00155 — Paradigm distinguishes onset (sensory detection) from response (motor execution) phases
- **Kernel Notes**: Shorter 0.8s window focuses on detection-response cycle. May reveal fatigue effects on response latency.

### Potential Task 1: Auditory Cue Detection (Subset)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`2611`, `2612`, `2621`, `2622`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `2611` | 0 | Auditory cue event — type 1 |
  | `2612` | 1 | Auditory cue event — type 2 |
  | `2621` | 2 | Auditory cue event — variant 1 |
  | `2622` | 3 | Auditory cue event — variant 2 |
- **Notes**: Present in only 28/131 files (subset of sessions). Requires subject-level filtering.
- **Kernel Notes**: Only available for subset of recordings; cannot be applied to full cohort without filtering.

### Potential Task 2: Driving State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`3200`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | continuous | speed state (categorical) | Speed/driving state marker |
- **Notes**: Plausible from paradigm alone — driving state (speed) likely modulates neural activity (alpha blocking, engagement). No direct reference confirms ML classification of driving state from EEG.
- **Kernel Notes**: Suggests using 4s segments with 50% overlap to capture sustained driving state. May correlate with fatigue markers.

### Potential Task 3: Perturbation Event Complexity
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.5 s, target_events = [`4220`, `4230`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `4220` | 0 | Perturbation event |
  | `4230` | 1 | Perturbation/direction event |
- **Notes**: Distinguishes general perturbation from direction-tagged perturbation events. Plausible task for decoding perturbation salience.
- **Kernel Notes**: Short 0.5s window focuses on early neural discrimination. Verify BCIT codebook for semantic distinction.