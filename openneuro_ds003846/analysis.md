# Prediction Error

**Dataset**: `openneuro_ds003846` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003846
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 50
**Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A virtual reality haptic interaction study where participants reached out to touch spawned virtual boxes while receiving varied combinations of visual, vibrotactile, and electrical muscle stimulation (EMS) feedback. Trials were marked as "normal" (congruent feedback) or "conflict" (incongruent prediction error condition), allowing investigation of multisensory prediction error processing. Three feedback modality conditions were run in separate sessions: visual-only, vibrotactile-only, and combined EMS conditions.

## File Scan Result

> **Kernel SHA256**: `5348370cdd070cc93f2f9cd52a2c61c152bc80a6751ccf0cdecbaad9b7debeec`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Prediction Error Detection (Normal vs Conflict)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`box`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `box` (normal_or_conflict:normal) | 0 | Normal (congruent) trial with expected feedback |
  | `box` (normal_or_conflict:conflict) | 1 | Conflict (prediction error) trial with incongruent feedback |
- **Evidence**:
  - DOI: `10.3389/fnrgo.2024.1411305` — Data descriptor paper describing binary classification of match (congruent/normal) vs mismatch (incongruent/conflict/prediction error) trials from openneuro_ds003846 dataset, using ERP epoch -0.1s to 0.6s relative to tap/box:touched event. Supports 2×3 design with visuo-haptic mismatch conditions.
- **Kernel Notes**: Extract events matching 'box' pattern; parse embedded annotation strings for `normal_or_conflict:normal` (label 0) vs `normal_or_conflict:conflict` (label 1). The box event serves as both spawn and touch marker; filter for touch events when extracting prediction error labels. Session-specific analysis recommended given three distinct feedback modality conditions (visual-only, vibrotactile-only, EMS). Reaction time available via misc route as optional regression target or covariate.

### Normal Task 1: Feedback Modality Comparison
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`visualFeedback`, `vibroFeedback`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `visualFeedback` | 0 | Visual-only feedback modality session |
  | `vibroFeedback` | 1 | Vibrotactile feedback modality session |
- **Evidence**:
  - DOI: `10.3389/fnrgo.2024.1411305` — Mentions three feedback modality conditions (visual-only, vibrotactile-only, EMS) run in separate sessions; evidence is partial as primary paper focuses on mismatch detection rather than explicit modality classification.
- **Kernel Notes**: Visual feedback events appear in fewer files (50) vs vibrotactile (198), suggesting uneven session completion. May require session-level stratification or separate modality-specific analysis pipelines. EMS condition events not listed in available event IDs—verify EMS feedback event naming convention in raw data.
