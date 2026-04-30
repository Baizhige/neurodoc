# Dataset on Emotion with Naturalistic Stimuli (DENS)

**Dataset**: `openneuro_ds003751` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003751
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 40 | **Manual Review**: Pending
**Channels**: 132 | **Sampling Rate**: 250 Hz

## Paradigm

Participants viewed naturalistic multimedia video clips (film excerpts, documentaries) to elicit a range of emotional states while EEG, ECG, and EMG data were simultaneously recorded. During viewing, participants provided continuous self-report ratings of emotional dimensions (valence, arousal, dominance, frustration, relief, looking behavior) by clicking at moments of emotional significance. After each video clip, participants also provided categorical emotion labels and continuous ratings. The dataset supports multimodal emotion recognition research using ecologically valid naturalistic stimuli.

## File Scan Result

> **Kernel SHA256**: `c667176ee37367028edf39272aa7b49de7d660958c021021a8a618188ae5ce22`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `arousal_low` | 431 | event | raw | Continuous arousal rating (low threshold marker) |
| `baseline` | 40 | event | raw | Baseline period onset |
| `baseline_end` | 40 | event | raw | Baseline period end |
| `boundary` | 53 | event | raw | Data file boundary marker |
| `category` | 288 | event | raw | Emotion category rating response |
| `click` | 744 | event | raw | Mouse click marking emotional moment |
| `dominance` | 431 | event | raw | Continuous dominance rating |
| `fixation_left` | 430 | event | raw | Fixation cross onset (left position) |
| `frustration` | 431 | event | raw | Continuous frustration rating |
| `interval_begin` | 134 | event | raw | Video clip block beginning |
| `interval_end` | 133 | event | raw | Video clip block end |
| `looking` | 431 | event | raw | Looking behavior rating |
| `net` | 2 | admin | raw | Network marker |
| `pause` | 50 | admin | raw | Pause marker |
| `quiz` | 15 | event | raw | Comprehension quiz question |
| `quiz_done` | 14 | event | raw | Quiz completion marker |
| `relief` | 431 | event | raw | Continuous relief rating |
| `restart` | 48 | admin | raw | Restart marker |
| `stimulus` | 432 | event | raw | Video clip onset |
| `stop` | 37 | admin | raw | Stop/pause marker |
| `trial_number` | 433 | event | raw | Trial number marker |
| `valence_negative_centered` | 431 | event | raw | Valence rating (negative-centered scale) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Stimulus-Locked Emotional Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 5.0 s, target_events = [`stimulus`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | stimulus | video_id | Video clip onset (432 events) |
- **Evidence**: N/A (plausible from paradigm alone)
- **Kernel Notes**: Alternative epoching approach using stimulus onset (`stimulus`, 432 events) instead of subjective click markers. Labels derived from subsequent continuous ratings. Captures initial stimulus-driven emotional response vs. self-initiated moment marking.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
