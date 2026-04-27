# EEG: Probabilistic Learning with Affective Feedback: Exp #1

**Dataset**: `openneuro_ds003822` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003822
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 66 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A reinforcement learning task using probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to subjective reward value. Participants made binary choices (left/right button) between cue stimuli (S1-S4) associated with liked or disliked affective feedback images. Following each choice, a feedback cue (S51-S54) predicted the affective image, then the full feedback (FB type) was presented. Feedback modalities included picture feedback (emotional images: puppies/chairs) and point feedback (colored bars: green +1, yellow bar, red -1). This is Experiment 1 in a two-experiment series (see ds003753 for Exp #2).

## File Scan Result

> **Kernel SHA256**: `da8530e877f8eb992d6189633b68c0e310a545bf76e90a90d3d641d0b9713d53`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `FB type: disliked loss` | 2500 | event | raw | Full picture feedback: disliked punishing image (chair) |
| `FB type: disliked loss::reward_valence=0::feedback_modality=1` | 2500 | event | super | Super-level: disliked loss with valence=0, modality=picture |
| `FB type: liked win` | 2500 | event | raw | Full picture feedback: liked rewarding image (puppy) |
| `FB type: liked win::reward_valence=1::feedback_modality=1` | 2500 | event | super | Super-level: liked win with valence=1, modality=picture |
| `FB type: point negative` | 585 | event | raw | Point feedback: negative outcome (-1, red bar) |
| `FB type: point negative::reward_valence=0::feedback_modality=0` | 585 | event | super | Super-level: point negative with valence=0, modality=point |
| `FB type: point positive` | 1230 | event | raw | Point feedback: positive outcome (+1, yellow bar) |
| `FB type: point positive::reward_valence=1::feedback_modality=0` | 1230 | event | super | Super-level: point positive with valence=1, modality=point |
| `S  1` | 1250 | event | raw | Cue stimulus type 1 (binary choice option) |
| `S  2` | 1250 | event | raw | Cue stimulus type 2 (binary choice option) |
| `S  3` | 1250 | event | raw | Cue stimulus type 3 (binary choice option) |
| `S  4` | 1250 | event | raw | Cue stimulus type 4 (binary choice option) |
| `S 10` | 2486 | event | raw | Feedback cue onset marker (predicts picture) |
| `S 20` | 2514 | event | raw | Feedback cue onset marker variant |
| `S 51` | 1350 | event | raw | Feedback onset marker type 1 |
| `S 52` | 1150 | event | raw | Feedback onset marker type 2 |
| `S 53` | 1366 | event | raw | Feedback onset marker type 3 |
| `S 54` | 1134 | event | raw | Feedback onset marker type 4 |
| `S200` | 1500 | event | raw | Response marker type 1 |
| `S201` | 3500 | event | raw | Response marker type 2 |
| `boundary` | 25 | event | raw | Discontinuous recording boundary marker |


### MISC Label Summary
*No MISC channels detected.*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Reward Valence Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`FB type: liked win::reward_valence=1::feedback_modality=1`, `FB type: disliked loss::reward_valence=0::feedback_modality=1`, `FB type: point positive::reward_valence=1::feedback_modality=0`, `FB type: point negative::reward_valence=0::feedback_modality=0`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|—---|
  | `FB type: liked win::*`, `FB type: point positive::*` | 1 | Rewarding/positive feedback (win conditions) |
  | `FB type: disliked loss::*`, `FB type: point negative::*` | 0 | Punishing/negative feedback (loss conditions) |
- **Evidence**:
  - DOI: 10.3758/s13415-021-00950-5 — Epochs data from -1000 to 3000 ms around outcome cue onset to examine Reward Positivity (RewP) amplitudes for liked vs disliked feedback images; classifies feedback valence (reward vs punishment) based on RewP ERP at Cz (200-350 ms)
- **Kernel Notes**: Detailed event IDs encode `reward_valence` parameter (0=loss, 1=win). Apply baseline correction -200 to 0 ms. Quantify RewP at 200-350 ms window at Cz for feature extraction. Boundary markers (n=25) indicate discontinuous recordings requiring concatenation verification.

### Classical Task 2: Feedback Modality Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s, target_events = [`FB type: liked win::reward_valence=1::feedback_modality=1`, `FB type: disliked loss::reward_valence=0::feedback_modality=1`, `FB type: point positive::reward_valence=1::feedback_modality=0`, `FB type: point negative::reward_valence=0::feedback_modality=0`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|—---|
  | `FB type: *::feedback_modality=1` | 1 | Picture feedback (puppy, chair, emotional images) |
  | `FB type: *::feedback_modality=0` | 0 | Point feedback (green +1, yellow bar, red -1) |
- **Evidence**:
  - DOI: 10.3758/s13415-021-00950-5 — Examines whether hedonic appraisal of picture vs point rewards modulates reward-related brain responses
- **Kernel Notes**: Detailed event IDs encode `feedback_modality` parameter (1=picture, 0=point). Apply baseline correction -200 to 0 ms. Verify event counts per subject: picture conditions show ~5000 total events (2500 liked + 2500 disliked); point conditions show ~1815 total events (1230 positive + 585 negative).

### Potential Task 1: Stimulus/Cue Classification (S1-S4)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S  1`, `S  2`, `S  3`, `S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|—---|
  | `S  1` | 1 | Cue stimulus type 1 |
  | `S  2` | 2 | Cue stimulus type 2 |
  | `S  3` | 3 | Cue stimulus type 3 |
  | `S  4` | 4 | Cue stimulus type 4 |
- **Kernel Notes**: S1-S4 markers each appear exactly 1250 times (balanced design). Plausible from paradigm: binary choice task requires 4 distinct cue stimuli (2 categories × 2 valence conditions). Verify cue meanings via experimental design documentation. Apply baseline correction -200 to 0 ms.

### Potential Task 2: Feedback Onset Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`S 51`, `S 52`, `S 53`, `S 54`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|—---|
  | `S 51` | 1 | Feedback onset marker 1 |
  | `S 52` | 2 | Feedback onset marker 2 |
  | `S 53` | 3 | Feedback onset marker 3 |
  | `S 54` | 4 | Feedback onset marker 4 |
- **Kernel Notes**: S51-S54 show varying counts (1350, 1150, 1366, 1134) with combined total ~5000, matching expected picture feedback trial count. Likely encode feedback stimulus onset with 4 distinct feedback types. Verify mapping to picture feedback categories (liked win, disliked loss). Apply baseline correction -200 to 0 ms.

### Potential Task 3: Response-Locked Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`S200`, `S201`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|—---|
  | `S200` | 0 | Response marker type 1 |
  | `S201` | 1 | Response marker type 2 |
- **Kernel Notes**: S200 (n=1500) and S201 (n=3500) show unequal counts. S200 likely marks response events (left/right button, accurate/inaccurate); S201 may mark trial completion or inter-trial interval. Verify via paradigm description (25 left + 25 right + 25 accurate + 25 inaccurate = 100 response events per subject, 2500 total across 25 subjects). Plausible from paradigm: response-locked ERPs examining feedback processing aligned to participant decisions.