# BCIT Traffic Complexity

**Dataset**: `openneuro_ds004123` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004123
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 74 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Subjects performed a simulated driving task with varying levels of visual traffic complexity (low, medium, high density of surrounding vehicles) while correcting for lateral vehicle perturbations. EEG was recorded to assess how increasing traffic complexity interacts with fatigue-related neural signatures. Part of the BCIT driving fatigue dataset series examining environmental complexity effects on driver workload.

## File Scan Result

> **Kernel SHA256**: `fd875c9ca9421e3b3bb78b5519bcd46c90f2b206d6664f11bf91fd8a6bfb69ec`
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

### Classical Task 1: Traffic Complexity Classification (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["3210", "3230", "3240"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `3210` | 0 | Low traffic complexity |
| `3230` | 1 | Medium traffic complexity |
| `3240` | 2 | High traffic complexity |

- **Evidence**: DOI: 10.1016/j.neuroimage.2019.116054 (Mega-analysis II: Cognitive aspects of event related features)
- **Kernel Notes**: Traffic complexity markers (3210/3230/3240) appear in all 30 files as short stimulus onset events (<2 s duration). These are the primary manipulation variable—neural responses should differentiate cognitive load across density conditions. The BCIT Traffic ARLT dataset (30 subjects, 44 codes) is explicitly referenced in the mega-analysis. Label Route via `event` since complexity level is directly encoded in raw trigger stream. Lane deviation or response latency could serve as secondary regressors for regression tasks.

### Normal Task 1: Lane Correction Response Classification (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = ["1211", "1212"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `1211` | 0 | Lane correction event type 1 |
| `1212` | 1 | Lane correction event type 2 |

- **Evidence**: Partial support from DOI: 10.1016/j.physbeh.2015.05.026 (event-related alpha perturbations related to steering wheel corrections); DOI: 10.3389/fnins.2014.00155 (lane deviation estimation from EEG power spectra)
- **Kernel Notes**: Lane correction events mark driver behavioral responses to lateral perturbations. Longer epoch window (tmin=-0.5 s) captures pre-response baseline; tmax=1.5 s captures motor execution and correction completion. Same ARL lab research context as BCIT dataset. Different subject counts in supporting papers (10-15 vs 30) limit direct cross-validation.

### Normal Task 2: Perturbation Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 2.0 s, target_events = ["3111", "4210", "4220", "4230"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `3111` | 0 | Perturbation onset |
| `4210` | 1 | Perturbation onset |
| `4220` | 2 | Perturbation event |
| `4230` | 3 | Perturbation/direction event |

- **Evidence**: Partial support from DOI: 10.1016/j.neuroimage.2017.02.057 (proactive and reactive brain states in driving with perturbations); DOI: 10.1080/00222895.2014.959887 (driver and vehicle interaction with transient changes)
- **Kernel Notes**: Perturbation onset markers (3111/4210) indicate lateral vehicle perturbations requiring driver correction. Extended window captures sensory processing, motor preparation, and corrective action. Key for studying fatigue-related response latency changes. Lateral perturbation types (4311/4312) may encode direction-specific features for expanded binary classification.

### Potential Task 1: Driving Performance Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = ["3310"]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `3310` | continuous | Performance metric value (per-trial) |

- **Evidence**: Partial support from DOI: 10.3389/fnins.2014.00155 (estimating lane deviation from EEG power spectra with SFFS feature selection); DOI: 10.1016/j.biopsycho.2015.12.009 (EEG features for behavioral estimation in real-world tasks)
- **Kernel Notes**: Same ARL lab driving research context. Performance metrics (3310) provide continuous behavioral labels for regression rather than discrete classification. Feature selection methods (SFFS) recommended for high-dimensional EEG power spectra inputs. Different subject counts (25 vs 30) in supporting studies—caution in cross-study generalization.

### Potential Task 2: Fatigue Signature Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: segment_length = 30-60 s, overlap = 0.5, target_events = ["3210", "3230", "3240"]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---------|
| `3210` | 0 | Low fatigue probability |
| `3240` | 1 | High fatigue probability |

- **Evidence**: Paradigm rationale only (BCIT driving fatigue dataset series examining environmental complexity effects on driver workload)
- **Kernel Notes**: Fatigue-related neural signatures expected to emerge during high traffic complexity (3240) due to increased sustained attention demands. Alpha-band perturbations documented in related ARL papers (DOI: 10.1016/j.physbeh.2015.05.026) support spectral markers for fatigue detection. Requires super-level meta derivation combining complexity condition with temporal progression within session. Speed marker (3200) can serve as auxiliary feature for artifact regression.