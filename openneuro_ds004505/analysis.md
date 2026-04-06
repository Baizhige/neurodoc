# Real World Table Tennis

**Dataset**: `openneuro_ds004505` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004505
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played real table tennis matches in two conditions: cooperative (rallying) and competitive (point-scoring). EEG was recorded during actual gameplay using a mobile EEG system. Events mark the condition type and specific ball-hit moments (moving_serve vs stationary_serve shots). The study investigates motor cortex dynamics during ecological real-world sport.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `moving_hit` | ~19xN | event | raw | Ball hit during moving serve condition |
| `stationary_hit` | ~19xN | event | raw | Ball hit during stationary serve condition |
| `cooperative` | ~19xN | event | raw | Cooperative play condition block |
| `competitive` | ~19xN | event | raw | Competitive play condition block |
| `moving_serve` | ~19xN | event | raw | Moving serve condition block |
| `stationary_serve` | ~19xN | event | raw | Stationary serve condition block |
| `STATUS` | ~19xN | admin | raw | BrainVision hardware status marker |
| `M 1` | ~19xN | admin | raw | Miscellaneous hardware marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Hit Type Classification (moving vs stationary serve)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`moving_hit`, `stationary_hit`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `moving_hit` | 0 | Ball hit in moving serve condition |
  | `stationary_hit` | 1 | Ball hit in stationary serve condition |
- **Super Meta Notes**: Derived from raw hit events by detecting peaks in IMU acceleration (first derivative exceeded 0.75g) and verified against video data - not raw stimulus triggers. Kernel step: Load IMU data from supporting files, compute acceleration first derivative, threshold at 0.75g, align with EEG timestamps to produce hit event labels.
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.110024 — Data in Brief paper describing dual-layer EEG dataset from table tennis with synchronized IMUs, where hit events were marked when IMU acceleration exceeded 0.75g and verified against video
- **Kernel Notes**: (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Hit Type Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS and M 1 are admin events - exclude from target_events. cooperative/competitive/moving_serve/stationary_serve are long condition blocks. Focus on discrete hit events for epoch-based analysis.

| Event | y | Meaning |
|-------|---|------|
| `moving_hit` | 0 | Ball hit in moving serve condition |
| `stationary_hit` | 1 | Ball hit in stationary serve condition |

## Data Quality Notes

- Real-world mobile EEG with significant motion artifacts expected
- STATUS and M 1 are hardware markers, not task events


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review