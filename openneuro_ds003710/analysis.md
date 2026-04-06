# APPLESEED Example Dataset

**Dataset**: `openneuro_ds003710` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003710
**Category**: Biological State | **Subjects**: 13 | **Files (Completed)**: 48
**Channels**: 32 | **Sampling Rate**: 5000 Hz

## Paradigm

Longitudinal spontaneous EEG recordings from infants at 4, 8, and 12 months of age during passive viewing of social and non-social stimuli (faces, speech, objects, water). The dataset validates the APPLESEED (Automated Preprocessing Pipe-Line for the Estimation of Scale-wise Entropy from EEG Data) pipeline for pediatric EEG preprocessing and entropy estimation. Stimuli include social (face, speech) and non-social (object, water) categories presented as short video clips, with attention-getter events to orient the infant.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `face` | 48 | event | raw | Face stimulus onset (social) |
| `speech` | 48 | event | raw | Speech stimulus onset (social) |
| `object` | 48 | event | raw | Object stimulus onset (non-social) |
| `water` | 48 | event | raw | Water stimulus onset (non-social) |
| `attention-getter` | 48 | event | raw | Attention-orienting stimulus before trial |
| `experimenter-pause` | 45 | admin | raw | Experimenter pause marker |
| `New Segment` | 48 | admin | raw | Recording segment boundary marker |
| `Comment` | 48 | admin | raw | Experimenter annotation |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
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
- **Kernel Notes**: Extract epochs time-locked to stimulus onset events (face, speech, object, water). Apply binary label: social (face, speech) = 1, non-social (object, water) = 0. Downsample from 5000 Hz to 250-500 Hz before epoching. Handle infant EEG artifact rejection. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Extremely high sampling rate (5000 Hz); downsampling required before standard EEG analysis.
- Infant population; high motion artifacts and data loss expected.
- Small sample (13 subjects); longitudinal design with 3-4 files per subject across age points.
- `New Segment` and `Comment` markers should be excluded from epoching.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review