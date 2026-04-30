# APPLESEED Infant EEG Dataset

**Dataset**: `openneuro_ds003710` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003710
**Category**: Biological State | **Subjects**: 13 | **Files (Completed)**: 48 | **Channels**: 32 | **Sampling Rate**: 5000 Hz | **Manual Review**: Pending

## Paradigm

Longitudinal spontaneous EEG recordings from infants at 4, 8, and 12 months of age during passive viewing of social and non-social stimuli (faces, speech, objects, water). The dataset validates the APPLESEED (Automated Preprocessing Pipe-Line for the Estimation of Scale-wise Entropy from EEG Data) pipeline for pediatric EEG preprocessing and entropy estimation. Stimuli include social (face, speech) and non-social (object, water) categories presented as short video clips, with attention-getter events to orient the infant.

## File Scan Result

> **Kernel SHA256**: `a00915a69eefe39c6bbea614db31be42ce7b8aba20ade7579fa65222fd072c1f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: Stimulus/S  5` | 1406 | event | raw | Attention-getter onset |
| `admin: Stimulus/S  6` | 64 | event | raw | Pause-related event marker |
| `admin: Stimulus/boundary` | 2 | event | raw | Data discontinuity boundary |
| `admin: Time 0/` | 4 | event | raw | Time zero marker |
| `face` | 3424 | event | raw | Face stimulus onset (social) |
| `object` | 1992 | event | raw | Object stimulus onset (non-social) |
| `speech` | 3316 | event | raw | Speech stimulus onset (social) |
| `unknown: Comment/ControlBox is not connected via USB` | 46 | admin | raw | System annotation comment |
| `unknown: New Segment/` | 6 | admin | raw | Recording segment boundary |
| `unknown: Stimulus/ControlBox is not connected via USB` | 4 | admin | raw | System annotation |
| `unknown: Stimulus/S 85` | 1 | admin | raw | Unknown stimulus event |
| `unknown: Stimulus/S255` | 3 | admin | raw | Unknown stimulus event |
| `water` | 2024 | event | raw | Water stimulus onset (non-social) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary social vs non-social stimulus classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`face`, `speech`, `object`, `water`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `face` | 1 | Face stimulus (social) |
  | `speech` | 1 | Speech stimulus (social) |
  | `object` | 0 | Object stimulus (non-social) |
  | `water` | 0 | Water stimulus (non-social) |
- **Evidence**:
  - DOI: 10.1016/j.dcn.2022.101163 — Uses APPLESEED pipeline on infant EEG from OpenNeuro ds003710 to analyze scale-wise entropy differences between face viewing (social) and object viewing (non-social) conditions across developmental stages. Confirms dataset, epoch parameters (tmin=-0.2s, tmax=1.0s), and binary social/non-social label mapping.
- **Kernel Notes**: Extract epochs time-locked to stimulus onset events (face, speech, object, water). Apply binary label: social (face, speech) = 1, non-social (object, water) = 0. Downsample from 5000 Hz to 250-500 Hz before epoching. Handle infant EEG artifact rejection. Attention-getter events (admin: Stimulus/S  5) precede stimuli but are not target classification events; exclude admin/unknown events from epoching.

### Potential Task 1: 4-class stimulus category classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`face`, `speech`, `object`, `water`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `face` | 0 | Face stimulus |
  | `speech` | 1 | Speech stimulus |
  | `object` | 2 | Object stimulus |
  | `water` | 3 | Water stimulus |
- **Evidence**:
  - DOI: 10.1016/j.dcn.2022.101163 — Paradigm includes all four stimulus categories presented during infant viewing; APPLESEED paper demonstrates feasibility of event-based epoching on these events. No reference explicitly validates multi-class classification, but all events are present with sufficient trial counts.
- **Kernel Notes**: Extract epochs for all four stimulus types. Apply 4-class labels (0=face, 1=speech, 2=object, 3=water). Expect class imbalance: face and speech have higher counts (~3300) than object and water (~2000). Longitudinal design (4, 8, 12 months) may enable age-stratified analysis. Same preprocessing as Classical Task 1 (downsampling, artifact rejection).

### Potential Task 2: Attention-getter triggered response analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`admin: Stimulus/S  5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `admin: Stimulus/S  5` | 0 | Attention-getter onset |
- **Evidence**:
  - Plausible from paradigm: The APPLESEED paradigm description indicates attention-getter events orient infant attention before stimulus trials. Event ID `admin: Stimulus/S  5` (1406 occurrences) likely corresponds to attention-getter markers based on count ratios and paradigm structure.
- **Kernel Notes**: Extract epochs around attention-getter onset for analysis of attentional orienting responses. Symmetric window (tmin=-0.5s, tmax=0.5s) captures pre- and post-attention-getter baseline and response. Use `admin: Stimulus/S  6` (64 occurrences) for pause-related events if needed; exclude `New Segment` events from epoching. Downsample from 5000 Hz. High artifact rate expected due to infant population.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
