# BCIT Auditory Cueing

**Dataset**: `openneuro_ds004105` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004105
**Category**: Complex Applied | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 74 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a long-duration simulated driving task involving lane maintenance with periodic lateral vehicle perturbations, while receiving auditory cues at varying intervals. EEG biomarkers of fatigue were investigated as performance and alertness declined over the driving session. The study is part of the BCIT (Brain Computer Interface and Technology) driving fatigue dataset series.

## File Scan Result

> **Kernel SHA256**: `b113b938fcff5edee53c6b6f20c99ad504795e3ea63ec6cf20c2bb6fda6a1887`
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

### Classical Task 1: Auditory Cue ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
| Event | y | Meaning |
|-------|---|--------|
| `1211` | 0 | Auditory cue type 1 |
| `1212` | 1 | Auditory cue type 2 |
- **Evidence**: Dataset origin: BCIT driving fatigue series (openneuro_ds004105); paradigm involves auditory cueing as primary experimental manipulation with varying intervals across 34 subjects.
- **Kernel Notes**: Auditory cue events (1211/1212) are short stimulus onset markers with 'raw' meta level. Epoch window captures P300/ERN-like auditory ERP components. Varying cue intervals may reveal fatigue-related modulation in auditory processing over driving session. Label route: Annotation.

### Normal Task 1: Lateral Perturbation Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
| Event | y | Meaning |
|-------|---|--------|
| `4311` | 0 | Lane deviation/correction type 1 |
| `4312` | 1 | Lane deviation/correction type 2 |
- **Evidence**: Partial reference 10.1016/j.neuroimage.2017.02.057 supports driving simulation with lateral perturbations; EEG linked to steering behavior; binary lane deviation events confirmed in dataset event structure (34 files).
- **Kernel Notes**: Binary classification task for lane deviation/correction events. Event codes are 'short' type with onset markers. Window [-0.2, 1.0]s captures pre-event baseline and post-perturbation response. Part of BCIT driving fatigue series. Label route: Annotation.

### Potential Task 1: Driving Event Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
| Event | y | Meaning |
|-------|---|--------|
| `4210` | 0 | Driving event 4210 (lateral perturbation onset) |
| `4220` | 1 | Driving event 4220 |
| `4230` | 2 | Driving event 4230 |
| `3111` | 3 | Perturbation response type 1 |
| `3112` | 4 | Perturbation response type 2 |
- **Evidence**: Supported by dataset event structure (34 files); partial reference indicates simulated driving with lateral perturbations and EEG linked to steering behavior.
- **Kernel Notes**: Extended epoch window (tmax=2.0s) captures sustained driver response dynamics and recovery. Events are 'short' type with onset markers. Multiclass target definition based on event codes. Label route: Annotation.

### Potential Task 2: Behavioral Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
| Event | y | Meaning |
|-------|---|
| `2621` | 0 | Behavioral response type 1 |
| `2622` | 1 | Behavioral response type 2 |
- **Evidence**: Behavioral response events (2621/2622) present in all 34 files.
- **Kernel Notes**: Binary classification task for behavioral responses. Full BCIT codebook required for semantic interpretation. Label route: Annotation.

### Potential Task 3: Performance Metric Analysis
- **Task Type**: classification/regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
| Event | y | Meaning |
|-------|---|
| `3310` | continuous | Performance metric event |
- **Evidence**: Event 3310 present in all 34 files; partial reference (10.1016/j.neuroimage.2017.02.057) links EEG to continuous driving performance metrics.
- **Kernel Notes**: Task may support regression on continuous performance measures. Label route: Annotation. Full BCIT codebook required for metric interpretation.