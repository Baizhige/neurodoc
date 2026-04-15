# Real World Table Tennis

**Dataset**: `openneuro_ds004505` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004505
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants played real table tennis matches in cooperative (rallying) and competitive (point-scoring) conditions with a partner. EEG was recorded during actual gameplay using a mobile EEG system with synchronized IMU sensors. Hit events were detected via IMU acceleration peaks (>0.75g threshold) verified against video data. Serve and hit markers distinguish roles (subject vs responder) during competitive play. The study investigates motor cortex dynamics during ecological real-world sport.

## File Scan Result

> **Kernel SHA256**: `no_kernel`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Hit_res_competitive` | 73 | event | raw | Ball hit by responder in competitive condition |
| `Hit_sub_competitive` | 78 | event | raw | Ball hit by subject in competitive condition |
| `M  1` | 48497 | event | raw | Hardware marker |
| `Master/M  1` | 48516 | event | raw | Master hardware marker |
| `Serve_res_competitive` | 20 | event | raw | Serve by responder in competitive condition |
| `Serve_sub_competitive` | 16 | event | raw | Serve by subject in competitive condition |
| `Subject_hit` | 37556 | event | raw | General ball hit event |
| `Subject_receive` | 19097 | event | raw | Ball receive event |
| `System/In sync` | 126 | event | raw | System synchronization marker |
| `System/Out of sync` | 130 | event | raw | System out-of-sync marker |
| `boundary` | 403 | event | raw | Data boundary marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Hit Type Classification (subject vs receiver)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Hit_res_competitive`, `Hit_sub_competitive`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Hit_res_competitive` | 0 | Ball hit by responder in competitive condition |
  | `Hit_sub_competitive` | 1 | Ball hit by subject in competitive condition |
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.110024 — Official Data in Brief descriptor for OpenNeuro ds004505; describes dual-layer EEG+IMU system for detecting hit events during table tennis gameplay; confirms hit events derived from IMU acceleration peaks (>0.75g threshold) verified against video
  - DOI: 10.1523/ENEURO.0463-22.2023 — Parieto-occipital dynamics paper from dataset creators; confirms motor action paradigm during competitive play with distinct responder/subject roles
- **Kernel Notes**: Alignment assumption: hit events mark movement onset. Filter `boundary` events (ID 403) before epoching. Exclude hardware markers (`M  1`, `Master/M  1`, `System/In sync`, `System/Out of sync`). Significant motion artifacts expected from mobile EEG during gameplay—may require extended ICA cleaning. For super meta: `Hit_res_competitive` and `Hit_sub_competitive` events derived from IMU acceleration first derivative exceeding 0.75g threshold, verified against video timestamps.

### Classical Task 2: Serve Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Serve_res_competitive`, `Serve_sub_competitive`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Serve_res_competitive` | 0 | Serve by responder in competitive condition |
  | `Serve_sub_competitive` | 1 | Serve by subject in competitive condition |
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.110024 — Confirms serve events recorded as block-level markers during competitive play
- **Kernel Notes**: Use `epoch_by_long_event_hdf5` for block events capturing full serve-and-hit sequence (4.0s window). These are long condition markers, not discrete events. Hardware markers excluded. Same motion artifact considerations as Classical Task 1.

### Potential Task 1: General Hit Classification (binary motor action)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Hit_res_competitive` | 0 | Ball hit during responder serve |
  | `Hit_sub_competitive` | 1 | Ball hit during subject serve |
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.110024 — Motor action paradigm with dual-layer EEG during real-world table tennis
- **Kernel Notes**: Alternative binary classification using raw `Subject_hit` events (n=37556 across 19 subjects) for general motor action detection. Excludes condition-specific subsets. Motion artifact handling critical for real-world mobile EEG.

### Potential Task 2: Serve Condition Block Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`Serve_res_competitive`, `Serve_sub_competitive`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Serve_res_competitive` | 0 | Competitive serve condition block |
  | `Serve_sub_competitive` | 1 | Competitive serve condition block |
- **Evidence**:
  - DOI: 10.1523/ENEURO.0463-22.2023 — Confirms competitive condition blocks with distinct serve roles
- **Kernel Notes**: Long epoch window captures neural dynamics across full serve-and-hit sequence. Block-level analysis instead of discrete hit events.