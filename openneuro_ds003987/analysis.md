# EEG: Amphetamine trials 5CCPT and Probabilistic Learning

**Dataset**: `openneuro_ds003987` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003987
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 69
**Channels**: 71 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

A double-blind, crossover pharmacological study investigating the effects of d-amphetamine on cognitive performance using two tasks: the 5-Choice Continuous Performance Task (5CCPT), which assesses sustained attention and impulsivity, and a Probabilistic Selection Task (PST), which measures reinforcement learning. EEG was recorded from 23 subjects across three drug sessions (placebo, low-dose, high-dose amphetamine), with recordings obtained using a 71-channel system at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `431be59018ac69425e5d16da6fb48c77bbe35597e3748dd6acad02e01a933ee7`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `21 5CCPT` | 16558 | event | raw | 5CCPT event type 21 (task-specific trial condition) |
| `22 5CCPT` | 9811 | event | raw | 5CCPT event type 22 (task-specific trial condition) |
| `23 5CCPT` | 9547 | event | raw | 5CCPT event type 23 (task-specific trial condition) |
| `25 5CCPT` | 4442 | event | raw | 5CCPT event type 25 (task-specific trial condition) |
| `unknown_1` | 263 | event | raw | Unidentified event code 1 |
| `unknown_10` | 4130 | event | raw | Unidentified event code 10 |
| `unknown_11` | 2388 | event | raw | Unidentified event code 11 |
| `unknown_12` | 2290 | event | raw | Unidentified event code 12 |
| `unknown_13` | 2378 | event | raw | Unidentified event code 13 |
| `unknown_14` | 2369 | event | raw | Unidentified event code 14 |
| `unknown_15` | 2389 | event | raw | Unidentified event code 15 |
| `unknown_16` | 3459 | event | raw | Unidentified event code 16 |
| `unknown_17` | 7445 | event | raw | Unidentified event code 17 |
| `unknown_18` | 5055 | event | raw | Unidentified event code 18 |
| `unknown_19` | 3745 | event | raw | Unidentified event code 19 |
| `unknown_2` | 2482 | event | raw | Unidentified event code 2 |
| `unknown_20` | 2383 | event | raw | Unidentified event code 20 |
| `unknown_24` | 4804 | event | raw | Unidentified event code 24 |
| `unknown_26` | 2094 | event | raw | Unidentified event code 26 |
| `unknown_27` | 536 | event | raw | Unidentified event code 27 |
| `unknown_28` | 888 | event | raw | Unidentified event code 28 |
| `unknown_29` | 1643 | event | raw | Unidentified event code 29 |
| `unknown_3` | 2481 | event | raw | Unidentified event code 3 |
| `unknown_30` | 1905 | event | raw | Unidentified event code 30 |
| `unknown_31` | 1534 | event | raw | Unidentified event code 31 (likely PST feedback condition) |
| `unknown_32` | 3526 | event | raw | Unidentified event code 32 (likely PST feedback condition) |
| `unknown_33` | 5216 | event | raw | Unidentified event code 33 |
| `unknown_34` | 4554 | event | raw | Unidentified event code 34 |
| `unknown_35` | 8011 | event | raw | Unidentified event code 35 |
| `unknown_36` | 12776 | event | raw | Unidentified event code 36 |
| `unknown_37` | 13916 | event | raw | Unidentified event code 37 |
| `unknown_38` | 9213 | event | raw | Unidentified event code 38 |
| `unknown_39` | 9749 | event | raw | Unidentified event code 39 (likely PST neutral feedback) |
| `unknown_4` | 2481 | event | raw | Unidentified event code 4 |
| `unknown_40` | 12868 | event | raw | Unidentified event code 40 |
| `unknown_41` | 7943 | event | raw | Unidentified event code 41 |
| `unknown_42` | 2919 | event | raw | Unidentified event code 42 |
| `unknown_43` | 1022 | event | raw | Unidentified event code 43 |
| `unknown_44` | 279 | event | raw | Unidentified event code 44 |
| `unknown_45` | 199 | event | raw | Unidentified event code 45 |
| `unknown_46` | 89 | event | raw | Unidentified event code 46 |
| `unknown_47` | 29 | event | raw | Unidentified event code 47 |
| `unknown_48` | 7 | event | raw | Unidentified event code 48 |
| `unknown_5` | 2482 | event | raw | Unidentified event code 5 |
| `unknown_6` | 2484 | event | raw | Unidentified event code 6 |
| `unknown_7` | 2484 | event | raw | Unidentified event code 7 |
| `unknown_8` | 7245 | event | raw | Unidentified event code 8 |
| `unknown_9` | 4049 | event | raw | Unidentified event code 9 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: PST Reward vs Punishment Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`31 PST`, `32 PST`, `39 PST`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31 PST` | 0 | Reward feedback (75% reward condition) |
  | `32 PST` | 1 | Punishment feedback (75% punishment condition) |
  | `39 PST` | 2 | Neutral feedback (50-50 condition) |
- **Evidence**: DOI: 10.1007/s00213-022-06082.z — "Amphetamine alters an EEG marker of reward processing in humans and mice." Double-blind crossover study (n=23 humans, all 3 sessions). EEG epochs around feedback onset (-500 to +1000ms) examining reward positivity (RewP) ERP (200-400ms window) and delta-band spectral responses. Explicitly maps event codes 31/32/39 to reward/punishment/neutral feedback conditions in the probabilistic selection task.
- **Kernel Notes**: RewP is a mid-frontal ERP component sensitive to reward prediction errors. The three-class design (reward vs punishment vs neutral) enables distinguishing between positive and negative feedback processing. Drug condition (placebo/low/high amphetamine) can be added as between-condition variable for pharmacology analysis.

### Potential Task 1: 5CCPT Sustained Attention Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`21 5CCPT`, `22 5CCPT`, `23 5CCPT`, `25 5CCPT`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `21 5CCPT` | 0 | 5CCPT condition 21 (e.g., target stimulus) |
  | `22 5CCPT` | 1 | 5CCPT condition 22 |
  | `23 5CCPT` | 2 | 5CCPT condition 23 |
  | `25 5CCPT` | 3 | 5CCPT condition 25 |
- **Evidence**: DOI: 10.1038/s41398-021-01562-w — "Electrophysiological biomarkers of behavioral dimensions from cross-species paradigms." Foundational methodology paper by same research group (Cavanagh, Young, Light, Swerdlow) describing 5C-CPT paradigm and response-locked theta power for sustained attention/impulsivity assessment.
- **Kernel Notes**: The 5-Choice Continuous Performance Task assesses sustained attention and impulsivity. Four event codes capture different trial conditions (e.g., correct target, incorrect response, anticipatory response). Pre-stimulus baseline (-200ms) allows for baseline correction. Drug effects on attentional processing can be compared across sessions.

### Potential Task 2: PST Delta-Band Reward Prediction Error Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`31 PST`, `32 PST`, `39 PST`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31 PST` | 0 | Reward feedback |
  | `32 PST` | 1 | Punishment feedback |
  | `39 PST` | 2 | Neutral feedback |
- **Evidence**: DOI: 10.1007/s00213-022-06082.z — Same paper describes delta-band (1-4 Hz) spectral responses time-locked to feedback onset that track reward prediction errors in probabilistic learning.
- **Kernel Notes**: Reuses same feedback-locked epochs as RewP analysis. Delta-band power changes differentiate reward vs punishment conditions and reflect prediction error signaling. Can combine with ERP features for multimodal analysis. Requires frequency-domain preprocessing (e.g., time-frequency decomposition).