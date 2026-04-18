# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based task with 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The trial structure follows a four-phase paradigm: baseline rest periods, cue-based preparation (ready phase), active task execution, and interval periods. Feedback cues are presented in a subset of trials, with 1237 feedback markers distributed across sessions, alongside system trigger synchronization markers.

## File Scan Result

> **Kernel SHA256**: `0b76d1f6b8c9debb1c945689a3b5b3eb4dfc108adca818f04c86bd04733505e5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 327 | event | raw | Trial phase onset: rest |
| `event_2` | 5090 | event | raw | Trial phase onset: task |
| `event_3` | 3270 | event | raw | Trial phase onset: ready |
| `event_4` | 1237 | event | raw | Trial phase onset: interval |
| `event_5` | 1237 | event | raw | Stimulus/response marker: cue |
| `event_6` | 91 | admin | raw | System marker: trigger sync |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Cue-Evoked Response Detection
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1.0 s, target_events = [`event_5`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_5` | 0 | Cue onset marker preceding task execution |
- **Evidence**: 1237 cue markers distributed across sessions; each cue is preceded by event_3 (ready) and followed by event_2 (task), suggesting cue-locked response analysis is feasible
- **Kernel Notes**: Single-class detection task; requires external event pairing (e.g., cue vs baseline) for binary framing. Recommended for evoked potential analysis (P300, cue-locked alpha modulation). Unclear semantic meaning without instruction column access to verify cue type distinctions.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
