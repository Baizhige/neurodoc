# Evidence accumulation relates to perceptual consciousness and monitoring

**Dataset**: `openneuro_ds001785` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds001785
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 54 | **Channels**: 71 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a threshold-level vibrotactile detection task in which a weak tactile stimulus was either present (threshold condition) or absent (adapt condition). After each trial, participants provided a confidence rating. The study investigated the neural mechanisms of evidence accumulation and metacognitive monitoring using signal detection theory outcomes (hit, miss, correct rejection, false alarm) as trial labels.

## File Scan Result

> **Kernel SHA256**: `e38f1fbdfa9a58a58e9594d0efedef37ea4433ded82407f44c1f960166e80fd1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Confidence Rating Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: `super`
- **Target Definition Table**:

 | Event | y | Meaning |
 |-------|---|-|
 | `200` | continuous | Stimulus onset (threshold condition) |
 | `201` | continuous | Stimulus onset (adapt condition) |
 | `confidence` | continuous | Confidence rating (misc channel) |

- **Evidence**: https://doi.org/10.1038/s41467-021-23540-y
- **Kernel Notes**: Confidence ratings from misc channel serve as continuous regression target. Cross-reference confidence values with stimulus events 200/201 to align trials. The confidence channel contains derived labels requiring metadata preservation (source, unit, version). Response times available in `response_time` misc channel for auxiliary analysis.

### Potential Task 1: Signal Detection Theory Four-Class Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to stimulus onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: `super`
- **Target Definition Table**:

 | Event | y | Meaning |
 |-------|---|-|
 | `100` | derived | Response marker (epoch trigger) |
 | `200` | derived | Stimulus onset: threshold condition |
 | `201` | derived | Stimulus onset: adapt condition |
 | `100+200` | 0 | Hit (stim-thr present + response) |
 | `100+200` | 1 | Miss (stim-thr present + no response) |
 | `100+201` | 2 | False Alarm (stim-adapt + response) |
 | `201 only` | 3 | Correct Rejection (stim-adapt + no response) |

- **Evidence**: https://doi.org/10.1038/s41467-021-23540-y
- **Kernel Notes**: SDT outcome labels (hit/miss/cr/fa) are not stored as native event IDs and must be derived by cross-referencing response marker 100, stimulus onset markers 200/201, and confidence markers 101/102. Epoch using event 100 as trigger; align to corresponding stimulus event 200 or 201 based on trial timing. Verify class balance—miss and false alarm counts may be sparse for threshold-level stimuli. The ~8750 count for events 100/200/201 suggests ~417 trials per subject across 21 subjects.

### Normal Task 2: Stimulus Condition Classification (Binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to stimulus onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: `raw`
- **Target Definition Table**:

 | Event | y | Meaning |
 |-------|---|-|
 | `200` | 0 | Threshold condition stimulus |
 | `201` | 1 | Adaptation condition stimulus |

- **Evidence**: https://doi.org/10.1038/s41467-021-23540-y
- **Kernel Notes**: Events 200 and 201 each have exactly 8750 occurrences, indicating balanced trial counts suitable for binary classification. This task serves as an alternative to SDT classification if label derivation proves problematic. The -0.2s pre-stimulus window enables baseline correction for evidence-accumulation components (e.g., CND).

### Normal Task 3: Response-Locked Metacognitive Monitoring
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s (relative to response), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Meta Level**: `raw`
- **Target Definition Table**:

 | Event | y | Meaning |
 |-------|---|-|
 | `100` | 0 | Response marker (all trials) |

- **Evidence**: https://doi.org/10.1038/s41467-021-23540-y
- **Kernel Notes**: Response-locked epochs using event 100 (8750 occurrences) capture motor preparation and post-decision monitoring processes. Combine with confidence values from misc channel post-epoching to analyze metacognitive evaluation. The symmetric ±0.5s window isolates pre-response preparation and post-response evaluation phases relevant to evidence monitoring.